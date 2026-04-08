"""
agents/orchestrator.py — Central brain of Sentinal.

THE KEY DESIGN:
  One function (run) → One LLM call → All four agent outputs.

Flow:
  1. Detect doomscrolling behavior (rule-based, no API)
  2. Fetch past context from DB (no API)
  3. Build master prompt
  4. ONE Gemini call → structured JSON → AgentOutput
  5. If LLM fails → rule-based fallback (no API needed)
  6. Run MCP-style tools (calendar, notes, tasks) — synchronously
  7. Persist session to DB
  8. Return RunResponse to FastAPI
"""
from __future__ import annotations
import logging
from typing import Tuple

from core import doomscroll as ds
from core.llm import call_llm
from core.fallback import generate_fallback
from core.schemas import AgentOutput, RunRequest, RunResponse
from db.storage import get_context_for_prompt, save_session
from prompts.master_prompt import build as build_prompt
from tools import calendar_tool, notes_tool, task_tool

logger = logging.getLogger("sentinal.orchestrator")


def _run_mcp_tools(session_id: int, output: AgentOutput) -> list[str]:
    """
    Invoke all MCP-style tools after LLM output is confirmed.
    Returns list of tool names that ran successfully.
    """
    tools_used: list[str] = []

    # ── Tool 1: Calendar — schedule the plan ─────────────────────────────
    cal_result = calendar_tool.schedule_events(
        session_id=session_id,
        schedule_slots=[s.model_dump() for s in output.schedule],
    )
    if cal_result.get("status") == "success":
        tools_used.append("calendar")
        logger.info(f"Calendar: {len(cal_result.get('events_created', []))} events created")

    # ── Tool 2: Notes — save memory ───────────────────────────────────────
    notes_result = notes_tool.save_session_notes(
        session_id=session_id,
        motivation=output.motivation_message,
        insights=[i.model_dump() for i in output.insights],
    )
    if notes_result.get("status") == "success":
        tools_used.append("notes")

    # ── Tool 3: Task Store — persist task list ────────────────────────────
    task_result = task_tool.save_tasks(
        session_id=session_id,
        tasks=[t.model_dump() for t in output.tasks],
    )
    if task_result.get("status") == "success":
        tools_used.append("task_store")

    return tools_used


def run(request: RunRequest) -> RunResponse:
    """
    Main orchestration entry point.

    Called by FastAPI on POST /run.
    Coordinates: detection → context → LLM → tools → DB → response.
    """
    logger.info(f"Orchestrator: new request — goal='{request.goal[:60]}...'")

    # ── Step 1: Doomscroll Detection (zero API, instant) ──────────────────
    doom_info = ds.detect(request.goal)
    logger.info(f"Doomscroll: detected={doom_info.detected} score={doom_info.score} type={doom_info.type}")

    # ── Step 2: Memory / Past Context (zero API) ──────────────────────────
    past_context = get_context_for_prompt()

    # ── Step 3: Build Master Prompt ───────────────────────────────────────
    prompt = build_prompt(
        goal=request.goal,
        available_time=request.available_time,
        doomscroll_type=doom_info.type,
        doomscroll_score=doom_info.score,
        past_context=past_context,
    )

    # ── Step 4: ONE LLM call → all four agent outputs ─────────────────────
    output: AgentOutput | None = call_llm(prompt)
    source = "llm"

    # ── Step 5: Graceful fallback if LLM failed ───────────────────────────
    if output is None:
        logger.warning("LLM unavailable — using rule-based fallback")
        output = generate_fallback(
            doomscroll_type=doom_info.type,
            available_time=request.available_time,
        )
        source = "fallback"

    # ── Step 6: Persist to DB (get session_id) ────────────────────────────
    session_id = save_session(
        goal=request.goal,
        available_time=request.available_time,
        output=output,
        source=source,
        tools_used=[],  # will update after tool calls
    )

    # ── Step 7: MCP-style tools ───────────────────────────────────────────
    tools_used = _run_mcp_tools(session_id=session_id, output=output)
    logger.info(f"Tools used: {tools_used}")

    # ── Step 8: Return structured response ───────────────────────────────
    return RunResponse(
        status="success" if source == "llm" else "fallback",
        message=(
            "✅ Sentinal analysis complete — AI agents coordinated."
            if source == "llm"
            else "⚠️ Running in offline mode — AI fallback activated."
        ),
        source=source,  # type: ignore[arg-type]
        data=output,
        tools_used=tools_used,
        session_id=session_id,
    )
