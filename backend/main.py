from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    input: str
    type: str

@app.post("/process")
def process_input(data: InputData):
    if data.type == "text":
        # Example processing for text input
        response = f"Processed text: {data.input.upper()}"
    elif data.type == "code":
        # Example processing for code input
        response = f"Processed code: Length of input is {len(data.input)} characters"
    else:
        response = "Invalid input type"

    return {"response": response}