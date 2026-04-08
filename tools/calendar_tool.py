"""
tools/calendar_tool.py — Mock MCP Calendar Tool.

In a production system, this would connect to Google Calendar / Outlook
via an MCP server. Here it simulates the behavior and stores events
in SQLite so the UI can show "events scheduled."

Interface mirrors how real MCP tools work:
  - tool_name() → dict with status + data
"""
from __future__ import annotations
import sqlite3
from datetime import datetime, timedelta
from typing import Any
from config import DB_PATH


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER,
            title       TEXT NOT NULL,
            start_time  TEXT NOT NULL,
            duration    TEXT NOT NULL,
            event_type  TEXT DEFAULT 'focus',
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def schedule_events(session_id: int, schedule_slots: list[dict[str, Any]]) -> dict:
    """
    Simulate creating calendar events from schedule slots.
    Returns list of created event titles for the UI.
    """
    conn = _get_conn()
    now = datetime.now()
    created = []

    try:
        for i, slot in enumerate(schedule_slots):
            # Simulate a start time based on slot index (since times may be relative)
            start = now + timedelta(minutes=i * 35)
            conn.execute("""
                INSERT INTO calendar_events (session_id, title, start_time, duration, event_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                slot.get("activity", f"Block {i+1}"),
                start.strftime("%I:%M %p"),
                slot.get("duration", "30 mins"),
                slot.get("type", "focus"),
                now.isoformat(),
            ))
            created.append(slot.get("activity", f"Block {i+1}"))
        conn.commit()
        return {"status": "success", "tool": "calendar", "events_created": created}
    except Exception as e:
        return {"status": "error", "tool": "calendar", "error": str(e)}
    finally:
        conn.close()


def get_upcoming_events(session_id: int) -> list[dict]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM calendar_events WHERE session_id = ? ORDER BY id",
            (session_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
