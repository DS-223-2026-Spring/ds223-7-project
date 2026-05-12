"""
Pulse — Segment Summary (Milestone 4)
Data Scientist: Silva Vardanyan

Generates per-segment summary statistics combining:
  - Behavioral averages from the DB (sessions, exports, paywall hits)
  - Conversion probability scores from user_conversion_scores (if populated)
  - A/B test results from ab_test_results (if run_ab_analysis.py has run)

Outputs:
  outputs/segment_summary.csv        — human-readable summary table
  outputs/segment_summary.json       — machine-readable version for frontend

Run (DB must be reachable):
    python segment_summary.py

Or inside Docker:
    docker-compose exec ds python segment_summary.py

Run order (for M4 full pipeline):
    1. docker-compose up --build          # seeds DB with 442 users
    2. python run_ab_analysis.py          # populates ab_test_results
    3. python predict.py                  # trains model, writes user_conversion_scores
    4. python segment_summary.py          # generates summary for frontend
"""

import json
import os
import warnings

import pandas as pd
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@localhost:5433/pulse",
)
OUTPUT_DIR = "outputs"

SEGMENT_ORDER      = ["power", "growing", "casual", "dormant"]
RECOMMENDED_ACTION = {
    "power":   "Upsell — users regularly hit export limits. Show Pro unlock CTA.",
    "growing": "Nurture — rising activity. Highlight advanced features.",
    "casual":  "Re-engage — template library hook. Show value of Pro templates.",
    "dormant": "Win-back — offer time-limited discount (30%) with urgency.",
}


def get_engine():
    """Return a SQLAlchemy engine connected to the Pulse database."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def load_segment_behavioral(conn) -> pd.DataFrame:
    """Load behavioral averages from the DB view."""
    rows = conn.execute(text("""
        SELECT
            s.name                                           AS segment_name,
            s.label,
            s.color_hex,
            COUNT(us.user_id)                               AS user_count,
            ROUND(AVG(us.feature_session_frequency), 2)    AS avg_sessions_per_week,
            ROUND(AVG(u.total_exports), 1)                  AS avg_exports,
            ROUND(AVG(u.total_paywall_hits), 1)             AS avg_paywall_hits
        FROM segments s
        LEFT JOIN user_segments us ON us.segment_id = s.segment_id
            AND us.expires_at IS NULL
        LEFT JOIN users u ON u.user_id = us.user_id
        GROUP BY s.name, s.label, s.color_hex
        ORDER BY s.name
    """)).mappings().all()
    return pd.DataFrame(rows)


def load_conversion_scores(conn) -> pd.DataFrame:
    """Load avg conversion prob per segment from user_conversion_scores."""
    try:
        rows = conn.execute(text("""
            SELECT
                segment_name,
                ROUND(AVG(conversion_prob), 4)  AS avg_conversion_prob,
                COUNT(*)                         AS scored_users,
                COUNT(*) FILTER (WHERE confidence_tier = 'high')   AS high_confidence,
                COUNT(*) FILTER (WHERE confidence_tier = 'medium') AS medium_confidence,
                COUNT(*) FILTER (WHERE confidence_tier = 'low')    AS low_confidence
            FROM user_conversion_scores
            GROUP BY segment_name
        """)).mappings().all()
        return pd.DataFrame(rows)
    except Exception:
        print("  Warning: user_conversion_scores not yet populated — run predict.py first")
        return pd.DataFrame(columns=["segment_name", "avg_conversion_prob",
                                     "scored_users", "high_confidence",
                                     "medium_confidence", "low_confidence"])


def load_ab_results(conn) -> pd.DataFrame:
    """Load A/B test significance and lift per segment."""
    try:
        rows = conn.execute(text("""
            SELECT
                s.name           AS segment_name,
                r.control_rate,
                r.treatment_rate,
                r.lift_pct,
                r.significance,
                r.p_value
            FROM ab_test_results r
            JOIN ab_tests t  ON t.test_id    = r.test_id
            JOIN segments s  ON s.segment_id = t.segment_id
        """)).mappings().all()
        return pd.DataFrame(rows)
    except Exception:
        print("  Warning: ab_test_results not yet populated — run run_ab_analysis.py first")
        return pd.DataFrame(columns=["segment_name", "control_rate", "treatment_rate",
                                     "lift_pct", "significance", "p_value"])


def build_summary(behavioral: pd.DataFrame,
                  scores: pd.DataFrame,
                  ab_results: pd.DataFrame) -> pd.DataFrame:
    """Merge all data sources into a single per-segment summary DataFrame."""
    df = behavioral.copy()
    df["segment_name"] = df["segment_name"].astype(str)

    if not scores.empty:
        scores["segment_name"] = scores["segment_name"].astype(str)
        df = df.merge(scores[["segment_name", "avg_conversion_prob",
                               "high_confidence", "medium_confidence", "low_confidence"]],
                      on="segment_name", how="left")
    else:
        df["avg_conversion_prob"] = None
        df["high_confidence"]     = None
        df["medium_confidence"]   = None
        df["low_confidence"]      = None

    if not ab_results.empty:
        ab_results["segment_name"] = ab_results["segment_name"].astype(str)
        df = df.merge(ab_results[["segment_name", "control_rate", "treatment_rate",
                                   "lift_pct", "significance"]],
                      on="segment_name", how="left")
    else:
        df["control_rate"]   = None
        df["treatment_rate"] = None
        df["lift_pct"]       = None
        df["significance"]   = None

    df["recommended_action"] = df["segment_name"].map(RECOMMENDED_ACTION)

    # Enforce display order
    df["_order"] = df["segment_name"].map(
        {s: i for i, s in enumerate(SEGMENT_ORDER)}
    ).fillna(99)
    df = df.sort_values("_order").drop(columns=["_order"]).reset_index(drop=True)
    return df


def save_outputs(df: pd.DataFrame) -> None:
    """Write summary to CSV and JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    csv_path = os.path.join(OUTPUT_DIR, "segment_summary.csv")
    df.to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    json_path = os.path.join(OUTPUT_DIR, "segment_summary.json")
    df.to_json(json_path, orient="records", indent=2, force_ascii=False)
    print(f"  Saved {json_path}")


def print_summary_table(df: pd.DataFrame) -> None:
    """Print a clean console summary."""
    print("\n" + "=" * 80)
    print("  Pulse — Segment Summary (Milestone 4)")
    print("=" * 80)
    print(f"  {'Segment':<10} {'Users':>6} {'Sess/wk':>8} {'Exports':>8} "
          f"{'Paywall':>8} {'Conv%':>7} {'Lift%':>7} {'Significance':<16}")
    print("  " + "-" * 76)
    for _, row in df.iterrows():
        conv = f"{float(row['avg_conversion_prob']):.1%}" if pd.notna(row.get("avg_conversion_prob")) else "—"
        lift = f"+{float(row['lift_pct']):.1f}%" if pd.notna(row.get("lift_pct")) else "—"
        sig  = str(row.get("significance") or "—")
        print(
            f"  {str(row['segment_name']):<10} "
            f"{int(row['user_count'] or 0):>6} "
            f"{float(row['avg_sessions_per_week'] or 0):>8.1f} "
            f"{float(row['avg_exports'] or 0):>8.1f} "
            f"{float(row['avg_paywall_hits'] or 0):>8.1f} "
            f"{conv:>7} {lift:>7} {sig:<16}"
        )
    print("=" * 80)
    print("\n  Recommended actions:")
    for _, row in df.iterrows():
        print(f"  {str(row['segment_name']).title():<10}: {row['recommended_action']}")


if __name__ == "__main__":
    print("=" * 65)
    print("  Pulse — Segment Summary Generator")
    print("=" * 65)

    engine = get_engine()
    with engine.connect() as conn:
        print("\n[1/3] Loading behavioral data …")
        behavioral = load_segment_behavioral(conn)
        print(f"  {len(behavioral)} segments found")

        print("\n[2/3] Loading conversion scores …")
        scores = load_conversion_scores(conn)
        if not scores.empty:
            print(f"  {scores['scored_users'].sum():,} users scored")

        print("\n[3/3] Loading A/B test results …")
        ab_results = load_ab_results(conn)
        if not ab_results.empty:
            print(f"  {len(ab_results)} test results found")

    summary = build_summary(behavioral, scores, ab_results)
    print_summary_table(summary)
    save_outputs(summary)

    print("\n✓ Segment summary complete.")
    print("  Use outputs/segment_summary.json for frontend integration.")
