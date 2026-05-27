from __future__ import annotations

import streamlit as st

from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import query_df

def render(context: DashboardContext) -> None:
    filters = context.filters
    st.subheader("Regional/server scaling readiness")
    st.caption("This simulator view recommends shard/server pressure actions from telemetry aggregates without touching real cloud infrastructure.")

    scaling = query_df(f"""
        SELECT
          source_profile,
          region,
          server_id,
          max(active_players) AS peak_local_players,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(hot_zone_risk_score) AS max_risk,
          sum(rubberband_events + desync_events) AS player_impact_events,
          count() AS observed_windows
        FROM agg_zone_30s
        WHERE {filters.time_filter}
          AND {context.active_filter}
        GROUP BY source_profile, region, server_id
        ORDER BY max_risk DESC
        LIMIT {filters.max_table_rows}
    """)

    if scaling.empty:
        st.info("No scaling data for the current filter.")
        return

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

    render_table(scaling, height=380)
