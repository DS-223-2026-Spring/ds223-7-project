"""
Pulse — Prediction Script (Final Outputs)
Data Scientist: Silva Vardanyan

Generates conversion probability scores and confidence bands for every
active free-tier user and writes the results to the database.

What this script produces:
    1. Conversion probability score (0-1) for each user — from the final model
    2. Confidence tier: high (>0.7) / medium (0.3-0.7) / low (<0.3)
    3. Top predictor feature and its coefficient → stored in ab_test_results
    4. outputs/predictions.csv — full prediction table (user_id, score, tier, segment)

Run (DB must be reachable):
    python predict.py

Or inside Docker:
    docker-compose exec ds python predict.py

Re-running is safe — predictions are idempotent (overwrites existing rows).
"""

import os
import warnings
import pickle

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from feature_pipeline import (
    load_model_dataset,
    prepare_features,
    build_feature_pipeline,
    FEATURE_COLS,
)
from final_model import train_and_select, save_model, get_feature_importance

warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@localhost:5433/pulse",
)
OUTPUT_DIR = "outputs"
MODEL_PATH = os.path.join(OUTPUT_DIR, "final_model.pkl")


def get_engine():
    """Return a SQLAlchemy engine connected to the Pulse database."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


# ── Model loader / trainer ─────────────────────────────────────────────────────

def get_or_train_model(X_raw: np.ndarray, y: np.ndarray, available: list[str]):
    """Return the fitted winning pipeline, training it if no pickle exists."""
    if os.path.exists(MODEL_PATH):
        print(f"  Loading saved model from {MODEL_PATH}")
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f), None, available
    else:
        print("  No saved model found — training now …")
        results = train_and_select(X_raw, y, available)
        winner_name = next(n for n, r in results.items() if r["is_winner"])
        pipeline = results[winner_name]["pipeline"]
        save_model(pipeline)
        return pipeline, results, available


# ── Prediction generation ──────────────────────────────────────────────────────

def generate_predictions(df: pd.DataFrame, pipeline) -> pd.DataFrame:
    """Run the model on all users and return a predictions DataFrame.

    Parameters
    ----------
    df       : pd.DataFrame — output of load_model_dataset()
    pipeline : fitted sklearn Pipeline

    Returns
    -------
    pd.DataFrame with columns:
        user_id, current_segment, converted (actual),
        conversion_prob, confidence_tier, rank
    """
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].fillna(0).values.astype(float)
    probs = pipeline.predict_proba(X)[:, 1]

    result = df[["user_id", "current_segment", "converted"]].copy()
    result["conversion_prob"] = probs.round(4)
    result["confidence_tier"] = pd.cut(
        probs,
        bins=[-0.001, 0.30, 0.70, 1.001],
        labels=["low", "medium", "high"],
    )
    result["rank"] = result["conversion_prob"].rank(ascending=False, method="min").astype(int)
    return result.sort_values("rank")


def top_predictor(pipeline, available: list[str]) -> tuple[str, float]:
    """Extract the most influential feature and its coefficient/importance."""
    clf = pipeline.named_steps["clf"]
    if hasattr(clf, "coef_"):
        coefs = pd.Series(np.abs(clf.coef_[0]), index=available)
        feat  = coefs.idxmax()
        val   = float(coefs.max())
    elif hasattr(clf, "feature_importances_"):
        imps = pd.Series(clf.feature_importances_, index=available)
        feat = imps.idxmax()
        val  = float(imps.max())
    else:
        feat, val = available[0], 0.0
    return feat, round(val, 6)


# ── DB write ───────────────────────────────────────────────────────────────────

def write_top_predictor_to_db(
    feat: str, coef: float, significance_label: str = "significant"
) -> None:
    """Store the top predictor info in ab_test_results for all completed tests.

    The top_predictor_feature and top_predictor_coef columns in ab_test_results
    surface in the A/B Tests screen to explain which feature drove the result.
    Only updates rows that already exist (created by run_ab_analysis.py).
    """
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE ab_test_results
                SET top_predictor_feature = :feat,
                    top_predictor_coef    = :coef,
                    computed_at           = now()
                WHERE top_predictor_feature IS NULL
            """),
            {"feat": feat, "coef": coef},
        )
        updated = result.rowcount
    if updated > 0:
        print(f"  ✓ Wrote top predictor ({feat} = {coef:.4f}) to {updated} ab_test_results row(s)")
    else:
        print(f"  ℹ  Top predictor already set in ab_test_results (no rows updated)")


def save_predictions_csv(preds: pd.DataFrame, save_dir: str = OUTPUT_DIR) -> str:
    """Write predictions to CSV and return the file path."""
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, "predictions.csv")
    preds.to_csv(path, index=False)
    return path


# ── Summary stats ──────────────────────────────────────────────────────────────

def print_prediction_summary(preds: pd.DataFrame) -> None:
    """Print a concise summary of the prediction output."""
    print(f"\n  Total users scored : {len(preds):,}")
    print(f"  Already converted  : {preds['converted'].sum():,}")
    print()

    tier_counts = preds["confidence_tier"].value_counts().reindex(["high", "medium", "low"])
    print("  Confidence tier distribution:")
    for tier, n in tier_counts.items():
        pct = n / len(preds) * 100
        print(f"    {tier:<8} {n:>4}  ({pct:.1f}%)")

    print("\n  Avg conversion probability by segment:")
    seg_avg = (
        preds.groupby("current_segment")["conversion_prob"]
        .mean()
        .round(4)
        .sort_values(ascending=False)
    )
    for seg, prob in seg_avg.items():
        print(f"    {seg:<10} {prob:.4f}  ({prob:.1%})")

    print("\n  Top 10 most likely to convert:")
    top10 = preds[preds["converted"] == 0].head(10)
    print(top10[["rank", "user_id", "current_segment", "conversion_prob",
                 "confidence_tier"]].to_string(index=False))


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  Pulse — Prediction Pipeline")
    print("=" * 65)

    print("\n[1/4] Loading data …")
    df = load_model_dataset()
    X_raw, y, available = prepare_features(df)
    print(f"  {len(df):,} users  |  {y.sum()} converted  |  "
          f"{len(available)} features: {available}")

    print("\n[2/4] Loading / training model …")
    pipeline, train_results, available = get_or_train_model(X_raw, y, available)

    print("\n[3/4] Generating predictions …")
    preds = generate_predictions(df, pipeline)
    print_prediction_summary(preds)

    csv_path = save_predictions_csv(preds)
    print(f"\n  ✓ Saved {csv_path}")

    print("\n[4/4] Writing top predictor to DB …")
    feat, coef = top_predictor(pipeline, available)
    print(f"  Top predictor: {feat}  (coef = {coef:.4f})")
    write_top_predictor_to_db(feat, coef)

    print("\n✓ Prediction pipeline complete.")
    print(f"  Full results: {csv_path}")
