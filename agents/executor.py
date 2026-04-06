# agents/executor.py

from services.gemini_client import generate

def execution_agent(task):
    prompt = f"""
You are an execution coach.

Convert this task into:
- Step-by-step actions
- Tools required
- Quick start guide

Task:
{task}
"""
    return generate(prompt)
