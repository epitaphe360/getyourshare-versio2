-- Migration: Ajouter paid_at à conversions
-- Date: 2024-12-06

ALTER TABLE conversions 
ADD COLUMN IF NOT EXISTS paid_at TIMESTAMPTZ;

COMMENT ON COLUMN conversions.paid_at IS 'Date et heure de validation du paiement';
