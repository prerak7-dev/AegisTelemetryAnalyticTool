# Phase 8 — Build Regression Analysis

This phase adds build-to-build performance comparison.

## New workspace

```text
Incidents > Build Regression
```

## Questions it answers

```text
Did server frame time regress?
Did packet-out increase?
Did physics events increase?
Did memory pressure increase?
Did desync/rubberbanding increase?
Which map/zone regressed most?
Which source profile reported the regression?
Is the release candidate a pass, watch, low confidence, or block?
```

## Configurable metric catalog

Build-regression metrics are configured in:

```text
config/dashboard_performance.json
```

under:

```text
build_regression.metric_catalog
```

Each metric supports:

```text
label
aggregation function
direction
unit
weight
```

This avoids hardcoding release-readiness logic in the view layer.

## New simulator options

The traffic generator now supports:

```bash
python simulator/generate_traffic.py \
  --scenario normal_load \
  --build-version 0.2.0 \
  --build-regression-mode none

python simulator/generate_traffic.py \
  --scenario normal_load \
  --build-version 0.2.1 \
  --build-regression-mode candidate_regressed
```

Supported build regression modes:

```text
none
candidate_regressed
candidate_improved
```

## Workspace outputs

```text
Release readiness summary
Comparable contexts
Critical/warning counts
Weighted regression score
Metric regression ranking
Context regression table
Metric regression table
Timeline for the most regressed context
Build inventory
Configuration evidence
```

## Production template

Optional SQL template:

```text
sql/phase8_build_regression_analysis.sql
```

The dashboard works without this table, but production-scale deployments can populate it for historical release-readiness records.
