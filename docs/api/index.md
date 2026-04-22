# API Layer

**Container:** `pulse_api` · **Port:** `8008` · **Build:** `myapp/api`

## Overview

The Pulse API is a FastAPI service that exposes database views and campaign management logic to the Streamlit frontend. All dashboard reads use pre-built SQL views (`v_*`). Write operations target campaign, message, and conversion tables.

**Base URL (internal):** `http://api:8000`

**Swagger UI:** `http://localhost:8008/docs`

## Endpoints

13 endpoints across 5 routers plus a `/health` liveness probe:

| Router | Prefix | Description |
|--------|--------|-------------|
| `segments` | `/api` | Segment summary with funnel metrics |
| `ab_tests` | `/api/ab-tests` | A/B test results and comparisons |
| `kpis` | `/api` | Platform-wide KPI overview |
| `campaigns` | `/api` | Campaign CRUD + launch/reset + message edit |
| `demo` | `/api` | User-level demo lookup |

## Tech Stack

- **FastAPI** — OpenAPI generation, dependency injection
- **SQLAlchemy** — raw `text()` queries against `v_*` views
- **Pydantic** — request/response validation
- **psycopg2** — PostgreSQL driver
- **uvicorn** — ASGI server

## Key Rules

1. Never query base tables for dashboard reads — use `v_*` views
2. Internal DB hostname is `db` (not `localhost`)
3. Every endpoint returns graceful empty results when DB is unreachable
