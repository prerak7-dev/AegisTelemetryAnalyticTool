from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

RECOMMENDATION_RULE_DIR = os.getenv("RECOMMENDATION_RULE_DIR", "/app/recommendation_rules")

@st.cache_data(ttl=60, show_spinner=False)
def load_recommendation_rule_profiles_for_ui() -> list[dict]:
    rule_dir = Path(RECOMMENDATION_RULE_DIR)
    rows = []

    if not rule_dir.exists():
        return rows

    for path in sorted(rule_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rules = payload.get("rules", [])
            enabled = [rule for rule in rules if rule.get("enabled", True)]
            rows.append({
                "profile_name": payload.get("profile_name", path.stem),
                "version": payload.get("version", "unknown"),
                "description": payload.get("description", ""),
                "rules": len(rules),
                "enabled_rules": len(enabled),
                "rule_ids": ", ".join(rule.get("id", "unknown") for rule in enabled),
            })
        except Exception:
            continue

    return rows
