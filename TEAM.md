# Pulse — Team Working Guide

> Read this before you touch any code. Takes 5 minutes. Saves hours.

---

## 1. Run the project locally

**Requirements: Docker Desktop must be running.**

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project
docker-compose up --build
```

Wait ~60 seconds for all containers to start. The ETL seeds the database automatically on first run.

### Where to see results

| What | URL |
|------|-----|
| **Streamlit Dashboard** (main app) | http://localhost:8501 |
| **FastAPI Swagger** (all endpoints, test them live) | http://localhost:8008/docs |
| **Jupyter Notebooks** (DS work) | http://localhost:8888 |
| **pgAdmin** (browse the database) | http://localhost:5050 |

**pgAdmin login:** `admin@admin.com` / `admin` — the DB auto-connects, no extra setup needed.

> If you see kernel warnings in the `ds` container logs — not an error. Just refresh the Jupyter tab.

---

## 2. Your tasks right now

### Narek (DB) — finish Milestone 2 first, then Milestone 3

**Milestone 2 (finish these first):**
- [ ] #22 — Post evidence comment on the `db` branch issue
- [ ] #28 — Add reusable CRUD helper methods to DB utilities
- [ ] #29 — Add docstrings to all DB utility functions
- [ ] #30 — Open a PR from `db` branch to `main`

**Milestone 3 (start after M2 is done):**
- [ ] #72 — Update DB tables per the revised ERD
- [ ] #73 — Add missing indexes and constraints
- [ ] #74 — Refactor DB utilities for clarity
- [ ] #75 — Finalize all docstrings
- [ ] #76 — Push updated work to `db` branch → open PR

---

### Anzhelika (Frontend) — finish Milestone 2 first, then Milestone 3

**Milestone 2 (finish these first):**
- [ ] #49 — Create the `front` git branch (if not done)
- [ ] #53 — Create reusable UI components / helper functions
- [ ] #56 — Push work to `front` branch → open PR

**Milestone 3 (start after M2 is done):**
- [ ] #88 — Build the final app layouts in Streamlit
- [ ] #89 — Refine screens based on PM requirements
- [ ] #90 — Use only built-in Streamlit components
- [ ] #91 — Prepare pages for tables, filters, charts, forms, model results
- [ ] #92 — Push final frontend work to `front` branch → open PR

> **Important for M3:** No need to connect to the API yet — that's M4. Build with realistic placeholder/mock data. Endpoint specs are in issue #68 so you know what field names to use in your layout.

---

### Albert (Backend) — start Milestone 3 directly

- [ ] #82 — Implement all API endpoints per PM specification (see #68)
- [ ] #83 — Create Pydantic request/response schemas for every route
- [ ] #84 — Integrate backend with the DB layer
- [ ] #85 — Add docstrings to all endpoints (these show in Swagger UI)
- [ ] #86 — Test all endpoints locally, verify response structures
- [ ] #87 — Push final backend work to `back` branch → open PR

> All routes are already scaffolded and live. Your job is to harden them: add schemas, docstrings, and test every endpoint at http://localhost:8008/docs

---

### Silva (DS) — start Milestone 3 directly

- [ ] #77 — Build the final model (best-performing solution)
- [ ] #78 — Finalize feature engineering, document the pipeline
- [ ] #79 — Prepare final outputs (predictions, confidence scores, segments)
- [ ] #80 — Convert notebook steps into reusable, repeatable scripts
- [ ] #81 — Push final DS work to `ds` branch → open PR

---

### Silva (PM) — Milestone 3 in progress

- [x] #67 — Endpoint design complete (see the comment on that issue)
- [x] #68 — Specs shared with Albert and Anzhelika
- [ ] #69 — Review UI with Anzhelika, suggest Streamlit components
- [ ] #70 — Align all roles on data flow and dependencies
- [ ] #71 — Track blockers, make scope decisions if needed

---

## 3. How to work on an issue

### Step 1 — Pull latest before starting
```bash
git checkout <your-branch>   # db / back / front / ds
git pull origin main
git pull origin <your-branch>
```

### Step 2 — Do the work

Make your changes on your branch. **Never commit directly to `main`.**

### Step 3 — Push and open a PR
```bash
git add .
git commit -m "feat: short description of what you did"
git push origin <your-branch>
```
Then go to GitHub → Pull Requests → New PR → base: `main`, compare: `<your-branch>`.

**PR title format:** `feat(narek): add CRUD helpers and docstrings` or `feat(anzhelika): final Streamlit layouts M3`

---

## 4. Comment on every issue you work on

**This is required for grading. The professor checks issue comments as evidence.**

After completing each task, go to the GitHub issue and add a comment like:

```
✅ Done — [short description of what you did]

Evidence:
- File: pulse/db/utils.py — added get_user_by_id(), get_users_by_segment()
- Docstrings added to all 6 functions
- Pushed on branch `db`, PR #XX
```

**Then change the issue status** in the project board to **"Review"** (do NOT close it — the PM reviews and closes).

> If you use Claude Code, you can ask it: *"Post an evidence comment on GitHub issue #XX for what I just did"* and it will do it automatically.

---

## 5. Answer the professor's comments

**This is critical — do not skip this.**

Before posting your evidence comment, scroll through the issue from the top and check if `hovhannisyan91` left any comment or question. If he did, **answer it directly in your comment.**

Example:
> Professor asked: *"Show me the reusable methods you added"*
> Your reply: *"Added `get_user_by_segment(segment_name)` and `update_user_status(user_id, status)` in `pulse/db/crud.py` — these are called by the ETL and will be used by the backend in M3."*

**Agents (including Claude Code) may miss professor comments if they don't read the full issue thread. Always read the full thread yourself before posting.**

---

## 6. After your PR is merged

- Silva merges the PR and deletes your branch
- Go back to your branch: `git checkout <your-branch>`
- Pull the updated main: `git pull origin main`
- Continue from there

---

## 7. Quick reference

| Person | Branch | M2 issues | M3 issues |
|--------|--------|-----------|-----------|
| Silva | `main` (PM) | — | #67 #68 #69 #70 #71 |
| Narek | `db` | #22 #28 #29 #30 | #72 #73 #74 #75 #76 |
| Silva | `ds` | ✅ done | #77 #78 #79 #80 #81 |
| Albert | `back` | ✅ done | #82 #83 #84 #85 #86 #87 |
| Anzhelika | `front` | #49 #53 #56 | #88 #89 #90 #91 #92 |

**Docs site:** https://ds-223-2026-spring.github.io/ds223-7-project/
(auto-updates on every push to `main`)
