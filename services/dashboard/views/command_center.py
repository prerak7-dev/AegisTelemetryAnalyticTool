from __future__ import annotations

import streamlit as st

from services.dashboard.charts import render_timeseries_chart
from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import query_df

def render(context: DashboardContext) -> None:
    filters = context.filters
    left, right = st.columns([1.3, 1.0])

    with left:
        st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
        st.subheader("Realtime server frame pressure")
        st.caption("P95 server frame time by source profile and region. Use this to spot live service degradation at a glance.")
        perf = query_df(f"""
            SELECT
              window_start,
              source_profile,
              region,
              quantile(0.95)(server_frame_ms_p95) AS p95_frame
            FROM agg_zone_30s
            WHERE {filters.time_filter}
              AND {context.active_filter}
            GROUP BY window_start, source_profile, region
            ORDER BY window_start ASC
            LIMIT 900
        """)
        if not perf.empty:
            perf["series"] = perf["source_profile"].astype(str) + " / " + perf["region"].astype(str)
            render_timeseries_chart(
                perf,
                x="window_start",
                y="p95_frame",
                series="series",
                height=360,
                y_title="P95 server frame (ms)",
            )
        else:
            st.info("No aggregate data for the current filter.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
        st.subheader("Worst hot zones")
        st.caption("Highest-risk server/zone windows in the selected source, region, and server scope.")
        hotzones = query_df(f"""
            SELECT
              window_start,
              source_profile,
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
            WHERE {filters.time_filter}
              AND {context.active_filter}
            ORDER BY window_start DESC, hot_zone_risk_score DESC
            LIMIT {filters.max_table_rows}
        """)
        if hotzones.empty:
            st.info("No hot-zone rows for the current filter.")
        else:
            render_table(hotzones, height=420)
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Source + regional risk summary")
    st.caption("Executive fleet view: compare pressure across source schemas and regions.")
    regional = query_df(f"""
        SELECT
          source_profile,
          region,
          countDistinct(server_id) AS observed_servers,
          max(hot_zone_risk_score) AS max_risk,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(active_players) AS peak_local_players,
          sum(aoe_events) AS aoe_events,
          sum(rubberband_events) AS rubberband_events,
          sum(desync_events) AS desync_events
        FROM agg_zone_30s
        WHERE {filters.time_filter}
          AND {context.active_filter}
        GROUP BY source_profile, region
        ORDER BY max_risk DESC
        LIMIT {filters.max_table_rows}
    """)
    if regional.empty:
        st.info("No regional summary for the current filter.")
    else:
        render_table(regional, height=330)
