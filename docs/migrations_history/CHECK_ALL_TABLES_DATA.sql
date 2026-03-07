-- ============================================
-- SCRIPT DE VÉRIFICATION DES DONNÉES DANS TOUTES LES TABLES
-- ============================================

-- Vérification des tables principales
SELECT 'users' as table_name, COUNT(*) as row_count FROM public.users
UNION ALL
SELECT 'merchants', COUNT(*) FROM public.merchants
UNION ALL
SELECT 'influencers', COUNT(*) FROM public.influencers
UNION ALL
SELECT 'products', COUNT(*) FROM public.products
UNION ALL
SELECT 'services', COUNT(*) FROM public.services
UNION ALL
SELECT 'product_categories', COUNT(*) FROM public.product_categories
UNION ALL
SELECT 'campaigns', COUNT(*) FROM public.campaigns
UNION ALL
SELECT 'campaign_products', COUNT(*) FROM public.campaign_products
UNION ALL
SELECT 'campaign_settings', COUNT(*) FROM public.campaign_settings
UNION ALL
SELECT 'tracking_links', COUNT(*) FROM public.tracking_links
UNION ALL
SELECT 'trackable_links', COUNT(*) FROM public.trackable_links
UNION ALL
SELECT 'conversions', COUNT(*) FROM public.conversions
UNION ALL
SELECT 'sales', COUNT(*) FROM public.sales
UNION ALL
SELECT 'commissions', COUNT(*) FROM public.commissions
UNION ALL
SELECT 'payouts', COUNT(*) FROM public.payouts
UNION ALL
SELECT 'invitations', COUNT(*) FROM public.invitations
UNION ALL
SELECT 'collaboration_requests', COUNT(*) FROM public.collaboration_requests
UNION ALL
SELECT 'collaboration_invitations', COUNT(*) FROM public.collaboration_invitations
UNION ALL
SELECT 'collaboration_history', COUNT(*) FROM public.collaboration_history
UNION ALL
SELECT 'subscription_plans', COUNT(*) FROM public.subscription_plans
UNION ALL
SELECT 'subscriptions', COUNT(*) FROM public.subscriptions
UNION ALL
SELECT 'subscription_usage', COUNT(*) FROM public.subscription_usage
UNION ALL
SELECT 'subscription_events', COUNT(*) FROM public.subscription_events
UNION ALL
SELECT 'subscription_coupons', COUNT(*) FROM public.subscription_coupons
UNION ALL
SELECT 'invoices', COUNT(*) FROM public.invoices
UNION ALL
SELECT 'platform_invoices', COUNT(*) FROM public.platform_invoices
UNION ALL
SELECT 'invoice_line_items', COUNT(*) FROM public.invoice_line_items
UNION ALL
SELECT 'payments', COUNT(*) FROM public.payments
UNION ALL
SELECT 'payment_methods', COUNT(*) FROM public.payment_methods
UNION ALL
SELECT 'payment_accounts', COUNT(*) FROM public.payment_accounts
UNION ALL
SELECT 'payment_transactions', COUNT(*) FROM public.payment_transactions
UNION ALL
SELECT 'leads', COUNT(*) FROM public.leads
UNION ALL
SELECT 'sales_leads', COUNT(*) FROM public.sales_leads
UNION ALL
SELECT 'lead_validation', COUNT(*) FROM public.lead_validation
UNION ALL
SELECT 'merchant_deposits', COUNT(*) FROM public.merchant_deposits
UNION ALL
SELECT 'company_deposits', COUNT(*) FROM public.company_deposits
UNION ALL
SELECT 'deposit_transactions', COUNT(*) FROM public.deposit_transactions
UNION ALL
SELECT 'affiliation_requests', COUNT(*) FROM public.affiliation_requests
UNION ALL
SELECT 'influencer_affiliation_requests', COUNT(*) FROM public.influencer_affiliation_requests
UNION ALL
SELECT 'merchant_affiliation_requests', COUNT(*) FROM public.merchant_affiliation_requests
UNION ALL
SELECT 'affiliate_requests', COUNT(*) FROM public.affiliate_requests
UNION ALL
SELECT 'affiliation_requests_stats', COUNT(*) FROM public.affiliation_requests_stats
UNION ALL
SELECT 'affiliation_request_history', COUNT(*) FROM public.affiliation_request_history
UNION ALL
SELECT 'influencer_agreements', COUNT(*) FROM public.influencer_agreements
UNION ALL
SELECT 'affiliate_links', COUNT(*) FROM public.affiliate_links
UNION ALL
SELECT 'social_connections', COUNT(*) FROM public.social_connections
UNION ALL
SELECT 'social_media_connections', COUNT(*) FROM public.social_media_connections
UNION ALL
SELECT 'social_media_accounts', COUNT(*) FROM public.social_media_accounts
UNION ALL
SELECT 'social_media_publications', COUNT(*) FROM public.social_media_publications
UNION ALL
SELECT 'social_media_stats', COUNT(*) FROM public.social_media_stats
UNION ALL
SELECT 'admin_social_posts', COUNT(*) FROM public.admin_social_posts
UNION ALL
SELECT 'admin_social_post_templates', COUNT(*) FROM public.admin_social_post_templates
UNION ALL
SELECT 'sales_representatives', COUNT(*) FROM public.sales_representatives
UNION ALL
SELECT 'sales_activities', COUNT(*) FROM public.sales_activities
UNION ALL
SELECT 'deals', COUNT(*) FROM public.deals
UNION ALL
SELECT 'sales_deals', COUNT(*) FROM public.sales_deals
UNION ALL
SELECT 'sales_targets', COUNT(*) FROM public.sales_targets
UNION ALL
SELECT 'sales_commissions', COUNT(*) FROM public.sales_commissions
UNION ALL
SELECT 'conversations', COUNT(*) FROM public.conversations
UNION ALL
SELECT 'messages', COUNT(*) FROM public.messages
UNION ALL
SELECT 'notifications', COUNT(*) FROM public.notifications
UNION ALL
SELECT 'reviews', COUNT(*) FROM public.reviews
UNION ALL
SELECT 'product_reviews', COUNT(*) FROM public.product_reviews
UNION ALL
SELECT 'click_tracking', COUNT(*) FROM public.click_tracking
UNION ALL
SELECT 'click_logs', COUNT(*) FROM public.click_logs
UNION ALL
SELECT 'tracking_events', COUNT(*) FROM public.tracking_events
UNION ALL
SELECT 'performance_metrics', COUNT(*) FROM public.performance_metrics
UNION ALL
SELECT 'user_gamification', COUNT(*) FROM public.user_gamification
UNION ALL
SELECT 'badges', COUNT(*) FROM public.badges
UNION ALL
SELECT 'missions', COUNT(*) FROM public.missions
UNION ALL
SELECT 'user_missions', COUNT(*) FROM public.user_missions
UNION ALL
SELECT 'kyc_submissions', COUNT(*) FROM public.kyc_submissions
UNION ALL
SELECT 'user_kyc_profile', COUNT(*) FROM public.user_kyc_profile
UNION ALL
SELECT 'user_kyc_documents', COUNT(*) FROM public.user_kyc_documents
UNION ALL
SELECT 'kyc_verification_logs', COUNT(*) FROM public.kyc_verification_logs
UNION ALL
SELECT 'trust_scores', COUNT(*) FROM public.trust_scores
UNION ALL
SELECT 'gateway_transactions', COUNT(*) FROM public.gateway_transactions
UNION ALL
SELECT 'gateway_statistics', COUNT(*) FROM public.gateway_statistics
UNION ALL
SELECT 'team_members', COUNT(*) FROM public.team_members
UNION ALL
SELECT 'team_invitations', COUNT(*) FROM public.team_invitations
UNION ALL
SELECT 'company_settings', COUNT(*) FROM public.company_settings
UNION ALL
SELECT 'platform_settings', COUNT(*) FROM public.platform_settings
UNION ALL
SELECT 'settings', COUNT(*) FROM public.settings
UNION ALL
SELECT 'contact_messages', COUNT(*) FROM public.contact_messages
UNION ALL
SELECT 'moderation_queue', COUNT(*) FROM public.moderation_queue
UNION ALL
SELECT 'swipe_history', COUNT(*) FROM public.swipe_history
UNION ALL
SELECT 'user_sessions', COUNT(*) FROM public.user_sessions
UNION ALL
SELECT 'webhook_logs', COUNT(*) FROM public.webhook_logs
UNION ALL
SELECT 'translations', COUNT(*) FROM public.translations
UNION ALL
SELECT 'match_preferences', COUNT(*) FROM public.match_preferences
UNION ALL
SELECT 'influencer_profiles_extended', COUNT(*) FROM public.influencer_profiles_extended
ORDER BY table_name;
