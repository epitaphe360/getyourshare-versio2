-- ============================================
-- TABLES POUR SYSTÈME DE GESTION D'ABONNEMENTS AVANCÉ
-- ============================================

-- Table des coupons promotionnels
CREATE TABLE IF NOT EXISTS coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('percentage', 'fixed', 'trial_extension', 'free_upgrade')),
    value DECIMAL(10,2) NOT NULL CHECK (value > 0),
    duration_type VARCHAR(20) NOT NULL CHECK (duration_type IN ('once', 'repeating', 'forever')),
    duration_months INTEGER CHECK (duration_months >= 1 AND duration_months <= 12),
    max_redemptions INTEGER CHECK (max_redemptions > 0),
    max_redemptions_per_user INTEGER NOT NULL DEFAULT 1 CHECK (max_redemptions_per_user > 0),
    redemption_count INTEGER NOT NULL DEFAULT 0,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE,
    eligible_plans JSONB, -- Liste des codes de plans éligibles ['pro', 'enterprise']
    new_customers_only BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Index pour les coupons
CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupons_is_active ON coupons(is_active);
CREATE INDEX IF NOT EXISTS idx_coupons_valid_dates ON coupons(valid_from, valid_until);

-- Table des utilisations de coupons
CREATE TABLE IF NOT EXISTS coupon_redemptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coupon_id UUID NOT NULL REFERENCES coupons(id) ON DELETE CASCADE,
    coupon_code VARCHAR(50) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    redeemed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    discount_amount DECIMAL(10,2),
    subscription_amount DECIMAL(10,2),
    metadata JSONB
);

-- Index pour les redemptions
CREATE INDEX IF NOT EXISTS idx_coupon_redemptions_coupon ON coupon_redemptions(coupon_id);
CREATE INDEX IF NOT EXISTS idx_coupon_redemptions_user ON coupon_redemptions(user_id);
CREATE INDEX IF NOT EXISTS idx_coupon_redemptions_date ON coupon_redemptions(redeemed_at);

-- Table pour le crédit utilisateur
CREATE TABLE IF NOT EXISTS user_credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) NOT NULL DEFAULT 'MAD',
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Index pour les crédits
CREATE INDEX IF NOT EXISTS idx_user_credits_user ON user_credits(user_id);

-- Table des événements d'abonnement (pour audit trail)
CREATE TABLE IF NOT EXISTS subscription_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'created', 'plan_changed', 'suspended', 'reactivated', 'cancelled', 'refunded'
    user_id UUID NOT NULL REFERENCES users(id),
    admin_id UUID REFERENCES users(id), -- Si action faite par un admin
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index pour les événements
CREATE INDEX IF NOT EXISTS idx_subscription_events_sub ON subscription_events(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_type ON subscription_events(event_type);
CREATE INDEX IF NOT EXISTS idx_subscription_events_date ON subscription_events(created_at);

-- Table des remboursements
CREATE TABLE IF NOT EXISTS refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    admin_id UUID REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'MAD',
    type VARCHAR(20) NOT NULL CHECK (type IN ('stripe', 'credit', 'manual')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'manual_required')),
    reason TEXT NOT NULL,
    stripe_refund_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Index pour les remboursements
CREATE INDEX IF NOT EXISTS idx_refunds_subscription ON refunds(subscription_id);
CREATE INDEX IF NOT EXISTS idx_refunds_user ON refunds(user_id);
CREATE INDEX IF NOT EXISTS idx_refunds_status ON refunds(status);

-- Ajouter des colonnes manquantes à la table subscriptions si elles n'existent pas
DO $$
BEGIN
    -- Colonne pour le plan précédent (pour tracking des changements)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscriptions' AND column_name='previous_plan') THEN
        ALTER TABLE subscriptions ADD COLUMN previous_plan VARCHAR(50);
    END IF;

    -- Colonne pour le motif d'annulation
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscriptions' AND column_name='cancellation_reason') THEN
        ALTER TABLE subscriptions ADD COLUMN cancellation_reason TEXT;
    END IF;

    -- Colonne pour metadata additionnelle
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscriptions' AND column_name='metadata') THEN
        ALTER TABLE subscriptions ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
    END IF;

    -- Colonne pour l'ID du paiement Stripe (pour les remboursements)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscriptions' AND column_name='stripe_payment_intent_id') THEN
        ALTER TABLE subscriptions ADD COLUMN stripe_payment_intent_id VARCHAR(255);
    END IF;
END $$;

-- Commentaires pour documentation
COMMENT ON TABLE coupons IS 'Codes promotionnels et coupons de réduction';
COMMENT ON TABLE coupon_redemptions IS 'Historique des utilisations de coupons';
COMMENT ON TABLE user_credits IS 'Crédits utilisateurs (remboursements, compensations)';
COMMENT ON TABLE subscription_events IS 'Audit trail de tous les événements d''abonnement';
COMMENT ON TABLE refunds IS 'Historique des remboursements effectués';

-- Données de test (optionnel)
INSERT INTO coupons (code, type, value, duration_type, valid_from, description, is_active)
VALUES 
    ('LAUNCH50', 'percentage', 50, 'once', NOW(), 'Offre de lancement - 50% de réduction sur le premier mois', true),
    ('WELCOME100', 'fixed', 100, 'once', NOW(), 'Crédit de bienvenue de 100 MAD', true),
    ('VIP20', 'percentage', 20, 'forever', NOW(), 'Remise VIP permanente de 20%', true)
ON CONFLICT (code) DO NOTHING;
