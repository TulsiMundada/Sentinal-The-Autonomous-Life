"""
core/fallback.py — Zero-API fallback engine.

When Gemini is down / rate-limited / key is missing,
Sentinal still produces a meaningful, structured response
using rule-based logic and pre-written templates.

This means the system NEVER fully breaks — it degrades gracefully.
"""
from __future__ import annotations
import random
from core.schemas import (
    AgentOutput, Task, ScheduleSlot,
    ExecutionStep, ReflectionInsight
)


# ─── Template banks (randomized so repeated calls feel different) ─────────────

_TASKS: dict[str, list[Task]] = {
    "social_media": [
        Task(title="Digital Detox Walk", priority="High", duration="30 mins",
             description="Go for a walk without your phone. Notice 5 things around you.", category="health"),
        Task(title="Learn something new", priority="High", duration="45 mins",
             description="Pick a topic you've been curious about and read/watch one focused resource.", category="learning"),
        Task(title="Creative journaling", priority="Medium", duration="20 mins",
             description="Write 3 things you want to accomplish this week.", category="creative"),
        Task(title="Connect meaningfully", priority="Medium", duration="30 mins",
             description="Call or text ONE person you haven't spoken to in a while — a real conversation.", category="social"),
    ],
    "binge_watching": [
        Task(title="Active movement break", priority="High", duration="25 mins",
             description="Do a 25-minute Pomodoro of exercise — stretches, yoga, or a jog.", category="health"),
        Task(title="Project work session", priority="High", duration="60 mins",
             description="Work on a personal project or skill you've been putting off.", category="professional"),
        Task(title="Meal prep / cooking", priority="Medium", duration="40 mins",
             description="Cook a healthy meal instead of ordering — engages hands and mind.", category="health"),
        Task(title="Read a book chapter", priority="Medium", duration="30 mins",
             description="Read for 30 mins from a book you've been meaning to finish.", category="learning"),
    ],
    "gaming": [
        Task(title="Physical activity", priority="High", duration="30 mins",
             description="Channel that competitive energy into sport — a jog, cycling, or gym.", category="health"),
        Task(title="Build something real", priority="High", duration="60 mins",
             description="Work on a side project, coding challenge, or DIY task.", category="professional"),
        Task(title="Social planning", priority="Medium", duration="20 mins",
             description="Plan an outing or activity with friends in the physical world.", category="social"),
    ],
    "general": [
        Task(title="Priority audit", priority="High", duration="20 mins",
             description="Write your top 3 goals for the next 7 days and pick ONE to start today.", category="professional"),
        Task(title="Physical reset", priority="High", duration="30 mins",
             description="Step away from the screen — walk, stretch, or hydrate.", category="health"),
        Task(title="Deep work session", priority="Medium", duration="45 mins",
             description="Do focused work on your most important pending task.", category="professional"),
        Task(title="Skill building", priority="Medium", duration="30 mins",
             description="Spend 30 minutes learning a skill that aligns with your goals.", category="learning"),
    ],
}

_MOTIVATION: dict[str, list[str]] = {
    "social_media":    [
        "Every minute you reclaim from the feed is a minute invested in your own story.",
        "The algorithm is designed to consume your time — you are designed to create.",
    ],
    "binge_watching":  [
        "Real life has better plot twists than any series — you just have to show up for them.",
        "One focused hour of action beats ten hours of watching someone else live their story.",
    ],
    "gaming":          [
        "The best game you can level up in is your own life.",
        "Channel that competitive drive into building something that lasts.",
    ],
    "general":         [
        "You already recognized the pattern — that's step one. Now take step two.",
        "Small redirects compound into massive life changes.",
    ],
}

_ENGAGEMENT_MENUS: dict[str, list[str]] = {
    "social_media":    ["30-min focused reading", "Cook a new recipe", "Call a friend", "Gym session", "Learn a new skill on YouTube (structured, not scrolling)"],
    "binge_watching":  ["Create something (draw, write, code)", "Plan your week", "Go for a walk", "Join an online community around a hobby", "Work on a side project"],
    "gaming":          ["Gym / sport session", "Build a side project", "Board games with friends", "Coding challenge", "Plan a trip or event"],
    "general":         ["Deep work session", "Journaling", "Read for 30 mins", "Exercise", "Organize your workspace"],
}

_INSIGHTS: list[ReflectionInsight] = [
    ReflectionInsight(pattern="Passive consumption loop detected", suggestion="Set a screen time limit in phone settings for the top app", impact="High"),
    ReflectionInsight(pattern="No structured alternative available", suggestion="Pre-plan 3 default activities for when boredom hits", impact="High"),
    ReflectionInsight(pattern="Likely triggered by boredom or avoidance", suggestion="Identify the underlying task you're avoiding and start with just 5 minutes of it", impact="Medium"),
    ReflectionInsight(pattern="No accountability system", suggestion="Share your plan with one person or track it in a habit app", impact="Medium"),
]


def generate_fallback(doomscroll_type: str, available_time: str) -> AgentOutput:
    """
    Build a complete AgentOutput without any LLM call.
    Uses randomized templates so repeated calls aren't identical.
    """
    dtype = doomscroll_type if doomscroll_type in _TASKS else "general"
    tasks = _TASKS[dtype]
    motivation = random.choice(_MOTIVATION.get(dtype, _MOTIVATION["general"]))
    menu = _ENGAGEMENT_MENUS.get(dtype, _ENGAGEMENT_MENUS["general"])

    # Build a simple time-based schedule
    schedule = [
        ScheduleSlot(time="Now → +5 min",   activity="Take a breath, put phone face-down",    duration="5 mins",  type="break"),
        ScheduleSlot(time="+5 → +35 min",   activity=tasks[0].title,                          duration="30 mins", type="focus"),
        ScheduleSlot(time="+35 → +40 min",  activity="Short break — water, stretch",           duration="5 mins",  type="break"),
        ScheduleSlot(time="+40 → +70 min",  activity=tasks[1].title if len(tasks) > 1 else "Continued focus", duration="30 mins", type="focus"),
        ScheduleSlot(time="+70 → +80 min",  activity="Reflect on what you accomplished",       duration="10 mins", type="review"),
    ]

    execution_steps = [
        ExecutionStep(step=1, action="Close all social / entertainment apps right now", tool=None, duration="1 min"),
        ExecutionStep(step=2, action="Set a 30-minute timer on your phone", tool="Clock app", duration="1 min"),
        ExecutionStep(step=3, action=f"Start: {tasks[0].description}", tool=None, duration="30 mins"),
        ExecutionStep(step=4, action="After timer — drink water and do 10 push-ups", tool=None, duration="5 mins"),
        ExecutionStep(step=5, action="Log what you completed in a notes app", tool="Notes app", duration="2 mins"),
    ]

    return AgentOutput(
        doomscroll_score=55,
        doomscroll_type=dtype,  # type: ignore[arg-type]
        alternative_activity=tasks[0].title,
        motivation_message=motivation,
        engagement_menu=menu,
        tasks=tasks,
        schedule=schedule,
        execution_steps=execution_steps,
        insights=random.sample(_INSIGHTS, k=min(3, len(_INSIGHTS))),
    )
