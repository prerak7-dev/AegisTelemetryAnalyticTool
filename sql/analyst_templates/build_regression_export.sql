/*
Build Regression Export

Compares configured builds when supplied by dashboard; otherwise summarizes by build.
{time_filter}
{active_filter}
{limit}
*/

SELECT
  build_version,
  source_profile,
  region,
  map_id,
  zone_id,
  count() AS aggregate_windows,
  countDistinct(server_id) AS servers,
  quantile(0.95)(server_frame_ms_p95) AS p95_server_frame_ms,
  quantile(0.95)(packet_out_kbps_p95) AS p95_packet_out_kbps,
  quantile(0.95)(packet_loss_p95) AS p95_packet_loss,
  quantile(0.95)(replicated_objects_p95) AS p95_replicated_objects,
  avg(physics_events) AS avg_physics_events,
  quantile(0.95)(memory_mb_p95) AS p95_memory_mb,
  avg(desync_events + rubberband_events) AS avg_player_impact,
  max(hot_zone_risk_score) AS max_hot_zone_risk
FROM agg_zone_30s
WHERE {time_filter}
  AND {active_filter}
GROUP BY build_version, source_profile, region, map_id, zone_id
ORDER BY build_version DESC, max_hot_zone_risk DESC
LIMIT {limit}
