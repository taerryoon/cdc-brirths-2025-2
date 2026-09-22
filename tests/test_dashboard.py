"""Unit and integration test suite for the CDC Natality Dashboard."""

import unittest
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

from src.config import MONTH_ORDER, US_STATE_TO_ABBR
from src.data_loader import clean_and_enrich_data, load_dataset, validate_raw_dataframe
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


class TestCDCNatalityDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_dataset()

    def test_dataset_dimensions_and_schema(self):
        """Verify row count, column structure, and zero missing values."""
        self.assertEqual(len(self.df), 1224, "Dataset should contain exactly 1,224 rows (51 * 12 * 2).")
        self.assertEqual(self.df.isnull().sum().sum(), 0, "Dataset should have zero nulls.")

        required_cols = {"State of Residence", "Month", "Month Code", "Year Code", "Sex of Infant", "Births", "State Code"}
        self.assertTrue(required_cols.issubset(set(self.df.columns)))

    def test_state_mapping_completeness(self):
        """Verify all 51 geographies are accurately mapped to 2-letter state codes."""
        unique_states = set(self.df["State of Residence"])
        self.assertEqual(len(unique_states), 51, "Must contain 50 states + DC.")
        for state in unique_states:
            self.assertIn(state, US_STATE_TO_ABBR, f"Missing state abbreviation for: {state}")
            abbr = US_STATE_TO_ABBR[state]
            self.assertEqual(len(abbr), 2, f"State code must be 2 characters: {abbr}")

    def test_chronological_month_order(self):
        """Verify months follow strict calendar order from January to December."""
        unique_months = list(self.df["Month"].cat.categories)
        self.assertEqual(unique_months, MONTH_ORDER)

    def test_kpi_computation(self):
        """Verify aggregate KPIs against known ground-truth values."""
        kpis = compute_kpis(self.df)
        self.assertEqual(kpis["total_births"], 3604640)
        self.assertEqual(kpis["num_geographies"], 51)
        self.assertEqual(kpis["top_geography"][0], "California")
        self.assertEqual(kpis["top_geography"][1], 393111)
        self.assertEqual(kpis["top_month"][0], "July")
        self.assertEqual(kpis["top_month"][1], 321538)
        self.assertAlmostEqual(kpis["avg_births_per_month"], 300386.67, delta=1.0)
        self.assertAlmostEqual(kpis["sex_ratio"], 104.48, delta=0.1)

    def test_empty_kpi_handling(self):
        """Verify KPI computation handles empty dataframe gracefully without errors."""
        empty_df = self.df.iloc[0:0]
        kpis = compute_kpis(empty_df)
        self.assertEqual(kpis["total_births"], 0)
        self.assertEqual(kpis["num_geographies"], 0)
        self.assertEqual(kpis["top_geography"], ("None", 0))

    def test_aggregations(self):
        """Verify aggregation functions return valid DataFrames."""
        monthly = get_monthly_aggregates(self.df)
        self.assertEqual(len(monthly), 12)
        self.assertEqual(monthly["Births"].sum(), 3604640)

        sex_agg = get_monthly_sex_aggregates(self.df)
        self.assertEqual(len(sex_agg), 24)

        state_agg = get_state_aggregates(self.df)
        self.assertEqual(len(state_agg), 51)
        self.assertEqual(state_agg.iloc[0]["State of Residence"], "California")
        self.assertEqual(state_agg.iloc[0]["Rank"], 1)

        matrix = get_state_month_matrix(self.df)
        self.assertEqual(matrix.shape, (51, 12))

        top_df, bottom_df = get_top_bottom_geographies(self.df, n=5)
        self.assertEqual(len(top_df), 5)
        self.assertEqual(len(bottom_df), 5)

    def test_visualizations_render_valid_figures(self):
        """Verify all chart generators output valid Plotly Figures and zero-baselines."""
        monthly = get_monthly_aggregates(self.df)
        fig_trend = plot_monthly_trend(monthly)
        self.assertIsInstance(fig_trend, go.Figure)
        # Check zero-baseline on y-axis
        self.assertEqual(fig_trend.layout.yaxis.rangemode, "tozero")

        monthly_sex = get_monthly_sex_aggregates(self.df)
        fig_sex = plot_sex_comparison(monthly_sex)
        self.assertIsInstance(fig_sex, go.Figure)
        self.assertEqual(fig_sex.layout.yaxis.rangemode, "tozero")

        state_agg = get_state_aggregates(self.df)
        fig_rank = plot_state_ranking(state_agg, top_n=10)
        self.assertIsInstance(fig_rank, go.Figure)
        self.assertEqual(fig_rank.layout.xaxis.rangemode, "tozero")

        fig_choro = plot_us_choropleth(state_agg)
        self.assertIsInstance(fig_choro, go.Figure)

        matrix = get_state_month_matrix(self.df)
        fig_heat = plot_state_month_heatmap(matrix, max_states=10)
        self.assertIsInstance(fig_heat, go.Figure)

        top_df, bottom_df = get_top_bottom_geographies(self.df, n=5)
        fig_comp = plot_top_bottom_comparison(top_df, bottom_df)
        self.assertIsInstance(fig_comp, go.Figure)

    def test_visualizations_handle_empty_gracefully(self):
        """Verify visualizations do not throw on empty datasets."""
        empty_df = pd.DataFrame(columns=["Month Code", "Month", "Births", "Sex of Infant", "State of Residence", "State Code"])
        fig1 = plot_monthly_trend(empty_df)
        self.assertIsInstance(fig1, go.Figure)

        fig2 = plot_sex_comparison(empty_df)
        self.assertIsInstance(fig2, go.Figure)

        fig3 = plot_state_ranking(empty_df)
        self.assertIsInstance(fig3, go.Figure)

        fig4 = plot_us_choropleth(empty_df)
        self.assertIsInstance(fig4, go.Figure)


if __name__ == "__main__":
    unittest.main()
