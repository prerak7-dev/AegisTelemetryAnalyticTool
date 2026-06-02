/*
Phase 9 — Experimentation and Fix Validation

Optional production table for storing validation decisions.

The dashboard workspace works directly from `raw_events` using experiment fields
stored in raw_json. At larger scale, scheduled jobs can write stable validation
results into this table.
*/

CREATE TABLE IF NOT EXISTS fix_validation_results
(
    evaluated_at DateTime DEFAULT now(),

    experiment_id String,
    control_variant LowCardinality(String),
    treatment_variant LowCardinality(String),
    change_id String,
    validation_plan_id String,

    source_profile LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),
    build_version LowCardinality(String),

    decision LowCardinality(String),
    metric LowCardinality(String),
    metric_label String,
    metric_role LowCardinality(String),

    control_value Float64,
    treatment_value Float64,
    raw_pct_change Float64,
    improvement_pct Float64,

    t_stat Float64,
    directional_t_stat Float64,
    statistically_meaningful UInt8,
    metric_status LowCardinality(String),

    validation_confidence Float64,
    control_samples UInt64,
    treatment_samples UInt64,

    evidence_json String
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(evaluated_at)
ORDER BY (evaluated_at, experiment_id, decision, metric_role, metric_status);

/*
Production note:

Keep metric catalog, decision thresholds, and field names in
config/dashboard_performance.json. If this table is populated by a backend job,
validate that backend formulas and dashboard formulas read from the same config.
*/
