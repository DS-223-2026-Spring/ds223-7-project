"""
A/B Tests screen endpoints.

GET /api/ab-tests/summary    → v_ab_test_summary
GET /api/ab-tests/comparison → v_segment_ab_comparison
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schema import ABTestSummary, SegmentABComparison

router = APIRouter(prefix="/api/ab-tests", tags=["ab-tests"])


@router.get("/summary", response_model=list[ABTestSummary])
def get_ab_test_summary(db: Session = Depends(get_db)):
    """Cards on the A/B Tests screen — one per segment test.

    Shows live counts (control_n, treatment_n, converted) plus final
    chi-square results once a test completes.
    Uses v_ab_test_summary.
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


@router.get("/comparison", response_model=list[SegmentABComparison])
def get_ab_comparison(db: Session = Depends(get_db)):
    """Bottom table on the A/B Tests screen.

    Control % / Treatment % / Lift / Significance per completed segment.
    Uses v_segment_ab_comparison.
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
