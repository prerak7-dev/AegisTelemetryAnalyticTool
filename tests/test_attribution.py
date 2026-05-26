from aegis_common.attribution import score_drivers, top_recommendation
from aegis_common.stats import risk_score

def test_aoe_replication_driver_wins():
    metrics = {
        "active_players": 180,
        "p95_frame": 75,
        "p99_frame": 110,
        "cpu_p95": 92,
        "packet_loss_p95": 4,
        "replicated_p95": 22000,
        "aoe_events": 900,
        "physics_events": 120,
        "desync_events": 20,
        "rubberband_events": 40,
    }
    assert top_recommendation(metrics)["driver"] == "aoe_event_density_and_replication"

def test_risk_score_high_under_meltdown():
    score = risk_score(
        players=220,
        server_frame_p95=80,
        cpu_p95=95,
        packet_loss_p95=6,
        desync_events=30,
        rubberband_events=60,
        aoe_events=900,
        replicated_objects_p95=24000,
    )
    assert score >= 80
