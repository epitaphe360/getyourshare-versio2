-- ============================================
-- SCRIPT DE VÉRIFICATION : COMPTAGE DES DONNÉES DANS TOUTES LES TABLES
-- ============================================
-- Exécute ce script pour voir combien d'enregistrements il y a dans chaque table
-- ============================================

-- Tables principales utilisateurs
SELECT 'users' as table_name, COUNT(*) as total_rows FROM public.users
UNION ALL
SELECT 'merchants', COUNT(*) FROM public.merchants
UNION ALL
SELECT 'influencers', COUNT(*) FROM public.influencers

-- Produits et services
UNION ALL
SELECT 'products', COUNT(*) FROM public.products
UNION ALL
SELECT 'services', COUNT(*) FROM public.services
UNION ALL
SELECT 'product_categories', COUNT(*) FROM public.product_categories

-- Campagnes et tracking
UNION ALL
SELECT 'campaigns', COUNT(*) FROM public.campaigns
UNION ALL
SELECT 'campaign_products', COUNT(*) FROM public.campaign_products
UNION ALL
SELECT 'tracking_links', COUNT(*) FROM public.tracking_links

-- Conversions et ventes
UNION ALL
SELECT 'conversions', COUNT(*) FROM public.conversions
UNION ALL
SELECT 'sales', COUNT(*) FROM public.sales
UNION ALL
SELECT 'commissions', COUNT(*) FROM public.commissions
UNION ALL
SELECT 'payouts', COUNT(*) FROM public.payouts

-- Invitations et collaborations
UNION ALL
SELECT 'invitations', COUNT(*) FROM public.invitations
UNION ALL
SELECT 'collaboration_requests', COUNT(*) FROM public.collaboration_requests

-- Demandes d'affiliation
UNION ALL
SELECT 'affiliation_requests', COUNT(*) FROM public.affiliation_requests

-- Social media
UNION ALL
SELECT 'social_connections', COUNT(*) FROM public.social_connections
UNION ALL
SELECT 'social_media_stats', COUNT(*) FROM public.social_media_stats

-- Reviews
UNION ALL
SELECT 'reviews', COUNT(*) FROM public.reviews
UNION ALL
SELECT 'product_reviews', COUNT(*) FROM public.product_reviews

-- Messaging
UNION ALL
SELECT 'conversations', COUNT(*) FROM public.conversations
UNION ALL
SELECT 'messages', COUNT(*) FROM public.messages
UNION ALL
SELECT 'notifications', COUNT(*) FROM public.notifications

-- Gamification
UNION ALL
SELECT 'user_gamification', COUNT(*) FROM public.user_gamification
UNION ALL
SELECT 'badges', COUNT(*) FROM public.badges
UNION ALL
SELECT 'missions', COUNT(*) FROM public.missions
UNION ALL
SELECT 'user_missions', COUNT(*) FROM public.user_missions

-- Paiements et transactions
UNION ALL
SELECT 'gateway_transactions', COUNT(*) FROM public.gateway_transactions
UNION ALL
SELECT 'invoices', COUNT(*) FROM public.invoices
UNION ALL
SELECT 'deposit_transactions', COUNT(*) FROM public.deposit_transactions
UNION ALL
SELECT 'merchant_deposits', COUNT(*) FROM public.merchant_deposits

-- Leads
UNION ALL
SELECT 'leads', COUNT(*) FROM public.leads

-- Webhooks et logs
UNION ALL
SELECT 'webhook_logs', COUNT(*) FROM public.webhook_logs

-- Abonnements
UNION ALL
SELECT 'subscription_plans', COUNT(*) FROM public.subscription_plans
UNION ALL
SELECT 'subscriptions', COUNT(*) FROM public.subscriptions

ORDER BY table_name;

-- ============================================
-- RÉSUMÉ PAR CATÉGORIE
-- ============================================
SELECT 
    '=== RÉSUMÉ GLOBAL ===' as categorie,
    '' as details;

SELECT 
    'UTILISATEURS' as categorie,
    CONCAT(
        (SELECT COUNT(*) FROM public.users), ' users | ',
        (SELECT COUNT(*) FROM public.users WHERE role = 'merchant'), ' merchants | ',
        (SELECT COUNT(*) FROM public.users WHERE role = 'influencer'), ' influencers | ',
        (SELECT COUNT(*) FROM public.users WHERE role = 'commercial'), ' commercials'
    ) as details
UNION ALL
SELECT 
    'PRODUITS & SERVICES',
    CONCAT(
        (SELECT COUNT(*) FROM public.products), ' produits | ',
        (SELECT COUNT(*) FROM public.services), ' services | ',
        (SELECT COUNT(*) FROM public.campaigns), ' campagnes'
    )
UNION ALL
SELECT 
    'VENTES & COMMISSIONS',
    CONCAT(
        (SELECT COUNT(*) FROM public.sales), ' ventes | ',
        (SELECT COUNT(*) FROM public.commissions), ' commissions | ',
        (SELECT COUNT(*) FROM public.payouts), ' paiements | ',
        (SELECT COUNT(*) FROM public.conversions), ' conversions'
    )
UNION ALL
SELECT 
    'LEADS & COMMERCIAUX',
    CONCAT(
        (SELECT COUNT(*) FROM public.leads), ' leads | ',
        (SELECT COUNT(*) FROM public.leads WHERE commercial_id = '44444444-4444-4444-4444-444444444444'), ' leads Lucas | ',
        (SELECT COUNT(*) FROM public.leads WHERE commercial_id = '44444444-4444-4444-4444-444444444445'), ' leads Claire | ',
        (SELECT COUNT(*) FROM public.leads WHERE commercial_id = '44444444-4444-4444-4444-444444444446'), ' leads David'
    )
UNION ALL
SELECT 
    'SOCIAL MEDIA',
    CONCAT(
        (SELECT COUNT(*) FROM public.social_connections), ' connexions | ',
        (SELECT COUNT(*) FROM public.social_media_stats), ' stats'
    )
UNION ALL
SELECT 
    'MESSAGING',
    CONCAT(
        (SELECT COUNT(*) FROM public.conversations), ' conversations | ',
        (SELECT COUNT(*) FROM public.messages), ' messages | ',
        (SELECT COUNT(*) FROM public.notifications), ' notifications'
    )
UNION ALL
SELECT 
    'GAMIFICATION',
    CONCAT(
        (SELECT COUNT(*) FROM public.user_gamification), ' users gamifiés | ',
        (SELECT COUNT(*) FROM public.badges), ' badges | ',
        (SELECT COUNT(*) FROM public.missions), ' missions | ',
        (SELECT COUNT(*) FROM public.user_missions), ' missions utilisateurs'
    )
UNION ALL
SELECT 
    'REVIEWS',
    CONCAT(
        (SELECT COUNT(*) FROM public.reviews), ' avis reviews | ',
        (SELECT COUNT(*) FROM public.product_reviews), ' avis produits'
    )
UNION ALL
SELECT 
    'TRANSACTIONS',
    CONCAT(
        (SELECT COUNT(*) FROM public.gateway_transactions), ' gateway | ',
        (SELECT COUNT(*) FROM public.deposit_transactions), ' deposits | ',
        (SELECT COUNT(*) FROM public.invoices), ' factures'
    );

-- ============================================
-- VÉRIFICATION DES COMMERCIAUX
-- ============================================
SELECT 
    '=== DÉTAILS COMMERCIAUX ===' as info,
    '' as valeur;

SELECT 
    u.full_name as commercial,
    u.email,
    COUNT(l.id) as nombre_leads,
    COUNT(CASE WHEN l.status = 'pending' THEN 1 END) as pending,
    COUNT(CASE WHEN l.status = 'contacted' THEN 1 END) as contacted,
    COUNT(CASE WHEN l.status = 'qualified' THEN 1 END) as qualified,
    COUNT(CASE WHEN l.status = 'converted' THEN 1 END) as converted
FROM public.users u
LEFT JOIN public.leads l ON u.id = l.commercial_id
WHERE u.role = 'commercial'
GROUP BY u.id, u.full_name, u.email
ORDER BY u.full_name;

-- ============================================
-- VÉRIFICATION DES INFLUENCEURS
-- ============================================
SELECT 
    '=== DÉTAILS INFLUENCEURS ===' as info,
    '' as valeur;

SELECT 
    u.full_name as influenceur,
    u.email,
    COUNT(DISTINCT sc.id) as connexions_sociales,
    SUM(sc.followers_count) as total_followers,
    COUNT(DISTINCT s.id) as ventes,
    COALESCE(SUM(c.amount), 0) as total_commissions
FROM public.users u
LEFT JOIN public.social_connections sc ON u.id = sc.influencer_id
LEFT JOIN public.sales s ON u.id = s.influencer_id
LEFT JOIN public.commissions c ON s.id = c.sale_id
WHERE u.role = 'influencer'
GROUP BY u.id, u.full_name, u.email
ORDER BY u.full_name;

-- ============================================
-- VÉRIFICATION DES MARCHANDS
-- ============================================
SELECT 
    '=== DÉTAILS MARCHANDS ===' as info,
    '' as valeur;

SELECT 
    u.full_name as marchand,
    u.email,
    COUNT(DISTINCT p.id) as produits,
    COUNT(DISTINCT s.id) as services,
    COUNT(DISTINCT c.id) as campagnes,
    COUNT(DISTINCT sa.id) as ventes
FROM public.users u
LEFT JOIN public.products p ON u.id = p.merchant_id
LEFT JOIN public.services s ON u.id = s.merchant_id
LEFT JOIN public.campaigns c ON u.id = c.merchant_id
LEFT JOIN public.sales sa ON u.id = sa.merchant_id
WHERE u.role = 'merchant'
GROUP BY u.id, u.full_name, u.email
ORDER BY u.full_name;

-- ============================================
-- FIN DU SCRIPT DE VÉRIFICATION
-- ============================================
