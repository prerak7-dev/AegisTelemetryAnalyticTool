from __future__ import annotations

import pandas as pd
import streamlit as st

from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.rules import load_recommendation_rule_profiles_for_ui

def render(context: DashboardContext) -> None:
    st.subheader("Recommendation rule profiles")
    st.caption("Issue detection and solution guidance are loaded from JSON rule profiles, so developers can add/edit conditions and actions without changing Python code.")

    profiles = load_recommendation_rule_profiles_for_ui()

    if not profiles:
        st.warning("No recommendation rule profiles found in /app/recommendation_rules.")
        return

    profile_df = pd.DataFrame(profiles)
    render_table(profile_df[["profile_name", "version", "rules", "enabled_rules", "description"]], height=260)

    selected_profile = st.selectbox(
        "Inspect recommendation profile",
        profile_df["profile_name"].tolist(),
    )
    selected = profile_df[profile_df["profile_name"] == selected_profile].iloc[0]

    st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
    st.write(f"**Profile:** `{selected['profile_name']}`")
    st.write(f"**Version:** `{selected['version']}`")
    st.write(f"**Enabled rules:** {selected['enabled_rules']} / {selected['rules']}")
    st.write(f"**Rule IDs:** {selected['rule_ids']}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("How developers add a new rule")
    example_rule = {
        "id": "custom_rule_id",
        "enabled": True,
        "title": "Readable issue title",
        "owner": "Owning team",
        "impact": "Why this matters to players or operations.",
        "condition": {
            "all": [
                {"metric": "p95_frame", "op": ">=", "value": 50},
                {"metric": "packet_loss_p95", "op": ">=", "value": 4}
            ]
        },
        "score": {
            "weighted_sum": [
                {"metric": "p95_frame", "min": 35, "max": 90, "weight": 0.5},
                {"metric": "packet_loss_p95", "min": 0, "max": 8, "weight": 0.5}
            ],
            "minimum": 0.2
        },
        "confidence": {
            "base": 0.45,
            "weighted_sum": [
                {"metric": "p95_frame", "min": 35, "max": 90, "weight": 0.25}
            ],
            "max": 0.95
        },
        "evidence_fields": ["p95_frame", "packet_loss_p95"],
        "recommended_actions": ["Specific action to test."],
        "investigation_steps": ["Specific investigation step."],
        "validation_plan": ["How to prove the action worked."],
        "guardrail_metrics": ["Metric that must not regress."],
        "tradeoffs": ["Known tradeoff."]
    }
    st.json(example_rule)

    st.write("Supported condition operators:")
    st.code(">  >=  <  <=  ==  !=  contains  not_contains  in  not_in", language="text")
