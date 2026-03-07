-- ============================================
-- SCRIPT DE NETTOYAGE ET CORRECTION DES SCHÉMAS
-- ============================================
-- ATTENTION: Ce script va SUPPRIMER toutes les données dans les tables concernées
-- Assurez-vous d'avoir une sauvegarde si nécessaire!
-- 
-- INSTRUCTIONS IMPORTANTES AVANT D'EXÉCUTER :
-- 1. Fermez TOUS les autres onglets Supabase (Dashboard, Table Editor, etc.)
-- 2. Gardez uniquement l'onglet SQL Editor ouvert
-- 3. Attendez 10 secondes avant d'exécuter
-- 4. Exécutez le script complet en une seule fois
-- ============================================

-- Désactiver RLS temporairement
SET session_replication_role = replica;

-- ============================================
-- ÉTAPE 1: SUPPRIMER TOUTES LES VUES EN PREMIER
-- ============================================
DROP VIEW IF EXISTS v_products_full CASCADE;
DROP VIEW IF EXISTS v_featured_products CASCADE;
DROP VIEW IF EXISTS v_deals_of_day CASCADE;
DROP VIEW IF EXISTS v_admin_social_posts_summary CASCADE;
DROP VIEW IF EXISTS v_admin_social_analytics CASCADE;
DROP VIEW IF EXISTS v_contact_stats CASCADE;

-- ============================================
-- ÉTAPE 2: SUPPRIMER LES TABLES EN ORDRE INVERSE DES DÉPENDANCES
-- ============================================
-- Ordre critique: supprimer d'abord les tables enfants, puis les parents
-- CASCADE force la suppression même s'il y a des dépendances

-- Tables de tracking et conversions (dépendent de tracking_links)
DROP TABLE IF EXISTS click_logs CASCADE;
DROP TABLE IF EXISTS click_tracking CASCADE;
DROP TABLE IF EXISTS tracking_events CASCADE;
DROP TABLE IF EXISTS conversions CASCADE;
DROP TABLE IF EXISTS tracking_links CASCADE;
DROP TABLE IF EXISTS trackable_links CASCADE;
DROP TABLE IF EXISTS affiliate_links CASCADE;

-- Tables de ventes et commissions
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS commissions CASCADE;

-- Tables de leads
DROP TABLE IF EXISTS lead_validation CASCADE;
DROP TABLE IF EXISTS leads CASCADE;

-- Tables de campagnes
DROP TABLE IF EXISTS campaign_products CASCADE;
DROP TABLE IF EXISTS campaign_settings CASCADE;
DROP TABLE IF EXISTS campaigns CASCADE;

-- Tables d'invitations et collaborations
DROP TABLE IF EXISTS collaboration_history CASCADE;
DROP TABLE IF EXISTS collaboration_requests CASCADE;
DROP TABLE IF EXISTS collaboration_invitations CASCADE;
DROP TABLE IF EXISTS invitations CASCADE;

-- Tables d'affiliation
DROP TABLE IF EXISTS affiliation_request_history CASCADE;
DROP TABLE IF EXISTS influencer_agreements CASCADE;
DROP TABLE IF EXISTS affiliate_requests CASCADE;
DROP TABLE IF EXISTS merchant_affiliation_requests CASCADE;
DROP TABLE IF EXISTS influencer_affiliation_requests CASCADE;
DROP TABLE IF EXISTS affiliation_requests_stats CASCADE;
DROP TABLE IF EXISTS affiliation_requests CASCADE;

-- Tables de produits et services
DROP TABLE IF EXISTS product_reviews CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Tables merchant et influencer
DROP TABLE IF EXISTS influencer_profiles_extended CASCADE;
DROP TABLE IF EXISTS match_preferences CASCADE;
DROP TABLE IF EXISTS influencers CASCADE;
DROP TABLE IF EXISTS merchants CASCADE;

-- ============================================
-- ÉTAPE 3: VÉRIFIER LA TABLE USERS
-- ============================================
-- Note: On ne supprime PAS users car elle contient les authentifications

-- Ajouter les colonnes manquantes à users si nécessaire
DO $$
BEGIN
    -- Ajouter role si manquant
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role') THEN
        ALTER TABLE public.users ADD COLUMN role TEXT DEFAULT 'influencer';
    END IF;
    
    -- Ajouter is_active si manquant
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_active') THEN
        ALTER TABLE public.users ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
    
    -- Ajouter company_name si manquant
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'company_name') THEN
        ALTER TABLE public.users ADD COLUMN company_name TEXT;
    END IF;
    
    RAISE NOTICE 'Table users mise à jour avec succès';
END $$;

-- ============================================
-- ÉTAPE 4: RECRÉER TOUTES LES TABLES AVEC LE BON SCHÉMA
-- ============================================

-- MERCHANTS
CREATE TABLE public.merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    business_type TEXT,
    industry TEXT,
    website TEXT,
    description TEXT,
    logo_url TEXT,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    monthly_budget DECIMAL(12,2) DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- INFLUENCERS
CREATE TABLE public.influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    instagram_handle TEXT,
    tiktok_handle TEXT,
    youtube_handle TEXT,
    twitter_handle TEXT,
    followers_count INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    niche TEXT[],
    audience_size INTEGER DEFAULT 0,
    avg_views INTEGER DEFAULT 0,
    content_style TEXT,
    rating DECIMAL(3,2) DEFAULT 0,
    total_collaborations INTEGER DEFAULT 0,
    total_earnings DECIMAL(12,2) DEFAULT 0,
    bio TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PRODUCTS
CREATE TABLE public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    price DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    image_url TEXT,
    product_url TEXT,
    sku TEXT,
    stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    type TEXT DEFAULT 'product',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SERVICES
CREATE TABLE public.services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    price DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    pricing_model TEXT CHECK (pricing_model IN ('fixed_price', 'per_lead', 'subscription', 'commission_only')) DEFAULT 'fixed_price',
    image_url TEXT,
    duration INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CAMPAIGNS
CREATE TABLE public.campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES public.users(id),
    name TEXT NOT NULL,
    description TEXT,
    budget DECIMAL(12,2) DEFAULT 0,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    status TEXT CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')) DEFAULT 'draft',
    type TEXT,
    target_audience TEXT,
    performance_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CAMPAIGN_PRODUCTS
CREATE TABLE public.campaign_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- TRACKING_LINKS (avec unique_code)
CREATE TABLE public.tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    unique_code TEXT UNIQUE NOT NULL,
    full_url TEXT NOT NULL,
    short_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0,
    commission_earned DECIMAL(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- TRACKABLE_LINKS
CREATE TABLE public.trackable_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    unique_code TEXT UNIQUE NOT NULL,
    full_url TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CONVERSIONS
CREATE TABLE public.conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_link_id UUID REFERENCES public.tracking_links(id),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    sale_amount DECIMAL(12,2),
    commission_amount DECIMAL(12,2),
    commission_rate DECIMAL(5,2),
    status TEXT CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded')) DEFAULT 'pending',
    conversion_date TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SALES
CREATE TABLE public.sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    influencer_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    amount DECIMAL(12,2) NOT NULL,
    commission_amount DECIMAL(12,2),
    platform_commission DECIMAL(12,2),
    status TEXT DEFAULT 'completed',
    sale_timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- COMMISSIONS
CREATE TABLE public.commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    sale_id UUID REFERENCES public.sales(id),
    amount DECIMAL(12,2) NOT NULL,
    status TEXT CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')) DEFAULT 'pending',
    payout_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INVITATIONS
CREATE TABLE public.invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    message TEXT,
    commission_rate DECIMAL(5,2),
    status TEXT CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled')) DEFAULT 'pending',
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- LEADS
CREATE TABLE public.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    influencer_id UUID REFERENCES public.users(id),
    commercial_id UUID REFERENCES public.users(id),
    sales_rep_id UUID REFERENCES public.users(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    product_id UUID REFERENCES public.products(id),
    service_id UUID REFERENCES public.services(id),
    customer_name TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    commission_amount DECIMAL(12,2),
    status TEXT CHECK (status IN ('pending', 'validated', 'rejected', 'paid')) DEFAULT 'pending',
    lead_status TEXT,
    score INTEGER,
    source TEXT,
    notes TEXT,
    metadata JSONB,
    validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AFFILIATION_REQUESTS
CREATE TABLE public.affiliation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    service_id UUID REFERENCES public.services(id),
    message TEXT,
    status TEXT CHECK (status IN ('pending_approval', 'active', 'rejected', 'cancelled')) DEFAULT 'pending_approval',
    requested_commission_rate DECIMAL(5,2),
    approved_commission_rate DECIMAL(5,2),
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ÉTAPE 5: CRÉER TOUS LES INDEX
-- ============================================

-- Index pour merchants
CREATE INDEX idx_merchants_user_id ON public.merchants(user_id);

-- Index pour influencers
CREATE INDEX idx_influencers_user_id ON public.influencers(user_id);

-- Index pour products
CREATE INDEX idx_products_merchant_id ON public.products(merchant_id);
CREATE INDEX idx_products_category ON public.products(category);
CREATE INDEX idx_products_is_active ON public.products(is_active);

-- Index pour services
CREATE INDEX idx_services_merchant_id ON public.services(merchant_id);

-- Index pour campaigns
CREATE INDEX idx_campaigns_merchant_id ON public.campaigns(merchant_id);
CREATE INDEX idx_campaigns_status ON public.campaigns(status);

-- Index pour tracking_links
CREATE INDEX idx_tracking_links_influencer ON public.tracking_links(influencer_id);
CREATE INDEX idx_tracking_links_merchant ON public.tracking_links(merchant_id);
CREATE INDEX idx_tracking_links_code ON public.tracking_links(unique_code);

-- Index pour conversions
CREATE INDEX idx_conversions_influencer ON public.conversions(influencer_id);
CREATE INDEX idx_conversions_status ON public.conversions(status);

-- Index pour sales
CREATE INDEX idx_sales_merchant ON public.sales(merchant_id);
CREATE INDEX idx_sales_influencer ON public.sales(influencer_id);

-- Index pour leads
CREATE INDEX idx_leads_merchant ON public.leads(merchant_id);
CREATE INDEX idx_leads_influencer ON public.leads(influencer_id);
CREATE INDEX idx_leads_status ON public.leads(status);

-- Index pour affiliation_requests
CREATE INDEX idx_affiliation_requests_influencer ON public.affiliation_requests(influencer_id);
CREATE INDEX idx_affiliation_requests_merchant ON public.affiliation_requests(merchant_id);
CREATE INDEX idx_affiliation_requests_status ON public.affiliation_requests(status);

-- ============================================
-- ÉTAPE 6: ACTIVER RLS ET CRÉER LES POLITIQUES
-- ============================================

ALTER TABLE public.merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.influencers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.services ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tracking_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trackable_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.commissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.affiliation_requests ENABLE ROW LEVEL SECURITY;

-- Politique admin pour toutes les tables
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'merchants', 'influencers', 'products', 'services', 'campaigns',
            'tracking_links', 'trackable_links', 'conversions', 'sales',
            'commissions', 'invitations', 'leads', 'affiliation_requests'
        )
    LOOP
        EXECUTE format('
            DROP POLICY IF EXISTS admin_all_access ON public.%I;
            CREATE POLICY admin_all_access ON public.%I
            FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM public.users 
                    WHERE id = auth.uid() AND role = ''admin''
                )
            );
        ', t, t);
    END LOOP;
END $$;

-- ============================================
-- ÉTAPE 7: RÉACTIVER RLS
-- ============================================
SET session_replication_role = DEFAULT;

-- ============================================
-- ÉTAPE 8: VÉRIFICATION FINALE
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'NETTOYAGE ET RECRÉATION TERMINÉS!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables recréées: %', (
        SELECT COUNT(*) FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'merchants', 'influencers', 'products', 'services', 'campaigns',
            'tracking_links', 'trackable_links', 'conversions', 'sales',
            'commissions', 'invitations', 'leads', 'affiliation_requests'
        )
    );
    RAISE NOTICE '';
    RAISE NOTICE 'Vous pouvez maintenant exécuter CREATE_ALL_TABLES_COMPLETE.sql';
    RAISE NOTICE 'pour créer les tables restantes.';
    RAISE NOTICE '========================================';
END $$;

-- Afficher la structure de tracking_links pour vérification
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'tracking_links' 
  AND table_schema = 'public'
ORDER BY ordinal_position;
