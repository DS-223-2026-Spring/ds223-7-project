"""
KPIs screen endpoint.

GET /api/kpis → v_platform_kpis
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schema import PlatformKPIs

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("", response_model=PlatformKPIs)
def get_platform_kpis(db: Session = Depends(get_db)):
    """Top metric row on the KPIs screen — four numbers.

    overall_conversion_rate, notification_engagement_rate,
    churn_rate_30d, avg_revenue_amd.

    Uses v_platform_kpis.  Returns zeros when no data exists yet.
    """
    try:
        row = db.execute(text("SELECT * FROM v_platform_kpis")).mappings().first()
        if row is None:
            return PlatformKPIs()
        return PlatformKPIs(
            overall_conversion_rate=float(row["overall_conversion_rate"])
                if row.get("overall_conversion_rate") else None,
            notification_engagement_rate=float(row["notification_engagement_rate"])
                if row.get("notification_engagement_rate") else None,
            churn_rate_30d=float(row["churn_rate_30d"])
                if row.get("churn_rate_30d") else None,
            avg_revenue_amd=float(row["avg_revenue_amd"])
                if row.get("avg_revenue_amd") else None,
        )
    except Exception:
        return PlatformKPIs()
