"""
config.py — Central configuration for Sentinal
All env vars, constants, and settings live here.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=False)

# ─── LLM ──────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")   # flash = faster + cheaper

# ─── Retry / Resilience ───────────────────────────────────────
MAX_RETRIES: int    = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY: float  = float(os.getenv("RETRY_DELAY", "1.0"))          # seconds (doubles each attempt)

# ─── Database ─────────────────────────────────────────────────
DB_PATH: str        = os.getenv("DB_PATH", "sentinal.db")

# ─── App ──────────────────────────────────────────────────────
APP_HOST: str       = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int       = int(os.getenv("APP_PORT", "8080"))
DEBUG: bool         = os.getenv("DEBUG", "false").lower() == "true"

# ─── Memory ───────────────────────────────────────────────────
CONTEXT_LOG_LIMIT: int = int(os.getenv("CONTEXT_LOG_LIMIT", "3"))     # how many past logs to inject

# ─── Doomscroll Detection ─────────────────────────────────────
DOOMSCROLL_KEYWORDS: dict[str, list[str]] = {
    "social_media":    ["instagram", "reels", "tiktok", "facebook", "twitter", "x.com", "snapchat", "scroll", "feed"],
    "binge_watching":  ["youtube", "netflix", "hotstar", "prime", "binge", "episode", "series", "watch"],
    "gaming":          ["gaming", "games", "valorant", "pubg", "cod", "fortnite", "mobile legends"],
    "news":            ["news", "articles", "reddit", "headlines", "twitter news"],
    "general":         ["waste time", "wasted", "doing nothing", "procrastinat", "lazy", "killing time"],
}
