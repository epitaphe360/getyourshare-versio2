-- View to optimize get_merchants endpoint
-- Aggregates data from users, merchants, sales, products, services, and campaigns
-- Eliminates N+1 query problem in backend/server.py

DROP VIEW IF EXISTS merchants_stats_view;

CREATE OR REPLACE VIEW merchants_stats_view AS
SELECT 
    u.id as user_id,
    m.id as merchant_id,
    u.email,
    u.created_at,
    u.balance,
    m.company_name,
    m.category,
    COALESCE(sales_stats.total_revenue, 0) as total_revenue,
    COALESCE(products_stats.products_count, 0) as products_count,
    COALESCE(services_stats.services_count, 0) as services_count,
    COALESCE(campaigns_stats.campaigns_count, 0) as campaigns_count,
    (COALESCE(products_stats.products_count, 0) + COALESCE(services_stats.services_count, 0)) as total_catalog_items
FROM 
    users u
JOIN 
    merchants m ON u.id = m.user_id
LEFT JOIN 
    (SELECT merchant_id, SUM(amount) as total_revenue FROM sales GROUP BY merchant_id) sales_stats ON m.id = sales_stats.merchant_id
LEFT JOIN 
    (SELECT merchant_id, COUNT(*) as products_count FROM products GROUP BY merchant_id) products_stats ON m.id = products_stats.merchant_id
LEFT JOIN 
    (SELECT merchant_id, COUNT(*) as services_count FROM services GROUP BY merchant_id) services_stats ON m.id = services_stats.merchant_id
LEFT JOIN 
    (SELECT merchant_id, COUNT(*) as campaigns_count FROM campaigns GROUP BY merchant_id) campaigns_stats ON m.id = campaigns_stats.merchant_id
WHERE 
    u.role = 'merchant';
