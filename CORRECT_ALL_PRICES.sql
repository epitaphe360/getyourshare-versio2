-- Correction complète des prix pour tous les plans (Base MAD)
-- Objectif : Cohérence entre MAD, EUR et USD

-- 1. Plan Marketplace (Influenceurs & Commerciaux)
-- Prix : 99 DH (~9.90 € / ~10.90 $)
UPDATE subscription_plans 
SET 
    price_mad = 99.00,
    price = 9.90,      -- Prix en EUR
    price_usd = 10.90  -- Prix en USD
WHERE code = 'marketplace';

-- 2. Plans Marchands (Entreprises)

-- Small Business
-- Prix : 199 DH (~19.90 € / ~21.90 $)
UPDATE subscription_plans 
SET 
    price_mad = 199.00,
    price = 19.90,
    price_usd = 21.90
WHERE code = 'small';

-- Medium Business
-- Prix : 499 DH (~49.90 € / ~54.90 $)
UPDATE subscription_plans 
SET 
    price_mad = 499.00,
    price = 49.90,
    price_usd = 54.90
WHERE code = 'medium';

-- Large Enterprise
-- Prix : 799 DH (~79.90 € / ~87.90 $)
UPDATE subscription_plans 
SET 
    price_mad = 799.00,
    price = 79.90,
    price_usd = 87.90
WHERE code = 'large';

-- 3. Plans Legacy (Starter, Pro, Elite) - Mise à jour pour cohérence
-- Starter (équivalent Small)
UPDATE subscription_plans 
SET price_mad = 290.00, price = 29.00, price_usd = 32.00 
WHERE code = 'starter';

-- Pro (équivalent Medium)
UPDATE subscription_plans 
SET price_mad = 490.00, price = 49.00, price_usd = 54.00 
WHERE code = 'pro';

-- Elite (équivalent Large)
UPDATE subscription_plans 
SET price_mad = 990.00, price = 99.00, price_usd = 109.00 
WHERE code = 'elite';

-- 4. Plans Gratuits
UPDATE subscription_plans 
SET price_mad = 0, price = 0, price_usd = 0 
WHERE price = 0 OR price_mad = 0;
