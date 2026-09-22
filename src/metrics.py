"""Metrics computation engine for CDC Natality data."""

from typing import Any, Dict, Tuple
import pandas as pd


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute top-level summary KPI metrics for the active filter selection."""
    if df.empty:
        return {
            "total_births": 0,
            "num_geographies": 0,
            "avg_births_per_month": 0,
            "top_geography": ("None", 0),
            "top_month": ("None", 0),
            "male_births": 0,
            "female_births": 0,
            "sex_ratio": 0.0,
        }

    total_births = int(df["Births"].sum())
    num_geographies = int(df["State of Residence"].nunique())

    # Average births per selected month
    # Aggregate across all records for each distinct month in selection
    monthly_totals = df.groupby("Month", observed=True)["Births"].sum()
    active_months_count = len(monthly_totals)
    avg_births_per_month = float(total_births / active_months_count) if active_months_count > 0 else 0.0

    # Top geography
    state_totals = df.groupby("State of Residence", observed=True)["Births"].sum()
    if not state_totals.empty and state_totals.max() > 0:
        top_state_name = str(state_totals.idxmax())
        top_state_val = int(state_totals.max())
    else:
        top_state_name = "N/A"
        top_state_val = 0

    # Top month
    if not monthly_totals.empty and monthly_totals.max() > 0:
        top_month_name = str(monthly_totals.idxmax())
        top_month_val = int(monthly_totals.max())
    else:
        top_month_name = "N/A"
        top_month_val = 0

    # Sex breakdown & biological ratio
    sex_totals = df.groupby("Sex of Infant", observed=True)["Births"].sum().to_dict()
    male_births = int(sex_totals.get("Male", 0))
    female_births = int(sex_totals.get("Female", 0))
    sex_ratio = round((male_births / female_births) * 100, 2) if female_births > 0 else 0.0

    return {
        "total_births": total_births,
        "num_geographies": num_geographies,
        "avg_births_per_month": avg_births_per_month,
        "top_geography": (top_state_name, top_state_val),
        "top_month": (top_month_name, top_month_val),
        "male_births": male_births,
        "female_births": female_births,
        "sex_ratio": sex_ratio,  # Males per 100 females
    }


def get_monthly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate total births by chronological month."""
    if df.empty:
        return pd.DataFrame(columns=["Month Code", "Month", "Births"])

    agg = (
        df.groupby(["Month Code", "Month"], observed=True)["Births"]
        .sum()
        .reset_index()
        .sort_values("Month Code")
    )
    return agg


def get_monthly_sex_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate births by month and infant sex."""
    if df.empty:
        return pd.DataFrame(columns=["Month Code", "Month", "Sex of Infant", "Births"])

    agg = (
        df.groupby(["Month Code", "Month", "Sex of Infant"], observed=True)["Births"]
        .sum()
        .reset_index()
        .sort_values(["Month Code", "Sex of Infant"])
    )
    return agg


def get_state_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate births by state with postal code, percentage share, and rank."""
    if df.empty:
        return pd.DataFrame(columns=["State of Residence", "State Code", "Births", "Share %", "Rank"])

    agg = (
        df.groupby(["State of Residence", "State Code"], observed=True)["Births"]
        .sum()
        .reset_index()
        .sort_values(by="Births", ascending=False)
    )
    total = agg["Births"].sum()
    agg["Share %"] = (agg["Births"] / total * 100).round(2) if total > 0 else 0.0
    agg["Rank"] = range(1, len(agg) + 1)
    return agg


def get_state_month_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Create a pivot table with states as rows and months as columns."""
    if df.empty:
        return pd.DataFrame()

    matrix = df.pivot_table(
        index="State of Residence",
        columns="Month",
        values="Births",
        aggfunc="sum",
        fill_value=0,
        observed=True,
    )
    # Sort states by descending total births
    matrix["Total"] = matrix.sum(axis=1)
    matrix = matrix.sort_values(by="Total", ascending=False)
    matrix = matrix.drop(columns=["Total"])
    return matrix


def get_top_bottom_geographies(df: pd.DataFrame, n: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Retrieve top N and bottom N states by birth count in the current selection."""
    state_agg = get_state_aggregates(df)
    if state_agg.empty:
        return pd.DataFrame(), pd.DataFrame()

    top_n = state_agg.head(n).copy()
    top_n["Group"] = f"Top {len(top_n)}"

    bottom_n = state_agg.tail(n).copy()
    bottom_n["Group"] = f"Bottom {len(bottom_n)}"
    # Sort bottom_n descending for consistent bar chart visualization
    bottom_n = bottom_n.sort_values(by="Births", ascending=True)

    return top_n, bottom_n
