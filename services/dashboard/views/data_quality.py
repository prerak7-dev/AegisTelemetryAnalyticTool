from __future__ import annotations

import streamlit as st

from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import combined_filter_sql, query_df

def render(context: DashboardContext) -> None:
    filters = context.filters
    st.subheader("Telemetry data quality")

    quality_filter = combined_filter_sql(
        filters.selected_source_profile,
        filters.selected_region,
        filters.selected_server,
    )

    quality_summary = query_df(f"""
        SELECT
          count() AS failed_events,
          max(failed_at) AS latest_failure,
          countDistinct(source_profile) AS affected_source_profiles,
          countDistinct(server_id) AS affected_servers
        FROM data_quality_failures
        WHERE {filters.quality_time_filter}
          AND {quality_filter}
    """)
    qrow = quality_summary.iloc[0] if not quality_summary.empty else {}

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        render_paper_metric("Validation failures", str(int(qrow.get("failed_events", 0) or 0)))
    with q2:
        render_paper_metric("Affected sources", str(int(qrow.get("affected_source_profiles", 0) or 0)))
    with q3:
        render_paper_metric("Affected servers", str(int(qrow.get("affected_servers", 0) or 0)))
    with q4:
        render_paper_metric("Latest failure", str(qrow.get("latest_failure", "—")))

    failure_breakdown = query_df(f"""
        SELECT
          source_profile,
          category,
          event_type,
          region,
          server_id,
          count() AS failures
        FROM data_quality_failures
        WHERE {filters.quality_time_filter}
          AND {quality_filter}
        GROUP BY source_profile, category, event_type, region, server_id
        ORDER BY failures DESC
        LIMIT {filters.max_table_rows}
    """)
    if failure_breakdown.empty:
        st.success("No validation failures captured for the current filter.")
    else:
        render_table(failure_breakdown, height=320)

    recent_failures = query_df(f"""
        SELECT
          failed_at,
          event_id,
          error,
          category,
          event_type,
          source_profile,
          region,
          server_id
        FROM data_quality_failures
        WHERE {filters.quality_time_filter}
          AND {quality_filter}
        ORDER BY failed_at DESC
        LIMIT {filters.max_table_rows}
    """)
    if not recent_failures.empty:
        st.write("Recent validation failures")
        render_table(recent_failures, height=320)
