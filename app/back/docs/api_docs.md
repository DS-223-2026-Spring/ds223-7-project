# Pulse API — Documentation

**Backend Developer** · Branch: `backend` · Folder: `app/back/`

## Quick start

```bash
# Inside the project root, once docker-compose.yml is ready:
docker-compose up --build backend
# API docs auto-generated at http://localhost:8000/docs
```

## Architecture decisions

All database access uses **SQLAlchemy** with raw `text()` queries against the pre-built views. ORM models were intentionally skipped in this first iteration because the schema is owned by the DB Developer and may still change — raw SQL against stable views is safer until the schema is frozen.

**Connection string:** `postgresql://pulse_user:pulse_pass@db:5432/pulse`

The backend container hostname is `backend` on the Docker network. The frontend calls `http://backend:8000`. The database hostname is `db`.

## Endpoint reference

### Segments screen

| Method | Path | View / Table | Purpose |
|--------|------|-------------|---------|
| GET | `/api/segments/counts` | `v_segment_counts` | Four segment KPI cards |
| GET | `/api/segments/behavioral-averages` | `v_segment_behavioral_averages` | Bar chart data |

### A/B Tests screen

| Method | Path | View / Table | Purpose |
|--------|------|-------------|---------|
| GET | `/api/ab-tests/summary` | `v_ab_test_summary` | Test cards with live counts |
| GET | `/api/ab-tests/comparison` | `v_segment_ab_comparison` | Bottom comparison table |

### KPIs screen

| Method | Path | View / Table | Purpose |
|--------|------|-------------|---------|
| GET | `/api/kpis` | `v_platform_kpis` | Top metric row (4 numbers) |

### Campaign Editor screen

| Method | Path | View / Table | Purpose |
|--------|------|-------------|---------|
| GET | `/api/campaigns` | `campaigns` + `message_templates` | All campaign cards |
| GET | `/api/campaigns/{id}` | same | Single campaign |
| PUT | `/api/campaigns/{id}` | `campaigns` | Update channel / trigger |
| PUT | `/api/campaigns/{id}/message` | `message_templates` | Edit message body |
| POST | `/api/campaigns/{id}/launch` | `campaigns` | Set status → running |
| DELETE | `/api/campaigns/{id}/reset` | `campaigns` | Reset to draft |
| GET | `/api/global-params` | `global_params` | Shared params |
| PUT | `/api/global-params/{key}` | `global_params` | Update a param |

### User Demo screen

| Method | Path | View / Table | Purpose |
|--------|------|-------------|---------|
| GET | `/api/demo/message/{segment}` | `campaigns` + `message_templates` + `global_params` | Rendered upgrade message |
| POST | `/api/demo/respond` | `conversion_outcomes` | Record upgrade/skip |

### Health

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness probe |

## Assumptions

1. The DB container is named `db` and exposes port 5432 on the Docker network.
2. The `pulse_schema.sql` has been run by the DB Developer before the backend starts. The backend does not create or migrate tables.
3. The four segments and four campaigns with default message templates are seeded by `pulse_schema.sql` — the backend reads them, never creates them from scratch.
4. Trigger-maintained columns (`total_sessions`, `total_exports`, `total_paywall_hits`, `total_thesaurus_uses`, `duration_seconds`, `days_since_last_login`) are never updated by backend code.
5. All dashboard reads go through the `v_*` views, never raw base tables.
6. The `{{placeholder}}` rendering in message templates uses the three global_params keys: `pro_price_amd`, `dormant_discount`, `template_count`. User-specific placeholders (`{{export_count}}`, `{{paywall_hits}}`) use dummy values for now — they need real user context from the frontend or session.
7. The "Write with AI" feature (inserting into `ai_generation_log`) is not yet implemented — it depends on the Model container (port 8001) being available.
8. A/B test creation logic (random 50/50 split into `ab_assignments`) is not yet implemented — it will be added when the Data Scientist's model container is ready.

## Pending dependencies

| What | Blocked by | Status |
|------|-----------|--------|
| `docker-compose.yml` wiring | PM | Pending — PM needs to add the `backend` service |
| Seed data in DB | DB Developer running `pulse_schema.sql` | Schema is written, needs to be executed |
| "Write with AI" endpoint | Model container (port 8001) | Not started |
| A/B test creation + assignment | Data Scientist | Not started |
| Real user-level placeholder values | Frontend passing user context | Dummy values used |

## Error handling

Every endpoint handles empty results gracefully — if the DB is unreachable or a view returns no rows, the endpoint returns an empty list `[]` or a zeroed-out object instead of crashing. The frontend should handle these empty states too.
