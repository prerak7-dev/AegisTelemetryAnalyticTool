/*
Phase 7.3 — Baselines, Anomaly Detection, and Dynamic Thresholds

Optional ClickHouse templates for promoting live baseline calculations into
precomputed tables. These are not automatically applied by Docker Compose.

The dashboard workspace works without these tables by calculating baselines from
the configured aggregate table. At larger scale, promote these concepts into
rollups/materialized views.
*/

CREATE TABLE IF NOT EXISTS baseline_anomaly_windows
(
    window_start DateTime,
    source_profile LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),

    current_p95_frame Float64,
    baseline_p95_frame Float64,
    frame_ratio Float64,
    frame_z Float64,

    current_packet_loss Float64,
    baseline_packet_loss Float64,
    packet_loss_ratio Float64,

    current_aoe_events Float64,
    baseline_aoe_events Float64,
    aoe_ratio Float64,

    current_memory Float64,
    baseline_memory Float64,
    memory_ratio Float64,

    current_physics_events Float64,
    baseline_physics_events Float64,
    physics_ratio Float64,

    current_replication Float64,
    baseline_replication Float64,
    replication_ratio Float64,

    current_player_impact Float64,
    baseline_player_impact Float64,
    player_impact_ratio Float64,

    dynamic_warning_frame_ms Float64,
    dynamic_critical_frame_ms Float64,

    anomaly_score Float64,
    anomaly_severity LowCardinality(String),
    dominant_anomaly_metric LowCardinality(String),
    baseline_confidence Float64,
    baseline_rows UInt64,
    current_rows UInt64,

    updated_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(window_start)
ORDER BY (source_profile, region, server_id, map_id, zone_id, window_start, anomaly_score);

/*
Production note:

Keep thresholds, weights, sample requirements, and metric definitions in
config/dashboard_performance.json. If you materialize this table, generate or
validate the SQL formulas from the same config so dashboard scoring and backend
scoring cannot drift.
*/
