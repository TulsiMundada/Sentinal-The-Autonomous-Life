# agents/reflection.py

from services.gemini_client import generate

def reflection_agent(logs):
    prompt = f"""
You are a performance analyst.

Analyze the following productivity logs:
{logs}

Give:
- Bottlenecks
- Wasted time patterns
- Improvement suggestions
"""
    return generate(prompt)
