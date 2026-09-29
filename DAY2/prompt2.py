import ollama 
response = ollama.chat(
    model = "llama3.2:3b",
    messages=[
        {
            "role":"user",
            "content":"give the answers in 2-3 lines only"
        }
    ]
)
print(response["message"]["content"])