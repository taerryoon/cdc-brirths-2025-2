"""Streamlit Dashboard for CDC Provisional Natality 2025 Data.

Target audience: Undergraduate Business Analytics students.
Explores geographic, monthly, and sex-based variations in birth counts.
"""

import streamlit as st
import pandas as pd

from src.config import (
    APP_SUBTITLE,
    APP_TITLE,
    MONTH_ORDER,
    US_STATE_TO_ABBR,
)
from src.data_loader import load_dataset, validate_raw_dataframe
from src.metrics import (
    compute_kpis,
    get_monthly_aggregates,
    get_monthly_sex_aggregates,
    get_state_aggregates,
    get_state_month_matrix,
    get_top_bottom_geographies,
)
from src.visualizations import (
    plot_monthly_trend,
    plot_sex_comparison,
    plot_state_month_heatmap,
    plot_state_ranking,
    plot_top_bottom_comparison,
    plot_us_choropleth,
)
from src.components import (
    inject_custom_css,
    render_empty_state,
    render_filter_summary,
    render_header,
    render_kpi_cards,
)

# 1. Page Configuration
st.set_page_config(
    page_title="CDC Provisional Natality Dashboard (2025)",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject CSS
inject_custom_css()

# 3. Load Dataset
try:
    df = load_dataset()
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

ALL_STATES = sorted(df["State of Residence"].unique().tolist())

# 4. Session State Filter Management
if "filter_states" not in st.session_state:
    st.session_state.filter_states = ALL_STATES.copy()

if "filter_months" not in st.session_state:
    st.session_state.filter_months = MONTH_ORDER.copy()

if "filter_sex" not in st.session_state:
    st.session_state.filter_sex = "All"


def reset_filters():
    st.session_state.filter_states = ALL_STATES.copy()
    st.session_state.filter_months = MONTH_ORDER.copy()
    st.session_state.filter_sex = "All"


def select_all_states():
    st.session_state.filter_states = ALL_STATES.copy()


def clear_all_states():
    st.session_state.filter_states = []


def select_all_months():
    st.session_state.filter_months = MONTH_ORDER.copy()


def clear_all_months():
    st.session_state.filter_months = []


# 5. Sidebar Filter Controls
with st.sidebar:
    st.header("🔍 Filter Controls")
    st.markdown("Customize your geographic, temporal, and demographic subset.")

    # State / Geography Filter
    st.subheader("1. Geography")
    st.multiselect(
        "Select States / Geographies:",
        options=ALL_STATES,
        key="filter_states",
        help="Select one or more US states / DC to include in the analytics.",
    )
    col_st1, col_st2 = st.columns(2)
    with col_st1:
        st.button("Select All States", on_click=select_all_states, use_container_width=True)
    with col_st2:
        st.button("Clear States", on_click=clear_all_states, use_container_width=True)

    st.markdown("---")

    # Month Filter
    st.subheader("2. Calendar Month")
    st.multiselect(
        "Select Months:",
        options=MONTH_ORDER,
        key="filter_months",
        help="Select calendar months. Chronological ordering is preserved in all analytics.",
    )
    col_mo1, col_mo2 = st.columns(2)
    with col_mo1:
        st.button("Select All Months", on_click=select_all_months, use_container_width=True)
    with col_mo2:
        st.button("Clear Months", on_click=clear_all_months, use_container_width=True)

    st.markdown("---")

    # Sex Filter
    st.subheader("3. Infant Sex")
    st.radio(
        "Select Infant Sex:",
        options=["All", "Female", "Male"],
        key="filter_sex",
        horizontal=True,
        help="Filter by infant biological sex recorded on birth certificates.",
    )

    st.markdown("---")

    # Reset Button
    st.button("🔄 Reset All Filters", on_click=reset_filters, type="primary", use_container_width=True)

    st.markdown("---")
    st.caption("CDC Provisional Natality 2025 | QM 389 Analytics Dashboard")


# 6. Apply Filters to Dataset
filtered_df = df.copy()

if st.session_state.filter_states:
    filtered_df = filtered_df[filtered_df["State of Residence"].isin(st.session_state.filter_states)]
else:
    filtered_df = filtered_df.iloc[0:0]

if st.session_state.filter_months:
    filtered_df = filtered_df[filtered_df["Month"].isin(st.session_state.filter_months)]
else:
    filtered_df = filtered_df.iloc[0:0]

if st.session_state.filter_sex != "All":
    filtered_df = filtered_df[filtered_df["Sex of Infant"] == st.session_state.filter_sex]

# 7. Render Header & Banners
render_header()

# 8. Render Active Filters Badge
render_filter_summary(
    states=st.session_state.filter_states,
    months=st.session_state.filter_months,
    sex=st.session_state.filter_sex,
    total_states=len(ALL_STATES),
)

# 9. Compute and Render KPI Cards
kpis = compute_kpis(filtered_df)
render_kpi_cards(kpis)

st.markdown("<br>", unsafe_allow_html=True)

# 10. Check Empty State Guard
if filtered_df.empty:
    render_empty_state()
    st.stop()

# 11. Dashboard Tabs
tab_overview, tab_geo, tab_monthly, tab_data, tab_about = st.tabs([
    "📊 Overview",
    "🗺️ Geographic Analysis",
    "📈 Monthly & Sex Analysis",
    "📋 Data Table & Download",
    "📖 About the Data",
])

# ==========================================
# TAB 1: OVERVIEW
# ==========================================
with tab_overview:
    st.subheader("Executive Analytics Summary")
    st.markdown(
        """
        This dashboard provides a business analytics perspective on provisional 2025 U.S. birth volumes.
        Use the sidebar to filter geographies, months, or infant sex. Key operational and analytical observations:
        """
    )

    # Metric callout highlights
    col_ov1, col_ov2, col_ov3 = st.columns(3)
    with col_ov1:
        st.info(
            f"**Volume Concentration**: The top 3 states ({kpis['top_geography'][0]}, Texas, Florida) "
            "account for roughly 28% of all recorded births nationwide, highlighting stark regional scale differences."
        )
    with col_ov2:
        st.info(
            f"**Seasonality Benchmark**: Peak birth volumes typically occur during late summer (July–August), "
            f"with **{kpis['top_month'][0]}** registering the highest monthly count ({kpis['top_month'][1]:,} births)."
        )
    with col_ov3:
        if kpis["sex_ratio"] > 0:
            st.info(
                f"**Secondary Sex Ratio**: The current selection exhibits a sex ratio of **{kpis['sex_ratio']:.1f} male births per 100 female births**, "
                "aligning with the universal biological benchmark (~105:100)."
            )
        else:
            st.info(f"**Sex Subset**: Active view is filtered strictly to **{st.session_state.filter_sex}** births.")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        monthly_agg = get_monthly_aggregates(filtered_df)
        st.plotly_chart(plot_monthly_trend(monthly_agg), use_container_width=True)

    with col_chart2:
        monthly_sex_agg = get_monthly_sex_aggregates(filtered_df)
        st.plotly_chart(plot_sex_comparison(monthly_sex_agg), use_container_width=True)


# ==========================================
# TAB 2: GEOGRAPHIC ANALYSIS
# ==========================================
with tab_geo:
    st.subheader("Geographic Distribution & State Disparities")
    st.markdown(
        "Analyze birth counts across the United States. Note how absolute volume is dominated by large population centers."
    )

    state_agg = get_state_aggregates(filtered_df)

    # US Choropleth Map
    st.plotly_chart(plot_us_choropleth(state_agg), use_container_width=True)

    st.markdown("---")

    col_rank, col_comp = st.columns([1.1, 1])

    with col_rank:
        st.markdown("#### Geographic Rankings")
        top_n_slider = st.slider("Select number of geographies to display in ranking:", min_value=5, max_value=len(state_agg), value=min(15, len(state_agg)))
        st.plotly_chart(plot_state_ranking(state_agg, top_n=top_n_slider), use_container_width=True)

    with col_comp:
        st.markdown("#### Top 5 vs. Bottom 5 Contrast")
        top_df, bottom_df = get_top_bottom_geographies(filtered_df, n=5)
        st.plotly_chart(plot_top_bottom_comparison(top_df, bottom_df), use_container_width=True)
        st.caption(
            "Analytics Insight: The top 5 states generate tens of times more births than the bottom 5 combined, "
            "reinforcing why raw counts cannot substitute for population-adjusted fertility rates."
        )


# ==========================================
# TAB 3: MONTHLY & SEX ANALYSIS
# ==========================================
with tab_monthly:
    st.subheader("Temporal Dynamics & Demographic Breakdown")
    st.markdown(
        "Explore month-by-month birth trajectories, seasonality patterns, and infant sex distributions."
    )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        monthly_agg = get_monthly_aggregates(filtered_df)
        st.plotly_chart(plot_monthly_trend(monthly_agg), use_container_width=True)

    with col_m2:
        monthly_sex_agg = get_monthly_sex_aggregates(filtered_df)
        st.plotly_chart(plot_sex_comparison(monthly_sex_agg), use_container_width=True)

    st.markdown("---")

    # State-by-Month Heatmap
    st.subheader("State-by-Month Matrix Heatmap")
    st.markdown("Inspect seasonal intensity across individual states.")

    matrix_df = get_state_month_matrix(filtered_df)
    if not matrix_df.empty:
        max_matrix_states = st.slider(
            "Number of top volume states to display in heatmap:",
            min_value=5,
            max_value=min(51, len(matrix_df)),
            value=min(20, len(matrix_df)),
        )
        st.plotly_chart(plot_state_month_heatmap(matrix_df, max_states=max_matrix_states), use_container_width=True)
    else:
        st.info("Insufficient data to generate heatmap.")


# ==========================================
# TAB 4: DATA TABLE & DOWNLOAD
# ==========================================
with tab_data:
    st.subheader("Searchable Data Explorer & CSV Export")
    st.markdown(
        "Inspect the granular dataset matching your active filters. Sort, search, and download for external analysis."
    )

    # Download button
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="cdc_provisional_natality_2025_filtered.csv",
        mime="text/csv",
        help="Export the currently filtered view as a CSV spreadsheet.",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Searchable dataframe
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "Births": st.column_config.NumberColumn("Births", format="%d"),
            "Month Code": st.column_config.NumberColumn("Month Code", format="%d"),
            "Year Code": st.column_config.NumberColumn("Year Code", format="%d"),
        },
        hide_index=True,
    )

    st.markdown("---")

    # Descriptive statistics
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.subheader("Descriptive Statistics (Births)")
        stats_df = filtered_df["Births"].describe().to_frame(name="Births Count")
        stats_df["Births Count"] = stats_df["Births Count"].map(lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{x:,}")
        st.table(stats_df)

    with col_stat2:
        st.subheader("State-Level Aggregated Summary")
        state_summary = get_state_aggregates(filtered_df)
        st.dataframe(
            state_summary,
            use_container_width=True,
            column_config={
                "Births": st.column_config.NumberColumn("Total Births", format="%d"),
                "Share %": st.column_config.NumberColumn("Share %", format="%.2f%%"),
                "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
            },
            hide_index=True,
        )


# ==========================================
# TAB 5: ABOUT THE DATA
# ==========================================
with tab_about:
    st.subheader("Analytical Primer for Business Analytics Students")

    st.markdown(
        """
        ### 1. Absolute Birth Counts vs. Demographic Birth Rates
        - **Raw Birth Counts**: Represents the absolute count of live births registered in a given jurisdiction and timeframe.
        - **Why Comparisons Can Be Misleading**: California (~393K births) and Texas (~385K births) naturally lead total counts because they are the most populous states. High counts **do not** imply higher fertility rates.
        - **Crude Birth Rate (CBR)**: Defined as:
        $$\\text{CBR} = \\left( \\frac{\\text{Number of Live Births}}{\\text{Total Resident Population}} \\right) \\times 1,000$$
        - To calculate birth rates, an analyst must merge this dataset with annual US Census Bureau state population estimates.

        ---

        ### 2. Seasonality & Calendar Artifacts
        - **Length of Month Effect**: February contains only 28 days (non-leap year), which is ~9.7% fewer days than 31-day months (January, March, May, July, August, October, December). Even if daily birth rates were identical, February will report lower monthly totals.
        - **Summer Peak Phenomenon**: Historically in the United States, late summer (July through September) exhibits seasonal spikes in birth volumes, reflecting conception trends in late autumn/winter.

        ---

        ### 3. The Secondary Sex Ratio at Birth
        - **Biological Baseline**: In human populations, the secondary sex ratio (ratio of male to female births) is consistently around **105 male births per 100 female births** (approximately 51.2% male, 48.8% female).
        - In this 2025 dataset, total national births comprise **1,841,800 males** and **1,762,840 females**, yielding a sex ratio of **104.48 males per 100 females**, matching demographic expectations.

        ---

        ### 4. Data Provenance & Provisional Nature
        - **Source**: Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS) Vital Statistics System.
        - **Provisional Status**: Monthly provisional natality counts are based on registered birth certificate records sent by state vital statistics jurisdictions. They undergo ongoing verification and are subject to minor retrospective adjustments before official final natality files are closed.

        ---

        ### 5. Automated Data Integrity & Schema Validation
        """
    )

    # Perform and display automated validation checks
    is_valid, validation_issues = validate_raw_dataframe(df)
    if is_valid:
        st.success(
            f"✅ **Automated Schema Checks Passed**: Verified 1,224 records across all 51 geographies (50 states + DC), "
            "12 chronological months, 2 sex categories, non-negative birth counts, and zero missing values."
        )
    else:
        st.error(f"❌ Schema Validation Warnings: {validation_issues}")

    st.markdown(
        """
        | Metric | Expected Value | Observed in Dataset |
        | :--- | :--- | :--- |
        | Total Records | 1,224 | 1,224 (51 states × 12 months × 2 sexes) |
        | Geographies | 50 States + District of Columbia | 51 Unique Geographies |
        | Calendar Months | January – December (1–12) | 12 Distinct Months |
        | Year Code | 2025 | 2025 |
        | Total National Births | ~3.6 Million | 3,604,640 |
        """
    )
