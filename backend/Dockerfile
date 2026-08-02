# Equa API — production image for ECS Fargate
# Build from repo root:
#   docker build -f backend/Dockerfile -t equa-api .

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 equa

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini .
COPY backend ./backend

RUN chmod +x /app/backend/docker-entrypoint.sh \
    && sed -i 's/\r$//' /app/backend/docker-entrypoint.sh \
    && chown -R equa:equa /app

USER equa

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1

ENTRYPOINT ["sh", "/app/backend/docker-entrypoint.sh"]
