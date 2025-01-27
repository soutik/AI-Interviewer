import openai

def evaluate_code_solution(question, code):
    prompt = f"""  
    Question: {question}  
    My solution: {code}  

    Analyze this code for:  
    1. Time/space complexity  
    2. Edge cases missed  
    3. Alternative approaches (e.g., iterative vs. recursive)  
    """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Example usage:
question = "Reverse a linked list."
code = """  
def reverse_list(head):  
    prev = None  
    while head:  
        next_node = head.next  
        head.next = prev  
        prev = head  
        head = next_node  
    return prev  
"""
print(evaluate_code_solution(question, code))
