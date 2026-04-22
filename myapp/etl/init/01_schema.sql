-- =============================================================================
-- PULSE — Free-to-Paid Conversion Platform
-- PostgreSQL Schema  |  Full Implementation  |  v2 (validated)
-- Based on: Problem Definition (Milestone 1) + Should_Have Prototype
-- =============================================================================
-- Run order: extensions → enums → tables → indexes → constraints → triggers
--            → views → seed data
-- Compatible with: PostgreSQL 14+
-- =============================================================================


-- =============================================================================
-- 0. EXTENSIONS
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- fuzzy search on message bodies


-- =============================================================================
-- 1. ENUMS
-- All domain values that appear as dropdowns or fixed states in the prototype
-- =============================================================================

-- User plan status
CREATE TYPE plan_type AS ENUM ('free', 'pro', 'cancelled');

-- User account status
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'banned');

-- The four behavioral segments discovered by K-Means clustering
CREATE TYPE segment_name AS ENUM ('power', 'growing', 'casual', 'dormant');

-- A/B test lifecycle  (matches badge classes: pending · running · paused)
CREATE TYPE test_status AS ENUM ('pending', 'running', 'paused', 'completed', 'cancelled');

-- Which group a user is randomly assigned to in a test
CREATE TYPE ab_group AS ENUM ('control', 'treatment');

-- Statistical significance verdict (matches badge classes in A/B Tests screen)
CREATE TYPE significance_level AS ENUM ('significant', 'borderline', 'not_significant');

-- Delivery channel (dropdowns in Campaign Editor)
CREATE TYPE message_channel AS ENUM ('in_app_popup', 'push_notification', 'email');

-- What event fires the message (dropdowns in Campaign Editor)
CREATE TYPE message_trigger AS ENUM ('on_paywall_hit', 'on_app_open', 'after_3rd_export');

-- Who authored a message template
CREATE TYPE message_source AS ENUM ('default', 'user_edited', 'ai_generated');

-- Campaign lifecycle
CREATE TYPE campaign_status AS ENUM ('draft', 'pending', 'running', 'paused', 'completed');

-- Notification engagement event
CREATE TYPE notification_event_type AS ENUM ('shown', 'opened', 'dismissed', 'clicked');

-- Platform tools inside the Armenian writing app (Armat)
CREATE TYPE tool_name AS ENUM ('thesaurus', 'rhyme', 'meter', 'synonym', 'export');

-- User decision when shown an upgrade card (User Demo screen)
CREATE TYPE upgrade_decision AS ENUM ('upgraded', 'try_later', 'dismissed');


-- =============================================================================
-- 2. CORE TABLES
-- =============================================================================

CREATE TABLE users (
    user_id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    email                 TEXT         NOT NULL UNIQUE,
    display_name          TEXT,
    plan                  plan_type    NOT NULL DEFAULT 'free',
    status                user_status  NOT NULL DEFAULT 'active',
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT now(),
    last_login_at         TIMESTAMPTZ,
    days_since_last_login INT,
    total_sessions        INT          NOT NULL DEFAULT 0,
    total_exports         INT          NOT NULL DEFAULT 0,
    total_paywall_hits    INT          NOT NULL DEFAULT 0,
    total_thesaurus_uses  INT          NOT NULL DEFAULT 0
);

CREATE TABLE segments (
    segment_id   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name         segment_name NOT NULL UNIQUE,
    label        TEXT         NOT NULL,
    color_hex    CHAR(7)      NOT NULL,
    description  TEXT,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE user_segments (
    assignment_id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                        UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    segment_id                     UUID        NOT NULL REFERENCES segments(segment_id),
    assigned_at                    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at                     TIMESTAMPTZ,
    feature_session_frequency      NUMERIC(6,2),
    feature_thesaurus_depth        NUMERIC(6,2),
    feature_paywall_hits_per_week  NUMERIC(6,2),
    feature_export_count           NUMERIC(6,2),
    kmeans_distance                NUMERIC(10,6)
);

CREATE INDEX idx_user_segments_user_active
    ON user_segments(user_id) WHERE expires_at IS NULL;


-- =============================================================================
-- 3. BEHAVIORAL EVENT TABLES
-- =============================================================================

CREATE TABLE session_events (
    session_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    started_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at          TIMESTAMPTZ,
    duration_seconds  INT,
    word_count        INT         NOT NULL DEFAULT 0,
    line_count        INT         NOT NULL DEFAULT 0,
    ip_address        INET,
    user_agent        TEXT
);

CREATE INDEX idx_session_events_user_id    ON session_events(user_id);
CREATE INDEX idx_session_events_started_at ON session_events(started_at);

CREATE TABLE tool_usage_logs (
    log_id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID        NOT NULL REFERENCES session_events(session_id) ON DELETE CASCADE,
    user_id          UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    tool             tool_name   NOT NULL,
    query_count      SMALLINT    NOT NULL DEFAULT 1,
    synonym_depth    SMALLINT    NOT NULL DEFAULT 0,
    feature_blocked  BOOLEAN     NOT NULL DEFAULT FALSE,
    used_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tool_usage_user_id    ON tool_usage_logs(user_id);
CREATE INDEX idx_tool_usage_session_id ON tool_usage_logs(session_id);
CREATE INDEX idx_tool_usage_tool       ON tool_usage_logs(tool);

CREATE TABLE paywall_events (
    event_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_id      UUID        NOT NULL REFERENCES session_events(session_id) ON DELETE CASCADE,
    tool            tool_name   NOT NULL,
    feature_blocked TEXT        NOT NULL,
    hit_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_paywall_user_id    ON paywall_events(user_id);
CREATE INDEX idx_paywall_session_id ON paywall_events(session_id);
CREATE INDEX idx_paywall_hit_at     ON paywall_events(hit_at);


-- =============================================================================
-- 4. CAMPAIGN TABLES
-- =============================================================================

CREATE TABLE campaigns (
    campaign_id        UUID             PRIMARY KEY DEFAULT gen_random_uuid(),
    segment_id         UUID             NOT NULL REFERENCES segments(segment_id),
    channel            message_channel  NOT NULL DEFAULT 'in_app_popup',
    trigger_event      message_trigger  NOT NULL DEFAULT 'on_paywall_hit',
    status             campaign_status  NOT NULL DEFAULT 'draft',
    active_message_id  UUID,
    created_at         TIMESTAMPTZ      NOT NULL DEFAULT now(),
    launched_at        TIMESTAMPTZ,
    UNIQUE (segment_id)
);

CREATE TABLE message_templates (
    message_id     UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id    UUID           NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    source         message_source NOT NULL DEFAULT 'default',
    body           TEXT           NOT NULL,
    body_rendered  TEXT,
    is_active      BOOLEAN        NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ    NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_message_templates_one_active
    ON message_templates(campaign_id) WHERE is_active = TRUE;

CREATE INDEX idx_message_templates_campaign ON message_templates(campaign_id);

ALTER TABLE campaigns
    ADD CONSTRAINT fk_campaigns_active_message
    FOREIGN KEY (active_message_id) REFERENCES message_templates(message_id)
    DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE global_params (
    param_id    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    key         TEXT        NOT NULL UNIQUE,
    value       TEXT        NOT NULL,
    description TEXT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- =============================================================================
-- 5. AI GENERATION
-- =============================================================================

CREATE TABLE ai_generation_log (
    gen_id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id    UUID        NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    message_id     UUID        NOT NULL REFERENCES message_templates(message_id) ON DELETE CASCADE,
    prompt_used    TEXT        NOT NULL,
    model_version  TEXT        NOT NULL DEFAULT 'claude-sonnet-4-20250514',
    raw_response   TEXT,
    duration_ms    INT,
    token_input    INT,
    token_output   INT,
    triggered_by   UUID        REFERENCES users(user_id),
    generated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ai_gen_campaign ON ai_generation_log(campaign_id);
CREATE INDEX idx_ai_gen_message  ON ai_generation_log(message_id);


-- =============================================================================
-- 6. A/B TEST TABLES
-- =============================================================================

CREATE TABLE ab_tests (
    test_id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id           UUID        NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    segment_id            UUID        NOT NULL REFERENCES segments(segment_id),
    status                test_status NOT NULL DEFAULT 'pending',
    started_at            TIMESTAMPTZ,
    ended_at              TIMESTAMPTZ,
    duration_days         SMALLINT    NOT NULL DEFAULT 14,
    control_message_id    UUID        REFERENCES message_templates(message_id),
    treatment_message_id  UUID        REFERENCES message_templates(message_id),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ab_tests_campaign ON ab_tests(campaign_id);
CREATE INDEX idx_ab_tests_segment  ON ab_tests(segment_id);
CREATE INDEX idx_ab_tests_status   ON ab_tests(status);

CREATE TABLE ab_assignments (
    assignment_id  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id        UUID        NOT NULL REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    user_id        UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    group_type     ab_group    NOT NULL,
    message_id     UUID        NOT NULL REFERENCES message_templates(message_id),
    assigned_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (test_id, user_id)
);

CREATE INDEX idx_ab_assignments_test  ON ab_assignments(test_id);
CREATE INDEX idx_ab_assignments_user  ON ab_assignments(user_id);
CREATE INDEX idx_ab_assignments_group ON ab_assignments(test_id, group_type);

CREATE TABLE ab_test_results (
    result_id              UUID               PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id                UUID               NOT NULL UNIQUE REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    control_shown          INT                NOT NULL DEFAULT 0,
    control_converted      INT                NOT NULL DEFAULT 0,
    treatment_shown        INT                NOT NULL DEFAULT 0,
    treatment_converted    INT                NOT NULL DEFAULT 0,
    control_rate           NUMERIC(6,4),
    treatment_rate         NUMERIC(6,4),
    lift_pct               NUMERIC(8,2),
    chi_square_stat        NUMERIC(10,4),
    p_value                NUMERIC(8,6),
    significance           significance_level,
    winning_group          ab_group,
    top_predictor_feature  TEXT,
    top_predictor_coef     NUMERIC(10,6),
    computed_at            TIMESTAMPTZ        NOT NULL DEFAULT now()
);


-- =============================================================================
-- 7. NOTIFICATION & CONVERSION TABLES
-- =============================================================================

CREATE TABLE notification_events (
    notification_id  UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID                    NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    campaign_id      UUID                    NOT NULL REFERENCES campaigns(campaign_id),
    message_id       UUID                    NOT NULL REFERENCES message_templates(message_id),
    test_id          UUID                    REFERENCES ab_tests(test_id),
    ab_group         ab_group,
    event_type       notification_event_type NOT NULL,
    channel          message_channel         NOT NULL,
    occurred_at      TIMESTAMPTZ             NOT NULL DEFAULT now()
);

CREATE INDEX idx_notif_user        ON notification_events(user_id);
CREATE INDEX idx_notif_campaign    ON notification_events(campaign_id);
CREATE INDEX idx_notif_test        ON notification_events(test_id);
CREATE INDEX idx_notif_occurred_at ON notification_events(occurred_at);

CREATE TABLE conversion_outcomes (
    conversion_id       UUID             PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    test_id             UUID             REFERENCES ab_tests(test_id),
    campaign_id         UUID             REFERENCES campaigns(campaign_id),
    message_id          UUID             REFERENCES message_templates(message_id),
    group_type          ab_group,
    decision            upgrade_decision NOT NULL,
    plan_subscribed     plan_type,
    churned_within_30d  BOOLEAN,
    revenue_amd         NUMERIC(10,2),
    converted_at        TIMESTAMPTZ      NOT NULL DEFAULT now()
);

CREATE INDEX idx_conversion_user     ON conversion_outcomes(user_id);
CREATE INDEX idx_conversion_test     ON conversion_outcomes(test_id);
CREATE INDEX idx_conversion_campaign ON conversion_outcomes(campaign_id);
CREATE INDEX idx_conversion_decision ON conversion_outcomes(decision);


-- =============================================================================
-- 8. TRIGGERS
-- =============================================================================

CREATE OR REPLACE FUNCTION trg_fn_session_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE users
    SET
        total_sessions        = total_sessions + 1,
        last_login_at         = NEW.started_at,
        days_since_last_login = 0
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_session_insert
    AFTER INSERT ON session_events
    FOR EACH ROW EXECUTE FUNCTION trg_fn_session_insert();

CREATE OR REPLACE FUNCTION trg_fn_session_close()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND OLD.ended_at IS NULL THEN
        NEW.duration_seconds :=
            EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at))::INT;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_session_close
    BEFORE UPDATE ON session_events
    FOR EACH ROW EXECUTE FUNCTION trg_fn_session_close();

CREATE OR REPLACE FUNCTION trg_fn_paywall_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE users
    SET total_paywall_hits = total_paywall_hits + 1
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_paywall_insert
    AFTER INSERT ON paywall_events
    FOR EACH ROW EXECUTE FUNCTION trg_fn_paywall_insert();

CREATE OR REPLACE FUNCTION trg_fn_tool_usage_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.tool = 'export' THEN
        UPDATE users SET total_exports = total_exports + NEW.query_count
        WHERE user_id = NEW.user_id;
    END IF;
    IF NEW.tool IN ('thesaurus', 'synonym') THEN
        UPDATE users SET total_thesaurus_uses = total_thesaurus_uses + NEW.query_count
        WHERE user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_tool_usage_insert
    AFTER INSERT ON tool_usage_logs
    FOR EACH ROW EXECUTE FUNCTION trg_fn_tool_usage_insert();

CREATE OR REPLACE FUNCTION trg_fn_set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_message_updated_at
    BEFORE UPDATE ON message_templates
    FOR EACH ROW EXECUTE FUNCTION trg_fn_set_updated_at();

CREATE OR REPLACE FUNCTION trg_fn_upgrade_user_plan()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.decision = 'upgraded' THEN
        UPDATE users SET plan = 'pro' WHERE user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_conversion_upgrade
    AFTER INSERT ON conversion_outcomes
    FOR EACH ROW EXECUTE FUNCTION trg_fn_upgrade_user_plan();


-- =============================================================================
-- 9. VIEWS
-- =============================================================================

CREATE OR REPLACE VIEW v_segment_counts AS
SELECT
    s.name        AS segment_name,
    s.label,
    s.color_hex,
    COUNT(us.user_id) AS user_count
FROM segments s
LEFT JOIN user_segments us
    ON us.segment_id = s.segment_id AND us.expires_at IS NULL
GROUP BY s.segment_id, s.name, s.label, s.color_hex
ORDER BY user_count DESC;

CREATE OR REPLACE VIEW v_segment_behavioral_averages AS
SELECT
    s.name                                             AS segment_name,
    ROUND(AVG(us.feature_export_count), 1)             AS avg_exports_per_week,
    ROUND(AVG(us.feature_paywall_hits_per_week), 1)    AS avg_paywall_hits,
    ROUND(AVG(us.feature_thesaurus_depth), 1)          AS avg_synonym_depth,
    ROUND(AVG(us.feature_session_frequency), 1)        AS avg_sessions_per_week
FROM segments s
JOIN user_segments us
    ON us.segment_id = s.segment_id AND us.expires_at IS NULL
GROUP BY s.segment_id, s.name;

CREATE OR REPLACE VIEW v_ab_test_summary AS
SELECT
    s.name                                                          AS segment_name,
    s.label                                                         AS segment_label,
    s.color_hex,
    t.test_id,
    t.status,
    t.started_at,
    t.ended_at,
    t.duration_days,
    COUNT(DISTINCT aa.user_id)                                      AS total_assigned,
    COUNT(DISTINCT aa.user_id) FILTER (WHERE aa.group_type = 'control')   AS control_n,
    COUNT(DISTINCT aa.user_id) FILTER (WHERE aa.group_type = 'treatment') AS treatment_n,
    COUNT(DISTINCT co.user_id) FILTER (
        WHERE co.group_type = 'control' AND co.decision = 'upgraded')     AS control_converted,
    COUNT(DISTINCT co.user_id) FILTER (
        WHERE co.group_type = 'treatment' AND co.decision = 'upgraded')   AS treatment_converted,
    r.control_rate,
    r.treatment_rate,
    r.lift_pct,
    r.p_value,
    r.significance,
    r.winning_group
FROM ab_tests t
JOIN campaigns c        ON c.campaign_id   = t.campaign_id
JOIN segments  s        ON s.segment_id    = t.segment_id
LEFT JOIN ab_assignments aa  ON aa.test_id = t.test_id
LEFT JOIN conversion_outcomes co
    ON co.test_id = t.test_id AND co.user_id = aa.user_id
LEFT JOIN ab_test_results r  ON r.test_id  = t.test_id
GROUP BY
    s.segment_id, s.name, s.label, s.color_hex,
    t.test_id, t.status, t.started_at, t.ended_at, t.duration_days,
    r.control_rate, r.treatment_rate, r.lift_pct,
    r.p_value, r.significance, r.winning_group;

CREATE OR REPLACE VIEW v_segment_ab_comparison AS
SELECT
    s.name         AS segment_name,
    s.label,
    s.color_hex,
    r.control_rate,
    r.treatment_rate,
    r.lift_pct,
    r.significance
FROM ab_test_results r
JOIN ab_tests t ON t.test_id    = r.test_id
JOIN segments s ON s.segment_id = t.segment_id
WHERE t.status = 'completed'
ORDER BY r.lift_pct DESC NULLS LAST;

CREATE OR REPLACE VIEW v_platform_kpis AS
WITH
  free_users AS (
      SELECT COUNT(*) AS cnt FROM users WHERE plan = 'free'
  ),
  conversions AS (
      SELECT
          COUNT(*) FILTER (WHERE decision = 'upgraded') AS total_upgraded,
          COUNT(*) FILTER (WHERE decision = 'upgraded' AND churned_within_30d = TRUE) AS churned,
          AVG(revenue_amd) FILTER (WHERE decision = 'upgraded') AS avg_revenue
      FROM conversion_outcomes
  ),
  notifications AS (
      SELECT
          COUNT(*) FILTER (WHERE event_type = 'shown')                AS shown,
          COUNT(*) FILTER (WHERE event_type IN ('opened', 'clicked')) AS engaged
      FROM notification_events
  )
SELECT
    ROUND(c.total_upgraded::NUMERIC / NULLIF(f.cnt, 0), 4)     AS overall_conversion_rate,
    ROUND(n.engaged::NUMERIC          / NULLIF(n.shown, 0), 4) AS notification_engagement_rate,
    ROUND(c.churned::NUMERIC          / NULLIF(c.total_upgraded, 0), 4) AS churn_rate_30d,
    ROUND(c.avg_revenue, 2)                                     AS avg_revenue_amd
FROM free_users f, conversions c, notifications n;

CREATE OR REPLACE VIEW v_user_behavioral_features AS
SELECT
    u.user_id,
    u.email,
    u.plan,
    u.created_at,
    u.last_login_at,
    u.days_since_last_login,
    u.total_sessions,
    u.total_exports,
    u.total_paywall_hits,
    u.total_thesaurus_uses,
    ROUND(
        COUNT(se.session_id) FILTER (
            WHERE se.started_at >= now() - INTERVAL '30 days'
        )::NUMERIC / 4.3, 2
    )                                                           AS sessions_per_week,
    ROUND(AVG(tul.synonym_depth), 2)                            AS avg_synonym_depth,
    COUNT(pe.event_id) FILTER (
        WHERE pe.hit_at >= now() - INTERVAL '7 days'
    )                                                           AS paywall_hits_last_7d,
    seg.name                                                    AS current_segment
FROM users u
LEFT JOIN session_events se   ON se.user_id  = u.user_id
LEFT JOIN tool_usage_logs tul ON tul.user_id = u.user_id
LEFT JOIN paywall_events pe   ON pe.user_id  = u.user_id
LEFT JOIN user_segments us    ON us.user_id  = u.user_id AND us.expires_at IS NULL
LEFT JOIN segments seg         ON seg.segment_id = us.segment_id
GROUP BY
    u.user_id, u.email, u.plan, u.created_at, u.last_login_at,
    u.days_since_last_login, u.total_sessions, u.total_exports,
    u.total_paywall_hits, u.total_thesaurus_uses, seg.name;


-- =============================================================================
-- 10. SEED DATA
-- =============================================================================

INSERT INTO segments (name, label, color_hex, description) VALUES
    ('power',   'Power users',   '#00b87a', 'Write daily, hit vocabulary/synonym limits often, export/publish frequently'),
    ('growing', 'Growing users', '#3b82f6', 'Write a few times a week, occasionally hit limits on rhyme or thesaurus'),
    ('casual',  'Casual users',  '#f59e0b', 'Write occasionally — personal notes, social captions — rarely hit limits'),
    ('dormant', 'Dormant users', '#9ca3af', 'Signed up, wrote once or twice, then stopped returning')
ON CONFLICT (name) DO NOTHING;

INSERT INTO global_params (key, value, description) VALUES
    ('pro_price_amd',    '2900', 'Monthly Pro subscription price in Armenian Dram'),
    ('dormant_discount', '20',   'Percentage discount offered to dormant users on re-engagement'),
    ('template_count',   '120',  'Number of exclusive Pro Armenian templates shown in casual message')
ON CONFLICT (key) DO NOTHING;

WITH seg AS (SELECT segment_id, name FROM segments)
INSERT INTO campaigns (segment_id, channel, trigger_event, status)
SELECT
    segment_id,
    CASE name
        WHEN 'power'   THEN 'in_app_popup'::message_channel
        WHEN 'growing' THEN 'email'::message_channel
        WHEN 'casual'  THEN 'push_notification'::message_channel
        WHEN 'dormant' THEN 'email'::message_channel
    END,
    CASE name
        WHEN 'power'   THEN 'on_paywall_hit'::message_trigger
        WHEN 'growing' THEN 'on_app_open'::message_trigger
        WHEN 'casual'  THEN 'after_3rd_export'::message_trigger
        WHEN 'dormant' THEN 'on_app_open'::message_trigger
    END,
    'draft'
FROM seg
ON CONFLICT (segment_id) DO NOTHING;

WITH cmp AS (
    SELECT c.campaign_id, s.name AS seg_name
    FROM campaigns c
    JOIN segments s ON s.segment_id = c.segment_id
)
INSERT INTO message_templates (campaign_id, source, body, is_active)
SELECT
    campaign_id,
    'default',
    CASE seg_name
        WHEN 'power'
            THEN 'You''ve exported {{export_count}} times and hit limits {{paywall_hits}} times — go unlimited for AMD {{price}}/month.'
        WHEN 'growing'
            THEN 'You''re growing fast! Unlock HD exports, custom fonts and more — AMD {{price}}/month.'
        WHEN 'casual'
            THEN 'Did you know Pro users get {{template_count}} exclusive Armenian templates? Try Pro free for 7 days.'
        WHEN 'dormant'
            THEN 'We miss you! Come back and get {{discount}}% off your first Pro month. Offer expires in 48h.'
    END,
    TRUE
FROM cmp
ON CONFLICT DO NOTHING;

UPDATE campaigns c
SET active_message_id = mt.message_id
FROM message_templates mt
WHERE mt.campaign_id = c.campaign_id
  AND mt.source      = 'default'
  AND mt.is_active   = TRUE
  AND c.active_message_id IS NULL;

-- =============================================================================
-- SCHEMA COMPLETE
-- =============================================================================
