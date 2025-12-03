-- ============================================================================
-- SCHEMAS SQL POUR SUPABASE - 3 NOUVELLES TABLES
-- Content Calendar, Unified Inbox, Review Management
-- Compatible avec PostgreSQL + Supabase
-- ============================================================================

-- ============================================================================
-- TABLE 1: CONTENT_POSTS (Content Calendar pour Influenceurs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    influencer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,

    -- Informations du post
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,

    -- Plateforme et type
    platform VARCHAR(50) NOT NULL CHECK (platform IN (
        'instagram', 'facebook', 'twitter', 'tiktok', 'youtube',
        'linkedin', 'pinterest', 'snapchat', 'blog'
    )),
    content_type VARCHAR(50) DEFAULT 'post' CHECK (content_type IN (
        'post', 'story', 'reel', 'video', 'carousel', 'live', 'igtv', 'article', 'short'
    )),

    -- Statut
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN (
        'draft', 'scheduled', 'published', 'failed', 'archived'
    )),

    -- Dates
    scheduled_date TIMESTAMP,
    published_date TIMESTAMP,

    -- Médias
    media_urls JSONB DEFAULT '[]',
    thumbnail_url VARCHAR(500),

    -- Social elements
    hashtags TEXT[] DEFAULT '{}',
    mentions TEXT[] DEFAULT '{}',

    -- Call to action
    cta_type VARCHAR(20) DEFAULT 'none' CHECK (cta_type IN ('link', 'shop', 'swipe_up', 'none')),
    cta_url VARCHAR(500),

    -- Tracking
    tracking_link VARCHAR(500),
    post_url VARCHAR(500),
    external_id VARCHAR(255),

    -- Métriques
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    revenue_generated DECIMAL(10,2) DEFAULT 0,

    -- Collaboration
    is_sponsored BOOLEAN DEFAULT FALSE,
    brand_name VARCHAR(255),
    commission_rate DECIMAL(5,2),

    -- Publication automatique
    auto_publish BOOLEAN DEFAULT FALSE,
    publish_attempts INTEGER DEFAULT 0,
    last_publish_error TEXT,

    -- Notes et rappels
    notes TEXT,
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_date TIMESTAMP,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour content_posts
CREATE INDEX IF NOT EXISTS idx_content_posts_influencer ON content_posts(influencer_id);
CREATE INDEX IF NOT EXISTS idx_content_posts_platform ON content_posts(platform);
CREATE INDEX IF NOT EXISTS idx_content_posts_status ON content_posts(status);
CREATE INDEX IF NOT EXISTS idx_content_posts_scheduled ON content_posts(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_content_posts_published ON content_posts(published_date);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_content_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER content_posts_updated_at
    BEFORE UPDATE ON content_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_content_posts_updated_at();

-- ============================================================================
-- TABLE 2: UNIFIED_MESSAGES (Unified Inbox pour Commerciaux)
-- ============================================================================
CREATE TABLE IF NOT EXISTS unified_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Thread/Conversation
    thread_id UUID NOT NULL,

    -- Relations
    commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID,

    -- Contact info
    contact_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),

    -- Canal et direction
    channel VARCHAR(20) NOT NULL CHECK (channel IN (
        'email', 'sms', 'whatsapp', 'messenger', 'instagram',
        'linkedin', 'twitter', 'in_app', 'phone'
    )),
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),

    -- Contenu
    subject VARCHAR(500),
    body TEXT NOT NULL,
    html_body TEXT,
    attachments JSONB DEFAULT '[]',

    -- Statut
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN (
        'pending', 'sent', 'delivered', 'read', 'replied', 'failed', 'bounced'
    )),

    -- Lecture
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,

    -- Organisation
    is_starred BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    tags TEXT[] DEFAULT '{}',

    -- Priorité
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),

    -- Réponse attendue
    requires_response BOOLEAN DEFAULT FALSE,
    response_deadline TIMESTAMP,

    -- Analyse IA
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    sentiment_score DECIMAL(3,2),
    category VARCHAR(50) CHECK (category IN (
        'inquiry', 'complaint', 'follow_up', 'quote_request',
        'support', 'feedback', 'other'
    )),
    auto_categorized BOOLEAN DEFAULT FALSE,

    -- Données externes
    external_id VARCHAR(255),
    external_thread_id VARCHAR(255),
    parent_message_id UUID REFERENCES unified_messages(id),

    -- Tracking
    opened_count INTEGER DEFAULT 0,
    clicked_links JSONB DEFAULT '[]',

    -- Automatisation
    is_automated BOOLEAN DEFAULT FALSE,
    sequence_id UUID,

    -- Envoi programmé
    scheduled_send_at TIMESTAMP,
    sent_at TIMESTAMP,

    -- Metadata
    metadata JSONB DEFAULT '{}',
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour unified_messages
CREATE INDEX IF NOT EXISTS idx_unified_messages_thread ON unified_messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_unified_messages_commercial ON unified_messages(commercial_id);
CREATE INDEX IF NOT EXISTS idx_unified_messages_channel ON unified_messages(channel);
CREATE INDEX IF NOT EXISTS idx_unified_messages_status ON unified_messages(status);
CREATE INDEX IF NOT EXISTS idx_unified_messages_read ON unified_messages(is_read);
CREATE INDEX IF NOT EXISTS idx_unified_messages_priority ON unified_messages(priority);
CREATE INDEX IF NOT EXISTS idx_unified_messages_sentiment ON unified_messages(sentiment);

-- Trigger pour updated_at
CREATE TRIGGER unified_messages_updated_at
    BEFORE UPDATE ON unified_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_content_posts_updated_at();

-- ============================================================================
-- TABLE 3: REVIEWS (Review Management pour Marchands)
-- ============================================================================
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    service_id UUID,
    merchant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Client
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255),
    order_id UUID,
    verified_purchase BOOLEAN DEFAULT FALSE,

    -- Avis
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT NOT NULL,

    -- Médias
    images TEXT[] DEFAULT '{}',
    videos TEXT[] DEFAULT '{}',

    -- Modération
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'approved', 'rejected', 'flagged', 'spam'
    )),
    auto_moderated BOOLEAN DEFAULT FALSE,
    moderation_score DECIMAL(3,2),
    moderation_reason TEXT,

    -- Analyse IA
    sentiment VARCHAR(20) CHECK (sentiment IN (
        'very_negative', 'negative', 'neutral', 'positive', 'very_positive'
    )),
    sentiment_score DECIMAL(3,2),
    detected_issues JSONB DEFAULT '[]',

    -- Détection spam/profanité
    is_spam BOOLEAN DEFAULT FALSE,
    spam_score DECIMAL(3,2) DEFAULT 0,
    contains_profanity BOOLEAN DEFAULT FALSE,

    -- Réponse marchand
    has_response BOOLEAN DEFAULT FALSE,
    response_text TEXT,
    response_date TIMESTAMP,
    auto_response BOOLEAN DEFAULT FALSE,

    -- Visibilité
    is_featured BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,

    -- Interactions
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    report_count INTEGER DEFAULT 0,

    -- Source
    source VARCHAR(20) DEFAULT 'website' CHECK (source IN (
        'website', 'email_request', 'google', 'facebook', 'trustpilot', 'import'
    )),
    external_id VARCHAR(255),

    -- Langue
    language VARCHAR(10) DEFAULT 'fr',
    translated_comment TEXT,

    -- Modération manuelle
    moderated_by UUID,
    moderated_at TIMESTAMP,
    moderation_notes TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour reviews
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_merchant ON reviews(merchant_id);
CREATE INDEX IF NOT EXISTS idx_reviews_customer ON reviews(customer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(status);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment);
CREATE INDEX IF NOT EXISTS idx_reviews_verified ON reviews(verified_purchase);
CREATE INDEX IF NOT EXISTS idx_reviews_featured ON reviews(is_featured);

-- Trigger pour updated_at
CREATE TRIGGER reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_content_posts_updated_at();

-- ============================================================================
-- VUES UTILES
-- ============================================================================

-- Vue pour statistiques des posts par influenceur
CREATE OR REPLACE VIEW content_posts_stats AS
SELECT
    influencer_id,
    platform,
    status,
    COUNT(*) as total_posts,
    SUM(views) as total_views,
    SUM(likes) as total_likes,
    SUM(comments) as total_comments,
    SUM(shares) as total_shares,
    AVG(engagement_rate) as avg_engagement_rate,
    SUM(revenue_generated) as total_revenue
FROM content_posts
GROUP BY influencer_id, platform, status;

-- Vue pour statistiques des messages par commercial
CREATE OR REPLACE VIEW unified_messages_stats AS
SELECT
    commercial_id,
    channel,
    direction,
    status,
    COUNT(*) as total_messages,
    SUM(CASE WHEN is_read THEN 1 ELSE 0 END) as read_count,
    SUM(CASE WHEN is_starred THEN 1 ELSE 0 END) as starred_count,
    AVG(CASE WHEN sentiment_score IS NOT NULL THEN sentiment_score ELSE 0 END) as avg_sentiment
FROM unified_messages
GROUP BY commercial_id, channel, direction, status;

-- Vue pour statistiques des avis par marchand
CREATE OR REPLACE VIEW reviews_stats AS
SELECT
    merchant_id,
    COUNT(*) as total_reviews,
    AVG(rating) as avg_rating,
    COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_count,
    COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_count,
    COUNT(CASE WHEN verified_purchase THEN 1 END) as verified_count,
    COUNT(CASE WHEN has_response THEN 1 END) as responded_count,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
    COUNT(CASE WHEN status = 'flagged' THEN 1 END) as flagged_count
FROM reviews
WHERE status = 'approved'
GROUP BY merchant_id;

-- ============================================================================
-- PERMISSIONS RLS (Row Level Security)
-- ============================================================================

-- Activer RLS
ALTER TABLE content_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE unified_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Policies pour content_posts (Influenceurs voient seulement leurs posts)
CREATE POLICY "Influencers can view own posts" ON content_posts
    FOR SELECT USING (auth.uid() = influencer_id);

CREATE POLICY "Influencers can insert own posts" ON content_posts
    FOR INSERT WITH CHECK (auth.uid() = influencer_id);

CREATE POLICY "Influencers can update own posts" ON content_posts
    FOR UPDATE USING (auth.uid() = influencer_id);

-- Policies pour unified_messages (Commerciaux voient leurs messages)
CREATE POLICY "Commercials can view own messages" ON unified_messages
    FOR SELECT USING (auth.uid() = commercial_id);

CREATE POLICY "Commercials can insert own messages" ON unified_messages
    FOR INSERT WITH CHECK (auth.uid() = commercial_id);

CREATE POLICY "Commercials can update own messages" ON unified_messages
    FOR UPDATE USING (auth.uid() = commercial_id);

-- Policies pour reviews (Marchands voient leurs avis)
CREATE POLICY "Merchants can view own reviews" ON reviews
    FOR SELECT USING (auth.uid() = merchant_id);

CREATE POLICY "Merchants can update own reviews" ON reviews
    FOR UPDATE USING (auth.uid() = merchant_id);

-- Policy pour reviews publics (lecture seule)
CREATE POLICY "Anyone can view approved reviews" ON reviews
    FOR SELECT USING (status = 'approved' AND is_visible = TRUE);

-- ============================================================================
-- FUNCTIONS UTILES
-- ============================================================================

-- Fonction pour calculer l'engagement rate d'un post
CREATE OR REPLACE FUNCTION calculate_engagement_rate(post_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    post_views INTEGER;
    total_engagement INTEGER;
BEGIN
    SELECT views, (likes + comments + shares)
    INTO post_views, total_engagement
    FROM content_posts
    WHERE id = post_id;

    IF post_views > 0 THEN
        RETURN (total_engagement::DECIMAL / post_views) * 100;
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir les posts en retard
CREATE OR REPLACE FUNCTION get_overdue_posts(influencer_uuid UUID)
RETURNS TABLE (
    id UUID,
    title VARCHAR,
    scheduled_date TIMESTAMP,
    days_overdue INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cp.id,
        cp.title,
        cp.scheduled_date,
        EXTRACT(DAY FROM (NOW() - cp.scheduled_date))::INTEGER as days_overdue
    FROM content_posts cp
    WHERE cp.influencer_id = influencer_uuid
    AND cp.status = 'scheduled'
    AND cp.scheduled_date < NOW()
    ORDER BY cp.scheduled_date ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DONNÉES DE TEST (Optionnel)
-- ============================================================================

-- Insérer un post de test
-- INSERT INTO content_posts (influencer_id, title, platform, content_type, status, scheduled_date)
-- VALUES (
--     'your-influencer-uuid',
--     'Test Post',
--     'instagram',
--     'post',
--     'scheduled',
--     NOW() + INTERVAL '1 day'
-- );

COMMENT ON TABLE content_posts IS 'Calendrier éditorial multi-plateformes pour influenceurs';
COMMENT ON TABLE unified_messages IS 'Boîte de réception unifiée multi-canal pour commerciaux';
COMMENT ON TABLE reviews IS 'Gestion des avis clients avec modération IA pour marchands';
