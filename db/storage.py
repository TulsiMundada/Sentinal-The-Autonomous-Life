import sqlite3
from datetime import datetime

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT,
    plan TEXT,
    schedule TEXT,
    execution TEXT,
    reflection TEXT,
    created_at TEXT
)
""")
conn.commit()

def save_log(goal, plan, schedule, execution, reflection):
    cursor.execute("""
    INSERT INTO logs (goal, plan, schedule, execution, reflection, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (goal, plan, schedule, execution, reflection, datetime.now()))
    conn.commit()

def get_recent_logs(limit=5):
    cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    return cursor.fetchall()
