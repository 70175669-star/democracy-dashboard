# app.py
# ─────────────────────────────────────────────────────────────────────────────
# V-Dem Democracy Dashboard  –  EDA Course Project
# Run with:  streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np

import filters
import charts

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="V-Dem Democracy Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title  { font-size:2.4rem; font-weight:800; color:#1a6faf; margin-bottom:0; }
    .sub-title   { font-size:1rem;  color:#555; margin-top:0.2rem; margin-bottom:1.2rem; }
    .kpi-card    { background:#f0f6ff; border-left:4px solid #1a6faf;
                   border-radius:8px; padding:14px 18px; text-align:center; }
    .kpi-number  { font-size:2rem; font-weight:700; color:#1a6faf; }
    .kpi-label   { font-size:0.82rem; color:#666; margin-top:4px; }
    .section-hdr { font-size:1.25rem; font-weight:700; color:#1a6faf;
                   border-bottom:2px solid #dde8f5; padding-bottom:4px;
                   margin-top:2rem; margin-bottom:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ── Load data (cached) ────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading V-Dem dataset …")
def get_data():
    return filters.load_data()

df_full = get_data()

# ── Sidebar — Filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/40px-Jupyter_logo.svg.png", width=36)
    st.markdown("## 🔧 Dashboard Filters")
    st.markdown("---")

    # 1. Year range
  st.markdown("**📅 Year Range**")
    min_year = int(df_full["year"].min())
    max_year = int(df_full["year"].max())
    if min_year == max_year:
        max_year = min_year + 1
    year_range = st.slider(
        "Select year range",
        min_value=min_year, max_value=max_year,
        value=(min_year, max_year), step=1,
    )
    # 2. Region multi-select
    st.markdown("**🌍 World Region**")
    all_regions = sorted(df_full["region"].dropna().unique().tolist())
    selected_regions = st.multiselect(
        "Select regions (empty = all)",
        options=all_regions,
        default=[],
    )

    # 3. Electoral Democracy score slider
    st.markdown("**📊 Electoral Democracy Score**")
    score_range = st.slider(
        "Score range (0–1)",
        min_value=0.0, max_value=1.0,
        value=(0.0, 1.0), step=0.01,
    )

    # 4. Country multi-select
    st.markdown("**🏳️ Countries**")
    all_countries = sorted(df_full["country_name"].unique().tolist())
    selected_countries = st.multiselect(
        "Select countries (empty = all)",
        options=all_countries,
        default=[],
    )

    # 5. Text search
    st.markdown("**🔍 Country Search**")
    search_text = st.text_input("Type country name keyword", value="")

    # 6. Scatter axis selectors
    st.markdown("---")
    st.markdown("**⚙️ Scatter Plot Axes**")
    score_options = [c for c in charts.SCORE_COLS if c in df_full.columns]
    x_axis = st.selectbox("X-Axis", score_options, index=0)
    y_axis = st.selectbox("Y-Axis", score_options, index=min(1, len(score_options)-1))
    # 7. Chart column selector (histogram / box / violin)
    st.markdown("**📈 Column for Histogram / Box / Violin**")
    hist_col = st.selectbox("Choose indicator", score_options, index=min(0, len(score_options)-1))

    # 8. Reset button
    st.markdown("---")
    if st.button("🔄 Reset All Filters"):
        st.rerun()

# ── Apply filters ─────────────────────────────────────────────────────────────
df = filters.apply_all_filters(
    df_full,
    year_range=year_range,
    regions=selected_regions,
    score_range=score_range,
    countries=selected_countries,
    search_text=search_text,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🌍 V-Dem Democracy Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Exploratory analysis of the Varieties of Democracy (V-Dem) dataset — '
    '202 countries · 1789–2025 · 400+ indicators</p>',
    unsafe_allow_html=True,
)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number">{len(df):,}</div>
        <div class="kpi-label">Total Records</div></div>""", unsafe_allow_html=True)

with k2:
    n_countries = df["country_name"].nunique()
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number">{n_countries}</div>
        <div class="kpi-label">Countries</div></div>""", unsafe_allow_html=True)

with k3:
    avg_dem = df["Electoral Democracy"].mean()
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number">{avg_dem:.3f}</div>
        <div class="kpi-label">Avg Electoral Democracy</div></div>""", unsafe_allow_html=True)

with k4:
    max_row = df.loc[df["Electoral Democracy"].idxmax()] if len(df) > 0 else None
    top_country = max_row["country_name"] if max_row is not None else "—"
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="font-size:1.2rem">{top_country}</div>
        <div class="kpi-label">Highest Democracy Score</div></div>""", unsafe_allow_html=True)

with k5:
    yr_span = f"{int(df['year'].min())} – {int(df['year'].max())}" if len(df) > 0 else "—"
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-number" style="font-size:1.3rem">{yr_span}</div>
        <div class="kpi-label">Year Span</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("⚠️ No data matches the current filters. Please adjust the sidebar settings.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Trends Over Time
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">📈 Section 1 — Trends Over Time</p>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Line Chart — Democracy Indices Over Time**")
    st.pyplot(charts.chart_line(df), use_container_width=True)

with col_b:
    st.markdown("**Area Chart — Share of Democracies**")
    st.pyplot(charts.chart_area(df), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Regional Comparisons
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">🌍 Section 2 — Regional Comparisons</p>', unsafe_allow_html=True)

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("**Bar Chart — Average Democracy by Region**")
    st.pyplot(charts.chart_bar(df), use_container_width=True)

with col_d:
    st.markdown("**Pie Chart — Countries by Region**")
    st.pyplot(charts.chart_pie(df), use_container_width=True)

col_e, col_f = st.columns(2)
with col_e:
    st.markdown("**Count Plot — Observations per Region**")
    st.pyplot(charts.chart_count(df), use_container_width=True)

with col_f:
    st.markdown("**Radar Chart (Bonus) — Democracy Dimensions by Region**")
    st.pyplot(charts.chart_radar(df), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Distributions
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">📊 Section 3 — Score Distributions</p>', unsafe_allow_html=True)

col_g, col_h = st.columns(2)
with col_g:
    st.markdown(f"**Histogram — {hist_col}**")
    st.pyplot(charts.chart_histogram(df, hist_col), use_container_width=True)

with col_h:
    st.markdown(f"**Box Plot — {hist_col} by Region**")
    st.pyplot(charts.chart_box(df, hist_col), use_container_width=True)

st.markdown(f"**Violin Plot — {hist_col} by Region**")
st.pyplot(charts.chart_violin(df, hist_col), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Relationships
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">🔗 Section 4 — Relationships Between Indicators</p>',
            unsafe_allow_html=True)

col_i, col_j = st.columns(2)
with col_i:
    st.markdown(f"**Scatter Plot — {x_axis} vs {y_axis}**")
    st.pyplot(charts.chart_scatter(df, x_axis, y_axis), use_container_width=True)

with col_j:
    st.markdown("**Bubble Chart (Bonus) — GDP vs Democracy**")
    st.pyplot(charts.chart_bubble(df), use_container_width=True)

st.markdown("**Heatmap — Correlation Matrix of All Indicators**")
st.pyplot(charts.chart_heatmap(df), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Raw Data
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">🗃️ Section 5 — Filtered Data Table</p>', unsafe_allow_html=True)
display_cols = ["country_name", "year", "region",
                "Electoral Democracy", "Liberal Democracy",
                "Rule of Law", "Political Corruption",
                "Women Empowerment", "GDP per Capita"]
display_cols = [c for c in display_cols if c in df.columns]
st.dataframe(
    df[display_cols].sort_values(["country_name", "year"]).reset_index(drop=True),
    use_container_width=True,
    height=350,
)
st.caption(f"Showing {len(df):,} rows after filters  ·  "
           f"Source: V-Dem Institute v16  ·  EDA Project 2026")
