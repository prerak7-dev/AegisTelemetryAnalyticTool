from __future__ import annotations

import math
import re

import pandas as pd
import streamlit as st

from services.dashboard.charts import render_horizontal_bar_chart, render_multi_metric_timeline
from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.performance_config import fix_validation_cfg, table_name
from services.dashboard.query import query_df_named

ALLOWED_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

SUMMARY_FUNCTIONS = {
    "avg": "avg",
    "max": "max",
    "min": "min",
    "sum": "sum",
    "quantile(0.95)": "quantile(0.95)",
    "quantile(0.99)": "quantile(0.99)",
}

def _safe_identifier(value: str, default: str) -> str:
    value = str(value or default)
    return value if ALLOWED_IDENTIFIER.match(value) else default

def _quote_sql(value: str) -> str:
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"

def _experiment_fields() -> dict[str, str]:
    fields = dict(fix_validation_cfg("experiment_fields", {}))
    return {
        "experiment_id": _safe_identifier(fields.get("experiment_id", "experiment_id"), "experiment_id"),
        "variant": _safe_identifier(fields.get("variant", "experiment_variant"), "experiment_variant"),
        "change_id": _safe_identifier(fields.get("change_id", "change_id"), "change_id"),
        "validation_plan_id": _safe_identifier(fields.get("validation_plan_id", "validation_plan_id"), "validation_plan_id"),
    }

def _json_field_expr(field_name: str) -> str:
    return f"JSONExtractString(raw_json, {_quote_sql(field_name)})"

def _metric_catalog() -> dict:
    return dict(fix_validation_cfg("metric_catalog", {}))

def _metric_summary_sql(metric_key: str, meta: dict) -> str:
    source_column = _safe_identifier(str(meta.get("source_column", metric_key)), metric_key)
    summary = SUMMARY_FUNCTIONS.get(str(meta.get("summary", "avg")), "avg")
    return f"{summary}({source_column}) AS {metric_key}__summary"

def _metric_stats_sql(metric_key: str, meta: dict) -> list[str]:
    source_column = _safe_identifier(str(meta.get("source_column", metric_key)), metric_key)
    return [
        _metric_summary_sql(metric_key, meta),
        f"avg({source_column}) AS {metric_key}__mean",
        f"stddevSamp({source_column}) AS {metric_key}__std",
    ]

def _safe_pct_change(control: float, treatment: float) -> float:
    if abs(float(control or 0)) < 1e-9:
        if abs(float(treatment or 0)) < 1e-9:
            return 0.0
        return 100.0
    return ((float(treatment) - float(control)) / abs(float(control))) * 100.0

def _improvement_pct(metric_key: str, control: float, treatment: float) -> float:
    raw_change = _safe_pct_change(control, treatment)
    direction = str(_metric_catalog().get(metric_key, {}).get("direction", "lower_is_better"))
    return -raw_change if direction == "lower_is_better" else raw_change

def _welch_t_stat(control_mean: float, treatment_mean: float, control_std: float, treatment_std: float, control_n: int, treatment_n: int) -> float:
    denominator = math.sqrt(
        ((float(control_std or 0) ** 2) / max(int(control_n), 1))
        + ((float(treatment_std or 0) ** 2) / max(int(treatment_n), 1))
    )
    if denominator <= 1e-9:
        return 0.0
    return (float(treatment_mean or 0) - float(control_mean or 0)) / denominator

def _metric_status(metric_role: str, improvement: float, significant: bool, confidence: float) -> str:
    thresholds = dict(fix_validation_cfg("decision_thresholds", {}))
    stats_cfg = dict(fix_validation_cfg("statistical_test", {}))
    min_confidence = float(stats_cfg.get("minimum_confidence", 0.35) or 0.35)
    min_primary = float(thresholds.get("minimum_primary_improvement_pct", 5.0) or 5.0)
    watch_primary = float(thresholds.get("watch_primary_improvement_pct", 2.0) or 2.0)
    max_guardrail_regression = float(thresholds.get("maximum_guardrail_regression_pct", 5.0) or 5.0)

    if confidence < min_confidence:
        return "low_confidence"

    if metric_role == "guardrail":
        if improvement < -max_guardrail_regression:
            return "guardrail_regressed"
        return "guardrail_ok"

    if improvement >= min_primary and significant:
        return "validated_improvement"
    if improvement >= min_primary:
        return "directional_improvement"
    if improvement >= watch_primary:
        return "small_improvement"
    if improvement < -max_guardrail_regression:
        return "regressed"
    return "no_clear_change"

def _variant_candidates(values: list[str], preferred: list[str]) -> str:
    lower_to_original = {value.lower(): value for value in values}
    for preferred_value in preferred:
        if str(preferred_value).lower() in lower_to_original:
            return lower_to_original[str(preferred_value).lower()]
    return values[0] if values else ""

def _evaluate_rows(summary: pd.DataFrame, control_variant: str, treatment_variant: str) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame()

    control_row = summary[summary["variant"] == control_variant]
    treatment_row = summary[summary["variant"] == treatment_variant]
    if control_row.empty or treatment_row.empty:
        return pd.DataFrame()

    control = control_row.iloc[0]
    treatment = treatment_row.iloc[0]
    control_n = int(control.get("samples", 0) or 0)
    treatment_n = int(treatment.get("samples", 0) or 0)
    min_samples = int(fix_validation_cfg("minimum_samples_per_variant", 100) or 100)
    strong_multiplier = float(dict(fix_validation_cfg("statistical_test", {})).get("strong_sample_multiplier", 5) or 5)
    strong_target = max(float(min_samples) * strong_multiplier, float(min_samples))
    confidence = max(0.0, min(1.0, min(control_n, treatment_n) / strong_target))
    t_threshold = float(dict(fix_validation_cfg("statistical_test", {})).get("t_stat_threshold", 1.96) or 1.96)
    stats_enabled = bool(dict(fix_validation_cfg("statistical_test", {})).get("enabled", True))

    rows = []
    for metric_key, meta in _metric_catalog().items():
        role = str(meta.get("role", "primary"))
        label = str(meta.get("label", metric_key))
        unit = str(meta.get("unit", ""))
        weight = float(meta.get("weight", 1.0) or 1.0)

        control_value = float(control.get(f"{metric_key}__summary", 0) or 0)
        treatment_value = float(treatment.get(f"{metric_key}__summary", 0) or 0)
        control_mean = float(control.get(f"{metric_key}__mean", 0) or 0)
        treatment_mean = float(treatment.get(f"{metric_key}__mean", 0) or 0)
        control_std = float(control.get(f"{metric_key}__std", 0) or 0)
        treatment_std = float(treatment.get(f"{metric_key}__std", 0) or 0)

        raw_pct_change = _safe_pct_change(control_value, treatment_value)
        improvement = _improvement_pct(metric_key, control_value, treatment_value)
        t_stat = _welch_t_stat(control_mean, treatment_mean, control_std, treatment_std, control_n, treatment_n)
        # Direction-aware significance.
        direction = str(meta.get("direction", "lower_is_better"))
        direction_multiplier = -1.0 if direction == "lower_is_better" else 1.0
        directional_t = t_stat * direction_multiplier
        significant = directional_t >= t_threshold if stats_enabled else True
        status = _metric_status(role, improvement, significant, confidence)

        rows.append({
            "metric": metric_key,
            "metric_label": label,
            "role": role,
            "control_value": control_value,
            "treatment_value": treatment_value,
            "raw_pct_change": raw_pct_change,
            "improvement_pct": improvement,
            "t_stat": t_stat,
            "directional_t_stat": directional_t,
            "statistically_meaningful": significant,
            "metric_status": status,
            "unit": unit,
            "weight": weight,
            "control_samples": control_n,
            "treatment_samples": treatment_n,
            "validation_confidence": confidence,
        })

    return pd.DataFrame(rows).sort_values(["role", "improvement_pct"], ascending=[False, False])

def _decision(metric_df: pd.DataFrame) -> tuple[str, str]:
    if metric_df.empty:
        return "NO DATA", "No comparable control/treatment rows were found."

    confidence = float(metric_df["validation_confidence"].mean() or 0)
    min_confidence = float(dict(fix_validation_cfg("statistical_test", {})).get("minimum_confidence", 0.35) or 0.35)

    primary = metric_df[metric_df["role"] == "primary"]
    guardrails = metric_df[metric_df["role"] == "guardrail"]

    guardrail_failures = guardrails[guardrails["metric_status"] == "guardrail_regressed"]
    primary_regressions = primary[primary["metric_status"] == "regressed"]
    validated_primary = primary[primary["metric_status"] == "validated_improvement"]
    directional_primary = primary[primary["metric_status"].isin(["directional_improvement", "small_improvement"])]

    if confidence < min_confidence:
        return "LOW CONFIDENCE", "The comparison does not have enough balanced samples to make a reliable decision."
    if not guardrail_failures.empty:
        return "FAIL GUARDRAILS", "Treatment improved or changed performance but one or more guardrail metrics regressed."
    if not primary_regressions.empty:
        return "REGRESSED", "Treatment made one or more primary performance metrics worse."
    if not validated_primary.empty:
        return "VALIDATED", "Treatment produced statistically meaningful primary improvement and guardrails stayed within tolerance."
    if not directional_primary.empty:
        return "PROMISING", "Treatment shows directional improvement, but statistical confidence is not strong enough yet."
    return "INCONCLUSIVE", "No clear primary improvement was detected."

def _load_experiments(context: DashboardContext, raw_table: str, fields: dict[str, str]) -> pd.DataFrame:
    experiment_expr = _json_field_expr(fields["experiment_id"])
    variant_expr = _json_field_expr(fields["variant"])
    return query_df_named(
        "fix_validation_available_experiments",
        f"""
        SELECT
          {experiment_expr} AS experiment_id,
          {variant_expr} AS variant,
          min(event_time) AS first_seen,
          max(event_time) AS last_seen,
          count() AS samples,
          countDistinct(server_id) AS servers,
          countDistinct(build_version) AS builds,
          countDistinct(map_id) AS maps,
          countDistinct(zone_id) AS zones
        FROM {raw_table}
        WHERE event_time >= now() - INTERVAL {int(context.filters.time_window_minutes)} MINUTE
          AND {context.active_filter}
          AND {experiment_expr} != ''
          AND {variant_expr} != ''
        GROUP BY experiment_id, variant
        ORDER BY last_seen DESC, samples DESC
        LIMIT 500
        """,
        cache_policy="medium",
    )

def render(context: DashboardContext) -> None:
    raw_table = table_name("raw_events") if table_name("raw_events") != "raw_events" else "raw_events"
    fields = _experiment_fields()
    catalog = _metric_catalog()

    st.subheader("Fix Validation")
    st.caption(
        "Validate whether a recommended optimization actually improved performance while protecting guardrail metrics."
    )

    experiments = _load_experiments(context, raw_table, fields)

    if experiments.empty:
        st.info(
            "No experiment/fix-validation telemetry found in the active filter window. "
            "Generate data with --experiment-id and --experiment-variant, or widen the analysis window."
        )
        st.code(
            "python simulator/generate_traffic.py --scenario replication_overload --build-version 0.2.1 "
            "--experiment-id replication_radius_fix --experiment-variant control --fix-validation-mode control\n\n"
            "python simulator/generate_traffic.py --scenario replication_overload --build-version 0.2.1 "
            "--experiment-id replication_radius_fix --experiment-variant treatment --fix-validation-mode treatment_improved",
            language="bash",
        )
        return

    experiment_ids = experiments["experiment_id"].dropna().astype(str).unique().tolist()
    selected_experiment = st.selectbox(
        "Experiment / fix validation ID",
        experiment_ids,
        index=0,
        key="aegis_fix_validation_experiment_id",
    )

    experiment_rows = experiments[experiments["experiment_id"] == selected_experiment].copy()
    variants = experiment_rows["variant"].dropna().astype(str).unique().tolist()

    if len(variants) < 2:
        st.warning("This experiment needs at least two variants, such as control and treatment.")
        render_table(experiment_rows, height=260)
        return

    default_control = _variant_candidates(variants, list(fix_validation_cfg("default_control_variants", [])))
    default_treatment_candidates = [variant for variant in variants if variant != default_control]
    default_treatment = _variant_candidates(
        default_treatment_candidates,
        list(fix_validation_cfg("default_treatment_variants", [])),
    )

    left, right = st.columns(2)
    with left:
        control_variant = st.selectbox(
            "Control variant",
            variants,
            index=variants.index(default_control) if default_control in variants else 0,
            key="aegis_fix_validation_control_variant",
        )
    with right:
        treatment_variant = st.selectbox(
            "Treatment variant",
            variants,
            index=variants.index(default_treatment) if default_treatment in variants else min(1, len(variants) - 1),
            key="aegis_fix_validation_treatment_variant",
        )

    if control_variant == treatment_variant:
        st.warning("Choose two different variants.")
        return

    metric_sql_parts = []
    for metric_key, meta in catalog.items():
        metric_sql_parts.extend(_metric_stats_sql(metric_key, meta))
    metric_sql = ",\n          ".join(metric_sql_parts)

    experiment_expr = _json_field_expr(fields["experiment_id"])
    variant_expr = _json_field_expr(fields["variant"])
    change_expr = _json_field_expr(fields["change_id"])
    plan_expr = _json_field_expr(fields["validation_plan_id"])

    summary = query_df_named(
        "fix_validation_variant_metric_summary",
        f"""
        SELECT
          {variant_expr} AS variant,
          anyLast({change_expr}) AS change_id,
          anyLast({plan_expr}) AS validation_plan_id,
          count() AS samples,
          countDistinct(server_id) AS servers,
          countDistinct(build_version) AS builds,
          countDistinct(map_id) AS maps,
          countDistinct(zone_id) AS zones,
          {metric_sql}
        FROM {raw_table}
        WHERE event_time >= now() - INTERVAL {int(context.filters.time_window_minutes)} MINUTE
          AND {context.active_filter}
          AND {experiment_expr} = {_quote_sql(selected_experiment)}
          AND {variant_expr} IN ({_quote_sql(control_variant)}, {_quote_sql(treatment_variant)})
        GROUP BY variant
        """,
        cache_policy="medium",
    )

    metric_df = _evaluate_rows(summary, control_variant, treatment_variant)
    decision, decision_copy = _decision(metric_df)

    st.markdown(
        f"""
        <div class="pressure-callout">
          <b>Validation decision:</b> {decision} · Comparing <b>{control_variant}</b> against <b>{treatment_variant}</b>
          for <b>{selected_experiment}</b>. {decision_copy}
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_paper_metric("Decision", decision)
    with k2:
        render_paper_metric("Control samples", str(int(summary[summary["variant"] == control_variant]["samples"].iloc[0]) if not summary[summary["variant"] == control_variant].empty else 0))
    with k3:
        render_paper_metric("Treatment samples", str(int(summary[summary["variant"] == treatment_variant]["samples"].iloc[0]) if not summary[summary["variant"] == treatment_variant].empty else 0))
    with k4:
        render_paper_metric("Validated primary", str(int((metric_df["metric_status"] == "validated_improvement").sum()) if not metric_df.empty else 0))
    with k5:
        render_paper_metric("Guardrail failures", str(int((metric_df["metric_status"] == "guardrail_regressed").sum()) if not metric_df.empty else 0))

    if metric_df.empty:
        st.info("No metric comparison rows were available.")
        return

    left_chart, right_chart = st.columns([1.0, 1.0])
    with left_chart:
        chart = metric_df.copy()
        chart["signed_result"] = chart["improvement_pct"]
        render_horizontal_bar_chart(
            chart.sort_values("signed_result", ascending=False),
            x="signed_result",
            y="metric_label",
            tooltip_columns=[
                "metric_label",
                "role",
                "control_value",
                "treatment_value",
                "improvement_pct",
                "metric_status",
                "statistically_meaningful",
                "unit",
            ],
            height=430,
            x_title="Improvement vs control (%)",
        )

    with right_chart:
        render_horizontal_bar_chart(
            metric_df.sort_values("directional_t_stat", ascending=False),
            x="directional_t_stat",
            y="metric_label",
            tooltip_columns=[
                "metric_label",
                "role",
                "directional_t_stat",
                "statistically_meaningful",
                "validation_confidence",
                "metric_status",
            ],
            height=430,
            x_title="Direction-aware t-statistic",
        )

    st.markdown('<div class="pressure-section-title">Validation Metrics</div>', unsafe_allow_html=True)
    display_cols = [
        "metric_label",
        "role",
        "control_value",
        "treatment_value",
        "raw_pct_change",
        "improvement_pct",
        "t_stat",
        "directional_t_stat",
        "statistically_meaningful",
        "metric_status",
        "unit",
        "control_samples",
        "treatment_samples",
        "validation_confidence",
    ]
    render_table(metric_df[[col for col in display_cols if col in metric_df.columns]], height=470)

    st.markdown('<div class="pressure-section-title">Variant Summary</div>', unsafe_allow_html=True)
    render_table(summary, height=320)

    with st.expander("Variant timeline", expanded=False):
        timeline_metric = st.selectbox(
            "Timeline metric",
            list(catalog.keys()),
            index=0,
            format_func=lambda key: str(catalog[key].get("label", key)),
            key="aegis_fix_validation_timeline_metric",
        )
        source_column = _safe_identifier(str(catalog[timeline_metric].get("source_column", timeline_metric)), timeline_metric)
        summary_func = SUMMARY_FUNCTIONS.get(str(catalog[timeline_metric].get("summary", "avg")), "avg")

        timeline = query_df_named(
            "fix_validation_variant_timeline",
            f"""
            SELECT
              toStartOfInterval(event_time, INTERVAL 30 SECOND) AS window_start,
              {variant_expr} AS variant,
              {summary_func}({source_column}) AS metric_value
            FROM {raw_table}
            WHERE event_time >= now() - INTERVAL {int(context.filters.time_window_minutes)} MINUTE
              AND {context.active_filter}
              AND {experiment_expr} = {_quote_sql(selected_experiment)}
              AND {variant_expr} IN ({_quote_sql(control_variant)}, {_quote_sql(treatment_variant)})
            GROUP BY window_start, variant
            ORDER BY window_start ASC
            LIMIT 1500
            """,
            cache_policy="short",
        )

        if timeline.empty:
            st.info("No timeline rows available for this experiment.")
        else:
            wide = timeline.pivot_table(index="window_start", columns="variant", values="metric_value", aggfunc="mean").reset_index()
            render_multi_metric_timeline(
                wide,
                x="window_start",
                metrics=[col for col in wide.columns if col != "window_start"],
                height=430,
                title=str(catalog[timeline_metric].get("label", timeline_metric)),
            )

    with st.expander("Experiment inventory and configuration", expanded=False):
        render_table(experiment_rows, height=260)
        st.json({
            "experiment_fields": fields,
            "minimum_samples_per_variant": fix_validation_cfg("minimum_samples_per_variant", 100),
            "statistical_test": fix_validation_cfg("statistical_test", {}),
            "decision_thresholds": fix_validation_cfg("decision_thresholds", {}),
            "metric_catalog": catalog,
        })
