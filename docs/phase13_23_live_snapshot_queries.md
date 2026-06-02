# Phase 13.23 — Live Snapshot Tables and Lightweight Dashboard Queries

This phase adds a live snapshot query layer for smoother auto-refresh.

## Added

```text
ClickHouse live snapshot SQL views
dashboard snapshot table existence checks
safe fallback to aggregate tables
snapshot-backed KPI strip
snapshot-backed sidebar filters
snapshot-backed Command Center live queries
manual snapshot apply tool
documentation page
```

## New files

```text
services/dashboard/live_snapshots.py
sql/live_snapshot_tables.sql
tools/apply_live_snapshot_tables.py
docs/toolkit/production_readiness/live_snapshot_queries.md
docs/phase13_23_live_snapshot_queries.md
```

## Updated files

```text
services/dashboard/app.py
services/dashboard/sidebar.py
services/dashboard/views/command_center.py
services/dashboard/performance_config.py
config/dashboard_performance.json
config/documentation_navigation.json
infra/clickhouse/init.sql
README.md
```

## Snapshot tables/views

```text
live_pressure_summary_1m
live_fleet_health_30s
live_regional_pressure_1m
live_hot_zones_30s
latest_incident_summary
latest_demo_pipeline_status
```

## Existing local ClickHouse volumes

Run:

```bash
python tools/apply_live_snapshot_tables.py \
  --host localhost \
  --port 8123 \
  --database aegis_telemetry \
  --password aegis_dev_password
```

## Fallback safety

The dashboard only uses a snapshot table when the table/view exists. Otherwise it falls back to the existing aggregate table.
