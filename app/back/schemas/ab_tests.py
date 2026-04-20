"""
Schemas for the A/B Tests screen.

Maps to views: v_ab_test_summary, v_segment_ab_comparison
"""

from datetime import datetime
from pydantic import BaseModel


class ABTestSummary(BaseModel):
    """One card on the A/B Tests screen — live counts + final results."""
    segment_name: str
    segment_label: str
    color_hex: str
    test_id: str
    status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_days: int
    total_assigned: int
    control_n: int
    treatment_n: int
    control_converted: int
    treatment_converted: int
    control_rate: float | None = None
    treatment_rate: float | None = None
    lift_pct: float | None = None
    p_value: float | None = None
    significance: str | None = None
    winning_group: str | None = None


class SegmentABComparison(BaseModel):
    """One row of the comparison table at the bottom of the A/B Tests
    screen — Control % / Treatment % / Lift / Significance."""
    segment_name: str
    label: str
    color_hex: str
    control_rate: float | None = None
    treatment_rate: float | None = None
    lift_pct: float | None = None
    significance: str | None = None
