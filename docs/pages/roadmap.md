# Roadmap

## Delivered

- [x] Business problem definition — Mer Lezun free-to-paid conversion
- [x] Behavioral user segmentation — Power, Growing, Casual, Dormant (442 users, 4 segments)
- [x] PostgreSQL 16 database — 15 tables, 6 views, triggers, custom enums
- [x] FastAPI backend — 18 endpoints across 6 route groups
- [x] Docker Compose stack — 6 containers: `db`, `back`, `front`, `ds`, `etl`, `pgadmin`
- [x] Streamlit PM dashboard — 5 fully wired screens with live API data
- [x] A/B test runner — Beta-Binomial Thompson Sampling, control vs treatment attribution
- [x] Campaign Editor — per-segment message editing, launch, reset, global params
- [x] User Demo — side-by-side control/treatment simulation with live response recording
- [x] KPI dashboard — period-filtered conversion rate, churn, revenue, engagement
- [x] ML pipeline — logistic regression conversion probability scores per user
- [x] MkDocs documentation site — deployed to GitHub Pages

## Future Work

- [ ] Authentication and role-based access control
- [ ] CI/CD pipeline with automated tests
- [ ] Real push notification and email delivery integration
- [ ] Multi-armed bandit for dynamic traffic allocation
- [ ] Cohort retention analysis
