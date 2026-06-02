/*
Rule Quality Review

{incident_time_filter}
{active_filter}
{limit}
*/

SELECT
  likely_driver,
  severity,
  source_profile,
  count() AS incidents,
  avg(confidence) AS avg_confidence,
  min(detected_at) AS first_detected,
  max(detected_at) AS latest_detected,
  countDistinct(server_id) AS affected_servers,
  countDistinct(map_id) AS affected_maps,
  countDistinct(zone_id) AS affected_zones,
  anyLast(recommended_action) AS latest_recommended_action
FROM incidents
WHERE {incident_time_filter}
  AND {active_filter}
GROUP BY likely_driver, severity, source_profile
ORDER BY
  multiIf(severity = 'critical', 1, severity = 'warning', 2, 3),
  incidents DESC,
  avg_confidence DESC
LIMIT {limit}
