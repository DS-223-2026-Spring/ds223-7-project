# Architecture

## System Overview

Pulse is a **6-container Docker Compose application**. Each service is isolated and communicates over an internal Docker network. The user only needs one command to start everything:

```bash
docker-compose up --build
```

## Container Map

```
Browser
  │
  ├── :8501  →  front    (Streamlit PM dashboard)
  ├── :8008  →  back     (FastAPI REST API)
  ├── :8888  →  ds       (Jupyter notebooks)
  └── :5050  →  pgadmin  (Database admin UI)

front  ──HTTP──►  back  ──SQLAlchemy──►  db (PostgreSQL 16)
                                              ▲
etl    ──────────────────────────────────────┘  (seeds once, exits)
ds     ──────────────────────────────────────┘  (reads & writes directly)
```

## Services

| Container | Image / Build | Port | Role |
|-----------|--------------|------|------|
| `db` | `postgres:16-alpine` | 5433 | Primary database — 15 tables, 6 views, triggers, enums |
| `pgadmin` | `dpage/pgadmin4` | 5050 | DB admin UI (admin@admin.com / admin) |
| `back` | `./pulse/api` | 8008 | FastAPI REST API — 18 endpoints |
| `front` | `./pulse/app` | 8501 | Streamlit PM dashboard — 5 screens |
| `ds` | `./pulse/ds` | 8888 | Jupyter + DS pipeline scripts |
| `etl` | `./pulse/etl` | — | One-time schema + seed (exits after run) |

## Startup Sequence

```
docker-compose up --build
    │
    ├── db starts + runs health check
    │
    ├── etl (depends on db healthy)
    │       └── Loads 01_schema.sql (tables, views, triggers, enums)
    │       └── Seeds 442 users, segments, campaigns, message templates
    │       └── Exits
    │
    ├── back (depends on db healthy)
    │       └── FastAPI + Uvicorn serve on :8000
    │
    ├── front (depends on back)
    │       └── Streamlit serves on :8501
    │
    └── ds (depends on etl completing successfully)
            └── seed_events.py   — seeds session + paywall events
            └── segment_kmeans.py — fits K-Means, writes user_segments
            └── run_ab_analysis.py — Thompson Sampling, writes ab_test_results
            └── jupyter notebook  — serves on :8888
```

## Data Flow

```
                    ┌─────────────────────────────────────────┐
                    │           PostgreSQL (db)                │
                    │                                         │
                    │  users, segments, user_segments         │
                    │  campaigns, message_templates           │
                    │  ab_tests, ab_assignments               │
                    │  conversion_outcomes                    │
                    │  session_events, paywall_events         │
                    │  user_conversion_scores                 │
                    │  ab_test_results                        │
                    └────────────┬──────────────┬────────────┘
                                 │              │
              ┌──────────────────┘              └──────────────────┐
              ▼                                                     ▼
   ┌─────────────────────┐                          ┌──────────────────────┐
   │   DS Pipeline        │                          │   FastAPI Backend    │
   │                     │                          │                      │
   │  seed_events.py     │                          │  reads DB via views  │
   │  segment_kmeans.py  │                          │  writes campaigns,   │
   │  run_ab_analysis.py │                          │  conversion_outcomes │
   │  predict.py         │                          │  serves 18 endpoints │
   └─────────────────────┘                          └──────────┬───────────┘
                                                               │ HTTP
                                                               ▼
                                                  ┌──────────────────────┐
                                                  │  Streamlit Frontend  │
                                                  │                      │
                                                  │  Segments screen     │
                                                  │  A/B Tests screen    │
                                                  │  KPIs screen         │
                                                  │  Campaign Editor     │
                                                  │  User Demo           │
                                                  └──────────────────────┘
```

**Rule:** DS writes to DB. Backend reads from DB and handles user actions. Frontend only talks to backend. No layer skips a level.

## Folder Structure

```
ds223-7-project/
├── docker-compose.yml
├── .env
├── mkdocs.yml
├── docs/                        ← MkDocs documentation source
└── pulse/
    ├── api/                     ← FastAPI backend
    │   ├── main.py
    │   ├── database.py          ← SQLAlchemy session factory
    │   ├── models.py            ← ORM models (15 tables)
    │   ├── schema.py            ← Pydantic request/response schemas
    │   ├── routes/
    │   │   ├── segments.py
    │   │   ├── ab_tests.py
    │   │   ├── kpis.py
    │   │   ├── campaigns.py
    │   │   ├── demo.py
    │   │   └── global_params.py
    │   └── Dockerfile
    ├── app/                     ← Streamlit frontend
    │   ├── app.py               ← all 5 screens in one file
    │   └── Dockerfile
    ├── ds/                      ← Data Science
    │   ├── seed_events.py       ← seeds session + paywall events
    │   ├── segment_kmeans.py    ← K-Means segmentation pipeline
    │   ├── run_ab_analysis.py   ← Thompson Sampling A/B analysis
    │   ├── feature_pipeline.py  ← feature engineering
    │   ├── final_model.py       ← logistic regression + random forest
    │   ├── predict.py           ← conversion probability scoring
    │   ├── segment_summary.py   ← per-segment summary export
    │   ├── modeling_related_files.py ← shared helpers
    │   ├── run_ds_pipeline.sh   ← runs all steps in order
    │   ├── experiments.ipynb    ← main analysis notebook
    │   └── Dockerfile
    └── etl/
        ├── init/
        │   ├── 01_schema.sql    ← full schema + seed data
        │   └── 02_migrations.sql
        ├── etl_process.py
        └── Dockerfile.etl
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| Database | PostgreSQL 16 |
| ML / Stats | scikit-learn, NumPy, pandas |
| Containerisation | Docker Compose |
| Documentation | MkDocs Material → GitHub Pages |
| CI/CD | GitHub Actions (docs deploy) |
