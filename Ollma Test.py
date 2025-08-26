import ollama

MODEL_NAME = "gpt-oss:20b"

prompt = "Hello buddy."

# Call the model
response = ollama.chat(
    model=MODEL_NAME,
    messages=[{"role": "user", "content": prompt}],
)

# Access the content from the response
text_output = response.message.content
print(text_output)
