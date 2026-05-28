# Phase 3.1 — No Migration Local Reset

This version removes the `clickhouse-migrate` service from Docker Compose.

For local development, schema changes are handled by clearing the local ClickHouse volume and letting the current `init.sql` recreate fresh tables.

## Run

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

This deletes the old local ClickHouse data volume and recreates:

- `raw_events`
- `agg_zone_30s`
- `incidents`
- `data_quality_failures`

with the current `source_profile` schema.

## Why this version exists

The migration container was useful in theory, but Docker/ClickHouse readiness timing made it fragile locally. Since this is a portfolio/dev stack, a clean volume reset is simpler and more reliable.
