# Pulse — Free-to-Paid Conversion Platform

**DS-223 Marketing Analytics · Group 7 · Spring 2026**

---

**Pulse** is a behavioral segmentation and A/B testing platform built for **Armat**, an Armenian writing SaaS, to convert free-tier users to paid Pro subscribers.

## What Pulse Does

1. **Segments** free users into four behavioral groups based on session activity, export frequency, and paywall interactions
2. **Targets** each segment with a tailored in-app upgrade message crafted in the Campaign Editor
3. **Tests** two message variants head-to-head in a 14-day A/B window and measures conversion lift
4. **Tracks** conversion rate, time-to-convert, and 30-day Pro retention in a live KPI dashboard

## Services

| Service | Technology | Port | Role |
|---------|-----------|------|------|
| `db` | PostgreSQL 16 | 5433 | Primary database — 15 tables, 6 views |
| `back` | FastAPI + SQLAlchemy | 8008 | REST API — 13 endpoints |
| `front` | Streamlit | 8501 | PM dashboard — 5 screens |
| `ds` | Jupyter | 8888 | Data science notebooks |
| `etl` | Python | — | One-time data seed (exits after run) |
| `pgadmin` | pgAdmin 4 | 5050 | Database admin UI |

## Quick Start

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project
docker-compose up --build
```

Then open:

- **Dashboard** → [http://localhost:8501](http://localhost:8501)
- **API docs** → [http://localhost:8008/docs](http://localhost:8008/docs)
- **Notebooks** → [http://localhost:8888](http://localhost:8888)

## Documentation Sections

- [Problem & Solution](problem.md) — business context and why Pulse exists
- [Architecture](architecture.md) — system design and container overview
- [Database](database.md) — schema, tables, and views
- [ETL Pipeline](etl.md) — data seeding and initialization
- [Model Engine](model.md) — segmentation logic and A/B statistics
- [API](api.md) — endpoint reference
- [Dashboard](dashboard.md) — Streamlit screens and components
- [Roadmap](roadmap.md) — milestone plan and delivery status
- [KPIs](kpis.md) — platform metrics and conversion funnel
- [Team](team.md) — team members and course info
