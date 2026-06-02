# Phase 7.3 — Baselines, Anomaly Detection, and Dynamic Thresholds

This phase moves the tool beyond static-threshold thinking.

Instead of only asking:

```text
Is p95 frame >= 50 ms?
```

the dashboard can now ask:

```text
Is this value abnormal for this source / region / server / map / zone context?
```

## New workspace

```text
Incidents > Baseline Intelligence
```

## What it does

The workspace compares the active filtered window against a configurable historical baseline.

It calculates:

```text
frame_ratio
frame_z
packet_loss_ratio
aoe_ratio
memory_ratio
physics_ratio
replication_ratio
player_impact_ratio
anomaly_score
dominant_anomaly_metric
baseline_confidence
dynamic warning / critical frame thresholds
dynamic warning / critical packet-loss thresholds
```

## Configurable baseline scope

Supported scopes are controlled by `config/dashboard_performance.json`:

```text
source_region_server_map_zone
source_region_map_zone
source_region
source_profile
```

## Configurable dynamic thresholds

Dynamic threshold parameters are configured in:

```text
baseline.dynamic_thresholds
```

Example:

```json
{
  "warning_z": 2.0,
  "critical_z": 3.0,
  "warning_ratio": 1.35,
  "critical_ratio": 1.75
}
```

## Configurable confidence

Baseline confidence is controlled by:

```text
baseline.minimum_baseline_rows
baseline.confidence.minimum_confidence
baseline.confidence.strong_sample_multiplier
```

Rows with insufficient baseline sample support are classified as:

```text
low_confidence
```

rather than being overclaimed as real anomalies.

## Robustness notes

This phase intentionally keeps the initial implementation dashboard-side so it can work immediately with the existing `agg_zone_30s` table. For large-scale production usage, use the included SQL template:

```text
sql/phase7_3_baseline_anomaly_detection.sql
```

to promote anomaly windows into ClickHouse rollups.
