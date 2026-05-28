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

LIVE_REFRESH_KEY = "aegis_filter_live_refresh"
REFRESH_INTERVAL_KEY = "aegis_filter_refresh_interval"
TIME_WINDOW_KEY = "aegis_filter_time_window_minutes"
SOURCE_PROFILE_KEY = "aegis_filter_source_profile"
REGION_KEY = "aegis_filter_region"
SERVER_DISPLAY_KEY = "aegis_filter_server_display"
TABLE_LIMIT_KEY = "aegis_filter_table_row_limit"

FILTER_STATE_KEY = "aegis_persisted_filters"
FILTER_WIDGET_KEYS = {
    LIVE_REFRESH_KEY,
    REFRESH_INTERVAL_KEY,
    TIME_WINDOW_KEY,
    SOURCE_PROFILE_KEY,
    REGION_KEY,
    SERVER_DISPLAY_KEY,
    TABLE_LIMIT_KEY,
}

QUERY_PARAM_BY_KEY = {
    LIVE_REFRESH_KEY: "live_refresh",
    REFRESH_INTERVAL_KEY: "refresh_interval",
    TIME_WINDOW_KEY: "analysis_window",
    SOURCE_PROFILE_KEY: "source_profile",
    REGION_KEY: "region",
    SERVER_DISPLAY_KEY: "server",
    TABLE_LIMIT_KEY: "row_limit",
}

def _filter_state() -> dict:
    return st.session_state.setdefault(FILTER_STATE_KEY, {})

def _query_param_get(name: str) -> str | None:
    """Read a query param safely across Streamlit versions."""
    try:
        value = st.query_params.get(name)
    except Exception:
        return None

    if isinstance(value, list):
        return str(value[0]) if value else None
    if value is None:
        return None
    return str(value)

def _option_from_string(raw_value: str | None, options: list, default_value):
    """Return the option matching a string while preserving option type."""
    if not options:
        return default_value

    if raw_value is None:
        return default_value if default_value in options else options[0]

    for option in options:
        if str(option) == str(raw_value):
            return option

    return default_value if default_value in options else options[0]

def _canonical_value_for(
    key: str,
    options: list,
    default_value,
):
    """Resolve persisted value from canonical state, URL params, or default."""
    state = _filter_state()

    if key in state:
        canonical = _option_from_string(str(state[key]), options, default_value)
    else:
        query_name = QUERY_PARAM_BY_KEY.get(key)
        canonical = _option_from_string(
            _query_param_get(query_name) if query_name else None,
            options,
            default_value,
        )

    # Keep canonical state valid for current options.
    state[key] = canonical
    return canonical

def _update_canonical_from_widget(key: str) -> None:
    """Callback used by widgets to persist their value immediately."""
    if key in st.session_state:
        _filter_state()[key] = st.session_state[key]

def _persisted_sidebar_selectbox(
    label: str,
    options: list,
    *,
    key: str,
    default_value,
    format_func=None,
):
    """Render a selectbox whose value survives Streamlit autorefresh.

    Widget keys are not treated as the only source of truth. Instead, each
    selection is mirrored into `aegis_persisted_filters` through an on_change
    callback. Before rendering, the widget key is restored from that canonical
    state. This avoids refresh components rebuilding selectboxes at defaults.
    """
    if not options:
        options = [default_value]

    canonical = _canonical_value_for(key, options, default_value)

    # Always restore the widget key from canonical state before the widget is
    # created. If the autorefresh component or changing options reset the widget,
    # this puts it back.
    st.session_state[key] = canonical

    selectbox_kwargs = {
        "label": label,
        "options": options,
        "key": key,
        "on_change": _update_canonical_from_widget,
        "args": (key,),
    }
    if format_func is not None:
        selectbox_kwargs["format_func"] = format_func

    return st.sidebar.selectbox(**selectbox_kwargs)

def _persisted_sidebar_toggle(label: str, *, key: str, default_value: bool = False) -> bool:
    state = _filter_state()
    if key not in state:
        query_value = _query_param_get(QUERY_PARAM_BY_KEY.get(key, ""))
        if query_value is None:
            state[key] = bool(default_value)
        else:
            state[key] = query_value.lower() in {"1", "true", "yes", "on"}

    st.session_state[key] = bool(state.get(key, default_value))
    return st.sidebar.toggle(
        label,
        key=key,
        on_change=_update_canonical_from_widget,
        args=(key,),
    )

def _sync_filter_query_params() -> None:
    """Persist canonical filter selections into the URL."""
    state = _filter_state()
    desired = {}
    for key, param_name in QUERY_PARAM_BY_KEY.items():
        if key not in state:
            continue
        value = state[key]
        if isinstance(value, bool):
            desired[param_name] = "1" if value else "0"
        else:
            desired[param_name] = str(value)

    try:
        current = {name: _query_param_get(name) for name in desired}
        if any(current.get(name) != value for name, value in desired.items()):
            for name, value in desired.items():
                st.query_params[name] = value
    except Exception:
        return

def render_sidebar() -> DashboardContext:
    """Render sidebar controls and return normalized dashboard context."""

    st.sidebar.header("Operations Controls")

    refresh = _persisted_sidebar_toggle("Live refresh", key=LIVE_REFRESH_KEY, default_value=False)

    refresh_interval = _persisted_sidebar_selectbox(
        "Refresh interval",
        REFRESH_INTERVAL_SECONDS,
        key=REFRESH_INTERVAL_KEY,
        default_value=REFRESH_INTERVAL_SECONDS[1] if len(REFRESH_INTERVAL_SECONDS) > 1 else REFRESH_INTERVAL_SECONDS[0],
        format_func=lambda x: f"{x} seconds",
    )

    if refresh:
        st_autorefresh(interval=int(refresh_interval) * 1000, key="aegis_live_refresh_tick")

    if st.sidebar.button("Refresh now"):
        clear_query_cache()
        st.rerun()

    time_window_minutes = _persisted_sidebar_selectbox(
        "Analysis window",
        TIME_WINDOW_MINUTES,
        key=TIME_WINDOW_KEY,
        default_value=TIME_WINDOW_MINUTES[1] if len(TIME_WINDOW_MINUTES) > 1 else TIME_WINDOW_MINUTES[0],
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

    selected_source_profile = _persisted_sidebar_selectbox(
        "Source profile",
        source_options,
        key=SOURCE_PROFILE_KEY,
        default_value=ALL_SOURCE_PROFILES,
    )
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

    selected_region = _persisted_sidebar_selectbox(
        "Region",
        regions,
        key=REGION_KEY,
        default_value=ALL_REGIONS,
    )

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

    selected_server_display = _persisted_sidebar_selectbox(
        "Server",
        server_options,
        key=SERVER_DISPLAY_KEY,
        default_value=ALL_SERVERS,
    )
    selected_server = (
        ALL_SERVERS
        if selected_server_display == ALL_SERVERS
        else server_display_to_id.get(selected_server_display, selected_server_display)
    )

    max_table_rows = _persisted_sidebar_selectbox(
        "Table row limit",
        TABLE_ROW_LIMITS,
        key=TABLE_LIMIT_KEY,
        default_value=TABLE_ROW_LIMITS[1] if len(TABLE_ROW_LIMITS) > 1 else TABLE_ROW_LIMITS[0],
    )

    # Sync after widgets render so newly changed values are durable for the
    # next autorefresh tick.
    _sync_filter_query_params()

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
