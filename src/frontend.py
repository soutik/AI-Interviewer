import streamlit as st
st.set_page_config(layout="wide")

from streamlit_ace import st_ace
from openai import OpenAI
from interviewagent import InterviewerAgent, InputData, SessionData, AgentResponse
import logging
from utils import post
import json

logger = logging.getLogger("< FrontEndApp >")
logging.basicConfig(level=logging.INFO)

# url
url = "http://localhost:8000"

# Sidebar for input configuration
st.sidebar.title("Interview Details")
interview_type = st.sidebar.selectbox("Choose interview type", ["Coding", "Product Sense"])
company = st.sidebar.text_input("Company:")
position = st.sidebar.text_input("Choose the position you are interviewing for:")
details = st.sidebar.text_input("Interview details:")
submit = st.sidebar.button("Submit", type="primary")

# Main Page
st.title("💬 AI Interviewer")

# initial message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "ai", "content": "Ready to get started? Start by setting the Interview Details on the side-bar!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Submit interview details
if submit:
    st.session_state["session_data"] = SessionData( company=company, position=position, interviewType=interview_type, recruiterMaterial=details)
    logger.info(f"Got session_details: {st.session_state['session_data']}")
    response = post(url+"/set_session_data", st.session_state["session_data"].to_dict())

    if response.status_code == 200:
        msg = "Successfully set the interview details. Let me know when you are ready to proceed!"
        st.session_state.messages.append({"role": "ai", "content": msg})
        st.chat_message("ai").write(msg)
    else:
        st.chat_message("ai").write("Failed to set Interview details, try again!")


if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = post(url+"/process", InputData(input=prompt).to_dict())
    msg = json.loads(response.text)["response"]
    if response.status_code == 200:
        st.session_state.messages.append({"role": "ai", "content": msg})
        st.chat_message("assistant").write(msg)
    else:
        st.session_state.messages.append({"role": "ai", "content": f"An error occured: {msg}"})