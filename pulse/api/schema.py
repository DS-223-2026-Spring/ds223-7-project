"""
Pulse API — Pydantic schemas (all screens).

Single file as required by project structure spec.
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel


# ═════════════════════════════════════════════════════════════════════
# SEGMENTS SCREEN
# ═════════════════════════════════════════════════════════════════════

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

class SegmentUserOut(BaseModel):
    """One user row in the segment drill-down table."""
    user_id: str
    email: str
    sessions_per_week: float
    total_exports: int
    paywall_hits: int
    days_since_last_session: int
    predicted_conversion_prob: float | None = None

# ═════════════════════════════════════════════════════════════════════
# A/B TESTS SCREEN
# ═════════════════════════════════════════════════════════════════════

class ABTestSummary(BaseModel):
    """One card on the A/B Tests screen — live counts + final results."""
    segment_name: str
    segment_label: str
    color_hex: str
    test_id: str
    status: Literal['pending', 'running', 'paused', 'completed', 'cancelled']
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
    significance: Literal['significant', 'borderline', 'not_significant'] | None = None
    winning_group: str | None = None


class SegmentABComparison(BaseModel):
    """One row of the comparison table — Control % / Treatment % / Lift."""
    segment_name: str
    label: str
    color_hex: str
    control_rate: float | None = None
    treatment_rate: float | None = None
    lift_pct: float | None = None
    significance: Literal['significant', 'borderline', 'not_significant'] | None = None


# ═════════════════════════════════════════════════════════════════════
# KPIs SCREEN
# ═════════════════════════════════════════════════════════════════════

class PlatformKPIs(BaseModel):
    """The top metric row on the KPIs screen — four numbers."""
    overall_conversion_rate: float | None = None
    notification_engagement_rate: float | None = None
    churn_rate_30d: float | None = None
    avg_revenue_amd: float | None = None


# ═════════════════════════════════════════════════════════════════════
# CAMPAIGN EDITOR SCREEN
# ═════════════════════════════════════════════════════════════════════

class MessageTemplateOut(BaseModel):
    """One message version inside a campaign card."""
    message_id: str
    source: str
    body: str
    body_rendered: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CampaignOut(BaseModel):
    """Full campaign card — one per segment, with its active message."""
    campaign_id: str
    segment_name: str
    segment_label: str
    color_hex: str
    channel: Literal['in_app_popup', 'push_notification', 'email']
    trigger_event: Literal['on_paywall_hit', 'on_app_open', 'after_3rd_export']
    status: Literal['draft', 'pending', 'running', 'paused', 'completed']
    active_message: MessageTemplateOut | None = None
    created_at: datetime
    launched_at: datetime | None = None


class GlobalParamOut(BaseModel):
    """One row from global_params — e.g. pro_price_amd = 2900."""
    key: str
    value: str
    description: str | None = None


class CampaignUpdate(BaseModel):
    """Update the channel and/or trigger of a campaign."""
    channel: Literal['in_app_popup', 'push_notification', 'email'] | None = None
    trigger_event: Literal['on_paywall_hit', 'on_app_open', 'after_3rd_export'] | None = None


class MessageUpdate(BaseModel):
    """Update the active message body."""
    body: str


class GlobalParamUpdate(BaseModel):
    """Update a global param value."""
    value: str


# ═════════════════════════════════════════════════════════════════════
# USER DEMO SCREEN
# ═════════════════════════════════════════════════════════════════════

class DemoMessageOut(BaseModel):
    """Messages for both A/B groups + campaign status."""
    segment_name: str
    segment_label: str
    color_hex: str
    campaign_status: str
    channel: str
    trigger_event: str
    control_body: str
    treatment_body: str
    user_id: str
    test_id: str


class DemoResponse(BaseModel):
    """Payload sent when the user clicks 'Upgrade' or 'Try Later'."""
    segment_name: str
    decision: Literal['upgraded', 'try_later', 'dismissed']
    ab_group: Literal['control', 'treatment']
    user_id: str
    test_id: str

    
class DemoRespondResult(BaseModel):
    """Response after recording an upgrade / try-later decision."""
    status: Literal['recorded']
    decision: Literal['upgraded', 'try_later', 'dismissed']
    ab_group: Literal['control', 'treatment']
    segment: str


class RunAnalysisResult(BaseModel):
    """Response from POST /api/ab-tests/run-analysis."""
    segments_analyzed: int
    message: str
