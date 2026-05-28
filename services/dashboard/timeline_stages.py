from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

TIMELINE_STAGE_DIR = os.getenv("TIMELINE_STAGE_DIR", "/app/timeline_stages")

@st.cache_data(ttl=60, show_spinner=False)
def load_timeline_stage_profiles_for_ui() -> list[dict]:
    stage_dir = Path(TIMELINE_STAGE_DIR)
    rows = []

    if not stage_dir.exists():
        return rows

    for path in sorted(stage_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows.append({
                "profile_name": payload.get("profile_name", path.stem),
                "version": payload.get("version", "unknown"),
                "description": payload.get("description", ""),
                "stages": len(payload.get("stages", [])),
                "rule_sequences": len(payload.get("rule_sequences", {})),
                "sequence_rule_ids": ", ".join(sorted(payload.get("rule_sequences", {}).keys())),
            })
        except Exception:
            continue

    return rows
