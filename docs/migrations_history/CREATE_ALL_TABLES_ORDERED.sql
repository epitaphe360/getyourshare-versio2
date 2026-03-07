-- ================================================
-- SCRIPT DE CRÉATION COMPLÈTE - ORDRE CORRECT
-- Création de toutes les tables manquantes
-- ================================================

-- ================================================
-- ÉTAPE 1: NETTOYER L'ANCIEN SCHÉMA
-- ================================================
-- Supprimer les vues en premier (pour éviter les dépendances)
DROP VIEW IF EXISTS influencer_stats CASCADE;
DROP VIEW IF EXISTS influencer_monthly_performance CASCADE;

-- Supprimer les fonctions
DROP FUNCTION IF EXISTS generate_tracking_code() CASCADE;
DROP FUNCTION IF EXISTS calculate_influencer_score(UUID) CASCADE;
DROP FUNCTION IF EXISTS update_subscriptions_updated_at() CASCADE;
DROP FUNCTION IF EXISTS update_tracking_links_updated_at() CASCADE;
DROP FUNCTION IF EXISTS update_invitations_updated_at() CASCADE;
DROP FUNCTION IF EXISTS update_collaboration_requests_updated_at() CASCADE;
DROP FUNCTION IF EXISTS update_payouts_updated_at() CASCADE;

-- Supprimer les tables dans l'ordre inverse des dépendances
DROP TABLE IF EXISTS conversions CASCADE;
DROP TABLE IF EXISTS payouts CASCADE;
DROP TABLE IF EXISTS collaboration_requests CASCADE;
DROP TABLE IF EXISTS invitations CASCADE;
DROP TABLE IF EXISTS tracking_links CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS subscription_plans CASCADE;
DROP TABLE IF EXISTS platform_settings CASCADE;

DO $$
BEGIN
    RAISE NOTICE '✓ Ancien schéma nettoyé - Redémarrage à zéro';
END $$;

-- ================================================
-- ÉTAPE 2: CRÉER subscription_plans EN PREMIER
-- ================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2),
    commission_rate DECIMAL(5,2) NOT NULL, -- Pourcentage de commission
    max_tracking_links INTEGER,
    instant_payout BOOLEAN DEFAULT FALSE,
    priority_support BOOLEAN DEFAULT FALSE,
    custom_domain BOOLEAN DEFAULT FALSE,
    analytics_advanced BOOLEAN DEFAULT FALSE,
    features JSONB, -- Liste des fonctionnalités
    stripe_price_id_monthly TEXT,
    stripe_price_id_yearly TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Créer les 3 plans par défaut
INSERT INTO subscription_plans (name, display_name, description, price_monthly, price_yearly, commission_rate, max_tracking_links, instant_payout, priority_support, custom_domain, analytics_advanced, features)
VALUES 
    ('Free', 'Plan Gratuit', 'Idéal pour démarrer', 0.00, 0.00, 10.00, 5, FALSE, FALSE, FALSE, FALSE, 
     '["Jusqu''à 5 liens trackés", "Commission 10%", "Paiements mensuels", "Support email"]'::jsonb),
    
    ('Pro', 'Plan Pro', 'Pour les influenceurs actifs', 29.99, 299.99, 7.00, 50, TRUE, TRUE, FALSE, TRUE,
     '["Jusqu''à 50 liens trackés", "Commission 7%", "Paiements instantanés", "Support prioritaire", "Analytics avancés"]'::jsonb),
    
    ('Elite', 'Plan Elite', 'Pour les professionnels', 99.99, 999.99, 5.00, NULL, TRUE, TRUE, TRUE, TRUE,
     '["Liens trackés illimités", "Commission 5%", "Paiements instantanés", "Support VIP 24/7", "Domaine personnalisé", "Analytics premium", "API access"]'::jsonb)
ON CONFLICT (name) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE '✓ Table subscription_plans créée avec 3 plans par défaut';
END $$;

-- ================================================
-- ÉTAPE 3: CRÉER platform_settings
-- ================================================
CREATE TABLE IF NOT EXISTS platform_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key TEXT NOT NULL UNIQUE,
    setting_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insérer les paramètres par défaut
INSERT INTO platform_settings (setting_key, setting_value, description)
VALUES 
    ('min_payout_amount', '50'::jsonb, 'Montant minimum pour demander un paiement (en euros)'),
    ('commission_base_rate', '10'::jsonb, 'Taux de commission par défaut (en pourcentage)'),
    ('payout_processing_days', '7'::jsonb, 'Nombre de jours pour traiter un paiement'),
    ('tracking_cookie_duration', '30'::jsonb, 'Durée de validité du cookie de tracking (en jours)'),
    ('allowed_payment_methods', '["bank_transfer", "paypal", "mobile_money"]'::jsonb, 'Méthodes de paiement autorisées')
ON CONFLICT (setting_key) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE '✓ Table platform_settings créée avec paramètres par défaut';
END $$;

-- ================================================
-- ÉTAPE 4: CRÉER ou CORRIGER subscriptions
-- ================================================
-- Vérifier si la table existe déjà
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        RAISE NOTICE 'Table subscriptions existe déjà - Ajout des colonnes manquantes...';
        
        -- Ajouter plan_id si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'plan_id') THEN
            ALTER TABLE subscriptions ADD COLUMN plan_id UUID;
            UPDATE subscriptions SET plan_id = (SELECT id FROM subscription_plans WHERE name = 'Free' LIMIT 1) WHERE plan_id IS NULL;
            ALTER TABLE subscriptions ALTER COLUMN plan_id SET NOT NULL;
            ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES subscription_plans(id);
            RAISE NOTICE '  ✓ Colonne plan_id ajoutée';
        END IF;
        
        -- Ajouter started_at si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'started_at') THEN
            ALTER TABLE subscriptions ADD COLUMN started_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
            RAISE NOTICE '  ✓ Colonne started_at ajoutée';
        END IF;
        
        -- Ajouter expires_at si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'expires_at') THEN
            ALTER TABLE subscriptions ADD COLUMN expires_at TIMESTAMPTZ;
            RAISE NOTICE '  ✓ Colonne expires_at ajoutée';
        END IF;
        
        -- Ajouter trial_ends_at si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'trial_ends_at') THEN
            ALTER TABLE subscriptions ADD COLUMN trial_ends_at TIMESTAMPTZ;
            RAISE NOTICE '  ✓ Colonne trial_ends_at ajoutée';
        END IF;
        
        -- Ajouter cancelled_at si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'cancelled_at') THEN
            ALTER TABLE subscriptions ADD COLUMN cancelled_at TIMESTAMPTZ;
            RAISE NOTICE '  ✓ Colonne cancelled_at ajoutée';
        END IF;
        
        -- Ajouter cancellation_reason si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'cancellation_reason') THEN
            ALTER TABLE subscriptions ADD COLUMN cancellation_reason TEXT;
            RAISE NOTICE '  ✓ Colonne cancellation_reason ajoutée';
        END IF;
        
        -- Ajouter payment_method si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'payment_method') THEN
            ALTER TABLE subscriptions ADD COLUMN payment_method TEXT;
            RAISE NOTICE '  ✓ Colonne payment_method ajoutée';
        END IF;
        
        -- Ajouter stripe_subscription_id si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'stripe_subscription_id') THEN
            ALTER TABLE subscriptions ADD COLUMN stripe_subscription_id TEXT;
            RAISE NOTICE '  ✓ Colonne stripe_subscription_id ajoutée';
        END IF;
        
        -- Ajouter stripe_customer_id si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'stripe_customer_id') THEN
            ALTER TABLE subscriptions ADD COLUMN stripe_customer_id TEXT;
            RAISE NOTICE '  ✓ Colonne stripe_customer_id ajoutée';
        END IF;
        
        -- Ajouter auto_renew si manquant
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'auto_renew') THEN
            ALTER TABLE subscriptions ADD COLUMN auto_renew BOOLEAN DEFAULT TRUE;
            RAISE NOTICE '  ✓ Colonne auto_renew ajoutée';
        END IF;
        
    ELSE
        -- Créer la table complète
        CREATE TABLE subscriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            plan_id UUID NOT NULL REFERENCES subscription_plans(id),
            status TEXT NOT NULL DEFAULT 'active', -- active, cancelled, expired, trial
            started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ,
            trial_ends_at TIMESTAMPTZ,
            cancelled_at TIMESTAMPTZ,
            cancellation_reason TEXT,
            payment_method TEXT, -- stripe, manual, etc.
            stripe_subscription_id TEXT,
            stripe_customer_id TEXT,
            auto_renew BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        RAISE NOTICE '✓ Table subscriptions créée';
    END IF;
END $$;

-- Créer les index
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_expires ON subscriptions(expires_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_unique_user_plan_start ON subscriptions(user_id, plan_id, started_at);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS subscriptions_updated_at ON subscriptions;
CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_subscriptions_updated_at();

DO $$
BEGIN
    RAISE NOTICE '✓ Index et triggers pour subscriptions créés';
END $$;

-- ================================================
-- ÉTAPE 5: CRÉER tracking_links
-- ================================================
CREATE TABLE IF NOT EXISTS tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    product_id UUID, -- Référence optionnelle vers products
    tracking_code TEXT NOT NULL UNIQUE,
    original_url TEXT NOT NULL,
    campaign_name TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    clicks_count INTEGER DEFAULT 0,
    conversions_count INTEGER DEFAULT 0,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    commission_earned DECIMAL(10,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracking_links_influencer ON tracking_links(influencer_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_merchant ON tracking_links(merchant_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_code ON tracking_links(tracking_code);
CREATE INDEX IF NOT EXISTS idx_tracking_links_active ON tracking_links(is_active);

CREATE OR REPLACE FUNCTION update_tracking_links_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tracking_links_updated_at ON tracking_links;
CREATE TRIGGER tracking_links_updated_at
    BEFORE UPDATE ON tracking_links
    FOR EACH ROW
    EXECUTE FUNCTION update_tracking_links_updated_at();

DO $$
BEGIN
    RAISE NOTICE '✓ Table tracking_links créée';
END $$;

-- ================================================
-- ÉTAPE 6: CRÉER conversions
-- ================================================
CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_link_id UUID NOT NULL REFERENCES tracking_links(id) ON DELETE CASCADE,
    influencer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    order_id TEXT,
    customer_id TEXT,
    conversion_type TEXT NOT NULL DEFAULT 'sale', -- sale, lead, signup
    order_amount DECIMAL(10,2),
    commission_amount DECIMAL(10,2),
    commission_rate DECIMAL(5,2),
    status TEXT DEFAULT 'pending', -- pending, confirmed, cancelled, refunded
    ip_address TEXT,
    user_agent TEXT,
    referrer TEXT,
    metadata JSONB,
    converted_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversions_tracking_link ON conversions(tracking_link_id);
CREATE INDEX IF NOT EXISTS idx_conversions_influencer ON conversions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_conversions_merchant ON conversions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_conversions_status ON conversions(status);
CREATE INDEX IF NOT EXISTS idx_conversions_date ON conversions(converted_at);

DO $$
BEGIN
    RAISE NOTICE '✓ Table conversions créée';
END $$;

-- ================================================
-- ÉTAPE 7: CRÉER invitations
-- ================================================
CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    influencer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    campaign_name TEXT NOT NULL,
    campaign_description TEXT,
    commission_rate DECIMAL(5,2),
    fixed_payment DECIMAL(10,2),
    duration_days INTEGER,
    requirements TEXT,
    status TEXT DEFAULT 'pending', -- pending, accepted, rejected, expired
    message TEXT,
    responded_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invitations_merchant ON invitations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invitations_influencer ON invitations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations(status);

CREATE OR REPLACE FUNCTION update_invitations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS invitations_updated_at ON invitations;
CREATE TRIGGER invitations_updated_at
    BEFORE UPDATE ON invitations
    FOR EACH ROW
    EXECUTE FUNCTION update_invitations_updated_at();

DO $$
BEGIN
    RAISE NOTICE '✓ Table invitations créée';
END $$;

-- ================================================
-- ÉTAPE 8: CRÉER collaboration_requests
-- ================================================
CREATE TABLE IF NOT EXISTS collaboration_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    merchant_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_id UUID,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    proposed_commission DECIMAL(5,2),
    proposed_payment DECIMAL(10,2),
    status TEXT DEFAULT 'pending', -- pending, accepted, rejected, negotiating
    merchant_response TEXT,
    counter_offer JSONB,
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_collaboration_requests_influencer ON collaboration_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_requests_merchant ON collaboration_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_requests_status ON collaboration_requests(status);

CREATE OR REPLACE FUNCTION update_collaboration_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS collaboration_requests_updated_at ON collaboration_requests;
CREATE TRIGGER collaboration_requests_updated_at
    BEFORE UPDATE ON collaboration_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_collaboration_requests_updated_at();

DO $$
BEGIN
    RAISE NOTICE '✓ Table collaboration_requests créée';
END $$;

-- ================================================
-- ÉTAPE 9: CRÉER payouts
-- ================================================
CREATE TABLE IF NOT EXISTS payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'EUR',
    payment_method TEXT NOT NULL, -- bank_transfer, paypal, mobile_money
    payment_details JSONB, -- IBAN, PayPal email, phone number, etc.
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed, cancelled
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    transaction_id TEXT,
    notes TEXT,
    admin_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payouts_influencer ON payouts(influencer_id);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
CREATE INDEX IF NOT EXISTS idx_payouts_requested ON payouts(requested_at);

CREATE OR REPLACE FUNCTION update_payouts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS payouts_updated_at ON payouts;
CREATE TRIGGER payouts_updated_at
    BEFORE UPDATE ON payouts
    FOR EACH ROW
    EXECUTE FUNCTION update_payouts_updated_at();

DO $$
BEGIN
    RAISE NOTICE '✓ Table payouts créée';
END $$;

-- ================================================
-- ÉTAPE 10: CRÉER LES VUES
-- ================================================

-- Supprimer les anciennes vues si elles existent
DROP VIEW IF EXISTS influencer_stats CASCADE;
DROP VIEW IF EXISTS influencer_monthly_performance CASCADE;

-- Vue pour les statistiques d'influenceur
CREATE OR REPLACE VIEW influencer_stats AS
SELECT 
    u.id as influencer_id,
    u.email,
    COALESCE(sp.name, 'Free') as plan_name,
    COALESCE(sp.commission_rate, 10.00) as commission_rate,
    COALESCE(COUNT(DISTINCT tl.id), 0) as total_links,
    COALESCE(SUM(tl.clicks_count), 0) as total_clicks,
    COALESCE(SUM(tl.conversions_count), 0) as total_conversions,
    COALESCE(SUM(tl.revenue_generated), 0) as total_revenue,
    COALESCE(SUM(tl.commission_earned), 0) as total_commission_earned,
    COALESCE((
        SELECT SUM(amount) 
        FROM payouts 
        WHERE influencer_id = u.id AND status IN ('pending', 'processing')
    ), 0) as pending_payout_amount,
    COALESCE((
        SELECT SUM(amount) 
        FROM payouts 
        WHERE influencer_id = u.id AND status = 'completed'
    ), 0) as total_paid_out
FROM auth.users u
LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'
LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
LEFT JOIN tracking_links tl ON u.id = tl.influencer_id
GROUP BY u.id, u.email, sp.name, sp.commission_rate;

DO $$
BEGIN
    RAISE NOTICE '✓ Vue influencer_stats créée';
END $$;

-- Vue pour les performances mensuelles
CREATE OR REPLACE VIEW influencer_monthly_performance AS
SELECT 
    tl.influencer_id,
    DATE_TRUNC('month', COALESCE(c.converted_at, NOW())) as month,
    COUNT(DISTINCT c.id) as conversions,
    COALESCE(SUM(c.order_amount), 0) as revenue,
    COALESCE(SUM(c.commission_amount), 0) as commission_earned,
    COUNT(DISTINCT tl.id) as active_links,
    COALESCE(SUM(tl.clicks_count), 0) as total_clicks
FROM tracking_links tl
LEFT JOIN conversions c ON tl.id = c.tracking_link_id AND c.status = 'confirmed' AND c.converted_at >= DATE_TRUNC('month', NOW() - INTERVAL '12 months')
GROUP BY tl.influencer_id, DATE_TRUNC('month', COALESCE(c.converted_at, NOW()));

DO $$
BEGIN
    RAISE NOTICE '✓ Vue influencer_monthly_performance créée';
END $$;

-- ================================================
-- ÉTAPE 11: CRÉER LES FONCTIONS
-- ================================================

-- Fonction pour générer un code de tracking unique
CREATE OR REPLACE FUNCTION generate_tracking_code()
RETURNS TEXT AS $$
DECLARE
    code TEXT;
    exists BOOLEAN;
BEGIN
    LOOP
        -- Générer un code de 8 caractères
        code := UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8));
        
        -- Vérifier s'il existe déjà
        SELECT EXISTS(SELECT 1 FROM tracking_links WHERE tracking_code = code) INTO exists;
        
        EXIT WHEN NOT exists;
    END LOOP;
    
    RETURN code;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    RAISE NOTICE '✓ Fonction generate_tracking_code() créée';
END $$;

-- Fonction pour calculer le score d'influenceur
CREATE OR REPLACE FUNCTION calculate_influencer_score(influencer_uuid UUID)
RETURNS DECIMAL AS $$
DECLARE
    score DECIMAL := 0;
    total_conversions INTEGER;
    total_clicks INTEGER;
    conversion_rate DECIMAL;
    avg_order_value DECIMAL;
BEGIN
    -- Récupérer les statistiques des tracking_links
    SELECT 
        COALESCE(SUM(conversions_count), 0),
        COALESCE(SUM(clicks_count), 0)
    INTO total_conversions, total_clicks
    FROM tracking_links
    WHERE influencer_id = influencer_uuid;
    
    -- Récupérer la valeur moyenne des commandes
    SELECT COALESCE(AVG(order_amount), 0)
    INTO avg_order_value
    FROM conversions
    WHERE influencer_id = influencer_uuid AND status = 'confirmed';
    
    -- Calculer le taux de conversion
    IF total_clicks > 0 THEN
        conversion_rate := (total_conversions::DECIMAL / total_clicks) * 100;
    ELSE
        conversion_rate := 0;
    END IF;
    
    -- Calculer le score (0-100)
    score := LEAST(100, 
        (total_conversions * 2) + -- 2 points par conversion
        (conversion_rate * 10) + -- Bonus pour bon taux de conversion
        (LEAST(avg_order_value / 10, 30)) -- Bonus pour valeur panier élevée
    );
    
    RETURN ROUND(score, 2);
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    RAISE NOTICE '✓ Fonction calculate_influencer_score() créée';
END $$;

-- ================================================
-- RÉSUMÉ FINAL
-- ================================================
DO $$
DECLARE
    v_plans_count INTEGER;
    v_subscriptions_count INTEGER;
    v_links_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_plans_count FROM subscription_plans;
    SELECT COUNT(*) INTO v_subscriptions_count FROM subscriptions;
    SELECT COUNT(*) INTO v_links_count FROM tracking_links;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'CRÉATION TERMINÉE AVEC SUCCÈS';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables créées:';
    RAISE NOTICE '  ✓ subscription_plans (% plans)', v_plans_count;
    RAISE NOTICE '  ✓ platform_settings';
    RAISE NOTICE '  ✓ subscriptions (% lignes)', v_subscriptions_count;
    RAISE NOTICE '  ✓ tracking_links (% lignes)', v_links_count;
    RAISE NOTICE '  ✓ conversions';
    RAISE NOTICE '  ✓ invitations';
    RAISE NOTICE '  ✓ collaboration_requests';
    RAISE NOTICE '  ✓ payouts';
    RAISE NOTICE '';
    RAISE NOTICE 'Vues créées:';
    RAISE NOTICE '  ✓ influencer_stats';
    RAISE NOTICE '  ✓ influencer_monthly_performance';
    RAISE NOTICE '';
    RAISE NOTICE 'Fonctions créées:';
    RAISE NOTICE '  ✓ generate_tracking_code()';
    RAISE NOTICE '  ✓ calculate_influencer_score()';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Vous pouvez maintenant créer les tables Commercial avec CREATE_COMMERCIAL_TABLES.sql';
    RAISE NOTICE '========================================';
END $$;
