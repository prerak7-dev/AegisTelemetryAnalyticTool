/*
Phase 7.2 — Query Architecture Hardening SQL Templates

These scripts are optional templates. They are not automatically applied by Docker Compose.

Use these once you are ready to move pressure scoring and leaderboard queries
out of Streamlit/Pandas and into ClickHouse rollups.

Before applying:
- Confirm your source aggregate table name.
- Confirm table names in config/dashboard_performance.json.
- Adjust budgets to match your game/server architecture.
- Prefer explicit migrations in your deployment pipeline.
*/

-- --------------------------------------------------------------------
-- 1. Dashboard-ready pressure rollup table.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agg_pressure_30s
(
    window_start DateTime,
    source_profile LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),

    simulation_pressure Float64,
    network_pressure Float64,
    replication_pressure Float64,
    physics_pressure Float64,
    memory_pressure Float64,
    ai_pressure Float64,
    matchmaking_pressure Float64,
    player_impact_pressure Float64,
    telemetry_quality_pressure Float64,

    max_pressure_score Float64,
    dominant_pressure_type LowCardinality(String),

    server_frame_ms_p95 Float64,
    server_frame_ms_p99 Float64,
    packet_loss_p95 Float64,
    packet_out_kbps_p95 Float64,
    replicated_objects_p95 Float64,
    physics_events UInt64,
    memory_mb_p95 Float64,
    ai_pathfinding_requests UInt64,
    matchmaking_queue_p95 Float64,
    desync_events UInt64,
    rubberband_events UInt64,

    updated_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(window_start)
ORDER BY (source_profile, region, server_id, window_start, map_id, zone_id);

-- --------------------------------------------------------------------
-- 2. Top pressure zone leaderboard.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agg_top_pressure_zones_1m
(
    bucket_start DateTime,
    source_profile LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),

    dominant_pressure_type LowCardinality(String),
    max_pressure_score Float64,
    simulation_pressure Float64,
    network_pressure Float64,
    replication_pressure Float64,
    physics_pressure Float64,
    memory_pressure Float64,
    ai_pressure Float64,
    matchmaking_pressure Float64,
    player_impact_pressure Float64,

    server_frame_ms_p95 Float64,
    packet_loss_p95 Float64,
    replicated_objects_p95 Float64,
    physics_events UInt64,
    desync_events UInt64,
    rubberband_events UInt64,

    updated_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(bucket_start)
ORDER BY (source_profile, region, bucket_start, max_pressure_score, server_id, map_id, zone_id);

-- --------------------------------------------------------------------
-- 3. Context baseline table for the next anomaly-detection phase.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agg_context_baseline_1h
(
    baseline_bucket DateTime,
    source_profile LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),
    build_version LowCardinality(String) DEFAULT 'unknown',
    platform LowCardinality(String) DEFAULT 'unknown',
    live_event_status LowCardinality(String) DEFAULT 'normal',

    baseline_p95_frame Float64,
    baseline_packet_loss Float64,
    baseline_aoe_events Float64,
    baseline_memory Float64,
    baseline_physics_events Float64,
    baseline_replication Float64,

    stddev_p95_frame Float64,
    stddev_packet_loss Float64,
    sample_count UInt64,

    updated_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(baseline_bucket)
ORDER BY (source_profile, region, server_id, map_id, zone_id, baseline_bucket);

-- --------------------------------------------------------------------
-- Notes
-- --------------------------------------------------------------------
-- 1. Materialized view formulas should be generated from the same thresholds
--    used in config/dashboard_performance.json.
--
-- 2. Keep config as the source of truth. Do not fork pressure budgets in SQL
--    without also updating configuration and documentation.
--
-- 3. For production, add migration tests that validate:
--    - table exists
--    - expected columns exist
--    - dashboard feature flags match available rollup tables
--
-- 4. Once rollups are populated, set:
--      "prefer_pressure_rollup_table": true
--      "prefer_top_pressure_zones_table": true
--    in config/dashboard_performance.json
*/
