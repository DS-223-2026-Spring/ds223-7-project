"""
Pulse — Data Science modeling helpers.
Data Scientist: Silva Vardanyan

This module contains reusable functions for:
  - Connecting to the database
  - Loading user behavioral features from v_user_behavioral_features
  - Running the K-Means segmentation model
  - Computing A/B test significance via Thompson Sampling (Bayesian)

Used by experiments.ipynb.
"""

import os
import pandas as pd
import numpy as np
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


# ── Segmentation (K-Means) ────────────────────────────────────────────

def kmeans_segment(df: pd.DataFrame) -> pd.Series:
    """Assign segments to all users using K-Means clustering (k=4).

    Delegates to segment_kmeans.run_kmeans(), which:
        1. Scales the 8 behavioral features (impute median → StandardScaler)
        2. Fits KMeans(k=4, n_init=20) for stable centroids
        3. Maps each cluster to a named segment by inspecting centroids:
               dormant  — highest days_since_last_login
               power    — highest total_exports + total_paywall_hits
               growing  — highest sessions_per_week (from remaining)
               casual   — the leftover cluster

    Parameters
    ----------
    df : DataFrame — output of load_behavioral_features(), one row per user

    Returns
    -------
    pd.Series of segment names (same index as df)
    """
    from segment_kmeans import run_kmeans, save_kmeans_model
    _, labels, mapping = run_kmeans(df)
    save_kmeans_model(_)
    return pd.Series([mapping[lbl] for lbl in labels], index=df.index)


def assign_segment(row: pd.Series) -> str:
    """Deprecated — rule-based fallback, kept for backward compatibility.

    Use kmeans_segment(df) instead for data-driven segmentation.
    """
    if row.get("days_since_last_login", 999) > 30:
        return "dormant"
    if row.get("avg_exports_per_week", 0) >= 3 and row.get("avg_paywall_hits", 0) >= 2:
        return "power"
    if row.get("avg_sessions_per_week", 0) >= 4:
        return "growing"
    return "casual"


# ── A/B test statistics (Thompson Sampling) ───────────────────────────

def thompson_sampling_ab_test(
    control_converted: int,
    control_total: int,
    treatment_converted: int,
    treatment_total: int,
    n_samples: int = 10_000,
    random_state: int = 42,
) -> dict:
    """Thompson Sampling A/B test using Bayesian Beta-Binomial inference.

    Models each variant's true conversion rate as a Beta posterior:

        Beta(alpha, beta)  where
            alpha = conversions + 1          (successes + uniform prior)
            beta  = non-conversions + 1      (failures  + uniform prior)

    Draws *n_samples* Monte Carlo samples from each posterior and estimates:
        - prob_treatment_wins : P(treatment_rate > control_rate)
        - significant         : True when prob_treatment_wins >= 0.95
        - control_rate        : posterior mean of control variant
        - treatment_rate      : posterior mean of treatment variant
        - lift_pct            : relative lift of treatment over control

    Parameters
    ----------
    control_converted   : int  — conversions in the control group
    control_total       : int  — total users in the control group
    treatment_converted : int  — conversions in the treatment group
    treatment_total     : int  — total users in the treatment group
    n_samples           : int  — Monte Carlo draws (default 10 000)
    random_state        : int  — seed for reproducibility (default 42)

    Returns
    -------
    dict with keys:
        prob_treatment_wins, significant, control_rate, treatment_rate,
        lift_pct, n_samples
    """
    import numpy as np

    rng = np.random.default_rng(random_state)

    # Posterior parameters (Beta-Binomial with uniform Beta(1,1) prior)
    ctrl_alpha  = control_converted + 1
    ctrl_beta   = (control_total - control_converted) + 1
    treat_alpha = treatment_converted + 1
    treat_beta  = (treatment_total - treatment_converted) + 1

    # Monte Carlo draws from each Beta posterior
    ctrl_samples  = rng.beta(ctrl_alpha,  ctrl_beta,  n_samples)
    treat_samples = rng.beta(treat_alpha, treat_beta, n_samples)

    prob_treatment_wins = float((treat_samples > ctrl_samples).mean())

    # Posterior means as point estimates
    control_rate   = ctrl_alpha  / (ctrl_alpha  + ctrl_beta)
    treatment_rate = treat_alpha / (treat_alpha + treat_beta)
    lift_pct = (
        (treatment_rate - control_rate) / control_rate * 100
        if control_rate else 0.0
    )

    return {
        "prob_treatment_wins": round(prob_treatment_wins, 4),
        "significant":         prob_treatment_wins >= 0.95,
        "control_rate":        round(control_rate,   4),
        "treatment_rate":      round(treatment_rate, 4),
        "lift_pct":            round(lift_pct, 2),
        "n_samples":           n_samples,
    }


# ── Backward-compatibility alias ──────────────────────────────────────

def chi_square_significance(
    control_converted: int,
    control_total: int,
    treatment_converted: int,
    treatment_total: int,
    alpha: float = 0.05,
) -> dict:
    """Deprecated — use thompson_sampling_ab_test() instead.

    Kept for backward compatibility only.  Delegates to Thompson Sampling
    and maps the result back to the old key names so existing callers
    do not break.
    """
    result = thompson_sampling_ab_test(
        control_converted, control_total,
        treatment_converted, treatment_total,
    )
    # Expose a synthetic p_value for any code that still reads it
    # (1 - prob_treatment_wins is the Bayesian "probability of no effect")
    p_value = 1.0 - result["prob_treatment_wins"]
    return {
        "p_value":        round(p_value, 4),
        "significant":    result["significant"],
        "control_rate":   result["control_rate"],
        "treatment_rate": result["treatment_rate"],
        "lift_pct":       result["lift_pct"],
    }
