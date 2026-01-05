-- ============================================
-- VÉRIFICATION DES DONNÉES DE TEST
-- ============================================
-- Exécutez ce script pour vérifier que toutes les données ont bien été insérées

-- 1. COMPTAGE GLOBAL
SELECT 
    '📊 STATISTIQUES GLOBALES' as section,
    '' as details;

SELECT 
    'Users' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE role = 'admin') as admins,
    COUNT(*) FILTER (WHERE role = 'merchant') as merchants,
    COUNT(*) FILTER (WHERE role = 'influencer') as influencers,
    COUNT(*) FILTER (WHERE role = 'commercial') as commercials
FROM users;

SELECT 
    'Campaigns' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'active') as active,
    COUNT(*) FILTER (WHERE status = 'draft') as draft,
    COUNT(*) FILTER (WHERE status = 'completed') as completed
FROM campaigns;

SELECT 
    'Products' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE is_active = true) as active,
    COUNT(*) FILTER (WHERE category = 'Fashion') as fashion,
    COUNT(*) FILTER (WHERE category = 'Electronics') as electronics,
    COUNT(*) FILTER (WHERE category = 'Beauty') as beauty,
    COUNT(*) FILTER (WHERE category = 'Sports') as sports
FROM products;

SELECT 
    'Sales' as table_name,
    COUNT(*) as total,
    COALESCE(SUM(amount), 0) as total_amount,
    COALESCE(SUM(commission_amount), 0) as total_commissions
FROM sales;

SELECT 
    'Commissions' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'paid') as paid,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'approved') as approved,
    COALESCE(SUM(amount), 0) as total_amount
FROM commissions;

SELECT 
    'Leads' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE lead_status = 'converted') as converted,
    COUNT(*) FILTER (WHERE lead_status = 'qualified') as qualified,
    COUNT(*) FILTER (WHERE lead_status = 'contacted') as contacted,
    COUNT(*) FILTER (WHERE lead_status = 'new') as new
FROM leads;

SELECT 
    'Invoices' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'paid') as paid,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    COALESCE(SUM(amount), 0) as total_amount
FROM invoices;

-- 2. DÉTAILS PAR MERCHANT
SELECT 
    '👥 DÉTAILS PAR MERCHANT' as section,
    '' as details;

SELECT 
    u.full_name as merchant,
    u.subscription_plan as plan,
    u.monthly_budget as budget,
    COUNT(DISTINCT c.id) as nb_campaigns,
    COUNT(DISTINCT p.id) as nb_products,
    COUNT(DISTINCT s.id) as nb_sales,
    COALESCE(SUM(s.amount), 0) as total_sales
FROM users u
LEFT JOIN campaigns c ON u.id = c.merchant_id
LEFT JOIN products p ON u.id = p.merchant_id
LEFT JOIN sales s ON u.id = s.merchant_id
WHERE u.role = 'merchant'
GROUP BY u.id, u.full_name, u.subscription_plan, u.monthly_budget
ORDER BY u.subscription_plan DESC, u.full_name;

-- 3. DÉTAILS PAR INFLUENCER
SELECT 
    '🌟 DÉTAILS PAR INFLUENCER' as section,
    '' as details;

SELECT 
    u.full_name as influencer,
    u.instagram_handle,
    u.followers_count,
    u.engagement_rate,
    COUNT(DISTINCT s.id) as nb_sales,
    COUNT(DISTINCT com.id) as nb_commissions,
    COALESCE(SUM(com.amount), 0) as total_earnings,
    COALESCE(SUM(com.amount) FILTER (WHERE com.status = 'paid'), 0) as paid_earnings
FROM users u
LEFT JOIN sales s ON u.id = s.influencer_id
LEFT JOIN commissions com ON u.id = com.influencer_id
WHERE u.role = 'influencer'
GROUP BY u.id, u.full_name, u.instagram_handle, u.followers_count, u.engagement_rate
ORDER BY total_earnings DESC;

-- 4. DÉTAILS PAR COMMERCIAL
SELECT 
    '💼 DÉTAILS PAR COMMERCIAL' as section,
    '' as details;

SELECT 
    u.full_name as commercial,
    COUNT(DISTINCT l.id) as total_leads,
    COUNT(DISTINCT l.id) FILTER (WHERE l.lead_status = 'converted') as converted,
    COUNT(DISTINCT l.id) FILTER (WHERE l.lead_status = 'qualified') as qualified,
    COUNT(DISTINCT l.id) FILTER (WHERE l.lead_status = 'contacted') as contacted,
    COUNT(DISTINCT l.id) FILTER (WHERE l.lead_status = 'new') as new,
    COUNT(DISTINCT l.id) FILTER (WHERE l.lead_status = 'lost') as lost,
    ROUND(AVG(l.score), 1) as avg_score
FROM users u
LEFT JOIN leads l ON u.id = l.commercial_id
WHERE u.role = 'commercial'
GROUP BY u.id, u.full_name
ORDER BY converted DESC, total_leads DESC;

-- 5. VÉRIFICATION DES DONNÉES ATTENDUES
SELECT 
    '✅ VALIDATION DES DONNÉES' as section,
    '' as details;

SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM users WHERE role = 'admin') = 1 THEN '✅'
        ELSE '❌'
    END as admin_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM users WHERE role = 'merchant') = 6 THEN '✅'
        ELSE '❌'
    END as merchants_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM users WHERE role = 'influencer') = 7 THEN '✅'
        ELSE '❌'
    END as influencers_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM users WHERE role = 'commercial') = 6 THEN '✅'
        ELSE '❌'
    END as commercials_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM campaigns) >= 15 THEN '✅'
        ELSE '❌'
    END as campaigns_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM products) >= 30 THEN '✅'
        ELSE '❌'
    END as products_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM sales) >= 3 THEN '✅'
        ELSE '❌'
    END as sales_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM commissions) >= 19 THEN '✅'
        ELSE '❌'
    END as commissions_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM leads) >= 13 THEN '✅'
        ELSE '❌'
    END as leads_ok,
    CASE 
        WHEN (SELECT COUNT(*) FROM invoices) >= 12 THEN '✅'
        ELSE '❌'
    END as invoices_ok;

-- 6. LISTE DES IDS DE TEST (pour faciliter le nettoyage ultérieur)
SELECT 
    '🔑 IDS DE TEST INSÉRÉS' as section,
    '' as details;

SELECT 'Admin' as type, id, email, full_name FROM users WHERE role = 'admin' AND id = '11111111-1111-1111-1111-111111111111'
UNION ALL
SELECT 'Merchant', id, email, full_name FROM users WHERE role = 'merchant' AND (id::text LIKE '22222222%' OR id::text LIKE '55555555%')
UNION ALL
SELECT 'Influencer', id, email, full_name FROM users WHERE role = 'influencer' AND (id::text LIKE '33333333%' OR id::text LIKE '66666666%' OR id::text LIKE '77777777%')
UNION ALL
SELECT 'Commercial', id, email, full_name FROM users WHERE role = 'commercial' AND id::text LIKE '44444444%'
ORDER BY type, full_name;
