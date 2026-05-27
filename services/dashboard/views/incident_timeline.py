from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from services.dashboard.charts import render_multi_metric_timeline, render_timeseries_chart
from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import combined_filter_sql, query_df, quote_sql

def safe_json_loads(value: str) -> dict:
    try:
        return json.loads(value)
    except Exception:
        return {}

def sql_dt(value: str) -> str:
    return f"parseDateTime64BestEffort({quote_sql(value)})"

def incident_label(row: pd.Series) -> str:
    return (
        f"{row['detected_at']} · {str(row['severity']).upper()} · "
        f"{row['likely_driver']} · {row['server_id']} · {row['zone_id']}"
    )

def first_time_where(df: pd.DataFrame, condition, label: str, detail_builder) -> dict[str, Any]:
    if df.empty:
        return {"stage": label, "time": "—", "details": "No timeline data available."}

    matched = df[condition(df)]
    if matched.empty:
        return {"stage": label, "time": "—", "details": "Signal not observed in replay window."}

    row = matched.iloc[0]
    return {
        "stage": label,
        "time": row.get("window_start", "—"),
        "details": detail_builder(row),
    }

def build_development_sequence(timeline: pd.DataFrame, selected_incident: pd.Series, evidence: dict) -> pd.DataFrame:
    if timeline.empty:
        return pd.DataFrame([
            {"stage": "Incident starts", "time": selected_incident.get("detected_at", "—"), "details": "No aggregate replay data found for this incident scope."}
        ])

    timeline = timeline.sort_values("window_start").copy()
    max_players = float(timeline["active_players"].max() or 0)
    max_subsystem_pressure = float(timeline["subsystem_pressure"].max() or 0)
    max_frame = float(timeline["server_frame_ms_p95"].max() or 0)
    max_impact = float(timeline["player_impact_events"].max() or 0)

    sequence = []

    incident_window = evidence.get("window_start") or selected_incident.get("detected_at", "—")
    sequence.append({
        "stage": "Incident starts",
        "time": incident_window,
        "details": (
            f"{selected_incident.get('severity', 'unknown')} incident triggered by "
            f"{selected_incident.get('likely_driver', 'unknown')} on "
            f"{selected_incident.get('server_id', 'unknown')} / {selected_incident.get('zone_id', 'unknown')}."
        ),
    })

    sequence.append(first_time_where(
        timeline,
        lambda df: df["active_players"] >= max(1, max_players * 0.75),
        "Player density rises",
        lambda row: f"active_players={int(row['active_players'])}; source_profile={row['source_profile']}; zone={row['zone_id']}",
    ))

    sequence.append(first_time_where(
        timeline,
        lambda df: df["subsystem_pressure"] >= max(1, max_subsystem_pressure * 0.70),
        "AoE / physics / network signal spikes",
        lambda row: (
            f"aoe_events={int(row['aoe_events'])}, physics_events={int(row['physics_events'])}, "
            f"replicated_objects_p95={float(row['replicated_objects_p95']):.0f}, "
            f"packet_out_kbps_p95={float(row.get('packet_out_kbps_p95', 0)):.1f}"
        ),
    ))

    sequence.append(first_time_where(
        timeline,
        lambda df: (df["server_frame_ms_p95"] >= 50) | (df["server_frame_ms_p95"] >= max(1, max_frame * 0.75)),
        "Server frame time degrades",
        lambda row: f"p95={float(row['server_frame_ms_p95']):.1f}ms; p99={float(row['server_frame_ms_p99']):.1f}ms; cpu_p95={float(row['cpu_p95']):.1f}%",
    ))

    sequence.append(first_time_where(
        timeline,
        lambda df: df["player_impact_events"] >= max(1, max_impact * 0.50),
        "Desync / rubberband impact appears",
        lambda row: f"desync={int(row['desync_events'])}; rubberband={int(row['rubberband_events'])}; packet_loss_p95={float(row['packet_loss_p95']):.2f}%",
    ))

    sequence.append({
        "stage": "Recommendation triggers",
        "time": selected_incident.get("detected_at", "—"),
        "details": selected_incident.get("recommended_action", "No recommendation text found."),
    })

    return pd.DataFrame(sequence)

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

    replay_minutes_before = st.selectbox("Minutes before incident", [5, 10, 15, 30, 60], index=2)
    replay_minutes_after = st.selectbox("Minutes after incident", [5, 10, 15, 30, 60], index=2)

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

    incident_options = {
        incident_label(row): index
        for index, row in incidents.iterrows()
    }
    selected_label = st.selectbox("Incident to replay", list(incident_options.keys()))
    selected_incident = incidents.loc[incident_options[selected_label]]
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

    timeline = timeline.copy()
    timeline["player_impact_events"] = timeline["desync_events"] + timeline["rubberband_events"]
    timeline["subsystem_pressure"] = (
        timeline["aoe_events"]
        + timeline["physics_events"]
        + (timeline["replicated_objects_p95"] / 100.0)
        + (timeline.get("packet_out_kbps_p95", 0) / 100.0)
        + timeline.get("ai_pathfinding_requests", 0)
    )

    st.markdown('<div class="section-label">Root-cause sequence</div>', unsafe_allow_html=True)
    sequence = build_development_sequence(timeline, selected_incident, evidence)
    render_table(sequence, height=300)

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
