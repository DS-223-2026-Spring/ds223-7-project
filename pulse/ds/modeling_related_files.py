"""
Pulse — Data Science modeling helpers.

This module contains reusable functions for:
  - Connecting to the database
  - Loading user behavioral features from v_user_behavioral_features
  - Running the segmentation model
  - Computing A/B test statistical significance

Used by experiments.ipynb.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

# ── Database connection ───────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@db:5432/pulse",
)


def get_engine():
    """Return a SQLAlchemy engine connected to the Pulse database."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def load_behavioral_features() -> pd.DataFrame:
    """Load the user behavioral feature view for segmentation.

    Returns a DataFrame from v_user_behavioral_features with one row per user.
    """
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(
            text("SELECT * FROM v_user_behavioral_features"),
            conn,
        )


# ── Segmentation ──────────────────────────────────────────────────────

def assign_segment(row: pd.Series) -> str:
    """Rule-based segment assignment for a single user row.

    Segments:
        power    — high exports + frequent paywall hits
        growing  — rising sessions, below paywall threshold
        casual   — low frequency, high template interest
        dormant  — no activity in 30+ days
    """
    if row.get("days_since_last_login", 999) > 30:
        return "dormant"
    if row.get("avg_exports_per_week", 0) >= 3 and row.get("avg_paywall_hits", 0) >= 2:
        return "power"
    if row.get("avg_sessions_per_week", 0) >= 4:
        return "growing"
    return "casual"


# ── A/B test statistics ───────────────────────────────────────────────

def chi_square_significance(
    control_converted: int,
    control_total: int,
    treatment_converted: int,
    treatment_total: int,
    alpha: float = 0.05,
) -> dict:
    """Chi-square test for A/B test conversion rate difference.

    Returns a dict with p_value, significant flag, and lift_pct.
    """
    from scipy.stats import chi2_contingency
    import numpy as np

    control_not = control_total - control_converted
    treatment_not = treatment_total - treatment_converted

    table = np.array([
        [control_converted, control_not],
        [treatment_converted, treatment_not],
    ])

    _, p_value, _, _ = chi2_contingency(table)

    control_rate = control_converted / control_total if control_total else 0
    treatment_rate = treatment_converted / treatment_total if treatment_total else 0
    lift_pct = ((treatment_rate - control_rate) / control_rate * 100) if control_rate else 0

    return {
        "p_value": round(p_value, 4),
        "significant": p_value < alpha,
        "control_rate": round(control_rate, 4),
        "treatment_rate": round(treatment_rate, 4),
        "lift_pct": round(lift_pct, 2),
    }
