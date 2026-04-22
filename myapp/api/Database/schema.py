from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SegmentBase(BaseModel):
    segment_id: str
    name: str
    label: str
    color_hex: str

class CampaignBase(BaseModel):
    campaign_id: str
    segment_id: str
    channel: Optional[str] = None
    trigger_event: Optional[str] = None
    status: str = "draft"

class ABTestBase(BaseModel):
    test_id: str
    campaign_id: str
    variant: str
    conversions: int = 0
    impressions: int = 0

    class Config:
        from_attributes = True
