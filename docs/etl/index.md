# ETL

## Overview

The ETL service (`myapp/etl`) is a one-shot container that runs on first startup to:

1. Apply the database schema (`init/01_schema.sql`) — handled automatically by the PostgreSQL Docker image via the mounted volume
2. Seed the database with initial user and campaign data from `data/users.csv`

## Structure

```
myapp/etl/
├── Database/
│   ├── __init__.py
│   ├── database.py      ← SQLAlchemy session factory
│   ├── models.py        ← ORM table definitions
│   └── data_generator.py ← synthetic data generation helpers
├── data/
│   └── users.csv        ← seed user records
├── init/
│   └── 01_schema.sql    ← full DB schema (DDL)
├── __init__.py
├── etl_process.py       ← main entry point
├── requirements.txt
└── Dockerfile
```

## Running

The ETL container starts automatically with `docker-compose up`. It exits after seeding.

To run manually:

```bash
docker-compose run --rm etl python etl_process.py
```

## Data Sources

| File | Description |
|------|-------------|
| `data/users.csv` | Seed free-tier user records with segment labels |
| `init/01_schema.sql` | Full DDL: tables, views, triggers, indexes |