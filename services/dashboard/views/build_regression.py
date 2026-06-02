from __future__ import annotations

import math

import pandas as pd
import streamlit as st

from services.dashboard.charts import render_horizontal_bar_chart, render_multi_metric_timeline
from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.performance_config import build_regression_cfg, table_name
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

AGG_FUNCTIONS = {
    "avg": "avg",
    "max": "max",
    "min": "min",
    "sum": "sum",
    "quantile(0.95)": "quantile(0.95)",
    "quantile(0.99)": "quantile(0.99)",
}

def _quote_sql(value: str) -> str:
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"

def _metric_catalog() -> dict:
    return dict(build_regression_cfg("metric_catalog", {}))

def _metric_label(metric_key: str) -> str:
    return str(_metric_catalog().get(metric_key, {}).get("label", metric_key))

def _metric_unit(metric_key: str) -> str:
    return str(_metric_catalog().get(metric_key, {}).get("unit", ""))

def _metric_weight(metric_key: str) -> float:
    try:
        return float(_metric_catalog().get(metric_key, {}).get("weight", 1.0) or 1.0)
    except Exception:
        return 1.0

def _metric_direction(metric_key: str) -> str:
    return str(_metric_catalog().get(metric_key, {}).get("direction", "lower_is_better"))

def _metric_agg_sql(metric_key: str, source_column: str) -> str:
    raw = str(_metric_catalog().get(metric_key, {}).get("agg", "avg"))
    agg = AGG_FUNCTIONS.get(raw, "avg")
    return f"{agg}({source_column})"

def _safe_pct_change(prev: float, curr: float) -> float:
    if prev is None or abs(float(prev)) < 1e-9:
        if curr and abs(float(curr)) > 1e-9:
            return 100.0
        return 0.0
    return ((float(curr) - float(prev)) / abs(float(prev))) * 100.0

def _regression_pct(metric_key: str, prev: float, curr: float) -> float:
    change = _safe_pct_change(prev, curr)
    if _metric_direction(metric_key) == "higher_is_better":
        return -change
    return change

def _classify_regression(score: float, confidence: float) -> str:
    thresholds = dict(build_regression_cfg("regression_thresholds", {}))
    warning = float(thresholds.get("warning_pct", 15.0) or 15.0)
    critical = float(thresholds.get("critical_pct", 35.0) or 35.0)
    min_conf = float(thresholds.get("minimum_confidence", 0.35) or 0.35)

    if confidence < min_conf:
        return "low_confidence"
    if score >= critical:
        return "critical"
    if score >= warning:
        return "warning"
    if score <= -warning:
        return "improved"
    return "stable"

def _scope_sql(scope_key: str) -> tuple[list[str], str, str, str]:
    dimensions = SCOPE_DIMENSIONS.get(scope_key, SCOPE_DIMENSIONS["source_region_map_zone"])
    select_sql = ",\n          ".join(dimensions)
    group_sql = ", ".join(dimensions)
    join_sql = ", ".join(dimensions)
    return dimensions, select_sql, group_sql, join_sql

def _scope_label(row: pd.Series, dimensions: list[str]) -> str:
    return " / ".join(str(row.get(dim, "—")) for dim in dimensions)

def _build_metric_aggregate_sql(metric_keys: list[str]) -> str:
    lines = []
    catalog = _metric_catalog()
    for metric_key in metric_keys:
        if metric_key not in catalog:
            continue
        lines.append(f"{_metric_agg_sql(metric_key, metric_key)} AS {metric_key}")
    return ",\n          ".join(lines)

def _load_builds(context: DashboardContext, aggregate_table: str, build_column: str) -> pd.DataFrame:
    return query_df_named(
        "build_regression_available_builds",
        f"""
        SELECT
          {build_column} AS build_version,
          min(window_start) AS first_seen,
          max(window_start) AS last_seen,
          count() AS windows,
          countDistinct(server_id) AS servers,
          countDistinct(map_id) AS maps,
          countDistinct(zone_id) AS zones,
          countDistinct(source_profile) AS source_profiles
        FROM {aggregate_table}
        WHERE {context.filters.time_filter}
          AND {context.active_filter}
        GROUP BY {build_column}
        ORDER BY last_seen DESC
        LIMIT 200
        """,
        cache_policy="medium",
    )

def _build_comparison_rows(
    previous_df: pd.DataFrame,
    current_df: pd.DataFrame,
    dimensions: list[str],
    metric_keys: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if previous_df.empty or current_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    merged = previous_df.merge(
        current_df,
        on=dimensions,
        suffixes=("_previous", "_current"),
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame(), pd.DataFrame()

    minimum_windows = int(build_regression_cfg("minimum_windows_per_build", 3) or 3)
    strong_multiplier = float(dict(build_regression_cfg("regression_thresholds", {})).get("strong_sample_multiplier", 4) or 4)
    strong_sample_target = max(float(minimum_windows) * strong_multiplier, float(minimum_windows))

    context_rows = []
    metric_rows = []

    for _, row in merged.iterrows():
        weighted_score = 0.0
        weight_total = 0.0
        max_metric = "none"
        max_metric_score = -999999.0

        prev_windows = float(row.get("windows_previous", 0) or 0)
        curr_windows = float(row.get("windows_current", 0) or 0)
        confidence = max(0.0, min(1.0, min(prev_windows, curr_windows) / strong_sample_target))

        for metric_key in metric_keys:
            prev = float(row.get(f"{metric_key}_previous", 0) or 0)
            curr = float(row.get(f"{metric_key}_current", 0) or 0)
            pct_change = _safe_pct_change(prev, curr)
            regression_pct = _regression_pct(metric_key, prev, curr)
            weight = _metric_weight(metric_key)

            if abs(regression_pct) > abs(max_metric_score) or max_metric == "none":
                max_metric = metric_key
                max_metric_score = regression_pct

            weighted_score += max(regression_pct, 0.0) * weight
            weight_total += weight

            metric_rows.append({
                **{dim: row.get(dim) for dim in dimensions},
                "metric": metric_key,
                "metric_label": _metric_label(metric_key),
                "previous_value": prev,
                "current_value": curr,
                "pct_change": pct_change,
                "regression_pct": regression_pct,
                "unit": _metric_unit(metric_key),
                "weight": weight,
                "baseline_windows": int(prev_windows),
                "current_windows": int(curr_windows),
                "comparison_confidence": confidence,
            })

        regression_score = weighted_score / max(weight_total, 1e-9)
        severity = _classify_regression(regression_score, confidence)

        context_rows.append({
            **{dim: row.get(dim) for dim in dimensions},
            "regression_score": regression_score,
            "regression_severity": severity,
            "dominant_regressed_metric": max_metric,
            "dominant_regressed_metric_label": _metric_label(max_metric) if max_metric != "none" else "none",
            "dominant_regression_pct": max_metric_score,
            "comparison_confidence": confidence,
            "baseline_windows": int(prev_windows),
            "current_windows": int(curr_windows),
        })

    context_df = pd.DataFrame(context_rows).sort_values("regression_score", ascending=False)
    metric_df = pd.DataFrame(metric_rows).sort_values("regression_pct", ascending=False)

    return context_df, metric_df

def _release_readiness_text(context_df: pd.DataFrame) -> tuple[str, str]:
    if context_df.empty:
        return "NO DATA", "No comparable build contexts were found for the active filter."

    critical = int((context_df["regression_severity"] == "critical").sum())
    warning = int((context_df["regression_severity"] == "warning").sum())
    low_conf = int((context_df["regression_severity"] == "low_confidence").sum())

    if critical > 0:
        return "BLOCK", f"{critical} critical build-regression context(s) detected. Release readiness should be reviewed before promotion."
    if warning > 0:
        return "WATCH", f"{warning} warning-level regression context(s) detected. Validate affected maps/zones and player-impact guardrails."
    if low_conf > 0:
        return "LOW CONFIDENCE", f"{low_conf} contexts have insufficient sample support. Generate more telemetry before making release decisions."
    return "PASS", "No material build regression detected for the selected scope and filters."

def render(context: DashboardContext) -> None:
    filters = context.filters
    aggregate_table = table_name("aggregate_zone_table")
    build_column = str(build_regression_cfg("build_column", "build_version"))
    catalog = _metric_catalog()
    metric_keys = list(catalog.keys())

    st.subheader("Build Regression")
    st.caption(
        "Compare performance between builds to support release readiness, hotfix validation, and live-ops regression triage."
    )

    builds = _load_builds(context, aggregate_table, build_column)

    if builds.empty or len(builds) < 2:
        st.info(
            "At least two build versions are needed for build regression analysis. "
            "Generate telemetry with different build versions, or widen the analysis window."
        )
        if not builds.empty:
            render_table(builds, height=260)
        return

    build_options = builds["build_version"].astype(str).tolist()
    default_current = build_options[0]
    default_previous = build_options[1] if len(build_options) > 1 else build_options[0]

    left_select, right_select, scope_select = st.columns([1, 1, 1])
    with left_select:
        previous_build = st.selectbox(
            "Previous / baseline build",
            build_options,
            index=build_options.index(default_previous),
            key="aegis_build_regression_previous_build",
        )
    with right_select:
        current_build = st.selectbox(
            "Current / candidate build",
            build_options,
            index=build_options.index(default_current),
            key="aegis_build_regression_current_build",
        )
    with scope_select:
        scopes = [scope for scope in build_regression_cfg("available_scopes", list(SCOPE_DIMENSIONS.keys())) if scope in SCOPE_DIMENSIONS]
        default_scope = str(build_regression_cfg("default_comparison_scope", "source_region_map_zone"))
        scope_key = st.selectbox(
            "Comparison scope",
            scopes or list(SCOPE_DIMENSIONS.keys()),
            index=(scopes or list(SCOPE_DIMENSIONS.keys())).index(default_scope) if default_scope in (scopes or []) else 0,
            format_func=lambda key: SCOPE_LABELS.get(key, key),
            key="aegis_build_regression_scope",
        )

    if previous_build == current_build:
        st.warning("Select two different builds to compare.")
        return

    dimensions, select_sql, group_sql, join_sql = _scope_sql(scope_key)
    metric_sql = _build_metric_aggregate_sql(metric_keys)

    if not metric_sql:
        st.warning("No build-regression metrics are configured.")
        return

    previous_df = query_df_named(
        "build_regression_previous_build_rollup",
        f"""
        SELECT
          {select_sql},
          count() AS windows,
          {metric_sql}
        FROM {aggregate_table}
        WHERE {filters.time_filter}
          AND {context.active_filter}
          AND {build_column} = {_quote_sql(previous_build)}
        GROUP BY {group_sql}
        """,
        cache_policy="medium",
    )

    current_df = query_df_named(
        "build_regression_current_build_rollup",
        f"""
        SELECT
          {select_sql},
          count() AS windows,
          {metric_sql}
        FROM {aggregate_table}
        WHERE {filters.time_filter}
          AND {context.active_filter}
          AND {build_column} = {_quote_sql(current_build)}
        GROUP BY {group_sql}
        """,
        cache_policy="medium",
    )

    context_df, metric_df = _build_comparison_rows(previous_df, current_df, dimensions, metric_keys)

    status, status_copy = _release_readiness_text(context_df)

    st.markdown(
        f"""
        <div class="pressure-callout">
          <b>Release readiness:</b> {status} · Comparing <b>{previous_build}</b> against <b>{current_build}</b>
          across <b>{SCOPE_LABELS.get(scope_key, scope_key)}</b>. {status_copy}
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_paper_metric("Comparable contexts", str(len(context_df)))
    with c2:
        render_paper_metric("Critical", str(int((context_df.get("regression_severity", pd.Series(dtype=str)) == "critical").sum()) if not context_df.empty else 0))
    with c3:
        render_paper_metric("Warning", str(int((context_df.get("regression_severity", pd.Series(dtype=str)) == "warning").sum()) if not context_df.empty else 0))
    with c4:
        render_paper_metric("Max regression", f"{float(context_df['regression_score'].max() if not context_df.empty else 0):.1f}%")
    with c5:
        render_paper_metric("Avg confidence", f"{float(context_df['comparison_confidence'].mean() if not context_df.empty else 0):.2f}")

    if context_df.empty:
        st.info("No overlapping source/region/map/zone contexts were found between the two builds.")
        return

    context_chart_df = context_df.copy()
    context_chart_df["scope"] = context_chart_df.apply(lambda row: _scope_label(row, dimensions), axis=1)

    st.markdown('<div class="pressure-section-title">Most Regressed Contexts</div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 1.0])

    with left:
        render_horizontal_bar_chart(
            context_chart_df.head(20),
            x="regression_score",
            y="scope",
            tooltip_columns=[
                "scope",
                "regression_score",
                "regression_severity",
                "dominant_regressed_metric_label",
                "dominant_regression_pct",
                "comparison_confidence",
            ],
            height=460,
            x_title="Weighted regression score (%)",
        )

    with right:
        metric_summary = (
            metric_df.groupby(["metric", "metric_label", "unit"], dropna=False)
            .agg(
                avg_regression_pct=("regression_pct", "mean"),
                max_regression_pct=("regression_pct", "max"),
                contexts=("metric", "count"),
                avg_confidence=("comparison_confidence", "mean"),
            )
            .reset_index()
            .sort_values("max_regression_pct", ascending=False)
        )
        render_horizontal_bar_chart(
            metric_summary.head(12),
            x="max_regression_pct",
            y="metric_label",
            tooltip_columns=[
                "metric_label",
                "avg_regression_pct",
                "max_regression_pct",
                "contexts",
                "avg_confidence",
                "unit",
            ],
            height=420,
            x_title="Worst metric regression (%)",
        )

    st.markdown('<div class="pressure-section-title">Metric Regression Table</div>', unsafe_allow_html=True)
    display_metric_cols = [
        *dimensions,
        "metric_label",
        "previous_value",
        "current_value",
        "pct_change",
        "regression_pct",
        "unit",
        "comparison_confidence",
        "baseline_windows",
        "current_windows",
    ]
    render_table(metric_df[[col for col in display_metric_cols if col in metric_df.columns]].head(filters.max_table_rows), height=470)

    st.markdown('<div class="pressure-section-title">Context Regression Table</div>', unsafe_allow_html=True)
    display_context_cols = [
        *dimensions,
        "regression_severity",
        "regression_score",
        "dominant_regressed_metric_label",
        "dominant_regression_pct",
        "comparison_confidence",
        "baseline_windows",
        "current_windows",
    ]
    render_table(context_df[[col for col in display_context_cols if col in context_df.columns]].head(filters.max_table_rows), height=420)

    with st.expander("Timeline for most regressed context", expanded=False):
        top = context_df.iloc[0]
        scope_filter_parts = []
        for dim in dimensions:
            value = _quote_sql(str(top.get(dim, "")))
            scope_filter_parts.append(f"{dim} = {value}")
        scope_filter = " AND ".join(scope_filter_parts) if scope_filter_parts else "1 = 1"

        timeline = query_df_named(
            "build_regression_top_context_timeline",
            f"""
            SELECT
              window_start,
              {build_column} AS build_version,
              quantile(0.95)(server_frame_ms_p95) AS server_frame_ms_p95,
              quantile(0.95)(packet_out_kbps_p95) AS packet_out_kbps_p95,
              quantile(0.95)(packet_loss_p95) AS packet_loss_p95,
              quantile(0.95)(replicated_objects_p95) AS replicated_objects_p95,
              avg(physics_events) AS physics_events,
              quantile(0.95)(memory_mb_p95) AS memory_mb_p95,
              avg(desync_events + rubberband_events) AS player_impact
            FROM {aggregate_table}
            WHERE {filters.time_filter}
              AND {context.active_filter}
              AND {build_column} IN ({_quote_sql(previous_build)}, {_quote_sql(current_build)})
              AND {scope_filter}
            GROUP BY window_start, {build_column}
            ORDER BY window_start ASC
            LIMIT 1500
            """,
            cache_policy="short",
        )

        if timeline.empty:
            st.info("No timeline rows available for the selected top context.")
        else:
            metric = st.selectbox(
                "Timeline metric",
                [
                    "server_frame_ms_p95",
                    "packet_out_kbps_p95",
                    "packet_loss_p95",
                    "replicated_objects_p95",
                    "physics_events",
                    "memory_mb_p95",
                    "player_impact",
                ],
                index=0,
                key="aegis_build_regression_timeline_metric",
            )
            render_multi_metric_timeline(
                timeline.pivot_table(index="window_start", columns="build_version", values=metric, aggfunc="mean").reset_index(),
                x="window_start",
                metrics=[col for col in timeline["build_version"].astype(str).unique().tolist()],
                height=440,
                title=metric,
            )

    with st.expander("Build inventory and configuration", expanded=False):
        st.caption("Builds observed in the current filter/time window.")
        render_table(builds, height=260)
        st.json({
            "build_column": build_column,
            "comparison_scope": scope_key,
            "minimum_windows_per_build": build_regression_cfg("minimum_windows_per_build", 3),
            "regression_thresholds": build_regression_cfg("regression_thresholds", {}),
            "metric_catalog": _metric_catalog(),
        })
