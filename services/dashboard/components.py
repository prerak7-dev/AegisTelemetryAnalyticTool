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
    st.dataframe(df, use_container_width=True, hide_index=True, height=height)

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
