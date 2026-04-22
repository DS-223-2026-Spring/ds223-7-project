"""
Schemas for the User Demo screen.

The Demo screen simulates what a real user would see: a rendered
upgrade message for their segment, and buttons to respond
(Upgrade / Try Later).
"""

from pydantic import BaseModel


class DemoMessageOut(BaseModel):
    """The rendered upgrade message shown inside the phone mockup."""
    segment_name: str
    segment_label: str
    color_hex: str
    rendered_body: str
    channel: str
    trigger_event: str


class DemoResponse(BaseModel):
    """Payload sent when the user clicks 'Upgrade' or 'Try Later'."""
    segment_name: str
    decision: str          # 'upgraded' | 'try_later'
    ab_group: str          # 'control' | 'treatment'
