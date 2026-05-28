from __future__ import annotations

import pandas as pd
import streamlit as st

from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.performance_config import cfg_get
from services.dashboard.query import clear_query_cache, get_query_history

def render(context: DashboardContext) -> None:
    st.subheader("Query Performance")
    st.caption(
        "Local dashboard diagnostics for query duration, budgets, cache policy, returned rows, and query errors. "
        "This helps keep the tool fast as the analytics surface grows."
    )

    history = get_query_history()

    if history.empty:
        st.info("No query diagnostics recorded yet. Visit a few workspaces or refresh the dashboard.")
        return

    clean = history.copy()
    clean["duration_ms"] = pd.to_numeric(clean["duration_ms"], errors="coerce").fillna(0)
    clean["budget_ms"] = pd.to_numeric(clean.get("budget_ms", 0), errors="coerce").fillna(0)
    clean["rows"] = pd.to_numeric(clean["rows"], errors="coerce").fillna(0).astype(int)
    clean["has_error"] = clean["error"].astype(str).str.len() > 0
    clean["over_budget"] = clean.get("over_budget", False).astype(bool)

    total_queries = len(clean)
    over_budget_queries = int(clean["over_budget"].sum())
    error_queries = int(clean["has_error"].sum())
    avg_duration = float(clean["duration_ms"].mean() or 0)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_paper_metric("Recorded queries", str(total_queries))
    with k2:
        render_paper_metric("Average ms", f"{avg_duration:.1f}")
    with k3:
        render_paper_metric("Over budget", str(over_budget_queries))
    with k4:
        render_paper_metric("Errors", str(error_queries))

    if st.button("Clear query diagnostics and cache"):
        clear_query_cache()
        st.rerun()

    st.markdown('<div class="pressure-section-title">Slowest Query Names</div>', unsafe_allow_html=True)
    by_name = (
        clean.groupby(["query_name", "cache_policy"], dropna=False)
        .agg(
            calls=("query_name", "count"),
            avg_ms=("duration_ms", "mean"),
            p95_ms=("duration_ms", lambda s: s.quantile(0.95)),
            max_ms=("duration_ms", "max"),
            avg_budget_ms=("budget_ms", "mean"),
            over_budget=("over_budget", "sum"),
            avg_rows=("rows", "mean"),
            errors=("has_error", "sum"),
        )
        .reset_index()
        .sort_values(["over_budget", "max_ms", "p95_ms"], ascending=False)
    )
    render_table(by_name, height=380)

    st.markdown('<div class="pressure-section-title">Recent Query Calls</div>', unsafe_allow_html=True)
    recent_cols = [
        "recorded_at",
        "query_name",
        "duration_ms",
        "budget_ms",
        "over_budget",
        "rows",
        "cache_policy",
        "cached",
        "sql_hash",
        "error",
    ]
    render_table(clean[[col for col in recent_cols if col in clean.columns]].tail(100).sort_index(ascending=False), height=440)

    st.markdown('<div class="pressure-section-title">Configured Cache TTLs</div>', unsafe_allow_html=True)
    ttl_rows = [
        {"cache_policy": key, "ttl_seconds": value}
        for key, value in dict(cfg_get("cache_policies", {})).items()
    ]
    render_table(pd.DataFrame(ttl_rows), height=200)

    st.markdown('<div class="pressure-section-title">Query Budget Guidance</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="pressure-callout">
          <b>Quality rule:</b> if a live query repeatedly exceeds budget, do not add more threads first.
          Prefer narrower filters, shorter result sets, lazy loading, rollup tables, or materialized views.
          Use <b>Performance Configuration</b> to tune budgets for your studio's infrastructure.
        </div>
        """,
        unsafe_allow_html=True,
    )
