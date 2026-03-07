-- ============================================
-- TABLES POUR SYSTÈME DE CONVERSIONS
-- ============================================

-- Table: affiliate_links (Liens d'affiliation)
CREATE TABLE IF NOT EXISTS affiliate_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    short_code VARCHAR(50) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_affiliate_links_short_code ON affiliate_links(short_code);
CREATE INDEX IF NOT EXISTS idx_affiliate_links_campaign ON affiliate_links(campaign_id);
CREATE INDEX IF NOT EXISTS idx_affiliate_links_influencer ON affiliate_links(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliate_links_status ON affiliate_links(status);

-- Table: conversions (Conversions/Ventes)
CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    affiliate_link_id UUID REFERENCES affiliate_links(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    order_amount DECIMAL(10, 2) NOT NULL,
    commission_amount DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    conversion_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validated_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    refunded_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour recherche et tri
CREATE INDEX IF NOT EXISTS idx_conversions_order_id ON conversions(order_id);
CREATE INDEX IF NOT EXISTS idx_conversions_campaign ON conversions(campaign_id);
CREATE INDEX IF NOT EXISTS idx_conversions_influencer ON conversions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_conversions_merchant ON conversions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_conversions_status ON conversions(status);
CREATE INDEX IF NOT EXISTS idx_conversions_date ON conversions(conversion_date DESC);

-- Table: clicks (Suivi des clics)
CREATE TABLE IF NOT EXISTS clicks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    affiliate_link_id UUID REFERENCES affiliate_links(id) ON DELETE CASCADE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer TEXT,
    device VARCHAR(20),
    browser VARCHAR(50),
    country VARCHAR(2),
    city VARCHAR(100),
    converted BOOLEAN DEFAULT FALSE,
    conversion_id UUID REFERENCES conversions(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour analytics
CREATE INDEX IF NOT EXISTS idx_clicks_link ON clicks(affiliate_link_id);
CREATE INDEX IF NOT EXISTS idx_clicks_date ON clicks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_clicks_converted ON clicks(converted);

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_conversions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversions_timestamp_trigger
    BEFORE UPDATE ON conversions
    FOR EACH ROW
    EXECUTE FUNCTION update_conversions_timestamp();

CREATE TRIGGER update_affiliate_links_timestamp_trigger
    BEFORE UPDATE ON affiliate_links
    FOR EACH ROW
    EXECUTE FUNCTION update_conversions_timestamp();

-- ============================================
-- VIEWS
-- ============================================

-- Vue: Conversions avec détails complets
CREATE OR REPLACE VIEW v_conversions_full AS
SELECT 
    c.id,
    c.order_id,
    c.order_amount,
    c.commission_amount,
    c.commission_rate,
    c.status,
    c.conversion_date,
    c.validated_at,
    c.paid_at,
    c.refunded_at,
    c.metadata,
    c.created_at,
    -- Campagne
    camp.name AS campaign_name,
    camp.description AS campaign_description,
    -- Influenceur
    inf.full_name AS influencer_name,
    inf.username AS influencer_username,
    u_inf.email AS influencer_email,
    -- Marchand
    m.company_name AS merchant_name,
    u_merch.email AS merchant_email,
    -- Lien d'affiliation
    al.short_code,
    al.original_url,
    al.clicks AS link_clicks
FROM conversions c
LEFT JOIN campaigns camp ON c.campaign_id = camp.id
LEFT JOIN influencers inf ON c.influencer_id = inf.id
LEFT JOIN auth.users u_inf ON inf.user_id = u_inf.id
LEFT JOIN merchants m ON c.merchant_id = m.id
LEFT JOIN auth.users u_merch ON m.user_id = u_merch.id
LEFT JOIN affiliate_links al ON c.affiliate_link_id = al.id;

-- Vue: Statistiques de conversions par campagne
CREATE OR REPLACE VIEW v_campaign_conversion_stats AS
SELECT 
    camp.id AS campaign_id,
    camp.name AS campaign_name,
    m.company_name AS merchant_name,
    COUNT(c.id) AS total_conversions,
    COUNT(CASE WHEN c.status = 'pending' THEN 1 END) AS pending_conversions,
    COUNT(CASE WHEN c.status = 'validated' THEN 1 END) AS validated_conversions,
    COUNT(CASE WHEN c.status = 'paid' THEN 1 END) AS paid_conversions,
    COUNT(CASE WHEN c.status = 'refunded' THEN 1 END) AS refunded_conversions,
    COALESCE(SUM(c.order_amount), 0) AS total_revenue,
    COALESCE(SUM(c.commission_amount), 0) AS total_commissions,
    COALESCE(AVG(c.commission_amount), 0) AS avg_commission
FROM campaigns camp
LEFT JOIN conversions c ON camp.id = c.campaign_id
LEFT JOIN merchants m ON camp.merchant_id = m.id
GROUP BY camp.id, camp.name, m.company_name;

-- Vue: Statistiques de conversions par influenceur
CREATE OR REPLACE VIEW v_influencer_conversion_stats AS
SELECT 
    inf.id AS influencer_id,
    inf.full_name AS influencer_name,
    inf.username AS influencer_username,
    u.email AS influencer_email,
    COUNT(c.id) AS total_conversions,
    COUNT(CASE WHEN c.status = 'paid' THEN 1 END) AS paid_conversions,
    COALESCE(SUM(CASE WHEN c.status = 'paid' THEN c.commission_amount ELSE 0 END), 0) AS total_earnings,
    COALESCE(SUM(CASE WHEN c.status IN ('validated', 'pending') THEN c.commission_amount ELSE 0 END), 0) AS pending_earnings,
    COALESCE(AVG(c.commission_amount), 0) AS avg_commission,
    MAX(c.conversion_date) AS last_conversion_date
FROM influencers inf
LEFT JOIN auth.users u ON inf.user_id = u.id
LEFT JOIN conversions c ON inf.id = c.influencer_id
GROUP BY inf.id, inf.full_name, inf.username, u.email;

-- ============================================
-- POLITIQUES RLS (Row Level Security)
-- ============================================

-- Activer RLS
ALTER TABLE affiliate_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE clicks ENABLE ROW LEVEL SECURITY;

-- Policy: Les admins voient tout
CREATE POLICY "Admins can view all affiliate_links" ON affiliate_links
    FOR SELECT USING (
        auth.jwt() ->> 'role' = 'admin'
    );

CREATE POLICY "Admins can view all conversions" ON conversions
    FOR SELECT USING (
        auth.jwt() ->> 'role' = 'admin'
    );

-- Policy: Les marchands voient leurs conversions
CREATE POLICY "Merchants can view their conversions" ON conversions
    FOR SELECT USING (
        merchant_id IN (
            SELECT id FROM merchants WHERE user_id = auth.uid()
        )
    );

-- Policy: Les influenceurs voient leurs conversions
CREATE POLICY "Influencers can view their conversions" ON conversions
    FOR SELECT USING (
        influencer_id IN (
            SELECT id FROM influencers WHERE user_id = auth.uid()
        )
    );

-- Policy: Les influenceurs voient leurs liens
CREATE POLICY "Influencers can view their links" ON affiliate_links
    FOR SELECT USING (
        influencer_id IN (
            SELECT id FROM influencers WHERE user_id = auth.uid()
        )
    );

-- ============================================
-- DONNÉES DE TEST (OPTIONNEL)
-- ============================================

-- Commentez cette section si vous voulez les créer via script Python

-- COMMIT;

-- Messages de succès
DO $$ 
BEGIN
    RAISE NOTICE '✅ Tables créées: affiliate_links, conversions, clicks';
    RAISE NOTICE '✅ 3 Views créées: v_conversions_full, v_campaign_conversion_stats, v_influencer_conversion_stats';
    RAISE NOTICE '✅ Politiques RLS activées';
    RAISE NOTICE '🎯 Prêt pour générer les conversions de test!';
END $$;
