from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.incident_workflow_store import (
    add_note,
    get_notes,
    get_record,
    merge_workflow_rows,
    records_dataframe_rows,
    upsert_record,
    workflow_store_path,
)
from services.dashboard.performance_config import incident_workflow_cfg
from services.dashboard.query import combined_filter_sql, query_df_named, quote_sql

ALL_STATUSES = "All statuses"
ALL_OWNERS = "All owners"

def _safe_json(value: str) -> dict:
    try:
        return json.loads(value or "{}")
    except Exception:
        return {}

def _incident_scope_label(row: pd.Series | dict) -> str:
    return (
        f"{row.get('source_profile', 'unknown')} / "
        f"{row.get('region', 'unknown')} / "
        f"{row.get('server_id', 'unknown')} / "
        f"{row.get('map_id', 'unknown')} / "
        f"{row.get('zone_id', 'unknown')}"
    )

def _minutes_since(value) -> float:
    try:
        if hasattr(value, "to_pydatetime"):
            dt = value.to_pydatetime()
        elif isinstance(value, datetime):
            dt = value
        else:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 60.0
    except Exception:
        return 0.0

def _sla_state(row: pd.Series | dict) -> str:
    severity = str(row.get("severity", "info")).lower()
    status = str(row.get("workflow_status", "open")).lower()
    resolved_statuses = set(incident_workflow_cfg("escalation.resolved_statuses", ["resolved"]))
    if status in resolved_statuses:
        return "resolved"

    sla_minutes = dict(incident_workflow_cfg("severity_sla_minutes", {"critical": 30, "warning": 120, "info": 360}))
    budget = float(sla_minutes.get(severity, sla_minutes.get("info", 360)) or 360)
    age = _minutes_since(row.get("detected_at"))
    if age >= budget:
        return "breached"
    if age >= budget * 0.75:
        return "at_risk"
    return "within_sla"

def _status_filter(df: pd.DataFrame, selected_status: str, selected_owner: str) -> pd.DataFrame:
    out = df.copy()
    if selected_status != ALL_STATUSES:
        out = out[out["workflow_status"] == selected_status]
    if selected_owner != ALL_OWNERS:
        out = out[out["assigned_owner"] == selected_owner]
    return out

def _generate_report(incident: pd.Series, workflow: dict, notes: list[dict]) -> str:
    title = str(incident_workflow_cfg("report.default_report_title", "AegisTelemetry Incident Report"))
    include_evidence = bool(incident_workflow_cfg("report.include_evidence_json", True))
    include_notes = bool(incident_workflow_cfg("report.include_workflow_notes", True))
    evidence = _safe_json(str(incident.get("evidence_json", "{}")))

    lines = [
        f"# {title}",
        "",
        f"**Incident ID:** `{incident.get('incident_id', '')}`",
        f"**Detected:** {incident.get('detected_at', '')}",
        f"**Severity:** {incident.get('severity', '')}",
        f"**Workflow status:** {workflow.get('status', '')}",
        f"**Assigned owner:** {workflow.get('assigned_owner', '')}",
        f"**Scope:** {_incident_scope_label(incident)}",
        f"**Likely driver:** {incident.get('likely_driver', '')}",
        f"**Confidence:** {float(incident.get('confidence', 0) or 0):.2f}",
        "",
        "## Symptom",
        str(incident.get("symptom", "")),
        "",
        "## Player Impact",
        str(incident.get("player_impact", "")),
        "",
        "## Recommended Action",
        str(incident.get("recommended_action", "")),
        "",
        "## Current Next Action",
        str(workflow.get("next_action", "")),
        "",
        "## Resolution Summary",
        str(workflow.get("resolution_summary", "")) or "_Not resolved yet._",
    ]

    if include_notes:
        lines += ["", "## Analyst Notes"]
        if notes:
            for note in notes:
                lines += [
                    f"- **{note.get('created_at', '')} · {note.get('author', 'Analyst')}:** {note.get('note', '')}"
                ]
        else:
            lines += ["_No notes recorded._"]

    if include_evidence:
        lines += ["", "## Evidence JSON", "```json", json.dumps(evidence, indent=2), "```"]

    return "\n".join(lines)

def _incident_query(context: DashboardContext) -> pd.DataFrame:
    filters = context.filters
    incident_filter = combined_filter_sql(
        filters.selected_source_profile,
        filters.selected_region,
        filters.selected_server,
    )

    return query_df_named(
        "incident_workflow_incident_inventory",
        f"""
        SELECT
          detected_at,
          incident_id,
          severity,
          source_profile,
          region,
          server_id,
          map_id,
          zone_id,
          build_version,
          symptom,
          likely_driver,
          confidence,
          player_impact,
          recommended_action,
          evidence_json
        FROM incidents
        WHERE {filters.incident_time_filter}
          AND {incident_filter}
        ORDER BY
          multiIf(severity = 'critical', 1, severity = 'warning', 2, 3),
          detected_at DESC
        LIMIT {filters.max_table_rows}
        """,
        cache_policy="short",
    )

def render(context: DashboardContext) -> None:
    st.subheader("Incident Workflow")
    st.caption(
        "Assign owners, track investigation status, add analyst notes, and generate exportable incident reports."
    )

    incidents = _incident_query(context)

    if incidents.empty:
        st.info("No incidents found in the current filter window. Generate incident telemetry or widen the analysis window.")
        stored = pd.DataFrame(records_dataframe_rows())
        if not stored.empty:
            st.caption("Local workflow records exist, but none match current live incidents.")
            render_table(stored, height=300)
        return

    merged = pd.DataFrame(merge_workflow_rows(incidents.to_dict("records")))
    merged["sla_state"] = merged.apply(_sla_state, axis=1)
    merged["scope"] = merged.apply(_incident_scope_label, axis=1)

    status_options = [ALL_STATUSES] + list(incident_workflow_cfg("status_options", ["open", "investigating", "mitigated", "resolved", "deferred"]))
    owner_options = [ALL_OWNERS] + list(incident_workflow_cfg("owner_options", ["Unassigned"]))

    left_filter, right_filter = st.columns(2)
    with left_filter:
        selected_status = st.selectbox("Workflow status", status_options, index=0, key="aegis_incident_workflow_status_filter")
    with right_filter:
        selected_owner = st.selectbox("Assigned owner", owner_options, index=0, key="aegis_incident_workflow_owner_filter")

    visible = _status_filter(merged, selected_status, selected_owner)

    open_count = int((merged["workflow_status"] == "open").sum())
    investigating_count = int((merged["workflow_status"] == "investigating").sum())
    breached_count = int((merged["sla_state"] == "breached").sum())
    unassigned_count = int((merged["assigned_owner"] == "Unassigned").sum())
    resolved_count = int((merged["workflow_status"] == "resolved").sum())

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_paper_metric("Open", str(open_count))
    with k2:
        render_paper_metric("Investigating", str(investigating_count))
    with k3:
        render_paper_metric("SLA breached", str(breached_count))
    with k4:
        render_paper_metric("Unassigned", str(unassigned_count))
    with k5:
        render_paper_metric("Resolved", str(resolved_count))

    if visible.empty:
        st.info("No incidents match the selected workflow filters.")
        return

    st.markdown('<div class="pressure-section-title">Triage Queue</div>', unsafe_allow_html=True)

    queue_cols = [
        "detected_at",
        "incident_id",
        "severity",
        "workflow_status",
        "assigned_owner",
        "sla_state",
        "scope",
        "likely_driver",
        "confidence",
        "next_action",
    ]
    render_table(visible[[col for col in queue_cols if col in visible.columns]], height=380)

    selected_label_rows = []
    for _, row in visible.iterrows():
        selected_label_rows.append(
            f"{row['severity'].upper()} · {row['workflow_status']} · {row['incident_id']} · {row['likely_driver']} · {row['scope']}"
        )

    selected_label = st.selectbox(
        "Select incident to update",
        selected_label_rows,
        index=0,
        key="aegis_incident_workflow_selected_incident",
    )
    selected_index = selected_label_rows.index(selected_label)
    selected = visible.iloc[selected_index]
    incident_id = str(selected["incident_id"])
    workflow = get_record(incident_id)
    notes = get_notes(incident_id)

    st.markdown('<div class="pressure-section-title">Workflow Update</div>', unsafe_allow_html=True)

    form_col, evidence_col = st.columns([1.0, 1.1])

    with form_col:
        with st.form(f"incident_workflow_form_{incident_id}"):
            status_values = list(incident_workflow_cfg("status_options", ["open", "investigating", "mitigated", "resolved", "deferred"]))
            owner_values = list(incident_workflow_cfg("owner_options", ["Unassigned"]))

            status = st.selectbox(
                "Status",
                status_values,
                index=status_values.index(workflow.get("status", status_values[0])) if workflow.get("status") in status_values else 0,
            )
            owner = st.selectbox(
                "Assigned owner",
                owner_values,
                index=owner_values.index(workflow.get("assigned_owner", "Unassigned")) if workflow.get("assigned_owner") in owner_values else 0,
            )
            next_action = st.text_area(
                "Recommended next action",
                value=str(workflow.get("next_action", "")),
                height=100,
            )
            resolution_summary = st.text_area(
                "Resolution summary",
                value=str(workflow.get("resolution_summary", "")),
                height=110,
            )
            submitted = st.form_submit_button("Save workflow update")

        if submitted:
            upsert_record(
                incident_id,
                status=status,
                assigned_owner=owner,
                next_action=next_action,
                resolution_summary=resolution_summary,
            )
            st.success("Workflow update saved.")
            st.rerun()

        with st.form(f"incident_note_form_{incident_id}"):
            note_author = st.text_input("Note author", value="Analyst")
            note_text = st.text_area("Add analyst note", height=120)
            note_submit = st.form_submit_button("Add note")

        if note_submit:
            note = add_note(incident_id, note_text, author=note_author)
            if note:
                st.success("Note added.")
                st.rerun()
            else:
                st.warning("Write a note before submitting.")

    with evidence_col:
        st.write(f"**Incident ID:** `{incident_id}`")
        st.write(f"**Detected:** {selected['detected_at']}")
        st.write(f"**Severity:** `{selected['severity']}`")
        st.write(f"**Likely driver:** `{selected['likely_driver']}`")
        st.write(f"**Confidence:** {float(selected['confidence']):.2f}")
        st.write(f"**Scope:** {selected['scope']}")
        st.write(f"**Symptom:** {selected['symptom']}")
        st.write(f"**Player impact:** {selected['player_impact']}")
        st.write(f"**Recommended action:** {selected['recommended_action']}")
        st.write(f"**Workflow store:** `{workflow_store_path()}`")

    st.markdown('<div class="pressure-section-title">Analyst Notes</div>', unsafe_allow_html=True)
    if notes:
        render_table(pd.DataFrame(notes), height=260)
    else:
        st.info("No analyst notes recorded for this incident yet.")

    st.markdown('<div class="pressure-section-title">Exportable Incident Report</div>', unsafe_allow_html=True)
    current_workflow = get_record(incident_id)
    report = _generate_report(selected, current_workflow, get_notes(incident_id))
    st.download_button(
        "Download incident report",
        data=report,
        file_name=f"incident_report_{incident_id}.md",
        mime="text/markdown",
    )
    with st.expander("Preview report", expanded=False):
        st.markdown(report)

    with st.expander("Evidence JSON", expanded=False):
        st.json(_safe_json(str(selected.get("evidence_json", "{}"))))
