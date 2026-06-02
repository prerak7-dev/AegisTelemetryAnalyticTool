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
        "live_fleet_health_table": "live_fleet_health_30s",
        "live_pressure_summary_table": "live_pressure_summary_1m",
        "live_regional_pressure_table": "live_regional_pressure_1m",
        "live_hot_zone_table": "live_hot_zones_30s",
        "latest_incident_summary_table": "latest_incident_summary",
        "latest_demo_pipeline_status_table": "latest_demo_pipeline_status",
    },
    "feature_flags": {
        "prefer_pressure_rollup_table": False,
        "prefer_top_pressure_zones_table": False,
        "enable_pipeline_health_cards": True,
        "enable_query_budget_warnings": True,
        "prefer_live_snapshot_tables": True,
        "enable_live_snapshot_badges": True,
    },
    "refresh_runtime": {
        "enabled": True,
        "default_workspace_policy": {
            "mode": "live",
            "auto_refresh": True,
            "interval_multiplier": 1.0,
            "min_interval_seconds": 5,
            "max_interval_seconds": 60,
            "render_kpi_strip": True,
            "cache_policy_hint": "live",
            "description": "Default live workspace refresh policy.",
        },
        "mode_defaults": {
            "live": {"auto_refresh": True, "render_kpi_strip": True, "cache_policy_hint": "live"},
            "incident": {"auto_refresh": True, "interval_multiplier": 1.5, "render_kpi_strip": True, "cache_policy_hint": "short"},
            "demo": {"auto_refresh": True, "interval_multiplier": 0.75, "min_interval_seconds": 3, "render_kpi_strip": False, "cache_policy_hint": "live"},
            "manual": {"auto_refresh": False, "render_kpi_strip": False, "cache_policy_hint": "medium"},
            "static": {"auto_refresh": False, "render_kpi_strip": False, "cache_policy_hint": "static"},
        },
        "adaptive_intervals": {"enabled": True, "jitter_ratio": 0.08},
        "workspaces": {
            "command_center": {"mode": "live", "auto_refresh": True, "render_kpi_strip": True},
            "selected_server": {"mode": "live", "auto_refresh": True, "interval_multiplier": 1.25, "render_kpi_strip": True},
            "scaling_readiness": {"mode": "live", "auto_refresh": True, "interval_multiplier": 1.5, "render_kpi_strip": True},
            "incident_dossier": {"mode": "incident", "auto_refresh": True, "interval_multiplier": 1.5, "render_kpi_strip": True},
            "incident_workflow": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": False},
            "incident_timeline": {"mode": "incident", "auto_refresh": True, "interval_multiplier": 2.0, "render_kpi_strip": True},
            "baseline_intelligence": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": True},
            "build_regression": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": False},
            "rule_testing": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": False},
            "fix_validation": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": False},
            "recommendation_rules": {"mode": "static", "auto_refresh": False, "render_kpi_strip": False},
            "timeline_stages": {"mode": "static", "auto_refresh": False, "render_kpi_strip": False},
            "data_quality": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": False},
            "source_schemas": {"mode": "static", "auto_refresh": False, "render_kpi_strip": False},
            "query_performance": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": False},
            "performance_config": {"mode": "static", "auto_refresh": False, "render_kpi_strip": False},
            "analyst_toolkit": {"mode": "manual", "auto_refresh": False, "render_kpi_strip": False},
            "documentation": {"mode": "static", "auto_refresh": False, "render_kpi_strip": False},
            "demo_control_center": {"mode": "demo", "auto_refresh": True, "interval_multiplier": 0.75, "min_interval_seconds": 3, "max_interval_seconds": 30, "render_kpi_strip": False},
        },
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
            "physics_ratio": 18,
            "replication_ratio": 18,
            "player_impact_ratio": 25,
        },
        "dynamic_thresholds": {
            "warning_z": 2.0,
            "critical_z": 3.0,
            "warning_ratio": 1.35,
            "critical_ratio": 1.75,
        },
        "confidence": {
            "minimum_confidence": 0.35,
            "strong_sample_multiplier": 4,
        },
        "baseline_scope": {
            "default_dimension": "source_region_server_map_zone",
            "available_dimensions": [
                "source_region_server_map_zone",
                "source_region_map_zone",
                "source_region",
                "source_profile",
            ],
        },
        "metric_catalog": {
            "frame": {
                "label": "P95 server frame",
                "current_column": "current_p95_frame",
                "baseline_column": "baseline_p95_frame",
                "ratio_column": "frame_ratio",
                "z_column": "frame_z",
                "unit": "ms",
            },
            "packet_loss": {
                "label": "Packet loss",
                "current_column": "current_packet_loss",
                "baseline_column": "baseline_packet_loss",
                "ratio_column": "packet_loss_ratio",
                "z_column": "",
                "unit": "%",
            },
            "aoe": {
                "label": "AoE events",
                "current_column": "current_aoe_events",
                "baseline_column": "baseline_aoe_events",
                "ratio_column": "aoe_ratio",
                "z_column": "",
                "unit": "events/window",
            },
            "memory": {
                "label": "Memory pressure",
                "current_column": "current_memory",
                "baseline_column": "baseline_memory",
                "ratio_column": "memory_ratio",
                "z_column": "",
                "unit": "MB",
            },
            "physics": {
                "label": "Physics events",
                "current_column": "current_physics_events",
                "baseline_column": "baseline_physics_events",
                "ratio_column": "physics_ratio",
                "z_column": "",
                "unit": "events/window",
            },
            "replication": {
                "label": "Replication pressure",
                "current_column": "current_replication",
                "baseline_column": "baseline_replication",
                "ratio_column": "replication_ratio",
                "z_column": "",
                "unit": "objects",
            },
            "player_impact": {
                "label": "Player impact",
                "current_column": "current_player_impact",
                "baseline_column": "baseline_player_impact",
                "ratio_column": "player_impact_ratio",
                "z_column": "",
                "unit": "events/window",
            },
        },
        "severity_thresholds": {"warning": 55, "critical": 80},
    },
    "production_readiness": {
        "openapi_contract_path": "/app/openapi/collector.openapi.json",
        "observability": {
            "metrics_endpoint": "http://collector:8000/metrics",
            "health_endpoint": "http://collector:8000/health",
            "prometheus_config": "/app/infra/observability/prometheus.yml",
            "grafana_dashboard": "/app/infra/observability/grafana/aegis_telemetry_dashboard.json",
        },
        "kafka": {
            "topic_retention_doc": "/app/docs/toolkit/production_readiness/kafka_retention_dlq.md",
            "dead_letter_topic": "telemetry.validation_failed",
            "processor_group_id": "aegis-processor-local",
        },
        "clickhouse": {
            "partitioning_doc": "/app/docs/toolkit/production_readiness/clickhouse_partitioning.md",
            "primary_aggregate_table": "agg_zone_30s",
        },
        "load_testing": {
            "profile_path": "/app/tools/load_test_collector.py",
            "default_eps": 500,
            "default_duration_sec": 300,
        },
        "readiness_checklist_path": "/app/docs/toolkit/production_readiness/readiness_checklist.md",
    },
    "documentation_workspace": {
        "navigation_path": "/app/config/documentation_navigation.json",
        "docs_root": "/app/docs/toolkit",
        "enable_markdown_download": True,
        "show_audience_badges": True,
        "show_table_of_contents": True,
        "max_search_results": 20,
    },
    "analyst_toolkit": {
        "sql_template_dir": "/app/sql/analyst_templates",
        "notebook_dir": "/app/notebooks",
        "export_row_limit_default": 1000,
        "export_row_limit_options": [100, 500, 1000, 2500, 5000, 10000],
        "allow_template_execution": True,
        "download_formats": ["csv", "json"],
        "templates": [
            {
                "id": "hot_zone_summary",
                "title": "Hot Zone Summary",
                "file": "hot_zone_summary.sql",
                "description": "Server/map/zone pressure summary for current filters.",
            },
            {
                "id": "incident_evidence",
                "title": "Incident Evidence",
                "file": "incident_evidence.sql",
                "description": "Evidence-backed incidents, recommendations, and likely drivers.",
            },
            {
                "id": "source_profile_comparison",
                "title": "Source Profile Comparison",
                "file": "source_profile_comparison.sql",
                "description": "Compare telemetry quality and pressure across source profiles.",
            },
            {
                "id": "build_regression_export",
                "title": "Build Regression Export",
                "file": "build_regression_export.sql",
                "description": "Build/version performance comparison export.",
            },
            {
                "id": "fix_validation_export",
                "title": "Fix Validation Export",
                "file": "fix_validation_export.sql",
                "description": "Experiment control/treatment validation export from raw event experiment fields.",
            },
            {
                "id": "rule_quality_review",
                "title": "Rule Quality Review",
                "file": "rule_quality_review.sql",
                "description": "Incident rule coverage and recommendation quality review.",
            },
        ],
    },
    "demo_control_center": {
        "scenario_library_path": "/app/config/demo_scenarios.json",
        "allow_subprocess_launch": True,
        "python_executable": "python",
        "simulator_script_path": "/app/simulator/generate_traffic.py",
        "collector_url": "http://collector:8000",
        "host_python_executable": "python",
        "host_simulator_script_path": "simulator/generate_traffic.py",
        "host_collector_url": "http://localhost:8000",
        "default_batch_size": 250,
        "max_parallel_scenario_processes": 4,
        "status_refresh_seconds": 2,
        "feedback_window_minutes": 10,
        "processor_warmup_seconds": 3,
        "aggregate_window_seconds": 30,
        "aggregate_grace_seconds": 8,
        "show_pipeline_feedback": True,
        "enable_data_reset": True,
        "reset_tables": [
            "raw_events",
            "agg_zone_30s",
            "data_quality_failures",
            "incidents",
        ],
        "scenario_history_path": "/app/data/demo_scenario_history.json",
        "safety": {
            "require_reset_confirmation": True,
            "allow_reset_in_demo_mode": True,
        },
    },
    "incident_workflow": {
        "store_path": "/app/data/incident_workflow.json",
        "status_options": ["open", "investigating", "mitigated", "resolved", "deferred"],
        "default_status": "open",
        "owner_options": [
            "Unassigned",
            "Live Ops",
            "Online Services",
            "Gameplay Engineering",
            "Network Engineering",
            "Technical Animation",
            "Data Platform",
            "Release Management",
        ],
        "severity_sla_minutes": {
            "critical": 30,
            "warning": 120,
            "info": 360,
        },
        "escalation": {
            "enabled": True,
            "default_next_action": "Review evidence, assign owner, validate likely driver, and choose mitigation path.",
            "stale_statuses": ["open", "investigating"],
            "resolved_statuses": ["resolved"],
        },
        "report": {
            "include_evidence_json": True,
            "include_workflow_notes": True,
            "default_report_title": "AegisTelemetry Incident Report",
        },
    },
    "fix_validation": {
        "experiment_fields": {
            "experiment_id": "experiment_id",
            "variant": "experiment_variant",
            "change_id": "change_id",
            "validation_plan_id": "validation_plan_id",
        },
        "default_control_variants": ["control", "baseline", "old", "previous"],
        "default_treatment_variants": ["treatment", "candidate", "new", "improved"],
        "minimum_samples_per_variant": 100,
        "statistical_test": {
            "enabled": True,
            "t_stat_threshold": 1.96,
            "minimum_confidence": 0.35,
            "strong_sample_multiplier": 5,
        },
        "decision_thresholds": {
            "minimum_primary_improvement_pct": 5.0,
            "maximum_guardrail_regression_pct": 5.0,
            "watch_primary_improvement_pct": 2.0,
        },
        "metric_catalog": {
            "server_frame_ms": {
                "label": "Server frame time",
                "source_column": "server_frame_ms",
                "summary": "quantile(0.95)",
                "direction": "lower_is_better",
                "role": "primary",
                "unit": "ms",
                "weight": 1.00,
            },
            "packet_out_kbps": {
                "label": "Packet out",
                "source_column": "packet_out_kbps",
                "summary": "quantile(0.95)",
                "direction": "lower_is_better",
                "role": "primary",
                "unit": "kbps",
                "weight": 0.85,
            },
            "replicated_objects": {
                "label": "Replicated objects",
                "source_column": "replicated_objects",
                "summary": "quantile(0.95)",
                "direction": "lower_is_better",
                "role": "primary",
                "unit": "objects",
                "weight": 0.75,
            },
            "physics_events": {
                "label": "Physics events",
                "source_column": "physics_events",
                "summary": "avg",
                "direction": "lower_is_better",
                "role": "primary",
                "unit": "events",
                "weight": 0.75,
            },
            "packet_loss_percent": {
                "label": "Packet loss",
                "source_column": "packet_loss_percent",
                "summary": "quantile(0.95)",
                "direction": "lower_is_better",
                "role": "guardrail",
                "unit": "%",
                "weight": 1.00,
            },
            "desync_count": {
                "label": "Desync events",
                "source_column": "desync_count",
                "summary": "avg",
                "direction": "lower_is_better",
                "role": "guardrail",
                "unit": "events",
                "weight": 1.00,
            },
            "rubberband_count": {
                "label": "Rubberband events",
                "source_column": "rubberband_count",
                "summary": "avg",
                "direction": "lower_is_better",
                "role": "guardrail",
                "unit": "events",
                "weight": 1.00,
            },
            "memory_mb": {
                "label": "Memory",
                "source_column": "memory_mb",
                "summary": "quantile(0.95)",
                "direction": "lower_is_better",
                "role": "guardrail",
                "unit": "MB",
                "weight": 0.80,
            },
            "player_count": {
                "label": "Player population",
                "source_column": "player_count",
                "summary": "avg",
                "direction": "higher_is_better",
                "role": "guardrail",
                "unit": "players",
                "weight": 0.50,
            },
        },
    },
    "build_regression": {
        "build_column": "build_version",
        "default_comparison_scope": "source_region_map_zone",
        "available_scopes": [
            "source_region_server_map_zone",
            "source_region_map_zone",
            "source_region",
            "source_profile",
        ],
        "minimum_windows_per_build": 3,
        "regression_thresholds": {
            "warning_pct": 15.0,
            "critical_pct": 35.0,
            "minimum_confidence": 0.35,
            "strong_sample_multiplier": 4,
        },
        "metric_catalog": {
            "server_frame_ms_p95": {
                "label": "P95 server frame",
                "agg": "quantile(0.95)",
                "direction": "lower_is_better",
                "unit": "ms",
                "weight": 1.00,
            },
            "server_frame_ms_p99": {
                "label": "P99 server frame",
                "agg": "quantile(0.95)",
                "direction": "lower_is_better",
                "unit": "ms",
                "weight": 1.00,
            },
            "packet_out_kbps_p95": {
                "label": "Packet out P95",
                "agg": "quantile(0.95)",
                "direction": "lower_is_better",
                "unit": "kbps",
                "weight": 0.85,
            },
            "packet_loss_p95": {
                "label": "Packet loss P95",
                "agg": "quantile(0.95)",
                "direction": "lower_is_better",
                "unit": "%",
                "weight": 0.95,
            },
            "replicated_objects_p95": {
                "label": "Replicated objects P95",
                "agg": "quantile(0.95)",
                "direction": "lower_is_better",
                "unit": "objects",
                "weight": 0.75,
            },
            "physics_events": {
                "label": "Physics events",
                "agg": "avg",
                "direction": "lower_is_better",
                "unit": "events/window",
                "weight": 0.80,
            },
            "memory_mb_p95": {
                "label": "Memory P95",
                "agg": "quantile(0.95)",
                "direction": "lower_is_better",
                "unit": "MB",
                "weight": 0.90,
            },
            "desync_events": {
                "label": "Desync events",
                "agg": "avg",
                "direction": "lower_is_better",
                "unit": "events/window",
                "weight": 0.95,
            },
            "rubberband_events": {
                "label": "Rubberband events",
                "agg": "avg",
                "direction": "lower_is_better",
                "unit": "events/window",
                "weight": 0.95,
            },
            "hot_zone_risk_score": {
                "label": "Hot-zone risk",
                "agg": "max",
                "direction": "lower_is_better",
                "unit": "score",
                "weight": 1.00,
            },
        },
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


def build_regression_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"build_regression.{key}", default)


def fix_validation_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"fix_validation.{key}", default)


def incident_workflow_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"incident_workflow.{key}", default)


def demo_control_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"demo_control_center.{key}", default)


def analyst_toolkit_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"analyst_toolkit.{key}", default)


def documentation_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"documentation_workspace.{key}", default)


def production_readiness_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"production_readiness.{key}", default)


def refresh_runtime_cfg(key: str, default: Any = None) -> Any:
    return cfg_get(f"refresh_runtime.{key}", default)
