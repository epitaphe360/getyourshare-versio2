-- ============================================
-- Table: admin_social_posts
-- Publications sociales de l'admin (publicité plateforme)
-- ============================================

DROP TABLE IF EXISTS admin_social_posts CASCADE;

CREATE TABLE IF NOT EXISTS admin_social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Admin qui a créé le post
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Contenu
    title VARCHAR(500),
    caption TEXT NOT NULL,
    media_urls JSONB DEFAULT '[]'::jsonb,  -- Array d'URLs images/vidéos
    media_type VARCHAR(50) DEFAULT 'image' CHECK (media_type IN ('image', 'video', 'carousel', 'text')),

    -- Call-to-action
    cta_text VARCHAR(255),  -- Ex: "Inscrivez-vous maintenant!"
    cta_url TEXT,  -- URL vers page d'inscription/téléchargement app

    -- Hashtags
    hashtags TEXT[],  -- Array de hashtags

    -- Plateformes ciblées
    platforms JSONB DEFAULT '{}'::jsonb,  -- {instagram: {post_id, status, url}, facebook: {...}, tiktok: {...}}

    -- Type de campagne
    campaign_type VARCHAR(100) DEFAULT 'general' CHECK (campaign_type IN (
        'general',
        'app_launch',
        'new_feature',
        'merchant_recruitment',
        'influencer_recruitment',
        'seasonal_promo',
        'user_testimonial',
        'milestone_celebration',
        'contest'
    )),

    -- Status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN (
        'draft',
        'scheduled',
        'published',
        'failed',
        'archived'
    )),

    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,

    -- Analytics (mis à jour périodiquement)
    total_views INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,  -- Clics sur CTA

    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_admin_social_posts_created_by ON admin_social_posts(created_by);
CREATE INDEX idx_admin_social_posts_status ON admin_social_posts(status);
CREATE INDEX idx_admin_social_posts_campaign_type ON admin_social_posts(campaign_type);
CREATE INDEX idx_admin_social_posts_scheduled_for ON admin_social_posts(scheduled_for);
CREATE INDEX idx_admin_social_posts_published_at ON admin_social_posts(published_at);

-- ============================================
-- Trigger: Auto-update updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_admin_social_posts_updated_at
    BEFORE UPDATE ON admin_social_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- Table: admin_social_post_templates
-- Templates de posts pour différentes campagnes
-- ============================================

DROP TABLE IF EXISTS admin_social_post_templates CASCADE;

CREATE TABLE IF NOT EXISTS admin_social_post_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Template info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'general',

    -- Contenu du template
    caption_template TEXT NOT NULL,  -- Peut contenir des variables: {{app_name}}, {{discount}}, etc.
    suggested_hashtags TEXT[],
    suggested_cta_text VARCHAR(255),
    suggested_cta_url TEXT,

    -- Exemple de média (placeholder)
    example_media_url TEXT,
    media_type VARCHAR(50) DEFAULT 'image',

    -- Metadata
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_admin_social_templates_category ON admin_social_post_templates(category);
CREATE INDEX idx_admin_social_templates_active ON admin_social_post_templates(is_active);

-- ============================================
-- View: Admin Social Posts Summary
-- ============================================

CREATE OR REPLACE VIEW v_admin_social_posts_summary AS
SELECT
    asp.*,
    u.email as creator_email,
    u.full_name as creator_name,
    (total_views + total_likes + total_comments + total_shares) as total_engagement
FROM admin_social_posts asp
JOIN users u ON asp.created_by = u.id
ORDER BY asp.created_at DESC;

-- ============================================
-- View: Admin Social Analytics
-- ============================================

CREATE OR REPLACE VIEW v_admin_social_analytics AS
SELECT
    COUNT(*) as total_posts,
    COUNT(CASE WHEN status = 'published' THEN 1 END) as published_posts,
    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_posts,
    COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_posts,
    SUM(total_views) as total_views,
    SUM(total_likes) as total_likes,
    SUM(total_comments) as total_comments,
    SUM(total_shares) as total_shares,
    SUM(total_clicks) as total_clicks,
    ROUND(AVG(total_views), 2) as avg_views_per_post,
    ROUND(AVG(total_likes), 2) as avg_likes_per_post,
    ROUND(
        (SUM(total_likes) + SUM(total_comments) + SUM(total_shares)) * 100.0 / NULLIF(SUM(total_views), 0),
        2
    ) as engagement_rate_percent
FROM admin_social_posts
WHERE status = 'published';

-- ============================================
-- Function: Increment template usage
-- ============================================

CREATE OR REPLACE FUNCTION increment_template_usage(template_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE admin_social_post_templates
    SET usage_count = usage_count + 1
    WHERE id = template_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Insert Template Examples
-- ============================================

INSERT INTO admin_social_post_templates (name, description, category, caption_template, suggested_hashtags, suggested_cta_text, suggested_cta_url, media_type) VALUES

('Lancement App', 'Post pour annoncer le lancement de l''application', 'app_launch',
'🚀 ShareYourSales est ENFIN disponible!

📱 La première plateforme marocaine qui connecte influenceurs et marchands.

✨ Gagnez de l''argent en partageant vos produits préférés!
💰 Commerçants: Boostez vos ventes avec nos influenceurs!

👉 Téléchargez l''app maintenant: {{app_url}}

#ShareYourSales #MarocDigital',
ARRAY['#shareyoursales', '#marocdigital', '#influence', '#casablanca', '#maroc', '#shopping', '#business'],
'Télécharger maintenant! 📲',
'https://shareyoursales.ma',
'image'),

('Recrutement Influenceurs', 'Post pour recruter des influenceurs', 'influencer_recruitment',
'🌟 Tu as une communauté engagée? Transforme-la en revenus!

💰 Gagne jusqu''à {{commission}}% de commission sur chaque vente
📊 Dashboard complet pour suivre tes performances
🚀 Publication automatique sur tes réseaux sociaux
🎁 Deals exclusifs pour ta communauté

Rejoins {{app_name}} dès maintenant! 👇

#InfluenceMaroc #GagnerArgent',
ARRAY['#influencemaroc', '#gagnerargent', '#monetisation', '#reseauxsociaux', '#maroc'],
'Devenir influenceur 🌟',
'https://shareyoursales.ma/register?role=influencer',
'image'),

('Recrutement Marchands', 'Post pour recruter des commerçants', 'merchant_recruitment',
'🏪 Commerçants marocains, boostez vos ventes! 📈

✅ Accès à +{{influencer_count}} influenceurs
✅ Paiement seulement à la performance
✅ Analytics en temps réel
✅ Gestion simplifiée des affiliations

💡 Ne payez que pour les ventes générées!

👉 Inscrivez-vous gratuitement: {{merchant_url}}

#EcommerceMaroc #Business',
ARRAY['#ecommercemaroc', '#business', '#casablanca', '#marketing', '#ventes'],
'Inscription gratuite! 🎯',
'https://shareyoursales.ma/register?role=merchant',
'image'),

('Nouvelle Fonctionnalité', 'Post pour annoncer une nouvelle feature', 'new_feature',
'🎉 Nouvelle fonctionnalité sur ShareYourSales!

{{feature_name}} est maintenant disponible!

{{feature_description}}

Mettez à jour votre app pour en profiter! 👇

#Innovation #MarocTech',
ARRAY['#innovation', '#maroctech', '#shareyoursales', '#update'],
'Découvrir maintenant ✨',
'https://shareyoursales.ma/features',
'video'),

('Témoignage Utilisateur', 'Post mettant en avant un témoignage', 'user_testimonial',
'💬 Témoignage de {{user_name}}, {{user_role}} sur ShareYourSales:

"{{testimonial_text}}"

📊 Résultats:
• {{metric_1}}
• {{metric_2}}
• {{metric_3}}

Vous aussi, rejoignez ShareYourSales! 🚀

#Success #Témoignage',
ARRAY['#success', '#témoignage', '#shareyoursales', '#maroc'],
'Rejoindre la communauté! 🎯',
'https://shareyoursales.ma/register',
'image'),

('Promotion Saisonnière', 'Post pour promotions saisonnières', 'seasonal_promo',
'🎊 {{season}} avec ShareYourSales!

🎁 {{promo_description}}

⏰ Offre valable jusqu''au {{end_date}}

Ne ratez pas cette opportunité! 👇

#Promo #{{season}}',
ARRAY['#promo', '#offre', '#maroc', '#shopping'],
'Profiter de l''offre! 🔥',
'https://shareyoursales.ma/promo',
'image'),

('Concours', 'Post pour organiser un concours', 'contest',
'🎁 CONCOURS ShareYourSales! 🎁

À GAGNER: {{prize_description}}

📝 Pour participer:
1️⃣ {{step_1}}
2️⃣ {{step_2}}
3️⃣ {{step_3}}

🗓 Tirage au sort le {{draw_date}}

Bonne chance! 🍀

#Concours #Giveaway',
ARRAY['#concours', '#giveaway', '#maroc', '#shareyoursales', '#cadeau'],
'Participer maintenant! 🎯',
'https://shareyoursales.ma/contest',
'image'),

('Milestone Celebration', 'Post pour célébrer un jalon important', 'milestone_celebration',
'🎉 {{milestone_number}} {{milestone_type}} sur ShareYourSales!

Merci à notre incroyable communauté! 🙏

{{thank_you_message}}

Ce n''est que le début! 🚀

#Milestone #Merci #Community',
ARRAY['#milestone', '#merci', '#community', '#shareyoursales', '#maroc'],
'Rejoindre la célébration! 🎊',
'https://shareyoursales.ma',
'image');

-- ============================================
-- RLS Policies
-- ============================================

ALTER TABLE admin_social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_social_post_templates ENABLE ROW LEVEL SECURITY;

-- Admins seulement
CREATE POLICY admin_social_posts_admin_all
    ON admin_social_posts FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY admin_social_templates_admin_all
    ON admin_social_post_templates FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Templates en lecture seule pour tous (pour preview)
CREATE POLICY admin_social_templates_public_select
    ON admin_social_post_templates FOR SELECT
    USING (is_active = TRUE);

-- ============================================
-- Commentaires
-- ============================================

COMMENT ON TABLE admin_social_posts IS 'Publications sociales créées par les admins pour promouvoir la plateforme';
COMMENT ON TABLE admin_social_post_templates IS 'Templates de posts réutilisables pour différentes campagnes';
COMMENT ON COLUMN admin_social_posts.platforms IS 'Statut de publication par plateforme {instagram: {post_id, status, url}, ...}';
COMMENT ON COLUMN admin_social_posts.campaign_type IS 'Type de campagne pour classification et analytics';
