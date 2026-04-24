# ETL Pipeline

**Container:** `etl` · **Build:** `pulse/etl` · Runs once then exits.

## Overview

The ETL service is a one-shot Python container that runs on first startup to:

1. Check the database connection and verify all expected tables exist
2. Seed the database with initial user and campaign data from `data/users.csv`

The database schema itself (`init/01_schema.sql`) is applied automatically by the PostgreSQL Docker image via a mounted volume — the ETL container does not run migrations.

## Structure

```
pulse/etl/
├── Database/
│   ├── database.py        ← SQLAlchemy session factory
│   ├── models.py          ← ORM table definitions
│   └── data_generator.py  ← synthetic data generation helpers
├── data/
│   └── users.csv          ← seed user records (4,420 rows)
├── init/
│   └── 01_schema.sql      ← full DDL: tables, views, triggers, indexes
├── etl_process.py         ← main entry point
├── check_connection.py    ← DB health check + table verification
├── seed_flat_data.py      ← seeds all tables from CSV
├── requirements.txt
└── Dockerfile
```

## Running

The ETL container starts automatically with `docker-compose up`. It exits cleanly after seeding.

To run manually (e.g. after wiping the DB):

```bash
docker-compose run --rm etl python etl_process.py
```

## Data Sources

| File | Description |
|------|-------------|
| `data/users.csv` | 4,420 free-tier user records with segment labels |
| `init/01_schema.sql` | Full DDL: 15 tables, views, triggers, indexes |

## Expected Tables

After seeding, the database should contain:

`users`, `segments`, `user_segments`, `session_events`, `tool_usage_logs`, `paywall_events`, `campaigns`, `message_templates`, `global_params`, `ai_generation_log`, `ab_tests`, `ab_assignments`, `ab_test_results`, `notification_events`, `conversion_outcomes`
