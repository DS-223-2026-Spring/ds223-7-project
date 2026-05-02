# Contributing to Pulse

## Branch Strategy

Each team member worked on a dedicated branch named after their role:

| Branch | Owner | Scope |
|--------|-------|-------|
| `main` | Silva Vardanyan (PM) | Stable, demo-ready code only |
| `back` | Albert Hakobyan | FastAPI backend, ORM models, API endpoints |
| `front` | Anzhelika Simonyan | Streamlit dashboard, UI components |
| `db` | Narek Dilbaryan | PostgreSQL schema, ETL pipeline, seed data |
| `ds` | Areg Avagyan | Data science models, EDA notebooks |

No direct commits to `main`. All changes were submitted via Pull Request and reviewed by the PM before merging.

---

## Commit Convention

Commits follow the format:

```
type: short description in present tense
```

| Type | Usage |
|------|-------|
| `feat` | New feature or endpoint |
| `fix` | Bug fix |
| `refactor` | Code restructure without behaviour change |
| `style` | UI or CSS changes |
| `docs` | README, docstrings, MkDocs content |
| `chore` | Config, Docker, dependencies |

---

## Pull Request Process

1. Work is pushed to the role branch (`back`, `front`, `db`, `ds`)
2. A PR is opened targeting `main`
3. PR description lists what was added and how it was tested
4. PM (Silva) reviews and either requests changes or approves
5. PM merges — team members do not merge their own PRs

---

## Review Expectations

- PM verified each PR ran correctly with `docker-compose up --build`
- Reviewer checked that endpoints matched the prototype screens
- Structural or naming issues (wrong paths, wrong Python version) were flagged before merge
- PRs with conflicts were resolved before merging

---

## Environment

Credentials are in `.env` at the repo root. No secrets or personal keys are committed.

To run the full stack locally:

```bash
cd ds223-7-project
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Streamlit dashboard | http://localhost:8501 |
| FastAPI Swagger UI | http://localhost:8008/docs |
| pgAdmin | http://localhost:5050 |
