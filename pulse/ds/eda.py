"""
Pulse — Exploratory Data Analysis
Data Scientist: Silva Vardanyan

Loads behavioral data from the Pulse database and produces summary
statistics and visual exploration used to inform segmentation and
conversion modelling.

Run locally (with DB running):
    python eda.py

Or import individual functions into experiments.ipynb.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@localhost:5433/pulse",
)

SEGMENT_COLORS = {
    "power":   "#00b87a",
    "growing": "#3b82f6",
    "casual":  "#f59e0b",
    "dormant": "#9ca3af",
}

plt.rcParams.update({
    "font.family":    "sans-serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.titlesize":    13,
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
})


# ── Database helpers ──────────────────────────────────────────────────

def get_engine():
    """Return a SQLAlchemy engine connected to the Pulse database."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def load_table(sql: str) -> pd.DataFrame:
    """Execute *sql* and return results as a DataFrame."""
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


# ── Data loaders ──────────────────────────────────────────────────────

def load_users() -> pd.DataFrame:
    """Load full users table."""
    return load_table("SELECT * FROM users ORDER BY user_id")


def load_behavioral_features() -> pd.DataFrame:
    """Load the behavioral feature view (one row per user)."""
    return load_table("SELECT * FROM v_user_behavioral_features ORDER BY user_id")


def load_conversion_outcomes() -> pd.DataFrame:
    """Load conversion_outcomes joined with user segment."""
    return load_table("""
        SELECT co.*, u.segment
        FROM conversion_outcomes co
        JOIN users u ON co.user_id = u.user_id
        ORDER BY co.user_id
    """)


def load_ab_tests() -> pd.DataFrame:
    """Load A/B test results per segment."""
    return load_table("SELECT * FROM ab_tests ORDER BY segment")


# ── EDA functions ─────────────────────────────────────────────────────

def segment_counts(users: pd.DataFrame) -> pd.Series:
    """Return user counts per segment."""
    return users["segment"].value_counts().reindex(SEGMENT_COLORS.keys(), fill_value=0)


def behavioral_summary(features: pd.DataFrame) -> pd.DataFrame:
    """Return mean behavioral metrics grouped by segment."""
    numeric_cols = [
        "avg_sessions_per_week",
        "avg_exports_per_week",
        "avg_paywall_hits",
        "avg_thesaurus_uses",
        "days_since_last_login",
    ]
    available = [c for c in numeric_cols if c in features.columns]
    return (
        features.groupby("segment")[available]
        .mean()
        .round(2)
        .reindex(SEGMENT_COLORS.keys())
    )


def conversion_rate_by_segment(outcomes: pd.DataFrame) -> pd.DataFrame:
    """Return conversion rate and average days-to-convert per segment."""
    grp = outcomes.groupby("segment").agg(
        total=("user_id", "count"),
        converted=("converted", "sum"),
        avg_days=("days_to_convert", "mean"),
    )
    grp["conversion_rate"] = (grp["converted"] / grp["total"]).round(4)
    grp["avg_days"] = grp["avg_days"].round(1)
    return grp.reindex(SEGMENT_COLORS.keys())


def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary of missing values per column."""
    report = pd.DataFrame({
        "missing":   df.isnull().sum(),
        "pct_miss":  (df.isnull().mean() * 100).round(2),
        "dtype":     df.dtypes,
    })
    return report[report["missing"] > 0].sort_values("pct_miss", ascending=False)


# ── Plotting ──────────────────────────────────────────────────────────

def plot_segment_distribution(counts: pd.Series, ax=None):
    """Bar chart of user counts per segment."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    colors = [SEGMENT_COLORS[s] for s in counts.index]
    bars = ax.bar(counts.index, counts.values, color=colors, width=0.55)
    ax.bar_label(bars, padding=4, fontsize=10)
    ax.set_title("User Count by Segment")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Users")
    ax.set_ylim(0, counts.max() * 1.2)
    return ax


def plot_behavioral_heatmap(summary: pd.DataFrame, ax=None):
    """Heatmap of normalised behavioral averages per segment."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 3.5))
    normed = (summary - summary.min()) / (summary.max() - summary.min() + 1e-9)
    sns.heatmap(
        normed,
        annot=summary.values,
        fmt=".2f",
        cmap="YlGnBu",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Normalised value"},
    )
    ax.set_title("Behavioral Averages by Segment (normalised colour scale)")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    return ax


def plot_conversion_rates(conv: pd.DataFrame, ax=None):
    """Horizontal bar chart of conversion rates per segment."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    colors = [SEGMENT_COLORS[s] for s in conv.index]
    rates_pct = conv["conversion_rate"] * 100
    bars = ax.barh(conv.index, rates_pct, color=colors, height=0.55)
    ax.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=10)
    ax.set_xlim(0, rates_pct.max() * 1.35)
    ax.set_title("Conversion Rate by Segment")
    ax.set_xlabel("Conversion Rate (%)")
    ax.invert_yaxis()
    return ax


def plot_correlation_matrix(features: pd.DataFrame, ax=None):
    """Correlation heatmap of numeric behavioral features."""
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5.5))
    numeric = features.select_dtypes(include=np.number).drop(
        columns=["user_id"], errors="ignore"
    )
    corr = numeric.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.4,
        ax=ax,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Feature Correlation Matrix")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    return ax


def plot_sessions_distribution(features: pd.DataFrame, ax=None):
    """KDE plot of sessions-per-week by segment."""
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4))
    for seg, color in SEGMENT_COLORS.items():
        sub = features[features["segment"] == seg]["avg_sessions_per_week"].dropna()
        if len(sub) > 1:
            sub.plot.kde(ax=ax, color=color, label=seg, linewidth=2)
    ax.set_title("Sessions per Week — Distribution by Segment")
    ax.set_xlabel("Avg sessions per week")
    ax.set_ylabel("Density")
    ax.legend(title="Segment")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    return ax


def full_eda_report(save_dir: str = "."):
    """Run the full EDA pipeline and save all plots to *save_dir*."""
    print("Loading data…")
    users    = load_users()
    features = load_behavioral_features()
    outcomes = load_conversion_outcomes()

    print(f"  {len(users):,} users  |  {len(features):,} feature rows  |  {len(outcomes):,} outcome rows")

    # Missing-value check
    mv = missing_value_report(users)
    if mv.empty:
        print("  No missing values in users table.")
    else:
        print("  Missing values detected:")
        print(mv.to_string())

    counts  = segment_counts(users)
    summary = behavioral_summary(features)
    conv    = conversion_rate_by_segment(outcomes)

    print("\nSegment counts:")
    print(counts.to_string())
    print("\nBehavioral averages:")
    print(summary.to_string())
    print("\nConversion rates:")
    print(conv[["total", "converted", "conversion_rate", "avg_days"]].to_string())

    # ── Plots ──────────────────────────────────────────────────────
    os.makedirs(save_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Pulse — EDA Overview", fontsize=15, fontweight="bold", y=1.01)

    plot_segment_distribution(counts, ax=axes[0, 0])
    plot_conversion_rates(conv, ax=axes[0, 1])
    plot_sessions_distribution(features, ax=axes[1, 0])
    plot_behavioral_heatmap(summary, ax=axes[1, 1])

    fig.tight_layout()
    path = os.path.join(save_dir, "eda_overview.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"\nSaved {path}")

    fig2, ax2 = plt.subplots(figsize=(7, 5.5))
    plot_correlation_matrix(features, ax=ax2)
    fig2.tight_layout()
    path2 = os.path.join(save_dir, "eda_correlation.png")
    fig2.savefig(path2, dpi=150, bbox_inches="tight")
    print(f"Saved {path2}")

    plt.show()
    return users, features, outcomes


if __name__ == "__main__":
    full_eda_report(save_dir="outputs")
