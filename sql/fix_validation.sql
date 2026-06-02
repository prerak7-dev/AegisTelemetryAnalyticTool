/*
Fix Validation Export

Reads experiment fields from raw_events.raw_json.
{event_time_filter}
{active_filter}
{limit}
*/

SELECT
  JSONExtractString(raw_json, 'experiment_id') AS experiment_id,
  JSONExtractString(raw_json, 'experiment_variant') AS experiment_variant,
  JSONExtractString(raw_json, 'change_id') AS change_id,
  JSONExtractString(raw_json, 'validation_plan_id') AS validation_plan_id,
  source_profile,
  region,
  build_version,
  map_id,
  zone_id,
  count() AS samples,
  countDistinct(server_id) AS servers,
  quantile(0.95)(server_frame_ms) AS p95_server_frame_ms,
  quantile(0.95)(packet_out_kbps) AS p95_packet_out_kbps,
  quantile(0.95)(packet_loss_percent) AS p95_packet_loss,
  quantile(0.95)(replicated_objects) AS p95_replicated_objects,
  avg(physics_events) AS avg_physics_events,
  avg(desync_count) AS avg_desync_events,
  avg(rubberband_count) AS avg_rubberband_events,
  quantile(0.95)(memory_mb) AS p95_memory_mb
FROM raw_events
WHERE {event_time_filter}
  AND {active_filter}
  AND JSONExtractString(raw_json, 'experiment_id') != ''
GROUP BY
  experiment_id,
  experiment_variant,
  change_id,
  validation_plan_id,
  source_profile,
  region,
  build_version,
  map_id,
  zone_id
ORDER BY experiment_id DESC, samples DESC
LIMIT {limit}
