"""Data ingestion, validation, and enrichment module for CDC Natality data."""

from pathlib import Path
from typing import List, Tuple, Union
import pandas as pd
import streamlit as st

from src.config import (
    DEFAULT_DATA_PATH,
    MONTH_ORDER,
    US_STATE_TO_ABBR,
)

REQUIRED_COLUMNS = [
    "State of Residence",
    "Month",
    "Month Code",
    "Year Code",
    "Sex of Infant",
    "Births",
]


def validate_raw_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Perform sanity and structural validation on the ingested dataset.
    
    Returns:
        is_valid: Boolean indicating whether validation passed.
        issues: List of validation error/warning messages.
    """
    issues = []

    if df.empty:
        issues.append("The loaded dataset is empty.")
        return False, issues

    # 1. Required column presence
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")

    # 2. Check null values
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if not cols_with_nulls.empty:
        issues.append(f"Dataset contains unexpected nulls: {cols_with_nulls.to_dict()}")

    # 3. Numeric checks on Births
    if "Births" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["Births"]):
            issues.append("'Births' column is not numeric.")
        elif (df["Births"] < 0).any():
            issues.append("Negative birth counts detected.")

    # 4. State mapping integrity
    if "State of Residence" in df.columns:
        unmapped_states = set(df["State of Residence"]) - set(US_STATE_TO_ABBR.keys())
        if unmapped_states:
            issues.append(f"Unrecognized geographies in state mapping: {unmapped_states}")

    # 5. Month code range
    if "Month Code" in df.columns:
        invalid_months = df[~df["Month Code"].isin(range(1, 13))]
        if not invalid_months.empty:
            issues.append(f"Detected out-of-range month codes: {invalid_months['Month Code'].unique().tolist()}")

    is_valid = len(issues) == 0
    return is_valid, issues


def clean_and_enrich_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column types, map state postal codes, and enforce month ordering."""
    df = raw_df.copy()

    # Enforce standard data types
    df["Births"] = pd.to_numeric(df["Births"], errors="coerce").fillna(0).astype(int)
    df["Month Code"] = pd.to_numeric(df["Month Code"], errors="coerce").astype(int)
    df["Year Code"] = pd.to_numeric(df["Year Code"], errors="coerce").astype(int)
    df["State of Residence"] = df["State of Residence"].astype(str).str.strip()
    df["Sex of Infant"] = df["Sex of Infant"].astype(str).str.strip()

    # Construct reliable state abbreviation mapping
    df["State Code"] = df["State of Residence"].map(US_STATE_TO_ABBR)

    # Enforce strict chronological order for Months
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    # Sort deterministically
    df = df.sort_values(by=["State of Residence", "Month Code", "Sex of Infant"]).reset_index(drop=True)
    return df


@st.cache_data(show_spinner="Loading CDC Natality Workbook...")
def load_dataset(filepath: Union[str, Path] = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load, validate, and enrich the CDC provisional natality workbook.
    
    Uses st.cache_data to avoid redundant disk I/O on interaction reruns.
    Works seamlessly across local paths and Streamlit Community Cloud.
    """
    path = Path(filepath)
    if not path.is_file():
        # Fallback search if current working directory differs
        search_candidates = [
            Path("Data/Provisional_Natality_2025_CDC.xlsx"),
            Path("./Data/Provisional_Natality_2025_CDC.xlsx"),
            Path(__file__).resolve().parent.parent / "Data" / "Provisional_Natality_2025_CDC.xlsx",
        ]
        found = None
        for candidate in search_candidates:
            if candidate.is_file():
                found = candidate
                break
        if found:
            path = found
        else:
            raise FileNotFoundError(f"CDC Natality workbook not found at '{filepath}' or common fallbacks.")

    raw_df = pd.read_excel(path)
    is_valid, issues = validate_raw_dataframe(raw_df)
    if not is_valid:
        raise ValueError(f"Data validation failed: {'; '.join(issues)}")

    return clean_and_enrich_data(raw_df)
