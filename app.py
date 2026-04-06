# app.py

from flask import Flask, request, jsonify
from agents.planner import planner_agent
from agents.scheduler import scheduler_agent
from agents.reflection import reflection_agent
from agents.executor import execution_agent

app = Flask(__name__)

@app.route("/")
def home():
    return "Life Debugger AI Running 🚀"

@app.route("/plan", methods=["POST"])
def plan():
    data = request.json
    goal = data.get("goal")
    result = planner_agent(goal)
    return jsonify({"plan": result})

@app.route("/schedule", methods=["POST"])
def schedule():
    data = request.json
    result = scheduler_agent(data["tasks"], data["time"])
    return jsonify({"schedule": result})

@app.route("/reflect", methods=["POST"])
def reflect():
    data = request.json
    result = reflection_agent(data["logs"])
    return jsonify({"reflection": result})

@app.route("/execute", methods=["POST"])
def execute():
    data = request.json
    result = execution_agent(data["task"])
    return jsonify({"execution": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
