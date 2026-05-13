-- =============================================================================
-- MIGRATION: Milestone 4 additions
-- Safe to run on existing databases (uses CREATE OR REPLACE / IF NOT EXISTS)
-- Run this manually on existing databases:
--   docker exec db psql -U pulse_user -d pulse -f /docker-entrypoint-initdb.d/02_migrations.sql
-- =============================================================================

-- Add control_message_id to campaigns if not already present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'campaigns'
        AND column_name = 'control_message_id'
    ) THEN
        ALTER TABLE campaigns ADD COLUMN control_message_id UUID;
    END IF;
END $$;

-- New table: user conversion scores (written by DS prediction pipeline)
CREATE TABLE IF NOT EXISTS user_conversion_scores (
    score_id        UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID         NOT NULL REFERENCES users(user_id),
    segment_name    segment_name NOT NULL,
    conversion_prob NUMERIC(6,4) NOT NULL CHECK (conversion_prob BETWEEN 0 AND 1),
    confidence_tier TEXT         NOT NULL CHECK (confidence_tier IN ('high','medium','low')),
    rank            INT,
    computed_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_conversion_scores_segment
    ON user_conversion_scores(segment_name);

CREATE INDEX IF NOT EXISTS idx_user_conversion_scores_user
    ON user_conversion_scores(user_id);

-- View: enriched user behavioral features for DS pipeline
CREATE OR REPLACE VIEW v_user_behavioral_features_m4 AS
SELECT
    u.user_id,
    u.email,
    u.plan,
    u.total_sessions,
    u.total_exports,
    u.total_paywall_hits,
    u.total_thesaurus_uses,
    u.days_since_last_login,
    s.name AS segment_name,
    COALESCE(abt.status::text, 'not_assigned') AS test_status,
    COALESCE(aa.group_type::text, 'unassigned') AS ab_group
FROM users u
LEFT JOIN user_segments us ON us.user_id = u.user_id AND us.expires_at IS NULL
LEFT JOIN segments s ON s.segment_id = us.segment_id
LEFT JOIN ab_assignments aa ON aa.user_id = u.user_id
LEFT JOIN ab_tests abt ON abt.test_id = aa.test_id;

-- View: conversion funnel for analytics dashboard
CREATE OR REPLACE VIEW v_conversion_funnel AS
SELECT
    s.name                                          AS segment_name,
    s.label,
    s.color_hex,
    COUNT(DISTINCT u.user_id)                       AS total_users,
    COUNT(DISTINCT ne.user_id)
        FILTER (WHERE ne.event_type = 'shown')      AS notified,
    COUNT(DISTINCT ne.user_id)
        FILTER (WHERE ne.event_type IN ('opened','clicked')) AS engaged,
    COUNT(DISTINCT co.user_id)
        FILTER (WHERE co.decision = 'upgraded')     AS converted,
    ROUND(
        COUNT(DISTINCT co.user_id) FILTER (WHERE co.decision = 'upgraded')::numeric
        / NULLIF(COUNT(DISTINCT u.user_id), 0), 4
    )                                               AS conversion_rate
FROM segments s
LEFT JOIN user_segments us ON us.segment_id = s.segment_id AND us.expires_at IS NULL
LEFT JOIN users u ON u.user_id = us.user_id
LEFT JOIN notification_events ne ON ne.user_id = u.user_id
LEFT JOIN conversion_outcomes co ON co.user_id = u.user_id
GROUP BY s.segment_id, s.name, s.label, s.color_hex
ORDER BY conversion_rate DESC NULLS LAST;