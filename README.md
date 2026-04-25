# Pulse — Free-to-Paid Conversion Platform

> DS-223 Marketing Analytics · Group 7 · American University of Armenia · Spring 2026

Pulse is a microservice application that helps Armat (an Armenian writing SaaS) convert free-tier users to paid Pro subscribers. It segments users by behaviour, lets the PM team launch targeted campaigns, run A/B tests, and track conversion KPIs in real time.

---

## Prototypes

| Version | Link |
|---------|------|
| Must Have | [prototype-must-have](https://willowy-dodol-1d69c6.netlify.app/) |
| Should & Nice to Have | [prototype-should-have](https://starlit-pastelito-981ea4.netlify.app/) |

---

## Team

| Name | Role |
|------|------|
| Silva Vardanyan | Product Manager |
| Albert Hakobyan | Backend Developer |
| Anzhelika Simonyan | Frontend Developer |
| Narek Dilbaryan | Database Engineer |
| Areg Avagyan | Data Scientist |

---

## Architecture

```
ds223-7-project/
├── docker-compose.yml
├── .env
└── pulse/
    ├── api/        FastAPI backend          →  localhost:8008
    ├── app/        Streamlit dashboard      →  localhost:8501
    ├── ds/         Data science models
    ├── etl/        DB seed pipeline (exits after run)
    └── pgadmin/    pgAdmin auto-configuration
```

Five Docker containers run together:

| Container | Description | Port |
|-----------|-------------|------|
| `db` | PostgreSQL 16 database | 5433 |
| `pgadmin` | pgAdmin UI | 5050 |
| `back` | FastAPI REST backend | 8008 |
| `front` | Streamlit dashboard | 8501 |
| `etl` | Seeds the database, then exits | — |

---

## Quick Start

**Requirements:** Docker + Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project

# 2. Credentials are already set in .env (dev defaults — no changes needed)

# 3. Build and start all containers
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Streamlit dashboard | http://localhost:8501 |
| FastAPI Swagger UI | http://localhost:8008/docs |
| pgAdmin | http://localhost:5050 |

**pgAdmin login:** `admin@admin.com` / `admin`

The ETL container runs automatically on first start, creates all 15 tables, and seeds 442 users with full behavioral data across all 4 segments.

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| Segments | User counts per segment, behavioral averages, breakdown table |
| A/B Tests | Control vs treatment stats, lift, p-value per segment |
| KPIs | Conversion rate, retention, engagement, results summary |
| User Demo | Simulate upgrade messages and record user responses live |
| Campaign Editor | Edit messages, set channels and triggers, launch A/B tests |

---

## User Segments

| Segment | Users | Strategy |
|---------|-------|----------|
| Power | 124 | Upsell — hit export limits regularly |
| Growing | 158 | Nurture — rising usage |
| Casual | 98 | Re-engage — template library hook |
| Dormant | 62 | Win-back — discount + urgency |

---

## Key KPIs

| Metric | Value |
|--------|-------|
| Conversion rate | 5.4% |
| Avg time to convert | 6.2 days |
| 30-day Pro retention | 83% |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/segments/counts` | User count per segment |
| GET | `/api/segments/behavioral-averages` | Avg exports, paywall hits, sessions |
| GET | `/api/ab-tests/summary` | A/B test results per segment |
| GET | `/api/kpis` | Platform-level conversion metrics |
| GET | `/api/campaigns` | All campaigns with active messages |
| GET | `/api/global-params` | Shared campaign parameters |
| PUT | `/api/campaigns/{id}/message` | Update campaign message |
| PUT | `/api/global-params/{key}` | Update a global parameter |
| POST | `/api/campaigns/{id}/launch` | Launch a campaign |
| DELETE | `/api/campaigns/{id}/reset` | Reset campaign to draft |
| POST | `/api/demo/respond` | Record a demo user response |

Full interactive docs at **http://localhost:8008/docs**

---

## Documentation

Full project documentation is available via MkDocs:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Then open **http://localhost:8000**

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| ETL | Python + psycopg2 |
| Containers | Docker Compose |
| Documentation | MkDocs Material |
