/*
Source Profile Comparison

{time_filter}
{quality_time_filter}
{limit}
*/

WITH aggregate_summary AS
(
  SELECT
    source_profile,
    count() AS aggregate_windows,
    countDistinct(server_id) AS servers,
    countDistinct(map_id) AS maps,
    countDistinct(zone_id) AS zones,
    max(window_start) AS latest_window,
    quantile(0.95)(server_frame_ms_p95) AS p95_frame_ms,
    quantile(0.95)(packet_loss_p95) AS p95_packet_loss,
    quantile(0.95)(packet_out_kbps_p95) AS p95_packet_out,
    max(hot_zone_risk_score) AS max_hot_zone_risk,
    sum(desync_events + rubberband_events) AS player_impact_events
  FROM agg_zone_30s
  WHERE {time_filter}
  GROUP BY source_profile
),
quality_summary AS
(
  SELECT
    source_profile,
    count() AS validation_failures
  FROM data_quality_failures
  WHERE {quality_time_filter}
  GROUP BY source_profile
)
SELECT
  a.source_profile,
  a.aggregate_windows,
  a.servers,
  a.maps,
  a.zones,
  a.latest_window,
  a.p95_frame_ms,
  a.p95_packet_loss,
  a.p95_packet_out,
  a.max_hot_zone_risk,
  a.player_impact_events,
  ifNull(q.validation_failures, 0) AS validation_failures
FROM aggregate_summary AS a
LEFT JOIN quality_summary AS q USING source_profile
ORDER BY a.max_hot_zone_risk DESC, validation_failures DESC
LIMIT {limit}
