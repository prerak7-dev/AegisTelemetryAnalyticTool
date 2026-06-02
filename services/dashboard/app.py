from __future__ import annotations

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from services.dashboard.components import render_filter_context, render_hero, render_paper_metric, render_status_banner
from services.dashboard.query import query_df
from services.dashboard.sidebar import LIVE_REFRESH_KEY, REFRESH_INTERVAL_KEY, render_sidebar
from services.dashboard.styles import inject_global_styles
from services.dashboard.navigation import render_workspace_navigation
from services.dashboard.live_snapshots import preferred_live_table, snapshot_badge
from services.dashboard.refresh_runtime import (
    auto_refresh_allowed,
    effective_refresh_interval_seconds,
    record_autorefresh_tick_if_new,
    should_render_kpi_strip,
    workspace_refresh_policy,
)

def render_kpi_strip(context) -> None:
    filters = context.filters
    live_table, using_snapshot = preferred_live_table(
        snapshot_config_key="live_pressure_summary_table",
        fallback_config_key="aggregate_zone_table",
    )
    latest = query_df(
        f"""
        SELECT
          max(window_start) AS latest_window,
          count() AS aggregate_rows,
          countDistinct(source_profile) AS observed_source_profiles,
          countDistinct(server_id) AS observed_servers,
          max(hot_zone_risk_score) AS max_risk,
          max(server_frame_ms_p95) AS max_p95_frame,
          sum(rubberband_events + desync_events) AS player_impact_events
        FROM {live_table}
        WHERE {filters.time_filter}
          AND {context.active_filter}
        """,
        name="app_live_snapshot_kpi_strip" if using_snapshot else "app_aggregate_kpi_strip",
        cache_policy="live",
    )

    row = latest.iloc[0] if not latest.empty else {}
    header_label = filters.selected_server if filters.selected_server != "All servers" else "Fleet"
    source_label = filters.selected_source_profile

    st.subheader(f"{header_label} Analytics · {source_label}")
    if using_snapshot:
        st.caption(snapshot_badge("KPI strip query source", using_snapshot))

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        render_paper_metric("Latest window", str(row.get("latest_window", "—")))
    with m2:
        render_paper_metric("Sources", str(int(row.get("observed_source_profiles", 0) or 0)))
    with m3:
        render_paper_metric("Servers", str(int(row.get("observed_servers", 0) or 0)))
    with m4:
        render_paper_metric("Rows", str(int(row.get("aggregate_rows", 0) or 0)))
    with m5:
        render_paper_metric("Max risk", f"{float(row.get('max_risk', 0) or 0):.1f}")
    with m6:
        render_paper_metric("Impact", str(int(row.get("player_impact_events", 0) or 0)))

    if filters.selected_server != "All servers" and not context.visible_inventory.empty:
        selected_meta = context.visible_inventory[context.visible_inventory["server_id"] == filters.selected_server]
        if not selected_meta.empty:
            meta = selected_meta.iloc[0]
            st.info(
                f"Selected server `{filters.selected_server}` · Source: `{meta.get('source_profile', 'unknown')}` · "
                f"Region: `{meta.get('region', 'unknown')}` · Latest map: `{meta.get('latest_map', 'unknown')}` · "
                f"Last seen: `{meta.get('last_seen', '—')}`"
            )

    render_status_banner(
        max_risk=float(row.get("max_risk", 0) or 0),
        max_p95_frame=float(row.get("max_p95_frame", 0) or 0),
        impact_events=int(row.get("player_impact_events", 0) or 0),
        source_label=source_label,
    )


def render_safe_autorefresh_controller(workspace_key: str) -> None:
    """Install auto-refresh only after the full page has rendered.

    The streamlit-autorefresh component can occasionally emit:
    "Bad message format: Tried to use SessionInfo before it was initialized"
    when it is mounted early during page/session initialization. Keep the
    component out of the sidebar/top-of-page path and use a stable component key
    so navigation changes do not constantly recreate the component.
    """
    refresh_enabled = bool(st.session_state.get(LIVE_REFRESH_KEY, False))
    try:
        raw_interval = int(st.session_state.get(REFRESH_INTERVAL_KEY, 10) or 10)
    except Exception:
        raw_interval = 10

    effective_interval = effective_refresh_interval_seconds(raw_interval, workspace_key)
    allow_auto_refresh = auto_refresh_allowed(refresh_enabled, workspace_key)
    policy = workspace_refresh_policy(workspace_key)

    if refresh_enabled and allow_auto_refresh:
        tick = st_autorefresh(
            interval=effective_interval * 1000,
            key="aegis_safe_live_refresh_tick",
        )
        record_autorefresh_tick_if_new(
            tick=tick,
            workspace_key=workspace_key,
            interval_seconds=effective_interval,
            enabled=True,
        )
    elif refresh_enabled:
        record_autorefresh_tick_if_new(
            tick=0,
            workspace_key=workspace_key,
            interval_seconds=effective_interval,
            enabled=False,
            skipped_reason=f"Workspace refresh mode is {policy.mode}.",
        )


def main() -> None:
    st.set_page_config(page_title="AegisTelemetry", layout="wide", initial_sidebar_state="expanded")
    inject_global_styles()
    render_hero()

    # Render workspace navigation before the sidebar so the refresh coordinator
    # can apply the current workspace policy during this same rerun.
    workspace = render_workspace_navigation()

    try:
        context = render_sidebar(active_workspace_key=workspace.key)
    except Exception as exc:
        st.error(f"Could not connect to ClickHouse yet: {exc}")
        st.stop()

    render_filter_context(context, workspace_label=workspace.label)

    policy = workspace_refresh_policy(workspace.key)
    if should_render_kpi_strip(workspace.key):
        render_kpi_strip(context)
        st.divider()
    else:
        st.caption(
            f"Static/manual workspace policy: `{policy.mode}` · fleet KPI strip skipped to reduce refresh/query work."
        )
        st.divider()

    workspace.renderer(context)

    # Mount auto-refresh last so Streamlit session state and page elements are
    # initialized before the component can trigger a rerun.
    render_safe_autorefresh_controller(workspace.key)

if __name__ == "__main__":
    main()
