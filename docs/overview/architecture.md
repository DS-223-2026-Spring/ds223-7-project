# Architecture

## System Overview

Pulse is a **microservice application** running entirely in Docker Compose. Each component is an isolated container communicating over an internal Docker network.

```
Browser
  │
  ├── :8501  →  app      (Streamlit frontend)
  ├── :8008  →  api      (FastAPI backend)
  └── :5050  →  pgadmin  (DB admin UI)

app  →  api  →  db  (PostgreSQL)
etl  →  db   (one-time seed / migration run)
```

## Services

| Container | Image / Build | Port | Role |
|-----------|--------------|------|------|
| `pulse_db` | `postgres:16-alpine` | 5433 | Primary database |
| `pulse_pgadmin` | `dpage/pgadmin4` | 5050 | DB admin UI |
| `pulse_api` | `./myapp/api` | 8008 | FastAPI REST backend |
| `pulse_app` | `./myapp/app` | 8501 | Streamlit dashboard |
| `pulse_etl` | `./myapp/etl` | — | One-time ETL / seed |

## Folder Structure

```
ds223-7-project/
├── myapp/
│   ├── docker-compose.yaml
│   ├── .env
│   ├── api/                  ← FastAPI backend
│   │   ├── Database/         ← SQLAlchemy models, session, Pydantic schemas
│   │   ├── routers/          ← endpoint modules (segments, campaigns, …)
│   │   ├── schemas/          ← Pydantic request/response models
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── app/                  ← Streamlit frontend
│   │   ├── pages/            ← multi-page app (page1, page2)
│   │   ├── app.py
│   │   └── Dockerfile
│   └── etl/                  ← Data pipeline
│       ├── Database/         ← ETL models, session, data generator
│       ├── data/             ← seed CSV files
│       ├── init/             ← SQL schema run on first DB start
│       ├── etl_process.py
│       └── Dockerfile
├── docs/                     ← MkDocs documentation source
└── mkdocs.yml
```

## Data Flow

1. **ETL** runs once on startup — loads `init/01_schema.sql` (via Docker volume) then seeds data from `data/users.csv`
2. **API** reads from PostgreSQL views (`v_*`) for all dashboard queries; writes to campaign/message tables
3. **App** calls the API over HTTP; renders results in Streamlit pages
4. **pgAdmin** connects directly to the DB for inspection and debugging

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL 16 |
| Containerisation | Docker Compose |
| Documentation | MkDocs Material |