"""
core/llm.py — Gemini client with:
  • Retry + exponential back-off
  • Forced JSON output (response_mime_type)
  • JSON extraction from markdown fences
  • Pydantic validation of the response
  • Returns None on total failure (fallback handled by orchestrator)
"""
import json
import logging
import time
from typing import Optional

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_RETRIES, RETRY_DELAY
from core.schemas import AgentOutput

logger = logging.getLogger("sentinal.llm")

# Build client once at import time — re-used for every call
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def _strip_json_fences(text: str) -> str:
    """Remove ```json … ``` wrappers that some model versions emit."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop opening fence line and closing fence line
        inner = []
        in_block = False
        for line in lines:
            if line.startswith("```") and not in_block:
                in_block = True
                continue
            if line.startswith("```") and in_block:
                break
            if in_block:
                inner.append(line)
        text = "\n".join(inner)
    return text.strip()


def call_llm(prompt: str) -> Optional[AgentOutput]:
    """
    Send one prompt to Gemini, ask for JSON, parse + validate.

    Returns:
        AgentOutput if successful (possibly after retries)
        None        if all retries exhausted (caller handles fallback)
    """
    if not _client:
        logger.error("No GEMINI_API_KEY set — skipping LLM call.")
        return None

    last_err = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"LLM attempt {attempt}/{MAX_RETRIES}")
            response = _client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )
            raw = response.text or ""
            cleaned = _strip_json_fences(raw)
            data = json.loads(cleaned)
            output = AgentOutput(**data)
            logger.info("LLM call succeeded.")
            return output

        except json.JSONDecodeError as e:
            logger.warning(f"Attempt {attempt}: JSON parse error — {e}")
            last_err = e

        except Exception as e:
            logger.warning(f"Attempt {attempt}: API error — {e}")
            last_err = e
            # Check if it's a rate-limit / quota error → back off longer
            err_str = str(e).lower()
            if any(x in err_str for x in ("429", "quota", "rate", "503", "unavailable")):
                backoff = RETRY_DELAY * (2 ** (attempt - 1))
                logger.info(f"Rate limit hit — backing off {backoff:.1f}s")
                time.sleep(backoff)
                continue

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY * attempt)

    logger.error(f"All {MAX_RETRIES} LLM attempts failed. Last: {last_err}")
    return None
