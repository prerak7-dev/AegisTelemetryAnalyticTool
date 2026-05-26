CREATE DATABASE IF NOT EXISTS aegis_telemetry;

CREATE TABLE IF NOT EXISTS aegis_telemetry.raw_events
(
    event_time DateTime64(3, 'UTC'),
    ingest_time DateTime64(3, 'UTC'),
    event_id String,
    category LowCardinality(String),
    event_type LowCardinality(String),
    priority UInt8,
    region LowCardinality(String),
    server_id String,
    match_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),
    build_version LowCardinality(String),
    player_count UInt32,
    players_nearby UInt32,
    ability_id LowCardinality(String),
    cpu_percent Float32,
    memory_mb Float32,
    server_frame_ms Float32,
    packet_loss_percent Float32,
    packet_out_kbps Float32,
    desync_count UInt32,
    rubberband_count UInt32,
    replicated_objects UInt32,
    physics_events UInt32,
    raw_json String
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, region, server_id, match_id, zone_id, event_type);

CREATE TABLE IF NOT EXISTS aegis_telemetry.agg_zone_30s
(
    window_start DateTime64(3, 'UTC'),
    window_end DateTime64(3, 'UTC'),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),
    build_version LowCardinality(String),
    events UInt64,
    active_players UInt32,
    ability_casts UInt64,
    aoe_events UInt64,
    physics_events UInt64,
    replicated_objects_p95 Float32,
    cpu_p95 Float32,
    server_frame_ms_avg Float32,
    server_frame_ms_p95 Float32,
    server_frame_ms_p99 Float32,
    packet_loss_p95 Float32,
    desync_events UInt64,
    rubberband_events UInt64,
    hot_zone_risk_score Float32
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(window_start)
ORDER BY (window_start, region, server_id, map_id, zone_id);

CREATE TABLE IF NOT EXISTS aegis_telemetry.incidents
(
    detected_at DateTime64(3, 'UTC'),
    incident_id String,
    severity LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    map_id LowCardinality(String),
    zone_id LowCardinality(String),
    build_version LowCardinality(String),
    symptom String,
    likely_driver String,
    confidence Float32,
    player_impact String,
    recommended_action String,
    evidence_json String
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(detected_at)
ORDER BY (detected_at, severity, region, server_id, zone_id);


CREATE TABLE IF NOT EXISTS aegis_telemetry.data_quality_failures
(
    failed_at DateTime64(3, 'UTC'),
    event_id String,
    error String,
    category LowCardinality(String),
    event_type LowCardinality(String),
    region LowCardinality(String),
    server_id String,
    raw_json String
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(failed_at)
ORDER BY (failed_at, region, server_id, event_type);
