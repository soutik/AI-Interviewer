from pydantic import BaseModel
import logging
import openai
import os
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

coding_interviewer_agent_prompt = """
I want you to act as an interviewer for a '{position}' focusing on 'coding' questions of '{type}' type at '{company}'. Follow these instructions when generating responses:
	1.	Begin by presenting a question relevant to the role and focused on asking the user to write code to answer the question.
	2.	If the user's response is correct, acknowledge it and move to the next question.
	3.	If the user's response is incorrect:
	    •	Provide hints to help the user improve their response.
	    •	Avoid revealing the correct answer immediately; instead, encourage another attempt.
	    •	If the user still doesn't get it right, explain the correct answer and move on to the next question.
	4.	Start at medium difficult questions and ensure the questions gradually increase in complexity to assess the user's depth of knowledge and adaptability.

Keep your responses clear, concise, and professional, offering educational value throughout the process. Tailor your feedback to the user's level of expertise.
"""

product_interviewer_agent_prompt = """
I want you to act as an interviewer assessing a candidate's product sense, metrics, and experimentation skills for the role of '{position}' at '{company}'. 

Follow these guidelines when generating responses:
	1.	Role and Context: Play the role of a product manager or data scientist conducting an interview. Focus on questions related to product strategy, defining key metrics, designing experiments, and interpreting results.
	2.	Question Style:
	    •	Ask scenario-based questions about defining product goals, identifying success metrics, and designing experiments.
	    •	Include questions on analyzing trade-offs, identifying risks, and improving user experiences.
	    •	Explore statistical understanding (e.g., A/B testing, sample size calculations) where relevant.
	3.	Evaluation Process:
	    •	If the candidate's answer is correct or well-reasoned, acknowledge it and provide a brief explanation of why it's a good answer. Then, ask the next question.
	    •	If the answer is partially correct or unclear, give a hint or rephrase the question for clarity. Allow them to try again.
	    •	If the candidate's second attempt is still incorrect, provide a thorough explanation of the correct answer and move to the next question.
	4.	Tone and Feedback: Maintain a professional and constructive tone. Ensure feedback is actionable and encourages learning. Adapt your responses to the level of expertise demonstrated by the candidate.
	5.	Progression: Begin with basic questions about product metrics and gradually move toward complex scenarios involving experimentation design and data interpretation.

"""

class InputData(BaseModel):
    input: str
    type: str

class SessionData(BaseModel):
    company: str
    position: str
    interviewType: str
    recruiterMaterial: str

class AgentResponse(BaseModel):
    response: str
    status: int

class InterviewerAgent:
    def __init__(self):
        self.session_data = None
        self.model = "gpt-4o"
        self.temperature = 0.7
        self.latest_input = None
        self.client = openai.OpenAI()
        self.client.api_key = os.getenv("OPENAI_API_KEY")
        self.thread = self.client.beta.threads.create()
        self.session_messages = []

        self.assistant = None

    def process_input(self, input: InputData):
        if self.session_data is None:
            return AgentResponse(response="Session data not set", status=400)
        else:
            self.session_messages.append({"role": "user", "content": input.input})
            self.latest_input = input.input

            if self.session_data.interviewType == "Coding":
                system_prompt = coding_interviewer_agent_prompt.format(
                    position=self.session_data.position,
                    company=self.session_data.company,
                    type=self.session_data.recruiterMaterial
                )
            elif self.session_data.interviewType == "Product Sense":
                system_prompt = product_interviewer_agent_prompt.format(
                    position=self.session_data.position,
                    company=self.session_data.company,
                    type=self.session_data.recruiterMaterial
                )

            response = self._get_ai_response(system_prompt)
            logger.info(f"Processing input: {input}")
            return AgentResponse(response=response, status=200)
    
    def set_session_data(self, data: SessionData) -> AgentResponse:
        self.session_data = data
        logger.info(f"Session data set: {data}")
        return AgentResponse(response="Session data set successfully", status=200)
    
    def _get_ai_response(self, system_prompt: str):
        """
        Processes user input and gets a response from the OpenAI API.
        """

        ai_response = ""
        self.session_messages.append({"role": "system", "content": system_prompt})
        self.session_messages.append({"role": "user", "content": "Let's start!"})

        if not self.assistant:
            # Create a new assistant if not exists
            self.assistant = self.client.beta.assistants.create(
                name="AI Interviewer",
                instructions=system_prompt,
                model=self.model,
                temperature=self.temperature
            )

        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=self.latest_input
        )

        run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
    
    # Loop until the run is completed
        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)
            logger.info(f"Current run status: {run_status.status}")
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                print("Run failed:", run_status.last_error)
                break
            time.sleep(2)  # wait for 2 seconds before checking again

        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )

        logger.info(f"Messages: {messages.data}")
        logger.info(f"Messages: {messages.data[-1].content[0].text.value}")
        for message in reversed(messages.data):
            role = message.role  
            for content in message.content:
                if content.type == 'text':
                    response = content.text.value 
                    logger.info(f'\n{role}: {response}')

                if role == "assistant":
                    ai_response = response
        return ai_response

        # response =self.client.chat.completions.create(
        #     model=self.model,
        #     messages=self.session_messages
        # )

        # ai_response = response.choices[0].message.content
        # self.session_messages.append({"role": "assistant", "content": ai_response})
        # return ai_response
