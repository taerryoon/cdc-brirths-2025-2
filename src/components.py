"""UI components, banners, KPI card formatters, and custom CSS styling."""

from typing import Any, Dict, List
import streamlit as st

from src.config import (
    APP_SUBTITLE,
    APP_TITLE,
    CDC_ATTRIBUTION,
    COUNT_VS_RATE_NOTICE,
    PROVISIONAL_NOTICE,
)


def inject_custom_css():
    """Inject clean, modern CSS for cards, badges, and layout aesthetics."""
    st.markdown(
        """
        <style>
        /* Modern metric card styles */
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        }
        .metric-title {
            font-size: 0.82rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.05em;
            color: #64748B;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #DC2626;
            line-height: 1.2;
            white-space: nowrap;
        }
        .metric-number-red {
            color: #DC2626;
            font-weight: 600;
        }
        .metric-subtitle {
            font-size: 0.8rem;
            color: #475569;
            margin-top: 4px;
        }

        /* Banner styles */
        .callout-banner {
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .banner-warning {
            background-color: #FFFBEB;
            border-left: 4px solid #F59E0B;
            color: #92400E;
        }
        .banner-info {
            background-color: #EFF6FF;
            border-left: 4px solid #3B82F6;
            color: #1E40AF;
        }
        .filter-badge-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            margin-bottom: 18px;
            padding: 10px 14px;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
        }
        .filter-badge {
            background-color: #E2E8F0;
            color: #1E293B;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .filter-badge-active {
            background-color: #DBEAFE;
            color: #1E40AF;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the dashboard header, provenance attribution, and analytical caveats."""
    st.title(f"🏛️ {APP_TITLE}")
    st.markdown(f"**{APP_SUBTITLE}**")

    # Header Callout Alerts
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(
            f"""
            <div class="callout-banner banner-warning">
                <strong>⚠️ {COUNT_VS_RATE_NOTICE}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="callout-banner banner-info">
                <strong>📌 {PROVISIONAL_NOTICE}</strong><br>
                <span style="font-size: 0.82rem; color: #3B82F6;">{CDC_ATTRIBUTION}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_filter_summary(states: List[str], months: List[str], sex: str, total_states: int = 51):
    """Render a clean summary of active filters."""
    states_text = "All 51 Geographies" if len(states) == total_states else f"{len(states)} of {total_states} Geographies"
    months_text = "All 12 Months" if len(months) == 12 else f"{len(months)} of 12 Months"
    sex_text = f"Sex: {sex}" if sex != "All" else "Sex: Both (Male & Female)"

    st.markdown(
        f"""
        <div class="filter-badge-bar">
            <span style="font-size: 0.85rem; font-weight: 600; color: #475569;">Active Filters:</span>
            <span class="{"filter-badge-active" if len(states) != total_states else "filter-badge"}">🗺️ {states_text}</span>
            <span class="{"filter-badge-active" if len(months) != 12 else "filter-badge"}">📅 {months_text}</span>
            <span class="{"filter-badge-active" if sex != "All" else "filter-badge"}">👥 {sex_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(kpis: Dict[str, Any]):
    """Render the 5 required responsive KPI cards with red numerical callouts."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Births</div>
                <div class="metric-value" style="color: #DC2626;">{kpis['total_births']:,}</div>
                <div class="metric-subtitle">In current selection</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Selected Geographies</div>
                <div class="metric-value" style="color: #DC2626;">{kpis['num_geographies']}</div>
                <div class="metric-subtitle">States & DC represented</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        avg_formatted = f"{kpis['avg_births_per_month']:,.0f}" if kpis['avg_births_per_month'] > 0 else "0"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Avg Births / Month</div>
                <div class="metric-value" style="color: #DC2626;">{avg_formatted}</div>
                <div class="metric-subtitle">Across active months</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        top_state_name, top_state_val = kpis["top_geography"]
        val_sub = f"<span class='metric-number-red' style='color: #DC2626; font-weight: 600;'>{top_state_val:,}</span> births" if top_state_val > 0 else ""
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Top Geography</div>
                <div class="metric-value" style="font-size: 1.45rem; color: #DC2626;">{top_state_name}</div>
                <div class="metric-subtitle">{val_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        top_month_name, top_month_val = kpis["top_month"]
        val_sub_m = f"<span class='metric-number-red' style='color: #DC2626; font-weight: 600;'>{top_month_val:,}</span> births" if top_month_val > 0 else ""
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Top Month</div>
                <div class="metric-value" style="font-size: 1.45rem; color: #DC2626;">{top_month_name}</div>
                <div class="metric-subtitle">{val_sub_m}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_empty_state():
    """Display an informative callout when no records match filter criteria."""
    st.warning(
        """
        **No observations match your current filter selection.**
        
        - Please select at least one State / Geography in the sidebar.
        - Please select at least one Calendar Month.
        - Click **"Reset Filters"** in the sidebar to restore default full dataset parameters.
        """
    )
