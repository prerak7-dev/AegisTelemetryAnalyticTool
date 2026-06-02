# Core Tables

## raw_events

Raw event-level telemetry.

Common uses:

- experiment/fix validation
- source-level debugging
- raw data exports
- validating simulator/collector flow

## agg_zone_30s

Main 30-second aggregate table by gameplay context.

Common dimensions:

- source_profile
- region
- server_id
- map_id
- zone_id
- build_version
- window_start

Common metrics:

- server_frame_ms_p95
- server_frame_ms_p99
- packet_loss_p95
- packet_out_kbps_p95
- replicated_objects_p95
- active_players
- aoe_events
- physics_events
- memory_mb_p95
- desync_events
- rubberband_events
- hot_zone_risk_score

## data_quality_failures

Validation failures and schema issues.

Use this to investigate:

- invalid source telemetry
- missing fields
- malformed values
- schema drift

## incidents

Detected incidents and recommendations.

Common fields:

- detected_at
- incident_id
- severity
- likely_driver
- confidence
- player_impact
- recommended_action
- evidence_json

## Local workflow stores

Phase 10 and Phase 11 use local JSON stores for demo-friendly persistence:

```text
data/incident_workflow.json
data/demo_scenario_history.json
```

These can later be replaced or mirrored by production database tables.
