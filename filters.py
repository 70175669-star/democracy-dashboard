# filters.py
# ─────────────────────────────────────────────────────────────────────────────
# All filtering / data-preparation logic for the V-Dem Dashboard.
# app.py imports these functions and calls them before passing data to charts.
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np

REGION_MAP = {
    1: "E. Europe & C. Asia",
    2: "Latin America",
    3: "MENA",
    4: "Sub-Saharan Africa",
    5: "W. Europe & N. America",
    6: "Asia & Pacific",
}

CORE_COLS = [
    "country_name", "country_text_id", "year",
    "v2x_polyarchy", "v2x_libdem", "v2x_partipdem",
    "v2x_delibdem", "v2x_egaldem",
    "v2x_freexp_altinf", "v2x_frassoc_thick",
    "v2xcl_rol", "v2x_corr", "v2x_execorr",
    "v2xel_frefair", "v2x_suffr",
    "v2x_gender", "v2xnp_pres",
    "e_regionpol_6C", "e_gdppc", "e_pop",
]


# ── Load ──────────────────────────────────────────────────────────────────────

def load_data(path: str = "data/V-Dem-CY-Full_Others-v16.csv") -> pd.DataFrame:
    """Load the V-Dem CSV and return a cleaned, enriched DataFrame."""
    df = pd.read_csv(path, usecols=lambda c: c in CORE_COLS, low_memory=False)

    # Add human-readable region label
    df["region"] = df["e_regionpol_6C"].map(REGION_MAP)

    # Rename for display
    df.rename(columns={
        "v2x_polyarchy":      "Electoral Democracy",
        "v2x_libdem":         "Liberal Democracy",
        "v2x_partipdem":      "Participatory Democracy",
        "v2x_delibdem":       "Deliberative Democracy",
        "v2x_egaldem":        "Egalitarian Democracy",
        "v2x_freexp_altinf":  "Freedom of Expression",
        "v2x_frassoc_thick":  "Freedom of Association",
        "v2xcl_rol":          "Rule of Law",
        "v2x_corr":           "Political Corruption",
        "v2x_execorr":        "Executive Corruption",
        "v2xel_frefair":      "Free & Fair Elections",
        "v2x_suffr":          "Universal Suffrage",
        "v2x_gender":         "Women Empowerment",
        "e_gdppc":            "GDP per Capita",
        "e_pop":              "Population",
    }, inplace=True)

    # Drop rows with no core score
    df.dropna(subset=["Electoral Democracy"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# ── Individual filter functions ───────────────────────────────────────────────

def filter_by_year(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    """Keep rows where year is within [start, end]."""
    return df[(df["year"] >= start) & (df["year"] <= end)]


def filter_by_region(df: pd.DataFrame, regions: list) -> pd.DataFrame:
    """Keep rows whose region label is in the selected list.
    If the list is empty, return the full DataFrame unchanged."""
    if not regions:
        return df
    return df[df["region"].isin(regions)]


def filter_by_score(df: pd.DataFrame, col: str,
                    min_val: float, max_val: float) -> pd.DataFrame:
    """Keep rows where *col* is within [min_val, max_val]."""
    return df[(df[col] >= min_val) & (df[col] <= max_val)]


def filter_by_country(df: pd.DataFrame, search_text: str) -> pd.DataFrame:
    """Case-insensitive substring search on country_name."""
    if not search_text or not search_text.strip():
        return df
    return df[df["country_name"].str.contains(search_text.strip(), case=False, na=False)]


def filter_multiselect(df: pd.DataFrame,
                       col: str, values: list) -> pd.DataFrame:
    """Keep rows where *col* value is in *values*.
    Returns full DataFrame if values list is empty."""
    if not values:
        return df
    return df[df[col].isin(values)]


def reset_filters(df_original: pd.DataFrame) -> pd.DataFrame:
    """Return the original unfiltered DataFrame (pass the cached original)."""
    return df_original.copy()


# ── Compound helper ───────────────────────────────────────────────────────────

def apply_all_filters(df: pd.DataFrame,
                      year_range: tuple,
                      regions: list,
                      score_range: tuple,
                      countries: list,
                      search_text: str) -> pd.DataFrame:
    """Apply every active filter in sequence and return the result."""
    filtered = df.copy()
    filtered = filter_by_year(filtered, *year_range)
    filtered = filter_by_region(filtered, regions)
    filtered = filter_by_score(filtered, "Electoral Democracy", *score_range)
    filtered = filter_multiselect(filtered, "country_name", countries)
    filtered = filter_by_country(filtered, search_text)
    return filtered
