from fastapi import FastAPI
from pydantic import BaseModel
from agents.planner import planner_agent
from agents.scheduler import scheduler_agent
from agents.reflection import reflection_agent
from agents.executor import execution_agent

app = FastAPI(title="Life Debugger AI 🚀")

# ------------------------
# Request Models
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

# ------------------------
# Routes
# ------------------------

@app.get("/")
def home():
    return {"status": "Life Debugger AI Running 🚀"}

@app.post("/plan")
def plan(request: PlanRequest):
    result = planner_agent(request.goal)
    return {"plan": result}

@app.post("/schedule")
def schedule(request: ScheduleRequest):
    result = scheduler_agent(request.tasks, request.time)
    return {"schedule": result}

@app.post("/reflect")
def reflect(request: ReflectRequest):
    result = reflection_agent(request.logs)
    return {"reflection": result}

@app.post("/execute")
def execute(request: ExecuteRequest):
    result = execution_agent(request.task)
    return {"execution": result}
