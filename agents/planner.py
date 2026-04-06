# agents/planner.py

from services.gemini_client import generate

def planner_agent(goal):
    prompt = f"""
You are a productivity strategist.

Break the following goal into:
- Clear tasks
- Priorities (High/Medium/Low)
- Estimated time

Goal:
{goal}
"""

    return generate(prompt)
