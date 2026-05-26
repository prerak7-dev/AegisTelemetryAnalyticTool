from __future__ import annotations

import json
import os

import clickhouse_connect
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "aegis_telemetry")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "aegis_dev_password")

st.set_page_config(page_title="AegisTelemetry", layout="wide")

@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        database=CLICKHOUSE_DATABASE,
        username="default",
        password=CLICKHOUSE_PASSWORD,
    )

def query_df(sql: str) -> pd.DataFrame:
    return get_client().query_df(sql)

def safe_json_loads(value: str) -> dict:
    try:
        return json.loads(value)
    except Exception:
        return {}

st.title("AegisTelemetry — Real-Time Gameplay Performance Intelligence")
st.caption("Streaming telemetry analytics for high-traffic live-service games.")

refresh = st.toggle("Auto-refresh every 5 seconds", value=True)
if refresh:
    st_autorefresh(interval=5000, key="refresh")

try:
    latest = query_df("""
        SELECT
          max(window_start) AS latest_window,
          count() AS aggregate_rows,
          max(hot_zone_risk_score) AS max_risk,
          max(server_frame_ms_p95) AS max_p95_frame
        FROM agg_zone_30s
    """)
except Exception as exc:
    st.error(f"Could not connect to ClickHouse yet: {exc}")
    st.stop()

row = latest.iloc[0] if not latest.empty else {}
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest window", str(row.get("latest_window", "—")))
col2.metric("Aggregate rows", int(row.get("aggregate_rows", 0) or 0))
col3.metric("Max hot-zone risk", f"{float(row.get('max_risk', 0) or 0):.1f}")
col4.metric("Max p95 frame", f"{float(row.get('max_p95_frame', 0) or 0):.1f} ms")

tab_command, tab_incidents, tab_quality, tab_scaling = st.tabs([
    "Command Center",
    "Incident Deep Dive",
    "Data Quality",
    "Scaling Readiness",
])

with tab_command:
    left, right = st.columns([1.3, 1.0])

    with left:
        st.subheader("Realtime server frame pressure")
        perf = query_df("""
            SELECT
              window_start,
              region,
              quantile(0.95)(server_frame_ms_p95) AS p95_frame
            FROM agg_zone_30s
            WHERE window_start >= now() - INTERVAL 30 MINUTE
            GROUP BY window_start, region
            ORDER BY window_start ASC
        """)
        if perf.empty:
            st.info("No aggregate data yet. Start the simulator.")
        else:
            st.line_chart(perf, x="window_start", y="p95_frame", color="region")

    with right:
        st.subheader("Worst hot zones")
        hotzones = query_df("""
            SELECT
              window_start,
              region,
              server_id,
              map_id,
              zone_id,
              active_players,
              aoe_events,
              physics_events,
              replicated_objects_p95,
              server_frame_ms_p95,
              server_frame_ms_p99,
              packet_loss_p95,
              desync_events,
              rubberband_events,
              hot_zone_risk_score
            FROM agg_zone_30s
            ORDER BY window_start DESC, hot_zone_risk_score DESC
            LIMIT 20
        """)
        if hotzones.empty:
            st.info("No hot zone rows yet.")
        else:
            st.dataframe(hotzones, use_container_width=True, hide_index=True)

    st.subheader("Regional risk summary")
    regional = query_df("""
        SELECT
          region,
          max(hot_zone_risk_score) AS max_risk,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(active_players) AS peak_local_players,
          sum(aoe_events) AS aoe_events,
          sum(rubberband_events) AS rubberband_events,
          sum(desync_events) AS desync_events
        FROM agg_zone_30s
        WHERE window_start >= now() - INTERVAL 30 MINUTE
        GROUP BY region
        ORDER BY max_risk DESC
    """)
    if not regional.empty:
        st.dataframe(regional, use_container_width=True, hide_index=True)

with tab_incidents:
    st.subheader("Live incidents and evidence-backed recommendations")
    incidents = query_df("""
        SELECT
          detected_at,
          severity,
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
        ORDER BY detected_at DESC
        LIMIT 25
    """)

    if incidents.empty:
        st.info("No incidents detected yet.")
    else:
        for _, inc in incidents.iterrows():
            with st.expander(f"{inc['severity'].upper()} · {inc['region']} · {inc['zone_id']} · {inc['likely_driver']}"):
                st.write(f"**Detected:** {inc['detected_at']}")
                st.write(f"**Server:** `{inc['server_id']}`")
                st.write(f"**Symptom:** {inc['symptom']}")
                st.write(f"**Confidence:** {float(inc['confidence']):.2f}")
                st.write(f"**Player impact:** {inc['player_impact']}")
                st.write(f"**Recommended action:** {inc['recommended_action']}")

                evidence = safe_json_loads(inc["evidence_json"])
                ranked = evidence.get("ranked_driver_scores", [])
                if ranked:
                    st.write("**Ranked attribution signals:**")
                    st.dataframe(pd.DataFrame(ranked), use_container_width=True, hide_index=True)

                st.write("**Evidence payload:**")
                st.json(evidence)

with tab_quality:
    st.subheader("Telemetry data quality")
    quality_summary = query_df("""
        SELECT
          count() AS failed_events,
          max(failed_at) AS latest_failure
        FROM data_quality_failures
    """)
    qrow = quality_summary.iloc[0] if not quality_summary.empty else {}
    q1, q2 = st.columns(2)
    q1.metric("Validation failures", int(qrow.get("failed_events", 0) or 0))
    q2.metric("Latest failure", str(qrow.get("latest_failure", "—")))

    failure_breakdown = query_df("""
        SELECT
          category,
          event_type,
          region,
          count() AS failures
        FROM data_quality_failures
        WHERE failed_at >= now() - INTERVAL 60 MINUTE
        GROUP BY category, event_type, region
        ORDER BY failures DESC
        LIMIT 50
    """)
    if failure_breakdown.empty:
        st.success("No validation failures captured in the last hour.")
    else:
        st.dataframe(failure_breakdown, use_container_width=True, hide_index=True)

    recent_failures = query_df("""
        SELECT
          failed_at,
          event_id,
          error,
          category,
          event_type,
          region,
          server_id
        FROM data_quality_failures
        ORDER BY failed_at DESC
        LIMIT 50
    """)
    if not recent_failures.empty:
        st.write("Recent validation failures")
        st.dataframe(recent_failures, use_container_width=True, hide_index=True)

with tab_scaling:
    st.subheader("Regional scaling readiness")
    st.caption("This is a portfolio-safe simulator view: it recommends shard pressure actions from telemetry aggregates without touching real cloud infrastructure.")

    scaling = query_df("""
        SELECT
          region,
          max(active_players) AS peak_local_players,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(hot_zone_risk_score) AS max_risk,
          sum(rubberband_events + desync_events) AS player_impact_events,
          countDistinct(server_id) AS observed_servers
        FROM agg_zone_30s
        WHERE window_start >= now() - INTERVAL 30 MINUTE
        GROUP BY region
        ORDER BY max_risk DESC
    """)

    if scaling.empty:
        st.info("No scaling data yet.")
    else:
        scaling = scaling.copy()
        scaling["recommended_action"] = scaling.apply(
            lambda row: "Add shards / split hot zones" if row["max_risk"] >= 75 or row["p95_frame"] >= 55
            else "Monitor" if row["max_risk"] >= 50
            else "No action",
            axis=1,
        )
        scaling["estimated_extra_shards"] = scaling.apply(
            lambda row: max(0, int((float(row["peak_local_players"]) - 120) // 40) + (2 if row["max_risk"] >= 80 else 0)),
            axis=1,
        )
        st.dataframe(scaling, use_container_width=True, hide_index=True)
