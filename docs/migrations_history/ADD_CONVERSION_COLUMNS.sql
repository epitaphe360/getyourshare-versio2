-- Migration: Ajouter colonnes manquantes à conversions
-- Date: 2024-12-06

ALTER TABLE conversions 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS order_id TEXT,
ADD COLUMN IF NOT EXISTS platform_fee DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS payment_method TEXT,
ADD COLUMN IF NOT EXISTS customer_email TEXT;

-- Commentaires
COMMENT ON COLUMN conversions.user_id IS 'ID de l''utilisateur (peut être différent de influencer_id)';
COMMENT ON COLUMN conversions.order_id IS 'ID de la commande externe';
COMMENT ON COLUMN conversions.platform_fee IS 'Frais de plateforme';
COMMENT ON COLUMN conversions.payment_method IS 'Méthode de paiement utilisée';
COMMENT ON COLUMN conversions.customer_email IS 'Email du client final';
