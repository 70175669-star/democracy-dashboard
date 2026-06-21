# charts.py
# ─────────────────────────────────────────────────────────────────────────────
# All chart / visualisation functions for the V-Dem Dashboard.
# Every function receives a (filtered) DataFrame and returns a Matplotlib Figure.
# app.py calls these and passes the figure to st.pyplot().
# ─────────────────────────────────────────────────────────────────────────────

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd

# ── Shared style ──────────────────────────────────────────────────────────────
PALETTE   = ["#1a6faf", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]
BG        = "#fafafa"
GRID_COL  = "#e0e0e0"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    BG,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.color":        GRID_COL,
    "grid.linewidth":    0.7,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
})

SCORE_COLS = [
    "Electoral Democracy", "Liberal Democracy",
    "Participatory Democracy", "Deliberative Democracy",
    "Egalitarian Democracy", "Freedom of Expression",
    "Freedom of Association", "Rule of Law",
    "Political Corruption", "Free & Fair Elections",
    "Universal Suffrage", "Women Empowerment",
]


def _fig(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    return fig, ax


# ── 1. PIE CHART ─────────────────────────────────────────────────────────────
def chart_pie(df: pd.DataFrame) -> plt.Figure:
    """Proportional share of countries by world region (latest year per country)."""
    latest = df.sort_values("year").groupby("country_name").last().reset_index()
    counts = latest["region"].value_counts().dropna()

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(BG)
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE,
        startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(edgecolor="white", linewidth=1.5),
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("Share of Countries by World Region", pad=15)
    ax.legend(counts.index, loc="lower right", fontsize=8,
              bbox_to_anchor=(1.25, 0.0))
    fig.tight_layout()
    return fig


# ── 2. HISTOGRAM ─────────────────────────────────────────────────────────────
def chart_histogram(df: pd.DataFrame, col: str = "Electoral Democracy") -> plt.Figure:
    """Frequency distribution of a chosen democracy index."""
    fig, ax = _fig(10, 5)
    vals = df[col].dropna()
    ax.hist(vals, bins=25, color=PALETTE[0], edgecolor="white", alpha=0.85)
    ax.axvline(vals.mean(),   color=PALETTE[1], linewidth=1.8,
               linestyle="--", label=f"Mean  {vals.mean():.2f}")
    ax.axvline(vals.median(), color=PALETTE[2], linewidth=1.8,
               linestyle=":",  label=f"Median {vals.median():.2f}")
    ax.set_xlabel(col)
    ax.set_ylabel("Number of Country-Year Observations")
    ax.set_title(f"Distribution of {col}")
    ax.legend()
    fig.tight_layout()
    return fig


# ── 3. LINE CHART ─────────────────────────────────────────────────────────────
def chart_line(df: pd.DataFrame) -> plt.Figure:
    """Global average of all five main democracy indices over time."""
    indices = ["Electoral Democracy", "Liberal Democracy",
               "Participatory Democracy", "Deliberative Democracy",
               "Egalitarian Democracy"]
    indices = [c for c in indices if c in df.columns]
    if not indices:
        fig, ax = _fig(12, 5)
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return fig
    annual = df.groupby("year")[indices].mean()
    fig, ax = _fig(12, 5)
    for col, color in zip(indices, PALETTE):
        ax.plot(annual.index, annual[col], label=col, linewidth=2, color=color)
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Score (0–1)")
    ax.set_title("Global Democracy Indices Over Time")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    return fig

# ── 4. BAR CHART ─────────────────────────────────────────────────────────────
def chart_bar(df: pd.DataFrame) -> plt.Figure:
    """Average Electoral Democracy score by world region (latest data)."""
    latest = df.sort_values("year").groupby("country_name").last().reset_index()
    rg = (latest.groupby("region")["Electoral Democracy"]
          .mean().dropna().sort_values(ascending=False))
    fig, ax = _fig(10, 5)
    bars = ax.bar(rg.index, rg.values,
                  color=PALETTE[:len(rg)], edgecolor="white", width=0.6)
    for bar, val in zip(bars, rg.values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.01,
                f"{val:.2f}", ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Mean Electoral Democracy Score")
    ax.set_xlabel("Region")
    ax.set_title("Average Electoral Democracy Score by Region")
    ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    return fig


# ── 5. SCATTER PLOT ───────────────────────────────────────────────────────────
def chart_scatter(df: pd.DataFrame,
                  x_col: str = "Rule of Law",
                  y_col: str = "Liberal Democracy") -> plt.Figure:
    """Relationship between two democracy indicators, coloured by region."""
    plot_df = df.dropna(subset=[x_col, y_col, "region"])
    fig, ax = _fig(10, 7)
    for (region, grp), color in zip(plot_df.groupby("region"), PALETTE):
        ax.scatter(grp[x_col], grp[y_col],
                   label=region, alpha=0.6, s=18,
                   color=color, edgecolors="white", linewidths=0.3)
    # regression line
    x, y = plot_df[x_col].values, plot_df[y_col].values
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() > 2:
        m, b = np.polyfit(x[mask], y[mask], 1)
        xr = np.linspace(x[mask].min(), x[mask].max(), 200)
        ax.plot(xr, m*xr + b, color="black", linewidth=1.2,
                linestyle="--", alpha=0.5, label="Trend")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f"{x_col} vs {y_col}")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    return fig


# ── 6. BOX PLOT ───────────────────────────────────────────────────────────────
def chart_box(df: pd.DataFrame, col: str = "Electoral Democracy") -> plt.Figure:
    """Box plots of a score across world regions."""
    plot_df = df.dropna(subset=[col, "region"])
    fig, ax = _fig(11, 6)
    regions = sorted(plot_df["region"].unique())
    data    = [plot_df[plot_df["region"] == r][col].values for r in regions]
    bp = ax.boxplot(data, patch_artist=True, notch=False,
                    medianprops=dict(color="white", linewidth=2))
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_xticks(range(1, len(regions)+1))
    ax.set_xticklabels(regions, rotation=20, ha="right")
    ax.set_ylabel(col)
    ax.set_title(f"Distribution of {col} by Region")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    return fig


# ── 7. HEATMAP ───────────────────────────────────────────────────────────────
def chart_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Correlation matrix of all main V-Dem indicator columns."""
    cols = [c for c in SCORE_COLS if c in df.columns]
    corr = df[cols].dropna(how="all").corr()
    fig, ax = plt.subplots(figsize=(12, 9))
    fig.patch.set_facecolor(BG)
    sns.heatmap(
        corr, annot=True, fmt=".2f", ax=ax,
        cmap="RdYlGn", vmin=-1, vmax=1, center=0,
        linewidths=0.4, linecolor="white",
        annot_kws={"size": 8},
        cbar_kws={"shrink": 0.8, "label": "Pearson r"},
    )
    ax.set_title("Correlation Matrix of V-Dem Indicators", pad=12)
    ax.tick_params(axis="x", rotation=40, labelsize=8)
    ax.tick_params(axis="y", rotation=0,  labelsize=8)
    fig.tight_layout()
    return fig


# ── 8. AREA CHART ─────────────────────────────────────────────────────────────
def chart_area(df: pd.DataFrame) -> plt.Figure:
    """Stacked area: % of countries scoring > 0.5 on Electoral Democracy per decade."""
    annual = (
        df.groupby("year")
        .apply(lambda g: (g["Electoral Democracy"].dropna() > 0.5).sum()
               / max(g["Electoral Democracy"].dropna().count(), 1) * 100)
        .reset_index(name="pct")
    )
    fig, ax = _fig(12, 5)
    ax.fill_between(annual["year"], annual["pct"], alpha=0.30, color=PALETTE[0])
    ax.plot(annual["year"], annual["pct"], color=PALETTE[0], linewidth=2)
    ax.axvline(1974, color=PALETTE[1], linestyle="--", linewidth=1.2)
    ax.text(1975, annual["pct"].max()*0.85, "Third Wave\n(1974)",
            fontsize=8, color=PALETTE[1])
    ax.set_xlabel("Year")
    ax.set_ylabel("% Countries (score > 0.5)")
    ax.set_title("Share of Electoral Democracies Over Time (Area Chart)")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    return fig


# ── 9. COUNT PLOT ─────────────────────────────────────────────────────────────
def chart_count(df: pd.DataFrame) -> plt.Figure:
    """Count of country-year observations by region."""
    plot_df = df.dropna(subset=["region"])
    fig, ax = _fig(10, 5)
    order = plot_df["region"].value_counts().index.tolist()
    sns.countplot(data=plot_df, y="region", order=order,
                  palette=PALETTE, ax=ax, edgecolor="white")
    ax.set_xlabel("Number of Country-Year Observations")
    ax.set_ylabel("Region")
    ax.set_title("Count of Observations by World Region")
    for container in ax.containers:
        ax.bar_label(container, fontsize=9, padding=3)
    fig.tight_layout()
    return fig


# ── 10. VIOLIN PLOT ───────────────────────────────────────────────────────────
def chart_violin(df: pd.DataFrame, col: str = "Electoral Democracy") -> plt.Figure:
    """Violin plot showing distribution & density of a score by region."""
    plot_df = df.dropna(subset=[col, "region"])
    fig, ax = _fig(12, 6)
    regions = sorted(plot_df["region"].unique())
    sns.violinplot(
        data=plot_df, x="region", y=col, order=regions,
        palette=PALETTE, inner="quartile", ax=ax, cut=0,
    )
    ax.set_xlabel("Region")
    ax.set_ylabel(col)
    ax.set_title(f"Violin Plot: {col} by Region")
    ax.set_ylim(-0.05, 1.05)
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    return fig


# ── BONUS: RADAR CHART ────────────────────────────────────────────────────────

def chart_radar(df: pd.DataFrame) -> plt.Figure:
    """Radar chart comparing 5 democracy dimensions across regions."""
    dims = ["Electoral Democracy", "Liberal Democracy", "Egalitarian Democracy",
            "Deliberative Democracy", "Participatory Democracy"]
    dims = [c for c in dims if c in df.columns]
    if len(dims) < 3:
        fig, ax = _fig(8, 8)
        ax.text(0.5, 0.5, "Not enough data for radar chart",
                ha="center", va="center")
        return fig
    labels = [d.split()[0] for d in dims]
    latest = df.sort_values("year").groupby("country_name").last().reset_index()
    rg = latest.dropna(subset=["region"]).groupby("region")[dims].mean()

    angles = np.linspace(0, 2*np.pi, len(dims), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG)
    for (region, row), color in zip(rg.iterrows(), PALETTE):
        vals = row.tolist() + [row.iloc[0]]
        ax.plot(angles, vals, linewidth=2, color=color, label=region)
        ax.fill(angles, vals, alpha=0.07, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_title("Democracy Dimensions by Region (Radar)", pad=20,
                 fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=9)
    fig.tight_layout()
    return fig


# ── BONUS: BUBBLE CHART ───────────────────────────────────────────────────────
def chart_bubble(df: pd.DataFrame) -> plt.Figure:
    """GDP per Capita vs Electoral Democracy; bubble = population."""
    plot_df = df.dropna(subset=["GDP per Capita", "Electoral Democracy",
                                 "Population", "region"])
    plot_df = plot_df[plot_df["GDP per Capita"] > 0]
    latest  = plot_df.sort_values("year").groupby("country_name").last().reset_index()
    fig, ax = _fig(11, 8)
    for (region, grp), color in zip(latest.groupby("region"), PALETTE):
        sizes = (grp["Population"] / latest["Population"].max()) * 1500 + 20
        ax.scatter(np.log10(grp["GDP per Capita"]), grp["Electoral Democracy"],
                   s=sizes, alpha=0.55, label=region,
                   color=color, edgecolors="white", linewidths=0.4)
    ax.set_xlabel("GDP per Capita (log₁₀ USD)")
    ax.set_ylabel("Electoral Democracy Index")
    ax.set_title("Wealth vs Democracy — Bubble Chart (size = Population)")
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${10**v:,.0f}"))
    ax.legend(fontsize=8, loc="lower right")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    return fig
