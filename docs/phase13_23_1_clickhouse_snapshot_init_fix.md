# Phase 13.23.1 — ClickHouse Snapshot Init Fix

This patch fixes ClickHouse startup failures caused by the Phase 13.23 snapshot SQL.

## Symptom

```text
dependency failed to start: container aegistelemetryanalytictool-clickhouse-1 exited (184)
```

## Likely root cause

ClickHouse exit code 184 usually indicates a query error during initialization. The Phase 13.23 snapshot SQL used view replacement and staleness-calculation patterns that can fail during docker-entrypoint init on the ClickHouse container.

## Fix

Snapshot SQL now uses:

```text
DROP VIEW IF EXISTS ...
CREATE VIEW ...
```

and staleness calculations now use a subquery:

```sql
SELECT
  latest_window,
  dateDiff('second', latest_window, now()) AS staleness_seconds
FROM
(
  SELECT max(window_start) AS latest_window
  FROM agg_zone_30s
)
```

## Updated files

```text
sql/live_snapshot_tables.sql
infra/clickhouse/init.sql
tools/apply_live_snapshot_tables.py
```

## Existing failed local volume

If ClickHouse failed during first initialization, reset the local dev volume:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

Warning: `docker compose down -v` removes local ClickHouse data.
