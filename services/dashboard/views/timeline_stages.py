from __future__ import annotations

import pandas as pd
import streamlit as st

from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.timeline_stages import load_timeline_stage_profiles_for_ui

def render(context: DashboardContext) -> None:
    st.subheader("Timeline Stage Profiles")
    st.caption("Incident replay stages are loaded from JSON profiles, so developers can add, remove, or reorder root-cause stages without editing Python code.")

    profiles = load_timeline_stage_profiles_for_ui()
    if not profiles:
        st.warning("No timeline stage profiles found in /app/timeline_stages.")
        return

    profile_df = pd.DataFrame(profiles)
    render_table(profile_df[["profile_name", "version", "stages", "rule_sequences", "description"]], height=260)

    selected_profile = st.selectbox("Inspect timeline stage profile", profile_df["profile_name"].tolist())
    selected = profile_df[profile_df["profile_name"] == selected_profile].iloc[0]

    st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
    st.write(f"**Profile:** `{selected['profile_name']}`")
    st.write(f"**Version:** `{selected['version']}`")
    st.write(f"**Stages:** {selected['stages']}")
    st.write(f"**Rule-specific sequences:** {selected['rule_sequences']}")
    st.write(f"**Rule IDs:** {selected['sequence_rule_ids']}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("How developers add a custom stage")
    st.json({
        "id": "custom_stage_id",
        "label": "Readable stage label",
        "mode": "first_match",
        "condition": {
            "all": [
                {"metric": "active_players", "op": ">=", "value": 160},
                {"metric": "top_ability_id", "op": "contains", "value": "aoe"}
            ]
        },
        "detail_fields": [
            "active_players",
            "top_ability_id",
            "server_frame_ms_p95"
        ],
        "fallback_detail": "Custom signal was not observed in this replay window."
    })

    st.write("Supported stage modes:")
    st.code("incident_start  recommendation  first_match  peak_match", language="text")

    st.write("Supported condition operators come from the same rule engine used by recommendation rules:")
    st.code(">  >=  <  <=  ==  !=  contains  not_contains  in  not_in", language="text")
