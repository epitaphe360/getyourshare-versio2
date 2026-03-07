-- Add price_usd column to subscription_plans
ALTER TABLE subscription_plans ADD COLUMN IF NOT EXISTS price_usd DECIMAL(10, 2);

-- Update existing plans with USD prices (approximate conversion or fixed tier)
-- Assuming price is EUR. 1 EUR ~= 1.1 USD. Let's make nice numbers.

-- Free
UPDATE subscription_plans SET price_usd = 0 WHERE price = 0;

-- Starter / Small
UPDATE subscription_plans SET price_usd = 29 WHERE price = 29; -- 29 EUR -> 29 USD (often SaaS parity)
UPDATE subscription_plans SET price_usd = 49 WHERE price = 49;

-- Pro / Medium
UPDATE subscription_plans SET price_usd = 99 WHERE price = 99;
UPDATE subscription_plans SET price_usd = 149 WHERE price = 149;
UPDATE subscription_plans SET price_usd = 199 WHERE price = 199;

-- Elite / Large
UPDATE subscription_plans SET price_usd = 299 WHERE price = 299;
UPDATE subscription_plans SET price_usd = 499 WHERE price = 499;
UPDATE subscription_plans SET price_usd = 799 WHERE price = 799;

-- Marketplace
UPDATE subscription_plans SET price_usd = 99 WHERE code = 'marketplace';

-- Ensure all have a value (fallback to price if null)
UPDATE subscription_plans SET price_usd = price WHERE price_usd IS NULL;
