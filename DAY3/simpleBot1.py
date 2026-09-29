import ollama
while True:
    question = input("Ask the question:") 
    if question.lower() == "exit":
        break
    response = ollama.chat(
        model = "llama3.2:3b",
        messages=[
            {
                "role":"system",
                "content":"give the answers in 2-3 lines only"
            },
            {
                "role":"user",
                "content":question
            }
        ]
    )
    print(response["message"]["content"])

    pip install streamlit