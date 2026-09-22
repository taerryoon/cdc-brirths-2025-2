"""Plotly visualization builders for CDC Natality Dashboard."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.config import COLORS, MONTH_ORDER


def apply_standard_layout(fig: go.Figure, title: str, subtitle: str = "") -> go.Figure:
    """Apply consistent, professional styling, accessible fonts, and clean padding."""
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size:12px; color:#64748B;'>{subtitle}</span>"

    fig.update_layout(
        title=dict(text=full_title, x=0.01, xanchor="left", font=dict(size=16, color=COLORS["neutral_dark"])),
        font=dict(family="system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.6)",
        margin=dict(l=40, r=30, t=60, b=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="system-ui, sans-serif",
            bordercolor=COLORS["border"],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
        ),
    )
    return fig


def plot_monthly_trend(monthly_df: pd.DataFrame) -> go.Figure:
    """Render monthly birth trend line chart with zero baseline and seasonal benchmark."""
    if monthly_df.empty:
        fig = go.Figure()
        return apply_standard_layout(fig, "Monthly Birth Trend", "No observations match current filters")

    avg_births = monthly_df["Births"].mean()

    fig = go.Figure()

    # Trend line with markers
    fig.add_trace(
        go.Scatter(
            x=monthly_df["Month"],
            y=monthly_df["Births"],
            mode="lines+markers",
            name="Monthly Births",
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=8, color=COLORS["secondary"], symbol="circle"),
            hovertemplate="<b>%{x}</b><br>Births: <b>%{y:,.0f}</b><extra></extra>",
        )
    )

    # Educational benchmark: Average monthly line
    fig.add_trace(
        go.Scatter(
            x=monthly_df["Month"],
            y=[avg_births] * len(monthly_df),
            mode="lines",
            name=f"Average ({avg_births:,.0f})",
            line=dict(color=COLORS["highlight"], width=2, dash="dash"),
            hovertemplate="Monthly Avg: <b>%{y:,.0f}</b><extra></extra>",
        )
    )

    fig.update_xaxes(
        title="Calendar Month (Chronological)",
        categoryorder="array",
        categoryarray=MONTH_ORDER,
        showgrid=True,
        gridcolor="#E2E8F0",
    )
    # Strictly zero baseline to prevent misleading visual distortion for students
    fig.update_yaxes(
        title="Total Registered Births",
        rangemode="tozero",
        tickformat=",.0f",
        showgrid=True,
        gridcolor="#E2E8F0",
    )

    return apply_standard_layout(
        fig,
        "Monthly Birth Volume Trajectory (2025)",
        "Chronological trend illustrating seasonality (zero-baseline axis to avoid visual distortion)",
    )


def plot_sex_comparison(monthly_sex_df: pd.DataFrame) -> go.Figure:
    """Render comparative bar chart of Female vs Male births across months."""
    if monthly_sex_df.empty:
        fig = go.Figure()
        return apply_standard_layout(fig, "Births by Infant Sex", "No observations match current filters")

    fig = px.bar(
        monthly_sex_df,
        x="Month",
        y="Births",
        color="Sex of Infant",
        barmode="group",
        color_discrete_map={"Female": COLORS["female"], "Male": COLORS["male"]},
        category_orders={"Month": MONTH_ORDER},
    )

    fig.update_traces(
        hovertemplate="<b>%{x} (%{data.name})</b><br>Births: <b>%{y:,.0f}</b><extra></extra>"
    )
    fig.update_xaxes(title="Month", categoryorder="array", categoryarray=MONTH_ORDER)
    fig.update_yaxes(title="Birth Count", rangemode="tozero", tickformat=",.0f", showgrid=True, gridcolor="#E2E8F0")

    return apply_standard_layout(
        fig,
        "Births by Infant Sex & Month",
        "Comparison of male and female registered births per month (Standard human sex ratio ~105 males : 100 females)",
    )


def plot_state_ranking(state_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Render horizontal bar chart for state rankings with true zero-baseline."""
    if state_df.empty:
        fig = go.Figure()
        return apply_standard_layout(fig, "Geographic Rankings", "No observations match current filters")

    # Slice top N and reverse order so highest is on top of horizontal bar
    df_slice = state_df.head(top_n).iloc[::-1]

    fig = go.Figure(
        go.Bar(
            x=df_slice["Births"],
            y=df_slice["State of Residence"],
            orientation="h",
            marker=dict(
                color=df_slice["Births"],
                colorscale="Blues",
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>Rank: #%{customdata[0]}<br>Births: <b>%{x:,.0f}</b><br>National Share: <b>%{customdata[1]:.2f}%</b><extra></extra>",
            customdata=df_slice[["Rank", "Share %"]].values,
        )
    )

    fig.update_xaxes(title="Total Birth Count", rangemode="tozero", tickformat=",.0f", showgrid=True, gridcolor="#E2E8F0")
    fig.update_yaxes(title="")

    return apply_standard_layout(
        fig,
        f"Top {len(df_slice)} Geographies by Birth Count",
        "Ranked volume reflecting regional scale (Zero baseline preserved)",
    )


def plot_us_choropleth(state_df: pd.DataFrame) -> go.Figure:
    """Render US Choropleth map with interactive hover and high-contrast color scale."""
    if state_df.empty:
        fig = go.Figure()
        return apply_standard_layout(fig, "U.S. Geographic Distribution", "No observations match current filters")

    fig = px.choropleth(
        state_df,
        locations="State Code",
        locationmode="USA-states",
        color="Births",
        scope="usa",
        color_continuous_scale="Blues",
        labels={"Births": "Births"},
        hover_name="State of Residence",
        hover_data={"State Code": True, "Births": ":,.0f", "Rank": True, "Share %": ":.2f%"},
    )

    fig.update_layout(
        geo=dict(
            lakecolor="rgb(255, 255, 255)",
            bgcolor="rgba(0,0,0,0)",
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Births", font=dict(size=12)),
            tickformat=",.0f",
            thickness=14,
            len=0.75,
        ),
    )

    return apply_standard_layout(
        fig,
        "Geographic Birth Count Density Across the United States",
        "Choropleth view of total births in current selection (Note: reflects total resident population)",
    )


def plot_state_month_heatmap(matrix_df: pd.DataFrame, max_states: int = 20) -> go.Figure:
    """Render heatmap matrix of States x Months."""
    if matrix_df.empty:
        fig = go.Figure()
        return apply_standard_layout(fig, "State-by-Month Heatmap", "No observations match current filters")

    # Take top N states by default to keep matrix readable
    df_slice = matrix_df.head(max_states)

    fig = go.Figure(
        data=go.Heatmap(
            z=df_slice.values,
            x=df_slice.columns.tolist(),
            y=df_slice.index.tolist(),
            colorscale="Viridis",
            hoverongaps=False,
            hovertemplate="<b>State:</b> %{y}<br><b>Month:</b> %{x}<br><b>Births:</b> %{z:,.0f}<extra></extra>",
            colorbar=dict(title=dict(text="Births", font=dict(size=12)), tickformat=",.0f", thickness=14),
        )
    )

    fig.update_xaxes(title="Month (Chronological)", categoryorder="array", categoryarray=MONTH_ORDER)
    fig.update_yaxes(title="State (Ordered by Volume)", autorange="reversed")

    return apply_standard_layout(
        fig,
        f"State-by-Month Heatmap (Top {len(df_slice)} States)",
        "Matrix visualization tracking seasonal variations across states",
    )


def plot_top_bottom_comparison(top_df: pd.DataFrame, bottom_df: pd.DataFrame) -> go.Figure:
    """Render comparison chart between highest and lowest volume geographies."""
    if top_df.empty or bottom_df.empty:
        fig = go.Figure()
        return apply_standard_layout(fig, "Top vs Bottom Comparison", "No observations match current filters")

    combined = pd.concat([top_df, bottom_df], ignore_index=True)

    fig = px.bar(
        combined,
        x="Births",
        y="State of Residence",
        color="Group",
        orientation="h",
        color_discrete_map={"Top 5": COLORS["primary"], "Bottom 5": COLORS["accent"]},
        hover_data={"Births": ":,.0f", "Share %": ":.2f%", "Rank": True},
    )

    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    fig.update_xaxes(title="Total Births", rangemode="tozero", tickformat=",.0f", showgrid=True, gridcolor="#E2E8F0")
    fig.update_yaxes(title="")

    return apply_standard_layout(
        fig,
        "High-Volume vs. Low-Volume State Comparison",
        "Demonstrates dramatic magnitude differences driven by demographic population scales",
    )
