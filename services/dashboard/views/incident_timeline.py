from __future__ import annotations

import json
import os

import pandas as pd
import streamlit as st

from aegis_common.timeline_stage_engine import (
    add_derived_timeline_metrics,
    build_timeline_sequence,
    get_active_timeline_stage_profile,
    load_timeline_stage_profiles,
)
from services.dashboard.charts import render_multi_metric_timeline
from services.dashboard.components import render_paper_metric, render_table, render_timeline_sequence_cards
from services.dashboard.context import DashboardContext
from services.dashboard.query import combined_filter_sql, query_df, quote_sql

DEFAULT_STAGE_PROFILE = os.getenv("TIMELINE_STAGE_PROFILE", "default_timeline_stages")
INCIDENT_SESSION_KEY = "incident_timeline_selected_incident_id"
PROFILE_SESSION_KEY = "incident_timeline_selected_stage_profile"
PROFILE_WIDGET_KEY = "incident_timeline_stage_profile_widget"
AUTO_FOLLOW_SESSION_KEY = "incident_timeline_auto_follow_latest"

def safe_json_loads(value: str) -> dict:
    try:
        return json.loads(value)
    except Exception:
        return {}

def sql_dt(value: str) -> str:
    return f"parseDateTime64BestEffort({quote_sql(value)})"

def incident_label_from_row(row: pd.Series) -> str:
    return (
        f"{row['detected_at']} · {str(row['severity']).upper()} · "
        f"{row['likely_driver']} · {row['server_id']} · {row['zone_id']}"
    )

def default_profile_index(profile_names: list[str]) -> int:
    """Choose the real default profile instead of the first alphabetic profile.

    The previous implementation sorted profiles alphabetically and used index 0.
    That meant `custom_timeline_stages_example` could be selected by default,
    causing every incident to show only the three example stages.
    """
    if DEFAULT_STAGE_PROFILE in profile_names:
        return profile_names.index(DEFAULT_STAGE_PROFILE)
    if "default_timeline_stages" in profile_names:
        return profile_names.index("default_timeline_stages")
    return 0

def stable_incident_id_selection(incidents: pd.DataFrame) -> str:
    """Return a stable incident_id selection across Streamlit reruns.

    Live refresh can insert newer incidents at the top of the dataframe. Using
    index=0 or a non-keyed label selectbox causes the selected incident to jump
    to the newest option. This function keeps the previously selected incident_id
    while it remains available.
    """
    incident_ids = incidents["incident_id"].astype(str).tolist()
    if not incident_ids:
        return ""

    auto_follow_latest = st.checkbox(
        "Auto-follow latest incident",
        value=st.session_state.get(AUTO_FOLLOW_SESSION_KEY, False),
        key=AUTO_FOLLOW_SESSION_KEY,
        help="When enabled, the replay selector follows the newest incident after each refresh. Keep this off to pin the selected incident while live refresh is running.",
    )

    if auto_follow_latest:
        st.session_state[INCIDENT_SESSION_KEY] = incident_ids[0]
    else:
        previous = st.session_state.get(INCIDENT_SESSION_KEY)
        if previous not in incident_ids:
            st.session_state[INCIDENT_SESSION_KEY] = incident_ids[0]

    selected_id = st.selectbox(
        "Incident to replay",
        incident_ids,
        index=incident_ids.index(st.session_state[INCIDENT_SESSION_KEY]),
        key=INCIDENT_SESSION_KEY,
        format_func=lambda incident_id: incident_label_from_row(
            incidents[incidents["incident_id"].astype(str) == str(incident_id)].iloc[0]
        ),
    )

    return str(selected_id)

def render_incident_scope(selected_incident: pd.Series, evidence: dict) -> None:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_paper_metric("Severity", str(selected_incident.get("severity", "—")).upper())
    with c2:
        render_paper_metric("Rule ID", str(selected_incident.get("likely_driver", "—")))
    with c3:
        render_paper_metric("Source", str(selected_incident.get("source_profile", "—")))
    with c4:
        render_paper_metric("Server", str(selected_incident.get("server_id", "—")))
    with c5:
        render_paper_metric("Zone", str(selected_incident.get("zone_id", "—")))

    st.info(
        f"Map `{selected_incident.get('map_id', 'unknown')}` · "
        f"Region `{selected_incident.get('region', 'unknown')}` · "
        f"Build `{selected_incident.get('build_version', 'unknown')}` · "
        f"Incident window `{evidence.get('window_start', 'unknown')}` → `{evidence.get('window_end', 'unknown')}`"
    )

def render(context: DashboardContext) -> None:
    filters = context.filters
    st.subheader("Historical Incident Replay and Root-Cause Timeline")
    st.caption("Replay how a detected incident developed before, during, and after the trigger window for the same source/server/map/zone.")

    stage_profiles = load_timeline_stage_profiles()
    profile_names = sorted(stage_profiles.keys()) or ["default_timeline_stages"]

    # Keep the selected profile stable without writing to the same key used by
    # the selectbox widget. Writing to the widget key and also passing a default
    # value/index causes Streamlit's warning:
    # "The widget with key ... was created with a default value but also had its
    # value set via the Session State API."
    preferred_profile = st.session_state.get(PROFILE_SESSION_KEY)
    if preferred_profile not in profile_names:
        preferred_profile = profile_names[default_profile_index(profile_names)]

    controls_col1, controls_col2, controls_col3 = st.columns(3)
    with controls_col1:
        replay_minutes_before = st.selectbox("Minutes before incident", [5, 10, 15, 30, 60], index=2)
    with controls_col2:
        replay_minutes_after = st.selectbox("Minutes after incident", [5, 10, 15, 30, 60], index=2)
    with controls_col3:
        selected_stage_profile_name = st.selectbox(
            "Timeline stage profile",
            profile_names,
            index=profile_names.index(preferred_profile),
            key=PROFILE_WIDGET_KEY,
            help="Defaults to default_timeline_stages. Custom/example profiles are available for testing but are not selected automatically.",
        )
        st.session_state[PROFILE_SESSION_KEY] = selected_stage_profile_name

    stage_profile = stage_profiles.get(selected_stage_profile_name) or get_active_timeline_stage_profile()

    incident_filter = combined_filter_sql(
        filters.selected_source_profile,
        filters.selected_region,
        filters.selected_server,
    )

    incidents = query_df(f"""
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
        ORDER BY detected_at DESC
        LIMIT 300
    """)

    if incidents.empty:
        st.info("No incidents are available for the current source/region/server/time-window filters.")
        return

    incidents = incidents.copy()
    incidents["incident_id"] = incidents["incident_id"].astype(str)

    selected_incident_id = stable_incident_id_selection(incidents)
    selected_incident = incidents[incidents["incident_id"] == selected_incident_id].iloc[0]
    evidence = safe_json_loads(selected_incident["evidence_json"])

    render_incident_scope(selected_incident, evidence)

    incident_anchor = evidence.get("window_start") or str(selected_incident["detected_at"])
    anchor_sql = sql_dt(str(incident_anchor))

    timeline = query_df(f"""
        SELECT
          window_start,
          window_end,
          source_profile,
          region,
          server_id,
          map_id,
          zone_id,
          build_version,
          events,
          active_players,
          ability_casts,
          aoe_events,
          physics_events,
          replicated_objects_p95,
          cpu_p95,
          server_frame_ms_avg,
          server_frame_ms_p95,
          server_frame_ms_p99,
          packet_loss_p95,
          packet_out_kbps_p95,
          memory_mb_p95,
          ai_agents_active_p95,
          ai_pathfinding_requests,
          matchmaking_events,
          matchmaking_queue_p95,
          top_ability_id,
          top_event_type,
          desync_events,
          rubberband_events,
          hot_zone_risk_score
        FROM agg_zone_30s
        WHERE window_start >= {anchor_sql} - INTERVAL {int(replay_minutes_before)} MINUTE
          AND window_start <= {anchor_sql} + INTERVAL {int(replay_minutes_after)} MINUTE
          AND source_profile = {quote_sql(str(selected_incident['source_profile']))}
          AND region = {quote_sql(str(selected_incident['region']))}
          AND server_id = {quote_sql(str(selected_incident['server_id']))}
          AND map_id = {quote_sql(str(selected_incident['map_id']))}
          AND zone_id = {quote_sql(str(selected_incident['zone_id']))}
        ORDER BY window_start ASC
        LIMIT 2000
    """)

    if timeline.empty:
        st.warning("No aggregate timeline data found for the selected incident scope.")
        return

    timeline = add_derived_timeline_metrics(timeline)

    st.markdown(
        f"<div class='timeline-note'>Using timeline stage profile "
        f"<b>{stage_profile.get('profile_name', selected_stage_profile_name)}</b> "
        f"for incident rule <b>{selected_incident.get('likely_driver', 'unknown')}</b>.</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Root-cause sequence</div>', unsafe_allow_html=True)
    sequence = build_timeline_sequence(
        timeline,
        incident=selected_incident.to_dict(),
        evidence=evidence,
        profile=stage_profile,
    )
    render_timeline_sequence_cards(sequence)

    with st.expander("Root-cause sequence table"):
        render_table(sequence, height=340)

    st.markdown('<div class="section-label">Metric timeline before / during / after incident</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.write("Density and server frame pressure")
        render_multi_metric_timeline(
            timeline,
            x="window_start",
            metrics=["active_players", "server_frame_ms_p95", "server_frame_ms_p99", "hot_zone_risk_score"],
            height=330,
            title="Density / frame / risk",
        )
    with chart_col2:
        st.write("Subsystem pressure signals")
        render_multi_metric_timeline(
            timeline,
            x="window_start",
            metrics=["aoe_events", "physics_events", "replicated_objects_p95", "packet_out_kbps_p95", "ai_pathfinding_requests"],
            height=330,
            title="Subsystem pressure",
        )

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.write("Network and player impact")
        render_multi_metric_timeline(
            timeline,
            x="window_start",
            metrics=["packet_loss_p95", "desync_events", "rubberband_events", "player_impact_events"],
            height=330,
            title="Network / impact",
        )
    with chart_col4:
        st.write("Memory, CPU, and AI")
        render_multi_metric_timeline(
            timeline,
            x="window_start",
            metrics=["cpu_p95", "memory_mb_p95", "ai_agents_active_p95", "matchmaking_queue_p95"],
            height=330,
            title="CPU / memory / AI",
        )

    st.markdown('<div class="section-label">Top event and ability context</div>', unsafe_allow_html=True)
    context_table = timeline[[
        "window_start",
        "top_event_type",
        "top_ability_id",
        "events",
        "ability_casts",
        "aoe_events",
        "physics_events",
        "active_players",
        "server_frame_ms_p95",
        "hot_zone_risk_score",
    ]].sort_values("window_start", ascending=True)
    render_table(context_table, height=360)

    st.markdown('<div class="section-label">Recommendation changes over replay window</div>', unsafe_allow_html=True)
    related_incidents = query_df(f"""
        SELECT
          detected_at,
          severity,
          likely_driver,
          confidence,
          symptom,
          recommended_action
        FROM incidents
        WHERE detected_at >= {anchor_sql} - INTERVAL {int(replay_minutes_before)} MINUTE
          AND detected_at <= {anchor_sql} + INTERVAL {int(replay_minutes_after)} MINUTE
          AND source_profile = {quote_sql(str(selected_incident['source_profile']))}
          AND region = {quote_sql(str(selected_incident['region']))}
          AND server_id = {quote_sql(str(selected_incident['server_id']))}
          AND map_id = {quote_sql(str(selected_incident['map_id']))}
          AND zone_id = {quote_sql(str(selected_incident['zone_id']))}
        ORDER BY detected_at ASC
        LIMIT 300
    """)
    if related_incidents.empty:
        st.info("No additional recommendation changes were detected in this replay window.")
    else:
        render_table(related_incidents, height=360)

    with st.expander("Selected incident evidence payload"):
        st.json(evidence)

    with st.expander("Active timeline stage profile"):
        st.json(stage_profile)
