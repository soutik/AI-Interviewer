from pydantic import BaseModel
import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
        self.ai = OpenAI()
        self.ai.api_key = os.getenv("OPENAI_API_KEY")
        self.session_data = None
        self.messages = []
        self.model = "gpt-4o"
        self.temperature = 0.5
        self.latest_input = None

    def process_input(self, input: InputData):
        if self.session_data is None:
            return AgentResponse(response="Session data not set", status=400)
        else:
            logger.info(f"Processing input: {input}")
            return AgentResponse(response="Processed input", status=200)
    
    def set_session_data(self, data: SessionData) -> AgentResponse:
        self.session_data = data
        logger.info(f"Session data set: {data}")
        return AgentResponse(response="Session data set successfully", status=200)