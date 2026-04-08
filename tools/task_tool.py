"""
tools/task_tool.py — Mock MCP Task Storage Tool.

Persists the planned tasks so users can track completion.
In production: connects to Todoist / Notion / Linear via MCP.
"""
from __future__ import annotations
import sqlite3
from datetime import datetime
from config import DB_PATH


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER,
            title       TEXT NOT NULL,
            priority    TEXT NOT NULL,
            duration    TEXT NOT NULL,
            category    TEXT NOT NULL,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_tasks(session_id: int, tasks: list[dict]) -> dict:
    """Persist the planner's task list for this session."""
    conn = _get_conn()
    now = datetime.now().isoformat()
    saved = []
    try:
        for task in tasks:
            conn.execute("""
                INSERT INTO tasks (session_id, title, priority, duration, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                task.get("title", "Task"),
                task.get("priority", "Medium"),
                task.get("duration", "30 mins"),
                task.get("category", "other"),
                now,
            ))
            saved.append(task.get("title"))
        conn.commit()
        return {"status": "success", "tool": "task_store", "tasks_saved": saved}
    except Exception as e:
        return {"status": "error", "tool": "task_store", "error": str(e)}
    finally:
        conn.close()


def get_tasks_for_session(session_id: int) -> list[dict]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE session_id = ? ORDER BY id",
            (session_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
