from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class DriverScore:
    driver: str
    score: float
    confidence: float
    evidence: str
    recommendation: str

def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))

def score_drivers(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Rank likely performance drivers for a zone/window.

    These are not causal claims. They are triage scores that tell analysts and
    engineers where to investigate first.
    """
    active_players = float(metrics.get("active_players", 0) or 0)
    p95_frame = float(metrics.get("p95_frame", 0) or 0)
    packet_loss_p95 = float(metrics.get("packet_loss_p95", 0) or 0)
    cpu_p95 = float(metrics.get("cpu_p95", 0) or 0)
    replicated_p95 = float(metrics.get("replicated_p95", 0) or 0)
    aoe_events = float(metrics.get("aoe_events", 0) or 0)
    physics_events = float(metrics.get("physics_events", 0) or 0)
    desync_events = float(metrics.get("desync_events", 0) or 0)
    rubberband_events = float(metrics.get("rubberband_events", 0) or 0)

    crowd_score = clamp((active_players - 70) / 130)
    frame_score = clamp((p95_frame - 35) / 45)
    cpu_score = clamp((cpu_p95 - 65) / 30)
    network_score = clamp(packet_loss_p95 / 8)
    replication_score = clamp((replicated_p95 - 6000) / 14000)
    aoe_score = clamp(aoe_events / 700)
    physics_score = clamp(physics_events / 400)
    player_impact_score = clamp((desync_events + rubberband_events) / 100)

    scores = [
        DriverScore(
            driver="aoe_event_density_and_replication",
            score=0.35 * aoe_score + 0.30 * replication_score + 0.20 * frame_score + 0.15 * crowd_score,
            confidence=0.55 + 0.35 * min(aoe_score, replication_score),
            evidence=f"AoE events={int(aoe_events)}, replicated_objects_p95={replicated_p95:.0f}, players={int(active_players)}, p95_frame={p95_frame:.1f}ms",
            recommendation="Reduce temporary AoE object replication radius/update frequency in high-density zones and validate hit-registration/desync guardrails.",
        ),
        DriverScore(
            driver="physics_event_spike",
            score=0.45 * physics_score + 0.25 * cpu_score + 0.20 * frame_score + 0.10 * crowd_score,
            confidence=0.52 + 0.38 * min(physics_score, cpu_score),
            evidence=f"Physics events={int(physics_events)}, cpu_p95={cpu_p95:.1f}%, p95_frame={p95_frame:.1f}ms",
            recommendation="Profile physics-heavy gameplay events and cap non-critical rigid-body simulation during high-density combat windows.",
        ),
        DriverScore(
            driver="zone_player_density",
            score=0.45 * crowd_score + 0.25 * frame_score + 0.15 * cpu_score + 0.15 * player_impact_score,
            confidence=0.50 + 0.35 * min(crowd_score, frame_score),
            evidence=f"Active players={int(active_players)}, p95_frame={p95_frame:.1f}ms, player impact events={int(desync_events + rubberband_events)}",
            recommendation="Evaluate shard splitting, encounter spacing, or non-critical simulation-budget reduction when local density crosses threshold.",
        ),
        DriverScore(
            driver="network_replication_pressure",
            score=0.35 * network_score + 0.30 * replication_score + 0.20 * player_impact_score + 0.15 * frame_score,
            confidence=0.50 + 0.35 * min(network_score, replication_score),
            evidence=f"packet_loss_p95={packet_loss_p95:.1f}%, replicated_objects_p95={replicated_p95:.0f}, player impact events={int(desync_events + rubberband_events)}",
            recommendation="Reduce replication of cosmetic/short-lived objects and inspect packet-out rates in affected regions.",
        ),
    ]

    ranked = sorted(scores, key=lambda item: item.score, reverse=True)
    return [
        {
            "driver": item.driver,
            "score": round(float(item.score), 3),
            "confidence": round(min(float(item.confidence), 0.95), 3),
            "evidence": item.evidence,
            "recommendation": item.recommendation,
        }
        for item in ranked
    ]

def top_recommendation(metrics: dict[str, Any]) -> dict[str, Any]:
    ranked = score_drivers(metrics)
    return ranked[0] if ranked else {
        "driver": "unknown",
        "score": 0.0,
        "confidence": 0.5,
        "evidence": "Insufficient signals.",
        "recommendation": "Collect more telemetry or inspect raw event timeline.",
    }
