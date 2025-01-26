from pydantic import BaseModel
import logging
import openai
import os
import time
import json

logger = logging.getLogger("< InterviewAgent >")
logging.basicConfig(level=logging.INFO)

summary_prompt = "Analyze the conversation and interview performance until now. Then provide concrete areas of improvement and study plan to the candidate. Be consise and profession in your response."

coding_interviewer_agent_prompt = """
Act as an interviewer for a '{position}' focusing on {difficulty} difficulty 'coding' questions of '{type}' type at '{company}'. 

Follow these instructions when generating responses:
	1.	Begin by presenting a question relevant to the role and company, focused on asking the user to write code to answer the question.
	2.	If the user's response is correct, acknowledge it and move to the next question.
	3.	If the user's response is incorrect:
	    •	Provide hints to help the user improve their response.
	    •	Avoid revealing the correct answer immediately; instead, encourage another attempt.
	    •	If the user still doesn't get it right, explain the correct answer and move on to the next question.
	4.	Start at the specified difficult questions and ensure the questions gradually increase in complexity to assess the user's depth of knowledge and adaptability.

Keep your responses clear, concise, and professional, offering educational value throughout the process. Tailor your feedback to the user's level of expertise. 

Ensure proper formatting in your responses with new lines and white space.
"""

product_interviewer_agent_prompt = """
Act as an interviewer assessing a candidate's product sense, metrics, and experimentation skills for the role of '{position}' at '{company}'. Ensure that the questions are of {difficulty} difficulty. 

Follow these guidelines when generating responses:
	1.	Role and Context: Play the role of a product manager or data scientist conducting an interview. Focus on questions related to product strategy, defining key metrics, designing experiments, and interpreting results.
	2.	Question Style:
	    •	Ask scenario-based questions about defining product goals, identifying success metrics, and designing experiments relevant to the company.
	    •	Include questions on analyzing trade-offs, identifying risks, and improving user experiences.
	    •	Explore statistical understanding (e.g., A/B testing, sample size calculations) where relevant.
	3.	Evaluation Process:
	    •	If the candidate's answer is correct or well-reasoned, acknowledge it and provide a brief explanation of why it's a good answer. Then, ask the next question.
	    •	If the answer is partially correct or unclear, give a hint or rephrase the question for clarity. Allow them to try again.
	    •	If the candidate's second attempt is still incorrect, provide a thorough explanation of the correct answer and move to the next question.
	4.	Tone and Feedback: Maintain a professional and constructive tone. Ensure feedback is actionable and encourages learning. Adapt your responses to the level of expertise demonstrated by the candidate.
	5.	Progression: Begin with questions based on the difficulty specificed about product metrics and gradually move toward complex scenarios involving experimentation design and data interpretation.

Keep your responses clear, concise, and professional, offering educational value throughout the process. Tailor your feedback to the user's level of expertise. 

Ensure proper formatting in your responses with new lines and white space.
"""

class InputData(BaseModel):
    input: str

    def to_dict(self) -> dict:
        return {"input" : self.input}

class SessionData(BaseModel):
    company: str
    position: str
    interviewType: str
    recruiterMaterial: str
    difficulty: str

    def to_dict(self) -> dict:
        return {"company" : self.company, "position": self.position, "interviewType": self.interviewType, "recruiterMaterial": self.recruiterMaterial, "difficulty": self.difficulty}

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
        self.system_prompt = None
        self.assistant = None
        self.n = 0

    def _reset(self):
        self.client = openai.OpenAI()
        self.thread = self.client.beta.threads.create()
        self.assistant = None
        self.session_messages = []
        self.latest_input = None
        self.session_data = None
        self.system_prompt = None
        self.n = 0

    def process_input(self, input: InputData):
        if self.session_data is None:
            return AgentResponse(response="Session data not set", status=400)
        else:
            ai_response = ""

            if self.session_data.interviewType == "Coding":
                self.system_prompt = coding_interviewer_agent_prompt.format(
                    position=self.session_data.position,
                    company=self.session_data.company,
                    type=self.session_data.recruiterMaterial,
                    difficulty=self.session_data.difficulty
                )
            elif self.session_data.interviewType == "Product Sense":
                self.system_prompt = product_interviewer_agent_prompt.format(
                    position=self.session_data.position,
                    company=self.session_data.company,
                    type=self.session_data.recruiterMaterial,
                    difficulty=self.session_data.difficulty
                )

            if self.n == 0:
                self.session_messages.append({"role": "system", "content": self.system_prompt})
                self.session_messages.append({"role": "user", "content": "Let's start!"})

            self.session_messages.append({"role": "user", "content": input.input})
            self.latest_input = input.input

            response = self._get_ai_response()
            logger.info(f"Processing input #{self.n}: {input}")
            self.session_messages.append({"role": "agent", "content": response})
            self.n += 1
            return AgentResponse(response=response, status=200)
    
    def set_session_data(self, data: SessionData) -> AgentResponse:
        self._reset()
        self.session_data = data
        logger.info(f"Session data set: {data}")
        return AgentResponse(response="Session data set successfully", status=200)
    
    def get_summary(self):
        if self.n > 1:
            self.latest_input = summary_prompt
            response = self._get_ai_response()
            logger.info(f"Processing input: {self.latest_input}")
            return AgentResponse(response=response, status=200)
        else:
            return AgentResponse(response="Not enough conversations", status=200)
    
    def _get_ai_response(self):
        """
        Processes user input and gets a response from the OpenAI API.
        """

        if not self.assistant:
            # Create a new assistant if not exists
            self.assistant = self.client.beta.assistants.create(
                name="AI Interviewer",
                instructions=self.system_prompt,
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
