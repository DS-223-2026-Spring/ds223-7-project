# Model Engine

**Container:** `ds` · **Port:** `8888` · **Build:** `pulse/ds`

## Overview

The Data Science service runs a Jupyter notebook server connected directly to the PostgreSQL database. It is used for exploratory analysis, segmentation model development, and A/B test statistical calculations.

## Notebooks

| Notebook | Location | Description |
|----------|----------|-------------|
| `experiments.ipynb` | `pulse/ds/experiments.ipynb` | Main analysis: segmentation, A/B testing, KPI calculations |
| `eda.ipynb` | `pulse/ds/notebooks/eda.ipynb` | Exploratory data analysis |

## File Structure

```
pulse/ds/
├── experiments.ipynb    ← primary experiments notebook
├── notebooks/
│   └── eda.ipynb        ← exploratory data analysis
├── Database/
│   └── database.py      ← SQLAlchemy session for DB access
├── requirements.txt
└── Dockerfile
```

## Access

Jupyter runs at `http://localhost:8888` with no token required (development mode).

## Segmentation Model

Users are segmented into four behavioural groups using session activity, export frequency, and paywall interaction:

| Segment | Logic |
|---------|-------|
| **Power writers** | High export frequency + regular paywall hits |
| **Growing writers** | Rising session frequency, below paywall threshold |
| **Casual writers** | Low frequency, high template browse rate |
| **Dormant writers** | No activity in last 30+ days |

## A/B Test Statistics

Statistical significance is measured using a **chi-square test** on conversion counts (control vs treatment group). A test is marked significant when `p < 0.05`.

## Tech Stack

- **Jupyter Notebook** — interactive analysis environment
- **pandas** — data manipulation
- **scipy** — statistical tests (chi-square)
- **SQLAlchemy** — direct DB connection for queries
- **python:3.13-slim** — Docker base image
