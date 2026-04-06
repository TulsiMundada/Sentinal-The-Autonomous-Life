from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"""
[Fallback Response 🚀]

AI model was busy, but system continued.

Processed:
{prompt[:100]}

Suggested Actions:
- Convert scrolling into learning
- Follow structured schedule
- Track productivity
"""