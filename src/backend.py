from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from interviewagent import InterviewerAgent, InputData, SessionData, AgentResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = InterviewerAgent()

@app.post("/process")
def process_input(data: InputData):
    agent_response:AgentResponse = agent.process_input(data)
    return {"response": agent_response.response, "status": agent_response.status}

@app.post("/set_session_data")
def set_session_data(data: SessionData):
    agent_response:AgentResponse = agent.set_session_data(data)
    return {"response": agent_response.response, "status": agent_response.status}
