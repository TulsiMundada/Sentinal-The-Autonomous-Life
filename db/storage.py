"""
db/storage.py — Thread-safe SQLite persistence for Sentinal.

KEY FIX from original code:
  The original used a MODULE-LEVEL sqlite3.connect() shared across
  all threads in FastAPI. This causes "SQLite objects created in a
  thread can only be used in that same thread" errors.

  Fix: Open a fresh connection per function call, close when done.
  SQLite is fast enough for this at hackathon / prototype scale.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from typing import Optional

from config import DB_PATH, CONTEXT_LOG_LIMIT


# ─── Schema Bootstrap ─────────────────────────────────────────────────────────

def _bootstrap():
    """Create tables on first import. Called once at module load."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            goal                TEXT    NOT NULL,
            available_time      TEXT,
            doomscroll_score    INTEGER DEFAULT 0,
            doomscroll_type     TEXT,
            alternative_activity TEXT,
            tasks_json          TEXT,
            schedule_json       TEXT,
            execution_json      TEXT,
            insights_json       TEXT,
            engagement_menu     TEXT,
            motivation_message  TEXT,
            source              TEXT DEFAULT 'llm',
            tools_used          TEXT,
            created_at          TEXT    NOT NULL
        );
    """)
    conn.commit()
    conn.close()


_bootstrap()


# ─── Write ────────────────────────────────────────────────────────────────────

def save_session(
    goal: str,
    available_time: str,
    output,              # AgentOutput
    source: str,
    tools_used: list[str],
) -> int:
    """Persist a completed session. Returns the new session ID."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("""
            INSERT INTO sessions (
                goal, available_time, doomscroll_score, doomscroll_type,
                alternative_activity, tasks_json, schedule_json, execution_json,
                insights_json, engagement_menu, motivation_message, source,
                tools_used, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            goal,
            available_time,
            output.doomscroll_score,
            output.doomscroll_type,
            output.alternative_activity,
            json.dumps([t.model_dump() for t in output.tasks]),
            json.dumps([s.model_dump() for s in output.schedule]),
            json.dumps([e.model_dump() for e in output.execution_steps]),
            json.dumps([i.model_dump() for i in output.insights]),
            json.dumps(output.engagement_menu),
            output.motivation_message,
            source,
            json.dumps(tools_used),
            datetime.now().isoformat(),
        ))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ─── Read ─────────────────────────────────────────────────────────────────────

def get_recent_sessions(limit: int = 10) -> list[dict]:
    """Fetch recent sessions for the logs page."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            # Parse JSON fields
            for field in ("tasks_json", "schedule_json", "execution_json", "insights_json"):
                try:
                    d[field] = json.loads(d[field] or "[]")
                except Exception:
                    d[field] = []
            try:
                d["engagement_menu"] = json.loads(d["engagement_menu"] or "[]")
            except Exception:
                d["engagement_menu"] = []
            try:
                d["tools_used"] = json.loads(d["tools_used"] or "[]")
            except Exception:
                d["tools_used"] = []
            result.append(d)
        return result
    finally:
        conn.close()


def get_context_for_prompt(limit: Optional[int] = None) -> str:
    """
    Build a concise context string from past sessions
    to inject into the master prompt for memory-aware suggestions.
    """
    n = limit or CONTEXT_LOG_LIMIT
    sessions = get_recent_sessions(limit=n)
    if not sessions:
        return ""
    lines = []
    for i, s in enumerate(reversed(sessions), 1):
        lines.append(
            f"Session {i} ({s['created_at'][:10]}): "
            f"Behavior={s['doomscroll_type']} Score={s['doomscroll_score']}/100 | "
            f"Alternative chosen: {s['alternative_activity']}"
        )
        tasks = s.get("tasks_json", [])
        if tasks:
            lines.append(f"  Tasks: {', '.join(t['title'] for t in tasks[:3])}")
    return "\n".join(lines)
