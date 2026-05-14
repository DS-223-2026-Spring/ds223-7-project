# Model Engine

**Container:** `ds` · **Port:** `8888` · **Build:** `pulse/ds`

## Overview

The DS service runs two independent ML models and a Bayesian A/B test engine, all connected directly to PostgreSQL.

| Model | Purpose | Output |
|-------|---------|--------|
| **K-Means clustering** | Segment users into 4 behavioral groups | `user_segments` table |
| **Logistic Regression / Random Forest** | Score each user's conversion probability | `user_conversion_scores` table |
| **Thompson Sampling** | Measure A/B test significance | `ab_test_results` table |

---

## 1. Segmentation — K-Means (k=4)

**Script:** `segment_kmeans.py`

### Features (7 behavioral signals)

| Feature | Description |
|---------|-------------|
| `total_sessions` | Lifetime session count |
| `total_exports` | Lifetime document exports |
| `total_paywall_hits` | Times user hit a Pro feature limit |
| `total_thesaurus_uses` | Lifetime synonym/thesaurus queries |
| `days_since_last_login` | Recency — days since last visit |
| `sessions_per_week` | Rolling 30-day session frequency |
| `paywall_hits_last_7d` | Paywall hits in the past 7 days |

### Pipeline

```
v_user_behavioral_features (PostgreSQL view)
    │
    ▼
SimpleImputer(strategy='median')   ← fills any missing values
    │
    ▼
StandardScaler()                   ← normalizes all features to same scale
    │
    ▼
KMeans(k=4, n_init=20)             ← fits 20 random restarts for stability
    │
    ▼
map_clusters_to_segments()         ← names clusters by inspecting centroids:
    │   1. highest days_since_last_login  → dormant
    │   2. highest exports + paywall_hits → power
    │   3. highest sessions_per_week      → growing
    │   4. remaining                      → casual
    ▼
user_segments table                ← old assignments expired, new ones inserted
outputs/kmeans_model.pkl           ← model saved for reuse
```

### Why K-Means?

K-Means is appropriate here because:

- We know the number of segments upfront (4 — defined by the business problem)
- The features are continuous and numeric — ideal for distance-based clustering
- The centroid naming logic makes segment assignment interpretable and stable across runs

---

## 2. Conversion Scoring — Logistic Regression / Random Forest

**Script:** `predict.py` (trains via `final_model.py`)

### What it predicts

Binary target: `converted = 1` if user has an `upgraded` outcome in `conversion_outcomes`, else `0`.

### Training

Two models compete on **5-fold stratified cross-validation ROC-AUC**. The winner is saved to `outputs/final_model.pkl`.

| Model | Tuning |
|-------|--------|
| Logistic Regression | C ∈ {0.01, 0.1, 1.0, 10.0}, solver, L2 penalty |
| Random Forest | n_estimators ∈ {100, 200}, max_depth ∈ {4, 6, None} |

Both use `class_weight='balanced'` to handle the fact that most users have NOT converted.

### Output per user

```python
conversion_prob    # 0.0 → 1.0 probability of converting
confidence_tier    # 'high' (>0.70) / 'medium' (0.30–0.70) / 'low' (<0.30)
rank               # 1 = most likely to convert across all 442 users
```

Written to `user_conversion_scores` (upserted — safe to re-run).  
Visible in the **Segments** screen → per-user breakdown table.

### Top predictor

The feature with the highest absolute coefficient (LR) or Gini importance (RF) is written to `ab_test_results` as `top_predictor_feature`. This surfaces in the A/B Tests screen to explain what drove the result.

---

## 3. A/B Test Statistics — Thompson Sampling

**Script:** `run_ab_analysis.py` · **Endpoint:** `POST /api/ab-tests/run-analysis`

### How it works

For each segment's A/B test, the engine reads control and treatment conversion counts from `conversion_outcomes` and runs **Beta-Binomial Thompson Sampling**:

```python
# Posterior parameters (uniform Beta(1,1) prior)
ctrl_alpha  = conversions_control + 1
ctrl_beta   = non_conversions_control + 1
treat_alpha = conversions_treatment + 1
treat_beta  = non_conversions_treatment + 1

# 10,000 Monte Carlo draws from each Beta posterior
ctrl_samples  = rng.beta(ctrl_alpha,  ctrl_beta,  10_000)
treat_samples = rng.beta(treat_alpha, treat_beta, 10_000)

prob_treatment_wins = (treat_samples > ctrl_samples).mean()
```

### Significance rule

```
prob_treatment_wins >= 0.95  →  significant (treatment confidently better)
prob_treatment_wins <  0.95  →  not significant (need more data)
```

### Why Thompson Sampling?

- **No minimum sample size assumption** — gives a result even with small counts
- **Bayesian** — accounts for uncertainty (small samples → wide posteriors → less confident)
- **Intuitive** — the output is a plain probability: "treatment wins 97% of the time"
- **Industry standard** for online A/B testing (used by Booking.com, Airbnb)

### Triggering re-analysis

Re-analysis runs automatically at container startup and can be triggered at any time from the dashboard:

```
A/B Tests screen → "Recalculate" button
    → POST /api/ab-tests/run-analysis
    → Thompson Sampling on latest conversion_outcomes
    → Updated rates, lift, significance written to ab_test_results
    → Dashboard refreshes
```

---

## Running the Full Pipeline

```bash
docker-compose exec ds bash run_ds_pipeline.sh
```

| Step | Script | Writes |
|------|--------|--------|
| 1 | `seed_events.py` | `session_events`, `paywall_events` |
| 2 | `segment_kmeans.py` | `user_segments`, `kmeans_model.pkl` |
| 3 | `run_ab_analysis.py` | `ab_test_results`, `ab_assignments` |
| 4 | `predict.py` | `user_conversion_scores`, `predictions.csv` |
| 5 | `segment_summary.py` | `segment_summary.csv`, `segment_summary.json` |
