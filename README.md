# AI Interviewer

Your personal AI mock interview platform.

![alt text](AIInterviewerScreenshot.png "AI Interviewer")

## Setup

1. Run the app in a Python virtual environment ideally.
2. Ensure all packages in `requirements.txt` are installed
3. OpenAI API key stored in as environment variable


## Run 

To run frontend: 
```python3 -m streamlit run frontend.py```

To run backend
```python3 -m uvicorn backend:app --reload --host localhost --port 8000```

App is available at: http://localhost:8501

Looking for code from the [substack post](https://soutik.substack.com/p/crush-your-next-interview-with-llms)? Find it under the `Scripts/` folder.
