-- =====================================================
-- SETUP COMPLET DASHBOARD COMMERCIAL
-- =====================================================
-- Ce script combine:
-- 1. Ajout colonne subscription_tier
-- 2. Création tables commerciales
-- 3. Insertion données de test
-- =====================================================

-- =====================================================
-- PARTIE 1: AJOUTER COLONNE subscription_tier
-- =====================================================

DO $$ 
BEGIN
    -- Ajouter la colonne subscription_tier si elle n'existe pas
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'subscription_tier'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN subscription_tier TEXT DEFAULT 'starter';
        
        -- Ajouter la contrainte CHECK séparément
        ALTER TABLE public.users 
        ADD CONSTRAINT check_subscription_tier 
        CHECK (subscription_tier IN ('starter', 'pro', 'enterprise'));
        
        RAISE NOTICE 'Colonne subscription_tier ajoutée';
    ELSE
        RAISE NOTICE 'Colonne subscription_tier existe déjà';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE 'Contrainte check_subscription_tier existe déjà';
    WHEN others THEN
        RAISE NOTICE 'Colonne subscription_tier déjà présente ou erreur: %', SQLERRM;
END $$;

-- Index
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier 
ON public.users(subscription_tier);

-- Mettre à jour utilisateurs existants
UPDATE public.users 
SET subscription_tier = 'starter' 
WHERE subscription_tier IS NULL;

-- =====================================================
-- PARTIE 2: CRÉER TABLES COMMERCIALES (SIMPLIFIÉES)
-- =====================================================

-- Table: commercial_leads (version simplifiée)
CREATE TABLE IF NOT EXISTS public.commercial_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    company TEXT,
    status TEXT DEFAULT 'nouveau' CHECK (status IN ('nouveau', 'qualifie', 'en_negociation', 'conclu', 'perdu')),
    temperature TEXT DEFAULT 'froid' CHECK (temperature IN ('froid', 'tiede', 'chaud')),
    source TEXT, -- 'linkedin', 'email', 'whatsapp', 'referral', 'event'
    estimated_value NUMERIC(12,2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_commercial_leads_user ON public.commercial_leads(user_id);
CREATE INDEX IF NOT EXISTS idx_commercial_leads_status ON public.commercial_leads(status);

-- Table: commercial_tracking_links
CREATE TABLE IF NOT EXISTS public.commercial_tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,
    link_code TEXT UNIQUE NOT NULL,
    full_url TEXT NOT NULL,
    channel TEXT, -- 'whatsapp', 'linkedin', 'facebook', 'email', 'sms'
    campaign_name TEXT,
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    total_revenue NUMERIC(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracking_links_user ON public.commercial_tracking_links(user_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_code ON public.commercial_tracking_links(link_code);

-- Table: commercial_templates
CREATE TABLE IF NOT EXISTS public.commercial_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    category TEXT NOT NULL, -- 'facebook', 'linkedin', 'whatsapp', 'email', 'sms', 'instagram'
    template_type TEXT NOT NULL, -- 'post', 'message', 'email_body', 'story'
    content TEXT NOT NULL,
    subscription_tier TEXT NOT NULL CHECK (subscription_tier IN ('starter', 'pro', 'enterprise')),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_templates_tier ON public.commercial_templates(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_templates_category ON public.commercial_templates(category);

-- Table: commercial_stats (statistiques agrégées)
CREATE TABLE IF NOT EXISTS public.commercial_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    period TEXT NOT NULL, -- 'daily', 'weekly', 'monthly'
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

CREATE INDEX IF NOT EXISTS idx_stats_user_date ON public.commercial_stats(user_id, period_date DESC);

-- Table: sales_representatives (compatible avec CREATE_COMMERCIAL_TABLES.sql)
CREATE TABLE IF NOT EXISTS public.sales_representatives (
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

CREATE INDEX IF NOT EXISTS idx_sales_reps_user ON public.sales_representatives(user_id);
CREATE INDEX IF NOT EXISTS idx_sales_reps_email ON public.sales_representatives(email);

-- =====================================================
-- PARTIE 3: INSÉRER DONNÉES DE TEST
-- =====================================================

-- 3.1: Créer 3 utilisateurs commerciaux
INSERT INTO public.users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.starter@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K', -- password: Test123!
    'commercial',
    'starter',
    NOW()
) ON CONFLICT (email) DO UPDATE SET subscription_tier = EXCLUDED.subscription_tier;

INSERT INTO public.users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.pro@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K',
    'commercial',
    'pro',
    NOW()
) ON CONFLICT (email) DO UPDATE SET subscription_tier = EXCLUDED.subscription_tier;

INSERT INTO public.users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.enterprise@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K',
    'commercial',
    'enterprise',
    NOW()
) ON CONFLICT (email) DO UPDATE SET subscription_tier = EXCLUDED.subscription_tier;

-- 3.2: Créer profils sales_representatives
INSERT INTO public.sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id, 'Ahmed', 'Benali', 'commercial.starter@getyourshare.com',
    '+212 6 12 34 56 78', 'Casablanca', 5.0, 10, 50000, TRUE
FROM public.users u WHERE u.email = 'commercial.starter@getyourshare.com'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO public.sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id, 'Fatima', 'Zahra', 'commercial.pro@getyourshare.com',
    '+212 6 23 45 67 89', 'Rabat', 7.5, 20, 150000, TRUE
FROM public.users u WHERE u.email = 'commercial.pro@getyourshare.com'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO public.sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id, 'Youssef', 'Alami', 'commercial.enterprise@getyourshare.com',
    '+212 6 34 56 78 90', 'Marrakech', 10.0, 50, 500000, TRUE
FROM public.users u WHERE u.email = 'commercial.enterprise@getyourshare.com'
ON CONFLICT (user_id) DO NOTHING;

-- 3.3: Templates (3 STARTER, 15 PRO, 4 ENTERPRISE)
INSERT INTO public.commercial_templates (title, category, template_type, content, subscription_tier) VALUES
('Post Facebook Simple', 'facebook', 'post', '🔥 Découvrez {product_name} à seulement {price}€ ! 
✨ Profitez de cette offre exclusive maintenant !
👉 Cliquez ici : {link}', 'starter'),
('Message WhatsApp Basique', 'whatsapp', 'message', 'Bonjour ! Je vous présente {product_name}, un produit fantastique à {price}€.
Intéressé(e) ? Répondez-moi pour plus d''infos ! 😊', 'starter'),
('Email Simple', 'email', 'email_body', 'Bonjour,

Je tenais à vous présenter {product_name}.

Prix: {price}€
Commission: {commission}€

Cordialement', 'starter')
ON CONFLICT DO NOTHING;

-- Templates PRO (simplifié - 5 templates au lieu de 15 pour garder le script lisible)
INSERT INTO public.commercial_templates (title, category, template_type, content, subscription_tier) VALUES
('Post LinkedIn Professionnel', 'linkedin', 'post', '🚀 Nouveauté dans mon réseau !

Je suis ravi de partager {product_name} avec vous.

Prix exceptionnel: {price}€

Contactez-moi en MP ! 💼', 'pro'),
('Story Instagram', 'instagram', 'story', '✨ ALERTE NOUVEAUTÉ ✨

{product_name}

Prix: {price}€ 

Swipe up 👆 pour commander !', 'pro'),
('Email de Relance', 'email', 'email_body', 'Bonjour {contact_name},

Je reviens vers vous concernant {product_name}.

Avez-vous eu le temps d''y réfléchir ?

Cordialement,
{sales_rep_name}', 'pro'),
('WhatsApp Business Pro', 'whatsapp', 'message', '👋 Bonjour {contact_name} !

Je vous contacte pour vous présenter {product_name}.

💰 Prix: {price}€

Souhaitez-vous une démonstration ?', 'pro'),
('Post Facebook Promo', 'facebook', 'post', '🎉 OFFRE SPÉCIALE 🎉

{product_name} en PROMOTION !

✅ Prix promo: {price}€

👉 Commandez maintenant : {link}', 'pro')
ON CONFLICT DO NOTHING;

-- Templates ENTERPRISE (2 exemples)
INSERT INTO public.commercial_templates (title, category, template_type, content, subscription_tier) VALUES
('Email Multitouch Séquence', 'email', 'email_body', 'Bonjour {contact_name},

{product_name} permet aux entreprises comme {company_name} de:
• Réduire les coûts de {percentage}%
• ROI en {roi_months} mois

Disponible pour un appel ?

{sales_rep_name}', 'enterprise'),
('Proposition Commerciale', 'email', 'email_body', 'Bonjour {contact_name},

Voici ma proposition:

📦 SOLUTION: {product_name}
💰 INVESTISSEMENT: {price}€ HT
📈 ROI ESTIMÉ: {roi}%

Cordialement,
{sales_rep_name}', 'enterprise')
ON CONFLICT DO NOTHING;

-- 3.4: Leads (3 pour STARTER, 15 pour PRO, 50 pour ENTERPRISE)
INSERT INTO public.commercial_leads (
    user_id, first_name, last_name, email, phone, company, 
    status, temperature, source, estimated_value, notes
)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.starter@getyourshare.com'),
    'Mohammed', 'Idrissi', 'mohammed@entreprise1.ma', '+212 6 11 22 33 44',
    'Tech Solutions Maroc', 'nouveau', 'froid', 'linkedin', 15000,
    'Contact initial via LinkedIn';

INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.starter@getyourshare.com'),
    'Amina', 'Benjelloun', 'amina@startup.ma', 'Startup Innovante', 
    'qualifie', 'tiede', 'email', 8000;

INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.starter@getyourshare.com'),
    'Hassan', 'Ouazzani', 'hassan@digital.ma', 'Digital Agency',
    'en_negociation', 'chaud', 'referral', 25000;

-- Leads pour PRO (15 leads - version simplifiée avec generate_series)
INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.pro@getyourshare.com'),
    'Client PRO ' || i,
    'Test ' || i,
    'pro' || i || '@company.ma',
    'Company PRO ' || i,
    (ARRAY['nouveau', 'qualifie', 'en_negociation', 'conclu'])[1 + (i % 4)],
    (ARRAY['froid', 'tiede', 'chaud'])[1 + (i % 3)],
    (ARRAY['linkedin', 'email', 'whatsapp', 'referral'])[1 + (i % 4)],
    (random() * 50000 + 5000)::NUMERIC(10,2)
FROM generate_series(1, 15) i;

-- Leads pour ENTERPRISE (50 leads)
INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.enterprise@getyourshare.com'),
    'Client ENT ' || i,
    'Test ' || i,
    'ent' || i || '@company.ma',
    'Company ENT ' || i,
    (ARRAY['nouveau', 'qualifie', 'en_negociation', 'conclu'])[1 + (i % 4)],
    (ARRAY['froid', 'tiede', 'chaud'])[1 + (i % 3)],
    (ARRAY['linkedin', 'email', 'whatsapp', 'referral', 'event'])[1 + (i % 5)],
    (random() * 100000 + 10000)::NUMERIC(10,2)
FROM generate_series(1, 50) i;

-- 3.5: Tracking Links (3 pour STARTER, 15 pour PRO, 30 pour ENTERPRISE)
-- Note: Nécessite table products - on utilise NULL pour product_id si elle n'existe pas
INSERT INTO public.commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, total_clicks, total_conversions, total_revenue
)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.starter@getyourshare.com'),
    NULL,
    'TRACK-STARTER-' || generate_series,
    'https://getyourshare.com/ref/starter' || generate_series,
    (ARRAY['whatsapp', 'linkedin', 'facebook'])[generate_series],
    'Campagne ' || (ARRAY['WhatsApp', 'LinkedIn', 'Facebook'])[generate_series],
    floor(random() * 50)::int,
    floor(random() * 5)::int,
    (random() * 5000)::NUMERIC(10,2)
FROM generate_series(1, 3);

INSERT INTO public.commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, total_clicks, total_conversions, total_revenue
)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.pro@getyourshare.com'),
    NULL,
    'TRACK-PRO-' || generate_series,
    'https://getyourshare.com/ref/pro' || generate_series,
    (ARRAY['whatsapp', 'linkedin', 'facebook', 'email', 'sms'])[1 + (generate_series % 5)],
    'Campagne PRO ' || generate_series,
    floor(random() * 200)::int,
    floor(random() * 20)::int,
    (random() * 15000)::NUMERIC(10,2)
FROM generate_series(1, 15);

INSERT INTO public.commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, total_clicks, total_conversions, total_revenue
)
SELECT 
    (SELECT id FROM public.users WHERE email = 'commercial.enterprise@getyourshare.com'),
    NULL,
    'TRACK-ENT-' || generate_series,
    'https://getyourshare.com/ref/ent' || generate_series,
    (ARRAY['whatsapp', 'linkedin', 'facebook', 'email', 'sms'])[1 + (generate_series % 5)],
    'Campagne ENT ' || generate_series,
    floor(random() * 500)::int,
    floor(random() * 50)::int,
    (random() * 50000)::NUMERIC(10,2)
FROM generate_series(1, 30);

-- 3.6: Stats (30 jours pour chaque commercial)
INSERT INTO public.commercial_stats (
    user_id, period, period_date, leads_generated, leads_qualified, leads_converted,
    total_revenue, total_commission, total_clicks, pipeline_value
)
SELECT 
    u.id,
    'daily'::TEXT,
    (CURRENT_DATE - i)::DATE,
    CASE 
        WHEN u.subscription_tier = 'starter' THEN floor(random() * 3)::int
        WHEN u.subscription_tier = 'pro' THEN floor(random() * 10)::int
        ELSE floor(random() * 20)::int
    END,
    CASE 
        WHEN u.subscription_tier = 'starter' THEN floor(random() * 2)::int
        WHEN u.subscription_tier = 'pro' THEN floor(random() * 5)::int
        ELSE floor(random() * 15)::int
    END,
    CASE 
        WHEN u.subscription_tier = 'starter' THEN floor(random() * 1)::int
        WHEN u.subscription_tier = 'pro' THEN floor(random() * 3)::int
        ELSE floor(random() * 8)::int
    END,
    CASE 
        WHEN u.subscription_tier = 'starter' THEN (random() * 5000)::NUMERIC(10,2)
        WHEN u.subscription_tier = 'pro' THEN (random() * 15000)::NUMERIC(10,2)
        ELSE (random() * 50000)::NUMERIC(10,2)
    END,
    CASE 
        WHEN u.subscription_tier = 'starter' THEN (random() * 250)::NUMERIC(10,2)
        WHEN u.subscription_tier = 'pro' THEN (random() * 1125)::NUMERIC(10,2)
        ELSE (random() * 5000)::NUMERIC(10,2)
    END,
    CASE 
        WHEN u.subscription_tier = 'starter' THEN floor(random() * 50)::int
        WHEN u.subscription_tier = 'pro' THEN floor(random() * 200)::int
        ELSE floor(random() * 500)::int
    END,
    CASE 
        WHEN u.subscription_tier = 'starter' THEN (random() * 20000)::NUMERIC(10,2)
        WHEN u.subscription_tier = 'pro' THEN (random() * 75000)::NUMERIC(10,2)
        ELSE (random() * 250000)::NUMERIC(10,2)
    END
FROM public.users u
CROSS JOIN generate_series(0, 29) i
WHERE u.role = 'commercial'
ON CONFLICT (user_id, period, period_date) DO NOTHING;

-- =====================================================
-- VÉRIFICATION FINALE
-- =====================================================

SELECT 
    'users' as table_name,
    COUNT(*) as count
FROM public.users WHERE role = 'commercial'
UNION ALL
SELECT 
    'sales_representatives',
    COUNT(*)
FROM public.sales_representatives
UNION ALL
SELECT 
    'commercial_leads',
    COUNT(*)
FROM public.commercial_leads
UNION ALL
SELECT 
    'commercial_tracking_links',
    COUNT(*)
FROM public.commercial_tracking_links
UNION ALL
SELECT 
    'commercial_templates',
    COUNT(*)
FROM public.commercial_templates
UNION ALL
SELECT 
    'commercial_stats',
    COUNT(*)
FROM public.commercial_stats;

-- Afficher les 3 comptes créés
SELECT 
    u.email,
    u.role,
    u.subscription_tier,
    'Test123!' as password
FROM public.users u
WHERE u.role = 'commercial'
ORDER BY u.subscription_tier;

-- =====================================================
-- ✅ SETUP TERMINÉ !
-- =====================================================
-- Vous pouvez maintenant vous connecter avec:
-- - commercial.starter@getyourshare.com / Test123!
-- - commercial.pro@getyourshare.com / Test123!
-- - commercial.enterprise@getyourshare.com / Test123!
-- =====================================================
