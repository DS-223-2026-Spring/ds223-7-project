from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Segment(Base):
    __tablename__ = "segments"
    segment_id = Column(String, primary_key=True)
    name = Column(String)
    label = Column(String)
    color_hex = Column(String)

class Campaign(Base):
    __tablename__ = "campaigns"
    campaign_id = Column(String, primary_key=True)
    segment_id = Column(String, ForeignKey("segments.segment_id"))
    channel = Column(String)
    trigger_event = Column(String)
    status = Column(String, default="draft")
    active_message_id = Column(String)
    created_at = Column(DateTime)
    launched_at = Column(DateTime, nullable=True)

class ABTest(Base):
    __tablename__ = "ab_tests"
    test_id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.campaign_id"))
    variant = Column(String)
    conversions = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
