# Roadmap

## Milestone 1 — Foundation (complete)

- [x] Problem definition and business case (Armat free-to-paid conversion)
- [x] User segmentation model — Power (1,240), Growing (1,580), Casual (980), Dormant (620)
- [x] Basic prototype — Overview dashboard with KPI cards and segment funnel
- [x] Should-Have prototype — full sidebar app with 5 screens: Segments, A/B Tests, KPIs, Campaign Editor, User Demo
- [x] Database schema design (`01_schema.sql`)
- [x] Flowchart and product roadmap diagram
- [x] Team roles defined: PM, Backend, Frontend, DB, Data Scientist

## Milestone 2 — Infrastructure

- [x] PostgreSQL database with schema (`01_schema.sql`)
- [x] FastAPI backend with endpoints for all 5 screens
- [x] Docker Compose stack (db, pgadmin, api, app, etl)
- [x] Project folder structure (`myapp/api`, `myapp/app`, `myapp/etl`)
- [ ] Streamlit frontend pages wired to live API
- [ ] ETL pipeline populating seed data

## Milestone 3 — Analytics & A/B Testing

- [ ] A/B test runner — variant assignment and result tracking
- [ ] Statistical significance calculation for test results
- [ ] KPI dashboard connected to real data
- [ ] Campaign launch and reset workflow

## Milestone 4 — Production Readiness

- [ ] Authentication / role-based access
- [ ] CI/CD pipeline
- [ ] Load testing and performance tuning
- [ ] Full MkDocs documentation site deployed to GitHub Pages