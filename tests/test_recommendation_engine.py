from aegis_common.recommendation_engine import top_issue

def test_ai_pathfinding_pressure_wins():
    metrics = {
        "active_players": 120, "p95_frame": 72, "p99_frame": 110, "cpu_p95": 94, "memory_p95": 5200,
        "packet_loss_p95": 1, "packet_out_p95": 1000, "replicated_p95": 4000, "aoe_events": 20,
        "physics_events": 40, "ai_agents_active_p95": 280, "ai_pathfinding_requests": 900,
        "matchmaking_events": 0, "matchmaking_queue_p95": 0, "desync_events": 5, "rubberband_events": 8,
        "top_ability_id": "", "top_event_type": "ai_pathfinding_request",
    }
    assert top_issue(metrics)["issue_type"] == "ai_pathfinding_pressure"
