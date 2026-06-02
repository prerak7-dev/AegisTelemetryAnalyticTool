from __future__ import annotations

import pandas as pd
import streamlit as st

from services.dashboard.charts import render_horizontal_bar_chart, render_multi_metric_timeline
from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.performance_config import baseline_cfg, cfg_get, table_name
from services.dashboard.pressure_model import baseline_history_minutes
from services.dashboard.query import query_df_named

SCOPE_DIMENSIONS = {
    "source_region_server_map_zone": ["source_profile", "region", "server_id", "map_id", "zone_id"],
    "source_region_map_zone": ["source_profile", "region", "map_id", "zone_id"],
    "source_region": ["source_profile", "region"],
    "source_profile": ["source_profile"],
}

SCOPE_LABELS = {
    "source_region_server_map_zone": "Source / Region / Server / Map / Zone",
    "source_region_map_zone": "Source / Region / Map / Zone",
    "source_region": "Source / Region",
    "source_profile": "Source Profile",
}

def _baseline_metric_weights() -> dict[str, float]:
    return {
        str(key): float(value)
        for key, value in dict(baseline_cfg("anomaly_score_weights", {})).items()
    }

def _ratio_expr(current_col: str, baseline_col: str) -> str:
    return f"if(b.{baseline_col} > 0, c.{current_col} / b.{baseline_col}, 0)"

def _safe_z_expr(current_col: str, mean_col: str, std_col: str) -> str:
    return f"if(b.{std_col} > 0, (c.{current_col} - b.{mean_col}) / b.{std_col}, 0)"

def _score_expression() -> str:
    weights = _baseline_metric_weights()
    expressions = [
        f"({_ratio_expr('current_p95_frame', 'baseline_p95_frame')}) * {weights.get('frame_ratio', 35)}",
        f"({_safe_z_expr('current_p95_frame', 'baseline_mean_frame', 'baseline_frame_std')}) * {weights.get('frame_z', 18)}",
        f"({_ratio_expr('current_packet_loss', 'baseline_packet_loss')}) * {weights.get('packet_loss_ratio', 30)}",
        f"({_ratio_expr('current_aoe_events', 'baseline_aoe_events')}) * {weights.get('aoe_ratio', 22)}",
        f"({_ratio_expr('current_memory', 'baseline_memory')}) * {weights.get('memory_ratio', 18)}",
        f"({_ratio_expr('current_physics_events', 'baseline_physics_events')}) * {weights.get('physics_ratio', 18)}",
        f"({_ratio_expr('current_replication', 'baseline_replication')}) * {weights.get('replication_ratio', 18)}",
        f"({_ratio_expr('current_player_impact', 'baseline_player_impact')}) * {weights.get('player_impact_ratio', 25)}",
    ]
    return "greatest(" + ", ".join(expressions) + ")"

def _dominant_metric_expression() -> str:
    weights = _baseline_metric_weights()
    pairs = [
        ("frame", f"({_ratio_expr('current_p95_frame', 'baseline_p95_frame')}) * {weights.get('frame_ratio', 35)}"),
        ("packet_loss", f"({_ratio_expr('current_packet_loss', 'baseline_packet_loss')}) * {weights.get('packet_loss_ratio', 30)}"),
        ("aoe", f"({_ratio_expr('current_aoe_events', 'baseline_aoe_events')}) * {weights.get('aoe_ratio', 22)}"),
        ("memory", f"({_ratio_expr('current_memory', 'baseline_memory')}) * {weights.get('memory_ratio', 18)}"),
        ("physics", f"({_ratio_expr('current_physics_events', 'baseline_physics_events')}) * {weights.get('physics_ratio', 18)}"),
        ("replication", f"({_ratio_expr('current_replication', 'baseline_replication')}) * {weights.get('replication_ratio', 18)}"),
        ("player_impact", f"({_ratio_expr('current_player_impact', 'baseline_player_impact')}) * {weights.get('player_impact_ratio', 25)}"),
    ]
    # ClickHouse multiIf(condition, value, ..., else)
    max_expr = "greatest(" + ", ".join(expr for _, expr in pairs) + ")"
    conditions = []
    for name, expr in pairs:
        conditions.append(f"{expr} = {max_expr}, '{name}'")
    return "multiIf(" + ", ".join(conditions) + ", 'frame')"

def _scope_select_sql(scope_key: str) -> tuple[list[str], str, str]:
    dimensions = SCOPE_DIMENSIONS.get(scope_key, SCOPE_DIMENSIONS["source_region_server_map_zone"])
    select_sql = ",\n            ".join(dimensions)
    group_sql = ", ".join(dimensions)
    join_sql = ", ".join(dimensions)
    return dimensions, select_sql, group_sql or "source_profile", join_sql or "source_profile"

def _classify_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    severity_cfg = dict(baseline_cfg("severity_thresholds", {"warning": 55, "critical": 80}))
    confidence_cfg = dict(baseline_cfg("confidence", {"minimum_confidence": 0.35, "strong_sample_multiplier": 4}))
    minimum_rows = int(baseline_cfg("minimum_baseline_rows", 6) or 6)
    strong_multiplier = float(confidence_cfg.get("strong_sample_multiplier", 4) or 4)
    min_confidence = float(confidence_cfg.get("minimum_confidence", 0.35) or 0.35)

    out["anomaly_score"] = pd.to_numeric(out["anomaly_score"], errors="coerce").fillna(0).clip(lower=0, upper=100)
    out["baseline_rows"] = pd.to_numeric(out["baseline_rows"], errors="coerce").fillna(0)
    out["current_rows"] = pd.to_numeric(out["current_rows"], errors="coerce").fillna(0)

    strong_sample_target = max(minimum_rows * strong_multiplier, minimum_rows)
    out["baseline_confidence"] = (out["baseline_rows"] / strong_sample_target).clip(lower=0, upper=1)

    def severity(row: pd.Series) -> str:
        if float(row["baseline_confidence"]) < min_confidence:
            return "low_confidence"
        if float(row["anomaly_score"]) >= float(severity_cfg.get("critical", 80)):
            return "critical"
        if float(row["anomaly_score"]) >= float(severity_cfg.get("warning", 55)):
            return "warning"
        return "normal"

    out["anomaly_severity"] = out.apply(severity, axis=1)
    return out

def _metric_breakdown(top_row: pd.Series | None) -> pd.DataFrame:
    if top_row is None:
        return pd.DataFrame()

    catalog = dict(baseline_cfg("metric_catalog", {}))
    rows = []
    for metric_key, meta in catalog.items():
        current_col = meta.get("current_column")
        baseline_col = meta.get("baseline_column")
        ratio_col = meta.get("ratio_column")
        z_col = meta.get("z_column")
        if not current_col or current_col not in top_row:
            continue

        rows.append({
            "metric": meta.get("label", metric_key),
            "current": float(top_row.get(current_col, 0) or 0),
            "baseline": float(top_row.get(baseline_col, 0) or 0),
            "ratio": float(top_row.get(ratio_col, 0) or 0),
            "z_score": float(top_row.get(z_col, 0) or 0) if z_col else 0.0,
            "unit": meta.get("unit", ""),
        })

    return pd.DataFrame(rows).sort_values("ratio", ascending=False)

def _scope_label(row: pd.Series, dimensions: list[str]) -> str:
    return " / ".join(str(row.get(dim, "—")) for dim in dimensions)

def render(context: DashboardContext) -> None:
    filters = context.filters
    aggregate_table = table_name("aggregate_zone_table")
    available_scopes = list(baseline_cfg("baseline_scope.available_dimensions", list(SCOPE_DIMENSIONS.keys())))
    default_scope = str(baseline_cfg("baseline_scope.default_dimension", "source_region_server_map_zone"))
    available_scopes = [scope for scope in available_scopes if scope in SCOPE_DIMENSIONS] or list(SCOPE_DIMENSIONS.keys())

    st.subheader("Baseline Intelligence")
    st.caption(
        "Context-aware anomaly detection: compare the active filtered window against recent historical behavior "
        "for the same gameplay/server context instead of relying only on static thresholds."
    )

    scope_key = st.selectbox(
        "Baseline scope",
        available_scopes,
        index=available_scopes.index(default_scope) if default_scope in available_scopes else 0,
        format_func=lambda key: SCOPE_LABELS.get(key, key),
    )

    active_minutes = int(filters.time_window_minutes)
    baseline_minutes = baseline_history_minutes(active_minutes)
    minimum_rows = int(baseline_cfg("minimum_baseline_rows", 6) or 6)
    threshold_cfg = dict(baseline_cfg("dynamic_thresholds", {}))
    warning_z = float(threshold_cfg.get("warning_z", 2.0))
    critical_z = float(threshold_cfg.get("critical_z", 3.0))
    warning_ratio = float(threshold_cfg.get("warning_ratio", 1.35))
    critical_ratio = float(threshold_cfg.get("critical_ratio", 1.75))

    dimensions, select_sql, group_sql, join_sql = _scope_select_sql(scope_key)
    anomaly_score_sql = _score_expression()
    dominant_metric_sql = _dominant_metric_expression()

    st.markdown(
        f"""
        <div class="pressure-callout">
          <b>Dynamic threshold mode:</b> current <b>{active_minutes}m</b> window compared against the previous
          <b>{baseline_minutes - active_minutes}m</b> baseline for <b>{SCOPE_LABELS.get(scope_key, scope_key)}</b>.
          Warning/critical limits are configured as z-score and ratio thresholds, not hardcoded in the view.
        </div>
        """,
        unsafe_allow_html=True,
    )

    baseline = query_df_named(
        "baseline_intelligence_anomaly_windows",
        f"""
        SELECT
          {select_sql},
          c.current_rows,
          b.baseline_rows,

          c.current_p95_frame,
          b.baseline_p95_frame,
          b.baseline_mean_frame,
          b.baseline_frame_std,
          {_ratio_expr('current_p95_frame', 'baseline_p95_frame')} AS frame_ratio,
          {_safe_z_expr('current_p95_frame', 'baseline_mean_frame', 'baseline_frame_std')} AS frame_z,
          greatest(b.baseline_mean_frame + ({warning_z} * b.baseline_frame_std), b.baseline_p95_frame * {warning_ratio}) AS dynamic_warning_frame_ms,
          greatest(b.baseline_mean_frame + ({critical_z} * b.baseline_frame_std), b.baseline_p95_frame * {critical_ratio}) AS dynamic_critical_frame_ms,

          c.current_packet_loss,
          b.baseline_packet_loss,
          {_ratio_expr('current_packet_loss', 'baseline_packet_loss')} AS packet_loss_ratio,
          b.baseline_packet_loss * {warning_ratio} AS dynamic_warning_packet_loss,
          b.baseline_packet_loss * {critical_ratio} AS dynamic_critical_packet_loss,

          c.current_aoe_events,
          b.baseline_aoe_events,
          {_ratio_expr('current_aoe_events', 'baseline_aoe_events')} AS aoe_ratio,

          c.current_memory,
          b.baseline_memory,
          {_ratio_expr('current_memory', 'baseline_memory')} AS memory_ratio,

          c.current_physics_events,
          b.baseline_physics_events,
          {_ratio_expr('current_physics_events', 'baseline_physics_events')} AS physics_ratio,

          c.current_replication,
          b.baseline_replication,
          {_ratio_expr('current_replication', 'baseline_replication')} AS replication_ratio,

          c.current_player_impact,
          b.baseline_player_impact,
          {_ratio_expr('current_player_impact', 'baseline_player_impact')} AS player_impact_ratio,

          {anomaly_score_sql} AS anomaly_score,
          {dominant_metric_sql} AS dominant_anomaly_metric
        FROM
        (
          SELECT
            {select_sql},
            count() AS current_rows,
            quantile(0.95)(server_frame_ms_p95) AS current_p95_frame,
            quantile(0.95)(packet_loss_p95) AS current_packet_loss,
            avg(aoe_events) AS current_aoe_events,
            quantile(0.95)(memory_mb_p95) AS current_memory,
            avg(physics_events) AS current_physics_events,
            quantile(0.95)(replicated_objects_p95) AS current_replication,
            avg(desync_events + rubberband_events) AS current_player_impact
          FROM {aggregate_table}
          WHERE {filters.time_filter}
            AND {context.active_filter}
          GROUP BY {group_sql}
        ) AS c
        LEFT JOIN
        (
          SELECT
            {select_sql},
            count() AS baseline_rows,
            avg(server_frame_ms_p95) AS baseline_mean_frame,
            quantile(0.95)(server_frame_ms_p95) AS baseline_p95_frame,
            stddevSamp(server_frame_ms_p95) AS baseline_frame_std,
            quantile(0.95)(packet_loss_p95) AS baseline_packet_loss,
            avg(aoe_events) AS baseline_aoe_events,
            quantile(0.95)(memory_mb_p95) AS baseline_memory,
            avg(physics_events) AS baseline_physics_events,
            quantile(0.95)(replicated_objects_p95) AS baseline_replication,
            avg(desync_events + rubberband_events) AS baseline_player_impact
          FROM {aggregate_table}
          WHERE window_start >= now() - INTERVAL {baseline_minutes} MINUTE
            AND window_start < now() - INTERVAL {active_minutes} MINUTE
            AND {context.active_filter}
          GROUP BY {group_sql}
        ) AS b
        USING {join_sql}
        WHERE b.baseline_rows >= {minimum_rows}
        ORDER BY anomaly_score DESC
        LIMIT {filters.max_table_rows}
        """,
        cache_policy="medium",
    )

    baseline = _classify_anomalies(baseline)

    if baseline.empty:
        st.info(
            "No baseline rows available for this scope yet. Generate more historical traffic, widen the analysis window, "
            "or choose a broader baseline scope such as Source / Region."
        )
        return

    total = len(baseline)
    critical_count = int((baseline["anomaly_severity"] == "critical").sum())
    warning_count = int((baseline["anomaly_severity"] == "warning").sum())
    low_confidence_count = int((baseline["anomaly_severity"] == "low_confidence").sum())
    max_score = float(baseline["anomaly_score"].max() or 0)
    avg_conf = float(baseline["baseline_confidence"].mean() or 0)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_paper_metric("Contexts scored", str(total))
    with k2:
        render_paper_metric("Critical", str(critical_count))
    with k3:
        render_paper_metric("Warning", str(warning_count))
    with k4:
        render_paper_metric("Max anomaly", f"{max_score:.0f}")
    with k5:
        render_paper_metric("Avg confidence", f"{avg_conf:.2f}")

    chart_df = baseline.copy()
    chart_df["scope"] = chart_df.apply(lambda row: _scope_label(row, dimensions), axis=1)
    chart_df = chart_df.sort_values("anomaly_score", ascending=False).head(20)

    st.markdown('<div class="pressure-section-title">Top Contextual Anomalies</div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 1.0])

    with left:
        render_horizontal_bar_chart(
            chart_df,
            x="anomaly_score",
            y="scope",
            tooltip_columns=[
                "scope",
                "anomaly_score",
                "anomaly_severity",
                "dominant_anomaly_metric",
                "frame_ratio",
                "frame_z",
                "packet_loss_ratio",
                "baseline_confidence",
            ],
            height=440,
            x_title="Contextual anomaly score",
        )

    with right:
        top_row = baseline.iloc[0] if not baseline.empty else None
        breakdown = _metric_breakdown(top_row)
        st.caption("Metric deviation breakdown for the highest-ranked anomaly.")
        if breakdown.empty:
            st.info("No metric breakdown available.")
        else:
            render_horizontal_bar_chart(
                breakdown,
                x="ratio",
                y="metric",
                tooltip_columns=["metric", "current", "baseline", "ratio", "z_score", "unit"],
                height=360,
                x_title="Current / baseline ratio",
            )

    st.markdown('<div class="pressure-section-title">Dynamic Threshold Table</div>', unsafe_allow_html=True)
    display_cols = [
        *dimensions,
        "anomaly_severity",
        "dominant_anomaly_metric",
        "anomaly_score",
        "baseline_confidence",
        "current_rows",
        "baseline_rows",
        "current_p95_frame",
        "baseline_p95_frame",
        "frame_ratio",
        "frame_z",
        "dynamic_warning_frame_ms",
        "dynamic_critical_frame_ms",
        "current_packet_loss",
        "baseline_packet_loss",
        "packet_loss_ratio",
        "dynamic_warning_packet_loss",
        "dynamic_critical_packet_loss",
        "aoe_ratio",
        "memory_ratio",
        "physics_ratio",
        "replication_ratio",
        "player_impact_ratio",
    ]
    render_table(baseline[[col for col in display_cols if col in baseline.columns]], height=520)

    with st.expander("Timeline for highest anomaly", expanded=False):
        top = baseline.iloc[0]
        where_parts = []
        for dim in dimensions:
            value = str(top.get(dim, ""))
            escaped = value.replace("\\", "\\\\").replace("'", "\\'")
            where_parts.append(f"{dim} = '{escaped}'")
        scope_filter = " AND ".join(where_parts) if where_parts else "1 = 1"

        timeline = query_df_named(
            "baseline_intelligence_top_scope_timeline",
            f"""
            SELECT
              window_start,
              quantile(0.95)(server_frame_ms_p95) AS server_frame_ms_p95,
              quantile(0.95)(packet_loss_p95) AS packet_loss_p95,
              avg(aoe_events) AS aoe_events,
              quantile(0.95)(memory_mb_p95) AS memory_mb_p95,
              avg(physics_events) AS physics_events,
              quantile(0.95)(replicated_objects_p95) AS replicated_objects_p95,
              avg(desync_events + rubberband_events) AS player_impact_events
            FROM {aggregate_table}
            WHERE window_start >= now() - INTERVAL {baseline_minutes} MINUTE
              AND {scope_filter}
            GROUP BY window_start
            ORDER BY window_start ASC
            LIMIT 1500
            """,
            cache_policy="short",
        )

        if timeline.empty:
            st.info("No timeline available for the top anomaly.")
        else:
            render_multi_metric_timeline(
                timeline,
                x="window_start",
                metrics=[
                    "server_frame_ms_p95",
                    "packet_loss_p95",
                    "aoe_events",
                    "memory_mb_p95",
                    "physics_events",
                    "replicated_objects_p95",
                    "player_impact_events",
                ],
                height=440,
                title="Raw metric value",
            )

    with st.expander("Configuration used for this analysis", expanded=False):
        st.json({
            "scope": scope_key,
            "dimensions": dimensions,
            "active_window_minutes": active_minutes,
            "baseline_history_minutes": baseline_minutes,
            "minimum_baseline_rows": minimum_rows,
            "dynamic_thresholds": threshold_cfg,
            "severity_thresholds": baseline_cfg("severity_thresholds", {}),
            "confidence": baseline_cfg("confidence", {}),
            "metric_weights": _baseline_metric_weights(),
        })
