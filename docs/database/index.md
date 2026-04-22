# Database

## Overview

PostgreSQL 16 is the single source of truth for all Pulse data. The schema is applied automatically on first container start via the `init/01_schema.sql` file mounted into the postgres container.

## Key Tables

| Table | Description |
|-------|-------------|
| `users` | Free-tier user records with segment assignment |
| `segments` | The four user segments (Power, Growing, Casual, Dormant) |
| `campaigns` | One campaign per segment; tracks channel, trigger, status |
| `message_templates` | Versioned message bodies per campaign |
| `ab_tests` | A/B test variants with impression and conversion counts |
| `global_params` | Shared tunable parameters (price, discount, template count) |

## Views

All dashboard reads go through `v_*` views — never raw tables. This decouples the API from table implementation details.

| View | Purpose |
|------|---------|
| `v_segment_summary` | Aggregated user counts and funnel rates per segment |
| `v_ab_results` | A/B test lift and statistical summary |
| `v_kpi_overview` | Platform-wide conversion rate, time-to-convert, retention |

## Connection

```
Host (external):  localhost:5433
Host (internal):  db:5432
Database:         ${DB_NAME}
User:             ${DB_USER}
```

## pgAdmin

Accessible at `http://localhost:5050`. Login with `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD` from `.env`.