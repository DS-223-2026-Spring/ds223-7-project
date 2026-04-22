"""
Segments screen endpoints.

GET /api/segments/counts             → v_segment_counts
GET /api/segments/behavioral-averages → v_segment_behavioral_averages
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from Database import get_db
from schemas.segments import SegmentCount, SegmentBehavioralAvg

router = APIRouter(prefix="/api/segments", tags=["segments"])


@router.get("/counts", response_model=list[SegmentCount])
def get_segment_counts(db: Session = Depends(get_db)):
    """Four KPI cards on the Segments screen.

    Returns one object per segment with user_count.
    Uses v_segment_counts — never queries base tables directly.
    """
    try:
        rows = db.execute(text("SELECT * FROM v_segment_counts")).mappings().all()
        return [SegmentCount(**row) for row in rows]
    except Exception:
        # Graceful empty response — no crashes (per master prompt)
        return []


@router.get("/behavioral-averages", response_model=list[SegmentBehavioralAvg])
def get_behavioral_averages(db: Session = Depends(get_db)):
    """Bar-chart data on the Segments screen.

    Returns avg exports/week, paywall hits, synonym depth per segment.
    Uses v_segment_behavioral_averages.
    """
    try:
        rows = db.execute(
            text("SELECT * FROM v_segment_behavioral_averages")
        ).mappings().all()
        return [
            SegmentBehavioralAvg(
                segment_name=r["segment_name"],
                label=r["segment_name"],          # view lacks label column
                color_hex="",                      # view lacks color column
                avg_sessions_per_week=r.get("avg_sessions_per_week"),
                avg_paywall_hits=r.get("avg_paywall_hits"),
                avg_synonym_depth=r.get("avg_synonym_depth"),
                avg_exports=r.get("avg_exports_per_week"),
            )
            for r in rows
        ]
    except Exception:
        return []
