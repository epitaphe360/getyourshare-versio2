-- ============================================
-- FONCTIONNALITÉS IA
-- Product Matching + Content Templates + Live Shopping
-- ============================================

-- Table: product_recommendations
-- Cache des recommandations IA par influenceur
CREATE TABLE IF NOT EXISTS public.product_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE NOT NULL,

    -- Score de matching (0-100)
    match_score INTEGER NOT NULL CHECK (match_score >= 0 AND match_score <= 100),

    -- Raisons du match
    match_reasons JSONB DEFAULT '[]'::jsonb,
    -- Exemple: ["Niche compatible: beauté", "Audience budget match", "Performance similaire: +42%"]

    -- Métriques
    niche_match BOOLEAN DEFAULT false,
    audience_match BOOLEAN DEFAULT false,
    price_match BOOLEAN DEFAULT false,
    performance_score INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT true,
    clicked BOOLEAN DEFAULT false,
    converted BOOLEAN DEFAULT false,
    link_created BOOLEAN DEFAULT false,

    -- Tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days',

    CONSTRAINT unique_influencer_product UNIQUE(influencer_id, product_id)
);

-- Table: ai_content_templates
-- Templates de contenu générés par IA
CREATE TABLE IF NOT EXISTS public.ai_content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,

    -- Type de contenu
    platform VARCHAR(20) NOT NULL, -- instagram, tiktok, facebook, linkedin
    content_type VARCHAR(20) NOT NULL, -- post, story, reel, caption

    -- Contenu généré
    title TEXT,
    content TEXT NOT NULL,
    hashtags TEXT[],
    call_to_action TEXT,

    -- Métadonnées IA
    generated_by VARCHAR(20) DEFAULT 'gpt-4', -- gpt-4, claude, gemini
    language VARCHAR(5) DEFAULT 'fr',
    tone VARCHAR(20), -- professional, casual, funny, inspirational

    -- Statistiques
    used BOOLEAN DEFAULT false,
    engagement_rate DECIMAL(5,2),
    conversions INTEGER DEFAULT 0,

    -- Timing
    best_post_time TIME,
    best_post_day VARCHAR(10),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Index
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table: live_shopping_sessions
-- Sessions de live shopping
CREATE TABLE IF NOT EXISTS public.live_shopping_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,

    -- Info session
    title VARCHAR(255) NOT NULL,
    description TEXT,
    platform VARCHAR(20) NOT NULL, -- instagram, tiktok, youtube, custom

    -- URLs
    stream_url TEXT,
    preview_image_url TEXT,

    -- Produits featured
    featured_products UUID[] DEFAULT '{}',

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, live, ended, cancelled

    -- Commission boost
    commission_boost_percentage DECIMAL(5,2) DEFAULT 5.0,

    -- Statistiques
    viewers_count INTEGER DEFAULT 0,
    peak_viewers INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_sales DECIMAL(12,2) DEFAULT 0,
    total_orders INTEGER DEFAULT 0,

    -- Timing
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Notifications
    notified_followers BOOLEAN DEFAULT false,

    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table: live_shopping_products
-- Produits dans une session live
CREATE TABLE IF NOT EXISTS public.live_shopping_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.live_shopping_sessions(id) ON DELETE CASCADE NOT NULL,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE NOT NULL,

    -- Prix spécial live
    live_price DECIMAL(10,2),
    discount_percentage DECIMAL(5,2),

    -- Tracking
    clicks INTEGER DEFAULT 0,
    orders INTEGER DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0,

    -- Display
    display_order INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: live_shopping_orders
-- Commandes pendant le live
CREATE TABLE IF NOT EXISTS public.live_shopping_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.live_shopping_sessions(id) ON DELETE CASCADE NOT NULL,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE NOT NULL,
    buyer_id UUID REFERENCES public.users(id) ON DELETE SET NULL,

    amount DECIMAL(10,2) NOT NULL,
    commission DECIMAL(10,2) NOT NULL,
    boosted_commission DECIMAL(10,2) NOT NULL, -- Commission avec boost live

    ordered_at TIMESTAMPTZ DEFAULT NOW(),

    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table: influencer_preferences
-- Préférences IA par influenceur
CREATE TABLE IF NOT EXISTS public.influencer_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,

    -- Préférences produits
    preferred_categories TEXT[],
    excluded_categories TEXT[],
    price_range_min DECIMAL(10,2),
    price_range_max DECIMAL(10,2),

    -- Audience
    audience_age_range VARCHAR(20),
    audience_gender VARCHAR(20),
    audience_location TEXT[],
    audience_interests TEXT[],

    -- Contenu
    preferred_content_types TEXT[], -- post, story, reel
    preferred_platforms TEXT[], -- instagram, tiktok
    content_tone VARCHAR(20), -- casual, professional, funny
    content_language VARCHAR(5) DEFAULT 'fr',

    -- Performance
    min_commission_rate DECIMAL(5,2),
    focus_on_conversion BOOLEAN DEFAULT true,

    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_user_preferences UNIQUE(user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_product_recs_influencer ON public.product_recommendations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_product_recs_score ON public.product_recommendations(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_product_recs_active ON public.product_recommendations(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_templates_user ON public.ai_content_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_templates_platform ON public.ai_content_templates(platform);
CREATE INDEX IF NOT EXISTS idx_live_sessions_host ON public.live_shopping_sessions(host_id);
CREATE INDEX IF NOT EXISTS idx_live_sessions_status ON public.live_shopping_sessions(status);
CREATE INDEX IF NOT EXISTS idx_live_products_session ON public.live_shopping_products(session_id);

-- Fonction: Calculer score de matching produit
CREATE OR REPLACE FUNCTION calculate_product_match_score(
    p_influencer_id UUID,
    p_product_id UUID
)
RETURNS INTEGER AS $$
DECLARE
    v_score INTEGER := 0;
    v_influencer_niche TEXT;
    v_product_category TEXT;
    v_avg_performance DECIMAL;
BEGIN
    -- Récupérer niche influenceur
    SELECT metadata->>'niche' INTO v_influencer_niche
    FROM public.users
    WHERE id = p_influencer_id;

    -- Récupérer catégorie produit
    SELECT category INTO v_product_category
    FROM public.products
    WHERE id = p_product_id;

    -- 1. Niche match (40 points)
    IF v_influencer_niche = v_product_category THEN
        v_score := v_score + 40;
    ELSIF v_influencer_niche ILIKE '%' || v_product_category || '%' THEN
        v_score := v_score + 20;
    END IF;

    -- 2. Performance historique (40 points)
    SELECT COALESCE(AVG(conversion_rate), 0) INTO v_avg_performance
    FROM public.conversions c
    JOIN public.products p ON c.product_id = p.id
    WHERE c.influencer_id = p_influencer_id
      AND p.category = v_product_category;

    v_score := v_score + LEAST(40, (v_avg_performance * 4)::INTEGER);

    -- 3. Prix match (20 points)
    -- Simplifié: on donne 20 points si le produit existe
    IF p_product_id IS NOT NULL THEN
        v_score := v_score + 20;
    END IF;

    RETURN LEAST(100, v_score);
END;
$$ LANGUAGE plpgsql;

-- Fonction: Générer recommandations pour influenceur
CREATE OR REPLACE FUNCTION generate_product_recommendations(p_influencer_id UUID)
RETURNS VOID AS $$
DECLARE
    v_product RECORD;
    v_score INTEGER;
BEGIN
    -- Supprimer anciennes recommandations
    DELETE FROM public.product_recommendations
    WHERE influencer_id = p_influencer_id
      AND expires_at < NOW();

    -- Générer nouvelles recommandations
    FOR v_product IN
        SELECT id FROM public.products
        WHERE is_active = true
        LIMIT 50
    LOOP
        v_score := calculate_product_match_score(p_influencer_id, v_product.id);

        IF v_score >= 50 THEN
            INSERT INTO public.product_recommendations (
                influencer_id, product_id, match_score,
                match_reasons, niche_match, performance_score
            )
            VALUES (
                p_influencer_id, v_product.id, v_score,
                jsonb_build_array('Score calculé: ' || v_score || '%'),
                v_score >= 70, v_score
            )
            ON CONFLICT (influencer_id, product_id)
            DO UPDATE SET
                match_score = EXCLUDED.match_score,
                updated_at = NOW(),
                expires_at = NOW() + INTERVAL '7 days';
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Vue: Top recommandations par influenceur
CREATE OR REPLACE VIEW public.v_top_recommendations AS
SELECT
    pr.influencer_id,
    pr.product_id,
    p.name as product_name,
    p.price,
    p.category,
    pr.match_score,
    pr.match_reasons,
    pr.created_at,
    COALESCE(m.company_name, m.full_name, m.email) as merchant_name
FROM public.product_recommendations pr
JOIN public.products p ON pr.product_id = p.id
JOIN public.users m ON p.merchant_id = m.id
WHERE pr.is_active = true
  AND pr.expires_at > NOW()
  AND pr.match_score >= 50
ORDER BY pr.influencer_id, pr.match_score DESC;

-- Commentaires
COMMENT ON TABLE public.product_recommendations IS 'Recommandations produits IA par influenceur';
COMMENT ON TABLE public.ai_content_templates IS 'Templates de contenu générés par IA';
COMMENT ON TABLE public.live_shopping_sessions IS 'Sessions de live shopping';
COMMENT ON TABLE public.influencer_preferences IS 'Préférences IA des influenceurs';

-- Vérification
SELECT 'Features IA créées avec succès!' as status;
