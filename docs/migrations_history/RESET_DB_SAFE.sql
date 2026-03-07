-- ============================================
-- SCRIPT DE RESET SÉCURISÉ DE LA BASE DE DONNÉES
-- ============================================
-- ÉTAPE 1: Exécutez ce script dans l'éditeur SQL de Supabase
-- ÉTAPE 2: Fermez TOUTES les connexions backend/frontend
-- ÉTAPE 3: Attendez 10 secondes
-- ÉTAPE 4: Exécutez CREATE_ALL_TABLES_COMPLETE.sql
-- ============================================

-- Désactiver temporairement les connexions
SET session_replication_role = replica;

-- Terminer toutes les requêtes actives (sauf la vôtre)
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE pid <> pg_backend_pid() 
  AND datname = current_database()
  AND usename = current_user;

-- Désactiver tous les triggers (ignorer les erreurs de permission)
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        BEGIN
            EXECUTE format('ALTER TABLE IF EXISTS %I.%I DISABLE TRIGGER ALL', r.schemaname, r.tablename);
        EXCEPTION WHEN insufficient_privilege THEN
            -- Ignorer les erreurs de permission pour les triggers système
            NULL;
        END;
    END LOOP;
END $$;

-- Supprimer toutes les vues d'abord
DROP VIEW IF EXISTS v_products_full CASCADE;
DROP VIEW IF EXISTS v_featured_products CASCADE;
DROP VIEW IF EXISTS v_deals_of_day CASCADE;
DROP VIEW IF EXISTS v_admin_social_posts_summary CASCADE;
DROP VIEW IF EXISTS v_admin_social_analytics CASCADE;
DROP VIEW IF EXISTS v_contact_stats CASCADE;

-- Supprimer toutes les tables dans l'ordre INVERSE des dépendances
-- (Tables enfants d'abord, tables parents à la fin)

-- Niveau 5: Tables sans dépendances externes (leaf tables)
DROP TABLE IF EXISTS translations CASCADE;
DROP TABLE IF EXISTS webhook_logs CASCADE;
DROP TABLE IF EXISTS swipe_history CASCADE;
DROP TABLE IF EXISTS click_tracking CASCADE;
DROP TABLE IF EXISTS click_logs CASCADE;
DROP TABLE IF EXISTS tracking_events CASCADE;
DROP TABLE IF EXISTS performance_metrics CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS moderation_queue CASCADE;
DROP TABLE IF EXISTS contact_messages CASCADE;
DROP TABLE IF EXISTS settings CASCADE;
DROP TABLE IF EXISTS gateway_statistics CASCADE;
DROP TABLE IF EXISTS subscription_coupons CASCADE;
DROP TABLE IF EXISTS badges CASCADE;
DROP TABLE IF EXISTS missions CASCADE;
DROP TABLE IF EXISTS trust_scores CASCADE;
DROP TABLE IF EXISTS match_preferences CASCADE;
DROP TABLE IF EXISTS influencer_profiles_extended CASCADE;

-- Niveau 4: Tables dépendant des tables de niveau 5
DROP TABLE IF EXISTS user_missions CASCADE;
DROP TABLE IF EXISTS kyc_verification_logs CASCADE;
DROP TABLE IF EXISTS user_kyc_documents CASCADE;
DROP TABLE IF EXISTS user_kyc_profile CASCADE;
DROP TABLE IF EXISTS kyc_submissions CASCADE;
DROP TABLE IF EXISTS user_gamification CASCADE;
DROP TABLE IF EXISTS affiliation_request_history CASCADE;
DROP TABLE IF EXISTS affiliation_requests_stats CASCADE;
DROP TABLE IF EXISTS affiliate_links CASCADE;
DROP TABLE IF EXISTS influencer_agreements CASCADE;
DROP TABLE IF EXISTS affiliate_requests CASCADE;
DROP TABLE IF EXISTS merchant_affiliation_requests CASCADE;
DROP TABLE IF EXISTS influencer_affiliation_requests CASCADE;
DROP TABLE IF EXISTS social_media_stats CASCADE;
DROP TABLE IF EXISTS social_media_publications CASCADE;
DROP TABLE IF EXISTS social_media_accounts CASCADE;
DROP TABLE IF EXISTS social_media_connections CASCADE;
DROP TABLE IF EXISTS social_connections CASCADE;
DROP TABLE IF EXISTS admin_social_post_templates CASCADE;
DROP TABLE IF EXISTS admin_social_posts CASCADE;

-- Niveau 3: Tables de transactions et relations complexes
DROP TABLE IF EXISTS sales_commissions CASCADE;
DROP TABLE IF EXISTS sales_targets CASCADE;
DROP TABLE IF EXISTS sales_deals CASCADE;
DROP TABLE IF EXISTS deals CASCADE;
DROP TABLE IF EXISTS sales_activities CASCADE;
DROP TABLE IF EXISTS deposit_transactions CASCADE;
DROP TABLE IF EXISTS company_deposits CASCADE;
DROP TABLE IF EXISTS merchant_deposits CASCADE;
DROP TABLE IF EXISTS lead_validation CASCADE;
DROP TABLE IF EXISTS sales_leads CASCADE;
DROP TABLE IF EXISTS gateway_transactions CASCADE;
DROP TABLE IF EXISTS payment_transactions CASCADE;
DROP TABLE IF EXISTS payment_accounts CASCADE;
DROP TABLE IF EXISTS payment_methods CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS invoice_line_items CASCADE;
DROP TABLE IF EXISTS platform_invoices CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS subscription_events CASCADE;
DROP TABLE IF EXISTS subscription_usage CASCADE;
DROP TABLE IF EXISTS payouts CASCADE;
DROP TABLE IF EXISTS commissions CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS conversions CASCADE;
DROP TABLE IF EXISTS trackable_links CASCADE;
DROP TABLE IF EXISTS tracking_links CASCADE;
DROP TABLE IF EXISTS product_reviews CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;

-- Niveau 2: Tables de configuration et relations intermédiaires
DROP TABLE IF EXISTS company_settings CASCADE;
DROP TABLE IF EXISTS team_invitations CASCADE;
DROP TABLE IF EXISTS team_members CASCADE;
DROP TABLE IF EXISTS platform_settings CASCADE;
DROP TABLE IF EXISTS collaboration_history CASCADE;
DROP TABLE IF EXISTS collaboration_invitations CASCADE;
DROP TABLE IF EXISTS collaboration_requests CASCADE;
DROP TABLE IF EXISTS affiliation_requests CASCADE;
DROP TABLE IF EXISTS invitations CASCADE;
DROP TABLE IF EXISTS campaign_settings CASCADE;
DROP TABLE IF EXISTS campaign_products CASCADE;
DROP TABLE IF EXISTS sales_representatives CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS subscription_plans CASCADE;
DROP TABLE IF EXISTS leads CASCADE;

-- Niveau 1: Tables de campagnes et produits
DROP TABLE IF EXISTS campaigns CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Niveau 0: Tables de base (merchants, influencers, users)
DROP TABLE IF EXISTS influencers CASCADE;
DROP TABLE IF EXISTS merchants CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Réactiver
SET session_replication_role = DEFAULT;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'BASE DE DONNÉES NETTOYÉE AVEC SUCCÈS!';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'PROCHAINES ÉTAPES:';
    RAISE NOTICE '1. Fermez toutes les connexions backend/frontend';
    RAISE NOTICE '2. Attendez 10 secondes';
    RAISE NOTICE '3. Exécutez CREATE_ALL_TABLES_COMPLETE.sql';
    RAISE NOTICE '============================================';
END $$;
