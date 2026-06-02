-- Phase 13.23.2 Live Snapshot Tables — Aggregation-Safe Version
--
-- IMPORTANT:
-- These default local-development snapshot views intentionally avoid aggregate
-- functions. They are pass-through compatibility views over agg_zone_30s.
--
-- Why:
-- The dashboard still performs aggregate queries such as dashboard-level aggregate functions over the configured live snapshot table. If the snapshot view
-- itself also contains aggregate functions like aggregate state functions, ClickHouse can reject
-- later dashboard queries with ILLEGAL_AGGREGATION because that becomes
-- aggregate-over-aggregate.
--
-- Production deployments can replace these pass-through views with real
-- materialized tables, but the dashboard query layer must then read already
-- final scalar columns without applying another aggregate layer.

DROP VIEW IF EXISTS aegis_telemetry.live_pressure_summary_1m;

CREATE VIEW aegis_telemetry.live_pressure_summary_1m AS
SELECT
    window_start,
    window_end,
    source_profile,
    region,
    server_id,
    map_id,
    zone_id,
    build_version,
    events,
    active_players,
    ability_casts,
    aoe_events,
    physics_events,
    replicated_objects_p95,
    cpu_p95,
    server_frame_ms_avg,
    server_frame_ms_p95,
    server_frame_ms_p99,
    packet_loss_p95,
    packet_out_kbps_p95,
    memory_mb_p95,
    ai_agents_active_p95,
    ai_pathfinding_requests,
    matchmaking_events,
    matchmaking_queue_p95,
    top_ability_id,
    top_event_type,
    desync_events,
    rubberband_events,
    hot_zone_risk_score
FROM aegis_telemetry.agg_zone_30s;

DROP VIEW IF EXISTS aegis_telemetry.live_hot_zones_30s;

CREATE VIEW aegis_telemetry.live_hot_zones_30s AS
SELECT
    window_start,
    window_end,
    source_profile,
    region,
    server_id,
    map_id,
    zone_id,
    build_version,
    events,
    active_players,
    ability_casts,
    aoe_events,
    physics_events,
    replicated_objects_p95,
    cpu_p95,
    server_frame_ms_avg,
    server_frame_ms_p95,
    server_frame_ms_p99,
    packet_loss_p95,
    packet_out_kbps_p95,
    memory_mb_p95,
    ai_agents_active_p95,
    ai_pathfinding_requests,
    matchmaking_events,
    matchmaking_queue_p95,
    top_ability_id,
    top_event_type,
    desync_events,
    rubberband_events,
    hot_zone_risk_score
FROM aegis_telemetry.agg_zone_30s;

DROP VIEW IF EXISTS aegis_telemetry.live_regional_pressure_1m;

CREATE VIEW aegis_telemetry.live_regional_pressure_1m AS
SELECT
    window_start,
    window_end,
    source_profile,
    region,
    server_id,
    map_id,
    zone_id,
    build_version,
    events,
    active_players,
    ability_casts,
    aoe_events,
    physics_events,
    replicated_objects_p95,
    cpu_p95,
    server_frame_ms_avg,
    server_frame_ms_p95,
    server_frame_ms_p99,
    packet_loss_p95,
    packet_out_kbps_p95,
    memory_mb_p95,
    ai_agents_active_p95,
    ai_pathfinding_requests,
    matchmaking_events,
    matchmaking_queue_p95,
    top_ability_id,
    top_event_type,
    desync_events,
    rubberband_events,
    hot_zone_risk_score
FROM aegis_telemetry.agg_zone_30s;

-- These lightweight status views use simple aggregates only and are not used as
-- input to another aggregate query by the dashboard. They are safe optional
-- convenience views for status panels.

DROP VIEW IF EXISTS aegis_telemetry.live_fleet_health_30s;

CREATE VIEW aegis_telemetry.live_fleet_health_30s AS
SELECT
    latest_window,
    dateDiff('second', latest_window, now()) AS staleness_seconds,
    aggregate_rows,
    observed_source_profiles,
    observed_servers,
    observed_regions,
    max_risk,
    max_p95_frame,
    player_impact_events
FROM
(
    SELECT
        max(window_start) AS latest_window,
        count() AS aggregate_rows,
        countDistinct(source_profile) AS observed_source_profiles,
        countDistinct(server_id) AS observed_servers,
        countDistinct(region) AS observed_regions,
        max(hot_zone_risk_score) AS max_risk,
        max(server_frame_ms_p95) AS max_p95_frame,
        sum(rubberband_events + desync_events) AS player_impact_events
    FROM aegis_telemetry.agg_zone_30s
);

DROP VIEW IF EXISTS aegis_telemetry.latest_incident_summary;

CREATE VIEW aegis_telemetry.latest_incident_summary AS
SELECT
    max(detected_at) AS latest_incident_at,
    count() AS incident_count,
    countIf(severity = 'critical') AS critical_count,
    countIf(severity = 'warning') AS warning_count,
    countDistinct(server_id) AS impacted_servers,
    max(likely_driver) AS latest_driver,
    max(recommended_action) AS latest_recommendation
FROM aegis_telemetry.incidents;

DROP VIEW IF EXISTS aegis_telemetry.latest_demo_pipeline_status;

CREATE VIEW aegis_telemetry.latest_demo_pipeline_status AS
SELECT
    latest_window,
    dateDiff('second', latest_window, now()) AS staleness_seconds,
    recent_rows,
    source_profiles,
    servers,
    max_risk
FROM
(
    SELECT
        max(window_start) AS latest_window,
        count() AS recent_rows,
        countDistinct(source_profile) AS source_profiles,
        countDistinct(server_id) AS servers,
        max(hot_zone_risk_score) AS max_risk
    FROM aegis_telemetry.agg_zone_30s
    WHERE window_start >= now() - INTERVAL 15 MINUTE
);
