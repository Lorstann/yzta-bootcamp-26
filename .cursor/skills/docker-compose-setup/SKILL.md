---
name: docker-compose-setup
description: Provides a docker-compose.yml for local development with API, frontend, Postgres, and Redis services including health checks, named volumes, and dependency conditions. Use when the user asks to set up docker-compose, a local dev setup, or containerize the app.
---

# docker-compose-setup

**Trigger**: "docker-compose", "local dev setup", "containerize"

**Template**:
```yaml
version: '3.9'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    ports:
      - "3001:3001"
    environment:
      NODE_ENV: development
      DATABASE_URL: postgresql://postgres:postgres@db:5432/hackathon
      REDIS_URL: redis://cache:6379
    volumes:
      - ./backend/src:/app/src
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3001/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: hackathon
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  postgres_data:
```
