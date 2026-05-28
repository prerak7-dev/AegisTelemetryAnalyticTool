# Phase 7.1 — Query Performance Foundation and Baseline Intelligence Preparation

This phase prioritizes quality and scale readiness instead of adding many new dashboard surfaces at once.

## Why

Phase 7 made Command Center more analytically powerful by promoting multiple pressure dimensions. The cost is that the dashboard can now execute more queries per refresh.

Phase 7.1 improves the query workflow before adding later phases such as build regression, fix validation, incident workflow, and demo control.

## Added

### 1. Named query diagnostics

Dashboard queries can now be executed with names:

```python
query_df_named(
    "command_center_pressure_timeline",
    sql,
    cache_policy="short",
)
```

The system records local query diagnostics:

```text
query_name
duration_ms
rows
cache_policy
cached
sql_hash
error
recorded_at
```

### 2. Cache TTL tiers

The query layer now has cache tiers:

```text
live    = 4 seconds
short   = 15 seconds
medium  = 60 seconds
static  = 300 seconds
```

This avoids refreshing slow-moving metadata as often as live cards.

### 3. Query Performance workspace

Added:

```text
Data & Schemas > Query Performance
```

This view shows:

```text
recorded queries
average query duration
slow queries
errors
slowest query names
recent query calls
cache-policy guidance
```

### 4. Lazy Command Center drilldowns

Expensive drilldown queries are now behind expanders:

```text
Pressure Drilldown / Top affected windows
Baseline Anomaly Preview / Context-aware thresholds
```

These queries only run when the analyst opens the section.

### 5. Baseline anomaly preview

Command Center now includes a baseline preview that compares the current active window against recent historical context for the same:

```text
source_profile
region
server_id
map_id
zone_id
```

It calculates:

```text
current_p95_frame
baseline_p95_frame
frame_ratio
frame_z
packet_loss_ratio
aoe_ratio
memory_ratio
anomaly_score
```

This is the foundation for full dynamic thresholds and anomaly detection.

## Future phases preserved

This phase intentionally prepares the system for:

```text
Phase 7 — Baselines, anomaly detection, dynamic thresholds
Phase 8 — Build regression analysis
Phase 9 — Experimentation and fix validation
Phase 10 — Alerting, ownership, incident workflow
Phase 11 — Demo control center and scenario library
Phase 12 — Analyst notebooks and SQL templates
Phase 13 — Production readiness layer
```

## Implementation notes

This phase does not add materialized views yet. The next production-scale step should move pressure scoring and baseline rollups into ClickHouse views/tables:

```text
agg_pressure_30s
agg_context_baseline_30s
agg_build_regression
```
