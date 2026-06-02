from __future__ import annotations

import pandas as pd
import streamlit as st

from services.dashboard.charts import (
    render_horizontal_bar_chart,
    render_multi_metric_timeline,
    render_timeseries_chart,
)
from services.dashboard.components import render_paper_metric, render_pressure_card, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.live_snapshots import preferred_live_table, snapshot_badge
from services.dashboard.performance_config import (
    baseline_cfg,
    cfg_get,
    feature_enabled,
    table_name,
)
from services.dashboard.pressure_model import (
    add_pressure_scores,
    baseline_anomaly_sql_score,
    baseline_history_minutes,
    build_pressure_summary,
    drilldown_limit,
    frame_timeline_limit,
    safe_int,
    timeline_limit,
)
from services.dashboard.query import combined_filter_sql, query_df_named

def render_pressure_cards(pressure_items: list[dict]) -> None:
    cols_per_row = 3
    for start in range(0, len(pressure_items), cols_per_row):
        cols = st.columns(cols_per_row, gap="medium")
        for col, item in zip(cols, pressure_items[start:start + cols_per_row]):
            with col:
                render_pressure_card(
                    title=item["pressure"],
                    score=float(item["score"]),
                    primary_value=item["primary"],
                    driver=item["driver"],
                    recommendation=item["recommendation"],
                )

def render_pipeline_health(context: DashboardContext) -> None:
    if not feature_enabled("enable_pipeline_health_cards", True):
        return

    filters = context.filters
    live_health_table, using_health_snapshot = preferred_live_table(
        snapshot_config_key="live_pressure_summary_table",
        fallback_config_key="aggregate_zone_table",
    )
    warning_seconds = int(cfg_get("pipeline_health.staleness_warning_seconds", 90) or 90)
    critical_seconds = int(cfg_get("pipeline_health.staleness_critical_seconds", 240) or 240)
    min_recent_rows = int(cfg_get("pipeline_health.minimum_recent_rows_warning", 10) or 10)

    health = query_df_named(
        "command_center_live_snapshot_pipeline_health" if using_health_snapshot else "command_center_pipeline_health",
        f"""
        SELECT
          latest_window,
          dateDiff('second', latest_window, now()) AS staleness_seconds,
          aggregate_rows,
          observed_servers,
          observed_sources
        FROM
        (
          SELECT
            max(window_start) AS latest_window,
            count() AS aggregate_rows,
            countDistinct(server_id) AS observed_servers,
            countDistinct(source_profile) AS observed_sources
          FROM {live_health_table}
          WHERE {filters.time_filter}
            AND {context.active_filter}
        )
        """,
        cache_policy="live",
    )

    if health.empty:
        return

    row = health.iloc[0]
    stale = float(row.get("staleness_seconds", 0) or 0)
    rows = int(row.get("aggregate_rows", 0) or 0)

    if stale >= critical_seconds or rows == 0:
        status = "CRITICAL"
    elif stale >= warning_seconds or rows < min_recent_rows:
        status = "WATCH"
    else:
        status = "HEALTHY"

    h1, h2, h3, h4 = st.columns(4, gap="medium")
    with h1:
        render_paper_metric("Pipeline status", status)
    with h2:
        render_paper_metric("Latest window", str(row.get("latest_window", "—")))
    with h3:
        render_paper_metric("Staleness sec", f"{stale:.0f}")
    with h4:
        render_paper_metric("Recent rows", str(rows))

def render_baseline_preview(context: DashboardContext) -> None:
    filters = context.filters
    aggregate_table = table_name("aggregate_zone_table")
    baseline_minutes = baseline_history_minutes(int(filters.time_window_minutes))
    minimum_baseline_rows = int(baseline_cfg("minimum_baseline_rows", 6) or 6)
    baseline_start = f"window_start >= now() - INTERVAL {baseline_minutes} MINUTE"
    baseline_end = f"window_start < now() - INTERVAL {int(filters.time_window_minutes)} MINUTE"
    anomaly_expression = baseline_anomaly_sql_score()

    baseline = query_df_named(
        "command_center_baseline_anomaly_preview",
        f"""
        SELECT
          c.source_profile,
          c.region,
          c.server_id,
          c.map_id,
          c.zone_id,
          c.current_rows,
          b.baseline_rows,
          c.current_p95_frame,
          b.baseline_p95_frame,
          b.baseline_frame_std,
          if(b.baseline_p95_frame > 0, c.current_p95_frame / b.baseline_p95_frame, 0) AS frame_ratio,
          if(b.baseline_frame_std > 0, (c.current_p95_frame - b.baseline_p95_frame) / b.baseline_frame_std, 0) AS frame_z,
          c.current_packet_loss,
          b.baseline_packet_loss,
          if(b.baseline_packet_loss > 0, c.current_packet_loss / b.baseline_packet_loss, 0) AS packet_loss_ratio,
          c.current_aoe_events,
          b.baseline_aoe_events,
          if(b.baseline_aoe_events > 0, c.current_aoe_events / b.baseline_aoe_events, 0) AS aoe_ratio,
          c.current_memory,
          b.baseline_memory,
          if(b.baseline_memory > 0, c.current_memory / b.baseline_memory, 0) AS memory_ratio,
          {anomaly_expression} AS anomaly_score
        FROM
        (
          SELECT
            source_profile,
            region,
            server_id,
            map_id,
            zone_id,
            count() AS current_rows,
            quantile(0.95)(server_frame_ms_p95) AS current_p95_frame,
            quantile(0.95)(packet_loss_p95) AS current_packet_loss,
            sum(aoe_events) AS current_aoe_events,
            quantile(0.95)(memory_mb_p95) AS current_memory
          FROM {aggregate_table}
          WHERE {filters.time_filter}
            AND {context.active_filter}
          GROUP BY source_profile, region, server_id, map_id, zone_id
        ) AS c
        LEFT JOIN
        (
          SELECT
            source_profile,
            region,
            server_id,
            map_id,
            zone_id,
            count() AS baseline_rows,
            quantile(0.95)(server_frame_ms_p95) AS baseline_p95_frame,
            stddevSamp(server_frame_ms_p95) AS baseline_frame_std,
            quantile(0.95)(packet_loss_p95) AS baseline_packet_loss,
            sum(aoe_events) AS baseline_aoe_events,
            quantile(0.95)(memory_mb_p95) AS baseline_memory
          FROM {aggregate_table}
          WHERE {baseline_start}
            AND {baseline_end}
            AND {context.active_filter}
          GROUP BY source_profile, region, server_id, map_id, zone_id
        ) AS b
        USING source_profile, region, server_id, map_id, zone_id
        WHERE baseline_p95_frame > 0
          AND baseline_rows >= {minimum_baseline_rows}
        ORDER BY anomaly_score DESC
        LIMIT {filters.max_table_rows}
        """,
        cache_policy="medium",
    )

    st.caption(
        f"Compares the active {filters.time_window_minutes}-minute window against the previous "
        f"{baseline_minutes - filters.time_window_minutes} minutes for the same source/region/server/map/zone context. "
        "History window, minimum samples, and anomaly weights are configurable."
    )

    if baseline.empty:
        st.info("No baseline comparison rows available yet. Generate more historical traffic or widen the analysis window.")
        return

    render_table(baseline, height=420)

def render(context: DashboardContext) -> None:
    filters = context.filters
    aggregate_table = table_name("aggregate_zone_table")
    quality_table = table_name("data_quality_table")
    live_pressure_table, using_pressure_snapshot = preferred_live_table(
        snapshot_config_key="live_pressure_summary_table",
        fallback_config_key="aggregate_zone_table",
    )
    live_hot_zone_table, using_hot_zone_snapshot = preferred_live_table(
        snapshot_config_key="live_hot_zone_table",
        fallback_config_key="aggregate_zone_table",
    )
    live_regional_table, using_regional_snapshot = preferred_live_table(
        snapshot_config_key="live_regional_pressure_table",
        fallback_config_key="aggregate_zone_table",
    )

    st.markdown('<div class="pressure-section-title">Live Pressure Overview</div>', unsafe_allow_html=True)

    summary = query_df_named(
        "command_center_live_snapshot_summary" if using_pressure_snapshot else "command_center_live_pressure_summary",
        f"""
        SELECT
          max(window_start) AS latest_window,
          count() AS aggregate_rows,
          countDistinct(server_id) AS observed_servers,
          countDistinct(source_profile) AS observed_source_profiles,
          max(hot_zone_risk_score) AS hot_zone_risk_score,
          quantile(0.95)(server_frame_ms_p95) AS server_frame_ms_p95,
          quantile(0.99)(server_frame_ms_p99) AS server_frame_ms_p99,
          quantile(0.95)(cpu_p95) AS cpu_p95,
          quantile(0.95)(packet_loss_p95) AS packet_loss_p95,
          quantile(0.95)(packet_out_kbps_p95) AS packet_out_kbps_p95,
          quantile(0.95)(replicated_objects_p95) AS replicated_objects_p95,
          sum(ability_casts) AS ability_casts,
          sum(aoe_events) AS aoe_events,
          sum(physics_events) AS physics_events,
          quantile(0.95)(memory_mb_p95) AS memory_mb_p95,
          quantile(0.95)(ai_agents_active_p95) AS ai_agents_active_p95,
          sum(ai_pathfinding_requests) AS ai_pathfinding_requests,
          sum(matchmaking_events) AS matchmaking_events,
          quantile(0.95)(matchmaking_queue_p95) AS matchmaking_queue_p95,
          sum(desync_events + rubberband_events) AS player_impact_events
        FROM {live_pressure_table}
        WHERE {filters.time_filter}
          AND {context.active_filter}
        """,
        cache_policy="live",
    )

    quality_filter = combined_filter_sql(
        filters.selected_source_profile,
        filters.selected_region,
        filters.selected_server,
    )
    quality = query_df_named(
        "command_center_data_quality_count",
        f"""
        SELECT count() AS failed_events
        FROM {quality_table}
        WHERE {filters.quality_time_filter}
          AND {quality_filter}
        """,
        cache_policy="medium",
    )
    quality_failures = 0 if quality.empty else safe_int(quality.iloc[0], "failed_events")

    if summary.empty:
        st.info("No aggregate data for the current filter.")
        return

    render_pipeline_health(context)

    summary_row = summary.iloc[0]
    pressure_items = build_pressure_summary(summary_row, quality_failures)
    pressure_df = pd.DataFrame(pressure_items).sort_values("score", ascending=False)

    render_pressure_cards(pressure_df.to_dict("records"))

    left, right = st.columns([1.2, 1.0])

    with left:
        st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
        st.subheader("Pressure trend timeline")
        st.caption("Normalized pressure scores over time. Pressure budgets are loaded from the dashboard performance profile.")
        timeline = query_df_named(
            "command_center_live_snapshot_timeline" if using_pressure_snapshot else "command_center_pressure_timeline",
            f"""
            SELECT
              window_start,
              quantile(0.95)(server_frame_ms_p95) AS server_frame_ms_p95,
              quantile(0.99)(server_frame_ms_p99) AS server_frame_ms_p99,
              quantile(0.95)(cpu_p95) AS cpu_p95,
              max(hot_zone_risk_score) AS hot_zone_risk_score,
              quantile(0.95)(packet_loss_p95) AS packet_loss_p95,
              quantile(0.95)(packet_out_kbps_p95) AS packet_out_kbps_p95,
              quantile(0.95)(replicated_objects_p95) AS replicated_objects_p95,
              sum(ability_casts) AS ability_casts,
              sum(aoe_events) AS aoe_events,
              sum(physics_events) AS physics_events,
              quantile(0.95)(memory_mb_p95) AS memory_mb_p95,
              quantile(0.95)(ai_agents_active_p95) AS ai_agents_active_p95,
              sum(ai_pathfinding_requests) AS ai_pathfinding_requests,
              sum(matchmaking_events) AS matchmaking_events,
              quantile(0.95)(matchmaking_queue_p95) AS matchmaking_queue_p95,
              sum(desync_events) AS desync_events,
              sum(rubberband_events) AS rubberband_events
            FROM {live_pressure_table}
            WHERE {filters.time_filter}
              AND {context.active_filter}
            GROUP BY window_start
            ORDER BY window_start ASC
            LIMIT {timeline_limit()}
            """,
            cache_policy="short",
        )
        timeline = add_pressure_scores(timeline, quality_failures)
        if timeline.empty:
            st.info("No pressure timeline for the current filter.")
        else:
            render_multi_metric_timeline(
                timeline,
                x="window_start",
                metrics=[
                    "simulation_pressure",
                    "network_pressure",
                    "replication_pressure",
                    "physics_pressure",
                    "memory_pressure",
                    "ai_pressure",
                    "matchmaking_pressure",
                    "player_impact_pressure",
                ],
                height=390,
                title="Normalized pressure score",
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
        st.subheader("Pressure ranking")
        st.caption("Highest pressure dimensions in the selected live window.")
        rank = pressure_df[["pressure", "score", "status", "primary", "validation_metric"]].copy()
        render_horizontal_bar_chart(
            rank,
            x="score",
            y="pressure",
            tooltip_columns=["pressure", "score", "status", "primary", "validation_metric"],
            height=360,
            x_title="Pressure score",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Pressure Drilldown / Top affected windows", expanded=False):
        selected_pressure = st.selectbox(
            "Pressure dimension",
            [
                "simulation_pressure",
                "network_pressure",
                "replication_pressure",
                "physics_pressure",
                "memory_pressure",
                "ai_pressure",
                "matchmaking_pressure",
                "player_impact_pressure",
            ],
            index=0,
            format_func=lambda value: value.replace("_", " ").title(),
        )

        drilldown = query_df_named(
            "command_center_live_snapshot_hotzones" if using_hot_zone_snapshot else "command_center_pressure_drilldown",
            f"""
            SELECT
              window_start,
              source_profile,
              region,
              server_id,
              map_id,
              zone_id,
              active_players,
              ability_casts,
              aoe_events,
              physics_events,
              replicated_objects_p95,
              cpu_p95,
              server_frame_ms_p95,
              server_frame_ms_p99,
              packet_loss_p95,
              packet_out_kbps_p95,
              memory_mb_p95,
              ai_agents_active_p95,
              ai_pathfinding_requests,
              matchmaking_events,
              matchmaking_queue_p95,
              desync_events,
              rubberband_events,
              hot_zone_risk_score,
              top_ability_id,
              top_event_type
            FROM {live_hot_zone_table}
            WHERE {filters.time_filter}
              AND {context.active_filter}
            ORDER BY window_start DESC
            LIMIT {drilldown_limit()}
            """,
            cache_policy="short",
        )
        drilldown = add_pressure_scores(drilldown, quality_failures)

        if drilldown.empty:
            st.info("No pressure drilldown rows for the current filter.")
        else:
            drilldown["scope"] = (
                drilldown["source_profile"].astype(str)
                + " / "
                + drilldown["region"].astype(str)
                + " / "
                + drilldown["server_id"].astype(str)
                + " / "
                + drilldown["zone_id"].astype(str)
            )
            sorted_drilldown = drilldown.sort_values(selected_pressure, ascending=False).head(filters.max_table_rows)
            display_cols = [
                "window_start",
                "scope",
                selected_pressure,
                "server_frame_ms_p95",
                "packet_loss_p95",
                "replicated_objects_p95",
                "physics_events",
                "memory_mb_p95",
                "ai_pathfinding_requests",
                "matchmaking_queue_p95",
                "desync_events",
                "rubberband_events",
                "top_event_type",
                "top_ability_id",
            ]
            render_table(sorted_drilldown[[col for col in display_cols if col in sorted_drilldown.columns]], height=420)

    with st.expander("Baseline Anomaly Preview / Context-aware thresholds", expanded=False):
        st.markdown(
            """
            <div class="pressure-callout">
              <b>Baseline intelligence foundation:</b> compares current windows against recent historical behavior for the same
              source, region, server, map, and zone. History windows, sample minimums, and anomaly weights are configurable.
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_baseline_preview(context)

    st.markdown('<div class="pressure-section-title">Frame-Time Symptom View</div>', unsafe_allow_html=True)
    left2, right2 = st.columns([1.3, 1.0])

    with left2:
        st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
        st.subheader("Realtime server frame pressure")
        st.caption("Still available as the primary simulation symptom, but no longer the only Command Center signal.")
        perf = query_df_named(
            "command_center_live_snapshot_frame_timeline" if using_pressure_snapshot else "command_center_frame_time_symptom_timeline",
            f"""
            SELECT
              window_start,
              source_profile,
              region,
              quantile(0.95)(server_frame_ms_p95) AS p95_frame
            FROM {live_pressure_table}
            WHERE {filters.time_filter}
              AND {context.active_filter}
            GROUP BY window_start, source_profile, region
            ORDER BY window_start ASC
            LIMIT {frame_timeline_limit()}
            """,
            cache_policy="short",
        )
        if not perf.empty:
            perf["series"] = perf["source_profile"].astype(str) + " / " + perf["region"].astype(str)
            render_timeseries_chart(
                perf,
                x="window_start",
                y="p95_frame",
                series="series",
                height=330,
                y_title="P95 server frame (ms)",
            )
        else:
            st.info("No aggregate data for the current filter.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
        st.subheader("Worst hot zones")
        st.caption("Highest-risk server/zone windows in the selected source, region, and server scope.")
        hotzones = query_df_named(
            "command_center_live_snapshot_worst_hot_zones" if using_hot_zone_snapshot else "command_center_worst_hot_zones",
            f"""
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
            FROM {live_hot_zone_table}
            WHERE {filters.time_filter}
              AND {context.active_filter}
            ORDER BY window_start DESC, hot_zone_risk_score DESC
            LIMIT {filters.max_table_rows}
            """,
            cache_policy="short",
        )
        if hotzones.empty:
            st.info("No hot-zone rows for the current filter.")
        else:
            render_table(hotzones, height=390)
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Source + regional pressure summary")
    st.caption("Executive fleet view: compare multidimensional pressure across source schemas and regions.")
    regional = query_df_named(
        "command_center_live_snapshot_regional" if using_pressure_snapshot else "command_center_source_regional_pressure_summary",
        f"""
        SELECT
          source_profile,
          region,
          countDistinct(server_id) AS observed_servers,
          max(hot_zone_risk_score) AS max_risk,
          quantile(0.95)(server_frame_ms_p95) AS p95_frame,
          quantile(0.95)(packet_loss_p95) AS packet_loss_p95,
          quantile(0.95)(replicated_objects_p95) AS replicated_objects_p95,
          quantile(0.95)(memory_mb_p95) AS memory_mb_p95,
          sum(physics_events) AS physics_events,
          sum(ai_pathfinding_requests) AS ai_pathfinding_requests,
          quantile(0.95)(matchmaking_queue_p95) AS matchmaking_queue_p95,
          sum(rubberband_events) AS rubberband_events,
          sum(desync_events) AS desync_events
        FROM {live_pressure_table}
        WHERE {filters.time_filter}
          AND {context.active_filter}
        GROUP BY source_profile, region
        ORDER BY max_risk DESC
        LIMIT {filters.max_table_rows}
        """,
        cache_policy="medium",
    )
    if regional.empty:
        st.info("No regional summary for the current filter.")
    else:
        render_table(regional, height=350)
