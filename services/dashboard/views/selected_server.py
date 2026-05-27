from __future__ import annotations

import streamlit as st

from services.dashboard.charts import render_timeseries_chart
from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.config import ALL_SERVERS
from services.dashboard.context import DashboardContext
from services.dashboard.query import query_df, server_filter_sql, source_filter_sql

def render(context: DashboardContext) -> None:
    filters = context.filters
    st.subheader("Selected server drilldown")
    st.caption("Per-server investigation surface for zone pressure, frame spikes, and player-impact signals.")

    if filters.selected_server == ALL_SERVERS:
        st.warning("Choose a specific server in the sidebar to view per-server drilldown analytics.")
        return

    timeline = query_df(f"""
        SELECT
          window_start,
          source_profile,
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
        WHERE {filters.time_filter}
          AND {source_filter_sql(filters.selected_source_profile)}
          AND {server_filter_sql(filters.selected_server)}
        GROUP BY window_start, source_profile, zone_id
        ORDER BY window_start ASC, hot_zone_risk_score DESC
        LIMIT 1000
    """)

    if timeline.empty:
        st.info("No drilldown data for this server in the selected time window.")
        return

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_paper_metric("Peak local players", str(int(timeline["active_players"].max())))
    with k2:
        render_paper_metric("Max p95 frame", f"{float(timeline['server_frame_ms_p95'].max()):.1f} ms")
    with k3:
        render_paper_metric("Max risk", f"{float(timeline['hot_zone_risk_score'].max()):.1f}")
    with k4:
        render_paper_metric("Impact events", str(int((timeline["desync_events"] + timeline["rubberband_events"]).sum())))

    timeline["series"] = timeline["source_profile"].astype(str) + " / " + timeline["zone_id"].astype(str)

    c1, c2 = st.columns(2)
    with c1:
        st.write("Server frame time by source/zone")
        render_timeseries_chart(
            timeline,
            x="window_start",
            y="server_frame_ms_p95",
            series="series",
            height=320,
            y_title="P95 server frame (ms)",
        )
    with c2:
        st.write("Hot-zone risk by source/zone")
        render_timeseries_chart(
            timeline,
            x="window_start",
            y="hot_zone_risk_score",
            series="series",
            height=320,
            y_title="Hot-zone risk",
        )

    st.write("Per-window server/zone details")
    render_table(
        timeline.sort_values(["window_start", "hot_zone_risk_score"], ascending=[False, False]).head(filters.max_table_rows),
        height=420,
    )

    st.subheader("Server-level pressure sources")
    pressure = query_df(f"""
        SELECT
          source_profile,
          zone_id,
          sum(aoe_events) AS aoe_events,
          sum(physics_events) AS physics_events,
          max(replicated_objects_p95) AS max_replicated_objects_p95,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(packet_loss_p95) AS max_packet_loss,
          sum(desync_events + rubberband_events) AS player_impact_events,
          max(hot_zone_risk_score) AS max_risk
        FROM agg_zone_30s
        WHERE {filters.time_filter}
          AND {source_filter_sql(filters.selected_source_profile)}
          AND {server_filter_sql(filters.selected_server)}
        GROUP BY source_profile, zone_id
        ORDER BY max_risk DESC
        LIMIT {filters.max_table_rows}
    """)
    render_table(pressure, height=320)
