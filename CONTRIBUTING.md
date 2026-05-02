# Contributing to Pulse

## Branch Strategy

Each team member works on a dedicated branch named after their role:

| Branch | Owner | Scope |
|--------|-------|-------|
| `main` | Silva Vardanyan (PM) | Stable, demo-ready code only |
| `back` | Albert Hakobyan | FastAPI backend, ORM models, API endpoints |
| `front` | Anzhelika Simonyan | Streamlit dashboard, UI components |
| `db` | Narek Dilbaryan | PostgreSQL schema, ETL pipeline, seed data |
| `ds` | Areg Avagyan | Data science models, EDA notebooks |

No direct commits to `main`. All changes must be submitted via Pull Request and reviewed by the PM before merging.

---

## Commit Convention

Commits must follow this format:

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

Examples:
```
feat: add A/B test summary endpoint
fix: correct API URL in Streamlit frontend
docs: update README quick start section
```

---

## Pull Request Process

1. Push work to your role branch (`back`, `front`, `db`, `ds`)
2. Open a PR targeting `main`
3. PR title must follow the commit convention above
4. PR description must list what was added and how it was tested
5. Tag the PM (Silva) as reviewer
6. Address any requested changes before re-requesting review
7. PM reviews and merges — team members do not merge their own PRs

---

## Review Expectations

- PM verifies each PR runs correctly with `docker-compose up --build`
- Reviewer checks that endpoints and pages match the prototype screens
- Structural issues (wrong paths, wrong Python version, missing files) must be fixed before merge
- PRs with unresolved conflicts will not be merged

---

## Environment

Credentials are in `.env` at the repo root. Do not commit secrets or personal API keys.

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
