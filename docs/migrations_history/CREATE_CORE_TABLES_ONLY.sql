-- ============================================
-- SCRIPT DE CRÉATION DES TABLES CORE UNIQUEMENT
-- ============================================
-- Ce script CRÉE SEULEMENT les tables, il ne supprime rien
-- À utiliser APRÈS avoir supprimé manuellement les tables via l'interface Supabase
-- ============================================

-- Désactiver RLS temporairement
SET session_replication_role = replica;

-- ============================================
-- VÉRIFIER ET METTRE À JOUR LA TABLE USERS
-- ============================================

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
    
    RAISE NOTICE 'Table users vérifiée';
END $$;

-- ============================================
-- CRÉER LES TABLES CORE
-- ============================================

-- MERCHANTS
CREATE TABLE IF NOT EXISTS public.merchants (
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
CREATE TABLE IF NOT EXISTS public.influencers (
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
CREATE TABLE IF NOT EXISTS public.products (
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
CREATE TABLE IF NOT EXISTS public.services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    price DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    image_url TEXT,
    duration INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CAMPAIGNS
CREATE TABLE IF NOT EXISTS public.campaigns (
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
CREATE TABLE IF NOT EXISTS public.campaign_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- TRACKING_LINKS (avec unique_code)
CREATE TABLE IF NOT EXISTS public.tracking_links (
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
CREATE TABLE IF NOT EXISTS public.trackable_links (
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
CREATE TABLE IF NOT EXISTS public.conversions (
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
CREATE TABLE IF NOT EXISTS public.sales (
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
CREATE TABLE IF NOT EXISTS public.commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    sale_id UUID REFERENCES public.sales(id),
    amount DECIMAL(12,2) NOT NULL,
    status TEXT CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')) DEFAULT 'pending',
    payout_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INVITATIONS
CREATE TABLE IF NOT EXISTS public.invitations (
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
CREATE TABLE IF NOT EXISTS public.leads (
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
CREATE TABLE IF NOT EXISTS public.affiliation_requests (
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
-- CRÉER LES INDEX
-- ============================================

CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON public.merchants(user_id);
CREATE INDEX IF NOT EXISTS idx_influencers_user_id ON public.influencers(user_id);
CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON public.products(merchant_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);
CREATE INDEX IF NOT EXISTS idx_services_merchant_id ON public.services(merchant_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_merchant_id ON public.campaigns(merchant_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON public.campaigns(status);
CREATE INDEX IF NOT EXISTS idx_tracking_links_influencer ON public.tracking_links(influencer_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_merchant ON public.tracking_links(merchant_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_code ON public.tracking_links(unique_code);
CREATE INDEX IF NOT EXISTS idx_conversions_influencer ON public.conversions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_conversions_status ON public.conversions(status);
CREATE INDEX IF NOT EXISTS idx_sales_merchant ON public.sales(merchant_id);
CREATE INDEX IF NOT EXISTS idx_sales_influencer ON public.sales(influencer_id);
CREATE INDEX IF NOT EXISTS idx_leads_merchant ON public.leads(merchant_id);
CREATE INDEX IF NOT EXISTS idx_leads_influencer ON public.leads(influencer_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON public.leads(status);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_influencer ON public.affiliation_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_merchant ON public.affiliation_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_status ON public.affiliation_requests(status);

-- ============================================
-- ACTIVER RLS
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

-- Politique admin
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN VALUES ('merchants'), ('influencers'), ('products'), ('services'), ('campaigns'),
                    ('tracking_links'), ('trackable_links'), ('conversions'), ('sales'),
                    ('commissions'), ('invitations'), ('leads'), ('affiliation_requests')
    LOOP
        BEGIN
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
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Erreur politique pour %: %', t, SQLERRM;
        END;
    END LOOP;
END $$;

-- Réactiver RLS
SET session_replication_role = DEFAULT;

-- ============================================
-- VÉRIFICATION
-- ============================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM pg_tables 
    WHERE schemaname = 'public' 
    AND tablename IN (
        'merchants', 'influencers', 'products', 'services', 'campaigns',
        'tracking_links', 'trackable_links', 'conversions', 'sales',
        'commissions', 'invitations', 'leads', 'affiliation_requests'
    );
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'CRÉATION TERMINÉE!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables créées: % / 13', table_count;
    
    IF table_count = 13 THEN
        RAISE NOTICE 'SUCCÈS! Toutes les tables sont créées.';
        RAISE NOTICE 'Vous pouvez maintenant exécuter CREATE_ALL_TABLES_COMPLETE.sql';
    ELSE
        RAISE NOTICE 'ATTENTION: Seulement % tables créées sur 13', table_count;
    END IF;
    
    RAISE NOTICE '========================================';
END $$;
