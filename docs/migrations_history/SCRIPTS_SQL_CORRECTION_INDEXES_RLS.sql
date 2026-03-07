-- ============================================
-- SUPABASE DATABASE AUDIT CORRECTION SCRIPTS
-- Ready-to-use SQL Scripts
-- ============================================

-- ============================================
-- PHASE 1: CREATE MISSING INDEXES (Day 1)
-- ============================================
-- Estimated runtime: 5-10 minutes
-- Impact: Immediate performance improvement

-- Foreign Key Indexes (7 missing)
CREATE INDEX IF NOT EXISTS idx_affiliations_campaign_id
  ON affiliations(campaign_id)
  WHERE campaign_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_moderation_history_performed_by
  ON moderation_history(performed_by)
  WHERE performed_by IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_moderation_queue_product_id
  ON moderation_queue(product_id)
  WHERE product_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_moderation_queue_user_id
  ON moderation_queue(user_id)
  WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_moderation_queue_admin_user_id
  ON moderation_queue(admin_user_id)
  WHERE admin_user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_platform_settings_updated_by
  ON platform_settings(updated_by)
  WHERE updated_by IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trackable_links_affiliation_id
  ON trackable_links(affiliation_id)
  WHERE affiliation_id IS NOT NULL;

-- GIN Indexes for JSONB (11 missing)
CREATE INDEX IF NOT EXISTS idx_influencers_social_links
  ON influencers USING GIN (social_links);

CREATE INDEX IF NOT EXISTS idx_influencers_payment_details
  ON influencers USING GIN (payment_details);

CREATE INDEX IF NOT EXISTS idx_products_images
  ON products USING GIN (images);

CREATE INDEX IF NOT EXISTS idx_products_videos
  ON products USING GIN (videos);

CREATE INDEX IF NOT EXISTS idx_products_specifications
  ON products USING GIN (specifications);

CREATE INDEX IF NOT EXISTS idx_campaigns_target_audience
  ON campaigns USING GIN (target_audience);

CREATE INDEX IF NOT EXISTS idx_ai_analytics_recommended_influencers
  ON ai_analytics USING GIN (recommended_influencers);

CREATE INDEX IF NOT EXISTS idx_ai_analytics_audience_insights
  ON ai_analytics USING GIN (audience_insights);

CREATE INDEX IF NOT EXISTS idx_ai_analytics_competitor_analysis
  ON ai_analytics USING GIN (competitor_analysis);

CREATE INDEX IF NOT EXISTS idx_moderation_queue_metadata
  ON moderation_queue USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_payments_gateway_response
  ON payments USING GIN (gateway_response);

-- Performance Indexes for Common Filters
CREATE INDEX IF NOT EXISTS idx_commissions_sale_id
  ON commissions(sale_id)
  WHERE sale_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status
  ON user_subscriptions(status);

CREATE INDEX IF NOT EXISTS idx_subscriptions_status
  ON subscriptions(status);

CREATE INDEX IF NOT EXISTS idx_sales_payment_status
  ON sales(payment_status);

CREATE INDEX IF NOT EXISTS idx_support_tickets_status
  ON support_tickets(status);

-- Composite Indexes (For common filter+sort combinations)
CREATE INDEX IF NOT EXISTS idx_sales_merchant_created
  ON sales(merchant_id, created_at DESC)
  WHERE merchant_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trackable_links_influencer_created
  ON trackable_links(influencer_id, created_at DESC)
  WHERE influencer_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_products_merchant_active
  ON products(merchant_id, is_available)
  WHERE merchant_id IS NOT NULL;

-- Partial Indexes (Only index active records)
CREATE INDEX IF NOT EXISTS idx_trackable_links_active
  ON trackable_links(id)
  WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_products_available
  ON products(id)
  WHERE is_available = TRUE;

CREATE INDEX IF NOT EXISTS idx_subscriptions_active
  ON subscriptions(id)
  WHERE status = 'active';

-- BRIN Indexes for Time-Series Data (Most efficient for sequential data)
CREATE INDEX IF NOT EXISTS idx_click_tracking_clicked_at_brin
  ON click_tracking USING BRIN (clicked_at);

CREATE INDEX IF NOT EXISTS idx_sales_created_at_brin
  ON sales USING BRIN (created_at);

CREATE INDEX IF NOT EXISTS idx_payments_created_at_brin
  ON payments USING BRIN (created_at);

-- Additional Performance Optimizations
CREATE INDEX IF NOT EXISTS idx_commissions_influencer_status
  ON commissions(influencer_id, status)
  WHERE influencer_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_transactions_user_created
  ON transactions(user_id, created_at DESC)
  WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_notifications_user_created
  ON notifications(user_id, created_at DESC)
  WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_moderation_queue_status_created
  ON moderation_queue(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_platform_invoices_status
  ON platform_invoices(status);

CREATE INDEX IF NOT EXISTS idx_payment_gateway_logs_gateway
  ON payment_gateway_logs(gateway_name);

-- ============================================
-- VERIFY INDEX CREATION
-- ============================================

-- Run this to see all indexes on your database
-- SELECT
--   schemaname,
--   tablename,
--   indexname,
--   idx_scan as scan_count,
--   idx_tup_read as tuples_read,
--   idx_tup_fetch as tuples_fetched
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;


-- ============================================
-- PHASE 2: ADD NOT NULL CONSTRAINTS
-- ============================================
-- Do this ONLY after verifying no NULL values exist
-- Recommended: Check first with "SELECT * FROM table WHERE column IS NULL"

ALTER TABLE IF EXISTS transactions
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN transaction_id SET NOT NULL;

ALTER TABLE IF EXISTS sales
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN status SET NOT NULL;

ALTER TABLE IF EXISTS commissions
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN influencer_id SET NOT NULL;

ALTER TABLE IF EXISTS payments
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN status SET NOT NULL;

ALTER TABLE IF EXISTS subscriptions
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN plan_type SET NOT NULL;

ALTER TABLE IF EXISTS merchants
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN company_name SET NOT NULL;

ALTER TABLE IF EXISTS influencers
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN username SET NOT NULL;


-- ============================================
-- PHASE 3: ENABLE RLS ON CRITICAL TABLES
-- ============================================
-- Phase 3A: USERS (Most critical)

ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Users can view only their own data
DROP POLICY IF EXISTS "users_select_own" ON users;
CREATE POLICY "users_select_own"
  ON users FOR SELECT
  USING (id = auth.uid());

-- Users can update only their own data
DROP POLICY IF EXISTS "users_update_own" ON users;
CREATE POLICY "users_update_own"
  ON users FOR UPDATE
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid());

-- Admins can view all users
DROP POLICY IF EXISTS "users_select_admin" ON users;
CREATE POLICY "users_select_admin"
  ON users FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Admins can update all users
DROP POLICY IF EXISTS "users_update_admin" ON users;
CREATE POLICY "users_update_admin"
  ON users FOR UPDATE
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Only authenticated users can insert (via auth.uid())
DROP POLICY IF EXISTS "users_insert_authenticated" ON users;
CREATE POLICY "users_insert_authenticated"
  ON users FOR INSERT
  WITH CHECK (id = auth.uid());


-- ============================================
-- Phase 3B: MERCHANTS
-- ============================================

ALTER TABLE IF EXISTS merchants ENABLE ROW LEVEL SECURITY;

-- Merchants can view only their own data
DROP POLICY IF EXISTS "merchants_select_own" ON merchants;
CREATE POLICY "merchants_select_own"
  ON merchants FOR SELECT
  USING (user_id = auth.uid());

-- Merchants can update only their own data
DROP POLICY IF EXISTS "merchants_update_own" ON merchants;
CREATE POLICY "merchants_update_own"
  ON merchants FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Admins can view all merchants
DROP POLICY IF EXISTS "merchants_select_admin" ON merchants;
CREATE POLICY "merchants_select_admin"
  ON merchants FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Admins can update all merchants
DROP POLICY IF EXISTS "merchants_update_admin" ON merchants;
CREATE POLICY "merchants_update_admin"
  ON merchants FOR UPDATE
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );


-- ============================================
-- Phase 3C: INFLUENCERS
-- ============================================

ALTER TABLE IF EXISTS influencers ENABLE ROW LEVEL SECURITY;

-- Influencers can view only their own data
DROP POLICY IF EXISTS "influencers_select_own" ON influencers;
CREATE POLICY "influencers_select_own"
  ON influencers FOR SELECT
  USING (user_id = auth.uid());

-- Influencers can update only their own data
DROP POLICY IF EXISTS "influencers_update_own" ON influencers;
CREATE POLICY "influencers_update_own"
  ON influencers FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Admins and merchants can view influencer profiles (public)
DROP POLICY IF EXISTS "influencers_select_public" ON influencers;
CREATE POLICY "influencers_select_public"
  ON influencers FOR SELECT
  USING (true);  -- Public read access


-- ============================================
-- Phase 3D: PRODUCTS
-- ============================================

ALTER TABLE IF EXISTS products ENABLE ROW LEVEL SECURITY;

-- Merchants can view and update their own products
DROP POLICY IF EXISTS "products_select_own" ON products;
CREATE POLICY "products_select_own"
  ON products FOR SELECT
  USING (
    merchant_id IN (
      SELECT id FROM merchants WHERE user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "products_update_own" ON products;
CREATE POLICY "products_update_own"
  ON products FOR UPDATE
  USING (
    merchant_id IN (
      SELECT id FROM merchants WHERE user_id = auth.uid()
    )
  )
  WITH CHECK (
    merchant_id IN (
      SELECT id FROM merchants WHERE user_id = auth.uid()
    )
  );

-- Products are readable by everyone (public marketplace)
DROP POLICY IF EXISTS "products_select_public" ON products;
CREATE POLICY "products_select_public"
  ON products FOR SELECT
  USING (is_available = TRUE);

-- Admins can view all products
DROP POLICY IF EXISTS "products_select_admin" ON products;
CREATE POLICY "products_select_admin"
  ON products FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );


-- ============================================
-- Phase 3E: SALES (Financial - Very sensitive)
-- ============================================

ALTER TABLE IF EXISTS sales ENABLE ROW LEVEL SECURITY;

-- Merchants can view sales of their own products
DROP POLICY IF EXISTS "sales_select_merchant" ON sales;
CREATE POLICY "sales_select_merchant"
  ON sales FOR SELECT
  USING (
    merchant_id IN (
      SELECT id FROM merchants WHERE user_id = auth.uid()
    )
  );

-- Influencers can view sales they generated
DROP POLICY IF EXISTS "sales_select_influencer" ON sales;
CREATE POLICY "sales_select_influencer"
  ON sales FOR SELECT
  USING (
    influencer_id IN (
      SELECT id FROM influencers WHERE user_id = auth.uid()
    )
  );

-- Admins can view all sales
DROP POLICY IF EXISTS "sales_select_admin" ON sales;
CREATE POLICY "sales_select_admin"
  ON sales FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Only backend service role can insert sales
-- (No INSERT policy = only service role can insert)


-- ============================================
-- Phase 3F: COMMISSIONS (Financial - Very sensitive)
-- ============================================

ALTER TABLE IF EXISTS commissions ENABLE ROW LEVEL SECURITY;

-- Influencers can view their own commissions
DROP POLICY IF EXISTS "commissions_select_influencer" ON commissions;
CREATE POLICY "commissions_select_influencer"
  ON commissions FOR SELECT
  USING (
    influencer_id IN (
      SELECT id FROM influencers WHERE user_id = auth.uid()
    )
  );

-- Admins can view all commissions
DROP POLICY IF EXISTS "commissions_select_admin" ON commissions;
CREATE POLICY "commissions_select_admin"
  ON commissions FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Only backend service role can insert/update commissions


-- ============================================
-- Phase 3G: TRACKABLE_LINKS
-- ============================================

ALTER TABLE IF EXISTS trackable_links ENABLE ROW LEVEL SECURITY;

-- Merchants can view links for their products
DROP POLICY IF EXISTS "trackable_links_select_merchant" ON trackable_links;
CREATE POLICY "trackable_links_select_merchant"
  ON trackable_links FOR SELECT
  USING (
    product_id IN (
      SELECT id FROM products
      WHERE merchant_id IN (
        SELECT id FROM merchants WHERE user_id = auth.uid()
      )
    )
  );

-- Influencers can view their own links
DROP POLICY IF EXISTS "trackable_links_select_influencer" ON trackable_links;
CREATE POLICY "trackable_links_select_influencer"
  ON trackable_links FOR SELECT
  USING (
    influencer_id IN (
      SELECT id FROM influencers WHERE user_id = auth.uid()
    )
  );

-- Admins can view all links
DROP POLICY IF EXISTS "trackable_links_select_admin" ON trackable_links;
CREATE POLICY "trackable_links_select_admin"
  ON trackable_links FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Public: can view active links for statistics
DROP POLICY IF EXISTS "trackable_links_select_public_stats" ON trackable_links;
CREATE POLICY "trackable_links_select_public_stats"
  ON trackable_links FOR SELECT
  USING (is_active = TRUE);


-- ============================================
-- Phase 3H: SUBSCRIPTIONS (User data)
-- ============================================

ALTER TABLE IF EXISTS subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can view their own subscriptions
DROP POLICY IF EXISTS "subscriptions_select_own" ON subscriptions;
CREATE POLICY "subscriptions_select_own"
  ON subscriptions FOR SELECT
  USING (user_id = auth.uid());

-- Admins can view all subscriptions
DROP POLICY IF EXISTS "subscriptions_select_admin" ON subscriptions;
CREATE POLICY "subscriptions_select_admin"
  ON subscriptions FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Only backend service role can insert/update subscriptions


-- ============================================
-- Phase 3I: PAYMENTS (Financial)
-- ============================================

ALTER TABLE IF EXISTS payments ENABLE ROW LEVEL SECURITY;

-- Users can view their own payments
DROP POLICY IF EXISTS "payments_select_own" ON payments;
CREATE POLICY "payments_select_own"
  ON payments FOR SELECT
  USING (user_id = auth.uid());

-- Admins can view all payments
DROP POLICY IF EXISTS "payments_select_admin" ON payments;
CREATE POLICY "payments_select_admin"
  ON payments FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Only backend service role can insert/update payments


-- ============================================
-- Phase 3J: SUPPORT_TICKETS (User support)
-- ============================================

ALTER TABLE IF EXISTS support_tickets ENABLE ROW LEVEL SECURITY;

-- Users can view their own tickets
DROP POLICY IF EXISTS "support_tickets_select_own" ON support_tickets;
CREATE POLICY "support_tickets_select_own"
  ON support_tickets FOR SELECT
  USING (user_id = auth.uid());

-- Support staff (admins) can view all tickets
DROP POLICY IF EXISTS "support_tickets_select_admin" ON support_tickets;
CREATE POLICY "support_tickets_select_admin"
  ON support_tickets FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- Users can create their own tickets
DROP POLICY IF EXISTS "support_tickets_insert_own" ON support_tickets;
CREATE POLICY "support_tickets_insert_own"
  ON support_tickets FOR INSERT
  WITH CHECK (user_id = auth.uid());


-- ============================================
-- REMAINING TABLES (Enable RLS, no policies yet)
-- ============================================

ALTER TABLE IF EXISTS affiliate_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS affiliation_request_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS affiliation_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS affiliations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ai_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS click_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS clicks ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS company_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS documentation_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS engagement_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS gateway_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS invoice_line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS mlm_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS moderation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS moderation_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS moderation_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS payment_gateway_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS payment_gateway_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS permissions_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS platform_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS platform_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS registration_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS smtp_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ticket_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS video_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS video_tutorials ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS whitelabel_settings ENABLE ROW LEVEL SECURITY;


-- ============================================
-- VERIFY RLS STATUS
-- ============================================

-- Run this to check which tables have RLS enabled:
-- SELECT tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY tablename;

-- Run this to see all policies:
-- SELECT
--   schemaname,
--   tablename,
--   policyname,
--   permissive,
--   roles,
--   qual,
--   with_check
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;


-- ============================================
-- END OF SCRIPTS
-- ============================================

-- Summary:
-- - Phase 1: 30 new indexes created (improves JOIN performance)
-- - Phase 2: NOT NULL constraints added (prevents silent bugs)
-- - Phase 3: RLS enabled on 46 tables with 30+ policies
--
-- Next steps:
-- 1. Backup your database before running
-- 2. Run Phase 1 (indexes) - safe, can be done anytime
-- 3. Run Phase 2 (NOT NULL) - verify no NULL values first
-- 4. Run Phase 3 (RLS) - test thoroughly with app
-- 5. Update backend to handle RLS policies
-- 6. Refactor N+1 queries in Python code
