-- =====================================================
-- INSERTION DONNÉES DE TEST - DASHBOARD COMMERCIAL
-- =====================================================
-- Prérequis: SETUP_COMMERCIAL_DEBUG.sql doit avoir été exécuté avec succès
-- =====================================================

-- =====================================================
-- PARTIE 1: SALES REPRESENTATIVES
-- =====================================================

INSERT INTO public.sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id, 'Ahmed', 'Benali', 'commercial.starter@getyourshare.com',
    '+212 6 12 34 56 78', 'Casablanca', 5.0, 10, 50000, TRUE
FROM public.users u 
WHERE u.email = 'commercial.starter@getyourshare.com'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO public.sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id, 'Fatima', 'Zahra', 'commercial.pro@getyourshare.com',
    '+212 6 23 45 67 89', 'Rabat', 7.5, 20, 150000, TRUE
FROM public.users u 
WHERE u.email = 'commercial.pro@getyourshare.com'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO public.sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id, 'Youssef', 'Alami', 'commercial.enterprise@getyourshare.com',
    '+212 6 34 56 78 90', 'Marrakech', 10.0, 50, 500000, TRUE
FROM public.users u 
WHERE u.email = 'commercial.enterprise@getyourshare.com'
ON CONFLICT (user_id) DO NOTHING;

SELECT '✅ Sales representatives créés' as status;

-- =====================================================
-- PARTIE 2: TEMPLATES (10 templates)
-- =====================================================

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

Cordialement', 'starter'),
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

👉 Commandez maintenant : {link}', 'pro'),
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

SELECT '✅ Templates créés: ' || COUNT(*)::TEXT FROM public.commercial_templates;

-- =====================================================
-- PARTIE 3: LEADS (68 leads: 3 + 15 + 50)
-- =====================================================

-- STARTER: 3 leads manuels
INSERT INTO public.commercial_leads (
    user_id, first_name, last_name, email, phone, company, 
    status, temperature, source, estimated_value, notes
)
SELECT 
    u.id,
    'Mohammed', 'Idrissi', 'mohammed@entreprise1.ma', '+212 6 11 22 33 44',
    'Tech Solutions Maroc', 'nouveau', 'froid', 'linkedin', 15000,
    'Contact initial via LinkedIn'
FROM public.users u 
WHERE u.email = 'commercial.starter@getyourshare.com';

INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    u.id,
    'Amina', 'Benjelloun', 'amina@startup.ma', 'Startup Innovante', 
    'qualifie', 'tiede', 'email', 8000
FROM public.users u 
WHERE u.email = 'commercial.starter@getyourshare.com';

INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    u.id,
    'Hassan', 'Ouazzani', 'hassan@digital.ma', 'Digital Agency',
    'en_negociation', 'chaud', 'referral', 25000
FROM public.users u 
WHERE u.email = 'commercial.starter@getyourshare.com';

-- PRO: 15 leads automatiques
INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    u.id,
    'Client PRO ' || i,
    'Test ' || i,
    'pro' || i || '@company.ma',
    'Company PRO ' || i,
    (ARRAY['nouveau', 'qualifie', 'en_negociation', 'conclu'])[1 + (i % 4)],
    (ARRAY['froid', 'tiede', 'chaud'])[1 + (i % 3)],
    (ARRAY['linkedin', 'email', 'whatsapp', 'referral'])[1 + (i % 4)],
    (random() * 50000 + 5000)::NUMERIC(10,2)
FROM public.users u 
CROSS JOIN generate_series(1, 15) i
WHERE u.email = 'commercial.pro@getyourshare.com';

-- ENTERPRISE: 50 leads automatiques
INSERT INTO public.commercial_leads (user_id, first_name, last_name, email, company, status, temperature, source, estimated_value)
SELECT 
    u.id,
    'Client ENT ' || i,
    'Test ' || i,
    'ent' || i || '@company.ma',
    'Company ENT ' || i,
    (ARRAY['nouveau', 'qualifie', 'en_negociation', 'conclu'])[1 + (i % 4)],
    (ARRAY['froid', 'tiede', 'chaud'])[1 + (i % 3)],
    (ARRAY['linkedin', 'email', 'whatsapp', 'referral', 'event'])[1 + (i % 5)],
    (random() * 100000 + 10000)::NUMERIC(10,2)
FROM public.users u 
CROSS JOIN generate_series(1, 50) i
WHERE u.email = 'commercial.enterprise@getyourshare.com';

SELECT '✅ Leads créés: ' || COUNT(*)::TEXT FROM public.commercial_leads;

-- =====================================================
-- PARTIE 4: TRACKING LINKS (48 links: 3 + 15 + 30)
-- =====================================================

-- STARTER: 3 links
INSERT INTO public.commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, 
    total_clicks, total_conversions, total_revenue
)
SELECT 
    u.id,
    NULL,
    'TRACK-STARTER-' || i,
    'https://getyourshare.com/ref/starter' || i,
    (ARRAY['whatsapp', 'linkedin', 'facebook'])[i],
    'Campagne ' || (ARRAY['WhatsApp', 'LinkedIn', 'Facebook'])[i],
    floor(random() * 50)::int,
    floor(random() * 5)::int,
    (random() * 5000)::NUMERIC(10,2)
FROM public.users u 
CROSS JOIN generate_series(1, 3) i
WHERE u.email = 'commercial.starter@getyourshare.com';

-- PRO: 15 links
INSERT INTO public.commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, 
    total_clicks, total_conversions, total_revenue
)
SELECT 
    u.id,
    NULL,
    'TRACK-PRO-' || i,
    'https://getyourshare.com/ref/pro' || i,
    (ARRAY['whatsapp', 'linkedin', 'facebook', 'email', 'sms'])[1 + (i % 5)],
    'Campagne PRO ' || i,
    floor(random() * 200)::int,
    floor(random() * 20)::int,
    (random() * 15000)::NUMERIC(10,2)
FROM public.users u 
CROSS JOIN generate_series(1, 15) i
WHERE u.email = 'commercial.pro@getyourshare.com';

-- ENTERPRISE: 30 links
INSERT INTO public.commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, 
    total_clicks, total_conversions, total_revenue
)
SELECT 
    u.id,
    NULL,
    'TRACK-ENT-' || i,
    'https://getyourshare.com/ref/ent' || i,
    (ARRAY['whatsapp', 'linkedin', 'facebook', 'email', 'sms'])[1 + (i % 5)],
    'Campagne ENT ' || i,
    floor(random() * 500)::int,
    floor(random() * 50)::int,
    (random() * 50000)::NUMERIC(10,2)
FROM public.users u 
CROSS JOIN generate_series(1, 30) i
WHERE u.email = 'commercial.enterprise@getyourshare.com';

SELECT '✅ Tracking links créés: ' || COUNT(*)::TEXT FROM public.commercial_tracking_links;

-- =====================================================
-- PARTIE 5: STATS (90 records: 30 jours × 3 users)
-- =====================================================

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

SELECT '✅ Stats créés: ' || COUNT(*)::TEXT FROM public.commercial_stats;

-- =====================================================
-- VÉRIFICATION FINALE
-- =====================================================

SELECT 
    'users' as table_name,
    COUNT(*) as count
FROM public.users WHERE role = 'commercial'
UNION ALL
SELECT 'sales_representatives', COUNT(*) FROM public.sales_representatives
UNION ALL
SELECT 'commercial_leads', COUNT(*) FROM public.commercial_leads
UNION ALL
SELECT 'commercial_tracking_links', COUNT(*) FROM public.commercial_tracking_links
UNION ALL
SELECT 'commercial_templates', COUNT(*) FROM public.commercial_templates
UNION ALL
SELECT 'commercial_stats', COUNT(*) FROM public.commercial_stats;

-- Afficher les comptes créés
SELECT 
    u.email,
    u.role,
    u.subscription_tier,
    'Test123!' as password,
    sr.first_name || ' ' || sr.last_name as commercial_name
FROM public.users u
LEFT JOIN public.sales_representatives sr ON sr.user_id = u.id
WHERE u.role = 'commercial'
ORDER BY u.subscription_tier;

-- =====================================================
-- ✅ SETUP TERMINÉ !
-- =====================================================
-- Comptes disponibles:
-- - commercial.starter@getyourshare.com / Test123! (Ahmed Benali)
-- - commercial.pro@getyourshare.com / Test123! (Fatima Zahra)
-- - commercial.enterprise@getyourshare.com / Test123! (Youssef Alami)
-- =====================================================
