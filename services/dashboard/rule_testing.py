from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

from aegis_common.rule_test_runner import evaluate_profile_against_samples, evaluate_single_metrics, load_sample
from aegis_common.rule_based_recommendation_engine import load_rule_profiles

RECOMMENDATION_RULE_DIR = os.getenv("RECOMMENDATION_RULE_DIR", "/app/recommendation_rules")
RECOMMENDATION_SAMPLE_DIR = os.getenv("RECOMMENDATION_SAMPLE_DIR", "/app/recommendation_rules/tests")

@st.cache_data(ttl=20, show_spinner=False)
def run_profile_tests_for_ui(profile_name: str) -> dict:
    return evaluate_profile_against_samples(
        profile_name=profile_name,
        rule_dir=RECOMMENDATION_RULE_DIR,
        sample_dir=RECOMMENDATION_SAMPLE_DIR,
    )

@st.cache_data(ttl=20, show_spinner=False)
def list_rule_profiles_for_testing() -> list[str]:
    return sorted(load_rule_profiles(RECOMMENDATION_RULE_DIR).keys())

@st.cache_data(ttl=20, show_spinner=False)
def list_rule_test_samples_for_ui() -> list[dict]:
    sample_dir = Path(RECOMMENDATION_SAMPLE_DIR)
    if not sample_dir.exists():
        return []

    rows = []
    for path in sorted(sample_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows.append({
                "sample_id": payload.get("sample_id", path.stem),
                "description": payload.get("description", ""),
                "expected_issue_ids": ", ".join(payload.get("expected_issue_ids", [])),
                "path": str(path),
            })
        except Exception:
            continue

    return rows

def preview_sample_for_ui(sample_path: str, profile_name: str) -> dict:
    sample = load_sample(sample_path)
    report = evaluate_single_metrics(
        metrics=sample["metrics"],
        profile_name=profile_name,
        rule_dir=RECOMMENDATION_RULE_DIR,
    )
    report["sample_id"] = sample["sample_id"]
    report["description"] = sample.get("description", "")
    report["expected_issue_ids"] = sample.get("expected_issue_ids", [])
    report["metrics"] = sample["metrics"]
    return report
