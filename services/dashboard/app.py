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

def quote_sql(value: str) -> str:
    """Small helper for safe dashboard-side literal quoting."""
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"

def server_filter_sql(selected_server: str, table_alias: str | None = None) -> str:
    if selected_server == "All servers":
        return "1 = 1"
    prefix = f"{table_alias}." if table_alias else ""
    return f"{prefix}server_id = {quote_sql(selected_server)}"

def region_filter_sql(selected_region: str, table_alias: str | None = None) -> str:
    if selected_region == "All regions":
        return "1 = 1"
    prefix = f"{table_alias}." if table_alias else ""
    return f"{prefix}region = {quote_sql(selected_region)}"

def combined_filter_sql(selected_region: str, selected_server: str, table_alias: str | None = None) -> str:
    return f"{region_filter_sql(selected_region, table_alias)} AND {server_filter_sql(selected_server, table_alias)}"

st.title("AegisTelemetry — Real-Time Gameplay Performance Intelligence")
st.caption("Streaming telemetry analytics for high-traffic live-service games.")

refresh = st.sidebar.toggle("Auto-refresh every 5 seconds", value=True)
if refresh:
    st_autorefresh(interval=5000, key="refresh")

# -------------------------------------------------------------------
# Sidebar discovery filters
# -------------------------------------------------------------------
try:
    server_inventory = query_df("""
        SELECT
          server_id,
          anyLast(region) AS region,
          anyLast(map_id) AS latest_map,
          max(window_start) AS last_seen,
          max(hot_zone_risk_score) AS max_risk,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(active_players) AS peak_local_players,
          count() AS aggregate_windows
        FROM agg_zone_30s
        GROUP BY server_id
        ORDER BY last_seen DESC, max_risk DESC
        LIMIT 500
    """)
except Exception as exc:
    st.error(f"Could not connect to ClickHouse yet: {exc}")
    st.stop()

st.sidebar.header("Server Explorer")

regions = ["All regions"]
if not server_inventory.empty and "region" in server_inventory.columns:
    regions += sorted([str(x) for x in server_inventory["region"].dropna().unique().tolist()])

selected_region = st.sidebar.selectbox("Region", regions, index=0)

if selected_region == "All regions":
    visible_inventory = server_inventory.copy()
else:
    visible_inventory = server_inventory[server_inventory["region"] == selected_region].copy()

server_options = ["All servers"]
if not visible_inventory.empty:
    server_options += visible_inventory["server_id"].dropna().astype(str).tolist()

selected_server = st.sidebar.selectbox("Server", server_options, index=0)

time_window_minutes = st.sidebar.selectbox(
    "Analysis window",
    [15, 30, 60, 180, 360],
    index=1,
    format_func=lambda x: f"Last {x} minutes",
)

active_filter = combined_filter_sql(selected_region, selected_server)
time_filter = f"window_start >= now() - INTERVAL {int(time_window_minutes)} MINUTE"

st.sidebar.divider()
st.sidebar.caption("Available servers are discovered from the live aggregate table. Generate traffic first if this list is empty.")

if visible_inventory.empty:
    st.sidebar.info("No servers observed yet.")
else:
    st.sidebar.dataframe(
        visible_inventory[[
            "server_id",
            "region",
            "latest_map",
            "last_seen",
            "max_risk",
            "p95_frame",
            "peak_local_players",
        ]].head(25),
        use_container_width=True,
        hide_index=True,
    )

# -------------------------------------------------------------------
# Global/selected-server KPIs
# -------------------------------------------------------------------
latest = query_df(f"""
    SELECT
      max(window_start) AS latest_window,
      count() AS aggregate_rows,
      countDistinct(server_id) AS observed_servers,
      max(hot_zone_risk_score) AS max_risk,
      max(server_frame_ms_p95) AS max_p95_frame,
      sum(rubberband_events + desync_events) AS player_impact_events
    FROM agg_zone_30s
    WHERE {time_filter}
      AND {active_filter}
""")

row = latest.iloc[0] if not latest.empty else {}
header_label = selected_server if selected_server != "All servers" else "Fleet"
st.subheader(f"{header_label} Analytics")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Latest window", str(row.get("latest_window", "—")))
col2.metric("Observed servers", int(row.get("observed_servers", 0) or 0))
col3.metric("Aggregate rows", int(row.get("aggregate_rows", 0) or 0))
col4.metric("Max risk", f"{float(row.get('max_risk', 0) or 0):.1f}")
col5.metric("Player impact events", int(row.get("player_impact_events", 0) or 0))

if selected_server != "All servers" and not visible_inventory.empty:
    selected_meta = visible_inventory[visible_inventory["server_id"] == selected_server]
    if not selected_meta.empty:
        meta = selected_meta.iloc[0]
        st.info(
            f"Selected server `{selected_server}` · Region: `{meta.get('region', 'unknown')}` · "
            f"Latest map: `{meta.get('latest_map', 'unknown')}` · Last seen: `{meta.get('last_seen', '—')}`"
        )

tab_command, tab_server, tab_incidents, tab_quality, tab_scaling = st.tabs([
    "Command Center",
    "Selected Server Analytics",
    "Incident Deep Dive",
    "Data Quality",
    "Scaling Readiness",
])

with tab_command:
    left, right = st.columns([1.3, 1.0])

    with left:
        st.subheader("Realtime server frame pressure")
        perf = query_df(f"""
            SELECT
              window_start,
              region,
              quantile(0.95)(server_frame_ms_p95) AS p95_frame
            FROM agg_zone_30s
            WHERE {time_filter}
              AND {active_filter}
            GROUP BY window_start, region
            ORDER BY window_start ASC
        """)
        if perf.empty:
            st.info("No aggregate data for the current filter. Start the simulator or choose All servers.")
        else:
            st.line_chart(perf, x="window_start", y="p95_frame", color="region")

    with right:
        st.subheader("Worst hot zones")
        hotzones = query_df(f"""
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
            WHERE {time_filter}
              AND {active_filter}
            ORDER BY window_start DESC, hot_zone_risk_score DESC
            LIMIT 50
        """)
        if hotzones.empty:
            st.info("No hot-zone rows for the current filter.")
        else:
            st.dataframe(hotzones, use_container_width=True, hide_index=True)

    st.subheader("Regional risk summary")
    regional = query_df(f"""
        SELECT
          region,
          countDistinct(server_id) AS observed_servers,
          max(hot_zone_risk_score) AS max_risk,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(active_players) AS peak_local_players,
          sum(aoe_events) AS aoe_events,
          sum(rubberband_events) AS rubberband_events,
          sum(desync_events) AS desync_events
        FROM agg_zone_30s
        WHERE {time_filter}
          AND {active_filter}
        GROUP BY region
        ORDER BY max_risk DESC
    """)
    if regional.empty:
        st.info("No regional summary for the current filter.")
    else:
        st.dataframe(regional, use_container_width=True, hide_index=True)

with tab_server:
    st.subheader("Selected server drilldown")

    if selected_server == "All servers":
        st.warning("Choose a specific server in the sidebar to view per-server drilldown analytics.")
    else:
        timeline = query_df(f"""
            SELECT
              window_start,
              zone_id,
              max(active_players) AS active_players,
              sum(aoe_events) AS aoe_events,
              sum(physics_events) AS physics_events,
              max(replicated_objects_p95) AS replicated_objects_p95,
              quantile(0.95)(server_frame_ms_p95) AS server_frame_ms_p95,
              max(server_frame_ms_p99) AS server_frame_ms_p99,
              max(packet_loss_p95) AS packet_loss_p95,
              sum(desync_events) AS desync_events,
              sum(rubberband_events) AS rubberband_events,
              max(hot_zone_risk_score) AS hot_zone_risk_score
            FROM agg_zone_30s
            WHERE {time_filter}
              AND {server_filter_sql(selected_server)}
            GROUP BY window_start, zone_id
            ORDER BY window_start ASC, hot_zone_risk_score DESC
        """)

        if timeline.empty:
            st.info("No drilldown data for this server in the selected time window.")
        else:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Peak local players", int(timeline["active_players"].max()))
            k2.metric("Max p95 frame", f"{float(timeline['server_frame_ms_p95'].max()):.1f} ms")
            k3.metric("Max risk", f"{float(timeline['hot_zone_risk_score'].max()):.1f}")
            k4.metric("Impact events", int((timeline["desync_events"] + timeline["rubberband_events"]).sum()))

            st.write("Server frame time by zone")
            st.line_chart(timeline, x="window_start", y="server_frame_ms_p95", color="zone_id")

            st.write("Hot-zone risk by zone")
            st.line_chart(timeline, x="window_start", y="hot_zone_risk_score", color="zone_id")

            st.write("Per-window server/zone details")
            st.dataframe(timeline.sort_values(["window_start", "hot_zone_risk_score"], ascending=[False, False]), use_container_width=True, hide_index=True)

            st.subheader("Server-level likely pressure sources")
            pressure = query_df(f"""
                SELECT
                  zone_id,
                  sum(aoe_events) AS aoe_events,
                  sum(physics_events) AS physics_events,
                  max(replicated_objects_p95) AS max_replicated_objects_p95,
                  quantile(0.95)(server_frame_ms_p95) AS p95_frame,
                  max(packet_loss_p95) AS max_packet_loss,
                  sum(desync_events + rubberband_events) AS player_impact_events,
                  max(hot_zone_risk_score) AS max_risk
                FROM agg_zone_30s
                WHERE {time_filter}
                  AND {server_filter_sql(selected_server)}
                GROUP BY zone_id
                ORDER BY max_risk DESC
            """)
            st.dataframe(pressure, use_container_width=True, hide_index=True)

with tab_incidents:
    st.subheader("Live incidents and evidence-backed recommendations")
    incident_time_filter = f"detected_at >= now() - INTERVAL {int(time_window_minutes)} MINUTE"
    incident_filter = combined_filter_sql(selected_region, selected_server)

    incidents = query_df(f"""
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
        WHERE {incident_time_filter}
          AND {incident_filter}
        ORDER BY detected_at DESC
        LIMIT 50
    """)

    if incidents.empty:
        st.info("No incidents detected for the current filter.")
    else:
        for _, inc in incidents.iterrows():
            with st.expander(f"{inc['severity'].upper()} · {inc['server_id']} · {inc['zone_id']} · {inc['likely_driver']}"):
                st.write(f"**Detected:** {inc['detected_at']}")
                st.write(f"**Region:** `{inc['region']}`")
                st.write(f"**Server:** `{inc['server_id']}`")
                st.write(f"**Map/Zone:** `{inc['map_id']} / {inc['zone_id']}`")
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
    quality_time_filter = f"failed_at >= now() - INTERVAL {int(time_window_minutes)} MINUTE"
    quality_filter = combined_filter_sql(selected_region, selected_server)

    quality_summary = query_df(f"""
        SELECT
          count() AS failed_events,
          max(failed_at) AS latest_failure,
          countDistinct(server_id) AS affected_servers
        FROM data_quality_failures
        WHERE {quality_time_filter}
          AND {quality_filter}
    """)
    qrow = quality_summary.iloc[0] if not quality_summary.empty else {}
    q1, q2, q3 = st.columns(3)
    q1.metric("Validation failures", int(qrow.get("failed_events", 0) or 0))
    q2.metric("Affected servers", int(qrow.get("affected_servers", 0) or 0))
    q3.metric("Latest failure", str(qrow.get("latest_failure", "—")))

    failure_breakdown = query_df(f"""
        SELECT
          category,
          event_type,
          region,
          server_id,
          count() AS failures
        FROM data_quality_failures
        WHERE {quality_time_filter}
          AND {quality_filter}
        GROUP BY category, event_type, region, server_id
        ORDER BY failures DESC
        LIMIT 100
    """)
    if failure_breakdown.empty:
        st.success("No validation failures captured for the current filter.")
    else:
        st.dataframe(failure_breakdown, use_container_width=True, hide_index=True)

    recent_failures = query_df(f"""
        SELECT
          failed_at,
          event_id,
          error,
          category,
          event_type,
          region,
          server_id
        FROM data_quality_failures
        WHERE {quality_time_filter}
          AND {quality_filter}
        ORDER BY failed_at DESC
        LIMIT 100
    """)
    if not recent_failures.empty:
        st.write("Recent validation failures")
        st.dataframe(recent_failures, use_container_width=True, hide_index=True)

with tab_scaling:
    st.subheader("Regional/server scaling readiness")
    st.caption("This simulator view recommends shard/server pressure actions from telemetry aggregates without touching real cloud infrastructure.")

    scaling = query_df(f"""
        SELECT
          region,
          server_id,
          max(active_players) AS peak_local_players,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(hot_zone_risk_score) AS max_risk,
          sum(rubberband_events + desync_events) AS player_impact_events,
          count() AS observed_windows
        FROM agg_zone_30s
        WHERE {time_filter}
          AND {active_filter}
        GROUP BY region, server_id
        ORDER BY max_risk DESC
        LIMIT 100
    """)

    if scaling.empty:
        st.info("No scaling data for the current filter.")
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
