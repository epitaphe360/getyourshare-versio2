-- ============================================================
-- ROW LEVEL SECURITY (RLS) - GetYourShare
-- VERSION ROBUSTE : chaque bloc gere ses propres erreurs
-- Toute table/colonne manquante est ignoree silencieusement
-- ============================================================

CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
  SELECT auth.uid()
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid()
      AND role IN ('admin', 'super_admin')
  )
$$ LANGUAGE SQL SECURITY DEFINER;

-- 1. users
DO $$ BEGIN
  ALTER TABLE users ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS users_select_own ON users;
  DROP POLICY IF EXISTS users_update_own ON users;
  DROP POLICY IF EXISTS users_admin_all  ON users;
  CREATE POLICY users_select_own ON users FOR SELECT USING (id = auth.uid() OR is_admin());
  CREATE POLICY users_update_own ON users FOR UPDATE USING (id = auth.uid() OR is_admin());
  CREATE POLICY users_admin_all  ON users FOR ALL    USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'users RLS: %', SQLERRM; END $$;

-- 2. user_settings
DO $$ BEGIN
  ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS user_settings_own ON user_settings;
  CREATE POLICY user_settings_own ON user_settings FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'user_settings RLS: %', SQLERRM; END $$;

-- 3. merchants
DO $$ BEGIN
  ALTER TABLE merchants ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS merchants_select_public ON merchants;
  DROP POLICY IF EXISTS merchants_manage_own    ON merchants;
  CREATE POLICY merchants_select_public ON merchants FOR SELECT USING (true);
  CREATE POLICY merchants_manage_own    ON merchants FOR ALL    USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'merchants RLS: %', SQLERRM; END $$;

-- 4. influencers
DO $$ BEGIN
  ALTER TABLE influencers ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS influencers_select_public ON influencers;
  DROP POLICY IF EXISTS influencers_manage_own    ON influencers;
  CREATE POLICY influencers_select_public ON influencers FOR SELECT USING (true);
  CREATE POLICY influencers_manage_own    ON influencers FOR ALL    USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'influencers RLS: %', SQLERRM; END $$;

-- 5. products
DO $$ BEGIN
  ALTER TABLE products ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS products_select_active   ON products;
  DROP POLICY IF EXISTS products_manage_merchant ON products;
  CREATE POLICY products_select_active ON products FOR SELECT USING (
    is_active = true
    OR merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );
  CREATE POLICY products_manage_merchant ON products FOR ALL USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );
EXCEPTION WHEN others THEN RAISE NOTICE 'products RLS: %', SQLERRM; END $$;

-- 6. campaigns
DO $$ BEGIN
  ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS campaigns_select ON campaigns;
  DROP POLICY IF EXISTS campaigns_manage ON campaigns;
  CREATE POLICY campaigns_select ON campaigns FOR SELECT USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR status = 'active'
    OR is_admin()
  );
  CREATE POLICY campaigns_manage ON campaigns FOR ALL USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );
EXCEPTION WHEN others THEN RAISE NOTICE 'campaigns RLS: %', SQLERRM; END $$;

-- 7. conversions
DO $$ BEGIN
  ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS conversions_own          ON conversions;
  DROP POLICY IF EXISTS conversions_create       ON conversions;
  DROP POLICY IF EXISTS conversions_admin_update ON conversions;
  CREATE POLICY conversions_own ON conversions FOR SELECT USING (
    influencer_id = auth.uid()
    OR merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );
  CREATE POLICY conversions_create       ON conversions FOR INSERT WITH CHECK (influencer_id = auth.uid() OR is_admin());
  CREATE POLICY conversions_admin_update ON conversions FOR UPDATE USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'conversions RLS: %', SQLERRM; END $$;

-- 8. tracking_links (influencer_id)
DO $$ BEGIN
  ALTER TABLE tracking_links ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tracking_links_own ON tracking_links;
  CREATE POLICY tracking_links_own ON tracking_links FOR ALL USING (influencer_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'tracking_links RLS: %', SQLERRM; END $$;

-- 9. tracking_events (via tracking_link)
DO $$ BEGIN
  ALTER TABLE tracking_events ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tracking_events_own        ON tracking_events;
  DROP POLICY IF EXISTS tracking_events_insert_all ON tracking_events;
  CREATE POLICY tracking_events_own ON tracking_events FOR SELECT USING (
    tracking_link_id IN (SELECT id FROM tracking_links WHERE influencer_id = auth.uid())
    OR is_admin()
  );
  CREATE POLICY tracking_events_insert_all ON tracking_events FOR INSERT WITH CHECK (true);
EXCEPTION WHEN others THEN RAISE NOTICE 'tracking_events RLS: %', SQLERRM; END $$;

-- 10. notifications
DO $$ BEGIN
  ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS notifications_own ON notifications;
  CREATE POLICY notifications_own ON notifications FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'notifications RLS: %', SQLERRM; END $$;

-- 11. affiliate_requests
DO $$ BEGIN
  ALTER TABLE affiliate_requests ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS affiliate_requests_own    ON affiliate_requests;
  DROP POLICY IF EXISTS affiliate_requests_create ON affiliate_requests;
  DROP POLICY IF EXISTS affiliate_requests_update ON affiliate_requests;
  CREATE POLICY affiliate_requests_own ON affiliate_requests FOR SELECT USING (
    influencer_id = auth.uid()
    OR merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );
  CREATE POLICY affiliate_requests_create ON affiliate_requests FOR INSERT WITH CHECK (influencer_id = auth.uid());
  CREATE POLICY affiliate_requests_update ON affiliate_requests FOR UPDATE USING (
    merchant_id IN (SELECT id FROM merchants WHERE user_id = auth.uid())
    OR is_admin()
  );
EXCEPTION WHEN others THEN RAISE NOTICE 'affiliate_requests RLS: %', SQLERRM; END $$;

-- 12. invoices
DO $$ BEGIN
  ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS invoices_own          ON invoices;
  DROP POLICY IF EXISTS invoices_admin_manage ON invoices;
  CREATE POLICY invoices_own          ON invoices FOR SELECT USING (user_id = auth.uid() OR is_admin());
  CREATE POLICY invoices_admin_manage ON invoices FOR ALL    USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'invoices RLS: %', SQLERRM; END $$;

-- 13. payouts (influencer_id)
DO $$ BEGIN
  ALTER TABLE payouts ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS payouts_own          ON payouts;
  DROP POLICY IF EXISTS payouts_create_own   ON payouts;
  DROP POLICY IF EXISTS payouts_admin_manage ON payouts;
  CREATE POLICY payouts_own          ON payouts FOR SELECT USING (influencer_id = auth.uid() OR is_admin());
  CREATE POLICY payouts_create_own   ON payouts FOR INSERT WITH CHECK (influencer_id = auth.uid());
  CREATE POLICY payouts_admin_manage ON payouts FOR UPDATE USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'payouts RLS: %', SQLERRM; END $$;

-- 14. sales_leads (sales_rep_id)
DO $$ BEGIN
  ALTER TABLE sales_leads ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS sales_leads_own ON sales_leads;
  CREATE POLICY sales_leads_own ON sales_leads FOR ALL USING (sales_rep_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'sales_leads RLS: %', SQLERRM; END $$;

-- 15. conversations (participant_ids UUID[])
DO $$ BEGIN
  ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS conversations_participants ON conversations;
  CREATE POLICY conversations_participants ON conversations FOR ALL USING (
    auth.uid() = ANY(participant_ids) OR is_admin()
  );
EXCEPTION WHEN others THEN RAISE NOTICE 'conversations RLS: %', SQLERRM; END $$;

-- 16. messages
DO $$ BEGIN
  ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS messages_participants ON messages;
  DROP POLICY IF EXISTS messages_create       ON messages;
  CREATE POLICY messages_participants ON messages FOR SELECT USING (
    conversation_id IN (SELECT id FROM conversations WHERE auth.uid() = ANY(participant_ids))
    OR is_admin()
  );
  CREATE POLICY messages_create ON messages FOR INSERT WITH CHECK (sender_id = auth.uid());
EXCEPTION WHEN others THEN RAISE NOTICE 'messages RLS: %', SQLERRM; END $$;

-- 17. api_keys
DO $$ BEGIN
  ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS api_keys_own ON api_keys;
  CREATE POLICY api_keys_own ON api_keys FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'api_keys RLS: %', SQLERRM; END $$;

-- 18. bot_conversations
DO $$ BEGIN
  ALTER TABLE bot_conversations ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS bot_conversations_own ON bot_conversations;
  CREATE POLICY bot_conversations_own ON bot_conversations FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'bot_conversations RLS: %', SQLERRM; END $$;

-- 19. bot_feedback
DO $$ BEGIN
  ALTER TABLE bot_feedback ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS bot_feedback_own ON bot_feedback;
  CREATE POLICY bot_feedback_own ON bot_feedback FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'bot_feedback RLS: %', SQLERRM; END $$;

-- 20. import_jobs
DO $$ BEGIN
  ALTER TABLE import_jobs ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS import_jobs_own ON import_jobs;
  CREATE POLICY import_jobs_own ON import_jobs FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'import_jobs RLS: %', SQLERRM; END $$;

-- 21. push_subscriptions
DO $$ BEGIN
  ALTER TABLE push_subscriptions ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS push_subscriptions_own ON push_subscriptions;
  CREATE POLICY push_subscriptions_own ON push_subscriptions FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'push_subscriptions RLS: %', SQLERRM; END $$;

-- 22. fiscal_email_settings
DO $$ BEGIN
  ALTER TABLE fiscal_email_settings ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS fiscal_email_settings_own ON fiscal_email_settings;
  CREATE POLICY fiscal_email_settings_own ON fiscal_email_settings FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'fiscal_email_settings RLS: %', SQLERRM; END $$;

-- 23. notification_preferences
DO $$ BEGIN
  ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS notification_preferences_own ON notification_preferences;
  CREATE POLICY notification_preferences_own ON notification_preferences FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'notification_preferences RLS: %', SQLERRM; END $$;

-- 24. product_reviews
DO $$ BEGIN
  ALTER TABLE product_reviews ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS product_reviews_select ON product_reviews;
  DROP POLICY IF EXISTS product_reviews_create ON product_reviews;
  DROP POLICY IF EXISTS product_reviews_admin  ON product_reviews;
  CREATE POLICY product_reviews_select ON product_reviews FOR SELECT USING (status = 'approved' OR user_id = auth.uid() OR is_admin());
  CREATE POLICY product_reviews_create ON product_reviews FOR INSERT WITH CHECK (user_id = auth.uid());
  CREATE POLICY product_reviews_admin  ON product_reviews FOR UPDATE USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'product_reviews RLS: %', SQLERRM; END $$;

-- 25. media_platforms
DO $$ BEGIN
  ALTER TABLE media_platforms ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS media_platforms_own ON media_platforms;
  CREATE POLICY media_platforms_own ON media_platforms FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'media_platforms RLS: %', SQLERRM; END $$;

-- 26. media_templates
DO $$ BEGIN
  ALTER TABLE media_templates ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS media_templates_own           ON media_templates;
  DROP POLICY IF EXISTS media_templates_public        ON media_templates;
  DROP POLICY IF EXISTS media_templates_public_select ON media_templates;
  CREATE POLICY media_templates_own           ON media_templates FOR ALL    USING (user_id = auth.uid() OR is_admin());
  CREATE POLICY media_templates_public_select ON media_templates FOR SELECT USING (is_public = true);
EXCEPTION WHEN others THEN RAISE NOTICE 'media_templates RLS: %', SQLERRM; END $$;

-- 27. media_generated_content
DO $$ BEGIN
  ALTER TABLE media_generated_content ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS media_generated_content_own ON media_generated_content;
  CREATE POLICY media_generated_content_own ON media_generated_content FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'media_generated_content RLS: %', SQLERRM; END $$;

-- 28. media_scheduled_posts
DO $$ BEGIN
  ALTER TABLE media_scheduled_posts ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS media_scheduled_posts_own ON media_scheduled_posts;
  CREATE POLICY media_scheduled_posts_own ON media_scheduled_posts FOR ALL USING (user_id = auth.uid() OR is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'media_scheduled_posts RLS: %', SQLERRM; END $$;

-- 29. subscriptions
DO $$ BEGIN
  ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS subscriptions_own          ON subscriptions;
  DROP POLICY IF EXISTS subscriptions_admin_manage ON subscriptions;
  CREATE POLICY subscriptions_own          ON subscriptions FOR SELECT USING (user_id = auth.uid() OR is_admin());
  CREATE POLICY subscriptions_admin_manage ON subscriptions FOR ALL    USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'subscriptions RLS: %', SQLERRM; END $$;

-- 30. subscription_plans
DO $$ BEGIN
  ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS subscription_plans_public ON subscription_plans;
  DROP POLICY IF EXISTS subscription_plans_admin  ON subscription_plans;
  CREATE POLICY subscription_plans_public ON subscription_plans FOR SELECT USING (is_active = true OR is_admin());
  CREATE POLICY subscription_plans_admin  ON subscription_plans FOR ALL    USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'subscription_plans RLS: %', SQLERRM; END $$;

-- 31. daily_analytics
DO $$ BEGIN
  ALTER TABLE daily_analytics ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS daily_analytics_admin ON daily_analytics;
  CREATE POLICY daily_analytics_admin ON daily_analytics FOR ALL USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'daily_analytics RLS: %', SQLERRM; END $$;

-- 32. system_jobs
DO $$ BEGIN
  ALTER TABLE system_jobs ENABLE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS system_jobs_admin ON system_jobs;
  CREATE POLICY system_jobs_admin ON system_jobs FOR ALL USING (is_admin());
EXCEPTION WHEN others THEN RAISE NOTICE 'system_jobs RLS: %', SQLERRM; END $$;

-- Verification
SELECT tablename, rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
