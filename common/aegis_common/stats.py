from __future__ import annotations

def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    sorted_values = sorted(float(v) for v in values)
    idx = (len(sorted_values) - 1) * q
    lower = int(idx)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = idx - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

def risk_score(
    players: int,
    server_frame_p95: float,
    cpu_p95: float,
    packet_loss_p95: float,
    desync_events: int,
    rubberband_events: int,
    aoe_events: int,
    replicated_objects_p95: float,
) -> float:
    score = 0.0
    score += min(players / 150.0, 1.0) * 15.0
    score += min(max(server_frame_p95 - 25.0, 0.0) / 50.0, 1.0) * 25.0
    score += min(max(cpu_p95 - 60.0, 0.0) / 35.0, 1.0) * 15.0
    score += min(packet_loss_p95 / 8.0, 1.0) * 10.0
    score += min((desync_events + rubberband_events) / 80.0, 1.0) * 15.0
    score += min(aoe_events / 700.0, 1.0) * 10.0
    score += min(replicated_objects_p95 / 15000.0, 1.0) * 10.0
    return round(min(score, 100.0), 2)
