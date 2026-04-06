from fastapi import FastAPI, Form
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

from agents.orchestrator import run_full_cycle
from agents.planner import planner_agent
from agents.scheduler import scheduler_agent
from agents.reflection import reflection_agent
from agents.executor import execution_agent
from db.storage import get_recent_logs

app = FastAPI(title="Sentinal - Autonomous Life 🚀")

# ------------------------
# Request Models (API use)
# ------------------------

class PlanRequest(BaseModel):
    goal: str

class ScheduleRequest(BaseModel):
    tasks: list
    time: str

class ReflectRequest(BaseModel):
    logs: str

class ExecuteRequest(BaseModel):
    task: str

class FullCycleRequest(BaseModel):
    goal: str
    time: str


# ------------------------
# HTML UI (MAIN PAGE)
# ------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Sentinal AI</title>
        </head>
        <body style="font-family: Arial; padding: 30px;">
            <h1>🧠 Sentinal - Autonomous Life</h1>
            <h3>🚫 Doomscrolling → 🎯 Productivity Converter</h3>

            <form action="/run-ui" method="post">
                <label><b>Goal:</b></label><br>
                <input type="text" name="goal" style="width:400px;" placeholder="e.g. scrolling reels for 3 hours"><br><br>

                <label><b>Available Time:</b></label><br>
                <input type="text" name="time" value="2 hours"><br><br>

                <button type="submit">🚀 Run AI Agents</button>
            </form>

            <br><br>
            <a href="/logs">📜 View Logs</a>
        </body>
    </html>
    """


# ------------------------
# UI FORM HANDLER
# ------------------------

@app.post("/run-ui", response_class=HTMLResponse)
def run_ui(goal: str = Form(...), time: str = Form(...)):
    result = run_full_cycle(goal, time)

    data = result.get("data", result)

    return f"""
    <html>
        <body style="font-family: Arial; padding: 30px;">
            <h1>✅ Result</h1>

            <h3>🎯 Goal</h3>
            <p>{data.get("goal")}</p>

            <h3>🧩 Plan</h3>
            <pre>{data.get("plan")}</pre>

            <h3>📅 Schedule</h3>
            <pre>{data.get("schedule")}</pre>

            <h3>⚡ Execution</h3>
            <pre>{data.get("execution")}</pre>

            <h3>🧠 Reflection</h3>
            <pre>{data.get("reflection")}</pre>

            <br><br>
            <a href="/">⬅️ Go Back</a>
        </body>
    </html>
    """


# ------------------------
# API ROUTES (for testing)
# ------------------------

@app.post("/run")
def run(request: FullCycleRequest):
    return run_full_cycle(request.goal, request.time)


@app.post("/plan")
def plan(request: PlanRequest):
    return {"plan": planner_agent(request.goal)}


@app.post("/schedule")
def schedule(request: ScheduleRequest):
    return {"schedule": scheduler_agent(request.tasks, request.time)}


@app.post("/reflect")
def reflect(request: ReflectRequest):
    return {"reflection": reflection_agent(request.logs)}


@app.post("/execute")
def execute(request: ExecuteRequest):
    return {"execution": execution_agent(request.task)}


@app.get("/logs")
def logs():
    return {"logs": get_recent_logs()}