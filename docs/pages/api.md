# API Layer

**Container:** `back` · **Port:** `8008` · **Build:** `pulse/api`

## Overview

The Pulse API is a FastAPI service that exposes database views and campaign management logic to the Streamlit frontend. All dashboard reads use pre-built SQL views (`v_*`). Write operations target campaign, message, and conversion tables.

**Base URL (internal Docker network):** `http://back:8000`

**Swagger UI:** `http://localhost:8008/docs`

## Endpoints

13 endpoints across 5 routes plus a `/health` liveness probe:

| Route file | Prefix | Endpoints |
|------------|--------|-----------|
| `routes/segments.py` | `/api/segments` | GET `/counts`, GET `/behavioral-averages` |
| `routes/ab_tests.py` | `/api/ab-tests` | GET `/summary`, GET `/comparison` |
| `routes/kpis.py` | `/api/kpis` | GET `` |
| `routes/campaigns.py` | `/api` | GET/PUT `/campaigns`, POST `/launch`, DELETE `/reset`, GET/PUT `/global-params` |
| `routes/demo.py` | `/api/demo` | GET `/message/{segment}`, POST `/respond` |

## File Structure

```
pulse/api/
├── database.py       ← SQLAlchemy session factory (get_db dependency)
├── models.py         ← SQLAlchemy ORM models for all 15 tables
├── schema.py         ← All Pydantic request/response schemas
├── main.py           ← FastAPI app, CORS, router registration
├── routes/
│   ├── segments.py
│   ├── ab_tests.py
│   ├── kpis.py
│   ├── campaigns.py
│   └── demo.py
├── requirements.txt
└── Dockerfile
```

## Tech Stack

- **FastAPI** — OpenAPI generation, dependency injection
- **SQLAlchemy** — raw `text()` queries against `v_*` views
- **Pydantic** — request/response validation
- **psycopg2** — PostgreSQL driver
- **uvicorn** — ASGI server (`python:3.13-slim` base image)

## Key Rules

1. Never query base tables for dashboard reads — always use `v_*` views
2. Internal DB hostname is always `db` (never `localhost`)
3. Every endpoint returns a graceful empty result when the DB is unreachable
4. All imports use flat module names: `from database import get_db`, `from schema import ...`
