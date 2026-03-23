# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 2: Runner ───────────────────────────────────────────
FROM python:3.12-slim AS runner

RUN useradd --system --uid 1001 --no-create-home appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

COPY app.py .
COPY templates/ ./templates/

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "2", "--timeout", "30", "app:app"]
