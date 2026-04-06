# agents/scheduler.py

from services.gemini_client import generate

def scheduler_agent(tasks, available_time):
    prompt = f"""
You are a smart calendar optimizer.

Schedule the following tasks into available time slots.

Tasks:
{tasks}

Available Time:
{available_time}

Return a structured timetable.
"""
    return generate(prompt)
