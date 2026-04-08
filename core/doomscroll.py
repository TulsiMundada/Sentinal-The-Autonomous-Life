"""
core/doomscroll.py — Behavioral pattern detection for Sentinal.

Uses a multi-signal scoring approach:
  - Platform / keyword matching  → 0–50 pts
  - Duration signals              → 0–30 pts
  - Frequency / repetition cues  → 0–20 pts

Score interpretation:
  0–30  → Low risk (minor unproductive phase)
  31–60 → Medium (classic doomscrolling)
  61–80 → High (significant time loss)
  81–100→ Critical (behavioral pattern requiring intervention)
"""
import re
from config import DOOMSCROLL_KEYWORDS
from core.schemas import DoomscrollInfo


# Duration signal patterns → additional score points
_DURATION_PATTERNS: list[tuple[re.Pattern, int]] = [
    (re.compile(r"\b(\d+)\s*hour", re.I),  0),   # hours → we extract the number
    (re.compile(r"\ball\s+day\b",   re.I), 30),
    (re.compile(r"\ball\s+night\b", re.I), 28),
    (re.compile(r"\bhours?\b",      re.I), 15),
    (re.compile(r"\bforever\b",     re.I), 25),
    (re.compile(r"\bwhole\s+day\b", re.I), 30),
]

_FREQUENCY_PATTERNS: list[tuple[re.Pattern, int]] = [
    (re.compile(r"\bagain\b",      re.I), 10),
    (re.compile(r"\bkeep\b",       re.I),  8),
    (re.compile(r"\bcan.t stop\b", re.I), 20),
    (re.compile(r"\baddicted\b",   re.I), 20),
    (re.compile(r"\bevery day\b",  re.I), 15),
    (re.compile(r"\bhabit\b",      re.I), 10),
]


def detect(text: str) -> DoomscrollInfo:
    """
    Run multi-signal doomscroll detection on free-form user input.
    Returns a DoomscrollInfo with score, type, and matched keywords.
    """
    text_lower = text.lower()
    score = 0
    keywords_found: list[str] = []
    detected_type = "general"
    type_scores: dict[str, int] = {k: 0 for k in DOOMSCROLL_KEYWORDS}

    # ── Signal 1: Platform / keyword matching (max 50 pts) ──────────────────
    for category, keywords in DOOMSCROLL_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                keywords_found.append(kw)
                type_scores[category] += 12

    # Pick the category with the highest match
    if type_scores:
        best = max(type_scores, key=lambda k: type_scores[k])
        if type_scores[best] > 0:
            detected_type = best
            score += min(type_scores[best], 50)

    # ── Signal 2: Duration signals (max 30 pts) ───────────────────────────
    for pattern, base_pts in _DURATION_PATTERNS:
        if pattern == _DURATION_PATTERNS[0][0]:          # numeric hours pattern
            m = pattern.search(text)
            if m:
                hours = int(m.group(1))
                # 1h → 5pts, 2h → 10, 3h → 18, 4h+ → 28
                duration_pts = min(5 * hours + max(0, (hours - 2) * 4), 28)
                score += duration_pts
        else:
            if pattern.search(text):
                score += base_pts

    # ── Signal 3: Frequency / habit cues (max 20 pts) ────────────────────
    freq_score = 0
    for pattern, pts in _FREQUENCY_PATTERNS:
        if pattern.search(text):
            freq_score += pts
    score += min(freq_score, 20)

    # ── Normalize ─────────────────────────────────────────────────────────
    score = min(score, 100)
    detected = score > 15 or len(keywords_found) > 0

    return DoomscrollInfo(
        detected=detected,
        score=score,
        type=detected_type if detected else "general",
        keywords_found=list(set(keywords_found)),
    )


def severity_label(score: int) -> str:
    if score <= 30:  return "Low"
    if score <= 60:  return "Medium"
    if score <= 80:  return "High"
    return "Critical"


def severity_color(score: int) -> str:
    if score <= 30:  return "#22c55e"   # green
    if score <= 60:  return "#f59e0b"   # amber
    if score <= 80:  return "#ef4444"   # red
    return "#7c3aed"                     # purple / critical
