-- =====================================================
-- SYSTÈME DE TRACKING DES VENTES COMMERCIALES
-- =====================================================
-- Résout le problème: Les commerciaux n'ont pas de liens affiliés
-- Date: 30 novembre 2025
-- =====================================================

-- =====================================================
-- 1. TABLE: commercial_tracking_links
-- Liens affiliés pour tracking des ventes
-- =====================================================

CREATE TABLE IF NOT EXISTS commercial_tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES services_leads(id) ON DELETE SET NULL,
    
    -- Tracking
    unique_code VARCHAR(50) UNIQUE NOT NULL,
    tracking_url TEXT NOT NULL,
    short_url VARCHAR(100),
    
    -- Métadonnées
    campaign VARCHAR(100),
    channel VARCHAR(50) DEFAULT 'email',
    notes TEXT,
    
    -- Stats
    clicks INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    total_revenue NUMERIC(12,2) DEFAULT 0,
    commission_earned NUMERIC(10,2) DEFAULT 0,
    
    -- État
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_clicked_at TIMESTAMPTZ,
    last_conversion_at TIMESTAMPTZ
);

-- Index
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_commercial ON commercial_tracking_links(commercial_id);
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_lead ON commercial_tracking_links(lead_id);
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_code ON commercial_tracking_links(unique_code);
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_active ON commercial_tracking_links(is_active);

-- RLS
ALTER TABLE commercial_tracking_links ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Commerciaux voient leurs liens" ON commercial_tracking_links;
CREATE POLICY "Commerciaux voient leurs liens"
    ON commercial_tracking_links FOR SELECT
    USING (commercial_id = auth.uid());

DROP POLICY IF EXISTS "Commerciaux créent leurs liens" ON commercial_tracking_links;
CREATE POLICY "Commerciaux créent leurs liens"
    ON commercial_tracking_links FOR INSERT
    WITH CHECK (commercial_id = auth.uid());

DROP POLICY IF EXISTS "Admins accès complet commercial_tracking" ON commercial_tracking_links;
CREATE POLICY "Admins accès complet commercial_tracking"
    ON commercial_tracking_links FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role = 'admin'
        )
    );

-- =====================================================
-- 2. TABLE: promo_codes
-- Codes promo personnalisés par commercial
-- =====================================================

CREATE TABLE IF NOT EXISTS promo_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Réduction
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed')),
    discount_value NUMERIC(10,2) NOT NULL,
    
    -- Limites
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    max_usage INTEGER DEFAULT 100,
    usage_count INTEGER DEFAULT 0,
    
    -- Plan éligible
    applicable_plans TEXT[] DEFAULT ARRAY['starter', 'pro', 'enterprise'],
    
    -- Stats
    revenue_generated NUMERIC(12,2) DEFAULT 0,
    commission_earned NUMERIC(10,2) DEFAULT 0,
    
    -- État
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_promo_codes_commercial ON promo_codes(commercial_id);
CREATE INDEX IF NOT EXISTS idx_promo_codes_code ON promo_codes(code);
CREATE INDEX IF NOT EXISTS idx_promo_codes_active ON promo_codes(is_active, valid_until);

-- RLS
ALTER TABLE promo_codes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Commerciaux voient leurs codes" ON promo_codes;
CREATE POLICY "Commerciaux voient leurs codes"
    ON promo_codes FOR SELECT
    USING (commercial_id = auth.uid());

DROP POLICY IF EXISTS "Commerciaux créent leurs codes" ON promo_codes;
CREATE POLICY "Commerciaux créent leurs codes"
    ON promo_codes FOR INSERT
    WITH CHECK (commercial_id = auth.uid());

DROP POLICY IF EXISTS "Admins accès complet promo_codes" ON promo_codes;
CREATE POLICY "Admins accès complet promo_codes"
    ON promo_codes FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role = 'admin'
        )
    );

-- =====================================================
-- 3. TABLE: subscription_attributions
-- Attribution des ventes aux commerciaux
-- =====================================================

CREATE TABLE IF NOT EXISTS subscription_attributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Attribution
    commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tracking_link_id UUID REFERENCES commercial_tracking_links(id),
    promo_code_id UUID REFERENCES promo_codes(id),
    lead_id UUID REFERENCES services_leads(id),
    
    -- Type d'attribution
    attribution_type VARCHAR(50) NOT NULL DEFAULT 'last_touch' CHECK (
        attribution_type IN ('first_touch', 'last_touch', 'multi_touch', 'manual')
    ),
    commission_percentage NUMERIC(5,2) NOT NULL,
    
    -- Montants
    subscription_amount NUMERIC(10,2) NOT NULL,
    commission_amount NUMERIC(10,2) NOT NULL,
    
    -- État
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN ('pending', 'approved', 'paid', 'cancelled')
    ),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ
);

-- Index
CREATE INDEX IF NOT EXISTS idx_subscription_attributions_commercial ON subscription_attributions(commercial_id);
CREATE INDEX IF NOT EXISTS idx_subscription_attributions_user ON subscription_attributions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_attributions_status ON subscription_attributions(status);

-- RLS
ALTER TABLE subscription_attributions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Commerciaux voient leurs attributions" ON subscription_attributions;
CREATE POLICY "Commerciaux voient leurs attributions"
    ON subscription_attributions FOR SELECT
    USING (commercial_id = auth.uid());

DROP POLICY IF EXISTS "Admins accès complet subscription_attributions" ON subscription_attributions;
CREATE POLICY "Admins accès complet subscription_attributions"
    ON subscription_attributions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role = 'admin'
        )
    );

-- =====================================================
-- 4. FONCTION: Générer lien affilié commercial
-- =====================================================

CREATE OR REPLACE FUNCTION generate_commercial_tracking_link(
    p_commercial_id UUID,
    p_lead_id UUID DEFAULT NULL,
    p_campaign VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    tracking_link_id UUID,
    unique_code VARCHAR,
    full_url TEXT,
    short_url VARCHAR
) AS $$
DECLARE
    v_code VARCHAR;
    v_commercial_name VARCHAR;
    v_link_id UUID;
    v_full_url TEXT;
    v_short_url VARCHAR;
BEGIN
    -- Récupérer nom commercial
    SELECT COALESCE(first_name, 'COM') INTO v_commercial_name 
    FROM users WHERE id = p_commercial_id;
    
    -- Générer code unique
    v_code := 'COM-' || UPPER(SUBSTRING(v_commercial_name, 1, 5)) || '-' || 
              UPPER(SUBSTRING(md5(random()::text || now()::text), 1, 6));
    
    -- Construire URLs
    v_full_url := 'https://getyourshare.ma/pricing?ref=' || v_code;
    v_short_url := 'https://gys.ma/' || LOWER(SUBSTRING(v_code, 5));
    
    -- Insérer dans table
    INSERT INTO commercial_tracking_links (
        commercial_id, lead_id, unique_code, tracking_url, 
        short_url, campaign
    )
    VALUES (
        p_commercial_id, p_lead_id, v_code, v_full_url, 
        v_short_url, p_campaign
    )
    RETURNING id INTO v_link_id;
    
    -- Retourner résultat
    RETURN QUERY SELECT 
        v_link_id,
        v_code,
        v_full_url,
        v_short_url;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 5. FONCTION: Tracker clic sur lien commercial
-- =====================================================

CREATE OR REPLACE FUNCTION track_commercial_click(
    p_tracking_code VARCHAR,
    p_ip_address VARCHAR DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_link_id UUID;
BEGIN
    -- Récupérer lien
    SELECT id INTO v_link_id 
    FROM commercial_tracking_links 
    WHERE unique_code = p_tracking_code 
    AND is_active = true;
    
    IF v_link_id IS NULL THEN
        RETURN false;
    END IF;
    
    -- Incrémenter compteurs
    UPDATE commercial_tracking_links 
    SET 
        clicks = clicks + 1,
        last_clicked_at = NOW()
    WHERE id = v_link_id;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. TRIGGER: Auto-génération lien lors création lead
-- =====================================================

CREATE OR REPLACE FUNCTION auto_generate_commercial_link()
RETURNS TRIGGER AS $$
BEGIN
    -- Générer automatiquement un lien affilié pour ce lead
    PERFORM generate_commercial_tracking_link(
        NEW.commercial_id,
        NEW.id,
        'lead_' || COALESCE(NEW.company_name, 'prospect')
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_auto_generate_commercial_link ON services_leads;
CREATE TRIGGER trigger_auto_generate_commercial_link
    AFTER INSERT ON services_leads
    FOR EACH ROW
    EXECUTE FUNCTION auto_generate_commercial_link();

-- =====================================================
-- 7. VUE: Statistiques liens commerciaux
-- =====================================================

CREATE OR REPLACE VIEW commercial_tracking_stats AS
SELECT 
    ctl.commercial_id,
    u.first_name || ' ' || COALESCE(u.last_name, '') as commercial_name,
    COUNT(ctl.id) as total_links,
    SUM(ctl.clicks) as total_clicks,
    SUM(ctl.conversions) as total_conversions,
    CASE 
        WHEN SUM(ctl.clicks) > 0 
        THEN ROUND((SUM(ctl.conversions)::NUMERIC / SUM(ctl.clicks)) * 100, 2)
        ELSE 0 
    END as conversion_rate,
    SUM(ctl.total_revenue) as total_revenue,
    SUM(ctl.commission_earned) as total_commission
FROM commercial_tracking_links ctl
JOIN users u ON ctl.commercial_id = u.id
WHERE u.role = 'commercial'
GROUP BY ctl.commercial_id, u.first_name, u.last_name;

-- =====================================================
-- 8. DONNÉES DE TEST
-- =====================================================

DO $$
DECLARE
    commercial_record RECORD;
    link_count INTEGER := 0;
BEGIN
    FOR commercial_record IN 
        SELECT id FROM users WHERE role = 'commercial' LIMIT 5
    LOOP
        -- Générer 3 liens par commercial
        FOR i IN 1..3 LOOP
            PERFORM generate_commercial_tracking_link(
                commercial_record.id,
                NULL,
                'test_campaign_' || i
            );
            link_count := link_count + 1;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE '✅ % liens affiliés commerciaux générés', link_count;
END $$;

-- =====================================================
-- 9. MESSAGE FINAL
-- =====================================================

DO $$
DECLARE
    links_count INTEGER;
    commercials_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO links_count FROM commercial_tracking_links;
    SELECT COUNT(*) INTO commercials_count FROM users WHERE role = 'commercial';
    
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  ✅ SYSTÈME DE TRACKING COMMERCIAL INSTALLÉ           ║';
    RAISE NOTICE '╠════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  📊 Commerciaux: %                                    ║', LPAD(commercials_count::TEXT, 10);
    RAISE NOTICE '║  🔗 Liens créés: %                                    ║', LPAD(links_count::TEXT, 10);
    RAISE NOTICE '║  ✨ Trigger auto-génération: ACTIF                    ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Les commerciaux peuvent maintenant:';
    RAISE NOTICE '   1. Générer des liens affiliés';
    RAISE NOTICE '   2. Tracker les clics et conversions';
    RAISE NOTICE '   3. Calculer leurs commissions automatiquement';
    RAISE NOTICE '';
END $$;
