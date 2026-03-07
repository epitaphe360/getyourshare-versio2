-- ============================================================
-- INDEX DE PERFORMANCE - GetYourShare
-- Corrige les requêtes lentes, élimine les N+1
-- Exécuter dans Supabase SQL Editor
-- ============================================================

-- ============================================================
-- TRACKING EVENTS : table la plus volumineuse (~millions de lignes)
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_tracking_events_user_created
  ON tracking_events(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tracking_events_link_type
  ON tracking_events(tracking_link_id, event_type);

CREATE INDEX IF NOT EXISTS idx_tracking_events_campaign_date
  ON tracking_events(campaign_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tracking_events_type_date
  ON tracking_events(event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tracking_events_device
  ON tracking_events(device_type) WHERE device_type IS NOT NULL;

-- ============================================================
-- TRACKING LINKS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_tracking_links_user_active
  ON tracking_links(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_tracking_links_short_code
  ON tracking_links(short_code);

CREATE INDEX IF NOT EXISTS idx_tracking_links_campaign
  ON tracking_links(campaign_id) WHERE campaign_id IS NOT NULL;

-- ============================================================
-- CONVERSIONS : dashboard principal + paiements
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_conversions_influencer_date
  ON conversions(influencer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversions_merchant_date
  ON conversions(merchant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversions_status_date
  ON conversions(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversions_commercial_date
  ON conversions(commercial_id, created_at DESC) WHERE commercial_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_conversions_paid_at
  ON conversions(paid_at DESC) WHERE paid_at IS NOT NULL;

-- ============================================================
-- NOTIFICATIONS : affichage temps réel
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread
  ON notifications(user_id, is_read, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_type
  ON notifications(type, created_at DESC);

-- ============================================================
-- PRODUCTS : recherche et listing marketplace
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_products_category_active
  ON products(category, is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_products_merchant_active
  ON products(merchant_id, is_active);

CREATE INDEX IF NOT EXISTS idx_products_rating
  ON products(rating DESC) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_products_created
  ON products(created_at DESC);

-- Index pour recherche full-text
CREATE INDEX IF NOT EXISTS idx_products_name_gin
  ON products USING gin(to_tsvector('french', coalesce(name, '') || ' ' || coalesce(description, '')));

-- ============================================================
-- CAMPAIGNS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_campaigns_merchant_status
  ON campaigns(merchant_id, status);

CREATE INDEX IF NOT EXISTS idx_campaigns_status_dates
  ON campaigns(status, start_date, end_date);

-- ============================================================
-- SALES_LEADS : CRM commercial
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_sales_leads_commercial_status
  ON sales_leads(commercial_id, status);

CREATE INDEX IF NOT EXISTS idx_sales_leads_merchant_date
  ON sales_leads(merchant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sales_leads_status_date
  ON sales_leads(status, created_at DESC);

-- ============================================================
-- USERS : lookup rapide
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_users_email
  ON users(email);

CREATE INDEX IF NOT EXISTS idx_users_role_active
  ON users(role, is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_users_username
  ON users(username) WHERE username IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_last_login
  ON users(last_login DESC) WHERE last_login IS NOT NULL;

-- ============================================================
-- MERCHANTS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_merchants_user
  ON merchants(user_id);

CREATE INDEX IF NOT EXISTS idx_merchants_verified
  ON merchants(is_verified) WHERE is_verified = true;

-- ============================================================
-- INFLUENCERS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_influencers_user
  ON influencers(user_id);

CREATE INDEX IF NOT EXISTS idx_influencers_audience
  ON influencers(audience_size DESC) WHERE audience_size IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_influencers_niche
  ON influencers(niche) WHERE niche IS NOT NULL;

-- ============================================================
-- AFFILIATE_REQUESTS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_affiliate_requests_influencer_status
  ON affiliate_requests(influencer_id, status);

CREATE INDEX IF NOT EXISTS idx_affiliate_requests_merchant_status
  ON affiliate_requests(merchant_id, status);

CREATE INDEX IF NOT EXISTS idx_affiliate_requests_created
  ON affiliate_requests(created_at DESC);

-- ============================================================
-- INVOICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_invoices_user_date
  ON invoices(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_invoices_status
  ON invoices(status, created_at DESC);

-- ============================================================
-- PAYOUTS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_payouts_user_status
  ON payouts(user_id, status);

CREATE INDEX IF NOT EXISTS idx_payouts_created
  ON payouts(created_at DESC);

-- ============================================================
-- SUBSCRIPTIONS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status
  ON subscriptions(user_id, status);

CREATE INDEX IF NOT EXISTS idx_subscriptions_expires
  ON subscriptions(expires_at) WHERE status = 'active';

-- ============================================================
-- CONVERSATIONS + MESSAGES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_conversations_participants
  ON conversations(participant1_id, participant2_id);

CREATE INDEX IF NOT EXISTS idx_conversations_updated
  ON conversations(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_date
  ON messages(conversation_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_sender
  ON messages(sender_id, created_at DESC);

-- ============================================================
-- API_KEYS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_api_keys_key_active
  ON api_keys(key) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_api_keys_user
  ON api_keys(user_id);

-- ============================================================
-- PASSWORD RESET + EMAIL VERIFICATION TOKENS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_password_reset_email
  ON password_reset_tokens(email) WHERE used = false;

CREATE INDEX IF NOT EXISTS idx_email_verification_email
  ON email_verification_tokens(email) WHERE used = false;

-- ============================================================
-- WEBHOOK_LOGS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_webhook_logs_created
  ON webhook_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_webhook_logs_source
  ON webhook_logs(source, created_at DESC);

-- ============================================================
-- VUES MATÉRIALISÉES POUR DASHBOARD ANALYTICS
-- Rafraîchies toutes les heures par Celery
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_conversion_stats AS
SELECT
    DATE(created_at) AS day,
    COUNT(*)         AS total_conversions,
    SUM(amount)      AS total_revenue,
    AVG(amount)      AS avg_amount,
    COUNT(DISTINCT influencer_id) AS active_influencers,
    COUNT(DISTINCT merchant_id)   AS active_merchants
FROM conversions
WHERE created_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(created_at)
ORDER BY day DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_conversion_stats_day
  ON mv_daily_conversion_stats(day);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_products AS
SELECT
    p.id,
    p.name,
    p.merchant_id,
    COUNT(DISTINCT tl.id)    AS link_count,
    COUNT(DISTINCT te.id)    AS click_count,
    COUNT(DISTINCT c.id)     AS conversion_count,
    COALESCE(SUM(c.amount), 0) AS total_revenue
FROM products p
LEFT JOIN tracking_links tl ON tl.product_id = p.id
LEFT JOIN tracking_events te ON te.tracking_link_id = tl.id AND te.event_type = 'click'
LEFT JOIN conversions c ON c.product_id = p.id
WHERE p.is_active = true
GROUP BY p.id, p.name, p.merchant_id
ORDER BY total_revenue DESC
LIMIT 100;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_top_products_id
  ON mv_top_products(id);

-- Fonction pour rafraîchir les vues matérialisées
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_conversion_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_products;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- ANALYSE DES REQUÊTES LENTES (activer pg_stat_statements)
-- ============================================================
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
-- SELECT query, calls, mean_exec_time, total_exec_time
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC LIMIT 20;
