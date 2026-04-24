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
pulse/
├── api/        FastAPI backend         →  localhost:8008
├── app/        Streamlit dashboard     →  localhost:8501
├── ds/         Data science notebooks
└── etl/        One-time DB seed pipeline
```

Five Docker containers run together:

| Container | Description | Port |
|-----------|-------------|------|
| `db` | PostgreSQL 16 database | 5433 |
| `pgadmin` | pgAdmin UI | 5050 |
| `back` | FastAPI REST backend | 8008 |
| `front` | Streamlit dashboard | 8501 |
| `etl` | ETL seed runner (exits after run) | — |

---

## Quick Start

**Requirements:** Docker + Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project

# 2. Credentials are already set in pulse/.env (dev defaults)
#    Edit pulse/.env if you want custom values

# 3. Navigate to the product folder and start all containers
cd pulse
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Streamlit dashboard | http://localhost:8501 |
| FastAPI Swagger UI | http://localhost:8008/docs |
| pgAdmin | http://localhost:5050 |

**pgAdmin login:** `admin@admin.com` / `admin`

---

## User Segments

| Segment | Users | Strategy |
|---------|-------|----------|
| Power writers | 1,240 | Upsell — hit export limits regularly |
| Growing writers | 1,580 | Nurture — rising usage |
| Casual writers | 980 | Re-engage — template library hook |
| Dormant writers | 620 | Win-back — discount + urgency |

---

## Key KPIs

| Metric | Value |
|--------|-------|
| Conversion rate | 5.4% |
| Avg time to convert | 6.2 days |
| 30-day Pro retention | 83% |

---

## Documentation

Full docs available via MkDocs:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Then open http://localhost:8000

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Containers | Docker Compose |
| Docs | MkDocs Material |
