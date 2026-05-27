from __future__ import annotations

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from services.dashboard.config import (
    ALL_REGIONS,
    ALL_SERVERS,
    ALL_SOURCE_PROFILES,
    DashboardFilters,
    REFRESH_INTERVAL_SECONDS,
    TABLE_ROW_LIMITS,
    TIME_WINDOW_MINUTES,
)
from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import (
    clear_query_cache,
    combined_filter_sql,
    query_df,
    region_filter_sql,
    server_filter_sql,
    source_filter_sql,
)

def render_sidebar() -> DashboardContext:
    """Render sidebar controls and return normalized dashboard context."""

    st.sidebar.header("Operations Controls")
    refresh = st.sidebar.toggle("Live refresh", value=False)
    refresh_interval = st.sidebar.selectbox(
        "Refresh interval",
        REFRESH_INTERVAL_SECONDS,
        index=1,
        format_func=lambda x: f"{x} seconds",
    )

    if refresh:
        st_autorefresh(interval=int(refresh_interval) * 1000, key="refresh")

    if st.sidebar.button("Refresh now"):
        clear_query_cache()
        st.rerun()

    time_window_minutes = st.sidebar.selectbox(
        "Analysis window",
        TIME_WINDOW_MINUTES,
        index=1,
        format_func=lambda x: f"Last {x} minutes",
    )
    time_filter = f"window_start >= now() - INTERVAL {int(time_window_minutes)} MINUTE"

    source_profiles_observed = query_df(f"""
        SELECT
          source_profile,
          count() AS aggregate_windows,
          countDistinct(server_id) AS servers,
          max(window_start) AS last_seen,
          max(hot_zone_risk_score) AS max_risk
        FROM agg_zone_30s
        WHERE {time_filter}
        GROUP BY source_profile
        ORDER BY aggregate_windows DESC
        LIMIT 100
    """)

    st.sidebar.header("Source Schema")
    source_options = [ALL_SOURCE_PROFILES]
    if not source_profiles_observed.empty:
        source_options += source_profiles_observed["source_profile"].dropna().astype(str).tolist()

    selected_source_profile = st.sidebar.selectbox("Source profile", source_options, index=0)
    source_filter = source_filter_sql(selected_source_profile)

    server_inventory = query_df(f"""
        SELECT
          source_profile,
          server_id,
          anyLast(region) AS region,
          anyLast(map_id) AS latest_map,
          max(window_start) AS last_seen,
          max(hot_zone_risk_score) AS max_risk,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          max(active_players) AS peak_local_players,
          count() AS aggregate_windows
        FROM agg_zone_30s
        WHERE {time_filter}
          AND {source_filter}
        GROUP BY source_profile, server_id
        ORDER BY max_risk DESC, last_seen DESC
        LIMIT 300
    """)

    st.sidebar.header("Server Explorer")

    regions = [ALL_REGIONS]
    if not server_inventory.empty and "region" in server_inventory.columns:
        regions += sorted([str(x) for x in server_inventory["region"].dropna().unique().tolist()])

    selected_region = st.sidebar.selectbox("Region", regions, index=0)

    if selected_region == ALL_REGIONS:
        visible_inventory = server_inventory.copy()
    else:
        visible_inventory = server_inventory[server_inventory["region"] == selected_region].copy()

    server_options = [ALL_SERVERS]
    server_display_to_id = {}

    if not visible_inventory.empty:
        visible_inventory = visible_inventory.copy()
        if selected_source_profile == ALL_SOURCE_PROFILES:
            visible_inventory["server_display"] = (
                visible_inventory["source_profile"].astype(str) + " / " + visible_inventory["server_id"].astype(str)
            )
        else:
            visible_inventory["server_display"] = visible_inventory["server_id"].astype(str)

        server_display_to_id = dict(zip(visible_inventory["server_display"], visible_inventory["server_id"]))
        server_options += visible_inventory["server_display"].dropna().astype(str).tolist()

    selected_server_display = st.sidebar.selectbox("Server", server_options, index=0)
    selected_server = (
        ALL_SERVERS
        if selected_server_display == ALL_SERVERS
        else server_display_to_id.get(selected_server_display, selected_server_display)
    )

    max_table_rows = st.sidebar.selectbox("Table row limit", TABLE_ROW_LIMITS, index=1)

    filters = DashboardFilters(
        selected_source_profile=selected_source_profile,
        selected_region=selected_region,
        selected_server=selected_server,
        time_window_minutes=int(time_window_minutes),
        max_table_rows=int(max_table_rows),
    )

    active_filter = combined_filter_sql(
        filters.selected_source_profile,
        filters.selected_region,
        filters.selected_server,
    )

    st.sidebar.divider()
    st.sidebar.caption("Use Source profile to compare native, generic, and Unreal-style telemetry streams.")

    if source_profiles_observed.empty:
        st.sidebar.info("No source profiles observed yet.")
    else:
        with st.sidebar.expander("Observed source profiles", expanded=True):
            render_table(source_profiles_observed, height=220)

    if visible_inventory.empty:
        st.sidebar.info("No servers observed for the current source/region filter.")
    else:
        with st.sidebar.expander("Available servers", expanded=True):
            render_table(
                visible_inventory[[
                    "source_profile",
                    "server_id",
                    "region",
                    "latest_map",
                    "last_seen",
                    "max_risk",
                    "p95_frame",
                    "peak_local_players",
                ]].head(30),
                height=300,
            )

    return DashboardContext(
        filters=filters,
        active_filter=active_filter,
        source_filter=source_filter_sql(filters.selected_source_profile),
        region_filter=region_filter_sql(filters.selected_region),
        server_filter=server_filter_sql(filters.selected_server),
        server_inventory=server_inventory,
        visible_inventory=visible_inventory,
        selected_server_display=selected_server_display,
    )
