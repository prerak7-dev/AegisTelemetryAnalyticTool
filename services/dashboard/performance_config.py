from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

import streamlit as st

DEFAULT_CONFIG_PATHS = [
    Path(os.getenv("AEGIS_DASHBOARD_PERFORMANCE_CONFIG", "")),
    Path("/app/config/dashboard_performance.json"),
    Path("config/dashboard_performance.json"),
]

DEFAULT_PERFORMANCE_CONFIG: dict[str, Any] = {
    "version": "7.2",
    "tables": {
        "aggregate_zone_table": "agg_zone_30s",
        "data_quality_table": "data_quality_failures",
        "pressure_rollup_table": "agg_pressure_30s",
        "top_pressure_zones_table": "agg_top_pressure_zones_1m",
        "context_baseline_table": "agg_context_baseline_1h",
        "incident_table": "incident_windows",
    },
    "feature_flags": {
        "prefer_pressure_rollup_table": False,
        "prefer_top_pressure_zones_table": False,
        "enable_pipeline_health_cards": True,
        "enable_query_budget_warnings": True,
    },
    "cache_policies": {
        "live": 4,
        "short": 15,
        "medium": 60,
        "static": 300,
    },
    "query_budgets_ms": {
        "default": 1500,
    },
    "parallelism": {
        "max_dashboard_workers": 3,
        "max_clickhouse_fanout": 4,
    },
    "pressure_scoring": {
        "status_thresholds": {"warning": 55, "critical": 80},
        "simulation": {"server_frame_ms_p95_budget": 75, "server_frame_ms_p99_budget": 95, "cpu_p95_budget": 95},
        "network": {"packet_loss_p95_budget": 5, "packet_out_kbps_p95_budget": 8000},
        "replication": {"replicated_objects_p95_budget": 12000, "ability_casts_budget": 1200, "aoe_events_budget": 650},
        "physics": {"physics_events_budget": 500},
        "memory": {"memory_mb_p95_budget": 12000},
        "ai": {"ai_pathfinding_requests_budget": 1200, "ai_agents_active_p95_budget": 280},
        "matchmaking": {"matchmaking_queue_p95_budget": 180, "matchmaking_events_budget": 650},
        "player_impact": {"impact_events_budget": 80, "packet_loss_weight_budget": 5, "packet_loss_weight_scale": 80},
        "telemetry_quality": {"quality_failure_ratio_budget": 0.20, "minimum_quality_denominator": 10},
    },
    "baseline": {
        "history_multiplier": 8,
        "minimum_history_minutes": 360,
        "minimum_baseline_rows": 6,
        "anomaly_score_weights": {
            "frame_ratio": 35,
            "frame_z": 18,
            "packet_loss_ratio": 30,
            "aoe_ratio": 22,
            "memory_ratio": 18,
        },
        "severity_thresholds": {"warning": 55, "critical": 80},
    },
    "dashboard_limits": {
        "default_drilldown_limit": 1200,
        "timeline_limit": 1200,
        "frame_timeline_limit": 900,
        "max_safe_table_rows": 200,
    },
    "pipeline_health": {
        "staleness_warning_seconds": 90,
        "staleness_critical_seconds": 240,
        "minimum_recent_rows_warning": 10,
    },
}

def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

@st.cache_resource(show_spinner=False)
def get_performance_config() -> dict[str, Any]:
    for path in DEFAULT_CONFIG_PATHS:
        if not path or str(path) == ".":
            continue
        try:
            if path.exists():
                with path.open("r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                return _deep_merge(DEFAULT_PERFORMANCE_CONFIG, loaded)
        except Exception:
            continue
    return copy.deepcopy(DEFAULT_PERFORMANCE_CONFIG)

def refresh_performance_config() -> None:
    get_performance_config.clear()

def cfg_get(path: str, default: Any = None) -> Any:
    value: Any = get_performance_config()
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value

def table_name(logical_name: str) -> str:
    return str(cfg_get(f"tables.{logical_name}", logical_name))

def feature_enabled(name: str, default: bool = False) -> bool:
    return bool(cfg_get(f"feature_flags.{name}", default))

def cache_ttl(policy: str) -> int:
    return int(cfg_get(f"cache_policies.{policy}", cfg_get("cache_policies.live", 4)) or 4)

def query_budget_ms(query_name: str) -> float:
    return float(cfg_get(f"query_budgets_ms.{query_name}", cfg_get("query_budgets_ms.default", 1500)) or 1500)

def pressure_budget(category: str, key: str, default: float) -> float:
    return float(cfg_get(f"pressure_scoring.{category}.{key}", default) or default)

def pressure_status_threshold(level: str, default: float) -> float:
    return float(cfg_get(f"pressure_scoring.status_thresholds.{level}", default) or default)

def dashboard_limit(key: str, default: int) -> int:
    return int(cfg_get(f"dashboard_limits.{key}", default) or default)

def baseline_cfg(key: str, default: Any) -> Any:
    return cfg_get(f"baseline.{key}", default)
