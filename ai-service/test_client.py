from services.groq_client import generate_response

response = generate_response("Explain ESG risk in simple words")

print("\n✅ AI Response:\n")
print(response)