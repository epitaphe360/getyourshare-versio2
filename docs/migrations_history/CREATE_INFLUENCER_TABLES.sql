-- ================================================
-- TABLES POUR DASHBOARD INFLUENCEUR
-- ================================================
-- Créer ces tables dans cet ordre (à cause des FK)
-- ================================================

-- 1. SUBSCRIPTION PLANS (Plans d'abonnement)
-- ================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE CHECK (name IN ('Free', 'Pro', 'Elite')),
    price NUMERIC(10,2) NOT NULL DEFAULT 0,
    currency TEXT DEFAULT 'EUR',
    commission_rate NUMERIC(5,2) NOT NULL DEFAULT 5.00 CHECK (commission_rate >= 0 AND commission_rate <= 100),
    max_campaigns INTEGER, -- NULL = illimité
    instant_payout BOOLEAN DEFAULT FALSE,
    analytics_level TEXT DEFAULT 'basic' CHECK (analytics_level IN ('basic', 'advanced', 'pro')),
    features JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON subscription_plans(name);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active);

-- Insérer les plans par défaut
INSERT INTO subscription_plans (name, price, commission_rate, max_campaigns, instant_payout, analytics_level, sort_order, features) VALUES
('Free', 0, 5.00, 5, FALSE, 'basic', 1, 
 '["5 campagnes max", "Commission 5%", "Support email", "Analytics basiques"]'::jsonb
),
('Pro', 29.99, 3.00, 50, TRUE, 'advanced', 2,
 '["50 campagnes/mois", "Commission 3%", "Paiement instantané", "Analytics avancés", "Support prioritaire", "API access"]'::jsonb
),
('Elite', 99.99, 1.00, NULL, TRUE, 'pro', 3,
 '["Campagnes illimitées", "Commission 1%", "Paiement instantané", "Analytics pro + IA", "Support dédié", "API premium", "Formation personnalisée"]'::jsonb
)
ON CONFLICT (name) DO NOTHING;


-- 2. SUBSCRIPTIONS (Abonnements utilisateurs)
-- ================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'pending', 'trial')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    trial_ends_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    payment_method TEXT, -- 'stripe', 'paypal', 'bank_transfer'
    stripe_subscription_id TEXT,
    stripe_customer_id TEXT,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ajouter la contrainte UNIQUE après la création de la table
CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_unique_user_plan_start 
    ON subscriptions(user_id, plan_id, started_at);

-- Index
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_expires ON subscriptions(expires_at);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_subscriptions_updated_at();


-- 3. TRACKING LINKS (Liens d'affiliation)
-- ================================================
CREATE TABLE IF NOT EXISTS tracking_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    tracking_code TEXT NOT NULL UNIQUE,
    short_url TEXT UNIQUE, -- URL courte générée
    original_url TEXT, -- URL originale du produit
    utm_source TEXT DEFAULT 'tracknow',
    utm_medium TEXT DEFAULT 'affiliate',
    utm_campaign TEXT,
    utm_content TEXT,
    utm_term TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    clicks_count INTEGER DEFAULT 0,
    conversions_count INTEGER DEFAULT 0,
    last_clicked_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_tracking_links_influencer ON tracking_links(influencer_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_product ON tracking_links(product_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_merchant ON tracking_links(merchant_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_code ON tracking_links(tracking_code);
CREATE INDEX IF NOT EXISTS idx_tracking_links_active ON tracking_links(is_active) WHERE is_active = TRUE;

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_tracking_links_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tracking_links_updated_at
    BEFORE UPDATE ON tracking_links
    FOR EACH ROW
    EXECUTE FUNCTION update_tracking_links_updated_at();


-- 4. INVITATIONS (Invitations marchand → influenceur)
-- ================================================
CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    product_ids UUID[] DEFAULT ARRAY[]::UUID[], -- Array de product IDs
    message TEXT,
    proposed_commission NUMERIC(5,2) CHECK (proposed_commission >= 0 AND proposed_commission <= 100),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'expired')),
    responded_at TIMESTAMPTZ,
    response_message TEXT,
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_invitations_merchant ON invitations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invitations_influencer ON invitations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations(status);
CREATE INDEX IF NOT EXISTS idx_invitations_expires ON invitations(expires_at);
CREATE INDEX IF NOT EXISTS idx_invitations_campaign ON invitations(campaign_id);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_invitations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER invitations_updated_at
    BEFORE UPDATE ON invitations
    FOR EACH ROW
    EXECUTE FUNCTION update_invitations_updated_at();


-- 5. COLLABORATION REQUESTS (Demandes de collaboration)
-- ================================================
CREATE TABLE IF NOT EXISTS collaboration_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    merchant_name TEXT NOT NULL,
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    product_ids UUID[] DEFAULT ARRAY[]::UUID[],
    proposed_commission NUMERIC(5,2) CHECK (proposed_commission >= 0 AND proposed_commission <= 100),
    message TEXT,
    terms TEXT, -- Conditions de la collaboration
    duration_months INTEGER, -- Durée de la collaboration en mois
    exclusivity BOOLEAN DEFAULT FALSE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'counter_offer', 'negotiating', 'expired')),
    counter_commission NUMERIC(5,2),
    counter_message TEXT,
    counter_terms TEXT,
    responded_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '14 days'),
    contract_signed_at TIMESTAMPTZ,
    contract_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_collaboration_requests_merchant ON collaboration_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_requests_influencer ON collaboration_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_requests_status ON collaboration_requests(status);
CREATE INDEX IF NOT EXISTS idx_collaboration_requests_expires ON collaboration_requests(expires_at);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_collaboration_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER collaboration_requests_updated_at
    BEFORE UPDATE ON collaboration_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_collaboration_requests_updated_at();


-- 6. PAYOUTS (Demandes de paiement) - SI N'EXISTE PAS DÉJÀ
-- ================================================
CREATE TABLE IF NOT EXISTS payouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    currency TEXT DEFAULT 'EUR',
    payment_method TEXT NOT NULL CHECK (payment_method IN ('bank_transfer', 'paypal', 'stripe', 'mobile_payment_ma')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'processing', 'paid', 'rejected', 'cancelled')),
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    paid_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    rejection_reason TEXT,
    transaction_id TEXT, -- ID de transaction externe (PayPal, Stripe, etc.)
    transaction_receipt_url TEXT,
    bank_account_info JSONB, -- Infos bancaires chiffrées
    paypal_email TEXT,
    mobile_payment_phone TEXT,
    mobile_payment_provider TEXT, -- 'cash_plus', 'orange_money', 'inwi_money', etc.
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_payouts_influencer ON payouts(influencer_id);
CREATE INDEX IF NOT EXISTS idx_payouts_user ON payouts(user_id);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
CREATE INDEX IF NOT EXISTS idx_payouts_requested_at ON payouts(requested_at DESC);
CREATE INDEX IF NOT EXISTS idx_payouts_paid_at ON payouts(paid_at DESC);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_payouts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payouts_updated_at
    BEFORE UPDATE ON payouts
    FOR EACH ROW
    EXECUTE FUNCTION update_payouts_updated_at();


-- 7. PLATFORM SETTINGS (Paramètres plateforme)
-- ================================================
CREATE TABLE IF NOT EXISTS platform_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    setting_type TEXT DEFAULT 'string' CHECK (setting_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE, -- Si TRUE, accessible sans auth
    category TEXT, -- 'payout', 'commission', 'general', etc.
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_platform_settings_key ON platform_settings(setting_key);
CREATE INDEX IF NOT EXISTS idx_platform_settings_public ON platform_settings(is_public) WHERE is_public = TRUE;
CREATE INDEX IF NOT EXISTS idx_platform_settings_category ON platform_settings(category);

-- Insérer les paramètres par défaut
INSERT INTO platform_settings (setting_key, setting_value, setting_type, description, is_public, category) VALUES
('min_payout_amount', '50', 'number', 'Montant minimum de retrait en EUR', TRUE, 'payout'),
('max_payout_amount', '10000', 'number', 'Montant maximum de retrait par demande en EUR', TRUE, 'payout'),
('payout_processing_days', '3', 'number', 'Délai de traitement des paiements (jours ouvrés)', TRUE, 'payout'),
('default_commission_rate', '5', 'number', 'Taux de commission par défaut (%)', TRUE, 'commission'),
('platform_fee_rate', '10', 'number', 'Frais de plateforme (%)', FALSE, 'commission')
ON CONFLICT (setting_key) DO NOTHING;


-- 8. CONVERSIONS (Si n'existe pas déjà) - Pour tracker les clics/conversions
-- ================================================
CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tracking_link_id UUID REFERENCES tracking_links(id) ON DELETE SET NULL,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    visitor_ip TEXT,
    visitor_user_agent TEXT,
    visitor_country TEXT,
    visitor_city TEXT,
    referrer_url TEXT,
    conversion_type TEXT DEFAULT 'click' CHECK (conversion_type IN ('click', 'view', 'sale', 'lead')),
    converted_at TIMESTAMPTZ DEFAULT NOW(),
    sale_id UUID REFERENCES sales(id) ON DELETE SET NULL,
    sale_amount NUMERIC(12,2),
    commission_amount NUMERIC(12,2),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_conversions_tracking_link ON conversions(tracking_link_id);
CREATE INDEX IF NOT EXISTS idx_conversions_influencer ON conversions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_conversions_product ON conversions(product_id);
CREATE INDEX IF NOT EXISTS idx_conversions_merchant ON conversions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_conversions_type ON conversions(conversion_type);
CREATE INDEX IF NOT EXISTS idx_conversions_date ON conversions(converted_at DESC);


-- ================================================
-- VUES UTILES POUR PERFORMANCES
-- ================================================

-- Vue: Stats influenceur
CREATE OR REPLACE VIEW influencer_stats AS
SELECT 
    i.id as influencer_id,
    i.user_id,
    COUNT(DISTINCT tl.id) as total_links,
    COUNT(DISTINCT CASE WHEN tl.is_active THEN tl.id END) as active_links,
    COALESCE(SUM(tl.clicks_count), 0) as total_clicks,
    COALESCE(SUM(tl.conversions_count), 0) as total_conversions,
    COUNT(DISTINCT s.id) as total_sales,
    COALESCE(SUM(s.commission_amount), 0) as total_earnings,
    COALESCE(SUM(CASE WHEN p.status = 'paid' THEN p.amount ELSE 0 END), 0) as total_paid,
    COALESCE(SUM(s.commission_amount), 0) - COALESCE(SUM(CASE WHEN p.status = 'paid' THEN p.amount ELSE 0 END), 0) as balance
FROM influencers i
LEFT JOIN tracking_links tl ON tl.influencer_id = i.id
LEFT JOIN sales s ON s.influencer_id = i.id
LEFT JOIN payouts p ON p.influencer_id = i.id
GROUP BY i.id, i.user_id;

-- Vue: Performance mensuelle influenceur
CREATE OR REPLACE VIEW influencer_monthly_performance AS
SELECT 
    i.id as influencer_id,
    DATE_TRUNC('month', s.sale_date) as month,
    COUNT(s.id) as sales_count,
    COALESCE(SUM(s.total_price), 0) as total_revenue,
    COALESCE(SUM(s.commission_amount), 0) as total_commission
FROM influencers i
LEFT JOIN sales s ON s.influencer_id = i.id
GROUP BY i.id, DATE_TRUNC('month', s.sale_date);


-- ================================================
-- FONCTIONS UTILES
-- ================================================

-- Fonction: Générer un code de tracking unique
CREATE OR REPLACE FUNCTION generate_tracking_code()
RETURNS TEXT AS $$
DECLARE
    new_code TEXT;
    code_exists BOOLEAN;
BEGIN
    LOOP
        -- Générer un code aléatoire de 8 caractères
        new_code := upper(substring(md5(random()::text) from 1 for 8));
        
        -- Vérifier si le code existe déjà
        SELECT EXISTS(SELECT 1 FROM tracking_links WHERE tracking_code = new_code) INTO code_exists;
        
        -- Si le code n'existe pas, le retourner
        IF NOT code_exists THEN
            RETURN new_code;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Fonction: Calculer le score d'un influenceur
CREATE OR REPLACE FUNCTION calculate_influencer_score(p_influencer_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_score INTEGER := 0;
    v_stats RECORD;
BEGIN
    SELECT * FROM influencer_stats WHERE influencer_id = p_influencer_id INTO v_stats;
    
    IF v_stats IS NULL THEN
        RETURN 0;
    END IF;
    
    -- Score basé sur différents critères
    v_score := v_score + (v_stats.total_sales * 10); -- 10 points par vente
    v_score := v_score + (v_stats.total_clicks / 10); -- 1 point tous les 10 clics
    v_score := v_score + (v_stats.total_earnings::INTEGER / 100); -- 1 point tous les 100€
    v_score := v_score + (v_stats.active_links * 5); -- 5 points par lien actif
    
    RETURN v_score;
END;
$$ LANGUAGE plpgsql;


-- ================================================
-- COMMENTAIRES & DOCUMENTATION
-- ================================================

COMMENT ON TABLE subscription_plans IS 'Plans d''abonnement disponibles pour les influenceurs';
COMMENT ON TABLE subscriptions IS 'Abonnements actifs des utilisateurs';
COMMENT ON TABLE tracking_links IS 'Liens d''affiliation générés pour les influenceurs';
COMMENT ON TABLE invitations IS 'Invitations envoyées par les marchands aux influenceurs';
COMMENT ON TABLE collaboration_requests IS 'Demandes de collaboration entre marchands et influenceurs';
COMMENT ON TABLE payouts IS 'Demandes de paiement des influenceurs';
COMMENT ON TABLE platform_settings IS 'Paramètres globaux de la plateforme';
COMMENT ON TABLE conversions IS 'Tracking des clics et conversions sur les liens d''affiliation';

-- ================================================
-- FIN DU SCRIPT
-- ================================================
-- Exécuter ce script dans l'ordre
-- Vérifier les erreurs avant de continuer
-- ================================================
