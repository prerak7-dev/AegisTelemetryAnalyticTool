from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from services.dashboard.config import SOURCE_SCHEMA_DIR

@st.cache_data(ttl=60, show_spinner=False)
def load_source_profiles_for_ui() -> list[dict]:
    """Load source-schema profiles shown in the Source Schemas workspace.

    To add a new source schema:
    1. Add a new JSON profile under `source_schemas/`.
    2. Rebuild the dashboard container.
    3. The profile appears automatically here.
    """
    profile_dir = Path(SOURCE_SCHEMA_DIR)
    rows = []

    if not profile_dir.exists():
        return rows

    for path in sorted(profile_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows.append({
                "profile_name": payload.get("profile_name", path.stem),
                "version": payload.get("version", "1.0.0"),
                "passthrough": payload.get("passthrough", False),
                "description": payload.get("description", ""),
                "mapped_fields": ", ".join(sorted(payload.get("field_map", {}).keys())),
            })
        except Exception:
            continue

    return rows
