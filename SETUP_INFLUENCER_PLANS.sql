-- Configuration des plans pour Influenceurs (Starter, Pro, Enterprise)
-- Désactivation du plan Marketplace (99 MAD)
UPDATE subscription_plans SET is_active = false WHERE code = 'marketplace';

-- 1. Plan Starter (Création ou Mise à jour)
INSERT INTO subscription_plans (id, code, name, type, price_mad, price, price_usd, role, is_active, features)
VALUES (
    uuid_generate_v4(),
    'starter',
    'Starter',
    'marketplace',
    290.00,
    29.00,
    32.00,
    'influencer',
    true,
    '{"commission_rate": 5, "analytics_level": "basic", "instant_payout": false, "priority_support": false}'::jsonb
)
ON CONFLICT (code) DO UPDATE SET
    name = 'Starter',
    type = 'marketplace',
    price_mad = 290.00,
    price = 29.00,
    price_usd = 32.00,
    role = 'influencer',
    is_active = true;

-- 2. Plan Pro (Mise à jour)
UPDATE subscription_plans 
SET 
    name = 'Pro',
    type = 'marketplace',
    price_mad = 490.00,
    price = 49.00,
    price_usd = 54.00,
    role = 'influencer',
    is_active = true,
    features = '{"commission_rate": 3, "analytics_level": "advanced", "instant_payout": true, "priority_support": true}'::jsonb
WHERE code = 'pro';

-- 3. Plan Enterprise (Anciennement Elite)
UPDATE subscription_plans 
SET 
    name = 'Enterprise',
    type = 'marketplace',
    price_mad = 990.00,
    price = 99.00,
    price_usd = 109.00,
    role = 'influencer',
    is_active = true,
    features = '{"commission_rate": 0, "analytics_level": "full", "instant_payout": true, "priority_support": true, "dedicated_manager": true}'::jsonb
WHERE code = 'elite';

-- S'assurer que le plan Elite est bien renommé/typé si le code est différent
-- Si 'elite' n'existe pas, on le crée comme 'enterprise_influencer'
INSERT INTO subscription_plans (id, code, name, type, price_mad, price, price_usd, role, is_active, features)
VALUES (
    uuid_generate_v4(),
    'enterprise_influencer',
    'Enterprise',
    'marketplace',
    990.00,
    99.00,
    109.00,
    'influencer',
    true,
    '{"commission_rate": 0, "analytics_level": "full", "instant_payout": true, "priority_support": true, "dedicated_manager": true}'::jsonb
)
ON CONFLICT (code) DO NOTHING;

-- Si 'elite' existait et a été mis à jour, on s'assure qu'on n'a pas de doublon avec 'enterprise_influencer'
-- On garde 'elite' comme code pour la compatibilité si déjà utilisé, mais on change le nom.
