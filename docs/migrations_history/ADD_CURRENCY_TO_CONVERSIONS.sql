-- Migration: Ajouter currency à conversions
-- Date: 2024-12-06

ALTER TABLE conversions 
ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'EUR';

COMMENT ON COLUMN conversions.currency IS 'Devise de la conversion (EUR, USD, MAD, etc.)';
