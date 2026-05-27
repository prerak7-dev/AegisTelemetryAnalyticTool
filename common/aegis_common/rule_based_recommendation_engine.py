from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_RULE_DIR = os.getenv("RECOMMENDATION_RULE_DIR", "/app/recommendation_rules")
DEFAULT_RULE_PROFILE = os.getenv("RECOMMENDATION_RULE_PROFILE", "default_recommendation_rules")

SUPPORTED_OPERATORS = {
    ">",
    ">=",
    "<",
    "<=",
    "==",
    "!=",
    "contains",
    "not_contains",
    "in",
    "not_in",
}

def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))

def metric_value(metrics: dict[str, Any], name: str) -> Any:
    if name == "player_impact_total":
        return float(metrics.get("desync_events", 0) or 0) + float(metrics.get("rubberband_events", 0) or 0)
    return metrics.get(name, 0)

def as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def normalized_metric(metrics: dict[str, Any], item: dict[str, Any]) -> float:
    value = as_float(metric_value(metrics, item.get("metric", "")))
    low = as_float(item.get("min", 0))
    high = as_float(item.get("max", 1))
    if high == low:
        return 0.0
    return clamp((value - low) / (high - low))

def evaluate_condition(condition: dict[str, Any], metrics: dict[str, Any]) -> bool:
    if not condition:
        return True

    if "all" in condition:
        return all(evaluate_condition(child, metrics) for child in condition["all"])

    if "any" in condition:
        return any(evaluate_condition(child, metrics) for child in condition["any"])

    metric = condition.get("metric")
    op = condition.get("op")
    expected = condition.get("value")
    actual = metric_value(metrics, metric)

    if op not in SUPPORTED_OPERATORS:
        raise ValueError(f"Unsupported rule operator '{op}' for metric '{metric}'")

    if op in {">", ">=", "<", "<="}:
        actual_num = as_float(actual)
        expected_num = as_float(expected)
        if op == ">":
            return actual_num > expected_num
        if op == ">=":
            return actual_num >= expected_num
        if op == "<":
            return actual_num < expected_num
        return actual_num <= expected_num

    if op == "==":
        return actual == expected
    if op == "!=":
        return actual != expected
    if op == "contains":
        return str(expected).lower() in str(actual).lower()
    if op == "not_contains":
        return str(expected).lower() not in str(actual).lower()
    if op == "in":
        return actual in (expected or [])
    if op == "not_in":
        return actual not in (expected or [])

    return False

def weighted_sum_score(metrics: dict[str, Any], config: dict[str, Any]) -> float:
    score = 0.0
    for item in config.get("weighted_sum", []):
        score += normalized_metric(metrics, item) * as_float(item.get("weight", 0))
    return round(clamp(score), 3)

def confidence_score(metrics: dict[str, Any], config: dict[str, Any]) -> float:
    confidence = as_float(config.get("base", 0.5))
    for item in config.get("weighted_sum", []):
        confidence += normalized_metric(metrics, item) * as_float(item.get("weight", 0))
    return round(clamp(confidence, 0.0, as_float(config.get("max", 0.96))), 3)

def evidence_from_fields(metrics: dict[str, Any], fields: list[str]) -> list[str]:
    evidence = []
    for field in fields:
        value = metric_value(metrics, field)
        evidence.append(f"{field}={value}")
    return evidence

def load_rule_profiles(rule_dir: str | Path = DEFAULT_RULE_DIR) -> dict[str, dict[str, Any]]:
    rule_path = Path(rule_dir)
    profiles: dict[str, dict[str, Any]] = {}

    if not rule_path.exists():
        return profiles

    for path in sorted(rule_path.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        profile_name = payload.get("profile_name") or path.stem
        profiles[profile_name] = payload

    return profiles

def get_active_profile(
    rule_dir: str | Path = DEFAULT_RULE_DIR,
    profile_name: str = DEFAULT_RULE_PROFILE,
) -> dict[str, Any]:
    profiles = load_rule_profiles(rule_dir)

    if profile_name in profiles:
        return profiles[profile_name]

    if "default_recommendation_rules" in profiles:
        return profiles["default_recommendation_rules"]

    return {
        "profile_name": "empty_fallback",
        "rules": [],
    }

def evaluate_rules(metrics: dict[str, Any], profile: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if profile is None:
        profile = get_active_profile()

    candidates: list[dict[str, Any]] = []

    for rule in profile.get("rules", []):
        if not rule.get("enabled", True):
            continue

        try:
            if not evaluate_condition(rule.get("condition", {}), metrics):
                continue
        except Exception as exc:
            candidates.append({
                "issue_type": f"invalid_rule:{rule.get('id', 'unknown')}",
                "title": "Invalid recommendation rule",
                "owner": "Telemetry Platform",
                "score": 0.0,
                "confidence": 0.0,
                "impact": f"Rule could not be evaluated: {exc}",
                "evidence": [],
                "recommended_actions": ["Fix the recommendation rule configuration."],
                "investigation_steps": [f"Inspect rule id {rule.get('id', 'unknown')} in the active recommendation profile."],
                "validation_plan": ["Run simulator traffic and confirm the rule evaluates without errors."],
                "guardrail_metrics": ["rule_evaluation_error_count"],
                "tradeoffs": [],
                "rule_id": rule.get("id", "unknown"),
            })
            continue

        score_config = rule.get("score", {})
        score = weighted_sum_score(metrics, score_config)
        minimum = as_float(score_config.get("minimum", 0.0))
        if score < minimum:
            continue

        candidates.append({
            "issue_type": rule.get("id", "unknown_rule"),
            "title": rule.get("title", rule.get("id", "Unknown issue")),
            "owner": rule.get("owner", "Unassigned"),
            "score": score,
            "confidence": confidence_score(metrics, rule.get("confidence", {})),
            "impact": rule.get("impact", ""),
            "evidence": evidence_from_fields(metrics, rule.get("evidence_fields", [])),
            "recommended_actions": rule.get("recommended_actions", []),
            "investigation_steps": rule.get("investigation_steps", []),
            "validation_plan": rule.get("validation_plan", []),
            "guardrail_metrics": rule.get("guardrail_metrics", []),
            "tradeoffs": rule.get("tradeoffs", []),
            "rule_id": rule.get("id", "unknown_rule"),
        })

    return sorted(candidates, key=lambda item: item.get("score", 0), reverse=True)

def top_rule_issue(metrics: dict[str, Any], profile: dict[str, Any] | None = None) -> dict[str, Any]:
    candidates = evaluate_rules(metrics, profile)
    if candidates:
        return candidates[0]

    return {
        "issue_type": "unclassified_performance_pressure",
        "title": "Unclassified performance pressure",
        "owner": "Telemetry Platform + Server Engineering",
        "score": 0.1,
        "confidence": 0.4,
        "impact": "Telemetry indicates performance pressure, but no configured rule matched strongly.",
        "evidence": [],
        "recommended_actions": [
            "Inspect raw event timeline and add a new recommendation rule for this pattern."
        ],
        "investigation_steps": [
            "Review p95/p99 server frame time, CPU, packet loss, replication count, and event-type distribution."
        ],
        "validation_plan": [
            "Create a custom rule matching the observed incident and replay the scenario."
        ],
        "guardrail_metrics": [
            "server_frame_ms_p95",
            "server_frame_ms_p99",
            "packet_loss_percent_p95"
        ],
        "tradeoffs": [],
        "rule_id": "unclassified_performance_pressure",
    }

def profile_summaries(rule_dir: str | Path = DEFAULT_RULE_DIR) -> list[dict[str, Any]]:
    summaries = []
    for profile in load_rule_profiles(rule_dir).values():
        enabled_rules = [rule for rule in profile.get("rules", []) if rule.get("enabled", True)]
        summaries.append({
            "profile_name": profile.get("profile_name"),
            "version": profile.get("version", "unknown"),
            "description": profile.get("description", ""),
            "rules": len(profile.get("rules", [])),
            "enabled_rules": len(enabled_rules),
            "rule_ids": ", ".join(rule.get("id", "unknown") for rule in enabled_rules),
        })
    return sorted(summaries, key=lambda item: item["profile_name"] or "")
