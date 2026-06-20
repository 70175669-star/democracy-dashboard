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


def load_data(path=None):
    df = pd.read_csv("data/vdem_tiny.csv", low_memory=False)
    available = [c for c in CORE_COLS if c in df.columns]
    if available:
    df = df[available]
    
    if "e_regionpol_6C" in df.columns:
        df["region"] = df["e_regionpol_6C"].map(REGION_MAP)
    else:
        df["region"] = "Unknown"
    
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
    
    if "Electoral Democracy" in df.columns:
        df.dropna(subset=["Electoral Democracy"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
def filter_by_year(df, start, end):
    return df[(df["year"] >= start) & (df["year"] <= end)]

def filter_by_region(df, regions):
    if not regions:
        return df
    return df[df["region"].isin(regions)]

def filter_by_score(df, col, min_val, max_val):
    if col not in df.columns:
        return df
    return df[(df[col] >= min_val) & (df[col] <= max_val)]

def filter_by_country(df, search_text):
    if not search_text or not search_text.strip():
        return df
    return df[df["country_name"].str.contains(search_text.strip(), case=False, na=False)]

def filter_multiselect(df, col, values):
    if not values:
        return df
    return df[df[col].isin(values)]

def reset_filters(df_original):
    return df_original.copy()

def apply_all_filters(df, year_range, regions, score_range, countries, search_text):
    filtered = df.copy()
    filtered = filter_by_year(filtered, *year_range)
    filtered = filter_by_region(filtered, regions)
    filtered = filter_by_score(filtered, "Electoral Democracy", *score_range)
    filtered = filter_multiselect(filtered, "country_name", countries)
    filtered = filter_by_country(filtered, search_text)
    return filtered
