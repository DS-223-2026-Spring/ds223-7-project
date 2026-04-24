"""
Schemas for the Segments screen.

Maps to views: v_segment_counts, v_segment_behavioral_averages
"""

from pydantic import BaseModel


class SegmentCount(BaseModel):
    """One card on the Segments screen — e.g. 'Power users: 1,240'."""
    segment_name: str
    label: str
    color_hex: str
    user_count: int


class SegmentBehavioralAvg(BaseModel):
    """One row of the bar-chart data on the Segments screen."""
    segment_name: str
    label: str
    color_hex: str
    avg_sessions_per_week: float | None = None
    avg_paywall_hits: float | None = None
    avg_synonym_depth: float | None = None
    avg_exports: float | None = None
