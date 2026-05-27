from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from services.dashboard.components import render_incident_card, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import combined_filter_sql, query_df, quote_sql

RECOMMENDATION_RULE_DIR = os.getenv("RECOMMENDATION_RULE_DIR", "/app/recommendation_rules")

SEVERITY_OPTIONS = {
    "All severities": "",
    "Critical only": "critical",
    "Warnings only": "warning",
}

ALL_RULE_IDS = "All rule IDs"

def safe_json_loads(value: str) -> dict:
    try:
        return json.loads(value)
    except Exception:
        return {}

def severity_filter_sql(selected_severity: str) -> str:
    severity = SEVERITY_OPTIONS.get(selected_severity, "")
    if not severity:
        return "1 = 1"
    return f"severity = {quote_sql(severity)}"

def rule_id_filter_sql(selected_rule_id: str) -> str:
    if selected_rule_id == ALL_RULE_IDS:
        return "1 = 1"
    return f"likely_driver = {quote_sql(selected_rule_id)}"

@st.cache_data(ttl=60, show_spinner=False)
def load_configured_rule_ids() -> list[str]:
    """Load all rule IDs from recommendation rule profile JSON files.

    This makes the Incident Dossier filter show built-in and custom rule IDs,
    even before a rule has produced an incident in the selected time window.
    """
    rule_dir = Path(RECOMMENDATION_RULE_DIR)
    rule_ids: set[str] = set()

    if not rule_dir.exists():
        return []

    for path in sorted(rule_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        for rule in payload.get("rules", []):
            rule_id = rule.get("id")
            if rule_id:
                rule_ids.add(str(rule_id))

    rule_ids.add("unclassified_performance_pressure")
    return sorted(rule_ids)

def get_observed_rule_ids(filters: DashboardContext, incident_filter: str) -> list[str]:
    observed = query_df(f"""
        SELECT DISTINCT likely_driver
        FROM incidents
        WHERE {filters.filters.incident_time_filter}
          AND {incident_filter}
        ORDER BY likely_driver ASC
        LIMIT 500
    """)

    if observed.empty:
        return []

    return sorted([
        str(value)
        for value in observed["likely_driver"].dropna().tolist()
        if str(value).strip()
    ])

def render(context: DashboardContext) -> None:
    filters = context.filters
    st.subheader("Live incidents and evidence-backed recommendations")

    incident_filter = combined_filter_sql(
        filters.selected_source_profile,
        filters.selected_region,
        filters.selected_server,
    )

    configured_rule_ids = load_configured_rule_ids()
    observed_rule_ids = get_observed_rule_ids(context, incident_filter)
    rule_options = [ALL_RULE_IDS] + sorted(set(configured_rule_ids) | set(observed_rule_ids))

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_severity = st.selectbox(
            "Incident severity",
            list(SEVERITY_OPTIONS.keys()),
            index=0,
            help="Filter the incident dossier by warning/critical severity so analysts can triage the right class of issue.",
        )

    with filter_col2:
        selected_rule_id = st.selectbox(
            "Rule ID / likely driver",
            rule_options,
            index=0,
            help="Filter incidents by the recommendation rule ID that produced the likely driver, such as memory_pressure or physics_simulation_spike.",
        )

    severity_filter = severity_filter_sql(selected_severity)
    rule_filter = rule_id_filter_sql(selected_rule_id)

    summary = query_df(f"""
        SELECT
          severity,
          likely_driver AS rule_id,
          count() AS incidents,
          max(detected_at) AS latest_incident
        FROM incidents
        WHERE {filters.incident_time_filter}
          AND {incident_filter}
        GROUP BY severity, likely_driver
        ORDER BY
          multiIf(severity = 'critical', 1, severity = 'warning', 2, 3),
          incidents DESC,
          latest_incident DESC
        LIMIT 200
    """)

    if not summary.empty:
        st.caption("Severity and rule distribution in the selected source/region/server/time window.")
        render_table(summary, height=220)

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
          AND {severity_filter}
          AND {rule_filter}
        ORDER BY
          multiIf(severity = 'critical', 1, severity = 'warning', 2, 3),
          detected_at DESC
        LIMIT {filters.max_table_rows}
    """)

    if incidents.empty:
        st.info(
            f"No incidents detected for severity `{selected_severity}` and rule ID `{selected_rule_id}` "
            "within the current source/region/server/time-window filters."
        )
        return

    st.markdown('<div class="section-label">Priority incident cards</div>', unsafe_allow_html=True)
    for _, inc in incidents.head(8).iterrows():
        render_incident_card(inc)

    st.markdown('<div class="section-label">Detailed evidence drilldown</div>', unsafe_allow_html=True)
    for _, inc in incidents.iterrows():
        with st.expander(f"{inc['severity'].upper()} · {inc['likely_driver']} · {inc['source_profile']} · {inc['server_id']} · {inc['zone_id']}"):
            st.write(f"**Detected:** {inc['detected_at']}")
            st.write(f"**Severity:** `{inc['severity']}`")
            st.write(f"**Rule ID / likely driver:** `{inc['likely_driver']}`")
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
