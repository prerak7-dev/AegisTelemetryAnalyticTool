from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from services.dashboard.components import render_incident_card, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import combined_filter_sql, query_df

def safe_json_loads(value: str) -> dict:
    try:
        return json.loads(value)
    except Exception:
        return {}

def render(context: DashboardContext) -> None:
    filters = context.filters
    st.subheader("Live incidents and evidence-backed recommendations")

    incident_filter = combined_filter_sql(
        filters.selected_source_profile,
        filters.selected_region,
        filters.selected_server,
    )

    incidents = query_df(f"""
        SELECT
          detected_at,
          severity,
          source_profile,
          region,
          server_id,
          map_id,
          zone_id,
          symptom,
          likely_driver,
          confidence,
          player_impact,
          recommended_action,
          evidence_json
        FROM incidents
        WHERE {filters.incident_time_filter}
          AND {incident_filter}
        ORDER BY detected_at DESC
        LIMIT {filters.max_table_rows}
    """)

    if incidents.empty:
        st.info("No incidents detected for the current filter.")
        return

    st.markdown('<div class="section-label">Priority incident cards</div>', unsafe_allow_html=True)
    for _, inc in incidents.head(8).iterrows():
        render_incident_card(inc)

    st.markdown('<div class="section-label">Detailed evidence drilldown</div>', unsafe_allow_html=True)
    for _, inc in incidents.iterrows():
        with st.expander(f"{inc['severity'].upper()} · {inc['source_profile']} · {inc['server_id']} · {inc['zone_id']} · {inc['likely_driver']}"):
            st.write(f"**Detected:** {inc['detected_at']}")
            st.write(f"**Source profile:** `{inc['source_profile']}`")
            st.write(f"**Region:** `{inc['region']}`")
            st.write(f"**Server:** `{inc['server_id']}`")
            st.write(f"**Map/Zone:** `{inc['map_id']} / {inc['zone_id']}`")
            st.write(f"**Symptom:** {inc['symptom']}")
            st.write(f"**Confidence:** {float(inc['confidence']):.2f}")
            st.write(f"**Player impact:** {inc['player_impact']}")
            st.write(f"**Recommended action:** {inc['recommended_action']}")

            evidence = safe_json_loads(inc["evidence_json"])
            ranked = evidence.get("issue_candidates", evidence.get("ranked_driver_scores", []))
            if ranked:
                st.write("**Ranked issue candidates:**")
                issue_rows = []
                for item in ranked:
                    issue_rows.append({
                        "issue_type": item.get("issue_type", item.get("driver", "unknown")),
                        "title": item.get("title", item.get("driver", "unknown")),
                        "owner": item.get("owner", "unknown"),
                        "score": item.get("score"),
                        "confidence": item.get("confidence"),
                        "impact": item.get("impact", item.get("evidence", "")),
                    })
                render_table(pd.DataFrame(issue_rows), height=260)

                top_issue = ranked[0]
                st.write("**Specific recommended actions:**")
                for action in top_issue.get("recommended_actions", []):
                    st.write(f"- {action}")
                st.write("**Investigation steps:**")
                for step in top_issue.get("investigation_steps", []):
                    st.write(f"- {step}")
                st.write("**Validation plan:**")
                for step in top_issue.get("validation_plan", []):
                    st.write(f"- {step}")
                st.write("**Guardrail metrics:**")
                st.write(", ".join(top_issue.get("guardrail_metrics", [])))
            st.write("**Evidence payload:**")
            st.json(evidence)
