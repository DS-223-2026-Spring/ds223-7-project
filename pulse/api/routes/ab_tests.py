"""
A/B Tests screen endpoints.

GET  /api/ab-tests/summary      → v_ab_test_summary
GET  /api/ab-tests/comparison   → v_segment_ab_comparison
POST /api/ab-tests/run-analysis → run Thompson Sampling inline, upsert results
"""

import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schema import ABTestSummary, SegmentABComparison, RunAnalysisResult

router = APIRouter(prefix="/api/ab-tests", tags=["ab-tests"])

N_TS_SAMPLES = 10_000
RANDOM_SEED  = 42


# ── Thompson Sampling (pure Python stdlib — no numpy needed) ─────────────────

def _thompson_sampling(ctrl_conv: int, ctrl_total: int,
                       treat_conv: int, treat_total: int,
                       n: int = N_TS_SAMPLES) -> dict:
    """Beta-Binomial Thompson Sampling.

    Prior: Beta(1, 1).  Posterior: Beta(conv+1, non_conv+1).
    Returns prob_treatment_wins, control_rate, treatment_rate, lift_pct.
    """
    rng = random.Random(RANDOM_SEED)
    ctrl_alpha  = ctrl_conv  + 1
    ctrl_beta   = (ctrl_total  - ctrl_conv)  + 1
    treat_alpha = treat_conv + 1
    treat_beta  = (treat_total - treat_conv) + 1

    ctrl_samples  = [rng.betavariate(ctrl_alpha,  ctrl_beta)  for _ in range(n)]
    treat_samples = [rng.betavariate(treat_alpha, treat_beta) for _ in range(n)]

    prob_wins    = sum(t > c for t, c in zip(treat_samples, ctrl_samples)) / n
    ctrl_rate    = ctrl_alpha  / (ctrl_alpha  + ctrl_beta)
    treat_rate   = treat_alpha / (treat_alpha + treat_beta)
    lift_pct     = ((treat_rate - ctrl_rate) / ctrl_rate * 100) if ctrl_rate else None

    if prob_wins >= 0.95:
        significance = "significant"
    elif prob_wins >= 0.80:
        significance = "borderline"
    else:
        significance = "not_significant"

    winner = None
    if prob_wins >= 0.95:
        winner = "treatment"
    elif prob_wins <= 0.05:
        winner = "control"

    return {
        "prob_wins":    round(prob_wins, 4),
        "ctrl_rate":    round(ctrl_rate, 4),
        "treat_rate":   round(treat_rate, 4),
        "lift_pct":     round(lift_pct, 2) if lift_pct is not None else None,
        "significance": significance,
        "winner":       winner,
    }


def _significance_to_status(sig: str) -> str:
    return "completed" if sig == "significant" else "running"


# ── GET /api/ab-tests/summary ────────────────────────────────────────────────

@router.get("/summary", response_model=list[ABTestSummary],
            responses={200: {"description": "A/B test results per segment"}})
def get_ab_test_summary(db: Session = Depends(get_db)):
    """Cards on the A/B Tests screen — one per segment test.

    Shows live counts (control_n, treatment_n, converted) plus Thompson
    Sampling results from ab_test_results.  Uses v_ab_test_summary.
    """
    try:
        rows = db.execute(text("SELECT * FROM v_ab_test_summary")).mappings().all()
        return [
            ABTestSummary(
                segment_name=r["segment_name"],
                segment_label=r["segment_label"],
                color_hex=r["color_hex"],
                test_id=str(r["test_id"]),
                status=r["status"],
                started_at=r.get("started_at"),
                ended_at=r.get("ended_at"),
                duration_days=r["duration_days"],
                total_assigned=r["total_assigned"],
                control_n=r["control_n"],
                treatment_n=r["treatment_n"],
                control_converted=r["control_converted"],
                treatment_converted=r["treatment_converted"],
                control_rate=float(r["control_rate"]) if r.get("control_rate") else None,
                treatment_rate=float(r["treatment_rate"]) if r.get("treatment_rate") else None,
                lift_pct=float(r["lift_pct"]) if r.get("lift_pct") else None,
                p_value=float(r["p_value"]) if r.get("p_value") else None,
                significance=r.get("significance"),
                winning_group=r.get("winning_group"),
            )
            for r in rows
        ]
    except Exception:
        return []


# ── GET /api/ab-tests/comparison ─────────────────────────────────────────────

@router.get("/comparison", response_model=list[SegmentABComparison],
            responses={200: {"description": "Control vs treatment comparison per segment"}})
def get_ab_comparison(db: Session = Depends(get_db)):
    """Variant Comparison tab on the A/B Tests screen.

    Uses v_segment_ab_comparison (shows all tests that have rates, not just completed).
    """
    try:
        rows = db.execute(
            text("SELECT * FROM v_segment_ab_comparison")
        ).mappings().all()
        return [
            SegmentABComparison(
                segment_name=r["segment_name"],
                label=r["label"],
                color_hex=r["color_hex"],
                control_rate=float(r["control_rate"]) if r.get("control_rate") else None,
                treatment_rate=float(r["treatment_rate"]) if r.get("treatment_rate") else None,
                lift_pct=float(r["lift_pct"]) if r.get("lift_pct") else None,
                significance=r.get("significance"),
            )
            for r in rows
        ]
    except Exception:
        return []


# ── POST /api/ab-tests/run-analysis ─────────────────────────────────────────

@router.post("/run-analysis", response_model=RunAnalysisResult,
             responses={200: {"description": "Thompson Sampling run, results upserted"}})
def run_analysis(db: Session = Depends(get_db)):
    """Run Thompson Sampling on all active A/B tests and upsert results.

    Called by the frontend 'Recalculate' button.  Reads live conversion data
    from ab_assignments + conversion_outcomes, runs Beta-Binomial Thompson
    Sampling, and writes updated rates / significance back to ab_test_results.

    Fully idempotent — safe to call multiple times.
    """
    # 1. Get all ab_tests with their segment info
    tests = db.execute(text("""
        SELECT t.test_id, t.segment_id, s.name AS segment_name
        FROM ab_tests t
        JOIN segments s ON s.segment_id = t.segment_id
    """)).mappings().all()

    if not tests:
        return RunAnalysisResult(
            segments_analyzed=0,
            message="No A/B tests found. Run the DS pipeline first."
        )

    updated = 0
    for t in tests:
        test_id    = t["test_id"]
        seg_name   = t["segment_name"]

        # 2. Count conversions per group for this test
        counts = db.execute(text("""
            SELECT
                aa.group_type,
                COUNT(aa.user_id)                                           AS total,
                COUNT(co.conversion_id) FILTER (WHERE co.decision = 'upgraded') AS converted
            FROM ab_assignments aa
            LEFT JOIN conversion_outcomes co
                ON  co.user_id = aa.user_id
                AND co.test_id = aa.test_id
            WHERE aa.test_id = :tid
            GROUP BY aa.group_type
        """), {"tid": test_id}).mappings().all()

        groups = {r["group_type"]: r for r in counts}
        ctrl   = groups.get("control",   {"total": 0, "converted": 0})
        treat  = groups.get("treatment", {"total": 0, "converted": 0})

        ctrl_total   = int(ctrl["total"]   or 0)
        ctrl_conv    = int(ctrl["converted"]  or 0)
        treat_total  = int(treat["total"]  or 0)
        treat_conv   = int(treat["converted"] or 0)

        if ctrl_total == 0 and treat_total == 0:
            continue

        # 3. Run Thompson Sampling
        ts = _thompson_sampling(ctrl_conv, ctrl_total, treat_conv, treat_total)

        # 4. Upsert into ab_test_results
        existing = db.execute(
            text("SELECT result_id FROM ab_test_results WHERE test_id = :tid"),
            {"tid": test_id}
        ).mappings().first()

        now = datetime.now(timezone.utc)

        if existing:
            db.execute(text("""
                UPDATE ab_test_results SET
                    control_shown     = :cn,
                    treatment_shown   = :tn,
                    control_converted = :cc,
                    treatment_converted = :tc,
                    control_rate      = :cr,
                    treatment_rate    = :tr,
                    lift_pct          = :lp,
                    p_value           = :pv,
                    significance      = CAST(:sig AS significance_level),
                    winning_group     = CAST(:winner AS ab_group),
                    computed_at       = :now
                WHERE test_id = :tid
            """), {
                "cn": ctrl_total, "tn": treat_total,
                "cc": ctrl_conv,  "tc": treat_conv,
                "cr": ts["ctrl_rate"], "tr": ts["treat_rate"],
                "lp": ts["lift_pct"], "pv": ts["prob_wins"],
                "sig": ts["significance"], "winner": ts["winner"],
                "now": now, "tid": test_id,
            })
        else:
            db.execute(text("""
                INSERT INTO ab_test_results
                    (result_id, test_id,
                     control_shown, treatment_shown,
                     control_converted, treatment_converted,
                     control_rate, treatment_rate, lift_pct, p_value,
                     significance, winning_group, computed_at)
                VALUES
                    (:rid, :tid, :cn, :tn, :cc, :tc, :cr, :tr, :lp, :pv,
                     CAST(:sig AS significance_level),
                     CAST(:winner AS ab_group), :now)
            """), {
                "rid": str(uuid.uuid4()), "tid": test_id,
                "cn": ctrl_total, "tn": treat_total,
                "cc": ctrl_conv,  "tc": treat_conv,
                "cr": ts["ctrl_rate"], "tr": ts["treat_rate"],
                "lp": ts["lift_pct"], "pv": ts["prob_wins"],
                "sig": ts["significance"], "winner": ts["winner"],
                "now": now,
            })

        # 5. Update ab_tests status
        new_status = _significance_to_status(ts["significance"])
        db.execute(
            text("UPDATE ab_tests SET status = :s WHERE test_id = :tid"),
            {"s": new_status, "tid": test_id}
        )
        updated += 1

    db.commit()
    return RunAnalysisResult(
        segments_analyzed=updated,
        message=f"Thompson Sampling complete — {updated} segment(s) updated."
    )
