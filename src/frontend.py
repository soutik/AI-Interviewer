import streamlit as st
st.set_page_config(layout="wide", page_title="💬 AI Interviewer!")

import streamlit.components.v1 as components
from openai import OpenAI
from interviewagent import InterviewerAgent, InputData, SessionData, AgentResponse
import logging
from utils import post
import json
from code_editor import code_editor

logger = logging.getLogger("< FrontEndApp >")
logging.basicConfig(level=logging.INFO)

# url
backendURL = "http://localhost:8000"

# Sidebar for input configuration
st.sidebar.title("Interview Details")
interview_type = st.sidebar.selectbox("Choose interview type", ["Coding", "Product Sense"])
company = st.sidebar.text_input("Company:")
position = st.sidebar.text_input("Choose the position you are interviewing for:")
details = st.sidebar.text_input("Interview details:")
difficulty = st.sidebar.selectbox("Choose the interview difficulty", ["Easy", "Medium", "Hard"])
submit = st.sidebar.button("Submit", type="primary")

# st Page
st.title("💬 AI Interviewer")

# Initialize session state for messages and summary
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "ai", "content": "Ready to get started? Start by setting the Interview Details on the side-bar!"}]
if "summary" not in st.session_state:
    st.session_state["summary"] = ""

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Submit interview details
if submit:
    st.session_state["session_data"] = SessionData(company=company, position=position, interviewType=interview_type, recruiterMaterial=details, difficulty=difficulty)
    logger.info(f"Got session_details: {st.session_state['session_data']}")
    response = post(backendURL + "/set_session_data", st.session_state["session_data"].to_dict())

    if response.status_code == 200:
        msg = "Successfully set the interview details."
        st.session_state.messages.append({"role": "system", "content": msg})
        st.chat_message("system", avatar="🤖").write(msg)
    else:
        st.chat_message("ai").write("Failed to set Interview details, try again!")

# Handle user input in chat
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = post(backendURL + "/process", InputData(input=prompt).to_dict())
    msg = json.loads(response.text)["response"]
    if response.status_code == 200:
        st.session_state.messages.append({"role": "ai", "content": msg})
        st.chat_message("assistant").write(msg)
    else:
        st.session_state.messages.append({"role": "ai", "content": f"An error occurred: {msg}"})

if st.button("Generate Interview Insights"):
    with st.popover(label="Interview Insights"):
        response = post(backendURL + "/get_summary")
        if response.status_code == 200:
            st.session_state["summary"] = json.loads(response.text)["response"]
            st.success("Summary generated! Click the 'View Summary' button.")
        else:
            st.session_state["summary"] = "here is a sample"
            st.error("Something went wrong. Try again!")
        st.code(st.session_state["summary"], language="markdown")  # Handles text and code formatting

# pop-up code editor
if interview_type == "Coding":
    with st.popover(label="Code editor", use_container_width=True):
        response_dict = code_editor("Feel free to use this scratch space to write code!")