# Dashboard

**Container:** `front` · **Port:** `8501` · **Build:** `pulse/app`

## Overview

The Pulse dashboard is a single-page Streamlit application with radio-button navigation across 5 screens. It connects exclusively to the FastAPI backend (`http://back:8000`) — it never touches the database directly.

## Screens

### 1. Segments

Shows the behavioral breakdown of all 442 free-tier users across the 4 K-Means segments.

**Components:**
- Segment counts bar chart (live from `GET /api/segments/counts`)
- Behavioral Averages table — sessions/week, exports, paywall hits per segment
- Per-user breakdown table with ML-predicted conversion probability and confidence tier

### 2. A/B Tests

Live Thompson Sampling results for each segment's running test.

**Components:**
- Summary cards — one per segment: status badge, control rate, treatment rate, lift %, significance
- Variant Comparison table — side-by-side across all segments
- Recalculate button — triggers `POST /api/ab-tests/run-analysis` to recompute on latest data

### 3. KPIs

Platform-level conversion and retention metrics with configurable time window.

**Components:**
- Period selector (Last 7 / 30 / 90 days) — wired to `GET /api/kpis?period=N`
- Four metric cards: conversion rate, avg revenue, churn rate, notification engagement

### 4. Campaign Editor

Edit and launch upgrade campaigns per segment.

**Components:**
- Segment selector (left panel)
- Message template textarea with placeholder syntax (`{{export_count}}`, `{{price}}`, etc.)
- Channel and trigger dropdowns
- Launch / Save / Reset to Draft action buttons
- Global Parameters section — test duration, discount %, min sample size, significance threshold, price, template count

**Status flow:**  
`Draft → Running` (Launch) · `Running → Draft` (Reset to Draft)

### 5. User Demo

Simulate what a real user sees and record their response.

**Components:**
- Segment selector dropdown
- Side-by-side columns: **Control** (generic message) vs **Treatment** (campaign message)
- Accept Upgrade / Dismiss buttons — enabled when campaign is running, greyed out when draft
- Response Stats panel (right side) — live accept/dismiss counts per segment from `GET /api/demo/stats`

## API Calls by Screen

| Screen | Endpoint | Method |
|--------|----------|--------|
| Segments | `/api/segments/counts` | GET |
| Segments | `/api/segments/behavioral-averages` | GET |
| Segments | `/api/segments/{name}/users` | GET |
| A/B Tests | `/api/ab-tests/summary` | GET |
| A/B Tests | `/api/ab-tests/comparison` | GET |
| A/B Tests | `/api/ab-tests/run-analysis` | POST |
| KPIs | `/api/kpis` | GET |
| Campaign Editor | `/api/campaigns` | GET |
| Campaign Editor | `/api/campaigns/{id}/message` | PUT |
| Campaign Editor | `/api/campaigns/{id}/launch` | POST |
| Campaign Editor | `/api/campaigns/{id}/reset` | POST |
| Campaign Editor | `/api/global-params` | GET |
| Campaign Editor | `/api/global-params/{key}` | PUT |
| User Demo | `/api/demo/message/{segment}` | GET |
| User Demo | `/api/demo/respond` | POST |
| User Demo | `/api/demo/stats` | GET |

## Tech Stack

- **Streamlit** — UI framework and state management
- **pandas** — dataframe display and transformation
- **requests** — HTTP client for API calls
- **python:3.11-slim** — Docker base image
