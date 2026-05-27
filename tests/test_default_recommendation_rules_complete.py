from pathlib import Path
import json

def test_default_recommendation_rules_include_builtin_issue_set():
    path = Path("recommendation_rules/default_recommendation_rules.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    rule_ids = {rule["id"] for rule in payload["rules"]}

    expected = {
        "aoe_replication_overload",
        "physics_simulation_spike",
        "network_packet_pressure",
        "local_density_tick_budget",
        "ai_pathfinding_pressure",
        "memory_pressure",
        "matchmaking_or_capacity_surge",
        "desync_hit_registration_risk",
    }

    assert expected.issubset(rule_ids)
