# ── Build stage ────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── App ────────────────────────────────────────────────────────
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# ── Runtime ────────────────────────────────────────────────────
EXPOSE 8080

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8080
ENV DB_PATH=/app/data/sentinal.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
