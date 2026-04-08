"""
tools/notes_tool.py — Mock MCP Notes / Memory Tool.

Stores motivational notes, engagement menu choices, and
session insights so the system can build a memory of what works
for each user over time.
"""
from __future__ import annotations
import sqlite3
from datetime import datetime
from config import DB_PATH


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER,
            note_type   TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_session_notes(session_id: int, motivation: str, insights: list[dict]) -> dict:
    """Save motivation message and insights as memory notes."""
    conn = _get_conn()
    now = datetime.now().isoformat()
    try:
        conn.execute(
            "INSERT INTO notes (session_id, note_type, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, "motivation", motivation, now)
        )
        for insight in insights:
            conn.execute(
                "INSERT INTO notes (session_id, note_type, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, "insight", f"{insight.get('pattern')}: {insight.get('suggestion')}", now)
            )
        conn.commit()
        return {"status": "success", "tool": "notes", "notes_saved": len(insights) + 1}
    except Exception as e:
        return {"status": "error", "tool": "notes", "error": str(e)}
    finally:
        conn.close()


def get_past_insights(limit: int = 5) -> list[str]:
    """Retrieve recent insights for memory-aware context injection."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT content FROM notes WHERE note_type = 'insight' ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [r["content"] for r in rows]
    finally:
        conn.close()
