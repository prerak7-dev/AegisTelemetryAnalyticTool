from pathlib import Path

from aegis_common.schema_mapper import load_profiles, normalize_with_profile

def test_generic_profile_maps_to_canonical():
    profiles = load_profiles(Path("source_schemas"))
    profile = profiles["generic_live_service"]

    raw = {
        "id": "evt-1",
        "ts": "2026-05-27T18:00:00Z",
        "typeGroup": "combat",
        "name": "combat.aoe_cast",
        "severityPriority": 1,
        "regionName": "EU-West",
        "shardId": "eu-west-001",
        "activityId": "match-1",
        "world": {"map": "storm_front"},
        "location": {"zone": "northern_ridge"},
        "clientBuild": "1.2.3",
        "population": {"serverPlayers": 200, "nearbyPlayers": 150},
        "gameplay": {"ability": "aoe_fire_burst"},
        "perf": {"cpuPct": 90.5, "memMb": 5000, "frameMs": 72.0},
        "net": {"packetLossPct": 3.2, "outKbps": 8000, "replicatedObjects": 17000},
        "impact": {"desyncs": 2, "rubberbands": 5},
        "physics": {"events": 120}
    }

    mapped = normalize_with_profile(raw, profile)

    assert mapped["event_id"] == "evt-1"
    assert mapped["event_type"] == "aoe_ability_cast"
    assert mapped["category"] == "gameplay"
    assert mapped["server_id"] == "eu-west-001"
    assert mapped["zone_id"] == "northern_ridge"
    assert mapped["server_frame_ms"] == 72.0
    assert mapped["source_profile"] == "generic_live_service"
    assert mapped["source_event_raw"]["id"] == "evt-1"
