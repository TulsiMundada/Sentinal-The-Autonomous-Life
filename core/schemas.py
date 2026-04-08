"""
core/schemas.py — Pydantic models for all structured data in Sentinal.

Every piece of data that flows through the system is typed and validated here.
This guarantees the LLM output is parseable and the UI always has clean data.
"""
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────────────
# Sub-structures (used inside AgentOutput)
# ──────────────────────────────────────────────────────────────────────────────

class Task(BaseModel):
    title: str
    priority: Literal["High", "Medium", "Low"]
    duration: str
    description: str
    category: Literal["learning", "health", "creative", "social", "professional", "other"] = "other"


class ScheduleSlot(BaseModel):
    time: str
    activity: str
    duration: str
    type: Literal["focus", "break", "review", "exercise", "social"]


class ExecutionStep(BaseModel):
    step: int
    action: str
    tool: Optional[str] = None
    duration: str


class ReflectionInsight(BaseModel):
    pattern: str
    suggestion: str
    impact: Literal["High", "Medium", "Low"]


# ──────────────────────────────────────────────────────────────────────────────
# Master Agent Output  (single LLM response → all 4 agents)
# ──────────────────────────────────────────────────────────────────────────────

class AgentOutput(BaseModel):
    """Complete output produced by one single LLM call in the orchestrator."""
    doomscroll_score: int = Field(ge=0, le=100)
    doomscroll_type: Literal["social_media", "binge_watching", "gaming", "news", "general"]
    alternative_activity: str
    motivation_message: str
    engagement_menu: List[str] = Field(min_length=3, max_length=5)

    # Planner Agent output
    tasks: List[Task] = Field(min_length=3, max_length=6)

    # Scheduler Agent output
    schedule: List[ScheduleSlot] = Field(min_length=3, max_length=7)

    # Execution Agent output
    execution_steps: List[ExecutionStep] = Field(min_length=3, max_length=7)

    # Reflection Agent output
    insights: List[ReflectionInsight] = Field(min_length=2, max_length=4)


# ──────────────────────────────────────────────────────────────────────────────
# API Request / Response models
# ──────────────────────────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    goal: str = Field(..., min_length=5, description="What the user was doing / wants to change")
    available_time: str = Field(default="2 hours", description="How much time is available")


class RunResponse(BaseModel):
    status: Literal["success", "fallback", "error"]
    message: str
    source: Literal["llm", "fallback"]
    data: Optional[AgentOutput] = None
    tools_used: List[str] = []
    session_id: Optional[int] = None


class LogEntry(BaseModel):
    id: int
    goal: str
    doomscroll_score: int
    alternative_activity: str
    tasks_count: int
    created_at: str


class DoomscrollInfo(BaseModel):
    detected: bool
    score: int
    type: str
    keywords_found: List[str]
