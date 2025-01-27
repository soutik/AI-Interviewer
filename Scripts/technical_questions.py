import openai

def generate_technical_question(topic="binary trees", difficulty="medium"):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": f"Generate a {difficulty}-difficulty coding question about {topic}. Include a sample input/output."
        }]
    )
    return response.choices[0].message.content

# Example usage:
print(generate_technical_question(difficulty="hard", topic="dynamic programming"))
