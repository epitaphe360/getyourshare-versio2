-- ============================================================
-- ROW LEVEL SECURITY (RLS) - GetYourShare
-- Exécuter dans Supabase SQL Editor
-- Protège les données : chaque utilisateur ne voit QUE ses données
-- ============================================================

-- ============================================================
-- HELPER FUNCTION : user_id courant depuis JWT
-- ============================================================
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
  SELECT auth.uid()
$$ LANGUAGE SQL SECURITY DEFINER;

-- ============================================================
-- HELPER : est-ce un admin ?
-- ============================================================
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid()
      AND role IN ('admin', 'super_admin')
  )
$$ LANGUAGE SQL SECURITY DEFINER;

-- ============================================================
-- 1. TABLE: users
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS users_select_own ON users;
DROP POLICY IF EXISTS users_update_own ON users;
DROP POLICY IF EXISTS users_admin_all ON users;

CREATE POLICY users_select_own ON users
  FOR SELECT USING (id = auth.uid() OR is_admin());

CREATE POLICY users_update_own ON users
  FOR UPDATE USING (id = auth.uid() OR is_admin());

CREATE POLICY users_admin_all ON users
  FOR ALL USING (is_admin());

-- ============================================================
-- 2. TABLE: user_settings
-- ============================================================
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS user_settings_own ON user_settings;
CREATE POLICY user_settings_own ON user_settings
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 3. TABLE: merchants
-- ============================================================
ALTER TABLE merchants ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS merchants_select_public ON merchants;
DROP POLICY IF EXISTS merchants_manage_own ON merchants;

CREATE POLICY merchants_select_public ON merchants
  FOR SELECT USING (true);  -- Profils marchands visibles publiquement

CREATE POLICY merchants_manage_own ON merchants
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 4. TABLE: influencers
-- ============================================================
ALTER TABLE influencers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS influencers_select_public ON influencers;
DROP POLICY IF EXISTS influencers_manage_own ON influencers;

CREATE POLICY influencers_select_public ON influencers
  FOR SELECT USING (true);

CREATE POLICY influencers_manage_own ON influencers
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 5. TABLE: products
-- ============================================================
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS products_select_active ON products;
DROP POLICY IF EXISTS products_manage_merchant ON products;

CREATE POLICY products_select_active ON products
  FOR SELECT USING (is_active = true OR merchant_id IN (
    SELECT id FROM merchants WHERE user_id = auth.uid()
  ) OR is_admin());

CREATE POLICY products_manage_merchant ON products
  FOR ALL USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );

-- ============================================================
-- 6. TABLE: campaigns
-- ============================================================
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS campaigns_select ON campaigns;
DROP POLICY IF EXISTS campaigns_manage ON campaigns;

CREATE POLICY campaigns_select ON campaigns
  FOR SELECT USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR status = 'active'
    OR is_admin()
  );

CREATE POLICY campaigns_manage ON campaigns
  FOR ALL USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );

-- ============================================================
-- 7. TABLE: conversions
-- ============================================================
ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS conversions_own ON conversions;

CREATE POLICY conversions_own ON conversions
  FOR SELECT USING (
    influencer_id = auth.uid()
    OR merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR commercial_id = auth.uid()
    OR is_admin()
  );

CREATE POLICY conversions_create ON conversions
  FOR INSERT WITH CHECK (influencer_id = auth.uid() OR is_admin());

CREATE POLICY conversions_admin_update ON conversions
  FOR UPDATE USING (is_admin());

-- ============================================================
-- 8. TABLE: tracking_links
-- ============================================================
ALTER TABLE tracking_links ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tracking_links_own ON tracking_links;

CREATE POLICY tracking_links_own ON tracking_links
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 9. TABLE: tracking_events
-- ============================================================
ALTER TABLE tracking_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tracking_events_own ON tracking_events;

CREATE POLICY tracking_events_own ON tracking_events
  FOR SELECT USING (
    user_id = auth.uid()
    OR is_admin()
  );

CREATE POLICY tracking_events_insert_all ON tracking_events
  FOR INSERT WITH CHECK (true);  -- Tout le monde peut créer des événements (clics publics)

-- ============================================================
-- 10. TABLE: notifications
-- ============================================================
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS notifications_own ON notifications;

CREATE POLICY notifications_own ON notifications
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 11. TABLE: affiliate_requests
-- ============================================================
ALTER TABLE affiliate_requests ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS affiliate_requests_own ON affiliate_requests;

CREATE POLICY affiliate_requests_own ON affiliate_requests
  FOR SELECT USING (
    influencer_id = auth.uid()
    OR merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );

CREATE POLICY affiliate_requests_create ON affiliate_requests
  FOR INSERT WITH CHECK (influencer_id = auth.uid());

CREATE POLICY affiliate_requests_update ON affiliate_requests
  FOR UPDATE USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );

-- ============================================================
-- 12. TABLE: invoices
-- ============================================================
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS invoices_own ON invoices;

CREATE POLICY invoices_own ON invoices
  FOR SELECT USING (user_id = auth.uid() OR is_admin());

CREATE POLICY invoices_admin_manage ON invoices
  FOR ALL USING (is_admin());

-- ============================================================
-- 13. TABLE: payouts
-- ============================================================
ALTER TABLE payouts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS payouts_own ON payouts;

CREATE POLICY payouts_own ON payouts
  FOR SELECT USING (user_id = auth.uid() OR is_admin());

CREATE POLICY payouts_create_own ON payouts
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY payouts_admin_manage ON payouts
  FOR UPDATE USING (is_admin());

-- ============================================================
-- 14. TABLE: sales_leads
-- ============================================================
ALTER TABLE sales_leads ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS sales_leads_own ON sales_leads;

CREATE POLICY sales_leads_own ON sales_leads
  FOR ALL USING (
    commercial_id = auth.uid()
    OR merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );

-- ============================================================
-- 15. TABLE: conversations
-- ============================================================
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS conversations_participants ON conversations;

CREATE POLICY conversations_participants ON conversations
  FOR ALL USING (
    participant1_id = auth.uid()
    OR participant2_id = auth.uid()
    OR is_admin()
  );

-- ============================================================
-- 16. TABLE: messages
-- ============================================================
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS messages_participants ON messages;

CREATE POLICY messages_participants ON messages
  FOR SELECT USING (
    conversation_id IN (
      SELECT id FROM conversations
      WHERE participant1_id = auth.uid()
         OR participant2_id = auth.uid()
    ) OR is_admin()
  );

CREATE POLICY messages_create ON messages
  FOR INSERT WITH CHECK (sender_id = auth.uid());

-- ============================================================
-- 17. TABLE: api_keys
-- ============================================================
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS api_keys_own ON api_keys;

CREATE POLICY api_keys_own ON api_keys
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 18. TABLE: bot_conversations
-- ============================================================
ALTER TABLE bot_conversations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS bot_conversations_own ON bot_conversations;

CREATE POLICY bot_conversations_own ON bot_conversations
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 19. TABLE: bot_feedback
-- ============================================================
ALTER TABLE bot_feedback ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS bot_feedback_own ON bot_feedback;

CREATE POLICY bot_feedback_own ON bot_feedback
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 20. TABLE: import_jobs
-- ============================================================
ALTER TABLE import_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS import_jobs_own ON import_jobs;

CREATE POLICY import_jobs_own ON import_jobs
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 21. TABLE: push_subscriptions
-- ============================================================
ALTER TABLE push_subscriptions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS push_subscriptions_own ON push_subscriptions;

CREATE POLICY push_subscriptions_own ON push_subscriptions
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 22. TABLE: fiscal_email_settings
-- ============================================================
ALTER TABLE fiscal_email_settings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS fiscal_email_settings_own ON fiscal_email_settings;

CREATE POLICY fiscal_email_settings_own ON fiscal_email_settings
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 23. TABLE: notification_preferences
-- ============================================================
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS notification_preferences_own ON notification_preferences;

CREATE POLICY notification_preferences_own ON notification_preferences
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 24. TABLE: product_reviews
-- ============================================================
ALTER TABLE product_reviews ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS product_reviews_select ON product_reviews;
DROP POLICY IF EXISTS product_reviews_create ON product_reviews;
DROP POLICY IF EXISTS product_reviews_admin ON product_reviews;

CREATE POLICY product_reviews_select ON product_reviews
  FOR SELECT USING (status = 'approved' OR user_id = auth.uid() OR is_admin());

CREATE POLICY product_reviews_create ON product_reviews
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY product_reviews_admin ON product_reviews
  FOR UPDATE USING (is_admin());

-- ============================================================
-- 25. TABLE: media_platforms
-- ============================================================
ALTER TABLE media_platforms ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS media_platforms_own ON media_platforms;

CREATE POLICY media_platforms_own ON media_platforms
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 26. TABLE: media_templates
-- ============================================================
ALTER TABLE media_templates ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS media_templates_own ON media_templates;
DROP POLICY IF EXISTS media_templates_public ON media_templates;

CREATE POLICY media_templates_own ON media_templates
  FOR ALL USING (user_id = auth.uid() OR is_admin());

CREATE POLICY media_templates_public_select ON media_templates
  FOR SELECT USING (is_public = true);

-- ============================================================
-- 27. TABLE: media_generated_content
-- ============================================================
ALTER TABLE media_generated_content ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS media_generated_content_own ON media_generated_content;

CREATE POLICY media_generated_content_own ON media_generated_content
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 28. TABLE: media_scheduled_posts
-- ============================================================
ALTER TABLE media_scheduled_posts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS media_scheduled_posts_own ON media_scheduled_posts;

CREATE POLICY media_scheduled_posts_own ON media_scheduled_posts
  FOR ALL USING (user_id = auth.uid() OR is_admin());

-- ============================================================
-- 29. TABLE: subscriptions
-- ============================================================
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS subscriptions_own ON subscriptions;

CREATE POLICY subscriptions_own ON subscriptions
  FOR SELECT USING (user_id = auth.uid() OR is_admin());

CREATE POLICY subscriptions_admin_manage ON subscriptions
  FOR ALL USING (is_admin());

-- ============================================================
-- 30. TABLE: subscription_plans (lecture publique)
-- ============================================================
ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS subscription_plans_public ON subscription_plans;

CREATE POLICY subscription_plans_public ON subscription_plans
  FOR SELECT USING (is_active = true OR is_admin());

CREATE POLICY subscription_plans_admin ON subscription_plans
  FOR ALL USING (is_admin());

-- ============================================================
-- 31. TABLE: daily_analytics (admin only)
-- ============================================================
ALTER TABLE daily_analytics ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS daily_analytics_admin ON daily_analytics;

CREATE POLICY daily_analytics_admin ON daily_analytics
  FOR ALL USING (is_admin());

-- ============================================================
-- 32. TABLE: system_jobs (admin only)
-- ============================================================
ALTER TABLE system_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS system_jobs_admin ON system_jobs;

CREATE POLICY system_jobs_admin ON system_jobs
  FOR ALL USING (is_admin());

-- ============================================================
-- GRANT service_role bypass RLS (pour le backend Python)
-- IMPORTANT: Le backend utilise la service_role key qui bypass RLS
-- RLS s'applique uniquement aux appels client (anon/authenticated)
-- ============================================================
-- Note: Supabase service_role key bypasse automatiquement RLS.
-- Aucune action supplémentaire nécessaire pour le backend.

-- ============================================================
-- VÉRIFICATION : lister les tables avec RLS activé
-- ============================================================
SELECT
    schemaname,
    tablename,
    rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
