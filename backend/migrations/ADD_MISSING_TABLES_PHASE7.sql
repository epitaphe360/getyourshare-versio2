-- ============================================================
-- MIGRATION : Tables manquantes détectées par analyse du code
-- Date : 2026-03-06
-- Ce fichier crée TOUTES les tables utilisées dans le backend
-- Python mais non encore définies dans les migrations SQL.
-- ============================================================

-- ============================================================
-- 1. BOT_CONVERSATIONS
-- Utilisé dans : backend/ai_bot_endpoints.py, backend/services/ai_bot_service.py
-- ============================================================
CREATE TABLE IF NOT EXISTS bot_conversations (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   VARCHAR(255) NOT NULL,
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    context_json TEXT,                        -- Contexte sérialisé en JSON
    message_count INTEGER DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_bot_conversations_session ON bot_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_bot_conversations_user   ON bot_conversations(user_id);

-- ============================================================
-- 2. BOT_FEEDBACK
-- Utilisé dans : backend/ai_bot_endpoints.py
-- ============================================================
CREATE TABLE IF NOT EXISTS bot_feedback (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    message_id VARCHAR(255),
    rating     SMALLINT CHECK (rating >= 1 AND rating <= 5),
    comment    TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bot_feedback_user    ON bot_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_feedback_session ON bot_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_bot_feedback_rating  ON bot_feedback(rating);

-- ============================================================
-- 3. PASSWORD_RESET_TOKENS
-- Utilisé dans : backend/auth_advanced_endpoints.py, backend/celery_tasks.py
-- ============================================================
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token      VARCHAR(512) NOT NULL UNIQUE,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email      VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used       BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prt_token      ON password_reset_tokens(token) WHERE used = false;
CREATE INDEX IF NOT EXISTS idx_prt_user       ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_prt_expires    ON password_reset_tokens(expires_at) WHERE used = false;

-- ============================================================
-- 4. EMAIL_VERIFICATION_TOKENS
-- Utilisé dans : backend/auth_advanced_endpoints.py, backend/celery_tasks.py
-- ============================================================
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token      VARCHAR(512) NOT NULL UNIQUE,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email      VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used       BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_evt_token   ON email_verification_tokens(token) WHERE used = false;
CREATE INDEX IF NOT EXISTS idx_evt_user    ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_evt_expires ON email_verification_tokens(expires_at) WHERE used = false;

-- ============================================================
-- 5. IMPORT_JOBS
-- Utilisé dans : backend/routes/missing_endpoints.py
-- ============================================================
CREATE TABLE IF NOT EXISTS import_jobs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        VARCHAR(100) NOT NULL DEFAULT 'bulk_import_products',
    status      VARCHAR(50) DEFAULT 'queued'
                    CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    total_rows  INTEGER DEFAULT 0,
    processed   INTEGER DEFAULT 0,
    errors      INTEGER DEFAULT 0,
    error_log   TEXT,
    result_url  TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_import_jobs_user   ON import_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_import_jobs_status ON import_jobs(status);

-- ============================================================
-- 6. USER_SETTINGS
-- Utilisé dans : backend/routes/missing_endpoints.py,
--                backend/routes/utility_routes.py,
--                backend/fiscal_email_service.py
-- ============================================================
CREATE TABLE IF NOT EXISTS user_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    -- Préférences générales
    language        VARCHAR(10) DEFAULT 'fr',
    timezone        VARCHAR(100) DEFAULT 'Africa/Casablanca',
    currency        VARCHAR(10) DEFAULT 'MAD',
    -- Notifications
    notifications        BOOLEAN DEFAULT true,
    email_alerts         BOOLEAN DEFAULT true,
    sms_alerts           BOOLEAN DEFAULT false,
    push_notifications   BOOLEAN DEFAULT true,
    -- Facturation automatique
    auto_billing         BOOLEAN DEFAULT false,
    billing_day          SMALLINT DEFAULT 1,
    -- GDPR / Données
    data_processing_consent BOOLEAN DEFAULT false,
    marketing_consent       BOOLEAN DEFAULT false,
    -- Paramètres étendus (tout le reste)
    extra_settings  JSONB DEFAULT '{}',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_settings_user ON user_settings(user_id);

-- ============================================================
-- 7. SYSTEM_JOBS
-- Utilisé dans : backend/routes/missing_endpoints.py
-- ============================================================
CREATE TABLE IF NOT EXISTS system_jobs (
    id           VARCHAR(100) PRIMARY KEY,
    type         VARCHAR(100) NOT NULL,      -- 'backup', 'cleanup', 'report', etc.
    status       VARCHAR(50) DEFAULT 'queued'
                     CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    triggered_by UUID REFERENCES users(id) ON DELETE SET NULL,
    result       JSONB DEFAULT '{}',
    error_message TEXT,
    started_at   TIMESTAMP,
    completed_at TIMESTAMP,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_system_jobs_type   ON system_jobs(type);
CREATE INDEX IF NOT EXISTS idx_system_jobs_status ON system_jobs(status);

-- ============================================================
-- 8. DAILY_ANALYTICS
-- Utilisé dans : backend/celery_tasks.py (aggregate_daily_analytics)
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_analytics (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date               DATE NOT NULL UNIQUE,
    total_clicks       INTEGER DEFAULT 0,
    total_conversions  INTEGER DEFAULT 0,
    total_revenue      DECIMAL(12, 2) DEFAULT 0.00,
    new_users          INTEGER DEFAULT 0,
    active_affiliates  INTEGER DEFAULT 0,
    top_campaign_id    UUID,
    notes              TEXT,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_daily_analytics_date ON daily_analytics(date DESC);

-- ============================================================
-- 9. PUSH_SUBSCRIPTIONS
-- Utilisé dans : backend/notification_endpoints.py
-- ============================================================
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint   TEXT NOT NULL UNIQUE,
    p256dh     TEXT,                         -- Clé publique ECDH
    auth       TEXT,                         -- Secret d'authentification
    user_agent VARCHAR(255) DEFAULT 'Web',
    is_active  BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user     ON push_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_endpoint ON push_subscriptions(endpoint);
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_active   ON push_subscriptions(is_active) WHERE is_active = true;

-- ============================================================
-- 10. FISCAL_EMAIL_SETTINGS
-- Utilisé dans : backend/fiscal_email_service.py
-- (Paramètres d'envoi automatique de factures)
-- ============================================================
CREATE TABLE IF NOT EXISTS fiscal_email_settings (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    currency          VARCHAR(10) DEFAULT 'MAD',
    send_monthly      BOOLEAN DEFAULT true,
    send_day          SMALLINT DEFAULT 1,    -- Jour du mois pour envoi auto
    include_pdf       BOOLEAN DEFAULT true,
    cc_emails         TEXT[],               -- Emails en copie
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fiscal_email_settings_user ON fiscal_email_settings(user_id);

-- ============================================================
-- TRIGGERS : updated_at automatique
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger sur chaque nouvelle table
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'bot_conversations',
        'import_jobs',
        'user_settings',
        'push_subscriptions',
        'fiscal_email_settings',
        'daily_analytics'
    ]
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM pg_trigger
            WHERE tgname = 'trg_' || t || '_updated_at'
        ) THEN
            EXECUTE format(
                'CREATE TRIGGER trg_%I_updated_at
                 BEFORE UPDATE ON %I
                 FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()',
                t, t
            );
        END IF;
    END LOOP;
END
$$;

-- ============================================================
-- RAPPEL : Les 7 tables du module Media Automation sont dans
-- backend/migrations/create_media_tables.sql. Assurez-vous
-- d'avoir exécuté ce fichier AVANT celui-ci.
-- Tables media : media_platforms, media_templates,
--   media_generated_content, media_scheduled_posts,
--   media_analytics, media_publishing_queue, media_oauth_states
-- ============================================================
