from __future__ import annotations

import pandas as pd
import streamlit as st

from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.query import query_df, region_filter_sql, server_filter_sql, source_filter_sql
from services.dashboard.schemas import load_source_profiles_for_ui

def render(context: DashboardContext) -> None:
    filters = context.filters
    st.subheader("Source schema adapter")
    st.caption("Incoming telemetry can use different field names and nesting. The collector maps each source profile into the canonical AegisTelemetry event contract before validation and streaming.")

    profiles = load_source_profiles_for_ui()
    if not profiles:
        st.warning("No source schema profiles found in /app/source_schemas.")
    else:
        profile_df = pd.DataFrame(profiles)
        render_table(profile_df[["profile_name", "version", "passthrough", "description"]], height=240)

        selected_profile = st.selectbox("Inspect profile", [p["profile_name"] for p in profiles])
        selected_payload = next((p for p in profiles if p["profile_name"] == selected_profile), None)
        if selected_payload:
            st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
            st.write(f"**Description:** {selected_payload['description']}")
            st.write(f"**Mapped canonical fields:** {selected_payload['mapped_fields'] or 'Native passthrough'}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Observed source profiles")
    observed_profiles = query_df(f"""
        SELECT
          source_profile,
          count() AS raw_events,
          countDistinct(server_id) AS servers,
          max(event_time) AS latest_event
        FROM raw_events
        WHERE {filters.raw_event_time_filter}
          AND {source_filter_sql(filters.selected_source_profile)}
          AND {region_filter_sql(filters.selected_region)}
          AND {server_filter_sql(filters.selected_server)}
        GROUP BY source_profile
        ORDER BY raw_events DESC
        LIMIT {filters.max_table_rows}
    """)
    if observed_profiles.empty:
        st.info("No raw events found for the current filter yet.")
    else:
        render_table(observed_profiles, height=260)

    st.subheader("Example ingestion commands")
    st.code(
        'curl -X POST http://localhost:8000/v1/events/generic_live_service -H "Content-Type: application/json" -d @sample_generic_event.json',
        language="bash",
    )
    st.code("curl -X GET http://localhost:8000/v1/source-profiles", language="bash")
