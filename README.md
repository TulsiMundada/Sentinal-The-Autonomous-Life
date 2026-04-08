# 🛡️ Sentinal — The Autonomous Life

> **Multi-agent AI system that detects doomscrolling and transforms passive digital consumption into structured, meaningful action.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-4285F4?logo=google)](https://ai.google.dev)

---

## 🌍 What is Sentinal?

Sentinal is a **behavioral AI system** — not a generic productivity app. It:

1. **Detects** when you're stuck in doomscrolling / passive consumption
2. **Breaks** the pattern with structured, personalized alternatives
3. **Plans, schedules, and guides** execution via 4 specialized AI agents
4. **Reflects** on your behavior patterns and improves over time with memory

---

## 🧠 Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                          │
│  ① Doomscroll Detection (rule-based, 0 API calls)       │
│  ② Past Context Injection (memory from DB)              │
│  ③ ONE Gemini Call → structured JSON                    │
│  ④ Fallback Engine (if API fails)                       │
│  ⑤ MCP Tools (Calendar / Notes / Task Store)            │
│  ⑥ DB Persistence                                       │
└─────────────────────────────────────────────────────────┘
         │ Single LLM Response
         ├──────────────────────────────────┐
         │                                  │
    ┌────▼────┐  ┌──────────┐  ┌────────┐  ┌──────────┐
    │ PLANNER │  │SCHEDULER │  │EXECUTOR│  │REFLECTOR │
    │ Tasks   │  │Time Slots│  │Steps   │  │Insights  │
    └─────────┘  └──────────┘  └────────┘  └──────────┘
```

### Key Design Decisions

| Problem | Solution |
|---------|----------|
| 4 LLM calls → rate limits | **1 master prompt** → all 4 agent outputs |
| API failure = system crash | **Rule-based fallback** produces valid output offline |
| No structured output | **Pydantic schemas** + `response_mime_type: application/json` |
| Thread-unsafe SQLite | **Per-call connections**, no module-level state |
| No memory | **Past sessions injected** into every new prompt |
| No tool integration | **MCP-style tools**: Calendar, Notes, Task Store |

---

## 📂 Project Structure

```
sentinal/
├── main.py                    # FastAPI app + all routes
├── config.py                  # All env vars and constants
├── requirements.txt
├── Dockerfile
├── .env.example
│
├── agents/
│   └── orchestrator.py        # Central brain — coordinates all agents
│
├── core/
│   ├── schemas.py             # Pydantic models (AgentOutput, RunRequest, etc.)
│   ├── llm.py                 # Gemini client with retry + JSON parsing
│   ├── doomscroll.py          # Multi-signal behavioral detection engine
│   └── fallback.py            # Rule-based fallback (zero API calls needed)
│
├── prompts/
│   └── master_prompt.py       # Single master prompt for all 4 agents
│
├── db/
│   └── storage.py             # Thread-safe SQLite persistence
│
├── tools/                     # MCP-style tool integrations
│   ├── calendar_tool.py       # Mock calendar event scheduler
│   ├── notes_tool.py          # Memory / insight storage
│   └── task_tool.py           # Task persistence tool
│
└── templates/                 # Jinja2 HTML templates
    ├── index.html             # Input form
    ├── result.html            # Agent output dashboard
    └── logs.html              # Session history
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd sentinal
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### 3. Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Open: http://localhost:8080

### 4. Docker

```bash
docker build -t sentinal .
docker run -p 8080:8080 -e GEMINI_API_KEY=your_key sentinal
```

---

## 🔌 API Reference

| Method | Endpoint     | Description                    |
|--------|-------------|-------------------------------|
| GET    | `/`          | HTML input form                |
| POST   | `/run-ui`    | Form submit → HTML result      |
| POST   | `/run`       | JSON API → RunResponse         |
| GET    | `/logs`      | HTML session history           |
| GET    | `/api/logs`  | JSON session history           |
| GET    | `/health`    | Health check                   |
| GET    | `/docs`      | Swagger UI (auto-generated)    |

### POST /run — Example

```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"goal": "I spent 5 hours scrolling Instagram reels", "available_time": "2 hours"}'
```

---

## 🛡️ Resilience

Sentinal is designed to **never fully break**:

1. **Retry logic** — up to 3 attempts with exponential backoff
2. **Rate limit detection** — backs off automatically on 429/503 errors
3. **JSON fallback** — strips markdown fences from LLM responses
4. **Pydantic validation** — if JSON is malformed, triggers fallback
5. **Rule-based fallback** — works with ZERO API access

---

## 🚀 Deployment (Google Cloud Run)

```bash
gcloud run deploy sentinal \
  --source . \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your_key \
  --allow-unauthenticated
```

---

## 🏆 Hackathon Highlights

- ✅ True multi-agent coordination (4 agents, 1 LLM call)
- ✅ Behavioral AI — not just a to-do list
- ✅ Always-on fallback — works even without internet
- ✅ Memory-aware — improves suggestions from past sessions
- ✅ MCP-style tool integration (calendar, notes, task store)
- ✅ Production-grade: retry logic, structured output, thread-safe DB
- ✅ Clean dark UI with agent visualization
