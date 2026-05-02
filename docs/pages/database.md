# Database

**Container:** `db` · **Port:** `5433` (external) / `5432` (internal) · **Image:** `postgres:16-alpine`

## Overview

PostgreSQL 16 is the single source of truth for all Pulse data. The schema (`pulse/etl/init/01_schema.sql`) is applied automatically on first container start via a Docker volume mount into `/docker-entrypoint-initdb.d/`.

## Tables (15)

| Table | Description |
|-------|-------------|
| `users` | Free-tier user records |
| `segments` | The four user segments (Power, Growing, Casual, Dormant) |
| `user_segments` | Many-to-one user → segment assignments with expiry |
| `session_events` | Per-session activity (start, duration, tool usage) |
| `tool_usage_logs` | Individual tool invocations (synonym, template, export) |
| `paywall_events` | Times a user hit a feature limit |
| `campaigns` | One campaign per segment; tracks channel, trigger, status |
| `message_templates` | Versioned message bodies per campaign (with active flag) |
| `global_params` | Shared tunable parameters (price, discount, template count) |
| `ai_generation_log` | Log of AI-generated message variants |
| `ab_tests` | A/B test runs per campaign |
| `ab_assignments` | Which group (control/treatment) each user is in |
| `ab_test_results` | Aggregated conversion counts per variant |
| `notification_events` | Delivery and open events for campaign messages |
| `conversion_outcomes` | Final upgrade / try-later decisions per user |

## Views (6)

All dashboard reads go through `v_*` views — the API never queries raw tables directly.

| View | Used by | Purpose |
|------|---------|---------|
| `v_segment_counts` | Segments screen | User count per segment |
| `v_segment_behavioral_averages` | Segments screen | Avg exports, paywall hits, synonym depth per segment |
| `v_ab_test_summary` | A/B Tests screen | Live A/B test counts + chi-square results |
| `v_segment_ab_comparison` | A/B Tests screen | Control vs treatment conversion rate comparison |
| `v_platform_kpis` | KPIs screen | Overall conversion rate, engagement, churn, revenue |
| `v_user_behavioral_features` | Data Science | Raw features for segmentation model |

## Connection

```
Host (external):  localhost:5433
Host (internal):  db:5432
Database:         pulse
User:             pulse_user
Password:         pulse_pass  (dev default — see pulse/.env)
```

## pgAdmin

Accessible at `http://localhost:5050`.

**Login:** `admin@admin.com` / `admin`

Connect to the server with host `db`, port `5432`, user `pulse_user`.
