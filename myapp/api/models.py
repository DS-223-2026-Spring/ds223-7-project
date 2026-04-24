"""
Pulse — SQLAlchemy ORM models for all 15 tables.

Based on: myapp/etl/init/01_schema.sql (and pulse_schema.sql from project files)

IMPORTANT:
- Trigger-maintained columns (total_sessions, total_exports, total_paywall_hits,
  total_thesaurus_uses, duration_seconds, days_since_last_login) must NEVER be
  updated by backend code — the DB triggers handle them.
- UUID primary keys use server_default=text("gen_random_uuid()") so the DB
  generates them, not Python.
"""

from sqlalchemy import (
    Column, String, Text, Integer, SmallInteger, Boolean, DateTime,
    Numeric, ForeignKey, UniqueConstraint, Index, text
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, INET

Base = declarative_base()


# =============================================================================
# 1. CORE TABLES
# =============================================================================

class User(Base):
    """Every writer registered on the Armat platform."""
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(Text, nullable=False, unique=True)
    display_name = Column(Text)
    plan = Column(String, nullable=False, server_default="free")          # free | pro | cancelled
    status = Column(String, nullable=False, server_default="active")      # active | inactive | banned
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    last_login_at = Column(DateTime(timezone=True))
    days_since_last_login = Column(Integer)                                # trigger-maintained
    # Denormalized counters — trigger-maintained, never update in code
    total_sessions = Column(Integer, nullable=False, server_default="0")
    total_exports = Column(Integer, nullable=False, server_default="0")
    total_paywall_hits = Column(Integer, nullable=False, server_default="0")
    total_thesaurus_uses = Column(Integer, nullable=False, server_default="0")

    # Relationships
    segments = relationship("UserSegment", back_populates="user")
    sessions = relationship("SessionEvent", back_populates="user")
    conversions = relationship("ConversionOutcome", back_populates="user")


class Segment(Base):
    """The four K-Means behavioral clusters. Seeded at deployment."""
    __tablename__ = "segments"

    segment_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False, unique=True)                    # power | growing | casual | dormant
    label = Column(Text, nullable=False)                                  # e.g. "Power users"
    color_hex = Column(String(7), nullable=False)                         # e.g. "#00b87a"
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    campaigns = relationship("Campaign", back_populates="segment")
    user_segments = relationship("UserSegment", back_populates="segment")


class UserSegment(Base):
    """Time-versioned segment assignments. Active row has expires_at IS NULL."""
    __tablename__ = "user_segments"

    assignment_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(UUID(as_uuid=False), ForeignKey("segments.segment_id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    expires_at = Column(DateTime(timezone=True))                          # NULL = currently active
    # K-Means feature snapshot
    feature_session_frequency = Column(Numeric(6, 2))
    feature_thesaurus_depth = Column(Numeric(6, 2))
    feature_paywall_hits_per_week = Column(Numeric(6, 2))
    feature_export_count = Column(Numeric(6, 2))
    kmeans_distance = Column(Numeric(10, 6))

    # Relationships
    user = relationship("User", back_populates="segments")
    segment = relationship("Segment", back_populates="user_segments")

    __table_args__ = (
        Index("idx_user_segments_user_active", "user_id", postgresql_where=text("expires_at IS NULL")),
    )


# =============================================================================
# 2. BEHAVIORAL EVENT TABLES
# =============================================================================

class SessionEvent(Base):
    """One row per writing session. duration_seconds filled by trigger."""
    __tablename__ = "session_events"

    session_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)                                     # trigger-maintained
    word_count = Column(Integer, nullable=False, server_default="0")
    line_count = Column(Integer, nullable=False, server_default="0")
    ip_address = Column(INET)
    user_agent = Column(Text)

    # Relationships
    user = relationship("User", back_populates="sessions")
    tool_usages = relationship("ToolUsageLog", back_populates="session")
    paywall_events = relationship("PaywallEvent", back_populates="session")


class ToolUsageLog(Base):
    """Every tool invocation inside the Armat editor."""
    __tablename__ = "tool_usage_logs"

    log_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    session_id = Column(UUID(as_uuid=False), ForeignKey("session_events.session_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    tool = Column(String, nullable=False)                                  # thesaurus | rhyme | meter | synonym | export
    query_count = Column(SmallInteger, nullable=False, server_default="1")
    synonym_depth = Column(SmallInteger, nullable=False, server_default="0")
    feature_blocked = Column(Boolean, nullable=False, server_default="false")
    used_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    session = relationship("SessionEvent", back_populates="tool_usages")


class PaywallEvent(Base):
    """Logged on every hard paywall hit. Strongest signal for upgrade readiness."""
    __tablename__ = "paywall_events"

    event_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=False), ForeignKey("session_events.session_id", ondelete="CASCADE"), nullable=False)
    tool = Column(String, nullable=False)
    feature_blocked = Column(Text, nullable=False)                         # e.g. "classical synonym layer"
    hit_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    session = relationship("SessionEvent", back_populates="paywall_events")


# =============================================================================
# 3. CAMPAIGN TABLES
# =============================================================================

class Campaign(Base):
    """One campaign per segment. active_message_id selects the live template."""
    __tablename__ = "campaigns"

    campaign_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    segment_id = Column(UUID(as_uuid=False), ForeignKey("segments.segment_id"), nullable=False, unique=True)
    channel = Column(String, nullable=False, server_default="in_app_popup")       # in_app_popup | push_notification | email
    trigger_event = Column(String, nullable=False, server_default="on_paywall_hit")  # on_paywall_hit | on_app_open | after_3rd_export
    status = Column(String, nullable=False, server_default="draft")                # draft | pending | running | paused | completed
    active_message_id = Column(UUID(as_uuid=False), ForeignKey("message_templates.message_id", use_alter=True, deferrable=True, initially="DEFERRED"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    launched_at = Column(DateTime(timezone=True))

    # Relationships
    segment = relationship("Segment", back_populates="campaigns")
    messages = relationship("MessageTemplate", back_populates="campaign", foreign_keys="MessageTemplate.campaign_id")
    ab_tests = relationship("ABTest", back_populates="campaign")


class MessageTemplate(Base):
    """All message versions per campaign. Exactly one may be is_active at a time."""
    __tablename__ = "message_templates"

    message_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False)
    source = Column(String, nullable=False, server_default="default")     # default | user_edited | ai_generated
    body = Column(Text, nullable=False)                                    # raw with {{placeholders}}
    body_rendered = Column(Text)                                           # cached preview
    is_active = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))  # trigger-maintained

    # Relationships
    campaign = relationship("Campaign", back_populates="messages", foreign_keys=[campaign_id])

    __table_args__ = (
        Index("idx_message_templates_one_active", "campaign_id", unique=True, postgresql_where=text("is_active = TRUE")),
    )


class GlobalParam(Base):
    """Shared campaign parameters: pro_price_amd, dormant_discount, template_count."""
    __tablename__ = "global_params"

    param_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    key = Column(Text, nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


# =============================================================================
# 4. AI GENERATION
# =============================================================================

class AIGenerationLog(Base):
    """Audit trail for every 'Write with AI' click."""
    __tablename__ = "ai_generation_log"

    gen_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False)
    message_id = Column(UUID(as_uuid=False), ForeignKey("message_templates.message_id", ondelete="CASCADE"), nullable=False)
    prompt_used = Column(Text, nullable=False)
    model_version = Column(Text, nullable=False, server_default="claude-sonnet-4-20250514")
    raw_response = Column(Text)
    duration_ms = Column(Integer)
    token_input = Column(Integer)
    token_output = Column(Integer)
    triggered_by = Column(UUID(as_uuid=False), ForeignKey("users.user_id"))
    generated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


# =============================================================================
# 5. A/B TEST TABLES
# =============================================================================

class ABTest(Base):
    """14-day controlled experiment. Control vs treatment message per run."""
    __tablename__ = "ab_tests"

    test_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(UUID(as_uuid=False), ForeignKey("segments.segment_id"), nullable=False)
    status = Column(String, nullable=False, server_default="pending")     # pending | running | paused | completed | cancelled
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    duration_days = Column(SmallInteger, nullable=False, server_default="14")
    control_message_id = Column(UUID(as_uuid=False), ForeignKey("message_templates.message_id"))
    treatment_message_id = Column(UUID(as_uuid=False), ForeignKey("message_templates.message_id"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    campaign = relationship("Campaign", back_populates="ab_tests")
    assignments = relationship("ABAssignment", back_populates="test")
    result = relationship("ABTestResult", back_populates="test", uselist=False)


class ABAssignment(Base):
    """50/50 split. UNIQUE(test_id, user_id) prevents double-assignment."""
    __tablename__ = "ab_assignments"

    assignment_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    test_id = Column(UUID(as_uuid=False), ForeignKey("ab_tests.test_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    group_type = Column(String, nullable=False)                            # control | treatment
    message_id = Column(UUID(as_uuid=False), ForeignKey("message_templates.message_id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    test = relationship("ABTest", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("test_id", "user_id", name="uq_ab_assignments_test_user"),
    )


class ABTestResult(Base):
    """Chi-square + logistic regression outputs. One row per completed test."""
    __tablename__ = "ab_test_results"

    result_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    test_id = Column(UUID(as_uuid=False), ForeignKey("ab_tests.test_id", ondelete="CASCADE"), nullable=False, unique=True)
    # Raw counts
    control_shown = Column(Integer, nullable=False, server_default="0")
    control_converted = Column(Integer, nullable=False, server_default="0")
    treatment_shown = Column(Integer, nullable=False, server_default="0")
    treatment_converted = Column(Integer, nullable=False, server_default="0")
    # Derived rates
    control_rate = Column(Numeric(6, 4))
    treatment_rate = Column(Numeric(6, 4))
    lift_pct = Column(Numeric(8, 2))
    # Chi-Square outputs
    chi_square_stat = Column(Numeric(10, 4))
    p_value = Column(Numeric(8, 6))
    significance = Column(String)                                          # significant | borderline | not_significant
    winning_group = Column(String)                                         # control | treatment | NULL
    # Logistic Regression outputs (nice-to-have)
    top_predictor_feature = Column(Text)
    top_predictor_coef = Column(Numeric(10, 6))
    computed_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    test = relationship("ABTest", back_populates="result")


# =============================================================================
# 6. NOTIFICATION & CONVERSION TABLES
# =============================================================================

class NotificationEvent(Base):
    """Full funnel: shown → opened → clicked/dismissed."""
    __tablename__ = "notification_events"

    notification_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("campaigns.campaign_id"), nullable=False)
    message_id = Column(UUID(as_uuid=False), ForeignKey("message_templates.message_id"), nullable=False)
    test_id = Column(UUID(as_uuid=False), ForeignKey("ab_tests.test_id"))
    ab_group = Column(String)                                              # control | treatment
    event_type = Column(String, nullable=False)                            # shown | opened | dismissed | clicked
    channel = Column(String, nullable=False)                               # in_app_popup | push_notification | email
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ConversionOutcome(Base):
    """Every upgrade/skip decision. Primary outcome table for A/B measurement."""
    __tablename__ = "conversion_outcomes"

    conversion_id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    test_id = Column(UUID(as_uuid=False), ForeignKey("ab_tests.test_id"))
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("campaigns.campaign_id"))
    message_id = Column(UUID(as_uuid=False), ForeignKey("message_templates.message_id"))
    group_type = Column(String)                                            # control | treatment
    decision = Column(String, nullable=False)                              # upgraded | try_later | dismissed
    plan_subscribed = Column(String)                                       # NULL when not upgraded
    churned_within_30d = Column(Boolean)
    revenue_amd = Column(Numeric(10, 2))
    converted_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    user = relationship("User", back_populates="conversions")
