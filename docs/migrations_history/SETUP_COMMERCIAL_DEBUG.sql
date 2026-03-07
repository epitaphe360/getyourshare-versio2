-- =====================================================
-- SCRIPT DEBUG - EXÉCUTION PAS À PAS
-- =====================================================
-- Exécutez chaque section séparément pour identifier le problème

-- =====================================================
-- ÉTAPE 1: Vérifier que la table users existe et voir ses colonnes
-- =====================================================
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'users'
ORDER BY ordinal_position;

-- =====================================================
-- ÉTAPE 2: Ajouter colonne subscription_tier
-- =====================================================
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'subscription_tier'
    ) THEN
        ALTER TABLE public.users ADD COLUMN subscription_tier TEXT DEFAULT 'starter';
        ALTER TABLE public.users ADD CONSTRAINT check_subscription_tier 
        CHECK (subscription_tier IN ('starter', 'pro', 'enterprise'));
        RAISE NOTICE 'Colonne subscription_tier ajoutée';
    ELSE
        RAISE NOTICE 'Colonne subscription_tier existe déjà';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE 'Contrainte existe déjà';
    WHEN others THEN
        RAISE NOTICE 'Erreur: %', SQLERRM;
END $$;

-- =====================================================
-- ÉTAPE 3: Créer les 5 tables commerciales
-- =====================================================

-- Table 1: commercial_leads
DROP TABLE IF EXISTS public.commercial_leads CASCADE;
CREATE TABLE public.commercial_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    company TEXT,
    status TEXT DEFAULT 'nouveau',
    temperature TEXT DEFAULT 'froid',
    source TEXT,
    estimated_value NUMERIC(12,2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table 2: commercial_tracking_links
DROP TABLE IF EXISTS public.commercial_tracking_links CASCADE;
CREATE TABLE public.commercial_tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    product_id UUID,
    link_code TEXT UNIQUE NOT NULL,
    full_url TEXT NOT NULL,
    channel TEXT,
    campaign_name TEXT,
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    total_revenue NUMERIC(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table 3: commercial_templates
DROP TABLE IF EXISTS public.commercial_templates CASCADE;
CREATE TABLE public.commercial_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    template_type TEXT NOT NULL,
    content TEXT NOT NULL,
    subscription_tier TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table 4: commercial_stats
DROP TABLE IF EXISTS public.commercial_stats CASCADE;
CREATE TABLE public.commercial_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    period TEXT NOT NULL,
    period_date DATE NOT NULL,
    leads_generated INTEGER DEFAULT 0,
    leads_qualified INTEGER DEFAULT 0,
    leads_converted INTEGER DEFAULT 0,
    total_revenue NUMERIC(12,2) DEFAULT 0,
    total_commission NUMERIC(12,2) DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    pipeline_value NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, period, period_date)
);

-- Table 5: sales_representatives
DROP TABLE IF EXISTS public.sales_representatives CASCADE;
CREATE TABLE public.sales_representatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    territory TEXT,
    commission_rate NUMERIC(5,2) DEFAULT 5.00,
    target_monthly_deals INTEGER DEFAULT 20,
    target_monthly_revenue NUMERIC(12,2) DEFAULT 100000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT 'Tables créées avec succès' as status;

-- =====================================================
-- ÉTAPE 4: Insérer 3 utilisateurs commerciaux
-- =====================================================

-- D'abord, vérifier si la colonne email existe bien
SELECT 'Vérification colonne email' as etape;
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'email';

-- Insérer utilisateur STARTER
INSERT INTO public.users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.starter@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K',
    'commercial',
    'starter',
    NOW()
) 
ON CONFLICT (email) DO UPDATE 
SET subscription_tier = EXCLUDED.subscription_tier,
    role = EXCLUDED.role;

-- Insérer utilisateur PRO
INSERT INTO public.users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.pro@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K',
    'commercial',
    'pro',
    NOW()
)
ON CONFLICT (email) DO UPDATE 
SET subscription_tier = EXCLUDED.subscription_tier,
    role = EXCLUDED.role;

-- Insérer utilisateur ENTERPRISE
INSERT INTO public.users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.enterprise@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K',
    'commercial',
    'enterprise',
    NOW()
)
ON CONFLICT (email) DO UPDATE 
SET subscription_tier = EXCLUDED.subscription_tier,
    role = EXCLUDED.role;

-- Vérifier insertion
SELECT email, role, subscription_tier 
FROM public.users 
WHERE role = 'commercial';

SELECT 'Utilisateurs créés avec succès' as status;
