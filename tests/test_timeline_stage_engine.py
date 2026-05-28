import json
from pathlib import Path

import pandas as pd

from aegis_common.timeline_stage_engine import (
    add_derived_timeline_metrics,
    build_timeline_sequence,
    load_timeline_stage_profiles,
)

def test_default_timeline_stage_profile_has_builtin_rule_sequences():
    profiles = load_timeline_stage_profiles("timeline_stages")
    profile = profiles["default_timeline_stages"]
    rule_ids = set(profile["rule_sequences"].keys())

    expected = {
        "aoe_replication_overload",
        "physics_simulation_spike",
        "network_packet_pressure",
        "local_density_tick_budget",
        "ai_pathfinding_pressure",
        "memory_pressure",
        "matchmaking_or_capacity_surge",
        "desync_hit_registration_risk",
        "unclassified_performance_pressure",
    }

    assert expected.issubset(rule_ids)

def test_timeline_sequence_builds_for_ai_pathfinding():
    profiles = load_timeline_stage_profiles("timeline_stages")
    profile = profiles["default_timeline_stages"]

    timeline = pd.DataFrame([
        {
            "window_start": "2026-01-01T00:00:00Z",
            "active_players": 40,
            "ai_pathfinding_requests": 10,
            "ai_agents_active_p95": 20,
            "server_frame_ms_p95": 24,
            "server_frame_ms_p99": 40,
            "hot_zone_risk_score": 10,
            "desync_events": 0,
            "rubberband_events": 0,
            "packet_loss_p95": 0,
            "aoe_events": 0,
            "physics_events": 0,
            "replicated_objects_p95": 0,
            "packet_out_kbps_p95": 0,
            "memory_mb_p95": 3000,
            "matchmaking_queue_p95": 0,
            "cpu_p95": 30,
            "source_profile": "test",
            "zone_id": "zone",
        },
        {
            "window_start": "2026-01-01T00:00:30Z",
            "active_players": 150,
            "ai_pathfinding_requests": 700,
            "ai_agents_active_p95": 250,
            "server_frame_ms_p95": 70,
            "server_frame_ms_p99": 95,
            "hot_zone_risk_score": 84,
            "desync_events": 4,
            "rubberband_events": 8,
            "packet_loss_p95": 1,
            "aoe_events": 10,
            "physics_events": 20,
            "replicated_objects_p95": 5000,
            "packet_out_kbps_p95": 1500,
            "memory_mb_p95": 4000,
            "matchmaking_queue_p95": 0,
            "cpu_p95": 94,
            "source_profile": "test",
            "zone_id": "zone",
        },
    ])

    incident = {
        "detected_at": "2026-01-01T00:00:30Z",
        "severity": "warning",
        "likely_driver": "ai_pathfinding_pressure",
        "server_id": "server",
        "zone_id": "zone",
        "recommended_action": "Throttle AI path recalculation."
    }
    evidence = {
        "window_start": "2026-01-01T00:00:30Z"
    }

    sequence = build_timeline_sequence(timeline, incident, evidence, profile)
    assert "AI pathfinding pressure spikes" in set(sequence["stage"].tolist())
    assert sequence[sequence["stage"] == "AI pathfinding pressure spikes"].iloc[0]["matched"]
