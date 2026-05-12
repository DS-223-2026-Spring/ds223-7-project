"""
Segments screen endpoints.

GET /api/segments/counts             → v_segment_counts
GET /api/segments/behavioral-averages → v_segment_behavioral_averages
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schema import SegmentCount, SegmentBehavioralAvg, SegmentUserOut

router = APIRouter(prefix="/api/segments", tags=["segments"])

SEGMENT_COLORS = {
    "power":   "#00b87a",
    "growing": "#3b82f6",
    "casual":  "#f59e0b",
    "dormant": "#9ca3af",
}


@router.get("/counts", response_model=list[SegmentCount],
            responses={200: {"description": "List of segments with user counts"}})
def get_segment_counts(db: Session = Depends(get_db)):
    """Four KPI cards on the Segments screen.

    Returns one object per segment with user_count.
    Uses v_segment_counts — never queries base tables directly.
    """
    try:
        rows = db.execute(text("SELECT * FROM v_segment_counts")).mappings().all()
        return [SegmentCount(**row) for row in rows]
    except Exception:
        return []


@router.get("/behavioral-averages", response_model=list[SegmentBehavioralAvg],
            responses={200: {"description": "Average behavioral metrics per segment"}})
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
                label=r["segment_name"],
                color_hex=SEGMENT_COLORS.get(r["segment_name"], "#9ca3af"),
                avg_sessions_per_week=r.get("avg_sessions_per_week"),
                avg_paywall_hits=r.get("avg_paywall_hits"),
                avg_synonym_depth=r.get("avg_synonym_depth"),
                avg_exports=r.get("avg_exports_per_week"),
            )
            for r in rows
        ]
    except Exception:
        return []

@router.get("/{name}/users", response_model=list[SegmentUserOut],
            responses={200: {"description": "Up to 50 users in the given segment"}})
def get_segment_users(name: str, db: Session = Depends(get_db)):
    """Drill-down: up to 50 users in the given segment.

    Path parameter `name` must match a segment name exactly
    (Power, Growing, Casual, Dormant).
    Queries base tables (users, user_segments, segments) per PM spec.
    """
    try:
        rows = db.execute(
            text("""
                SELECT
                    u.user_id::text,
                    u.email,
                    COALESCE(us.feature_session_frequency, 0)    AS sessions_per_week,
                    COALESCE(u.total_exports, 0)                  AS total_exports,
                    COALESCE(u.total_paywall_hits, 0)             AS paywall_hits,
                    COALESCE(u.days_since_last_login, 999)        AS days_since_last_session,
                    NULL                                           AS predicted_conversion_prob
                FROM users u
                JOIN user_segments us ON us.user_id = u.user_id AND us.expires_at IS NULL
                JOIN segments s       ON s.segment_id = us.segment_id
                WHERE s.name = :seg_name
                ORDER BY us.feature_session_frequency DESC NULLS LAST
                LIMIT 50
            """),
            {"seg_name": name},
        ).mappings().all()
        return [SegmentUserOut(**r) for r in rows]
    except Exception:
        return []