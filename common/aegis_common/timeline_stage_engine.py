from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from aegis_common.rule_based_recommendation_engine import evaluate_condition

DEFAULT_TIMELINE_STAGE_DIR = os.getenv("TIMELINE_STAGE_DIR", "/app/timeline_stages")
DEFAULT_TIMELINE_STAGE_PROFILE = os.getenv("TIMELINE_STAGE_PROFILE", "default_timeline_stages")

def load_timeline_stage_profiles(stage_dir: str | Path = DEFAULT_TIMELINE_STAGE_DIR) -> dict[str, dict[str, Any]]:
    stage_path = Path(stage_dir)
    profiles: dict[str, dict[str, Any]] = {}

    if not stage_path.exists():
        return profiles

    for path in sorted(stage_path.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        profile_name = payload.get("profile_name") or path.stem
        profiles[profile_name] = payload

    return profiles

def get_active_timeline_stage_profile(
    stage_dir: str | Path = DEFAULT_TIMELINE_STAGE_DIR,
    profile_name: str = DEFAULT_TIMELINE_STAGE_PROFILE,
) -> dict[str, Any]:
    profiles = load_timeline_stage_profiles(stage_dir)

    if profile_name in profiles:
        return profiles[profile_name]

    if "default_timeline_stages" in profiles:
        return profiles["default_timeline_stages"]

    return {
        "profile_name": "empty_timeline_stage_fallback",
        "stages": [],
        "default_sequence": [],
        "rule_sequences": {},
    }

def _safe_max(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns or df.empty:
        return 0.0
    try:
        return float(df[column].max() or 0.0)
    except Exception:
        return 0.0

def add_derived_timeline_metrics(timeline: pd.DataFrame) -> pd.DataFrame:
    """Add ratio/helper fields used by configurable timeline-stage rules."""
    if timeline.empty:
        return timeline.copy()

    df = timeline.copy()

    df["player_impact_events"] = df.get("desync_events", 0) + df.get("rubberband_events", 0)
    df["subsystem_pressure"] = (
        df.get("aoe_events", 0)
        + df.get("physics_events", 0)
        + (df.get("replicated_objects_p95", 0) / 100.0)
        + (df.get("packet_out_kbps_p95", 0) / 100.0)
        + df.get("ai_pathfinding_requests", 0)
    )

    ratio_sources = {
        "active_players_ratio": "active_players",
        "aoe_events_ratio": "aoe_events",
        "physics_events_ratio": "physics_events",
        "replicated_objects_ratio": "replicated_objects_p95",
        "packet_out_ratio": "packet_out_kbps_p95",
        "server_frame_p95_ratio": "server_frame_ms_p95",
        "player_impact_ratio": "player_impact_events",
        "ai_pathfinding_ratio": "ai_pathfinding_requests",
        "memory_ratio": "memory_mb_p95",
        "matchmaking_queue_ratio": "matchmaking_queue_p95",
        "subsystem_pressure_ratio": "subsystem_pressure",
    }

    for ratio_name, source_column in ratio_sources.items():
        max_value = _safe_max(df, source_column)
        if max_value <= 0:
            df[ratio_name] = 0.0
        else:
            df[ratio_name] = df.get(source_column, 0) / max_value

    return df

def _row_to_metrics(row: pd.Series) -> dict[str, Any]:
    return row.to_dict()

def _format_field_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)

def build_stage_detail_from_fields(row_or_source: Any, fields: list[str]) -> str:
    if hasattr(row_or_source, "get"):
        values = []
        for field in fields:
            value = row_or_source.get(field, None)
            if value is not None:
                values.append(f"{field}={_format_field_value(value)}")
        return "; ".join(values) if values else "No configured detail fields were available."
    return "No detail data available."

def _stage_by_id(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {stage["id"]: stage for stage in profile.get("stages", []) if stage.get("id")}

def sequence_for_rule(profile: dict[str, Any], rule_id: str) -> list[str]:
    rule_sequences = profile.get("rule_sequences", {})
    return rule_sequences.get(rule_id) or profile.get("default_sequence", [])

def evaluate_stage(
    stage: dict[str, Any],
    timeline: pd.DataFrame,
    incident: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    mode = stage.get("mode", "first_match")
    fields = stage.get("detail_fields", [])
    label = stage.get("label", stage.get("id", "Unknown stage"))

    if mode == "incident_start":
        detail_source = {
            **incident,
            **evidence,
        }
        return {
            "stage_id": stage.get("id"),
            "stage": label,
            "time": evidence.get("window_start") or incident.get("detected_at", "—"),
            "details": build_stage_detail_from_fields(detail_source, fields) or stage.get("fallback_detail", "Incident trigger point."),
            "matched": True,
            "mode": mode,
        }

    if mode == "recommendation":
        detail_source = {
            **incident,
            **evidence,
        }
        details = build_stage_detail_from_fields(detail_source, fields)
        if not details or details == "No configured detail fields were available.":
            details = incident.get("recommended_action") or stage.get("fallback_detail", "No recommendation text was found.")
        return {
            "stage_id": stage.get("id"),
            "stage": label,
            "time": incident.get("detected_at", "—"),
            "details": details,
            "matched": True,
            "mode": mode,
        }

    if timeline.empty:
        return {
            "stage_id": stage.get("id"),
            "stage": label,
            "time": "—",
            "details": stage.get("fallback_detail", "No timeline data available."),
            "matched": False,
            "mode": mode,
        }

    condition = stage.get("condition", {})
    matches: list[pd.Series] = []

    for _, row in timeline.sort_values("window_start").iterrows():
        metrics = _row_to_metrics(row)
        try:
            if evaluate_condition(condition, metrics):
                matches.append(row)
        except Exception as exc:
            return {
                "stage_id": stage.get("id"),
                "stage": label,
                "time": "—",
                "details": f"Stage condition failed to evaluate: {exc}",
                "matched": False,
                "mode": mode,
            }

    if not matches:
        return {
            "stage_id": stage.get("id"),
            "stage": label,
            "time": "—",
            "details": stage.get("fallback_detail", "Signal not observed in replay window."),
            "matched": False,
            "mode": mode,
        }

    if mode == "peak_match":
        # Pick the row with the highest first detail field, or first match if no
        # useful numeric field is configured.
        preferred_field = fields[0] if fields else None
        if preferred_field and preferred_field in timeline.columns:
            row = max(matches, key=lambda item: float(item.get(preferred_field, 0) or 0))
        else:
            row = matches[0]
    else:
        row = matches[0]

    return {
        "stage_id": stage.get("id"),
        "stage": label,
        "time": row.get("window_start", "—"),
        "details": build_stage_detail_from_fields(row, fields),
        "matched": True,
        "mode": mode,
    }

def build_timeline_sequence(
    timeline: pd.DataFrame,
    incident: dict[str, Any],
    evidence: dict[str, Any],
    profile: dict[str, Any] | None = None,
) -> pd.DataFrame:
    if profile is None:
        profile = get_active_timeline_stage_profile()

    rule_id = str(incident.get("likely_driver") or evidence.get("likely_driver") or "unclassified_performance_pressure")
    stage_lookup = _stage_by_id(profile)
    sequence_ids = sequence_for_rule(profile, rule_id)

    if not sequence_ids:
        sequence_ids = [stage["id"] for stage in profile.get("stages", []) if stage.get("id")]

    enriched_timeline = add_derived_timeline_metrics(timeline)

    rows = []
    for stage_id in sequence_ids:
        stage = stage_lookup.get(stage_id)
        if not stage:
            rows.append({
                "stage_id": stage_id,
                "stage": f"Missing stage: {stage_id}",
                "time": "—",
                "details": "This stage ID is referenced by the profile sequence but is not defined in stages.",
                "matched": False,
                "mode": "missing",
            })
            continue
        rows.append(evaluate_stage(stage, enriched_timeline, incident, evidence))

    return pd.DataFrame(rows)

def profile_summaries(stage_dir: str | Path = DEFAULT_TIMELINE_STAGE_DIR) -> list[dict[str, Any]]:
    summaries = []
    for profile in load_timeline_stage_profiles(stage_dir).values():
        summaries.append({
            "profile_name": profile.get("profile_name"),
            "version": profile.get("version", "unknown"),
            "description": profile.get("description", ""),
            "stages": len(profile.get("stages", [])),
            "rule_sequences": len(profile.get("rule_sequences", {})),
            "sequence_rule_ids": ", ".join(sorted(profile.get("rule_sequences", {}).keys())),
        })
    return sorted(summaries, key=lambda item: item["profile_name"] or "")
