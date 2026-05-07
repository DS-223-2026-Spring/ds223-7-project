"""
Pulse — A/B Test Analysis (Thompson Sampling)
Data Scientist: Silva Vardanyan

Reads the live A/B test data from the database, runs Bayesian Thompson
Sampling on each segment's test, and writes the results back to
ab_test_results so the frontend A/B Tests screen shows real data.

Algorithm: Beta-Binomial Thompson Sampling
    - Prior: uniform Beta(1, 1)
    - Posterior: Beta(conversions + 1, non-conversions + 1) per arm
    - Decision criterion: P(treatment > control) >= 0.95

If no formal ab_tests / ab_assignments exist yet (DB freshly seeded),
this script will create them automatically using a 50/50 random split
of the existing users per segment, so the screen always has live data.

Run (DB must be reachable):
    python run_ab_analysis.py

Or inside Docker:
    docker-compose exec ds python run_ab_analysis.py

Re-running is fully idempotent — results are upserted, not duplicated.
"""

import os
import random
import uuid
import warnings

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from modeling_related_files import thompson_sampling_ab_test

warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@localhost:5433/pulse",
)
RANDOM_STATE  = 42
N_TS_SAMPLES  = 10_000   # Monte Carlo draws per test

SEGMENT_COLORS = {
    "power":   "#00b87a",
    "growing": "#3b82f6",
    "casual":  "#f59e0b",
    "dormant": "#9ca3af",
}


def get_engine():
    """Return a SQLAlchemy engine connected to the Pulse database."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _new_id() -> str:
    return str(uuid.uuid4())


def _significance_label(prob_wins: float) -> str:
    """Map Thompson Sampling probability to significance_level enum value."""
    if prob_wins >= 0.95:
        return "significant"
    if prob_wins >= 0.80:
        return "borderline"
    return "not_significant"


# ── Step 1: Ensure ab_tests rows exist (one per segment campaign) ──────────────

def ensure_ab_tests(conn) -> dict:
    """Create ab_tests rows for each segment campaign if they don't exist.

    Returns
    -------
    dict: segment_name → test_id
    """
    rows = conn.execute(text("""
        SELECT s.name AS seg_name, t.test_id
        FROM ab_tests t
        JOIN campaigns c ON c.campaign_id = t.campaign_id
        JOIN segments  s ON s.segment_id  = t.segment_id
    """)).mappings().all()

    existing = {r["seg_name"]: str(r["test_id"]) for r in rows}

    # campaigns table has active_message_id only (no control_message_id column)
    campaigns = conn.execute(text("""
        SELECT s.name AS seg_name, c.campaign_id, c.active_message_id
        FROM campaigns c
        JOIN segments s ON s.segment_id = c.segment_id
    """)).mappings().all()

    for camp in campaigns:
        seg = camp["seg_name"]
        if seg not in existing:
            test_id = _new_id()
            # Get segment_id
            seg_id = conn.execute(
                text("SELECT segment_id FROM segments WHERE name = :n"),
                {"n": seg},
            ).scalar()
            conn.execute(text("""
                INSERT INTO ab_tests (
                    test_id, campaign_id, segment_id,
                    status, started_at, duration_days,
                    control_message_id, treatment_message_id
                ) VALUES (
                    :tid, :cid, :sid,
                    'running', now() - interval '14 days', 14,
                    :ctrl_msg, :treat_msg
                )
                ON CONFLICT DO NOTHING
            """), {
                "tid":       test_id,
                "cid":       str(camp["campaign_id"]),
                "sid":       str(seg_id),
                "ctrl_msg":  str(camp["active_message_id"]) if camp["active_message_id"] else None,
                "treat_msg": str(camp["active_message_id"]) if camp["active_message_id"] else None,
            })
            existing[seg] = test_id
            print(f"  Created ab_tests row for segment '{seg}' (test_id={test_id})")

    return existing


# ── Step 2: Ensure ab_assignments exist (50/50 split of users per segment) ─────

def ensure_ab_assignments(conn, test_map: dict) -> None:
    """Assign unassigned users in each segment to control or treatment 50/50.

    Only assigns users who don't already have an ab_assignments row for
    this test, so re-running is safe.
    """
    rng = random.Random(RANDOM_STATE)

    for seg_name, test_id in test_map.items():
        # Find users in this segment who aren't assigned yet
        unassigned = conn.execute(text("""
            SELECT us.user_id
            FROM user_segments us
            JOIN segments s ON s.segment_id = us.segment_id
            WHERE s.name = :seg
              AND us.expires_at IS NULL
              AND us.user_id NOT IN (
                  SELECT user_id FROM ab_assignments WHERE test_id = :tid
              )
        """), {"seg": seg_name, "tid": test_id}).mappings().all()

        users = [str(r["user_id"]) for r in unassigned]
        if not users:
            continue

        rng.shuffle(users)
        half      = len(users) // 2
        control   = users[:half]
        treatment = users[half:]

        # Get the message_id for this test
        msg_id = conn.execute(
            text("SELECT control_message_id FROM ab_tests WHERE test_id = :tid"),
            {"tid": test_id},
        ).scalar()

        for uid in control:
            conn.execute(text("""
                INSERT INTO ab_assignments
                    (assignment_id, test_id, user_id, group_type, message_id)
                VALUES (:aid, :tid, :uid, 'control', :mid)
                ON CONFLICT (test_id, user_id) DO NOTHING
            """), {
                "aid": _new_id(), "tid": test_id,
                "uid": uid, "mid": str(msg_id) if msg_id else None,
            })
        for uid in treatment:
            conn.execute(text("""
                INSERT INTO ab_assignments
                    (assignment_id, test_id, user_id, group_type, message_id)
                VALUES (:aid, :tid, :uid, 'treatment', :mid)
                ON CONFLICT (test_id, user_id) DO NOTHING
            """), {
                "aid": _new_id(), "tid": test_id,
                "uid": uid, "mid": str(msg_id) if msg_id else None,
            })

        print(f"  Assigned {len(control)} control + {len(treatment)} treatment "
              f"for '{seg_name}'")


# ── Step 3: Link conversion_outcomes to their test ────────────────────────────

def link_conversions_to_tests(conn) -> None:
    """Update conversion_outcomes to set test_id and group_type from assignments.

    Only updates rows where test_id IS NULL so existing links are preserved.
    """
    conn.execute(text("""
        UPDATE conversion_outcomes co
        SET test_id    = aa.test_id,
            group_type = aa.group_type
        FROM ab_assignments aa
        WHERE aa.user_id = co.user_id
          AND co.test_id IS NULL
    """))
    print("  Linked conversion_outcomes → ab_assignments")


# ── Step 4: Count and run Thompson Sampling ───────────────────────────────────

def compute_ab_results(conn, test_map: dict) -> list[dict]:
    """For each test, count conversions per arm and run Thompson Sampling.

    Returns list of result dicts ready to upsert into ab_test_results.
    """
    results = []
    for seg_name, test_id in test_map.items():
        row = conn.execute(text("""
            SELECT
                COUNT(aa.user_id) FILTER (WHERE aa.group_type = 'control')   AS ctrl_total,
                COUNT(aa.user_id) FILTER (WHERE aa.group_type = 'treatment') AS treat_total,
                COUNT(co.user_id) FILTER (
                    WHERE aa.group_type = 'control'
                      AND co.decision = 'upgraded')                           AS ctrl_conv,
                COUNT(co.user_id) FILTER (
                    WHERE aa.group_type = 'treatment'
                      AND co.decision = 'upgraded')                           AS treat_conv
            FROM ab_assignments aa
            LEFT JOIN conversion_outcomes co
                ON co.user_id = aa.user_id
               AND co.test_id = aa.test_id
            WHERE aa.test_id = :tid
        """), {"tid": test_id}).mappings().first()

        if not row:
            continue

        ctrl_total  = int(row["ctrl_total"]  or 0)
        treat_total = int(row["treat_total"] or 0)
        ctrl_conv   = int(row["ctrl_conv"]   or 0)
        treat_conv  = int(row["treat_conv"]  or 0)

        if ctrl_total == 0 and treat_total == 0:
            continue

        # Run Thompson Sampling
        ts = thompson_sampling_ab_test(
            control_converted=ctrl_conv,
            control_total=max(ctrl_total, 1),
            treatment_converted=treat_conv,
            treatment_total=max(treat_total, 1),
            n_samples=N_TS_SAMPLES,
            random_state=RANDOM_STATE,
        )

        sig_label   = _significance_label(ts["prob_treatment_wins"])
        winner_grp  = "treatment" if ts["significant"] else None

        results.append({
            "test_id":           test_id,
            "ctrl_total":        ctrl_total,
            "ctrl_conv":         ctrl_conv,
            "treat_total":       treat_total,
            "treat_conv":        treat_conv,
            "control_rate":      ts["control_rate"],
            "treatment_rate":    ts["treatment_rate"],
            "lift_pct":          ts["lift_pct"],
            "prob_treatment_wins": ts["prob_treatment_wins"],
            "significance":      sig_label,
            "winner":            winner_grp,
            "segment":           seg_name,
        })

        print(f"  {seg_name:<10} ctrl={ctrl_conv}/{ctrl_total}  "
              f"treat={treat_conv}/{treat_total}  "
              f"P(treatment wins)={ts['prob_treatment_wins']:.4f}  "
              f"→ {sig_label}")

    return results


# ── Step 5: Upsert results into ab_test_results ───────────────────────────────

def upsert_ab_results(conn, results: list[dict]) -> None:
    """Write Thompson Sampling results to ab_test_results (upsert by test_id)."""
    for r in results:
        conn.execute(text("""
            INSERT INTO ab_test_results (
                result_id,
                test_id,
                control_shown,      control_converted,
                treatment_shown,    treatment_converted,
                control_rate,       treatment_rate,
                lift_pct,
                chi_square_stat,    -- stores n_samples (10 000) — Thompson Sampling
                p_value,            -- stores prob_treatment_wins
                significance,
                winning_group,
                computed_at
            ) VALUES (
                :rid, :tid,
                :ctrl_shown,  :ctrl_conv,
                :treat_shown, :treat_conv,
                :ctrl_rate,   :treat_rate,
                :lift,
                :n_samples,   :prob_wins,
                :sig::significance_level,
                :winner::ab_group,
                now()
            )
            ON CONFLICT (test_id) DO UPDATE SET
                control_shown      = EXCLUDED.control_shown,
                control_converted  = EXCLUDED.control_converted,
                treatment_shown    = EXCLUDED.treatment_shown,
                treatment_converted = EXCLUDED.treatment_converted,
                control_rate       = EXCLUDED.control_rate,
                treatment_rate     = EXCLUDED.treatment_rate,
                lift_pct           = EXCLUDED.lift_pct,
                chi_square_stat    = EXCLUDED.chi_square_stat,
                p_value            = EXCLUDED.p_value,
                significance       = EXCLUDED.significance,
                winning_group      = EXCLUDED.winning_group,
                computed_at        = now()
        """), {
            "rid":        _new_id(),
            "tid":        r["test_id"],
            "ctrl_shown": r["ctrl_total"],
            "ctrl_conv":  r["ctrl_conv"],
            "treat_shown":r["treat_total"],
            "treat_conv": r["treat_conv"],
            "ctrl_rate":  r["control_rate"],
            "treat_rate": r["treatment_rate"],
            "lift":       r["lift_pct"],
            "n_samples":  N_TS_SAMPLES,
            "prob_wins":  r["prob_treatment_wins"],
            "sig":        r["significance"],
            "winner":     r["winner"],
        })
    print(f"  ✓ Upserted {len(results)} rows into ab_test_results")


# ── Step 6: Mark completed tests ──────────────────────────────────────────────

def mark_completed_tests(conn, results: list[dict]) -> None:
    """Set test status to 'completed' + ended_at for significant tests."""
    for r in results:
        if r["significance"] == "significant":
            conn.execute(text("""
                UPDATE ab_tests
                SET status   = 'completed',
                    ended_at = now()
                WHERE test_id = :tid
                  AND status != 'completed'
            """), {"tid": r["test_id"]})
    print("  ✓ Marked significant tests as 'completed'")


# ── Summary report ─────────────────────────────────────────────────────────────

def print_summary(results: list[dict]) -> None:
    """Print a clean summary table of Thompson Sampling results."""
    if not results:
        print("  (no results computed)")
        return

    print("\n" + "=" * 70)
    print("  Thompson Sampling A/B Test Summary")
    print("=" * 70)
    print(f"  {'Segment':<12} {'Ctrl%':>7} {'Treat%':>8} {'Lift':>7} "
          f"{'P(win)':>8} {'Result':<16}")
    print("  " + "-" * 65)
    for r in results:
        ctrl_pct  = r["control_rate"]   * 100
        treat_pct = r["treatment_rate"] * 100
        lift      = r["lift_pct"]
        prob      = r["prob_treatment_wins"]
        sig       = r["significance"]
        icon      = "★ SIGNIFICANT" if sig == "significant" else (
                    "~ borderline"  if sig == "borderline"  else "  no signal")
        print(f"  {r['segment']:<12} {ctrl_pct:>6.1f}% {treat_pct:>7.1f}% "
              f"{lift:>+6.1f}% {prob:>8.4f}  {icon}")
    print("=" * 70)


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  Pulse — A/B Test Analysis (Thompson Sampling)")
    print("=" * 65)

    engine = get_engine()
    with engine.begin() as conn:

        print("\n[1/5] Ensuring ab_tests rows exist …")
        test_map = ensure_ab_tests(conn)
        print(f"  Tests found/created: {list(test_map.keys())}")

        print("\n[2/5] Ensuring ab_assignments exist (50/50 split) …")
        ensure_ab_assignments(conn, test_map)

        print("\n[3/5] Linking conversion_outcomes → tests …")
        link_conversions_to_tests(conn)

        print("\n[4/5] Running Thompson Sampling per segment …")
        results = compute_ab_results(conn, test_map)

        print("\n[5/5] Upserting results into ab_test_results …")
        upsert_ab_results(conn, results)
        mark_completed_tests(conn, results)

    print_summary(results)
    print("\n✓ A/B analysis complete — results live in ab_test_results.")
