import openai

def behavioral_interview_simulator():  
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": "Simulate a behavioral interview for a machine learning role. Ask a STAR-formatted question."
        }]
    )
    print("Interviewer:", response.choices[0].message.content)

    while True:
        user_input = input("\nYour answer: ")
        if user_input.lower() == "exit":
            break
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Critique this STAR answer: {user_input}. Focus on specificity and metrics."
            }]
        )
        print("\nFeedback:", response.choices[0].message.content)

# Start the simulation:
behavioral_interview_simulator()

