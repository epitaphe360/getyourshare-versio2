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

-- Table 3: Contenu généré
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

-- Table 4: Publications planifiées
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

-- Table 7: États OAuth
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

-- Fonction pour mettre à jour updated_at automatiquement
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

-- Nettoyage automatique des états OAuth expirés (optionnel - à exécuter périodiquement)
-- DELETE FROM media_oauth_states WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '1 day';

COMMENT ON TABLE media_platforms IS 'Connexions OAuth aux plateformes sociales';
COMMENT ON TABLE media_templates IS 'Templates de prompts pour génération de contenu';
COMMENT ON TABLE media_generated_content IS 'Contenu généré par IA';
COMMENT ON TABLE media_scheduled_posts IS 'Publications planifiées';
COMMENT ON TABLE media_analytics IS 'Métriques de performance des publications';
COMMENT ON TABLE media_publishing_queue IS 'File d attente pour publications massives';
COMMENT ON TABLE media_oauth_states IS 'États temporaires pour flux OAuth';
