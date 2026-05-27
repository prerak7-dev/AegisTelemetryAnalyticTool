from __future__ import annotations

import streamlit as st

def inject_global_styles() -> None:
    """Inject square-edged, high-contrast dashboard styles.

    This file owns visual design only. Developers adding new views should avoid
    putting large CSS blocks into workspace files; add reusable classes here.
    """
    st.markdown(
        """
        <style>
          :root {
            --aegis-bg: #34313d;
            --aegis-bg-2: #2c2934;
            --aegis-bg-3: #26232c;
            --aegis-surface: #efefef;
            --aegis-surface-2: #dddde0;
            --aegis-ink: #25232a;
            --aegis-text: #f4f4f4;
            --aegis-muted: #c5c3cb;
            --aegis-line: #4a4654;
            --aegis-line-2: #bebec2;
            --aegis-blue: #56B4E9;
            --aegis-orange: #E69F00;
            --aegis-green: #009E73;
            --aegis-red: #D55E00;
            --aegis-purple: #CC79A7;
          }

          html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }

          .stApp {
            background:
              linear-gradient(135deg, transparent 0 8%, #9b9ba1 8% 18%, transparent 18%),
              linear-gradient(180deg, var(--aegis-bg) 0%, var(--aegis-bg-2) 100%);
            color: var(--aegis-text);
          }

          .block-container {
            padding-top: 1.2rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
            padding-bottom: 2rem;
            max-width: 1520px;
          }

          [data-testid="stSidebar"] {
            min-width: 310px;
            background: linear-gradient(180deg, #2a2730 0%, #24212a 100%);
            border-right: 1px solid var(--aegis-line);
          }

          [data-testid="stSidebar"] * {
            color: var(--aegis-text);
          }

          [data-testid="stSidebar"] h2,
          [data-testid="stSidebar"] h3 {
            font-size: 0.92rem;
            letter-spacing: 0.12em;
            border-bottom: 1px solid var(--aegis-line);
            padding-bottom: 0.55rem;
            margin-top: 1.15rem;
          }

          [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #ebecee;
            color: var(--aegis-ink);
            border: 1px solid #bebec2;
            border-radius: 0;
          }

          [data-testid="stSidebar"] [data-baseweb="select"] *,
          [data-testid="stSidebar"] [data-baseweb="popover"] *,
          [data-testid="stSidebar"] div[role="option"],
          [data-testid="stSidebar"] div[role="listbox"] *,
          div[data-baseweb="popover"] *,
          div[role="option"] {
            color: #25232a !important;
          }

          [data-testid="stSidebar"] input,
          [data-testid="stSidebar"] textarea {
            border-radius: 0 !important;
          }

          h1, h2, h3 {
            letter-spacing: -0.04em;
            text-transform: uppercase;
          }

          .hero-shell {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--aegis-line);
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
            padding: 28px 32px 24px;
            margin-bottom: 1.15rem;
            box-shadow: 0 18px 45px rgba(0,0,0,0.16);
          }

          .hero-shell::after {
            content: "";
            position: absolute;
            left: -30px;
            bottom: -30px;
            width: 220px;
            height: 220px;
            background: linear-gradient(135deg, #9b9ba1 0%, #9b9ba1 50%, transparent 50%);
            opacity: 0.28;
          }

          .hero-kicker {
            position: relative;
            z-index: 1;
            color: var(--aegis-muted);
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0.18em;
            font-weight: 800;
          }

          .hero-title {
            position: relative;
            z-index: 1;
            max-width: 1120px;
            font-size: clamp(2.8rem, 5.5vw, 5.8rem);
            line-height: 0.92;
            letter-spacing: -0.08em;
            font-weight: 900;
            margin: 0.25rem 0 0.85rem;
          }

          .hero-subtitle {
            position: relative;
            z-index: 1;
            max-width: 980px;
            color: #dddce3;
            font-size: 1.0rem;
            border-left: 4px solid #d8d8dc;
            padding-left: 1rem;
          }

          .dossier-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--aegis-line);
            padding: 16px 18px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.12);
          }

          .dossier-card h2,
          .dossier-card h3 {
            margin-top: 0 !important;
          }

          .paper-card {
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, var(--aegis-surface) 0%, var(--aegis-surface-2) 100%);
            color: var(--aegis-ink);
            border: 1px solid var(--aegis-line-2);
            padding: 16px 18px;
            min-height: 108px;
          }

          .paper-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 6px;
            height: 100%;
            background: #56B4E9;
          }

          .paper-card .label {
            font-size: 0.70rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: rgba(37,35,42,0.70);
            font-weight: 800;
          }

          .paper-card .value {
            font-size: 2.0rem;
            line-height: 1.0;
            font-weight: 900;
            color: var(--aegis-ink);
            margin-top: 0.55rem;
            font-variant-numeric: tabular-nums;
          }

          .folder-tab-note {
            color: var(--aegis-muted);
            font-size: 0.90rem;
            margin-top: -0.25rem;
            margin-bottom: 0.9rem;
          }

          div[role="radiogroup"] {
            gap: 0.18rem !important;
          }

          div[role="radiogroup"] label {
            background: linear-gradient(180deg, #ececed 0%, #d8d8dc 100%);
            color: var(--aegis-ink) !important;
            padding: 0.7rem 1.05rem !important;
            border: 1px solid #bdbdc2;
            box-shadow: none;
            transform: none;
            transition: background 140ms ease, border-color 140ms ease;
          }

          div[role="radiogroup"] label:hover {
            background: #ffffff;
            border-color: #ffffff;
          }

          div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none;
          }

          .ops-banner {
            display: grid;
            grid-template-columns: 260px 1fr;
            gap: 1.25rem;
            align-items: center;
            padding: 16px 18px;
            margin: 6px 0 18px;
            background: #ececed;
            color: #25232a;
            border-left: 8px solid #56B4E9;
            border-top: 1px solid #bebec2;
            border-right: 1px solid #bebec2;
            border-bottom: 1px solid #bebec2;
          }

          .ops-banner.sev-critical { border-left-color: #D55E00; }
          .ops-banner.sev-warning { border-left-color: #E69F00; }
          .ops-banner.sev-info { border-left-color: #009E73; }

          .ops-eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: rgba(37,35,42,0.70);
            font-size: 0.70rem;
            font-weight: 900;
          }

          .ops-status {
            font-size: 2.2rem;
            line-height: 1;
            letter-spacing: -0.06em;
            font-weight: 950;
          }

          .ops-copy {
            font-size: 1.02rem;
            font-weight: 650;
            color: rgba(37,35,42,0.82);
          }

          .section-label {
            color: #e9e9ee;
            font-size: 0.88rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            font-weight: 900;
            margin: 1.2rem 0 0.5rem;
          }

          .incident-card {
            background: #ececed;
            color: #25232a;
            border: 1px solid #bebec2;
            border-left: 8px solid #56B4E9;
            padding: 16px 18px;
            margin-bottom: 12px;
          }

          .incident-card.sev-critical { border-left-color: #D55E00; }
          .incident-card.sev-warning { border-left-color: #E69F00; }
          .incident-card.sev-info { border-left-color: #009E73; }

          .incident-topline {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            color: rgba(37,35,42,0.67);
            font-size: 0.72rem;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            font-weight: 900;
            margin-bottom: 0.5rem;
          }

          .incident-title {
            font-size: 1.45rem;
            line-height: 1.05;
            text-transform: uppercase;
            letter-spacing: -0.04em;
            font-weight: 950;
            margin-bottom: 0.35rem;
          }

          .incident-meta {
            font-size: 0.86rem;
            color: rgba(37,35,42,0.75);
            margin-bottom: 0.75rem;
          }

          .incident-body {
            font-size: 0.96rem;
            color: rgba(37,35,42,0.82);
            margin-bottom: 0.85rem;
          }

          .incident-action {
            background: rgba(37,35,42,0.08);
            border-left: 4px solid rgba(37,35,42,0.35);
            padding: 10px 12px;
            font-size: 0.94rem;
          }

          [data-testid="stDataFrame"] {
            border: 1px solid var(--aegis-line);
            background: rgba(255,255,255,0.03);
            font-variant-numeric: tabular-nums;
          }

          [data-testid="stDataFrame"] [role="columnheader"] {
            background: #e7e7ea !important;
            color: #1f1d24 !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            border-bottom: 1px solid #bdbdc2 !important;
          }

          [data-testid="stDataFrame"] [role="gridcell"] {
            border-color: rgba(255,255,255,0.06) !important;
          }

          div[data-testid="stExpander"] {
            border: 1px solid var(--aegis-line) !important;
            background: rgba(255,255,255,0.025) !important;
          }

          div[data-testid="stExpander"] summary {
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 800;
          }

          .stAlert {
            border: 1px solid var(--aegis-line);
            background: rgba(255,255,255,0.04);
          }

          .stButton > button,
          button[kind="primary"] {
            border: 1px solid #bdbdc2;
            background: linear-gradient(180deg, #ececed 0%, #d8d8dc 100%);
            color: var(--aegis-ink);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 800;
            box-shadow: none;
          }

          .stButton > button:hover,
          button[kind="primary"]:hover {
            background: #ffffff;
            border-color: #ffffff;
          }

          .stSelectbox label, .stMultiSelect label, .stToggle label {
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.76rem;
            color: var(--aegis-muted);
          }

          .stCodeBlock, pre, code {
            border-radius: 0 !important;
          }

          .element-container, .stMarkdown, .stHorizontalBlock, .stVerticalBlock, .stAlert, .stDataFrame,
          .paper-card, .dossier-card, .hero-shell, div[role="radiogroup"] label, [data-testid="stMetric"],
          div[data-testid="stExpander"] {
            border-radius: 0 !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
