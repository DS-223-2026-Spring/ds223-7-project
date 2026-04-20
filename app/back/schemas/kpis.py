"""
Schemas for the KPIs screen.

Maps to view: v_platform_kpis
"""

from pydantic import BaseModel


class PlatformKPIs(BaseModel):
    """The top metric row on the KPIs screen — four numbers."""
    overall_conversion_rate: float | None = None
    notification_engagement_rate: float | None = None
    churn_rate_30d: float | None = None
    avg_revenue_amd: float | None = None
