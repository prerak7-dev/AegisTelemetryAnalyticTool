from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.performance_config import (
    get_performance_config,
    refresh_performance_config,
)

def _flatten_config(data: dict, prefix: str = "") -> list[dict]:
    rows: list[dict] = []
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            rows.extend(_flatten_config(value, path))
        else:
            rows.append({"setting": path, "value": value})
    return rows

def render(context: DashboardContext) -> None:
    st.subheader("Performance Configuration")
    st.caption(
        "Studio/game-specific settings for query budgets, table names, pressure scoring, baseline windows, "
        "pipeline health thresholds, cache policies, and feature flags."
    )

    config = get_performance_config()

    st.markdown(
        """
        <div class="pressure-callout">
          <b>Configuration path:</b> set <code>AEGIS_DASHBOARD_PERFORMANCE_CONFIG</code> to point to a JSON config.
          If unset, the dashboard uses <code>/app/config/dashboard_performance.json</code> and falls back to built-in defaults.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Reload performance configuration"):
        refresh_performance_config()
        st.rerun()

    tabs = st.tabs(["Flattened Settings", "Raw JSON", "Recommended Rollups"])

    with tabs[0]:
        rows = pd.DataFrame(_flatten_config(config))
        render_table(rows, height=520)

    with tabs[1]:
        st.code(json.dumps(config, indent=2), language="json")

    with tabs[2]:
        st.markdown(
            """
            These settings are intentionally configurable so the same dashboard can be adapted to different games.
            For high scale, configure the table names below and wire them to ClickHouse rollups/materialized views.
            """
        )
        table_rows = []
        for key, value in config.get("tables", {}).items():
            table_rows.append({"logical_table": key, "configured_name": value})
        render_table(pd.DataFrame(table_rows), height=260)

        st.markdown(
            """
            Recommended ClickHouse rollup scripts are included in:

            ```text
            sql/phase7_2_query_architecture_hardening.sql
            ```

            They are templates and are not automatically applied by Docker Compose. Apply them manually once you are ready
            to promote pressure scoring and leaderboard queries from dashboard-time computation into ClickHouse-time rollups.
            """
        )
