from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.performance_config import analyst_toolkit_cfg
from services.dashboard.query import query_df_named

ALL_TEMPLATE_CATEGORIES = "All templates"

def _candidate_path(configured_path: str, fallback_relative: str) -> Path:
    candidates = [
        Path(str(configured_path)),
        Path(fallback_relative),
        Path.cwd() / fallback_relative,
        Path(__file__).resolve().parents[3] / fallback_relative,
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]

def _template_dir() -> Path:
    return _candidate_path(str(analyst_toolkit_cfg("sql_template_dir", "/app/sql/analyst_templates")), "sql/analyst_templates")

def _notebook_dir() -> Path:
    return _candidate_path(str(analyst_toolkit_cfg("notebook_dir", "/app/notebooks")), "notebooks")

def _safe_limit(value: int) -> int:
    options = list(analyst_toolkit_cfg("export_row_limit_options", [100, 500, 1000, 2500, 5000, 10000]))
    max_allowed = max(int(v) for v in options) if options else 10000
    return max(1, min(int(value), max_allowed))

def _render_file_downloads(directory: Path, pattern: str, mime: str) -> pd.DataFrame:
    rows = []
    if not directory.exists():
        return pd.DataFrame(rows)

    for file_path in sorted(directory.glob(pattern)):
        if not file_path.is_file():
            continue
        rows.append({
            "name": file_path.name,
            "path": str(file_path),
            "size_kb": round(file_path.stat().st_size / 1024, 1),
        })
    return pd.DataFrame(rows)

def _template_values(context: DashboardContext, limit: int) -> dict[str, str]:
    filters = context.filters
    return {
        "time_filter": filters.time_filter,
        "incident_time_filter": filters.incident_time_filter,
        "event_time_filter": f"event_time >= now() - INTERVAL {int(filters.time_window_minutes)} MINUTE",
        "quality_time_filter": filters.quality_time_filter,
        "active_filter": context.active_filter,
        "source_filter": context.source_filter,
        "region_filter": context.region_filter,
        "server_filter": context.server_filter,
        "limit": str(_safe_limit(limit)),
    }

def _load_template_sql(template_file: str) -> str:
    file_name = Path(template_file).name
    path = _template_dir() / file_name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def _apply_template(template_sql: str, context: DashboardContext, limit: int) -> str:
    values = _template_values(context, limit)
    return template_sql.format(**values)

def _to_json_bytes(df: pd.DataFrame) -> bytes:
    return df.to_json(orient="records", date_format="iso", indent=2).encode("utf-8")

def render(context: DashboardContext) -> None:
    st.subheader("Analyst Toolkit")
    st.caption(
        "Export reusable evidence, inspect SQL templates, and open notebook workflows for deeper analysis."
    )

    templates = list(analyst_toolkit_cfg("templates", []))
    sql_dir = _template_dir()
    notebook_dir = _notebook_dir()
    limit_options = list(analyst_toolkit_cfg("export_row_limit_options", [100, 500, 1000, 2500, 5000, 10000]))
    default_limit = int(analyst_toolkit_cfg("export_row_limit_default", 1000) or 1000)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_paper_metric("SQL templates", str(len(templates)))
    with k2:
        render_paper_metric("Notebooks", str(len(list(notebook_dir.glob("*.ipynb"))) if notebook_dir.exists() else 0))
    with k3:
        render_paper_metric("Execution", "Enabled" if analyst_toolkit_cfg("allow_template_execution", True) else "Disabled")
    with k4:
        render_paper_metric("Default rows", str(default_limit))

    st.markdown(
        """
        <div class="pressure-callout">
          <b>Analyst workflow:</b> choose a template, preview the filter-aware SQL, run it against the current dashboard filters,
          then export CSV/JSON or continue the deeper investigation in a notebook.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not templates:
        st.warning("No analyst SQL templates are configured.")
        return

    template_labels = [f"{item.get('title', item.get('id', 'template'))} · {item.get('id', '')}" for item in templates]
    selected_label = st.selectbox("SQL template", template_labels, index=0, key="aegis_analyst_template_select")
    selected_template = templates[template_labels.index(selected_label)]

    row_limit = st.selectbox(
        "Export row limit",
        limit_options,
        index=limit_options.index(default_limit) if default_limit in limit_options else 0,
        key="aegis_analyst_export_row_limit",
    )

    template_sql = _load_template_sql(str(selected_template.get("file", "")))
    if not template_sql:
        st.error(f"Template file not found: {selected_template.get('file', '')}")
        return

    try:
        rendered_sql = _apply_template(template_sql, context, int(row_limit))
    except Exception as exc:
        st.error(f"Could not render SQL template: {exc}")
        st.code(template_sql, language="sql")
        return

    st.write(f"**Description:** {selected_template.get('description', '')}")

    with st.expander("Preview rendered SQL", expanded=False):
        st.code(rendered_sql, language="sql")

    run_enabled = bool(analyst_toolkit_cfg("allow_template_execution", True))
    run_clicked = st.button(
        "Run export query",
        type="primary",
        disabled=not run_enabled,
        key="aegis_analyst_run_export_query",
    )

    if not run_enabled:
        st.info("Template execution is disabled by configuration. You can still copy or download the SQL templates.")

    if run_clicked:
        try:
            df = query_df_named(
                f"analyst_toolkit_{selected_template.get('id', 'template')}",
                rendered_sql,
                cache_policy="short",
            )
        except Exception as exc:
            st.error(f"Query failed: {exc}")
            return

        st.markdown('<div class="pressure-section-title">Export Result</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            render_paper_metric("Rows", str(len(df)))
        with c2:
            render_paper_metric("Columns", str(len(df.columns)))
        with c3:
            render_paper_metric("Template", str(selected_template.get("id", "")))

        if df.empty:
            st.info("The query returned no rows. Widen the analysis window or relax filters.")
        else:
            render_table(df, height=520)

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            json_bytes = _to_json_bytes(df)
            base_name = f"analyst_export_{selected_template.get('id', 'template')}"
            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "Download CSV",
                    data=csv_bytes,
                    file_name=f"{base_name}.csv",
                    mime="text/csv",
                )
            with d2:
                st.download_button(
                    "Download JSON",
                    data=json_bytes,
                    file_name=f"{base_name}.json",
                    mime="application/json",
                )

    st.markdown('<div class="pressure-section-title">Reusable SQL Templates</div>', unsafe_allow_html=True)
    sql_files = _render_file_downloads(sql_dir, "*.sql", "text/sql")
    if sql_files.empty:
        st.info(f"No SQL templates found at {sql_dir}")
    else:
        render_table(sql_files, height=260)
        selected_sql = st.selectbox("Download SQL template", sql_files["name"].tolist(), key="aegis_analyst_sql_download")
        sql_path = sql_dir / selected_sql
        st.download_button(
            "Download selected SQL",
            data=sql_path.read_text(encoding="utf-8"),
            file_name=selected_sql,
            mime="text/sql",
        )

    st.markdown('<div class="pressure-section-title">Analyst Notebooks</div>', unsafe_allow_html=True)
    notebooks = _render_file_downloads(notebook_dir, "*.ipynb", "application/x-ipynb+json")
    if notebooks.empty:
        st.info(f"No notebooks found at {notebook_dir}")
    else:
        render_table(notebooks, height=260)
        selected_nb = st.selectbox("Download notebook", notebooks["name"].tolist(), key="aegis_analyst_notebook_download")
        nb_path = notebook_dir / selected_nb
        st.download_button(
            "Download selected notebook",
            data=nb_path.read_bytes(),
            file_name=selected_nb,
            mime="application/x-ipynb+json",
        )

    with st.expander("Toolkit configuration", expanded=False):
        st.json({
            "sql_template_dir": str(sql_dir),
            "notebook_dir": str(notebook_dir),
            "export_row_limit_options": limit_options,
            "allow_template_execution": run_enabled,
            "templates": templates,
        })
