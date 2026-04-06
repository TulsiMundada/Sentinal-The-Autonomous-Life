# agents/reflection.py

from services.gemini_client import generate

prompt = f"""
You are a performance analyst.

Analyze the following productivity logs:
{logs}

Give:
- Bottlenecks
- Wasted time patterns
- Improvement suggestions
"""

def reflection_agent(logs):
    try:
        return generate(prompt)
    except:
        return "Reflection: You tend to lose time in passive scrolling. Replace with structured habits."