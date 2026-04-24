# Roadmap

## Milestone 1 — Foundation (complete)

- [x] Problem definition and business case (Armat free-to-paid conversion)
- [x] User segmentation model — Power (1,240), Growing (1,580), Casual (980), Dormant (620)
- [x] Basic prototype — Overview dashboard with KPI cards and segment funnel
- [x] Should-Have prototype — full sidebar app with 5 screens: Segments, A/B Tests, KPIs, Campaign Editor, User Demo
- [x] Database schema design (`01_schema.sql`)
- [x] Flowchart and product roadmap diagram
- [x] Team roles defined: PM, Backend, Frontend, DB, Data Scientist

## Milestone 2 — Infrastructure (in progress)

- [x] PostgreSQL 16 database with full schema (`pulse/etl/init/01_schema.sql`) — 15 tables, views, triggers
- [x] FastAPI backend with 13 endpoints across 5 routes (`pulse/api/routes/`)
- [x] Docker Compose stack — 6 containers: db, pgadmin, back, front, ds, etl
- [x] Correct project folder structure (`pulse/api`, `pulse/app`, `pulse/ds`, `pulse/etl`)
- [x] SQLAlchemy ORM models for all 15 tables (`pulse/api/models.py`)
- [x] Pydantic schemas merged into single `pulse/api/schema.py`
- [x] All Dockerfiles use `python:3.13-slim`
- [x] Streamlit frontend scaffolding with navigation, layout, and component stubs (`pulse/app/`)
- [ ] Streamlit pages fully wired to live API data
- [ ] ETL seed pipeline producing complete dataset

## Milestone 3 — Analytics & A/B Testing

- [ ] A/B test runner — variant assignment and result tracking
- [ ] Statistical significance calculation (chi-square) for test results
- [ ] KPI dashboard connected to real data
- [ ] Campaign launch and reset workflow
- [ ] Data Science analysis in `pulse/ds/experiments.ipynb`

## Milestone 4 — Production Readiness

- [ ] Authentication / role-based access
- [ ] CI/CD pipeline
- [ ] Load testing and performance tuning
- [ ] Full MkDocs documentation site deployed to GitHub Pages
