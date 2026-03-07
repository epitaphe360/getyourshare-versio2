-- Script pour ajouter les plans manquants pour Commerciaux et Marchands
-- Basé sur la documentation du backend

DO $$
BEGIN
    -- 1. Plan Marketplace (Pour Commerciaux et Influenceurs Indépendants)
    IF NOT EXISTS (SELECT 1 FROM subscription_plans WHERE code = 'marketplace') THEN
        INSERT INTO subscription_plans (name, code, type, price_mad, price, max_team_members, max_domains, features, is_active)
        VALUES (
            'Marketplace', 
            'marketplace', 
            'marketplace', 
            99.00, 
            99.00, 
            0, 
            0, 
            '{"marketplace_access": true, "analytics": "advanced", "support": "priority"}', 
            true
        );
    END IF;

    -- 2. Plan Small (Pour Marchands débutants)
    IF NOT EXISTS (SELECT 1 FROM subscription_plans WHERE code = 'small') THEN
        INSERT INTO subscription_plans (name, code, type, price_mad, price, max_team_members, max_domains, features, is_active)
        VALUES (
            'Small Business', 
            'small', 
            'enterprise', 
            199.00, 
            199.00, 
            2, 
            1, 
            '{"products": 50, "campaigns": 5, "analytics": "standard"}', 
            true
        );
    END IF;

    -- 3. Plan Medium (Pour Marchands en croissance)
    IF NOT EXISTS (SELECT 1 FROM subscription_plans WHERE code = 'medium') THEN
        INSERT INTO subscription_plans (name, code, type, price_mad, price, max_team_members, max_domains, features, is_active)
        VALUES (
            'Medium Business', 
            'medium', 
            'enterprise', 
            499.00, 
            499.00, 
            10, 
            2, 
            '{"products": "unlimited", "campaigns": "unlimited", "analytics": "advanced"}', 
            true
        );
    END IF;

    -- 4. Plan Large (Pour Grandes Entreprises)
    IF NOT EXISTS (SELECT 1 FROM subscription_plans WHERE code = 'large') THEN
        INSERT INTO subscription_plans (name, code, type, price_mad, price, max_team_members, max_domains, features, is_active)
        VALUES (
            'Large Enterprise', 
            'large', 
            'enterprise', 
            799.00, 
            799.00, 
            30, 
            999, 
            '{"products": "unlimited", "campaigns": "unlimited", "analytics": "premium", "api_access": true}', 
            true
        );
    END IF;

END $$;
