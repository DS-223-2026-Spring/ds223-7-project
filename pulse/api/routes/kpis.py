"""
KPIs screen endpoint.

GET /api/kpis?period=30 → platform KPIs filtered to the last N days
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schema import PlatformKPIs

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("", response_model=PlatformKPIs,
            responses={200: {"description": "Platform-wide KPI metrics"}})
def get_platform_kpis(
    period: int = Query(default=30, ge=1, description="Lookback window in days"),
    db: Session = Depends(get_db),
):
    """Top metric row on the KPIs screen filtered by reporting period.

    period=7 / 30 / 90 days (default 30).
    """
    try:
        row = db.execute(text("""
            WITH
              free_users AS (
                  SELECT COUNT(*) AS cnt FROM users WHERE plan = 'free'
              ),
              conversions AS (
                  SELECT
                      COUNT(*) FILTER (WHERE decision = 'upgraded')                              AS total_upgraded,
                      COUNT(*) FILTER (WHERE decision = 'upgraded' AND churned_within_30d = TRUE) AS churned,
                      AVG(revenue_amd) FILTER (WHERE decision = 'upgraded')                       AS avg_revenue
                  FROM conversion_outcomes
                  WHERE converted_at >= now() - make_interval(days => :days)
              ),
              notifications AS (
                  SELECT
                      COUNT(*) FILTER (WHERE event_type = 'shown')                AS shown,
                      COUNT(*) FILTER (WHERE event_type IN ('opened', 'clicked')) AS engaged
                  FROM notification_events
                  WHERE occurred_at >= now() - make_interval(days => :days)
              )
            SELECT
                ROUND(c.total_upgraded::NUMERIC / NULLIF(f.cnt, 0), 4)      AS overall_conversion_rate,
                ROUND(n.engaged::NUMERIC          / NULLIF(n.shown, 0), 4)  AS notification_engagement_rate,
                ROUND(c.churned::NUMERIC          / NULLIF(c.total_upgraded, 0), 4) AS churn_rate_30d,
                ROUND(c.avg_revenue, 2)                                      AS avg_revenue_amd
            FROM free_users f, conversions c, notifications n
        """), {"days": period}).mappings().first()

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
