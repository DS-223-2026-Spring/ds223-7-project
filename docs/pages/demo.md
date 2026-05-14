# Pulse — Full Project Demo

**DS-223 Marketing Analytics · Group 7 · Spring 2026**  
**Team:** Silva Vardanyan (PM) · Albert Hakobyan (Backend) · Anzhelika Simonyan (Frontend) · Narek Dilbaryan (DB)

---

## The Problem

**Mer Lezun** is an Armenian writing and document-export SaaS on a freemium model. Free users can create documents and export them but hit feature limits on the free plan. Converting these users to **Pro (AMD 2,900/month)** is the core business challenge.

**Before Pulse, Mer Lezun had no:**

- Segmentation — all free users treated identically
- Campaign tooling — no interface to write or launch targeted messages
- A/B testing — no way to learn which message converts best
- Conversion analytics — no real-time dashboard

**Result:** generic, ineffective upgrade campaigns with no feedback loop.

---

## The Solution

**Pulse** is a free-to-paid conversion analytics platform built for Mer Lezun's PM team. It:

1. **Segments** 442 free users into 4 behavioral groups using K-Means clustering
2. **Lets PMs** craft and launch targeted in-app upgrade messages per segment
3. **Runs A/B tests** — control (generic message) vs. treatment (campaign message) — using Beta-Binomial Thompson Sampling
4. **Tracks KPIs** — conversion rate, churn, revenue, notification engagement — in a live dashboard
5. **Simulates user responses** via the User Demo screen, feeding real interaction data back into the ML pipeline

---

## Architecture

**6-container Docker Compose stack. One command to start everything:**

```bash
docker-compose up --build
```

### Containers

| Container | Technology | Port | Role |
|-----------|-----------|------|------|
| `db` | PostgreSQL 16 | 5433 | Primary database — 15 tables, 6 views, triggers, enums |
| `back` | FastAPI + SQLAlchemy | 8008 | REST API — 18 endpoints |
| `front` | Streamlit | 8501 | PM dashboard — 5 screens |
| `ds` | Python + Jupyter | 8888 | DS pipeline + notebooks |
| `etl` | Python | — | One-time seed — exits after run |
| `pgadmin` | pgAdmin 4 | 5050 | DB admin UI |

### Data Flow

```
Browser → Streamlit (front) → FastAPI (back) → PostgreSQL (db)
                                                      ↑
                              ETL seeds once on startup
                              DS pipeline writes segments, scores, A/B results
```

**Rule:** DS writes to DB. Backend reads from DB and handles user actions. Frontend only calls backend. No layer skips a level.

### Startup Sequence

```
docker-compose up --build
  ├── db          → starts, runs health check
  ├── etl         → loads schema, seeds 442 users, campaigns, templates → exits
  ├── back        → FastAPI serves on :8008
  ├── front       → Streamlit serves on :8501
  └── ds          → seed_events.py → segment_kmeans.py → run_ab_analysis.py → Jupyter
```

---

## Segmentation — K-Means (k=4)

Users are clustered on **7 behavioral features:**

| Feature | What it measures |
|---------|-----------------|
| `total_sessions` | Lifetime visits |
| `total_exports` | Lifetime document exports |
| `total_paywall_hits` | Times user hit a Pro feature limit |
| `total_thesaurus_uses` | Writing depth — synonym queries |
| `days_since_last_login` | Recency / churn risk |
| `sessions_per_week` | Rolling 30-day activity |
| `paywall_hits_last_7d` | Immediate upgrade pressure |

**Pipeline:** `SimpleImputer(median)` → `StandardScaler` → `KMeans(k=4, n_init=20)`

**Cluster naming** — by inspecting centroids in order:

1. Highest `days_since_last_login` → **Dormant**
2. Highest `total_exports + total_paywall_hits` → **Power**
3. Highest `sessions_per_week` → **Growing**
4. Remaining → **Casual**

**Result:**

| Segment | Users | Sessions/week | Avg Exports | Paywall Hits |
|---------|-------|--------------|-------------|--------------|
| Power | 66 | 8.9 | 9.5 | 25.5 |
| Growing | 107 | 0.6 | 5.2 | 0.1 |
| Casual | 176 | 0.3 | 2.0 | 0.1 |
| Dormant | 93 | 0.0 | 1.0 | 0.0 |

---

## Conversion Scoring — ML Model

Each user gets a **conversion probability score (0–1)** from a binary classifier trained on the same 7 features.

Two models compete on 5-fold stratified CV ROC-AUC. Winner saved to `outputs/final_model.pkl`.

| Model | Tuning |
|-------|--------|
| Logistic Regression | C, solver, L2 penalty |
| Random Forest | n_estimators, max_depth, min_samples_leaf |

Both use `class_weight='balanced'` to handle class imbalance (most users haven't converted).

Output per user: `conversion_prob`, `confidence_tier` (high/medium/low), `rank`.

---

## A/B Testing — Thompson Sampling

For each segment, the engine compares control vs. treatment conversion rates using **Beta-Binomial Thompson Sampling:**

```python
ctrl_samples  = Beta(conversions_ctrl + 1,  non_conversions_ctrl + 1,  10_000 draws)
treat_samples = Beta(conversions_treat + 1, non_conversions_treat + 1, 10_000 draws)

prob_treatment_wins = (treat_samples > ctrl_samples).mean()
# significant when >= 0.95
```

**Why Thompson Sampling?** Works with small samples, Bayesian, intuitive output, industry standard (Booking.com, Airbnb).

---

## Dashboard Screens

### Segments

![Segments](imgs/segments.png)

Live segment counts bar chart + behavioral averages table (sessions/week, exports, paywall hits) + per-user ML conversion probability scores.

---

### A/B Tests

![A/B Tests](imgs/ab_tests.png)

One card per segment showing: status, control rate, treatment rate, lift %, significance. Recalculate button reruns Thompson Sampling on the latest data instantly.

---

### KPIs

![KPIs](imgs/kpis.png)

Platform metrics filtered by time window (Last 7 / 30 / 90 days): conversion rate, avg revenue per conversion (AMD 2,900), churn rate, notification engagement rate.

---

### Campaign Editor

![Campaign Editor](imgs/campaigns.png)

Edit message templates with placeholders (`{{export_count}}`, `{{paywall_hits}}`, `{{price}}`, `{{discount}}`). Set channel (In-App / Email / Push) and trigger. Launch → sets campaign + ab_test to running. Reset → reverts to draft.

**Global Parameters:** test duration, discount %, min sample size, significance threshold, price, template count.

---

### User Demo

![User Demo](imgs/user_demo.png)

Side-by-side simulation of what a user sees:

- **Control** — generic baseline message
- **Treatment** — targeted campaign message

Click Accept Upgrade or Dismiss for either group → recorded in `conversion_outcomes` → hit Recalculate on A/B Tests → rates update instantly.

---

## Quick Start

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-7-project.git
cd ds223-7-project
docker-compose up --build
```

| URL | Service |
|-----|---------|
| [http://localhost:8501](http://localhost:8501) | PM Dashboard |
| [http://localhost:8008/docs](http://localhost:8008/docs) | API Swagger |
| [http://localhost:8888](http://localhost:8888) | Jupyter Notebooks |
| [http://localhost:5050](http://localhost:5050) | pgAdmin |
