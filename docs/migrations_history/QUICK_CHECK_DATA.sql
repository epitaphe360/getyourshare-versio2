-- ============================================
-- VÉRIFICATION RAPIDE DES DONNÉES DE TEST
-- ============================================
-- Copie ce script dans Supabase SQL Editor et exécute-le
-- ============================================

-- COMPTAGE RAPIDE PAR TABLE
SELECT 
    'users' as table_name, 
    COUNT(*) as total,
    COUNT(CASE WHEN role = 'admin' THEN 1 END) as admin,
    COUNT(CASE WHEN role = 'merchant' THEN 1 END) as merchants,
    COUNT(CASE WHEN role = 'influencer' THEN 1 END) as influencers,
    COUNT(CASE WHEN role = 'commercial' THEN 1 END) as commercials
FROM public.users;

SELECT 'products' as table_name, COUNT(*) as total FROM public.products;
SELECT 'services' as table_name, COUNT(*) as total FROM public.services;
SELECT 'campaigns' as table_name, COUNT(*) as total FROM public.campaigns;
SELECT 'tracking_links' as table_name, COUNT(*) as total FROM public.tracking_links;

SELECT 'conversions' as table_name, COUNT(*) as total FROM public.conversions;
SELECT 'sales' as table_name, COUNT(*) as total FROM public.sales;
SELECT 'commissions' as table_name, COUNT(*) as total FROM public.commissions;
SELECT 'payouts' as table_name, COUNT(*) as total FROM public.payouts;

SELECT 'leads' as table_name, COUNT(*) as total FROM public.leads;
SELECT 'merchant_deposits' as table_name, COUNT(*) as total FROM public.merchant_deposits;
SELECT 'deposit_transactions' as table_name, COUNT(*) as total FROM public.deposit_transactions;
SELECT 'invoices' as table_name, COUNT(*) as total FROM public.invoices;

SELECT 'social_connections' as table_name, COUNT(*) as total FROM public.social_connections;
SELECT 'social_media_stats' as table_name, COUNT(*) as total FROM public.social_media_stats;
SELECT 'invitations' as table_name, COUNT(*) as total FROM public.invitations;
SELECT 'collaboration_requests' as table_name, COUNT(*) as total FROM public.collaboration_requests;
SELECT 'affiliation_requests' as table_name, COUNT(*) as total FROM public.affiliation_requests;

SELECT 'reviews' as table_name, COUNT(*) as total FROM public.reviews;
SELECT 'product_reviews' as table_name, COUNT(*) as total FROM public.product_reviews;
SELECT 'conversations' as table_name, COUNT(*) as total FROM public.conversations;
SELECT 'messages' as table_name, COUNT(*) as total FROM public.messages;
SELECT 'notifications' as table_name, COUNT(*) as total FROM public.notifications;

SELECT 'user_gamification' as table_name, COUNT(*) as total FROM public.user_gamification;
SELECT 'badges' as table_name, COUNT(*) as total FROM public.badges;
SELECT 'missions' as table_name, COUNT(*) as total FROM public.missions;
SELECT 'user_missions' as table_name, COUNT(*) as total FROM public.user_missions;

SELECT 'gateway_transactions' as table_name, COUNT(*) as total FROM public.gateway_transactions;
SELECT 'webhook_logs' as table_name, COUNT(*) as total FROM public.webhook_logs;

-- ============================================
-- VÉRIFICATION DES COMMERCIAUX ET LEURS LEADS
-- ============================================
SELECT 
    '=== LEADS PAR COMMERCIAL ===' as info;

SELECT 
    u.full_name as commercial,
    u.email,
    COUNT(l.id) as total_leads,
    COUNT(CASE WHEN l.status = 'new' THEN 1 END) as new_leads,
    COUNT(CASE WHEN l.status = 'contacted' THEN 1 END) as contacted,
    COUNT(CASE WHEN l.status = 'qualified' THEN 1 END) as qualified,
    COUNT(CASE WHEN l.status = 'converted' THEN 1 END) as converted
FROM public.users u
LEFT JOIN public.leads l ON u.id = l.commercial_id
WHERE u.role = 'commercial'
GROUP BY u.id, u.full_name, u.email
ORDER BY u.full_name;

-- ============================================
-- RÉSUMÉ FINAL
-- ============================================
SELECT 
    '✅ PART 1: Users' as partie,
    (SELECT COUNT(*) FROM public.users) as total
UNION ALL
SELECT 
    '✅ PART 2: Products/Services/Campaigns',
    (SELECT COUNT(*) FROM public.products) + 
    (SELECT COUNT(*) FROM public.services) + 
    (SELECT COUNT(*) FROM public.campaigns)
UNION ALL
SELECT 
    '✅ PART 3: Sales/Commissions/Leads',
    (SELECT COUNT(*) FROM public.sales) + 
    (SELECT COUNT(*) FROM public.commissions) + 
    (SELECT COUNT(*) FROM public.leads)
UNION ALL
SELECT 
    '✅ PART 4: Social/Messages/Gamification',
    (SELECT COUNT(*) FROM public.social_connections) + 
    (SELECT COUNT(*) FROM public.messages) + 
    (SELECT COUNT(*) FROM public.badges);

SELECT 
    '🎉 BASE DE DONNÉES REMPLIE AVEC SUCCÈS !' as status,
    (SELECT COUNT(*) 
     FROM information_schema.tables 
     WHERE table_schema = 'public' 
     AND table_type = 'BASE TABLE') as total_tables;
