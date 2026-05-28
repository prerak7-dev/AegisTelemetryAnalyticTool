# Phase 6.1 — Configurable Timeline Stages

Phase 6.1 removes hardcoded root-cause sequence stages from the Incident Timeline.

Timeline stages now live in JSON profiles:

```text
timeline_stages/
  default_timeline_stages.json
  custom_timeline_stages_example.json
```

## What developers can configure

Developers can add/edit:

- stage ID
- stage label
- stage mode
- condition
- detail fields
- fallback text
- default sequence
- rule-specific sequences

## Built-in stage coverage

The default profile includes out-of-the-box stage sequences for every built-in recommendation rule:

```text
aoe_replication_overload
physics_simulation_spike
network_packet_pressure
local_density_tick_budget
ai_pathfinding_pressure
memory_pressure
matchmaking_or_capacity_surge
desync_hit_registration_risk
unclassified_performance_pressure
```

## Stage modes

```text
incident_start
recommendation
first_match
peak_match
```

## Example stage

```json
{
  "id": "server_frame_degrades",
  "label": "Server frame time degrades",
  "mode": "first_match",
  "condition": {
    "any": [
      { "metric": "server_frame_ms_p95", "op": ">=", "value": 50 },
      { "metric": "hot_zone_risk_score", "op": ">=", "value": 70 }
    ]
  },
  "detail_fields": [
    "server_frame_ms_p95",
    "server_frame_ms_p99",
    "cpu_p95"
  ],
  "fallback_detail": "Frame-time degradation was not observed."
}
```

## Dashboard

The Incident Timeline now has a `Timeline stage profile` selector.

A new `Timeline Stages` workspace shows available profiles and a template for adding custom stages.
