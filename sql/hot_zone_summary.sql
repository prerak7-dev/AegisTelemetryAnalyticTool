/*
Hot Zone Summary

Placeholders supplied by Analyst Toolkit:
{time_filter}
{active_filter}
{limit}
*/

SELECT
  source_profile,
  region,
  server_id,
  map_id,
  zone_id,
  count() AS aggregate_windows,
  min(window_start) AS first_window,
  max(window_start) AS latest_window,
  max(active_players) AS peak_active_players,
  quantile(0.95)(server_frame_ms_p95) AS p95_server_frame_ms,
  quantile(0.99)(server_frame_ms_p99) AS p99_server_frame_ms,
  quantile(0.95)(packet_loss_p95) AS p95_packet_loss,
  quantile(0.95)(packet_out_kbps_p95) AS p95_packet_out_kbps,
  quantile(0.95)(replicated_objects_p95) AS p95_replicated_objects,
  sum(aoe_events) AS aoe_events,
  sum(physics_events) AS physics_events,
  quantile(0.95)(memory_mb_p95) AS p95_memory_mb,
  sum(desync_events) AS desync_events,
  sum(rubberband_events) AS rubberband_events,
  max(hot_zone_risk_score) AS max_hot_zone_risk
FROM agg_zone_30s
WHERE {time_filter}
  AND {active_filter}
GROUP BY source_profile, region, server_id, map_id, zone_id
ORDER BY max_hot_zone_risk DESC, p95_server_frame_ms DESC
LIMIT {limit}
