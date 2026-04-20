"""
Schemas for the Campaign Editor screen.

Maps to tables: campaigns, message_templates, global_params
"""

from datetime import datetime
from pydantic import BaseModel


# ── Read schemas ────────────────────────────────────────────────────

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
    channel: str
    trigger_event: str
    status: str
    active_message: MessageTemplateOut | None = None
    created_at: datetime
    launched_at: datetime | None = None


class GlobalParamOut(BaseModel):
    """One row from global_params — e.g. pro_price_amd = 2900."""
    key: str
    value: str
    description: str | None = None


# ── Write schemas ───────────────────────────────────────────────────

class CampaignUpdate(BaseModel):
    """Update the channel and/or trigger of a campaign."""
    channel: str | None = None
    trigger_event: str | None = None


class MessageUpdate(BaseModel):
    """Update the active message body (PM editing the textarea)."""
    body: str


class GlobalParamUpdate(BaseModel):
    """Update a global param value."""
    value: str
