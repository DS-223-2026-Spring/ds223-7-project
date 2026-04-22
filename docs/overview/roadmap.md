# Roadmap

## Milestone 1 — Foundation (complete)

- [x] Problem definition and business case
- [x] User segmentation model (Power / Growing / Casual / Dormant)
- [x] Basic prototype (Overview dashboard)
- [x] Should-Have prototype (full sidebar app with Campaign Editor, A/B Tests, KPIs)
- [x] Database schema design
- [x] Flowchart and architecture diagram

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