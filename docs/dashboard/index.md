# Dashboard

**Container:** `front` · **Port:** `8501` · **Build:** `pulse/app`

## Overview

The Pulse dashboard is a multi-page Streamlit application. It connects to the FastAPI backend (`http://back:8000`) and presents real-time data across five screens. The PM team uses it to monitor conversion KPIs, review A/B test results, and manage campaigns.

## Screens

| Screen | Route | Description |
|--------|-------|-------------|
| Segments | `/` | User segment breakdown — counts and behavioural averages |
| A/B Tests | `pages/` | Live A/B test cards and segment comparison table |
| KPIs | `pages/` | Platform-wide conversion rate, retention, churn metrics |
| Campaign Editor | `pages/` | Edit message templates, set channel/trigger, launch/reset |
| User Demo | `pages/` | Phone mockup showing rendered upgrade message per segment |

## File Structure

```
pulse/app/
├── app.py               ← main Streamlit entry point + navigation
├── components/
│   ├── sidebar.py       ← navigation sidebar component
│   ├── metrics.py       ← reusable KPI metric cards
│   └── campaign_form.py ← campaign editor form component
├── pages/
│   ├── page1.py         ← screen stubs (to be wired to API)
│   └── page2.py
├── requirements.txt
└── Dockerfile
```

## API Calls

The frontend reads exclusively from these backend endpoints:

| Screen | Endpoint |
|--------|----------|
| Segments | `GET /api/segments/counts`, `GET /api/segments/behavioral-averages` |
| A/B Tests | `GET /api/ab-tests/summary`, `GET /api/ab-tests/comparison` |
| KPIs | `GET /api/kpis` |
| Campaign Editor | `GET /api/campaigns`, `PUT /api/campaigns/{id}`, `PUT /api/campaigns/{id}/message`, `POST /api/campaigns/{id}/launch` |
| User Demo | `GET /api/demo/message/{segment}`, `POST /api/demo/respond` |

## Tech Stack

- **Streamlit** — UI framework
- **requests** — HTTP client for API calls
- **python:3.13-slim** — Docker base image
