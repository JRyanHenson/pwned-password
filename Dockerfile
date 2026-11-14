# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 2: Runner ───────────────────────────────────────────
FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS runner

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Runtime doesn't need pip; removing it also removes its vendored
# copies of urllib3/msgpack/setuptools that Trivy flags.
RUN pip uninstall -y pip

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
