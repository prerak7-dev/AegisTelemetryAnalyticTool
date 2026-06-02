# Phase 11.2 — Demo UX and Fast Feedback Loop

This patch improves the Demo Control Center experience before moving to the next phase.

## Fixed visual issues

The `Duration seconds` and `Events per second` inputs now have dedicated styling:

```text
visible labels
high-contrast input text
square dashboard styling
matching panel treatment
dark/light contrast aligned with the rest of the dashboard
```

## Smoother demo feedback

The demo used to feel silent for 10-15 seconds because the architecture has multiple stages:

```text
dashboard starts simulator process
  ↓
simulator sends events to collector
  ↓
collector publishes to Redpanda/Kafka
  ↓
processor inserts raw events
  ↓
processor closes aggregate windows
  ↓
agg_zone_30s and incidents become visible to dashboard workspaces
```

The aggregate table intentionally waits until the current window closes plus grace time, so aggregate-driven charts can lag behind raw ingestion.

## New Live Demo Feedback panel

The Demo Control Center now shows:

```text
generator state
raw event count
aggregate window count
incident count
max risk
latest raw event age
latest aggregate window age
latest incident age
scenario/build/experiment filters used for feedback
```

This makes the demo feel responsive immediately because raw ingestion is visible before aggregate windows are ready.

## Auto-refresh while demo is running

When scenario generators are active, the Demo Control Center auto-refreshes at a configurable interval:

```text
demo_control_center.status_refresh_seconds
```

Default:

```text
2 seconds
```

## Config added

```json
{
  "demo_control_center": {
    "status_refresh_seconds": 2,
    "feedback_window_minutes": 10,
    "processor_warmup_seconds": 3,
    "aggregate_window_seconds": 30,
    "aggregate_grace_seconds": 8,
    "show_pipeline_feedback": true
  }
}
```

## Architecture note

This patch does not fake aggregate data. It exposes the real pipeline stages so the user understands when data has reached raw ingestion versus aggregate analytics.
