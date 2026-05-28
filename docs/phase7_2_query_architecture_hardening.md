# Phase 7.2 — Query Architecture Hardening

Phase 7.2 strengthens performance and configurability before moving into deeper baseline/anomaly detection.

## Main goals

- Keep Command Center fast.
- Avoid hardcoded thresholds where studios need configurability.
- Add query budgets and over-budget diagnostics.
- Make table names configurable.
- Prepare ClickHouse rollup tables for future scale.
- Keep expensive sections lazy-loaded.
- Expose dashboard performance configuration to users.

## New configuration file

```text
config/dashboard_performance.json
```

This file controls:

```text
table names
feature flags
cache TTL policies
query budgets
parallelism limits
pressure scoring budgets
baseline history settings
dashboard row limits
pipeline health thresholds
```

You can override the path with:

```bash
AEGIS_DASHBOARD_PERFORMANCE_CONFIG=/path/to/dashboard_performance.json
```

## New Python module

```text
services/dashboard/performance_config.py
```

It loads the JSON config, merges it with safe defaults, and provides helpers such as:

```python
table_name("aggregate_zone_table")
query_budget_ms("command_center_pressure_timeline")
pressure_budget("network", "packet_loss_p95_budget", 5)
dashboard_limit("default_drilldown_limit", 1200)
```

## Query layer upgrades

`services/dashboard/query.py` now supports:

```text
configurable cache TTL constants
query budgets
over-budget diagnostics
configurable parallel fanout caps
budget_ms recorded per query call
```

The Query Performance workspace now shows:

```text
duration_ms
budget_ms
over_budget
rows
cache_policy
sql_hash
error
```

## Command Center upgrades

Command Center now uses:

```text
configurable table names
configurable pressure scoring budgets
configurable baseline history windows
configurable drilldown/timeline limits
configurable pipeline-health thresholds
```

## New workspace

```text
Data & Schemas > Performance Config
```

This view shows the active performance configuration as flattened settings and raw JSON.

## Rollup SQL templates

Included:

```text
sql/phase7_2_query_architecture_hardening.sql
```

This contains optional ClickHouse table templates for:

```text
agg_pressure_30s
agg_top_pressure_zones_1m
agg_context_baseline_1h
```

They are not automatically applied. They prepare the architecture for the next performance and analytics steps.

## Why this phase matters

This keeps the tool configurable and production-minded. A studio can tune pressure budgets by:

```text
game type
server tick model
region
platform
live event mode
map scale
backend capacity
```

without editing dashboard code.
