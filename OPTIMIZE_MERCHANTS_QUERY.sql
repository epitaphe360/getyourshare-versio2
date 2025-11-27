-- Optimisation des performances pour le Dashboard Admin
-- Cette vue remplace les requêtes lourdes qui récupèrent toutes les ventes

CREATE OR REPLACE VIEW merchants_stats_view AS
SELECT 
    u.id as user_id,
    u.email,
    u.created_at,
    COALESCE(m.company_name, u.username, 'Inconnu') as company_name,
    COALESCE(m.industry, 'General') as category,
    COALESCE(SUM(s.amount), 0) as total_revenue,
    COUNT(s.id) as sales_count
FROM users u
LEFT JOIN merchants m ON u.id = m.user_id
LEFT JOIN sales s ON u.id = s.merchant_id
WHERE u.role = 'merchant'
GROUP BY u.id, u.email, u.created_at, m.company_name, m.industry;

-- Index pour accélérer les jointures
CREATE INDEX IF NOT EXISTS idx_sales_merchant_id ON sales(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON merchants(user_id);
