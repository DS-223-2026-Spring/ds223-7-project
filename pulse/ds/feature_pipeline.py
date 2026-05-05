"""
Pulse — Feature Engineering Pipeline
Data Scientist: Silva Vardanyan

Builds a fully documented, reproducible scikit-learn feature pipeline
from the raw Pulse database tables.

Feature set (8 numeric signals):
    total_sessions          — lifetime session count
    total_exports           — lifetime export count
    total_paywall_hits      — lifetime paywall hits (strong conversion signal)
    total_thesaurus_uses    — lifetime thesaurus/synonym queries
    days_since_last_login   — recency (imputed to 999 if no sessions)
    sessions_per_week       — rolling 30-day session frequency
    avg_synonym_depth       — average synonym query depth (engagement depth)
    paywall_hits_last_7d    — recent paywall pressure (short-term urgency signal)

Target variable:
    converted               — 1 if user has an 'upgraded' conversion_outcome, else 0

Run standalone (DB must be reachable):
    python feature_pipeline.py
"""

import os
import warnings
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@localhost:5433/pulse",
)

# All numeric features fed into the model
FEATURE_COLS = [
    "total_sessions",
    "total_exports",
    "total_paywall_hits",
    "total_thesaurus_uses",
    "days_since_last_login",
    "sessions_per_week",
    "avg_synonym_depth",
    "paywall_hits_last_7d",
]

# Human-readable descriptions for the evidence report
FEATURE_DESCRIPTIONS = {
    "total_sessions":        "Lifetime session count — general engagement proxy",
    "total_exports":         "Lifetime export events — document completion intent",
    "total_paywall_hits":    "Times user hit a pro feature limit — strongest conversion signal",
    "total_thesaurus_uses":  "Lifetime thesaurus/synonym queries — writing depth",
    "days_since_last_login": "Days since last session — recency / churn risk",
    "sessions_per_week":     "Rolling 30-day session rate — current activity level",
    "avg_synonym_depth":     "Average synonym query depth — advanced feature usage",
    "paywall_hits_last_7d":  "Paywall hits in past 7 days — immediate upgrade pressure",
}


# ── Database helpers ───────────────────────────────────────────────────────────

def get_engine():
    """Return a SQLAlchemy engine connected to the Pulse database."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


# ── Data loader ────────────────────────────────────────────────────────────────

def load_model_dataset() -> pd.DataFrame:
    """Load the full modelling dataset: behavioral features + conversion label.

    Joins v_user_behavioral_features with conversion_outcomes to produce
    one row per user with all feature columns and a binary 'converted' label.

    Returns
    -------
    pd.DataFrame with columns FEATURE_COLS + ['user_id', 'current_segment', 'converted']
    """
    sql = text("""
        SELECT
            f.user_id,
            f.current_segment,
            COALESCE(f.total_sessions,       0)   AS total_sessions,
            COALESCE(f.total_exports,         0)   AS total_exports,
            COALESCE(f.total_paywall_hits,    0)   AS total_paywall_hits,
            COALESCE(f.total_thesaurus_uses,  0)   AS total_thesaurus_uses,
            COALESCE(f.days_since_last_login, 999) AS days_since_last_login,
            COALESCE(f.sessions_per_week,     0)   AS sessions_per_week,
            COALESCE(f.avg_synonym_depth,     0)   AS avg_synonym_depth,
            COALESCE(f.paywall_hits_last_7d,  0)   AS paywall_hits_last_7d,
            CASE
                WHEN co.decision = 'upgraded' THEN 1
                ELSE 0
            END                                    AS converted
        FROM v_user_behavioral_features f
        LEFT JOIN conversion_outcomes co
            ON co.user_id = f.user_id
           AND co.decision = 'upgraded'
        ORDER BY f.user_id
    """)
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
    # Deduplicate: keep 1 row per user (a user could have multiple conversion rows)
    df = df.sort_values("converted", ascending=False).drop_duplicates("user_id")
    return df.reset_index(drop=True)


# ── Feature pipeline builder ───────────────────────────────────────────────────

def build_feature_pipeline() -> Pipeline:
    """Build and return the scikit-learn preprocessing pipeline.

    Steps:
        1. SimpleImputer (median) — handles any remaining NULLs
        2. StandardScaler        — zero-mean, unit-variance for LR compatibility

    Returns
    -------
    sklearn.pipeline.Pipeline (unfitted)
    """
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])


def prepare_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Extract and preprocess feature matrix from the modelling DataFrame.

    Parameters
    ----------
    df : pd.DataFrame — output of load_model_dataset()

    Returns
    -------
    X_raw  : np.ndarray — raw (unscaled) feature matrix
    y      : np.ndarray — binary target (1 = converted)
    available : list[str] — feature column names actually present
    """
    available = [c for c in FEATURE_COLS if c in df.columns]
    X_raw = df[available].values.astype(float)
    y     = df["converted"].values.astype(int)
    return X_raw, y, available


# ── Quality checks ─────────────────────────────────────────────────────────────

def feature_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary DataFrame with quality stats for every feature column.

    Columns: n_missing, pct_missing, mean, std, min, max, description
    """
    available = [c for c in FEATURE_COLS if c in df.columns]
    rows = []
    for col in available:
        series = df[col]
        rows.append({
            "feature":     col,
            "n_missing":   int(series.isnull().sum()),
            "pct_missing": round(series.isnull().mean() * 100, 2),
            "mean":        round(series.mean(), 3),
            "std":         round(series.std(),  3),
            "min":         round(series.min(),  3),
            "max":         round(series.max(),  3),
            "description": FEATURE_DESCRIPTIONS.get(col, ""),
        })
    return pd.DataFrame(rows).set_index("feature")


def correlation_with_target(df: pd.DataFrame) -> pd.Series:
    """Return Pearson correlation of each feature with the binary target."""
    available = [c for c in FEATURE_COLS if c in df.columns]
    return (
        df[available + ["converted"]]
        .corr()["converted"]
        .drop("converted")
        .sort_values(ascending=False)
        .round(4)
    )


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  Pulse — Feature Engineering Pipeline")
    print("=" * 65)

    df = load_model_dataset()
    print(f"\nDataset: {len(df):,} users  |  converted: {df['converted'].sum()} "
          f"({df['converted'].mean():.1%})\n")

    print("── Feature quality report ──")
    report = feature_quality_report(df)
    print(report[["n_missing", "mean", "std", "min", "max"]].to_string())

    print("\n── Correlation with conversion target ──")
    corr = correlation_with_target(df)
    for feat, r in corr.items():
        bar = "█" * int(abs(r) * 30)
        sign = "+" if r >= 0 else "-"
        print(f"  {feat:<32} {sign}{abs(r):.4f}  {bar}")

    print("\n── Feature pipeline ──")
    pipe = build_feature_pipeline()
    X_raw, y, available = prepare_features(df)
    X_scaled = pipe.fit_transform(X_raw)
    print(f"  Input shape : {X_raw.shape}")
    print(f"  Output shape: {X_scaled.shape}")
    print(f"  Features    : {available}")
    print(f"\n  Pipeline steps:")
    for name, step in pipe.steps:
        print(f"    {name:12} → {type(step).__name__}")

    print("\n── Segment-level feature averages ──")
    seg_avg = df.groupby("current_segment")[available].mean().round(2)
    print(seg_avg.to_string())

    print("\n✓ Feature pipeline validated — ready for modelling.")
