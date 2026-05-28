from __future__ import annotations

import streamlit as st

from services.dashboard.components import render_filter_context, render_hero, render_paper_metric, render_status_banner
from services.dashboard.query import query_df
from services.dashboard.sidebar import render_sidebar
from services.dashboard.styles import inject_global_styles
from services.dashboard.navigation import render_workspace_navigation

def render_kpi_strip(context) -> None:
    filters = context.filters
    latest = query_df(f"""
        SELECT
          max(window_start) AS latest_window,
          count() AS aggregate_rows,
          countDistinct(source_profile) AS observed_source_profiles,
          countDistinct(server_id) AS observed_servers,
          max(hot_zone_risk_score) AS max_risk,
          max(server_frame_ms_p95) AS max_p95_frame,
          sum(rubberband_events + desync_events) AS player_impact_events
        FROM agg_zone_30s
        WHERE {filters.time_filter}
          AND {context.active_filter}
    """)

    row = latest.iloc[0] if not latest.empty else {}
    header_label = filters.selected_server if filters.selected_server != "All servers" else "Fleet"
    source_label = filters.selected_source_profile

    st.subheader(f"{header_label} Analytics · {source_label}")

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

def main() -> None:
    st.set_page_config(page_title="AegisTelemetry", layout="wide", initial_sidebar_state="expanded")
    inject_global_styles()
    render_hero()

    try:
        context = render_sidebar()
    except Exception as exc:
        st.error(f"Could not connect to ClickHouse yet: {exc}")
        st.stop()

    workspace = render_workspace_navigation()

    render_filter_context(context, workspace_label=workspace.label)

    render_kpi_strip(context)

    st.divider()

    workspace.renderer(context)

if __name__ == "__main__":
    main()
