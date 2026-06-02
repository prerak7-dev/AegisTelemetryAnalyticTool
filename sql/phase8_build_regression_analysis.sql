/*
Phase 8 — Build Regression Analysis

Optional ClickHouse table for precomputed build-to-build comparisons.

The dashboard workspace works directly from `agg_zone_30s`, but at larger
production scale this table can be populated by a scheduled job or materialized
pipeline.
*/

CREATE TABLE IF NOT EXISTS build_regression_results
(
    evaluated_at DateTime DEFAULT now(),

    previous_build LowCardinality(String),
    current_build LowCardinality(String),
    comparison_scope LowCardinality(String),

    source_profile LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),

    metric LowCardinality(String),
    metric_label String,
    previous_value Float64,
    current_value Float64,
    pct_change Float64,
    regression_pct Float64,
    unit LowCardinality(String),

    regression_score Float64,
    regression_severity LowCardinality(String),
    comparison_confidence Float64,
    baseline_windows UInt64,
    current_windows UInt64,

    evidence_json String
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(evaluated_at)
ORDER BY (evaluated_at, current_build, previous_build, source_profile, region, map_id, zone_id, regression_score);

/*
Production notes:

1. Keep metric definitions in config/dashboard_performance.json.
2. Generate this table from the same config so dashboard scoring and backend scoring do not drift.
3. Use this table for release-readiness reports and historical regression tracking.
*/
