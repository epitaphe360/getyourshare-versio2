-- ============================================
-- MIGRATION: RECRÉATION DES TABLES INFLUENCERS ET MERCHANTS
-- ============================================
-- Date: 2025-11-25
-- Objectif: Créer les tables influencers et merchants avec les bonnes colonnes

-- 1. Supprimer les tables existantes (avec CASCADE pour supprimer les contraintes)
DROP TABLE IF EXISTS public.influencers CASCADE;
DROP TABLE IF EXISTS public.merchants CASCADE;

-- ============================================
-- 2. CRÉER TABLE MERCHANTS
-- ============================================

CREATE TABLE public.merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    category VARCHAR(100) CHECK (category IN (
        'E-commerce',
        'Services en ligne',
        'Voyage et tourisme',
        'Mode et lifestyle',
        'Beauté et bien-être',
        'Technologie',
        'Finance et assurance',
        'Santé et bien-être',
        'Alimentation et boissons',
        'Divertissement et médias',
        'Automobile',
        'Immobilier',
        'Sport et fitness',
        'Éducation',
        'Bricolage et décoration'
    )),
    address TEXT,
    tax_id VARCHAR(50),
    website VARCHAR(255),
    logo_url TEXT,
    description TEXT,
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('free', 'starter', 'pro', 'enterprise')) DEFAULT 'starter',
    subscription_status VARCHAR(50) DEFAULT 'active',
    commission_rate DECIMAL(5, 2) DEFAULT 5.00,
    monthly_fee DECIMAL(10, 2) DEFAULT 0.00,
    total_sales DECIMAL(15, 2) DEFAULT 0.00,
    total_commission_paid DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX idx_merchants_user_id ON public.merchants(user_id);
CREATE INDEX idx_merchants_category ON public.merchants(category);
CREATE INDEX idx_merchants_subscription_plan ON public.merchants(subscription_plan);

-- ============================================
-- 3. CRÉER TABLE INFLUENCERS
-- ============================================

CREATE TABLE public.influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    bio TEXT,
    profile_picture_url TEXT,
    category VARCHAR(100),
    influencer_type VARCHAR(50) CHECK (influencer_type IN ('nano', 'micro', 'macro', 'mega')) DEFAULT 'micro',
    audience_size INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2) DEFAULT 0.00,
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('starter', 'pro')) DEFAULT 'starter',
    subscription_status VARCHAR(50) DEFAULT 'active',
    platform_fee_rate DECIMAL(5, 2) DEFAULT 5.00,
    monthly_fee DECIMAL(10, 2) DEFAULT 9.90,
    
    -- Réseaux sociaux (JSON)
    social_links JSONB DEFAULT '{}',
    
    -- Statistiques globales
    total_clicks INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_earnings DECIMAL(15, 2) DEFAULT 0.00,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Méthodes de paiement
    payment_method VARCHAR(50),
    payment_details JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX idx_influencers_user_id ON public.influencers(user_id);
CREATE INDEX idx_influencers_username ON public.influencers(username);
CREATE INDEX idx_influencers_category ON public.influencers(category);
CREATE INDEX idx_influencers_type ON public.influencers(influencer_type);
CREATE INDEX idx_influencers_subscription_plan ON public.influencers(subscription_plan);

-- ============================================
-- 4. PERMISSIONS RLS (Row Level Security)
-- ============================================

-- Activer RLS
ALTER TABLE public.merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.influencers ENABLE ROW LEVEL SECURITY;

-- Policies pour merchants
CREATE POLICY "Les marchands peuvent voir leur propre profil"
ON public.merchants FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Les marchands peuvent modifier leur propre profil"
ON public.merchants FOR UPDATE
USING (auth.uid() = user_id);

-- Policies pour influencers
CREATE POLICY "Les influenceurs peuvent voir leur propre profil"
ON public.influencers FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Les influenceurs peuvent modifier leur propre profil"
ON public.influencers FOR UPDATE
USING (auth.uid() = user_id);

-- Policies pour les admins (peuvent tout voir)
CREATE POLICY "Les admins peuvent tout voir (merchants)"
ON public.merchants FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE users.id = auth.uid() 
        AND users.role = 'admin'
    )
);

CREATE POLICY "Les admins peuvent tout voir (influencers)"
ON public.influencers FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE users.id = auth.uid() 
        AND users.role = 'admin'
    )
);

-- ============================================
-- 5. TRIGGERS POUR UPDATED_AT
-- ============================================

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour merchants
DROP TRIGGER IF EXISTS update_merchants_updated_at ON public.merchants;
CREATE TRIGGER update_merchants_updated_at
    BEFORE UPDATE ON public.merchants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour influencers
DROP TRIGGER IF EXISTS update_influencers_updated_at ON public.influencers;
CREATE TRIGGER update_influencers_updated_at
    BEFORE UPDATE ON public.influencers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- MIGRATION TERMINÉE
-- ============================================

-- Afficher un message de succès
DO $$
BEGIN
    RAISE NOTICE '✅ Tables merchants et influencers créées avec succès !';
    RAISE NOTICE '✅ Index créés pour améliorer les performances';
    RAISE NOTICE '✅ RLS activé avec policies appropriées';
    RAISE NOTICE '✅ Triggers updated_at configurés';
END $$;
