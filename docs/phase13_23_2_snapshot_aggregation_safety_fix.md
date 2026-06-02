# Phase 13.23.2 — ClickHouse Snapshot Aggregation Safety Fix

This patch fixes the remaining ClickHouse `ILLEGAL_AGGREGATION` failure.

## Symptom

```text
ClickHouse rejects init/query SQL with ILLEGAL_AGGREGATION
```

The issue is aggregate-on-aggregate behavior. The dashboard still performs aggregate queries over the configured live snapshot table. If the snapshot view itself also contains aggregate functions, ClickHouse can reject the resulting query as nested aggregation.

## Fix

The default local-development snapshot views are now pass-through compatibility views over:

```text
agg_zone_30s
```

They do not aggregate. This means the dashboard can safely keep aggregating over the configured live snapshot table.

## Important startup safety change

Optional snapshot views are no longer appended to:

```text
infra/clickhouse/init.sql
```

ClickHouse startup now only creates the core tables. Optional snapshot views are installed manually after ClickHouse is healthy.

## Apply optional snapshot views

For an existing local stack:

```bash
python tools/apply_live_snapshot_tables.py \
  --host localhost \
  --port 8123 \
  --database aegis_telemetry \
  --password aegis_dev_password
```

Inside Docker/container network:

```bash
python tools/apply_live_snapshot_tables.py \
  --host clickhouse \
  --port 8123 \
  --database aegis_telemetry \
  --password aegis_dev_password
```

## Reset after failed init

If ClickHouse failed during initialization, reset the local volume:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

Warning: this deletes local ClickHouse data.
