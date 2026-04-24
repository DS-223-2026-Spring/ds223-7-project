# Architecture

## System Overview

Pulse is a **microservice application** running entirely in Docker Compose. Each component is an isolated container communicating over an internal Docker network.

```
Browser
  │
  ├── :8501  →  front   (Streamlit dashboard)
  ├── :8008  →  back    (FastAPI backend)
  ├── :8888  →  ds      (Jupyter notebooks)
  └── :5050  →  pgadmin (DB admin UI)

front  →  back  →  db  (PostgreSQL)
etl    →  db    (one-time seed on first start)
ds     →  db    (read-only analytics queries)
```

## Services

| Container | Image / Build | Port | Role |
|-----------|--------------|------|------|
| `db` | `postgres:16-alpine` | 5433 | Primary PostgreSQL database |
| `pgadmin` | `dpage/pgadmin4` | 5050 | DB admin UI |
| `back` | `./api` | 8008 | FastAPI REST backend |
| `front` | `./app` | 8501 | Streamlit dashboard |
| `ds` | `./ds` | 8888 | Jupyter data science notebooks |
| `etl` | `./etl` | — | One-time ETL seed (exits after run) |

## Folder Structure

```
ds223-7-project/
├── pulse/
│   ├── docker-compose.yml
│   ├── .env
│   ├── api/                  ← FastAPI backend
│   │   ├── database.py       ← SQLAlchemy session factory
│   │   ├── models.py         ← SQLAlchemy ORM models (15 tables)
│   │   ├── schema.py         ← Pydantic request/response schemas
│   │   ├── routes/           ← endpoint modules (segments, ab_tests, …)
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── app/                  ← Streamlit frontend
│   │   ├── components/       ← reusable UI components
│   │   ├── pages/            ← multi-page app screens
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── ds/                   ← Data Science
│   │   ├── experiments.ipynb ← main analysis notebook
│   │   ├── notebooks/        ← exploratory notebooks
│   │   └── Dockerfile
│   └── etl/                  ← Data pipeline
│       ├── data/             ← seed CSV files
│       ├── init/             ← SQL schema (run on first DB start)
│       ├── etl_process.py    ← main entry point
│       ├── check_connection.py
│       ├── seed_flat_data.py
│       └── Dockerfile
├── docs/                     ← MkDocs documentation source
└── mkdocs.yml
```

## Data Flow

1. **ETL** runs once on startup — loads `init/01_schema.sql` via Docker volume mount, then seeds all tables from `data/users.csv`
2. **API** reads from PostgreSQL views (`v_*`) for all dashboard queries; writes to campaign, message, and conversion tables
3. **App** calls the API over HTTP (`http://back:8000`); renders results in Streamlit pages
4. **DS** connects directly to the database for exploratory analysis and model development
5. **pgAdmin** connects directly to the DB for inspection and debugging

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL 16 |
| Data Science | Jupyter + pandas + scipy |
| Containerisation | Docker Compose |
| Base Image | `python:3.13-slim` (all services) |
| Documentation | MkDocs Material |
