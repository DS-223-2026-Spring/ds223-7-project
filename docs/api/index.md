<<<<<<< backend
# API Layer

**Owner:** Backend Developer · **Branch:** `backend` · **Container:** `back`

## Overview

The Pulse API is a FastAPI service that exposes the database views and campaign management logic to the Streamlit frontend. All dashboard reads use pre-built SQL views. Write operations target the campaign, message, and conversion tables.

**Base URL:** `http://backend:8000` (inside Docker network)

**Interactive docs:** `http://localhost:8000/docs` (Swagger UI, auto-generated)

## Endpoints

See the full endpoint reference in `app/back/docs/api_docs.md`.

Quick summary: 13 endpoints across 5 screens (Segments, A/B Tests, KPIs, Campaign Editor, User Demo) plus a `/health` liveness probe.

## Tech stack

- **FastAPI** — async-capable web framework with automatic OpenAPI generation
- **SQLAlchemy** — database access layer (raw `text()` queries against views)
- **Pydantic** — request/response validation and serialization
- **psycopg2** — PostgreSQL driver
- **uvicorn** — ASGI server with hot-reload in development

## Key rules

1. Never query base tables directly for dashboard data — use `v_*` views
2. Never update trigger-maintained columns in code
3. Every endpoint returns graceful empty results when DB is unreachable
4. Internal DB hostname is `db`, internal backend hostname is `backend`
=======
# API
>>>>>>> main
