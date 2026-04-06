# agents/executor.py

from services.gemini_client import generate

prompt = f"""
You are an execution coach.

Convert this task into:
- Step-by-step actions
- Tools required
- Quick start guide

Task:
{task}
"""
def execution_agent(task):
    try:
        return generate(prompt)
    except:
        return "Step-by-step execution: Start small, 10-min focus session, remove distractions."