# Contributing Guide — Pulse · DS-223 Group 7

> Read this fully before you start. Every team member has a dedicated section below.

---

## Repository Structure

```
ds223-7-project/
├── myapp/
│   ├── docker-compose.yaml   ← all services defined here
│   ├── api/                  ← Backend (Albert)
│   ├── app/                  ← Frontend (Anzhelika)
│   ├── etl/                  ← Database / ETL (Narek)
│   ├── ds/                   ← Data Science (Areg)
│   └── .env                  ← shared credentials (already filled)
├── docs/                     ← MkDocs documentation
└── README.md
```

---

## Git Workflow (everyone follows this)

```
main  ←  your-branch  (you work here, then open a PR)
```

1. Clone the repo **once**
2. Create your branch (name specified in your section below)
3. Work **only inside your folder** (`myapp/api/`, `myapp/app/`, etc.)
4. Commit often with clear messages
5. Push your branch and open a Pull Request to `main`
6. Silva (PM) reviews and merges

**Never push directly to `main`.**

---

## Commit Message Format

```
type: short description

Examples:
feat: add segments router
fix: correct database connection string
docs: add docstrings to crud helpers
```

---

## Running the Full Stack Locally

```bash
cd myapp
docker-compose up --build
```

| Service | URL |
|---------|-----|
| FastAPI Swagger | http://localhost:8008/docs |
| Streamlit app | http://localhost:8501 |
| pgAdmin | http://localhost:5050 |
| Jupyter (DS) | http://localhost:8888 |

pgAdmin login: `admin@admin.com` / `admin`

---

---

# Albert Hakobyan — Backend Developer

## Branch: `back`

## Status: previous work preserved ✅

Your FastAPI code from the old `backend` branch has been moved to `myapp/api/`. Everything is there — routers, schemas, Database connection. You do **not** start from scratch.

---

## Step 1 — Set up

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project
git checkout -b back
git push origin back
```

---

## Step 2 — Understand your folder

```
myapp/api/
├── Database/
│   ├── __init__.py         ← re-exports get_db, engine, SessionLocal
│   ├── database.py         ← SQLAlchemy session factory (get_db)
│   ├── models.py           ← SQLAlchemy ORM models (placeholder — update from ERD)
│   └── schema.py           ← Pydantic schemas (placeholder — your schemas/ folder has the real ones)
├── routers/
│   ├── ab_tests.py         ← your original code ✅
│   ├── campaigns.py        ← your original code ✅
│   ├── demo.py             ← your original code ✅
│   ├── kpis.py             ← your original code ✅
│   └── segments.py         ← your original code ✅
├── schemas/
│   ├── ab_tests.py         ← your original Pydantic schemas ✅
│   ├── campaigns.py        ✅
│   ├── demo.py             ✅
│   ├── kpis.py             ✅
│   └── segments.py         ✅
├── main.py                 ← your original entry point ✅
├── Dockerfile              ✅
└── requirements.txt        ✅
```

---

## Step 3 — What you need to do (remaining issues)

### Update models.py to match the ERD (#44 cleanup)

The `Database/models.py` currently has a placeholder. Replace it with the actual SQLAlchemy models based on the ERD that was shared. The full schema is in `myapp/etl/init/01_schema.sql` — use that as reference for table names, columns, and relationships.

Key tables from the ERD:
`users`, `segments`, `user_segments`, `session_events`, `tool_usage_logs`,
`paywall_events`, `campaigns`, `message_templates`, `global_params`,
`ai_generation_log`, `ab_tests`, `ab_assignments`, `ab_test_results`,
`notification_events`, `conversion_outcomes`

### Test your endpoints (#46)

Start the stack and verify every endpoint works:

```bash
cd myapp
docker-compose up --build
# open http://localhost:8008/docs
```

Test each router:
- `GET /api/segments` — returns segment list
- `GET /api/campaigns` — returns all campaigns
- `GET /api/ab-tests` — returns A/B test results
- `GET /api/kpis` — returns KPI overview
- `GET /health` — returns `{"status": "ok"}`

### Document API assumptions (#47)

In `myapp/api/docs/api_docs.md`, make sure you document:
- Which endpoints are ready vs. pending DB data
- Which endpoints depend on Narek's views (`v_*`)
- Any pending dependencies on the frontend

---

## Step 4 — Push and open PR (#48)

```bash
git add myapp/api/
git commit -m "feat: backend complete — models updated, endpoints tested"
git push origin back
```

Then go to GitHub → open a Pull Request from `back` → `main`.

---

---

# Narek Dilbaryan — Database Engineer

## Branch: `db` (already exists on GitHub)

## Status: previous work preserved ✅

Your schema, connection script, and seed loader from `db-milestone-2-setup` have been moved to `myapp/etl/`. The full 626-line `01_schema.sql` is intact.

---

## Step 1 — Set up

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project
git checkout db
git pull origin db
```

If `db` branch is behind `main`, update it:

```bash
git fetch origin
git rebase origin/main
```

---

## Step 2 — Understand your folder

```
myapp/etl/
├── Database/
│   ├── __init__.py
│   ├── database.py         ← SQLAlchemy session factory
│   ├── models.py           ← ORM models (update to match full ERD)
│   └── data_generator.py   ← synthetic data helpers
├── data/
│   └── users.csv           ← seed data (add more CSVs here)
├── init/
│   └── 01_schema.sql       ← your full schema ✅ (626 lines, 15 tables)
├── check_connection.py     ← your original connection checker ✅
├── seed_flat_data.py       ← your original CSV loader ✅
├── etl_process.py          ← runner that calls both scripts
├── Dockerfile
└── requirements.txt
```

---

## Step 3 — What you need to do (remaining issues)

### Add reusable CRUD helpers (#28)

In `myapp/etl/Database/database.py`, add helper methods so the Data Scientist and Backend can reuse them:

```python
def insert(table: str, data: dict) -> None:
    """Insert one row into table."""

def select(table: str, filters: dict = None) -> list[dict]:
    """Select rows from table, optionally filtered."""

def update(table: str, filters: dict, data: dict) -> None:
    """Update rows matching filters."""

def delete(table: str, filters: dict) -> None:
    """Delete rows matching filters."""
```

### Add more seed CSV files (#27 extension)

`seed_flat_data.py` already expects these files in `myapp/etl/data/` — create them:
- `session_events.csv`
- `tool_usage_logs.csv`
- `paywall_events.csv`
- `notification_events.csv`
- `conversion_outcomes.csv`

Use realistic fake data that matches the schema column names in `01_schema.sql`.

### Add docstrings to all utilities (#29)

Every function in `check_connection.py`, `seed_flat_data.py`, and `Database/database.py` should have a clear docstring explaining what it does, its parameters, and what it returns.

### Verify everything runs (#26 validation)

```bash
cd myapp
docker-compose up --build
docker-compose run --rm etl python check_connection.py
docker-compose run --rm etl python seed_flat_data.py
```

All 15 tables should show ✅.

---

## Step 4 — Push and open PR (#30)

```bash
git add myapp/etl/
git commit -m "feat: db complete — CRUD helpers, seed data, docstrings"
git push origin db
```

Then go to GitHub → open a Pull Request from `db` → `main`.

---

---

# Anzhelika Simonyan — Frontend Developer

## Branch: `front` (you create it)

## Status: skeleton exists in `myapp/app/` — start from there

---

## Step 1 — Set up

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project
git checkout -b front
git push origin front
```

---

## Step 2 — Understand your folder

```
myapp/app/
├── pages/
│   ├── page1.py            ← placeholder: Segment Overview
│   └── page2.py            ← placeholder: Campaign Editor
├── __init__.py
├── app.py                  ← main Streamlit entry point
├── Dockerfile
└── requirements.txt        ← streamlit, requests
```

The app runs on **http://localhost:8501**. Albert's API is at **http://back:8000** inside Docker (or `http://localhost:8008` from your browser).

---

## Step 3 — Understand the prototype

Look at the two prototypes for reference — these are what the screens should look like:
- [Must Have prototype](https://willowy-dodol-1d69c6.netlify.app/)
- [Should Have prototype](https://starlit-pastelito-981ea4.netlify.app/)

The app has **5 screens** (matching the 5 API routers):

| Screen | API endpoint | Your page file |
|--------|-------------|----------------|
| Segment Overview | `GET /api/segments` | `pages/page1.py` |
| Campaign Editor | `GET/PUT /api/campaigns` | `pages/page2.py` |
| A/B Tests | `GET /api/ab-tests` | `pages/page3.py` (create) |
| KPIs | `GET /api/kpis` | `pages/page4.py` (create) |
| User Demo | `GET /api/demo` | `pages/page5.py` (create) |

---

## Step 4 — What you need to do (issues)

### Build the navigation skeleton (#52)

In `app.py`, set up multi-page navigation using Streamlit's sidebar:

```python
import streamlit as st

st.set_page_config(page_title="Pulse", layout="wide")

page = st.sidebar.selectbox("Navigate", [
    "Segment Overview", "Campaign Editor",
    "A/B Tests", "KPIs", "User Demo"
])
```

### Build each page with placeholders (#52 #54)

For each page, follow this pattern — call the API and display the response. If the API is not ready yet, use hardcoded placeholder data:

```python
import streamlit as st
import requests, os

API = os.getenv("API_URL", "http://localhost:8008")

st.title("Segment Overview")

try:
    data = requests.get(f"{API}/api/segments", timeout=5).json()
    # display data here
except Exception:
    st.warning("API not reachable — showing placeholder data")
    data = []  # put placeholder dict/list here
```

### Create reusable helpers (#53)

Create `myapp/app/utils.py` with shared functions:

```python
def fetch(endpoint: str) -> dict | list:
    """Call the API and return JSON, or empty on failure."""

def segment_color(segment: str) -> str:
    """Return hex color for a segment name."""
    colors = {"power": "#00a86b", "growing": "#3b82f6",
              "casual": "#f59e0b", "dormant": "#9ca3af"}
    return colors.get(segment, "#000")
```

### Document data dependencies (#55)

Create `myapp/app/docs/data_requirements.md` listing:
- Which endpoint each page calls
- What fields it expects in the response
- What fields are currently missing from the API

---

## Step 5 — Test locally (#52 validation)

```bash
cd myapp
docker-compose up --build
# open http://localhost:8501
```

Navigate through all 5 pages — they should load without crashing.

---

## Step 6 — Push and open PR (#56)

```bash
git add myapp/app/
git commit -m "feat: frontend skeleton with 5 pages and navigation"
git push origin front
```

Then go to GitHub → open a Pull Request from `front` → `main`.

---

---

# Areg Avagyan — Data Scientist

## Branch: `ds` (you create it)

## Status: folder and Jupyter scaffold exist in `myapp/ds/`

---

## Step 1 — Set up

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project
git checkout -b ds
git push origin ds
```

---

## Step 2 — Understand your folder

```
myapp/ds/
├── Database/
│   ├── __init__.py
│   └── database.py         ← query() function to read from PostgreSQL into pandas
├── notebooks/
│   └── eda.ipynb           ← starter notebook (already connected to DB)
├── models/                 ← put trained model files here
├── __init__.py
├── Dockerfile              ← runs Jupyter on port 8888
└── requirements.txt        ← jupyter, pandas, sklearn, matplotlib, seaborn
```

Jupyter runs at **http://localhost:8888** (no password).

---

## Step 3 — Understand the data

The full database schema is in `myapp/etl/init/01_schema.sql`. Key tables for your work:

| Table | Description |
|-------|-------------|
| `users` | Free-tier users — plan, status, segment |
| `user_segments` | Segment assignment history |
| `session_events` | User sessions — duration, pages visited |
| `tool_usage_logs` | Which Armat tools each user used |
| `paywall_events` | When users hit export/feature limits |
| `conversion_outcomes` | Whether and when a user converted to Pro |

**Target variable:** `conversion_outcomes.converted` (True/False)

---

## Step 4 — What you need to do (issues)

### Explore the data (#33 #36)

In `notebooks/eda.ipynb`, run basic exploration:

```python
from Database.database import query

# User distribution
users = query("SELECT plan, segment_name, COUNT(*) FROM users GROUP BY plan, segment_name")

# Paywall hits per user
paywall = query("SELECT user_id, COUNT(*) as hits FROM paywall_events GROUP BY user_id")

# Session stats
sessions = query("SELECT AVG(duration_seconds), segment_name FROM session_events JOIN user_segments USING(user_id) GROUP BY segment_name")
```

Include:
- Distribution of users per segment
- Conversion rate per segment
- Avg sessions before conversion
- Top tools used by converted vs. non-converted users
- Missing values report per table

### Simulate synthetic data where needed (#34)

If tables like `session_events` or `tool_usage_logs` are empty (Narek's seed data is in progress), generate realistic synthetic data and document it clearly:

```python
# SYNTHETIC DATA — generated because session_events table was empty on [date]
import numpy as np
# ... generation code
```

### Use DB connection not local files (#35)

Always use `Database.database.query()` to read data — never load CSV files directly in your analysis. The only exception is if you are generating seed data to hand off to Narek.

### Build baseline models (#37)

In `notebooks/baseline_model.ipynb`, build and compare:

| Model | Why |
|-------|-----|
| Logistic Regression | interpretable baseline |
| Decision Tree | easy to explain to PM |
| Random Forest | better accuracy, check feature importance |

Predict: will a free user convert to Pro? (binary classification)

Features to try:
- Days since signup
- Number of paywall hits
- Session count and avg duration
- Tools used (one-hot)
- Segment label

### Document everything (#38)

At the top of each notebook, write a markdown cell covering:
- What question this notebook answers
- What data it uses (table names)
- What is real vs. synthetic
- Target variable definition
- Key assumptions

---

## Step 5 — Test locally

```bash
cd myapp
docker-compose up --build
# open http://localhost:8888
# open eda.ipynb and run all cells
```

---

## Step 6 — Push and open PR (#39)

```bash
git add myapp/ds/
git commit -m "feat: EDA complete, baseline models, synthetic data documented"
git push origin ds
```

Then go to GitHub → open a Pull Request from `ds` → `main`.

---

---

# Silva Vardanyan — Product Manager

## Tasks remaining

### #18 — This document is your contribution rules ✅
Share this `CONTRIBUTING.md` with all team members.

### #19 — Track progress
Check GitHub Issues weekly. Each issue has the member's name assigned. If an issue is done, close it.

### #20 — Review and merge PRs
When a team member opens a PR:
1. Read the changed files
2. Check that they only changed their own folder
3. Make sure the app still runs (`docker-compose up --build`)
4. Merge if everything looks good
5. Close the related issues

### #21 — Delete merged branches
After merging a PR, delete the branch on GitHub (there's a button right after merging).

### ERD — #16 ✅
Already shared with Albert and Narek, reflected in `01_schema.sql` and API routers.
