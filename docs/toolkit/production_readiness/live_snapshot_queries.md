# Live Snapshot Tables and Lightweight Dashboard Queries

Phase 13.23 adds a live snapshot query layer.

## Why this exists

Auto-refresh feels slow when the dashboard repeatedly runs expensive aggregations against broad telemetry tables.

The live snapshot layer gives dashboards smaller, stable query targets:

```text
live_pressure_summary_1m
live_fleet_health_30s
live_regional_pressure_1m
live_hot_zones_30s
latest_incident_summary
latest_demo_pipeline_status
```

In local development these are ClickHouse views. In production they can be replaced by materialized views or scheduled rollup tables using the same names.

## SQL assets

```text
sql/live_snapshot_tables.sql
```

For new local ClickHouse volumes, the views are also appended to:

```text
infra/clickhouse/init.sql
```

## Existing local volumes

ClickHouse init scripts only run when a volume is first created. For an existing local volume, apply the views manually:

```bash
python tools/apply_live_snapshot_tables.py \
  --host localhost \
  --port 8123 \
  --database aegis_telemetry \
  --password aegis_dev_password
```

From inside Docker/container context, use:

```bash
python tools/apply_live_snapshot_tables.py \
  --host clickhouse \
  --port 8123 \
  --database aegis_telemetry \
  --password aegis_dev_password
```

## Dashboard fallback behavior

The dashboard prefers snapshot tables when:

```text
feature_flags.prefer_live_snapshot_tables = true
the configured snapshot table/view exists in ClickHouse
```

If a table/view does not exist, the dashboard falls back to the existing aggregate table.

This keeps old developer environments working.

## Config

Table names are configured in:

```text
config/dashboard_performance.json
```

```json
{
  "tables": {
    "live_fleet_health_table": "live_fleet_health_30s",
    "live_pressure_summary_table": "live_pressure_summary_1m",
    "live_regional_pressure_table": "live_regional_pressure_1m",
    "live_hot_zone_table": "live_hot_zones_30s"
  },
  "feature_flags": {
    "prefer_live_snapshot_tables": true,
    "enable_live_snapshot_badges": true
  }
}
```

## Updated query paths

The following dashboard paths now prefer snapshots:

```text
KPI strip
Sidebar source-profile inventory
Sidebar server inventory
Command Center live pressure summary
Command Center pressure timeline
Command Center pressure drilldown
Command Center frame-time timeline
Command Center worst hot zones
Command Center regional summary
```

## Production evolution

For production, replace the local views with materialized tables:

```text
raw/aggregate ingestion
  ↓
materialized/scheduled snapshot tables
  ↓
dashboard reads small snapshot tables
```

This keeps heavy aggregation outside the UI request path.


## Phase 13.23.2 aggregation-safety note

The default local snapshot views are pass-through views over `agg_zone_30s`.
They intentionally do not aggregate, because the dashboard still applies
aggregation functions over the configured live table.

Production materialized snapshots can pre-aggregate, but dashboard SQL must
then be changed to read final scalar columns directly instead of applying
another aggregate layer.

Optional snapshot views are no longer installed in `infra/clickhouse/init.sql`
so ClickHouse startup cannot be blocked by optional optimization SQL.
