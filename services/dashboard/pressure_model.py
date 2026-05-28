from __future__ import annotations

import math
from typing import Any

import pandas as pd

from services.dashboard.performance_config import (
    baseline_cfg,
    cfg_get,
    dashboard_limit,
    pressure_budget,
    pressure_status_threshold,
)

def clamp_score(value: float) -> float:
    try:
        if math.isnan(float(value)):
            return 0.0
        return max(0.0, min(100.0, float(value)))
    except Exception:
        return 0.0

def safe_float(row: pd.Series | dict, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default) or default)
    except Exception:
        return default

def safe_int(row: pd.Series | dict, key: str, default: int = 0) -> int:
    try:
        return int(float(row.get(key, default) or default))
    except Exception:
        return default

def divide_score(value: float, budget: float) -> float:
    if budget <= 0:
        return 0.0
    return clamp_score((float(value or 0) / budget) * 100.0)

def pressure_status(score: float) -> str:
    score = clamp_score(score)
    critical = pressure_status_threshold("critical", 80)
    warning = pressure_status_threshold("warning", 55)
    if score >= critical:
        return "critical"
    if score >= warning:
        return "warning"
    return "stable"

def build_pressure_summary(row: pd.Series | dict, quality_failures: int = 0) -> list[dict[str, Any]]:
    aggregate_rows = max(1, safe_int(row, "aggregate_rows", 1))
    impact_events = safe_float(row, "player_impact_events")
    packet_loss = safe_float(row, "packet_loss_p95")
    packet_out = safe_float(row, "packet_out_kbps_p95")
    replicated_objects = safe_float(row, "replicated_objects_p95")
    ability_casts = safe_float(row, "ability_casts")
    aoe_events = safe_float(row, "aoe_events")
    physics_events = safe_float(row, "physics_events")
    server_frame = safe_float(row, "server_frame_ms_p95")
    server_frame_p99 = safe_float(row, "server_frame_ms_p99")
    cpu = safe_float(row, "cpu_p95")
    hot_zone = safe_float(row, "hot_zone_risk_score")
    memory = safe_float(row, "memory_mb_p95")
    ai_agents = safe_float(row, "ai_agents_active_p95")
    ai_paths = safe_float(row, "ai_pathfinding_requests")
    matchmaking_events = safe_float(row, "matchmaking_events")
    matchmaking_queue = safe_float(row, "matchmaking_queue_p95")

    quality_ratio_budget = pressure_budget("telemetry_quality", "quality_failure_ratio_budget", 0.20)
    minimum_quality_denominator = pressure_budget("telemetry_quality", "minimum_quality_denominator", 10)
    quality_denominator = max(minimum_quality_denominator, aggregate_rows * quality_ratio_budget)

    summaries = [
        {
            "pressure": "Simulation",
            "score": max(
                divide_score(server_frame, pressure_budget("simulation", "server_frame_ms_p95_budget", 75)),
                divide_score(server_frame_p99, pressure_budget("simulation", "server_frame_ms_p99_budget", 95)),
                divide_score(cpu, pressure_budget("simulation", "cpu_p95_budget", 95)),
                clamp_score(hot_zone),
            ),
            "primary": f"P95 frame {server_frame:.1f} ms · CPU {cpu:.1f}",
            "driver": "Tracks frame-time, p99 hitch risk, CPU pressure, and hot-zone risk.",
            "recommendation": "Validate thread/job pressure and profile the top server/zone before treating frame time as the root cause.",
            "validation_metric": "server_frame_ms_p95 below configured budget",
        },
        {
            "pressure": "Network",
            "score": max(
                divide_score(packet_loss, pressure_budget("network", "packet_loss_p95_budget", 5)),
                divide_score(packet_out, pressure_budget("network", "packet_out_kbps_p95_budget", 8000)),
            ),
            "primary": f"Packet loss {packet_loss:.2f}% · Out {packet_out:.0f} kbps",
            "driver": "Tracks packet loss and outbound bandwidth saturation.",
            "recommendation": "Inspect packet budgets, resend pressure, and high-frequency state updates before reducing simulation quality.",
            "validation_metric": "packet_loss_p95 below configured budget",
        },
        {
            "pressure": "Replication",
            "score": max(
                divide_score(replicated_objects, pressure_budget("replication", "replicated_objects_p95_budget", 12000)),
                divide_score(ability_casts, pressure_budget("replication", "ability_casts_budget", 1200)),
                divide_score(aoe_events, pressure_budget("replication", "aoe_events_budget", 650)),
            ),
            "primary": f"Rep objects {replicated_objects:.0f} · AoE {aoe_events:.0f}",
            "driver": "Tracks replicated object count, ability casts, and AoE replication pressure.",
            "recommendation": "Review relevancy radius, replication frequency, reliable RPC usage, and non-critical actor updates.",
            "validation_metric": "replicated_objects_p95 trending down",
        },
        {
            "pressure": "Physics",
            "score": divide_score(physics_events, pressure_budget("physics", "physics_events_budget", 500)),
            "primary": f"Physics events {physics_events:.0f}",
            "driver": "Tracks collision, rigid-body, projectile, explosion, and interaction pressure proxies.",
            "recommendation": "Cap non-critical rigid-body simulation and profile overlap/raycast-heavy gameplay events.",
            "validation_metric": "physics_events stable before frame pressure",
        },
        {
            "pressure": "Memory",
            "score": divide_score(memory, pressure_budget("memory", "memory_mb_p95_budget", 12000)),
            "primary": f"Memory P95 {memory:.0f} MB",
            "driver": "Tracks memory pressure and potential allocation or object-lifetime risk.",
            "recommendation": "Inspect object churn, pooled gameplay objects, asset streaming, and session-long memory growth.",
            "validation_metric": "memory_mb_p95 below configured budget",
        },
        {
            "pressure": "AI",
            "score": max(
                divide_score(ai_paths, pressure_budget("ai", "ai_pathfinding_requests_budget", 1200)),
                divide_score(ai_agents, pressure_budget("ai", "ai_agents_active_p95_budget", 280)),
            ),
            "primary": f"Path req {ai_paths:.0f} · Agents {ai_agents:.0f}",
            "driver": "Tracks active AI agents and pathfinding request pressure.",
            "recommendation": "Stagger AI updates, cache path queries, and rate-limit replans in crowded combat zones.",
            "validation_metric": "ai_pathfinding_requests reduced",
        },
        {
            "pressure": "Matchmaking",
            "score": max(
                divide_score(matchmaking_queue, pressure_budget("matchmaking", "matchmaking_queue_p95_budget", 180)),
                divide_score(matchmaking_events, pressure_budget("matchmaking", "matchmaking_events_budget", 650)),
            ),
            "primary": f"Queue P95 {matchmaking_queue:.0f} · Events {matchmaking_events:.0f}",
            "driver": "Tracks regional capacity, session surge, and matchmaking queue pressure.",
            "recommendation": "Warm additional regional capacity and review autoscaling thresholds for the active source profile.",
            "validation_metric": "matchmaking_queue_p95 below configured target",
        },
        {
            "pressure": "Player Impact",
            "score": max(
                divide_score(impact_events, pressure_budget("player_impact", "impact_events_budget", 80)),
                divide_score(packet_loss, pressure_budget("player_impact", "packet_loss_weight_budget", 5))
                * (pressure_budget("player_impact", "packet_loss_weight_scale", 80) / 100.0),
            ),
            "primary": f"Impact events {impact_events:.0f}",
            "driver": "Tracks rubberbanding and desync as player-facing symptoms.",
            "recommendation": "Prioritize incidents where server/network pressure is followed by desync or rubberband events.",
            "validation_metric": "desync + rubberband returns to baseline",
        },
        {
            "pressure": "Telemetry Quality",
            "score": clamp_score((float(quality_failures or 0) / max(1.0, quality_denominator)) * 100.0),
            "primary": f"Validation failures {int(quality_failures or 0)}",
            "driver": "Tracks whether telemetry is complete enough to trust automated diagnosis.",
            "recommendation": "Fix schema drift or missing fields before making production optimization decisions from low-confidence data.",
            "validation_metric": "data quality failures near zero",
        },
    ]

    for item in summaries:
        item["score"] = clamp_score(item["score"])
        item["status"] = pressure_status(float(item["score"]))

    return summaries

def add_pressure_scores(df: pd.DataFrame, quality_failure_count: int = 0) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()

    def col(name: str) -> pd.Series:
        if name in out.columns:
            return pd.to_numeric(out[name], errors="coerce").fillna(0)
        return pd.Series(0, index=out.index)

    def series_score(*values: pd.Series) -> pd.Series:
        if not values:
            return pd.Series(0, index=out.index)
        combined = pd.concat(values, axis=1).max(axis=1)
        return combined.clip(lower=0, upper=100)

    impact = col("desync_events") + col("rubberband_events")

    out["simulation_pressure"] = series_score(
        col("server_frame_ms_p95") / pressure_budget("simulation", "server_frame_ms_p95_budget", 75) * 100.0,
        col("server_frame_ms_p99") / pressure_budget("simulation", "server_frame_ms_p99_budget", 95) * 100.0,
        col("cpu_p95") / pressure_budget("simulation", "cpu_p95_budget", 95) * 100.0,
        col("hot_zone_risk_score"),
    )
    out["network_pressure"] = series_score(
        col("packet_loss_p95") / pressure_budget("network", "packet_loss_p95_budget", 5) * 100.0,
        col("packet_out_kbps_p95") / pressure_budget("network", "packet_out_kbps_p95_budget", 8000) * 100.0,
    )
    out["replication_pressure"] = series_score(
        col("replicated_objects_p95") / pressure_budget("replication", "replicated_objects_p95_budget", 12000) * 100.0,
        col("ability_casts") / pressure_budget("replication", "ability_casts_budget", 1200) * 100.0,
        col("aoe_events") / pressure_budget("replication", "aoe_events_budget", 650) * 100.0,
    )
    out["physics_pressure"] = (col("physics_events") / pressure_budget("physics", "physics_events_budget", 500) * 100.0).clip(lower=0, upper=100)
    out["memory_pressure"] = (col("memory_mb_p95") / pressure_budget("memory", "memory_mb_p95_budget", 12000) * 100.0).clip(lower=0, upper=100)
    out["ai_pressure"] = series_score(
        col("ai_pathfinding_requests") / pressure_budget("ai", "ai_pathfinding_requests_budget", 1200) * 100.0,
        col("ai_agents_active_p95") / pressure_budget("ai", "ai_agents_active_p95_budget", 280) * 100.0,
    )
    out["matchmaking_pressure"] = series_score(
        col("matchmaking_queue_p95") / pressure_budget("matchmaking", "matchmaking_queue_p95_budget", 180) * 100.0,
        col("matchmaking_events") / pressure_budget("matchmaking", "matchmaking_events_budget", 650) * 100.0,
    )
    out["player_impact_pressure"] = series_score(
        impact / pressure_budget("player_impact", "impact_events_budget", 80) * 100.0,
        col("packet_loss_p95") / pressure_budget("player_impact", "packet_loss_weight_budget", 5)
        * pressure_budget("player_impact", "packet_loss_weight_scale", 80),
    )

    quality_ratio_budget = pressure_budget("telemetry_quality", "quality_failure_ratio_budget", 0.20)
    min_quality_denominator = pressure_budget("telemetry_quality", "minimum_quality_denominator", 10)
    out["telemetry_quality_pressure"] = clamp_score(
        (quality_failure_count / max(min_quality_denominator, len(out) * quality_ratio_budget)) * 100.0
    )
    out["max_pressure_score"] = out[
        [
            "simulation_pressure",
            "network_pressure",
            "replication_pressure",
            "physics_pressure",
            "memory_pressure",
            "ai_pressure",
            "matchmaking_pressure",
            "player_impact_pressure",
            "telemetry_quality_pressure",
        ]
    ].max(axis=1)

    return out

def baseline_history_minutes(active_window_minutes: int) -> int:
    multiplier = int(baseline_cfg("history_multiplier", 8) or 8)
    minimum = int(baseline_cfg("minimum_history_minutes", 360) or 360)
    return max(active_window_minutes * multiplier, minimum)

def baseline_anomaly_sql_score() -> str:
    weights = baseline_cfg(
        "anomaly_score_weights",
        {
            "frame_ratio": 35,
            "frame_z": 18,
            "packet_loss_ratio": 30,
            "aoe_ratio": 22,
            "memory_ratio": 18,
        },
    )
    return f"""
          greatest(
            if(b.baseline_p95_frame > 0, (c.current_p95_frame / b.baseline_p95_frame) * {float(weights.get("frame_ratio", 35))}, 0),
            if(b.baseline_frame_std > 0, ((c.current_p95_frame - b.baseline_p95_frame) / b.baseline_frame_std) * {float(weights.get("frame_z", 18))}, 0),
            if(b.baseline_packet_loss > 0, (c.current_packet_loss / b.baseline_packet_loss) * {float(weights.get("packet_loss_ratio", 30))}, 0),
            if(b.baseline_aoe_events > 0, (c.current_aoe_events / b.baseline_aoe_events) * {float(weights.get("aoe_ratio", 22))}, 0),
            if(b.baseline_memory > 0, (c.current_memory / b.baseline_memory) * {float(weights.get("memory_ratio", 18))}, 0)
          )
    """

def drilldown_limit(default: int = 1200) -> int:
    return dashboard_limit("default_drilldown_limit", default)

def timeline_limit(default: int = 1200) -> int:
    return dashboard_limit("timeline_limit", default)

def frame_timeline_limit(default: int = 900) -> int:
    return dashboard_limit("frame_timeline_limit", default)
