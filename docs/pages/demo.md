# Demo Walkthrough

**Stack:** Streamlit · FastAPI · PostgreSQL · Docker Compose  
**Start:** `docker-compose up --build` → open [http://localhost:8501](http://localhost:8501)

---

## Segments

The first screen shows who Mer Lezun's free users are, broken into four behavioral clusters produced by **K-Means (k=4)**.

**What you see:**

- **Segment counts bar chart** — live from `GET /api/segments/counts`
- **Behavioral Averages table** — sessions/week, exports, paywall hits per segment, from `GET /api/segments/behavioral-averages`
- **Per-user breakdown table** — each user's predicted conversion probability from the ML model, from `GET /api/segments/{name}/users`

| Segment | Users | Sessions/week | Avg Exports | Paywall Hits |
|---------|-------|--------------|-------------|--------------|
| Power | 66 | 8.9 | 9.5 | 25.5 |
| Growing | 107 | 0.6 | 5.2 | 0.1 |
| Casual | 176 | 0.3 | 2.0 | 0.1 |
| Dormant | 93 | 0.0 | 1.0 | 0.0 |

**How K-Means assigns segments:**  
The model fits on 7 behavioral features (`total_sessions`, `total_exports`, `total_paywall_hits`, `total_thesaurus_uses`, `days_since_last_login`, `sessions_per_week`, `paywall_hits_last_7d`), then maps each cluster to a name by inspecting centroids:

1. Highest `days_since_last_login` → **Dormant**
2. Highest `total_exports + total_paywall_hits` → **Power**
3. Highest `sessions_per_week` → **Growing**
4. Remaining → **Casual**

---

## A/B Tests

Thompson Sampling A/B test results — control vs. treatment conversion rates per segment.

**What you see:**

- **Summary cards** — one per segment showing status, control rate, treatment rate, lift %, and whether the test is significant
- **Variant Comparison table** — side-by-side breakdown across all segments
- **Recalculate button** — re-runs Thompson Sampling on the latest `conversion_outcomes` data immediately (`POST /api/ab-tests/run-analysis`)

**When is a test significant?**  
The model draws 10,000 samples from `Beta(conversions+1, non-conversions+1)` for each variant. When `P(treatment wins) ≥ 0.95`, the test is marked **significant** — meaning the treatment message is confidently better than the control.

Data sources: `GET /api/ab-tests/summary`, `GET /api/ab-tests/comparison`

---

## KPIs

Platform-level metrics filtered by time window (Last 7 / 30 / 90 days).

| KPI | Description |
|-----|-------------|
| **Overall conversion rate** | Upgraded users ÷ total free users in period |
| **Avg revenue per conversion** | Average `revenue_amd` from `conversion_outcomes` (AMD 2,900/month flat) |
| **Churn rate (30d)** | Users who churned within 30 days of upgrading |
| **Notification engagement rate** | Opened or clicked ÷ total notifications shown |

All four metrics recalculate dynamically when the period selector changes.  
Data source: `GET /api/kpis?period=7|30|90`

---

## Campaign Editor

Create and manage upgrade campaigns per segment. Edit message templates, set delivery parameters, and launch.

**How to use:**

1. Select a segment from the left panel (Power / Growing / Casual / Dormant)
2. Edit the **Message template** — use placeholders:
    - `{{export_count}}` — user's lifetime export count
    - `{{paywall_hits}}` — times user hit a Pro limit
    - `{{price}}` — AMD 2,900 (from global params)
    - `{{discount}}` — % discount (from global params)
    - `{{template_count}}` — number of Pro templates
3. Set **Channel** (In-App Popup / Email / Push Notification) and **Trigger** (On Paywall Hit / On App Open / After 3rd Export)
4. Click **Launch** — sets campaign status to `running`, syncs ab_test to `running`
5. Click **Save** — saves draft message without launching
6. Click **Reset to Draft** — reverts to draft, pauses ab_test

**Global Parameters** (bottom of screen) — shared across all campaigns:

| Parameter | Default |
|-----------|---------|
| Test Duration (days) | 7 |
| Discount % | 20 |
| Min Sample Size | 50 |
| Significance Threshold | 0.05 |
| Price (AMD) | 2900 |
| Template Count | 120 |

Backend calls: `GET/PUT /api/campaigns/{id}`, `POST /api/campaigns/{id}/launch`, `POST /api/campaigns/{id}/reset`, `GET/PUT /api/global-params/{key}`

---

## User Demo

Simulate the upgrade message a real free-tier user would see. Record their simulated response to feed real conversion outcome data back into the system.

**How to use:**

1. Select a segment from the dropdown
2. Both **Control** (generic baseline message) and **Treatment** (campaign message) are shown side by side
3. Click **Accept Upgrade** or **Dismiss** for either group to record the outcome
4. Response is written to `conversion_outcomes` via `POST /api/demo/respond`
5. Hit **Recalculate** on the A/B Tests screen to see updated conversion rates immediately

**When is the treatment group active?**  
The treatment buttons are enabled only when a campaign is in `running` status. If the campaign is in `draft`, both columns are visible but the treatment buttons are greyed out with a note to launch the campaign first.

**What happens under the hood:**

```
Click "Accept Upgrade" (treatment)
    → POST /api/demo/respond
    → Backend writes to conversion_outcomes
         (user_id from treatment ab_assignment, decision = 'upgraded')
    → Click Recalculate on A/B Tests
    → Thompson Sampling reruns on fresh data
    → treatment_rate updates in dashboard
```

The **Response Stats** panel on the right shows live accept/dismiss counts per segment, from `GET /api/demo/stats`.

---

## Running the DS Pipeline

The DS pipeline runs automatically on container startup. To re-run manually:

```bash
docker-compose exec ds bash run_ds_pipeline.sh
```

| Step | Script | What it does |
|------|--------|--------------|
| 1 | `seed_events.py` | Seeds `session_events` and `paywall_events` with realistic timestamps |
| 2 | `segment_kmeans.py` | Fits K-Means, writes new `user_segments` assignments |
| 3 | `run_ab_analysis.py` | Runs Thompson Sampling, writes `ab_test_results` |
| 4 | `predict.py` | Trains logistic regression / random forest, scores all 442 users |
| 5 | `segment_summary.py` | Exports `outputs/segment_summary.csv` and `.json` |

---

## API — Swagger UI

All 18 endpoints are documented and testable at [http://localhost:8008/docs](http://localhost:8008/docs).

| Group | Endpoints |
|-------|-----------|
| `segments` | `GET /counts`, `/behavioral-averages`, `/{name}/users` |
| `ab-tests` | `GET /summary`, `/comparison`, `POST /run-analysis` |
| `kpis` | `GET /api/kpis` |
| `campaigns` | `GET/PUT /{id}`, `POST /{id}/launch`, `/{id}/reset`, `PUT /{id}/message` |
| `global-params` | `GET /api/global-params`, `PUT /{key}` |
| `demo` | `GET /message/{segment}`, `POST /respond`, `GET /stats` |
| `health` | `GET /health` |
