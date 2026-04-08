"""
main.py — Sentinal FastAPI Application

Endpoints:
  GET  /           → HTML homepage
  POST /run-ui     → Form submission → HTML result
  POST /run        → JSON API (for Swagger / programmatic use)
  GET  /logs       → HTML session history
  GET  /api/logs   → JSON session history
  GET  /health     → Health check
  GET  /docs       → Auto-generated Swagger UI (FastAPI built-in)
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from agents.orchestrator import run as orchestrator_run
from core.schemas import RunRequest, RunResponse
from db.storage import get_recent_sessions
from config import DEBUG

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
)
logger = logging.getLogger("sentinal.api")


# ─── App Lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Sentinal starting up…")
    yield
    logger.info("🛑 Sentinal shutting down.")


# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sentinal — The Autonomous Life",
    description=(
        "Multi-agent AI system that detects doomscrolling and replaces it "
        "with structured, meaningful alternatives. "
        "4 agents coordinated via a single LLM call."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

templates = Jinja2Templates(directory="templates")


# ─── HTML Routes ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Landing page with input form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/run-ui", response_class=HTMLResponse)
def run_ui(
    request: Request,
    goal: str = Form(...),
    available_time: str = Form("1 hour"),
):
    """
    HTML form handler — runs the full agent pipeline
    and renders the result page.
    """
    logger.info(f"[UI] POST /run-ui | goal='{goal[:60]}' | time={available_time}")

    try:
        result: RunResponse = orchestrator_run(
            RunRequest(goal=goal, available_time=available_time)
        )
    except Exception as e:
        logger.exception(f"Orchestrator error: {e}")
        return HTMLResponse(
            content=f"""
            <html><body style="font-family:monospace; padding:2rem; background:#0a0a0f; color:#ef4444;">
            <h2>❌ Unexpected Error</h2>
            <pre>{e}</pre>
            <a href="/" style="color:#7c3aed;">← Go back</a>
            </body></html>
            """,
            status_code=500,
        )

    return templates.TemplateResponse("result.html", {
        "request":   request,
        "data":      result.data,
        "status":    result.status,
        "message":   result.message,
        "source":    result.source,
        "tools_used": result.tools_used,
        "session_id": result.session_id,
    })


@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request):
    """Session history HTML page."""
    sessions = get_recent_sessions(limit=20)
    return templates.TemplateResponse("logs.html", {
        "request":  request,
        "sessions": sessions,
    })


# ─── JSON API Routes ──────────────────────────────────────────────────────────

@app.post("/run", response_model=RunResponse, tags=["API"])
def run_api(request: RunRequest):
    """
    **Main API endpoint.**

    Accepts a JSON body with `goal` and `available_time`,
    runs all four agents via a single LLM call,
    and returns a fully structured RunResponse.

    Example:
    ```json
    {"goal": "I spent 4 hours scrolling Instagram", "available_time": "2 hours"}
    ```
    """
    logger.info(f"[API] POST /run | goal='{request.goal[:60]}'")
    return orchestrator_run(request)


@app.get("/api/logs", tags=["API"])
def api_logs(limit: int = 10):
    """Return recent session logs as JSON."""
    return {"sessions": get_recent_sessions(limit=limit)}


@app.get("/health", tags=["System"])
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "sentinal", "version": "2.0.0"}


# ─── Dev entrypoint ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from config import APP_HOST, APP_PORT
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)
