from agents.planner import planner_agent
from agents.scheduler import scheduler_agent
from agents.executor import execution_agent
from agents.reflection import reflection_agent
from db.storage import save_log


def detect_doomscrolling(goal):
    keywords = ["instagram", "reels", "scroll", "youtube", "waste time"]
    return any(k in goal.lower() for k in keywords)


def run_full_cycle(goal, available_time):

    # 🔥 Step 0: Detect doomscrolling
    if detect_doomscrolling(goal):
        goal = f"""
User is stuck in doomscrolling behavior.

Convert this into a productive and engaging alternative activity.

Original Input: {goal}
"""

    # Step 1: Plan
    plan = planner_agent(goal)

    # Step 2: Schedule
    schedule = scheduler_agent(plan, available_time)

    # Step 3: Execute
    execution = execution_agent(plan)

    # Step 4: Reflect
    reflection = reflection_agent(plan)

    # Step 5: Save to DB
    save_log(goal, plan, schedule, execution, reflection)

    return {
        "goal": goal,
        "plan": plan,
        "schedule": schedule,
        "execution": execution,
        "reflection": reflection
    }