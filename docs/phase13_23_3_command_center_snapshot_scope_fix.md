# Phase 13.23.3 — Command Center Snapshot Scope Fix

This patch fixes a runtime NameError in the Command Center.

## Symptom

```text
NameError: name 'live_pressure_table' is not defined
```

Trace:

```text
render_pipeline_health(context)
FROM {live_pressure_table}
```

## Root cause

`live_pressure_table` was defined inside the main `render()` function, but `render_pipeline_health()` is a separate helper function. The helper referenced a local variable that was outside its scope.

## Fix

`render_pipeline_health()` now resolves its own preferred live table locally:

```python
live_health_table, using_health_snapshot = preferred_live_table(
    snapshot_config_key="live_pressure_summary_table",
    fallback_config_key="aggregate_zone_table",
)
```

The pipeline-health SQL now uses:

```text
live_health_table
```

instead of the undefined:

```text
live_pressure_table
```

The staleness query was also made ClickHouse-safe by calculating `max(window_start)` in a subquery before applying `dateDiff`.
