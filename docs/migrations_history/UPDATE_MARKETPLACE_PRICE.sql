-- Update Marketplace plan price to 29 (matching Creator Pro level)
UPDATE subscription_plans 
SET price = 29.00, price_mad = 290.00, price_usd = 32.00 
WHERE code = 'marketplace';
