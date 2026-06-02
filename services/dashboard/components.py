from __future__ import annotations

import pandas as pd
import streamlit as st

def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-shell">
          <div class="hero-kicker">Aegis Analytics Tool</div>
          <div class="hero-title">Gameplay Performance Analysis</div>
          <div class="hero-subtitle">
            A real-time analytics command center for server pressure, hot-zone risk, source-schema lineage,
            telemetry quality, and evidence-backed optimization decisions in high-traffic live-service games.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

def render_paper_metric(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="paper-card">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_table(df: pd.DataFrame, *, height: int = 360) -> None:
    """Render a dataframe with horizontal scrolling when columns exceed width."""
    st.markdown('<div class="aegis-table-scroll-shell">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True, height=height)
    st.markdown('</div>', unsafe_allow_html=True)

def render_filter_context(context, *, workspace_label: str | None = None) -> None:
    """Render the active data scope so every chart/table has visible context."""
    filters = context.filters
    workspace = _escape_html(workspace_label or "Current Workspace")
    source = _escape_html(filters.selected_source_profile)
    region = _escape_html(filters.selected_region)
    server = _escape_html(getattr(context, "selected_server_display", filters.selected_server))
    window = _escape_html(f"Last {int(filters.time_window_minutes)} minutes")
    rows = _escape_html(str(int(filters.max_table_rows)))

    st.markdown(
        f"""
        <div class="filter-context-strip">
          <div class="filter-context-title">Filtered Data Scope / {workspace}</div>
          <div class="filter-context-chips">
            <span><b>Source</b>{source}</span>
            <span><b>Region</b>{region}</span>
            <span><b>Server</b>{server}</span>
            <span><b>Window</b>{window}</span>
            <span><b>Table Limit</b>{rows}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def severity_class(severity: str) -> str:
    severity = str(severity or "").lower()
    if severity == "critical":
        return "sev-critical"
    if severity == "warning":
        return "sev-warning"
    return "sev-info"

def render_status_banner(max_risk: float, max_p95_frame: float, impact_events: int, source_label: str) -> None:
    if max_risk >= 80 or max_p95_frame >= 75:
        status = "CRITICAL"
        css_class = "sev-critical"
        action = "Immediate live-ops and server engineering review recommended."
    elif max_risk >= 60 or max_p95_frame >= 50 or impact_events > 0:
        status = "WATCH"
        css_class = "sev-warning"
        action = "Monitor affected servers and validate likely gameplay/system drivers."
    else:
        status = "STABLE"
        css_class = "sev-info"
        action = "No urgent server-performance action detected in the selected window."

    st.markdown(
        f"""
        <div class="ops-banner {css_class}">
          <div>
            <div class="ops-eyebrow">Operational Status / {source_label}</div>
            <div class="ops-status">{status}</div>
          </div>
          <div class="ops-copy">{action}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_incident_card(inc: pd.Series) -> None:
    css_class = severity_class(str(inc.get("severity", "")))
    confidence = float(inc.get("confidence", 0) or 0)

    st.markdown(
        f"""
        <div class="incident-card {css_class}">
          <div class="incident-topline">
            <span>{str(inc.get("severity", "")).upper()}</span>
            <span>{inc.get("source_profile", "unknown")} / {inc.get("region", "unknown")}</span>
          </div>
          <div class="incident-title">{inc.get("likely_driver", "unknown")}</div>
          <div class="incident-meta">
            Server <b>{inc.get("server_id", "unknown")}</b> · Zone <b>{inc.get("zone_id", "unknown")}</b> · Confidence <b>{confidence:.2f}</b>
          </div>
          <div class="incident-body">{inc.get("symptom", "")}</div>
          <div class="incident-action"><b>Recommended action:</b> {inc.get("recommended_action", "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _escape_html(value: object) -> str:
    import html
    return html.escape(str(value if value is not None else ""))

def render_timeline_sequence_cards(sequence_df: pd.DataFrame) -> None:
    """Render root-cause sequence as reliable wrapped cards.

    This intentionally renders each card through its own `st.markdown` call.
    Rendering one large joined HTML blob can cause Streamlit/Markdown to display
    later cards as raw escaped HTML in some versions, especially when the page
    reruns during live refresh.
    """
    if sequence_df.empty:
        st.info("No root-cause sequence stages available.")
        return

    st.markdown('<div class="timeline-sequence-stack">', unsafe_allow_html=True)

    for _, row in sequence_df.iterrows():
        matched = bool(row.get("matched", False))
        status = "matched" if matched else "not observed"
        css_class = "" if matched else " unmatched"

        stage = _escape_html(row.get("stage", "Unknown stage"))
        stage_id = _escape_html(row.get("stage_id", "unknown_stage"))
        time_value = _escape_html(row.get("time", "—"))
        mode = _escape_html(row.get("mode", "unknown"))
        details = _escape_html(row.get("details", ""))

        card_html = f"""
        <div class="timeline-stage-card{css_class}">
          <div class="timeline-stage-topline">
            <span>{stage_id}</span>
            <span>{time_value}</span>
            <span>{mode}</span>
            <span class="timeline-stage-status">{status}</span>
          </div>
          <div class="timeline-stage-title">{stage}</div>
          <div class="timeline-stage-detail">{details}</div>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def pressure_status(score: float) -> tuple[str, str]:
    score = float(score or 0)
    if score >= 80:
        return "critical", "CRITICAL"
    if score >= 55:
        return "warning", "WATCH"
    return "stable", "STABLE"

def render_pressure_card(
    *,
    title: str,
    score: float,
    primary_value: str,
    driver: str,
    recommendation: str,
) -> None:
    """Render one live pressure card for Command Center.

    This is intentionally HTML-based because the dashboard visual language
    uses sharp, square dossier cards instead of rounded default widgets.
    """
    css_class, status = pressure_status(score)
    title = _escape_html(title)
    primary_value = _escape_html(primary_value)
    driver = _escape_html(driver)
    recommendation = _escape_html(recommendation)

    st.markdown(
        f"""
        <div class="pressure-card pressure-{css_class}">
          <div class="pressure-topline">
            <span>{title}</span>
            <span>{status}</span>
          </div>
          <div class="pressure-score">{float(score or 0):.0f}</div>
          <div class="pressure-primary">{primary_value}</div>
          <div class="pressure-driver">{driver}</div>
          <div class="pressure-recommendation">{recommendation}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
