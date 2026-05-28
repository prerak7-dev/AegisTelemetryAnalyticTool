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

          /* Phase 6.3 Incident Timeline readability fixes */
          .timeline-sequence-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            margin-top: 8px;
            margin-bottom: 18px;
          }

          .timeline-stage-card {
            background: #ececed;
            color: #25232a;
            border: 1px solid #bebec2;
            border-left: 8px solid #56B4E9;
            padding: 14px 16px;
            overflow-wrap: anywhere;
            word-break: break-word;
            white-space: normal;
          }

          .timeline-stage-card.unmatched {
            border-left-color: #D55E00;
            background: #f3f0ea;
          }

          .timeline-stage-topline {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 8px 14px;
            color: rgba(37,35,42,0.68);
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 900;
            margin-bottom: 6px;
          }

          .timeline-stage-title {
            font-size: 1.25rem;
            line-height: 1.08;
            text-transform: uppercase;
            letter-spacing: -0.035em;
            font-weight: 950;
            margin-bottom: 8px;
            overflow-wrap: anywhere;
            white-space: normal;
          }

          .timeline-stage-detail {
            font-size: 0.95rem;
            line-height: 1.45;
            color: rgba(37,35,42,0.84);
            overflow-wrap: anywhere;
            word-break: break-word;
            white-space: normal;
          }

          .timeline-stage-status {
            display: inline-block;
            padding: 2px 8px;
            border: 1px solid rgba(37,35,42,0.28);
            background: rgba(37,35,42,0.08);
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 900;
          }

          .timeline-note,
          .timeline-note *,
          .stCaption,
          [data-testid="stCaptionContainer"],
          [data-testid="stCaptionContainer"] *,
          [data-testid="stMarkdownContainer"] a {
            color: #f4f4f4 !important;
          }

          [data-testid="stMarkdownContainer"] a:hover {
            color: #ffffff !important;
            text-decoration-color: #ffffff !important;
          }

          /* Phase 6.3 grouped workspace navigation */
          .workspace-nav-shell {
            position: relative;
            border: 1px solid var(--aegis-line);
            background:
              linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.025)),
              rgba(38,35,44,0.94);
            padding: 14px 16px 16px;
            margin: 0 0 14px;
            overflow: visible;
          }

          .workspace-nav-shell::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, #56B4E9, #E69F00, #009E73);
            opacity: 0.9;
          }

          .workspace-nav-kicker {
            color: #f4f4f4 !important;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            font-weight: 900;
            margin-bottom: 4px;
          }

          .workspace-nav-title {
            color: #ffffff !important;
            font-size: 1.15rem;
            line-height: 1.08;
            letter-spacing: -0.035em;
            text-transform: uppercase;
            font-weight: 950;
            margin-bottom: 2px;
          }

          .workspace-nav-copy {
            color: #d9d8df !important;
            font-size: 0.88rem;
            margin-bottom: 10px;
          }

          .workspace-nav-shell [data-baseweb="select"] > div {
            border-radius: 0 !important;
            border: 1px solid #bebec2 !important;
            background: linear-gradient(180deg, #f5f5f6 0%, #dedee2 100%) !important;
            color: #25232a !important;
            transition: background 160ms ease, border-color 160ms ease, transform 160ms ease, box-shadow 160ms ease;
            box-shadow: none !important;
          }

          .workspace-nav-shell [data-baseweb="select"] > div:hover {
            background: #ffffff !important;
            border-color: #ffffff !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.16) !important;
          }

          .workspace-nav-shell [data-baseweb="select"] *,
          .workspace-nav-shell div[role="button"] *,
          div[data-baseweb="popover"] *,
          div[role="option"] {
            color: #25232a !important;
          }

          .workspace-nav-footer {
            color: #f4f4f4 !important;
            font-size: 0.82rem;
            margin-top: 8px;
          }

          /* Phase 6.4 two-tier tab navigation */
          .workspace-tabs-anchor {
            height: 0;
            margin: 0;
            padding: 0;
          }

          /* Override the previous dropdown-shell navigation. */
          .workspace-nav-shell,
          .workspace-nav-kicker,
          .workspace-nav-title,
          .workspace-nav-copy,
          .workspace-nav-footer {
            display: none !important;
          }

          /* Main group and sub-workspace radio rows. */
          div[role="radiogroup"] {
            width: 100%;
            gap: 0 !important;
            border-radius: 0 !important;
          }

          div[role="radiogroup"] label {
            position: relative;
            min-height: 44px;
            border-radius: 0 !important;
            border: 1px solid rgba(190,190,194,0.85) !important;
            border-right: 0 !important;
            background: linear-gradient(180deg, #f6f6f7 0%, #dedee2 100%) !important;
            color: #25232a !important;
            padding: 0.72rem 1.25rem !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 160ms ease,
              color 160ms ease,
              border-color 160ms ease,
              transform 160ms ease,
              box-shadow 160ms ease;
          }

          div[role="radiogroup"] label:last-child {
            border-right: 1px solid rgba(190,190,194,0.85) !important;
          }

          div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            border-color: #ffffff !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.16) !important;
            z-index: 2;
          }

          div[role="radiogroup"] label p,
          div[role="radiogroup"] label span,
          div[role="radiogroup"] label div {
            color: #25232a !important;
            font-weight: 850 !important;
            letter-spacing: 0.035em;
            text-transform: uppercase;
          }

          div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          /* Selected tab indicator. Streamlit/BaseWeb marks selected radio with aria-checked. */
          div[role="radiogroup"] label:has(input:checked),
          div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%) !important;
            border-color: #34313d !important;
            z-index: 3;
          }

          div[role="radiogroup"] label:has(input:checked) *,
          div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #ffffff !important;
          }

          div[role="radiogroup"] label:has(input:checked)::after,
          div[role="radiogroup"] label:has([aria-checked="true"])::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: -1px;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 180ms ease-out both;
          }

          @keyframes aegisTabUnderline {
            from {
              transform: scaleX(0);
              opacity: 0;
            }
            to {
              transform: scaleX(1);
              opacity: 1;
            }
          }

          /* Subnav row: lighter, glassier strip like the reference lower bar. */
          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"],
          .workspace-tabs-anchor.sub-tier ~ div div[role="radiogroup"] {
            background: rgba(255,255,255,0.08);
            border-top: 1px solid rgba(255,255,255,0.10);
            border-bottom: 1px solid rgba(255,255,255,0.10);
            animation: aegisSubnavFade 180ms ease-out both;
          }

          @keyframes aegisSubnavFade {
            from {
              opacity: 0;
              transform: translateY(-4px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          @media (prefers-reduced-motion: reduce) {
            div[role="radiogroup"] label,
            .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"],
            .workspace-tabs-anchor.sub-tier ~ div div[role="radiogroup"] {
              transition: none !important;
              animation: none !important;
            }
          }

          /* Phase 6.5 visually distinct sub-navigation */
          .workspace-subnav-context {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 6px 0 0;
            padding: 7px 10px 6px;
            background: rgba(255,255,255,0.055);
            border-left: 4px solid #56B4E9;
            border-top: 1px solid rgba(255,255,255,0.08);
            border-right: 1px solid rgba(255,255,255,0.08);
            color: #f4f4f4;
          }

          .workspace-subnav-eyebrow {
            font-size: 0.66rem;
            line-height: 1;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            font-weight: 950;
            color: #cfd0d8 !important;
          }

          .workspace-subnav-group {
            font-size: 0.82rem;
            line-height: 1;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            font-weight: 850;
            color: #ffffff !important;
          }

          /* Primary group row: larger and bolder. */
          .workspace-tabs-anchor.top-tier + div div[role="radiogroup"] label {
            min-height: 48px !important;
            padding: 0.84rem 1.35rem !important;
          }

          .workspace-tabs-anchor.top-tier + div div[role="radiogroup"] label p,
          .workspace-tabs-anchor.top-tier + div div[role="radiogroup"] label span,
          .workspace-tabs-anchor.top-tier + div div[role="radiogroup"] label div {
            font-size: 0.88rem !important;
            letter-spacing: 0.075em !important;
            font-weight: 950 !important;
          }

          /* Sub-navigation row: smaller, inset, secondary strip. */
          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] {
            padding: 0 0 8px 14px !important;
            background:
              linear-gradient(90deg, rgba(86,180,233,0.14), rgba(255,255,255,0.035)),
              rgba(255,255,255,0.035) !important;
            border-left: 4px solid #56B4E9 !important;
            border-bottom: 1px solid rgba(255,255,255,0.10) !important;
            animation: aegisSubnavFade 180ms ease-out both;
          }

          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label {
            min-height: 34px !important;
            margin-top: 8px !important;
            padding: 0.48rem 0.95rem !important;
            background: rgba(236,236,237,0.88) !important;
            border-color: rgba(190,190,194,0.70) !important;
            border-right: 1px solid rgba(190,190,194,0.70) !important;
            opacity: 0.92;
          }

          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label + label {
            margin-left: 6px !important;
          }

          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label p,
          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label span,
          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label div {
            font-size: 0.72rem !important;
            letter-spacing: 0.055em !important;
            font-weight: 820 !important;
          }

          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label:hover {
            opacity: 1;
            transform: translateY(-1px);
            background: #ffffff !important;
          }

          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label:has(input:checked),
          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: linear-gradient(180deg, #dedee2 0%, #cfd0d8 100%) !important;
            border-color: #56B4E9 !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label:has(input:checked) *,
          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #25232a !important;
          }

          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label:has(input:checked)::after,
          .workspace-tabs-anchor.sub-tier + div div[role="radiogroup"] label:has([aria-checked="true"])::after {
            display: none !important;
          }


          /* Phase 6.6 hover-expanded two-level workspace navigation */
          .workspace-subnav-context,
          .workspace-tabs-anchor,
          .workspace-subnav-eyebrow,
          .workspace-subnav-group {
            display: none !important;
          }

          .aegis-hover-nav {
            position: relative;
            z-index: 50;
            margin: 0 0 0;
            border: 1px solid rgba(190,190,194,0.75);
            border-bottom: 0;
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%);
          }

          .aegis-hover-primary-row {
            display: flex;
            flex-wrap: nowrap;
            align-items: stretch;
            min-height: 48px;
          }

          .aegis-hover-group {
            position: relative;
            flex: 0 0 auto;
          }

          .aegis-hover-group-button {
            appearance: none;
            border: 0;
            border-right: 1px solid rgba(190,190,194,0.75);
            border-radius: 0;
            min-height: 48px;
            padding: 0 24px;
            background: transparent;
            color: #25232a;
            font-size: 0.88rem;
            letter-spacing: 0.075em;
            text-transform: uppercase;
            font-weight: 900;
            cursor: default;
            transition:
              background 160ms ease,
              color 160ms ease,
              transform 160ms ease;
          }

          .aegis-hover-group.active > .aegis-hover-group-button,
          .aegis-hover-group:hover > .aegis-hover-group-button {
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%);
            color: #ffffff;
          }

          .aegis-hover-group.active > .aegis-hover-group-button::after,
          .aegis-hover-group:hover > .aegis-hover-group-button::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 160ms ease-out both;
          }

          .aegis-hover-subnav {
            position: absolute;
            left: 0;
            top: 100%;
            min-width: max(100%, 980px);
            display: flex;
            align-items: center;
            gap: 0;
            background: rgba(245,245,246,0.96);
            border-top: 1px solid rgba(190,190,194,0.65);
            border-right: 1px solid rgba(190,190,194,0.65);
            border-bottom: 1px solid rgba(190,190,194,0.65);
            box-shadow: 0 18px 28px rgba(0,0,0,0.16);
            opacity: 0;
            transform: translateY(-8px);
            pointer-events: none;
            transition:
              opacity 150ms ease,
              transform 150ms ease;
          }

          .aegis-hover-group:hover > .aegis-hover-subnav,
          .aegis-hover-subnav:hover {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
          }

          .aegis-hover-subnav-link {
            display: block;
            padding: 13px 28px;
            color: #4f4d55 !important;
            text-decoration: none !important;
            font-size: 0.82rem;
            letter-spacing: 0.03em;
            font-weight: 720;
            white-space: nowrap;
            border-right: 1px solid rgba(190,190,194,0.45);
            transition:
              color 140ms ease,
              background 140ms ease,
              transform 140ms ease;
          }

          .aegis-hover-subnav-link:hover {
            color: #25232a !important;
            background: #ffffff;
            transform: translateY(-1px);
          }

          .aegis-hover-subnav-link.active {
            color: #25232a !important;
            background: #ffffff;
            box-shadow: inset 0 -3px 0 #56B4E9;
            font-weight: 900;
          }

          .workspace-title-region {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0 12px;
            color: #f4f4f4;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 950;
          }

          .workspace-title-group {
            color: #cfd0d8;
            font-size: 0.82rem;
          }

          .workspace-title-current {
            color: #ffffff;
            font-size: 1.08rem;
          }

          .workspace-title-separator-img {
            height: 22px;
            width: auto;
            object-fit: contain;
            display: inline-block;
            filter: none;
          }

          .workspace-title-separator-fallback {
            color: #56B4E9;
            font-size: 1rem;
            font-weight: 900;
          }

          @media (max-width: 900px) {
            .aegis-hover-primary-row {
              overflow-x: auto;
            }

            .aegis-hover-group-button {
              padding: 0 16px;
              font-size: 0.78rem;
            }

            .aegis-hover-subnav {
              min-width: 720px;
            }
          }

          @media (prefers-reduced-motion: reduce) {
            .aegis-hover-group-button,
            .aegis-hover-subnav,
            .aegis-hover-subnav-link {
              transition: none !important;
              animation: none !important;
            }
          }


          /* Phase 6.8 hover navigation polish */
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link,
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link:link,
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link:visited,
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link:hover,
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link:active,
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link.active,
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link *,
          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link.active * {
            color: #3f3d45 !important;
          }

          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link.active {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
            font-weight: 900 !important;
          }

          .aegis-hover-nav .aegis-hover-subnav .aegis-hover-subnav-link:hover {
            background: #ffffff !important;
            color: #25232a !important;
          }

          .workspace-title-separator-img {
            height: 24px !important;
            width: 24px !important;
            object-fit: contain;
            display: inline-block;
          }


          /* Phase 6.9 state-driven workspace navigation */
          .aegis-hover-nav {
            display: none !important;
          }

          .aegis-state-nav {
            width: 100%;
            margin: 0;
            padding: 0;
          }

          .aegis-state-nav-primary {
            border: 1px solid rgba(190,190,194,0.75);
            border-bottom: 0;
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%);
          }

          .aegis-state-nav-sub {
            border: 1px solid rgba(190,190,194,0.60);
            background: rgba(245,245,246,0.96);
            box-shadow: 0 8px 18px rgba(0,0,0,0.10);
            animation: aegisSubnavFade 150ms ease-out both;
          }

          .aegis-state-nav div[role="radiogroup"] {
            gap: 0 !important;
            width: 100%;
            background: transparent !important;
            border: 0 !important;
            padding: 0 !important;
          }

          .aegis-state-nav div[role="radiogroup"] label {
            position: relative;
            border-radius: 0 !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .aegis-state-nav-primary div[role="radiogroup"] label {
            min-height: 48px !important;
            padding: 0.84rem 1.35rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.75) !important;
            background: transparent !important;
          }

          .aegis-state-nav-primary div[role="radiogroup"] label p,
          .aegis-state-nav-primary div[role="radiogroup"] label span,
          .aegis-state-nav-primary div[role="radiogroup"] label div {
            color: #25232a !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.075em !important;
            text-transform: uppercase !important;
            font-weight: 950 !important;
          }

          .aegis-state-nav-primary div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          .aegis-state-nav-primary div[role="radiogroup"] label:has(input:checked),
          .aegis-state-nav-primary div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%) !important;
            border-color: #34313d !important;
            z-index: 3;
          }

          .aegis-state-nav-primary div[role="radiogroup"] label:has(input:checked) *,
          .aegis-state-nav-primary div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #ffffff !important;
          }

          .aegis-state-nav-primary div[role="radiogroup"] label:has(input:checked)::after,
          .aegis-state-nav-primary div[role="radiogroup"] label:has([aria-checked="true"])::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 160ms ease-out both;
          }

          .aegis-state-nav-sub div[role="radiogroup"] label {
            min-height: 42px !important;
            padding: 0.68rem 1.45rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            background: transparent !important;
          }

          .aegis-state-nav-sub div[role="radiogroup"] label p,
          .aegis-state-nav-sub div[role="radiogroup"] label span,
          .aegis-state-nav-sub div[role="radiogroup"] label div,
          .aegis-state-nav-sub div[role="radiogroup"] label:has(input:checked) *,
          .aegis-state-nav-sub div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
            font-size: 0.80rem !important;
            letter-spacing: 0.035em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          .aegis-state-nav-sub div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          .aegis-state-nav-sub div[role="radiogroup"] label:has(input:checked),
          .aegis-state-nav-sub div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          .aegis-state-nav-sub div[role="radiogroup"] label:has(input:checked)::after,
          .aegis-state-nav-sub div[role="radiogroup"] label:has([aria-checked="true"])::after {
            display: none !important;
          }

          .aegis-state-nav div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          .workspace-title-region {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0 12px;
            color: #f4f4f4;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 950;
          }

          .workspace-title-group {
            color: #cfd0d8;
            font-size: 0.82rem;
          }

          .workspace-title-current {
            color: #ffffff;
            font-size: 1.08rem;
          }

          .workspace-title-separator-img {
            height: 24px !important;
            width: 24px !important;
            object-fit: contain;
            display: inline-block;
          }

          .workspace-title-separator-fallback {
            color: #56B4E9;
            font-size: 1rem;
            font-weight: 900;
          }

          @media (prefers-reduced-motion: reduce) {
            .aegis-state-nav div[role="radiogroup"] label {
              transition: none !important;
              animation: none !important;
            }
          }


          /* Phase 6.10 state-driven hover-style navigation */
          .aegis-hover-nav,
          .aegis-state-nav,
          .aegis-state-nav-primary,
          .aegis-state-nav-sub,
          .workspace-subnav-context,
          .workspace-tabs-anchor {
            display: none !important;
          }

          .aegis-state-hover-marker {
            height: 0;
            margin: 0;
            padding: 0;
          }

          /* Top primary group tab row: always visible. */
          .aegis-state-hover-primary + div div[role="radiogroup"] {
            width: 100%;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.75) !important;
            border-bottom: 0 !important;
            border-radius: 0 !important;
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%) !important;
            padding: 0 !important;
          }

          .aegis-state-hover-primary + div div[role="radiogroup"] label {
            position: relative;
            min-height: 48px !important;
            padding: 0.84rem 1.35rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.75) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .aegis-state-hover-primary + div div[role="radiogroup"] label p,
          .aegis-state-hover-primary + div div[role="radiogroup"] label span,
          .aegis-state-hover-primary + div div[role="radiogroup"] label div {
            color: #25232a !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.075em !important;
            text-transform: uppercase !important;
            font-weight: 950 !important;
          }

          .aegis-state-hover-primary + div div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          .aegis-state-hover-primary + div div[role="radiogroup"] label:has(input:checked),
          .aegis-state-hover-primary + div div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%) !important;
            border-color: #34313d !important;
            z-index: 3;
          }

          .aegis-state-hover-primary + div div[role="radiogroup"] label:has(input:checked) *,
          .aegis-state-hover-primary + div div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #ffffff !important;
          }

          .aegis-state-hover-primary + div div[role="radiogroup"] label:has(input:checked)::after,
          .aegis-state-hover-primary + div div[role="radiogroup"] label:has([aria-checked="true"])::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 160ms ease-out both;
          }

          /* Subnav row: native Streamlit radio, collapsed by default. */
          .aegis-state-hover-sub + div {
            max-height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            transform: translateY(-8px);
            transition:
              max-height 180ms ease,
              opacity 150ms ease,
              transform 150ms ease;
            position: relative;
            z-index: 55;
          }

          /* Reveal subnav while hovering top row, marker, or subnav area. */
          .aegis-state-hover-primary + div:hover + div + div,
          .aegis-state-hover-primary + div + div:hover + div,
          .aegis-state-hover-sub + div:hover {
            max-height: 76px !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            transform: translateY(0);
            overflow: visible !important;
          }

          .aegis-state-hover-sub + div div[role="radiogroup"] {
            width: 100%;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.65) !important;
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            box-shadow: 0 18px 28px rgba(0,0,0,0.16);
            padding: 0 !important;
          }

          .aegis-state-hover-sub + div div[role="radiogroup"] label {
            position: relative;
            min-height: 44px !important;
            padding: 0.70rem 1.45rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          /* Subnav text: always dark gray/black, including selected. */
          .aegis-state-hover-sub + div div[role="radiogroup"] label p,
          .aegis-state-hover-sub + div div[role="radiogroup"] label span,
          .aegis-state-hover-sub + div div[role="radiogroup"] label div,
          .aegis-state-hover-sub + div div[role="radiogroup"] label:has(input:checked) *,
          .aegis-state-hover-sub + div div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          .aegis-state-hover-sub + div div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          /* Selected subnav: only blue underline highlight, same dark text. */
          .aegis-state-hover-sub + div div[role="radiogroup"] label:has(input:checked),
          .aegis-state-hover-sub + div div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          .aegis-state-hover-sub + div div[role="radiogroup"] label:has(input:checked)::after,
          .aegis-state-hover-sub + div div[role="radiogroup"] label:has([aria-checked="true"])::after {
            display: none !important;
          }

          .aegis-state-hover-primary + div div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child,
          .aegis-state-hover-sub + div div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          .workspace-title-region {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0 12px;
            color: #f4f4f4;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 950;
          }

          .workspace-title-group {
            color: #cfd0d8;
            font-size: 0.82rem;
          }

          .workspace-title-current {
            color: #ffffff;
            font-size: 1.08rem;
          }

          .workspace-title-separator-img {
            height: 24px !important;
            width: 24px !important;
            object-fit: contain;
            display: inline-block;
          }

          .workspace-title-separator-fallback {
            color: #56B4E9;
            font-size: 1rem;
            font-weight: 900;
          }

          @media (prefers-reduced-motion: reduce) {
            .aegis-state-hover-primary + div div[role="radiogroup"] label,
            .aegis-state-hover-sub + div,
            .aegis-state-hover-sub + div div[role="radiogroup"] label {
              transition: none !important;
              animation: none !important;
            }
          }


          /* Phase 6.11 robust state-driven hover navigation */
          .aegis-hover-nav,
          .aegis-state-nav,
          .aegis-state-nav-primary,
          .aegis-state-nav-sub,
          .workspace-subnav-context,
          .workspace-tabs-anchor,
          .aegis-state-hover-marker {
            display: none !important;
          }

          .st-key-aegis_nav_hover_region {
            position: relative !important;
            z-index: 200 !important;
            overflow: visible !important;
            margin-bottom: 0 !important;
          }

          .aegis-nav-primary-marker,
          .aegis-nav-sub-marker {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
          }

          /* Primary group nav. */
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] {
            width: 100% !important;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.75) !important;
            border-bottom: 0 !important;
            border-radius: 0 !important;
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%) !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label {
            position: relative !important;
            min-height: 48px !important;
            padding: 0.84rem 1.35rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.75) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label p,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label span,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label div {
            color: #25232a !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.075em !important;
            text-transform: uppercase !important;
            font-weight: 950 !important;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%) !important;
            border-color: #34313d !important;
            z-index: 3;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #ffffff !important;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked)::after,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-primary-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"])::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 160ms ease-out both;
          }

          /* Subnav radio container: hidden by default. */
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] {
            position: absolute !important;
            left: 0 !important;
            top: 48px !important;
            min-width: min(980px, 100vw) !important;
            max-height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            transform: translateY(-8px);
            transition:
              max-height 180ms ease,
              opacity 150ms ease,
              transform 150ms ease;
            z-index: 260 !important;
          }

          /* Show subnav only while hovering the keyed nav region. */
          .st-key-aegis_nav_hover_region:hover div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] {
            max-height: 76px !important;
            opacity: 1 !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: translateY(0);
          }

          /* Subnav style: match Phase 6.8 hover dropdown visual language. */
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] {
            width: 100% !important;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.65) !important;
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            box-shadow: 0 18px 28px rgba(0,0,0,0.16) !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label {
            position: relative !important;
            min-height: 44px !important;
            padding: 0.70rem 1.45rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          /* Subnav text: dark gray/black for every state, selected included. */
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label p,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label span,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label div,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          /* Selected subnav: same dark text, only blue underline. */
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked)::after,
          .st-key-aegis_nav_hover_region div[data-testid="stMarkdownContainer"]:has(.aegis-nav-sub-marker)
            + div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"])::after {
            display: none !important;
          }

          /* Hide native radio circles. */
          .st-key-aegis_nav_hover_region div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          .workspace-title-region {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0 12px;
            color: #f4f4f4;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 950;
          }

          .workspace-title-group {
            color: #cfd0d8;
            font-size: 0.82rem;
          }

          .workspace-title-current {
            color: #ffffff;
            font-size: 1.08rem;
          }

          .workspace-title-separator-img {
            height: 24px !important;
            width: 24px !important;
            object-fit: contain;
            display: inline-block;
          }

          .workspace-title-separator-fallback {
            color: #56B4E9;
            font-size: 1rem;
            font-weight: 900;
          }

          @media (prefers-reduced-motion: reduce) {
            .st-key-aegis_nav_hover_region div[data-testid="stRadio"],
            .st-key-aegis_nav_hover_region div[data-testid="stRadio"] label {
              transition: none !important;
              animation: none !important;
            }
          }


          /* Phase 6.12 final state-driven hover nav fix */
          .aegis-hover-nav,
          .aegis-state-nav,
          .aegis-state-nav-primary,
          .aegis-state-nav-sub,
          .workspace-subnav-context,
          .workspace-tabs-anchor,
          .aegis-state-hover-marker,
          .aegis-nav-primary-marker,
          .aegis-nav-sub-marker {
            display: none !important;
          }

          /* Primary group row identified by radio aria-label. */
          div[role="radiogroup"][aria-label="Workspace group"] {
            width: 100% !important;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.75) !important;
            border-bottom: 0 !important;
            border-radius: 0 !important;
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%) !important;
            padding: 0 !important;
            position: relative !important;
            z-index: 300 !important;
          }

          div[role="radiogroup"][aria-label="Workspace group"] label {
            position: relative !important;
            min-height: 48px !important;
            padding: 0.84rem 1.35rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.75) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          div[role="radiogroup"][aria-label="Workspace group"] label p,
          div[role="radiogroup"][aria-label="Workspace group"] label span,
          div[role="radiogroup"][aria-label="Workspace group"] label div {
            color: #25232a !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.075em !important;
            text-transform: uppercase !important;
            font-weight: 950 !important;
          }

          div[role="radiogroup"][aria-label="Workspace group"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          div[role="radiogroup"][aria-label="Workspace group"] label:has(input:checked),
          div[role="radiogroup"][aria-label="Workspace group"] label:has([aria-checked="true"]) {
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%) !important;
            border-color: #34313d !important;
            z-index: 3;
          }

          div[role="radiogroup"][aria-label="Workspace group"] label:has(input:checked) *,
          div[role="radiogroup"][aria-label="Workspace group"] label:has([aria-checked="true"]) * {
            color: #ffffff !important;
          }

          div[role="radiogroup"][aria-label="Workspace group"] label:has(input:checked)::after,
          div[role="radiogroup"][aria-label="Workspace group"] label:has([aria-checked="true"])::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 160ms ease-out both;
          }

          /* Hide the whole Workspace radio widget wrapper by default. */
          div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Workspace"]) {
            max-height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            transform: translateY(-8px);
            transition:
              max-height 180ms ease,
              opacity 150ms ease,
              transform 150ms ease;
            position: relative !important;
            z-index: 310 !important;
            margin: 0 !important;
          }

          /*
             Reveal subnav when the top group radio or the subnav itself is hovered.
             This gives Phase 6.8-style hover dropdown behavior while keeping the
             radio widget state-driven.
          */
          body:has(div[role="radiogroup"][aria-label="Workspace group"]:hover)
            div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Workspace"]),
          div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Workspace"]):hover {
            max-height: 76px !important;
            opacity: 1 !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: translateY(0);
          }

          /* Subnavigation style: Phase 6.8-style light dropdown strip. */
          div[role="radiogroup"][aria-label="Workspace"] {
            width: 100% !important;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.65) !important;
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            box-shadow: 0 18px 28px rgba(0,0,0,0.16) !important;
            padding: 0 !important;
            position: relative !important;
            z-index: 320 !important;
          }

          div[role="radiogroup"][aria-label="Workspace"] label {
            position: relative !important;
            min-height: 44px !important;
            padding: 0.70rem 1.45rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          /* Subnav text: dark gray/black for every state, selected included. */
          div[role="radiogroup"][aria-label="Workspace"] label p,
          div[role="radiogroup"][aria-label="Workspace"] label span,
          div[role="radiogroup"][aria-label="Workspace"] label div,
          div[role="radiogroup"][aria-label="Workspace"] label:has(input:checked) *,
          div[role="radiogroup"][aria-label="Workspace"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          div[role="radiogroup"][aria-label="Workspace"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          /* Selected subnav: only blue underline highlight. */
          div[role="radiogroup"][aria-label="Workspace"] label:has(input:checked),
          div[role="radiogroup"][aria-label="Workspace"] label:has([aria-checked="true"]) {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          div[role="radiogroup"][aria-label="Workspace"] label:has(input:checked)::after,
          div[role="radiogroup"][aria-label="Workspace"] label:has([aria-checked="true"])::after {
            display: none !important;
          }

          /* Hide native radio circles for both nav rows. */
          div[role="radiogroup"][aria-label="Workspace group"] label[data-baseweb="radio"] > div:first-child,
          div[role="radiogroup"][aria-label="Workspace"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          .workspace-title-region {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0 12px;
            color: #f4f4f4;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 950;
          }

          .workspace-title-group {
            color: #cfd0d8;
            font-size: 0.82rem;
          }

          .workspace-title-current {
            color: #ffffff;
            font-size: 1.08rem;
          }

          .workspace-title-separator-img {
            height: 24px !important;
            width: 24px !important;
            object-fit: contain;
            display: inline-block;
          }

          .workspace-title-separator-fallback {
            color: #56B4E9;
            font-size: 1rem;
            font-weight: 900;
          }

          @media (prefers-reduced-motion: reduce) {
            div[data-testid="stRadio"]:has(div[role="radiogroup"][aria-label="Workspace"]),
            div[role="radiogroup"][aria-label="Workspace group"] label,
            div[role="radiogroup"][aria-label="Workspace"] label {
              transition: none !important;
              animation: none !important;
            }
          }


          /* Phase 6.13 per-group state-driven hover navigation */
          .aegis-hover-nav,
          .aegis-state-nav,
          .aegis-state-nav-primary,
          .aegis-state-nav-sub,
          .workspace-subnav-context,
          .workspace-tabs-anchor,
          .aegis-state-hover-marker,
          .aegis-nav-primary-marker,
          .aegis-nav-sub-marker {
            display: none !important;
          }

          .aegis-per-group-nav-shell {
            height: 0;
            margin: 0;
            padding: 0;
          }

          [data-testid="column"],
          [data-testid="column"] > div,
          div[class*="st-key-aegis_nav_group_"] {
            overflow: visible !important;
          }

          div[class*="st-key-aegis_nav_group_"] {
            position: relative !important;
            z-index: 300 !important;
          }

          div[class*="st-key-aegis_nav_group_"]:hover {
            z-index: 800 !important;
          }

          .aegis-main-group-tab {
            min-height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 1.35rem;
            border: 1px solid rgba(190,190,194,0.75);
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%);
            color: #25232a;
            cursor: default;
            transform: translateY(0);
            transition:
              background 140ms ease,
              color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .aegis-main-group-tab span {
            color: #25232a !important;
            font-size: 0.88rem;
            letter-spacing: 0.075em;
            text-transform: uppercase;
            font-weight: 950;
            white-space: nowrap;
          }

          .aegis-main-group-tab:hover,
          div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab {
            background: #ffffff;
            transform: translateY(-1px);
          }

          .aegis-main-group-tab.active,
          div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab.active {
            position: relative;
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%);
            border-color: #34313d;
            z-index: 3;
          }

          .aegis-main-group-tab.active span {
            color: #ffffff !important;
          }

          .aegis-main-group-tab.active::after,
          div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 160ms ease-out both;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] {
            position: absolute !important;
            left: 0 !important;
            top: 48px !important;
            min-width: max(100%, 980px) !important;
            max-height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            transform: translateY(-8px);
            transition:
              max-height 180ms ease,
              opacity 150ms ease,
              transform 150ms ease;
            z-index: 820 !important;
            margin: 0 !important;
          }

          div[class*="st-key-aegis_nav_group_"]:hover div[data-testid="stRadio"],
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"]:hover {
            max-height: 76px !important;
            opacity: 1 !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: translateY(0);
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] {
            width: 100% !important;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.65) !important;
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            box-shadow: 0 18px 28px rgba(0,0,0,0.16) !important;
            padding: 0 !important;
            display: flex !important;
            flex-wrap: nowrap !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label {
            position: relative !important;
            min-height: 44px !important;
            padding: 0.70rem 1.45rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
            white-space: nowrap !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label p,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label span,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label div,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked)::after,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"])::after {
            display: none !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          .workspace-title-region {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0 12px;
            color: #f4f4f4;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 950;
          }

          .workspace-title-group {
            color: #cfd0d8;
            font-size: 0.82rem;
          }

          .workspace-title-current {
            color: #ffffff;
            font-size: 1.08rem;
          }

          .workspace-title-separator-img {
            height: 24px !important;
            width: 24px !important;
            object-fit: contain;
            display: inline-block;
          }

          .workspace-title-separator-fallback {
            color: #56B4E9;
            font-size: 1rem;
            font-weight: 900;
          }

          @media (max-width: 900px) {
            div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] {
              min-width: 720px !important;
            }

            .aegis-main-group-tab {
              padding: 0 0.95rem;
            }

            .aegis-main-group-tab span {
              font-size: 0.76rem;
            }
          }

          @media (prefers-reduced-motion: reduce) {
            .aegis-main-group-tab,
            div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"],
            div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] label {
              transition: none !important;
              animation: none !important;
            }
          }


          /* Phase 6.14 subnav gap + width fix */
          /*
            The per-group hover nav is state-driven, but Streamlit wraps every
            markdown/radio element in extra block containers. In Phase 6.13 that
            allowed the subnav to render lower than the main tab, creating a
            hover gap. These stronger layout rules pin each group container to
            exactly one tab height and place the subnav directly beneath it.
          */

          div[class*="st-key-aegis_nav_group_"] {
            height: 48px !important;
            min-height: 48px !important;
            max-height: 48px !important;
            overflow: visible !important;
            position: relative !important;
            z-index: 300 !important;
          }

          div[class*="st-key-aegis_nav_group_"]:hover {
            z-index: 1000 !important;
          }

          div[class*="st-key-aegis_nav_group_"] [data-testid="stVerticalBlock"],
          div[class*="st-key-aegis_nav_group_"] [data-testid="stVerticalBlock"] > div,
          div[class*="st-key-aegis_nav_group_"] [data-testid="element-container"] {
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stMarkdownContainer"],
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
          }

          .aegis-main-group-tab {
            height: 48px !important;
            min-height: 48px !important;
            max-height: 48px !important;
            box-sizing: border-box !important;
          }

          /*
            Add a tiny invisible hover bridge and overlap the subnav by 1px.
            This prevents the menu from disappearing while the cursor moves from
            the main tab into the dropdown.
          */
          div[class*="st-key-aegis_nav_group_"]::after {
            content: "";
            position: absolute;
            left: 0;
            top: 46px;
            width: 100%;
            height: 10px;
            z-index: 810;
            background: transparent;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] {
            top: 47px !important;
            left: 0 !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 32px) !important;
          }

          div[class*="st-key-aegis_nav_group_"]:hover div[data-testid="stRadio"],
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"]:hover {
            max-height: 76px !important;
            opacity: 1 !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: translateY(0) !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 32px) !important;
            display: inline-flex !important;
            flex-wrap: nowrap !important;
            align-items: stretch !important;
            background: rgba(245,245,246,0.98) !important;
          }

          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:last-child {
            border-right: 0 !important;
          }

          /*
            The dropdown should end at the last tab, not continue as an empty
            white strip. Streamlit sometimes stretches child blocks to 100%;
            these rules keep all wrappers shrink-wrapped to the radio content.
          */
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] > div,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] > div > div {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 32px) !important;
          }

          /*
            Keep subnavigation text readable and consistent:
            dark gray/black for every state, with the selected item indicated
            only by the blue underline.
          */
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label p,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label span,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label div,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,
          div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
          }


          /* Phase 6.15 nav positioning + clickability fix */
          /*
            Root fix:
            - The subnav must be positioned relative to the actual top nav bar.
            - It must not sit below the breadcrumb/workspace title.
            - It must remain hoverable/clickable while moving the cursor down.
            - It must shrink-wrap to the last tab.
          */

          .aegis-hover-nav,
          .aegis-state-nav,
          .aegis-state-nav-primary,
          .aegis-state-nav-sub,
          .workspace-subnav-context,
          .workspace-tabs-anchor,
          .aegis-state-hover-marker,
          .aegis-nav-primary-marker,
          .aegis-nav-sub-marker,
          .aegis-per-group-nav-shell {
            display: none !important;
          }

          .st-key-aegis_nav_bar {
            position: relative !important;
            z-index: 5000 !important;
            height: 48px !important;
            min-height: 48px !important;
            max-height: 48px !important;
            overflow: visible !important;
            margin: 0 0 14px 0 !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_bar [data-testid="stHorizontalBlock"],
          .st-key-aegis_nav_bar [data-testid="column"],
          .st-key-aegis_nav_bar [data-testid="column"] > div {
            height: 48px !important;
            min-height: 48px !important;
            max-height: 48px !important;
            overflow: visible !important;
            margin-top: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
          }

          .st-key-aegis_nav_bar [data-testid="column"] {
            position: relative !important;
            z-index: 5000 !important;
          }

          .st-key-aegis_nav_bar [data-testid="column"]:hover {
            z-index: 7000 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] {
            position: relative !important;
            height: 48px !important;
            min-height: 48px !important;
            max-height: 48px !important;
            overflow: visible !important;
            margin: 0 !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] [data-testid="stVerticalBlock"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] [data-testid="stVerticalBlock"] > div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] [data-testid="element-container"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stMarkdownContainer"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
            overflow: visible !important;
          }

          .aegis-main-group-tab {
            height: 48px !important;
            min-height: 48px !important;
            max-height: 48px !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 1.35rem !important;
            border: 1px solid rgba(190,190,194,0.75) !important;
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%) !important;
            color: #25232a !important;
            cursor: default !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .aegis-main-group-tab span {
            color: #25232a !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.075em !important;
            text-transform: uppercase !important;
            font-weight: 950 !important;
            white-space: nowrap !important;
          }

          .aegis-main-group-tab:hover,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          .aegis-main-group-tab.active {
            position: relative !important;
            background: linear-gradient(180deg, #34313d 0%, #24212a 100%) !important;
            border-color: #34313d !important;
            z-index: 3 !important;
          }

          .aegis-main-group-tab.active span {
            color: #ffffff !important;
          }

          .aegis-main-group-tab.active::after,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 3px;
            background: #56B4E9;
            animation: aegisTabUnderline 160ms ease-out both;
          }

          /*
            This bridge fills the exact cursor path from the tab to the dropdown.
            The dropdown overlaps the tab by 1px, so there is literally no gap.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]::after {
            content: "";
            position: absolute;
            left: 0;
            top: 46px;
            width: 100%;
            height: 12px;
            z-index: 7100;
            background: transparent;
            pointer-events: auto;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] {
            position: absolute !important;
            left: 0 !important;
            top: 47px !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 32px) !important;
            max-height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            transform: translateY(-6px);
            transition:
              max-height 160ms ease,
              opacity 140ms ease,
              transform 140ms ease;
            z-index: 7200 !important;
            margin: 0 !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover div[data-testid="stRadio"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"]:hover {
            max-height: 80px !important;
            opacity: 1 !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: translateY(0) !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] > div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] > div > div {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 32px) !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 32px) !important;
            display: inline-flex !important;
            flex-wrap: nowrap !important;
            align-items: stretch !important;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.65) !important;
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            box-shadow: 0 18px 28px rgba(0,0,0,0.16) !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label {
            position: relative !important;
            min-height: 44px !important;
            padding: 0.70rem 1.45rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            white-space: nowrap !important;
            transition:
              background 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:last-child {
            border-right: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label p,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label span,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked)::after,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"])::after {
            display: none !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          .workspace-title-region {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 14px 0 12px;
            color: #f4f4f4;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 950;
          }

          .workspace-title-group {
            color: #cfd0d8;
            font-size: 0.82rem;
          }

          .workspace-title-current {
            color: #ffffff;
            font-size: 1.08rem;
          }

          .workspace-title-separator-img {
            height: 24px !important;
            width: 24px !important;
            object-fit: contain;
            display: inline-block;
          }

          @media (prefers-reduced-motion: reduce) {
            .aegis-main-group-tab,
            .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"],
            .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] label {
              transition: none !important;
              animation: none !important;
            }
          }


          /* Phase 6.16 flow-based subnav fix */
          /*
            This intentionally removes absolute-positioned subnav placement.
            The subnav now expands in normal flow directly under the hovered
            main tab. This avoids hardcoded top pixel values and eliminates the
            cursor gap that made the subnav impossible to click.
          */

          .st-key-aegis_nav_bar {
            position: relative !important;
            z-index: 5000 !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            overflow: visible !important;
            margin: 0 0 0.85rem 0 !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_bar [data-testid="stHorizontalBlock"],
          .st-key-aegis_nav_bar [data-testid="column"],
          .st-key-aegis_nav_bar [data-testid="column"] > div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] {
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            overflow: visible !important;
            margin: 0 !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_bar [data-testid="column"] {
            position: relative !important;
            z-index: 5000 !important;
          }

          .st-key-aegis_nav_bar [data-testid="column"]:hover {
            z-index: 7000 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] {
            position: relative !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] [data-testid="stVerticalBlock"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] [data-testid="stVerticalBlock"] > div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] [data-testid="element-container"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stMarkdownContainer"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
            overflow: visible !important;
          }

          .aegis-main-group-tab {
            min-block-size: 3rem !important;
            height: auto !important;
            max-height: none !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0.85rem 1.35rem !important;
            border: 1px solid rgba(190,190,194,0.75) !important;
            background: linear-gradient(180deg, #f7f7f8 0%, #e3e3e6 100%) !important;
            color: #25232a !important;
            cursor: default !important;
            transform: translateY(0);
            transition:
              background 140ms ease,
              color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          /*
            Remove the old pseudo bridge. There is no longer a physical gap,
            because the subnav is directly adjacent in normal flow.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]::after {
            display: none !important;
          }

          /*
            Subnav lives in normal flow directly under the main tab.
            Hidden by default, expanded only for the hovered group.
            No hardcoded pixel top offsets.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] {
            position: relative !important;
            inset: auto !important;
            top: auto !important;
            left: auto !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            max-height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            transform: translateY(-0.35rem);
            transition:
              max-height 170ms ease,
              opacity 140ms ease,
              transform 140ms ease;
            z-index: 7200 !important;
            margin: 0 !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover div[data-testid="stRadio"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"]:hover {
            max-height: 5rem !important;
            opacity: 1 !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: translateY(0) !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] > div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] > div > div {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            display: inline-flex !important;
            flex-wrap: nowrap !important;
            align-items: stretch !important;
            gap: 0 !important;
            border: 1px solid rgba(190,190,194,0.65) !important;
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            box-shadow: 0 1.1rem 1.75rem rgba(0,0,0,0.16) !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label {
            position: relative !important;
            min-block-size: 2.75rem !important;
            padding: 0.70rem 1.45rem !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: translateY(0);
            white-space: nowrap !important;
            transition:
              background 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:last-child {
            border-right: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label p,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label span,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) * {
            color: #3f3d45 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"]) {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked)::after,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label:has([aria-checked="true"])::after {
            display: none !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
          }

          /*
            Breadcrumb/title should naturally appear after the nav block. When
            subnav is expanded, it pushes the title downward instead of overlaying
            with a gap. This is more reliable across Streamlit DOM changes.
          */
          .workspace-title-region {
            margin-block-start: 0.75rem !important;
          }


          /* Phase 6.17 selected main-tab hover readability fix */
          /*
            Normal selected state:
              dark background + white text.

            Hovering the selected tab:
              light background + dark text, so the tab never becomes
              white-on-white.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab.active {
            background: #ffffff !important;
            border-color: rgba(190,190,194,0.75) !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab.active span,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab.active *,
          .aegis-main-group-tab.active:hover span,
          .aegis-main-group-tab.active:hover * {
            color: #25232a !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover .aegis-main-group-tab.active::after,
          .aegis-main-group-tab.active:hover::after {
            background: #56B4E9 !important;
          }


          /* Phase 6.18 left navigation dropdown font/style fix */
          /*
            Match sidebar/left-navigation dropdown text to the workspace-tab
            design language: dark gray text, strong weight, compact tracking,
            sharp professional look.
          */

          [data-testid="stSidebar"] [data-baseweb="select"] *,
          [data-testid="stSidebar"] [data-baseweb="popover"] *,
          [data-testid="stSidebar"] div[role="listbox"] *,
          [data-testid="stSidebar"] div[role="option"],
          [data-testid="stSidebar"] div[role="option"] *,
          section[data-testid="stSidebar"] [data-baseweb="select"] *,
          section[data-testid="stSidebar"] div[role="option"],
          section[data-testid="stSidebar"] div[role="option"] * {
            color: #25232a !important;
            font-family: inherit !important;
            font-size: 0.82rem !important;
            font-weight: 850 !important;
            letter-spacing: 0.055em !important;
            text-transform: uppercase !important;
          }

          [data-testid="stSidebar"] [data-baseweb="select"] > div,
          section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            border-radius: 0 !important;
            border: 1px solid rgba(190,190,194,0.85) !important;
            background: linear-gradient(180deg, #f6f6f7 0%, #dedee2 100%) !important;
            color: #25232a !important;
            box-shadow: none !important;
          }

          [data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
          section[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
            background: #ffffff !important;
            border-color: #ffffff !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.16) !important;
            transition:
              background 140ms ease,
              border-color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          /*
            BaseWeb renders the dropdown menu popover outside the sidebar DOM,
            so this global popover rule is required for opened dropdown options.
          */
          div[data-baseweb="popover"] div[role="listbox"],
          div[data-baseweb="popover"] ul,
          div[data-baseweb="popover"] div[role="option"] {
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
          }

          div[data-baseweb="popover"] div[role="option"],
          div[data-baseweb="popover"] div[role="option"] *,
          div[data-baseweb="popover"] li,
          div[data-baseweb="popover"] li * {
            color: #25232a !important;
            font-family: inherit !important;
            font-size: 0.82rem !important;
            font-weight: 850 !important;
            letter-spacing: 0.055em !important;
            text-transform: uppercase !important;
          }

          div[data-baseweb="popover"] div[role="option"]:hover,
          div[data-baseweb="popover"] li:hover {
            background: #ffffff !important;
            color: #25232a !important;
          }


          /* Phase 6.19 remove top white Streamlit shell strip */
          /*
            Removes the default Streamlit top header/toolbar band that appeared
            as a white strip above the AegisTelemetry hero.
          */

          header[data-testid="stHeader"],
          [data-testid="stHeader"],
          [data-testid="stToolbar"],
          [data-testid="stDecoration"],
          #MainMenu,
          footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
          }

          .stApp,
          [data-testid="stAppViewContainer"],
          [data-testid="stAppViewContainer"] > .main,
          section.main,
          div[data-testid="stMain"] {
            background: #34313d !important;
          }

          .block-container,
          [data-testid="stMainBlockContainer"],
          main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
          }

          /*
            Some Streamlit builds keep a small top offset even after hiding the
            header. This removes that inherited gap without touching internal
            workspace spacing.
          */
          [data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
          }


          /* Phase 6.20 global dropdown/select typography and field styling */
          /*
            Apply the same dropdown style used in the left navigation to every
            selectbox/dropdown field across all dashboard workspaces.
          */

          div[data-baseweb="select"] > div,
          [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
          [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
            border-radius: 0 !important;
            border: 1px solid rgba(190,190,194,0.85) !important;
            background: linear-gradient(180deg, #f6f6f7 0%, #dedee2 100%) !important;
            color: #25232a !important;
            box-shadow: none !important;
            min-height: 2.45rem !important;
            transition:
              background 140ms ease,
              border-color 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          div[data-baseweb="select"] > div:hover,
          [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
          [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:hover {
            background: #ffffff !important;
            border-color: #ffffff !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.16) !important;
          }

          div[data-baseweb="select"] *,
          [data-testid="stSelectbox"] div[data-baseweb="select"] *,
          [data-testid="stMultiSelect"] div[data-baseweb="select"] *,
          [data-testid="stSelectbox"] input,
          [data-testid="stMultiSelect"] input {
            color: #25232a !important;
            font-family: inherit !important;
            font-size: 0.82rem !important;
            font-weight: 850 !important;
            letter-spacing: 0.055em !important;
            text-transform: uppercase !important;
          }

          /*
            BaseWeb renders open dropdown menus in a global popover layer, not
            inside the workspace container. These rules make opened options match
            the same style across all workspaces.
          */
          div[data-baseweb="popover"] div[role="listbox"],
          div[data-baseweb="popover"] ul,
          div[data-baseweb="popover"] [data-baseweb="menu"] {
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            border: 1px solid rgba(190,190,194,0.85) !important;
            box-shadow: 0 18px 28px rgba(0,0,0,0.16) !important;
          }

          div[data-baseweb="popover"] div[role="option"],
          div[data-baseweb="popover"] div[role="option"] *,
          div[data-baseweb="popover"] li,
          div[data-baseweb="popover"] li *,
          div[data-baseweb="popover"] [data-baseweb="menu"] *,
          div[data-baseweb="popover"] [role="listbox"] * {
            color: #25232a !important;
            font-family: inherit !important;
            font-size: 0.82rem !important;
            font-weight: 850 !important;
            letter-spacing: 0.055em !important;
            text-transform: uppercase !important;
          }

          div[data-baseweb="popover"] div[role="option"]:hover,
          div[data-baseweb="popover"] li:hover,
          div[data-baseweb="popover"] [data-baseweb="menu"] div:hover {
            background: #ffffff !important;
            color: #25232a !important;
          }

          /*
            Keep labels readable on the dark dashboard background while the
            dropdown values/options use the tab-like dark-on-light style.
          */
          [data-testid="stSelectbox"] label,
          [data-testid="stMultiSelect"] label {
            color: #f4f4f4 !important;
            font-size: 0.72rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.12em !important;
            text-transform: uppercase !important;
          }


          /* Phase 6.21 timeline HTML render fix */
          .timeline-sequence-stack {
            display: block;
            margin-top: 8px;
            margin-bottom: 18px;
          }

          .timeline-sequence-stack .timeline-stage-card {
            margin-bottom: 12px;
          }

          .timeline-sequence-stack .timeline-stage-card:last-child {
            margin-bottom: 0;
          }


          /* Phase 6.22 button-based state-driven subnavigation fix */
          /*
            Subnav radios are replaced by buttons. This fixes the edge case
            where clicking an already-selected radio item inside an inactive
            main group did not fire a state change. Buttons always trigger.
          */

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[class*="st-key-aegis_nav_subnav_"] {
            position: relative !important;
            inset: auto !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            max-height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            transform: translateY(-0.35rem);
            transition:
              max-height 170ms ease,
              opacity 140ms ease,
              transform 140ms ease;
            z-index: 7200 !important;
            margin: 0 !important;
            padding: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"]:hover div[class*="st-key-aegis_nav_subnav_"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[class*="st-key-aegis_nav_subnav_"]:hover {
            max-height: 5rem !important;
            opacity: 1 !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: translateY(0) !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stVerticalBlock"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stVerticalBlock"] > div {
            display: inline-flex !important;
            flex-direction: row !important;
            align-items: stretch !important;
            gap: 0 !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            background: rgba(245,245,246,0.98) !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] {
            border: 1px solid rgba(190,190,194,0.65) !important;
            border-radius: 0 !important;
            background: rgba(245,245,246,0.98) !important;
            box-shadow: 0 1.1rem 1.75rem rgba(0,0,0,0.16) !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="element-container"] {
            margin: 0 !important;
            padding: 0 !important;
            width: auto !important;
            min-width: auto !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button {
            min-block-size: 2.75rem !important;
            border-radius: 0 !important;
            border: 0 !important;
            border-right: 1px solid rgba(190,190,194,0.45) !important;
            background: transparent !important;
            color: #3f3d45 !important;
            box-shadow: none !important;
            padding: 0.70rem 1.45rem !important;
            white-space: nowrap !important;
            transition:
              background 140ms ease,
              transform 140ms ease,
              box-shadow 140ms ease;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="element-container"]:last-child button {
            border-right: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
            color: #3f3d45 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button *,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button p,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button span {
            color: #3f3d45 !important;
            font-family: inherit !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: none !important;
            font-weight: 780 !important;
          }

          /*
            Active workspace button: same dark text, selected only by blue
            underline. This applies to Streamlit primary buttons inside subnav.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button[data-testid="stBaseButton-primary"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button[kind="primary"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_item_"][class*="_active"] button {
            background: #ffffff !important;
            box-shadow: inset 0 -3px 0 #56B4E9 !important;
            color: #3f3d45 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_item_"][class*="_active"] button *,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_item_"][class*="_active"] button span,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_item_"][class*="_active"] button p {
            color: #3f3d45 !important;
          }

          /*
            Hide old radio subnav artifacts if any remain from previous CSS
            or Streamlit cache during hot reload.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_group_"] div[data-testid="stRadio"] {
            display: none !important;
          }


          /* Phase 6.23 horizontal button subnav fix */
          /*
            Subnav items are state-driven buttons, but the previous render used
            a vertical Streamlit block, so they stacked vertically. This patch
            renders the buttons in columns and forces the subnav's horizontal
            block/columns to behave like a single horizontal tab strip.
          */

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stHorizontalBlock"] {
            display: inline-flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: stretch !important;
            gap: 0 !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            background: rgba(245,245,246,0.98) !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="column"] {
            width: auto !important;
            min-width: max-content !important;
            max-width: max-content !important;
            flex: 0 0 auto !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: visible !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="column"] > div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="column"] [data-testid="element-container"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stButton"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stButton"] > button {
            width: auto !important;
            min-width: max-content !important;
            max-width: max-content !important;
            margin: 0 !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
          }

          /*
            The subnav wrapper should end at the last button and not create
            vertical stacking or empty white strips.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stVerticalBlock"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stVerticalBlock"] > div {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            overflow: visible !important;
          }

          /*
            Keep the visual language exactly as intended:
            light strip, dark text, active tab indicated only by blue underline.
          */
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button *,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button span,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button p {
            color: #3f3d45 !important;
          }


          /* Phase 6.25 navigation label width/clipping fix */
          /*
            Longer labels such as "Recommendation Rules" should not be clipped.
            Navigation columns now use content-weighted ratios in Python; these
            CSS rules prevent Streamlit/BaseWeb button internals from hiding or
            truncating the label text.
          */

          .st-key-aegis_nav_bar .aegis-main-group-tab,
          .st-key-aegis_nav_bar .aegis-main-group-tab span {
            min-width: max-content !important;
            width: 100% !important;
            overflow: visible !important;
            white-space: nowrap !important;
            text-overflow: clip !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stButton"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stButton"] > button,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button *,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button span,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] button p {
            min-width: max-content !important;
            width: 100% !important;
            max-width: none !important;
            overflow: visible !important;
            white-space: nowrap !important;
            text-overflow: clip !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="column"],
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="column"] > div,
          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="element-container"] {
            min-width: max-content !important;
            overflow: visible !important;
          }

          .st-key-aegis_nav_bar div[class*="st-key-aegis_nav_subnav_"] [data-testid="stHorizontalBlock"] {
            width: max-content !important;
            min-width: max-content !important;
            max-width: calc(100vw - 2rem) !important;
            overflow: visible !important;
          }

        </style>
        """,
        unsafe_allow_html=True,
    )
