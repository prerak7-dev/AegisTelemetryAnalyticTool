# ClickHouse Partitioning and Rollup Strategy

ClickHouse is the analytics store for the toolkit.

## Current core tables

```text
raw_events
agg_zone_30s
data_quality_failures
incidents
```

## Recommended partitioning

For time-series telemetry:

```sql
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (source_profile, region, server_id, map_id, zone_id, event_time)
```

For aggregate windows:

```sql
PARTITION BY toYYYYMMDD(window_start)
ORDER BY (source_profile, region, server_id, map_id, zone_id, build_version, window_start)
```

For incidents:

```sql
PARTITION BY toYYYYMMDD(detected_at)
ORDER BY (severity, source_profile, region, server_id, detected_at)
```

## Why this order

The dashboard frequently filters by:

- source profile
- region
- server
- map
- zone
- time window
- build version

The order should help common dashboard queries prune data quickly.

## Rollup candidates

Production-scale deployments should add materialized or scheduled rollups for:

```text
regional_pressure_1m
server_pressure_1m
zone_pressure_5m
baseline_anomaly_windows
build_regression_results
fix_validation_results
query_performance_daily
```

## TTL strategy

Suggested:

```sql
ALTER TABLE raw_events MODIFY TTL event_time + INTERVAL 3 DAY;
ALTER TABLE agg_zone_30s MODIFY TTL window_start + INTERVAL 90 DAY;
ALTER TABLE incidents MODIFY TTL detected_at + INTERVAL 180 DAY;
```

Adjust based on compliance and storage budgets.

## Query hygiene

Prefer:

- aggregate tables over raw events for dashboards
- bounded time filters
- explicit row limits
- precomputed rollups for expensive comparisons
- query budget tracking

Avoid:

- unbounded raw scans
- high-cardinality group-bys without a time filter
- joining large raw tables inside Streamlit views
