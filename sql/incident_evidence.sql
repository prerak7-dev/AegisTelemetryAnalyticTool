/*
Incident Evidence Export

{incident_time_filter}
{active_filter}
{limit}
*/

SELECT
  detected_at,
  incident_id,
  severity,
  source_profile,
  region,
  server_id,
  map_id,
  zone_id,
  build_version,
  symptom,
  likely_driver,
  confidence,
  player_impact,
  recommended_action,
  evidence_json
FROM incidents
WHERE {incident_time_filter}
  AND {active_filter}
ORDER BY
  multiIf(severity = 'critical', 1, severity = 'warning', 2, 3),
  detected_at DESC
LIMIT {limit}
