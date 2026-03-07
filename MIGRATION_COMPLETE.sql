-- ============================================================
-- MIGRATION COMPLETE GetYourShare
-- Executer ce fichier en entier dans Supabase SQL Editor
-- ============================================================

-- ============================================
-- MIGRATION: Tables pour Media Automation Module
-- Date: 2026-01-05
-- ============================================

-- Table 1: Connexions aux plateformes sociales
CREATE TABLE IF NOT EXISTS media_platforms (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'twitter', 'linkedin', 'facebook', 'tiktok')),
    account_name VARCHAR(255),
    account_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,  -- Encrypted
    refresh_token TEXT,  -- Encrypted
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform, account_id)
);

CREATE INDEX idx_media_platforms_user ON media_platforms(user_id);
CREATE INDEX idx_media_platforms_active ON media_platforms(is_active) WHERE is_active = true;

-- Table 2: Templates de prompts
CREATE TABLE IF NOT EXISTS media_templates (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'twitter', 'linkedin', 'facebook', 'tiktok')),
    category VARCHAR(100) CHECK (category IN ('promotional', 'educational', 'engagement', 'story', 'announcement', 'behind_scenes', 'user_generated', 'testimonial')),
    prompt_template TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    tone VARCHAR(50) CHECK (tone IN ('professional', 'casual', 'friendly', 'luxury', 'playful', 'authoritative', 'empathetic', 'witty', 'inspirational', 'educational')),
    max_length INTEGER,
    include_hashtags BOOLEAN DEFAULT true,
    include_emojis BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_templates_user ON media_templates(user_id);
CREATE INDEX idx_media_templates_platform ON media_templates(platform);
CREATE INDEX idx_media_templates_public ON media_templates(is_public) WHERE is_public = true;

-- Table 3: Contenu gÃ©nÃ©rÃ©
CREATE TABLE IF NOT EXISTS media_generated_content (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES media_templates(id) ON DELETE SET NULL,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'twitter', 'linkedin', 'facebook', 'tiktok')),
    prompt TEXT NOT NULL,
    generated_text TEXT NOT NULL,
    generated_hashtags TEXT[] DEFAULT '{}',
    media_urls TEXT[] DEFAULT '{}',
    ai_model VARCHAR(100) DEFAULT 'gpt-4-turbo',
    tone VARCHAR(50) NOT NULL,
    variables_used JSONB DEFAULT '{}',
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    engagement_prediction INTEGER CHECK (engagement_prediction >= 0 AND engagement_prediction <= 100),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'scheduled', 'published', 'rejected')),
    approved_at TIMESTAMP,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_content_user ON media_generated_content(user_id);
CREATE INDEX idx_media_content_platform ON media_generated_content(platform);
CREATE INDEX idx_media_content_status ON media_generated_content(status);
CREATE INDEX idx_media_content_created ON media_generated_content(created_at DESC);

-- Table 4: Publications planifiÃ©es
CREATE TABLE IF NOT EXISTS media_scheduled_posts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES media_generated_content(id) ON DELETE CASCADE,
    platform_id INTEGER NOT NULL REFERENCES media_platforms(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'twitter', 'linkedin', 'facebook', 'tiktok')),
    scheduled_time TIMESTAMP NOT NULL,
    optimal_time_suggested BOOLEAN DEFAULT false,
    post_text TEXT NOT NULL,
    media_urls TEXT[] DEFAULT '{}',
    hashtags TEXT[] DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'publishing', 'published', 'failed', 'cancelled')),
    published_at TIMESTAMP,
    platform_post_id VARCHAR(255),
    platform_post_url TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_posts_user ON media_scheduled_posts(user_id);
CREATE INDEX idx_media_posts_platform ON media_scheduled_posts(platform);
CREATE INDEX idx_media_posts_status ON media_scheduled_posts(status);
CREATE INDEX idx_media_posts_scheduled ON media_scheduled_posts(scheduled_time);
CREATE INDEX idx_media_posts_due ON media_scheduled_posts(scheduled_time) WHERE status = 'scheduled';

-- Table 5: Analytics des publications
CREATE TABLE IF NOT EXISTS media_analytics (
    id SERIAL PRIMARY KEY,
    scheduled_post_id INTEGER NOT NULL REFERENCES media_scheduled_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'twitter', 'linkedin', 'facebook', 'tiktok')),
    platform_post_id VARCHAR(255),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2),
    reach INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    video_views INTEGER DEFAULT 0,
    fetch_count INTEGER DEFAULT 0,
    last_fetched_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_analytics_post ON media_analytics(scheduled_post_id);
CREATE INDEX idx_media_analytics_user ON media_analytics(user_id);
CREATE INDEX idx_media_analytics_platform ON media_analytics(platform);

-- Table 6: File d'attente de publication
CREATE TABLE IF NOT EXISTS media_publishing_queue (
    id SERIAL PRIMARY KEY,
    scheduled_post_id INTEGER NOT NULL REFERENCES media_scheduled_posts(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    next_attempt_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_log TEXT,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_queue_status ON media_publishing_queue(status);
CREATE INDEX idx_media_queue_next_attempt ON media_publishing_queue(next_attempt_at) WHERE status = 'pending';

-- Table 7: Ã‰tats OAuth
CREATE TABLE IF NOT EXISTS media_oauth_states (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'twitter', 'linkedin', 'facebook', 'tiktok')),
    state_token VARCHAR(255) NOT NULL UNIQUE,
    code_verifier VARCHAR(255),
    redirect_uri TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_oauth_state ON media_oauth_states(state_token) WHERE used = false;
CREATE INDEX idx_media_oauth_cleanup ON media_oauth_states(expires_at) WHERE used = false;

-- Fonction pour mettre Ã  jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_media_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour updated_at
CREATE TRIGGER update_media_platforms_updated_at
    BEFORE UPDATE ON media_platforms
    FOR EACH ROW
    EXECUTE FUNCTION update_media_updated_at();

CREATE TRIGGER update_media_templates_updated_at
    BEFORE UPDATE ON media_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_media_updated_at();

CREATE TRIGGER update_media_content_updated_at
    BEFORE UPDATE ON media_generated_content
    FOR EACH ROW
    EXECUTE FUNCTION update_media_updated_at();

CREATE TRIGGER update_media_posts_updated_at
    BEFORE UPDATE ON media_scheduled_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_media_updated_at();

CREATE TRIGGER update_media_analytics_updated_at
    BEFORE UPDATE ON media_analytics
    FOR EACH ROW
    EXECUTE FUNCTION update_media_updated_at();

CREATE TRIGGER update_media_queue_updated_at
    BEFORE UPDATE ON media_publishing_queue
    FOR EACH ROW
    EXECUTE FUNCTION update_media_updated_at();

-- Nettoyage automatique des Ã©tats OAuth expirÃ©s (optionnel - Ã  exÃ©cuter pÃ©riodiquement)
-- DELETE FROM media_oauth_states WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '1 day';

COMMENT ON TABLE media_platforms IS 'Connexions OAuth aux plateformes sociales';
COMMENT ON TABLE media_templates IS 'Templates de prompts pour gÃ©nÃ©ration de contenu';
COMMENT ON TABLE media_generated_content IS 'Contenu gÃ©nÃ©rÃ© par IA';
COMMENT ON TABLE media_scheduled_posts IS 'Publications planifiÃ©es';
COMMENT ON TABLE media_analytics IS 'MÃ©triques de performance des publications';
COMMENT ON TABLE media_publishing_queue IS 'File d attente pour publications massives';
COMMENT ON TABLE media_oauth_states IS 'Ã‰tats temporaires pour flux OAuth';


-- ============================================================
-- MIGRATION : Tables manquantes dÃ©tectÃ©es par analyse du code
-- Date : 2026-03-06
-- Ce fichier crÃ©e TOUTES les tables utilisÃ©es dans le backend
-- Python mais non encore dÃ©finies dans les migrations SQL.
-- ============================================================

-- ============================================================
-- 1. BOT_CONVERSATIONS
-- UtilisÃ© dans : backend/ai_bot_endpoints.py, backend/services/ai_bot_service.py
-- ============================================================
CREATE TABLE IF NOT EXISTS bot_conversations (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   VARCHAR(255) NOT NULL,
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    context_json TEXT,                        -- Contexte sÃ©rialisÃ© en JSON
    message_count INTEGER DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_bot_conversations_session ON bot_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_bot_conversations_user   ON bot_conversations(user_id);

-- ============================================================
-- 2. BOT_FEEDBACK
-- UtilisÃ© dans : backend/ai_bot_endpoints.py
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
-- UtilisÃ© dans : backend/auth_advanced_endpoints.py, backend/celery_tasks.py
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
-- UtilisÃ© dans : backend/auth_advanced_endpoints.py, backend/celery_tasks.py
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
-- UtilisÃ© dans : backend/routes/missing_endpoints.py
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
-- UtilisÃ© dans : backend/routes/missing_endpoints.py,
--                backend/routes/utility_routes.py,
--                backend/fiscal_email_service.py
-- ============================================================
CREATE TABLE IF NOT EXISTS user_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    -- PrÃ©fÃ©rences gÃ©nÃ©rales
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
    -- GDPR / DonnÃ©es
    data_processing_consent BOOLEAN DEFAULT false,
    marketing_consent       BOOLEAN DEFAULT false,
    -- ParamÃ¨tres Ã©tendus (tout le reste)
    extra_settings  JSONB DEFAULT '{}',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_settings_user ON user_settings(user_id);

-- ============================================================
-- 7. SYSTEM_JOBS
-- UtilisÃ© dans : backend/routes/missing_endpoints.py
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
-- UtilisÃ© dans : backend/celery_tasks.py (aggregate_daily_analytics)
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
-- UtilisÃ© dans : backend/notification_endpoints.py
-- ============================================================
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint   TEXT NOT NULL UNIQUE,
    p256dh     TEXT,                         -- ClÃ© publique ECDH
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
-- UtilisÃ© dans : backend/fiscal_email_service.py
-- (ParamÃ¨tres d'envoi automatique de factures)
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
-- d'avoir exÃ©cutÃ© ce fichier AVANT celui-ci.
-- Tables media : media_platforms, media_templates,
--   media_generated_content, media_scheduled_posts,
--   media_analytics, media_publishing_queue, media_oauth_states
-- ============================================================

