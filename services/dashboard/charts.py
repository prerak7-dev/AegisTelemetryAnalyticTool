from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from services.dashboard.config import CHART_PALETTE

def render_timeseries_chart(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    series: str,
    height: int = 340,
    y_title: str | None = None,
) -> None:
    """Render a consistent premium time-series chart.

    Developers adding new charts should prefer this helper first. If a new
    chart type is needed, create a new helper here instead of embedding chart
    configuration directly in a view file.
    """
    if df.empty:
        st.info("No data available for the current filter.")
        return

    chart = (
        alt.Chart(df)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X(
                f"{x}:T",
                axis=alt.Axis(title=None, labelColor="#E7E7EA", gridColor="#4A4654", tickColor="#4A4654"),
            ),
            y=alt.Y(
                f"{y}:Q",
                axis=alt.Axis(
                    title=y_title,
                    titleColor="#E7E7EA",
                    labelColor="#E7E7EA",
                    gridColor="#4A4654",
                    tickColor="#4A4654",
                ),
            ),
            color=alt.Color(
                f"{series}:N",
                scale=alt.Scale(range=CHART_PALETTE),
                legend=alt.Legend(title=None, labelColor="#E7E7EA", orient="bottom", columns=3, symbolType="stroke"),
            ),
            tooltip=[
                alt.Tooltip(f"{x}:T", title="Time"),
                alt.Tooltip(f"{series}:N", title="Series"),
                alt.Tooltip(f"{y}:Q", title=y_title or y, format=",.2f"),
            ],
        )
        .properties(height=height)
        .interactive()
        .configure(background="#34313d")
        .configure_view(stroke="#4A4654", fill="#34313d")
        .configure_axis(domainColor="#4A4654", titleFontSize=12, labelFontSize=11)
        .configure_legend(labelFontSize=11, titleFontSize=11)
    )

    st.altair_chart(chart, use_container_width=True)
