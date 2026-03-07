-- ============================================
-- SCRIPT DE CORRECTION FINALE - TOUTES LES COLONNES MANQUANTES
-- GetYourShare / ShareYourSales
-- Date: 26 Novembre 2025
-- ============================================

-- ============================================
-- 1. TABLE TRACKING_LINKS - Colonnes manquantes
-- ============================================
DO $$
BEGIN
    -- Ajouter tracking_code si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tracking_links' AND column_name = 'tracking_code'
    ) THEN
        ALTER TABLE tracking_links ADD COLUMN tracking_code VARCHAR(50) UNIQUE;
        -- Générer des codes pour les lignes existantes
        UPDATE tracking_links SET tracking_code = CONCAT('TRK-', UPPER(LEFT(id::text, 8))) WHERE tracking_code IS NULL;
    END IF;

    -- Ajouter short_url si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tracking_links' AND column_name = 'short_url'
    ) THEN
        ALTER TABLE tracking_links ADD COLUMN short_url VARCHAR(255);
    END IF;

    -- Ajouter expires_at si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tracking_links' AND column_name = 'expires_at'
    ) THEN
        ALTER TABLE tracking_links ADD COLUMN expires_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- ============================================
-- 2. TABLE INVITATIONS - Colonnes manquantes
-- ============================================
DO $$
BEGIN
    -- Ajouter expires_at si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'invitations' AND column_name = 'expires_at'
    ) THEN
        ALTER TABLE invitations ADD COLUMN expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days');
    END IF;

    -- Ajouter response_message si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'invitations' AND column_name = 'response_message'
    ) THEN
        ALTER TABLE invitations ADD COLUMN response_message TEXT;
    END IF;

    -- Ajouter responded_at si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'invitations' AND column_name = 'responded_at'
    ) THEN
        ALTER TABLE invitations ADD COLUMN responded_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- ============================================
-- 3. TABLE NOTIFICATIONS - Colonnes manquantes
-- ============================================
DO $$
BEGIN
    -- Ajouter is_read si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'notifications' AND column_name = 'is_read'
    ) THEN
        ALTER TABLE notifications ADD COLUMN is_read BOOLEAN DEFAULT FALSE;
    END IF;

    -- Si la colonne 'read' existe, migrer vers is_read
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'notifications' AND column_name = 'read'
    ) THEN
        UPDATE notifications SET is_read = "read" WHERE is_read IS NULL;
    END IF;
END $$;

-- ============================================
-- 4. TABLE SUBSCRIPTION_PLANS - Colonnes manquantes
-- ============================================
DO $$
BEGIN
    -- Ajouter code si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscription_plans' AND column_name = 'code'
    ) THEN
        ALTER TABLE subscription_plans ADD COLUMN code VARCHAR(50);
        -- Générer les codes depuis les noms
        UPDATE subscription_plans SET code = LOWER(REPLACE(name, ' ', '_')) WHERE code IS NULL;
    END IF;

    -- Ajouter type si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscription_plans' AND column_name = 'type'
    ) THEN
        ALTER TABLE subscription_plans ADD COLUMN type VARCHAR(50) DEFAULT 'enterprise';
        UPDATE subscription_plans 
        SET type = CASE 
            WHEN LOWER(name) IN ('marketplace', 'influencer', 'commercial') THEN 'marketplace'
            ELSE 'enterprise'
        END
        WHERE type IS NULL OR type = 'enterprise';
    END IF;

    -- Ajouter max_domains si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscription_plans' AND column_name = 'max_domains'
    ) THEN
        ALTER TABLE subscription_plans ADD COLUMN max_domains INTEGER;
        UPDATE subscription_plans 
        SET max_domains = CASE 
            WHEN LOWER(name) = 'small' THEN 1
            WHEN LOWER(name) = 'medium' THEN 2
            WHEN LOWER(name) IN ('large', 'elite', 'enterprise') THEN NULL
            ELSE 0
        END
        WHERE max_domains IS NULL;
    END IF;

    -- Ajouter price_mad si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscription_plans' AND column_name = 'price_mad'
    ) THEN
        ALTER TABLE subscription_plans ADD COLUMN price_mad DECIMAL(10,2);
        UPDATE subscription_plans SET price_mad = price * 10 WHERE price_mad IS NULL AND price IS NOT NULL;
    END IF;
END $$;

-- ============================================
-- 5. TABLE SUBSCRIPTIONS - Colonnes manquantes
-- ============================================
DO $$
BEGIN
    -- Ajouter current_period_start si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscriptions' AND column_name = 'current_period_start'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN current_period_start TIMESTAMP WITH TIME ZONE;
        UPDATE subscriptions SET current_period_start = started_at WHERE current_period_start IS NULL;
    END IF;

    -- Ajouter current_period_end si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscriptions' AND column_name = 'current_period_end'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN current_period_end TIMESTAMP WITH TIME ZONE;
        UPDATE subscriptions SET current_period_end = ends_at WHERE current_period_end IS NULL;
    END IF;

    -- Ajouter trial_end si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscriptions' AND column_name = 'trial_end'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN trial_end TIMESTAMP WITH TIME ZONE;
    END IF;

    -- Ajouter current_team_members si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscriptions' AND column_name = 'current_team_members'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN current_team_members INTEGER DEFAULT 0;
    END IF;

    -- Ajouter current_domains si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscriptions' AND column_name = 'current_domains'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN current_domains INTEGER DEFAULT 0;
    END IF;

    -- Ajouter stripe_subscription_id si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_subscription_id'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN stripe_subscription_id VARCHAR(255);
    END IF;

    -- Ajouter stripe_customer_id si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_customer_id'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN stripe_customer_id VARCHAR(255);
    END IF;
END $$;

-- ============================================
-- 6. VUE v_active_subscriptions - Mise à jour complète
-- ============================================
CREATE OR REPLACE VIEW v_active_subscriptions AS
SELECT
    s.id,
    s.user_id,
    s.plan_id,
    s.status,
    s.started_at,
    s.ends_at,
    s.created_at,
    s.current_period_start,
    s.current_period_end,
    s.trial_end,
    s.current_team_members,
    s.current_domains,
    sp.name as plan_name,
    sp.price as plan_price,
    COALESCE(sp.code, LOWER(REPLACE(sp.name, ' ', '_'))) as plan_code,
    COALESCE(sp.type, 
        CASE 
            WHEN LOWER(sp.name) IN ('marketplace', 'influencer', 'commercial') THEN 'marketplace'
            ELSE 'enterprise'
        END
    ) as plan_type,
    sp.commission_rate as plan_commission_rate,
    sp.max_team_members as plan_max_team_members,
    COALESCE(sp.max_domains, 
        CASE 
            WHEN LOWER(sp.name) = 'small' THEN 1
            WHEN LOWER(sp.name) = 'medium' THEN 2
            WHEN LOWER(sp.name) IN ('large', 'elite', 'enterprise') THEN NULL
            ELSE 0
        END
    ) as plan_max_domains,
    sp.max_campaigns as plan_max_campaigns,
    sp.max_tracking_links as plan_max_tracking_links,
    sp.instant_payout as plan_instant_payout,
    sp.analytics_level as plan_analytics_level,
    sp.priority_support as plan_priority_support,
    COALESCE(s.current_team_members, 0) < COALESCE(sp.max_team_members, 999999) as can_add_team_member,
    COALESCE(s.current_domains, 0) < COALESCE(sp.max_domains, 999999) as can_add_domain
FROM subscriptions s
JOIN subscription_plans sp ON s.plan_id = sp.id
WHERE s.status IN ('active', 'trialing');

-- ============================================
-- 7. TABLE PRODUCTS - Colonnes manquantes
-- ============================================
DO $$
BEGIN
    -- Ajouter price (colonne simple) si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'products' AND column_name = 'price'
    ) THEN
        ALTER TABLE products ADD COLUMN price DECIMAL(10,2);
        UPDATE products SET price = COALESCE(discounted_price, original_price) WHERE price IS NULL;
    END IF;
END $$;

-- ============================================
-- 8. TABLE REFERRAL_CODES - Colonnes manquantes
-- ============================================
DO $$
BEGIN
    -- Ajouter uses_count si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'referral_codes' AND column_name = 'uses_count'
    ) THEN
        ALTER TABLE referral_codes ADD COLUMN uses_count INTEGER DEFAULT 0;
    END IF;

    -- Ajouter is_active si manquant
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'referral_codes' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE referral_codes ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;
END $$;

-- ============================================
-- 9. Fonction check_subscription_limit
-- ============================================
CREATE OR REPLACE FUNCTION check_subscription_limit(p_user_id UUID, p_limit_type VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_current INTEGER;
    v_max INTEGER;
BEGIN
    SELECT 
        CASE 
            WHEN p_limit_type = 'team_members' THEN COALESCE(s.current_team_members, 0)
            WHEN p_limit_type = 'domains' THEN COALESCE(s.current_domains, 0)
            ELSE 0
        END,
        CASE 
            WHEN p_limit_type = 'team_members' THEN sp.max_team_members
            WHEN p_limit_type = 'domains' THEN COALESCE(sp.max_domains, 
                CASE 
                    WHEN LOWER(sp.name) = 'small' THEN 1
                    WHEN LOWER(sp.name) = 'medium' THEN 2
                    ELSE NULL
                END
            )
            ELSE NULL
        END
    INTO v_current, v_max
    FROM subscriptions s
    JOIN subscription_plans sp ON s.plan_id = sp.id
    WHERE s.user_id = p_user_id
    AND s.status IN ('active', 'trialing')
    LIMIT 1;

    -- Si pas de limite (NULL), on peut toujours ajouter
    IF v_max IS NULL THEN
        RETURN TRUE;
    END IF;

    -- Sinon, vérifier la limite
    RETURN v_current < v_max;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 10. Messages de confirmation
-- ============================================
SELECT '✅ Toutes les colonnes manquantes ont été ajoutées' as status;
SELECT '✅ Vue v_active_subscriptions mise à jour' as status;
SELECT '✅ Fonction check_subscription_limit mise à jour' as status;
