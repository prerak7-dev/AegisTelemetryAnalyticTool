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


def render_multi_metric_timeline(
    df: pd.DataFrame,
    *,
    x: str,
    metrics: list[str],
    height: int = 320,
    title: str | None = None,
) -> None:
    """Render multiple metric columns as a long-form timeline.

    This is useful for incident replay where the analyst needs to see
    how density, subsystem pressure, server frame time, and player impact
    moved before/during/after an incident.
    """
    if df.empty:
        st.info("No timeline data available for the current incident scope.")
        return

    available_metrics = [metric for metric in metrics if metric in df.columns]
    if not available_metrics:
        st.info("None of the requested metrics are available in the timeline data.")
        return

    plot_df = df[[x] + available_metrics].copy()
    long_df = plot_df.melt(id_vars=[x], var_name="metric", value_name="value")

    chart = (
        alt.Chart(long_df)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X(
                f"{x}:T",
                axis=alt.Axis(title=None, labelColor="#E7E7EA", gridColor="#4A4654", tickColor="#4A4654"),
            ),
            y=alt.Y(
                "value:Q",
                axis=alt.Axis(title=title, titleColor="#E7E7EA", labelColor="#E7E7EA", gridColor="#4A4654", tickColor="#4A4654"),
            ),
            color=alt.Color(
                "metric:N",
                scale=alt.Scale(range=CHART_PALETTE),
                legend=alt.Legend(title=None, labelColor="#E7E7EA", orient="bottom", columns=3, symbolType="stroke"),
            ),
            tooltip=[
                alt.Tooltip(f"{x}:T", title="Time"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("value:Q", title="Value", format=",.2f"),
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


def render_horizontal_bar_chart(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    tooltip_columns: list[str] | None = None,
    height: int = 320,
    x_title: str | None = None,
) -> None:
    """Render a compact horizontal bar chart for ranked pressure views."""
    if df.empty:
        st.info("No data available for the current filter.")
        return

    tooltip_columns = tooltip_columns or [y, x]
    tooltips = []
    for column in tooltip_columns:
        if column not in df.columns:
            continue
        if pd.api.types.is_numeric_dtype(df[column]):
            tooltips.append(alt.Tooltip(f"{column}:Q", title=column, format=",.2f"))
        else:
            tooltips.append(alt.Tooltip(f"{column}:N", title=column))

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{x}:Q",
                axis=alt.Axis(
                    title=x_title or x,
                    titleColor="#E7E7EA",
                    labelColor="#E7E7EA",
                    gridColor="#4A4654",
                    tickColor="#4A4654",
                ),
            ),
            y=alt.Y(
                f"{y}:N",
                sort="-x",
                axis=alt.Axis(title=None, labelColor="#E7E7EA"),
            ),
            tooltip=tooltips,
        )
        .properties(height=height)
        .configure(background="#34313d")
        .configure_view(stroke="#4A4654", fill="#34313d")
        .configure_axis(domainColor="#4A4654", titleFontSize=12, labelFontSize=11)
    )

    st.altair_chart(chart, use_container_width=True)
