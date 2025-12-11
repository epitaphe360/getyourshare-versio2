-- ============================================================================
-- SCRIPT SQL POUR GÉNÉRER DES DONNÉES DE TEST POUR LES DASHBOARDS
-- Exécutez ce script dans Supabase SQL Editor pour remplir vos dashboards
-- ============================================================================

-- 1. GÉNÉRER DES VENTES DES 30 DERNIERS JOURS (300 ventes)
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    i INTEGER;
    days_ago INTEGER;
    sale_date TIMESTAMP;
    sale_amount DECIMAL(10,2);
    merchant_id_var UUID;
    product_id_var UUID;
BEGIN
    -- Récupérer un merchant et produit existant
    SELECT id INTO merchant_id_var FROM users WHERE role = 'merchant' LIMIT 1;
    SELECT id INTO product_id_var FROM products LIMIT 1;

    -- Créer 300 ventes sur 30 jours (10 par jour)
    FOR days_ago IN 0..29 LOOP
        FOR i IN 1..10 LOOP
            sale_date := NOW() - (days_ago || ' days')::INTERVAL;
            sale_amount := (RANDOM() * 450 + 50)::DECIMAL(10,2);  -- Entre 50€ et 500€

            INSERT INTO sales (
                merchant_id,
                product_id,
                amount,
                platform_commission,
                commission_amount,
                status,
                created_at
            ) VALUES (
                merchant_id_var,
                product_id_var,
                sale_amount,
                (sale_amount * 0.10)::DECIMAL(10,2),  -- 10% commission plateforme
                (sale_amount * 0.05)::DECIMAL(10,2),  -- 5% commission influenceur
                'completed',
                sale_date
            );
        END LOOP;
    END LOOP;

    RAISE NOTICE '✅ 300 ventes créées pour les 30 derniers jours';
END $$;

-- 2. GÉNÉRER DES NOUVEAUX UTILISATEURS DES 30 DERNIERS JOURS
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    i INTEGER;
    days_ago INTEGER;
    user_date TIMESTAMP;
    user_role TEXT;
BEGIN
    -- Créer 90 nouveaux utilisateurs (3 par jour)
    FOR days_ago IN 0..29 LOOP
        FOR i IN 1..3 LOOP
            user_date := NOW() - (days_ago || ' days')::INTERVAL;

            -- Alterner entre merchant, influencer, et commercial
            user_role := CASE (i % 3)
                WHEN 0 THEN 'merchant'
                WHEN 1 THEN 'influencer'
                ELSE 'commercial'
            END;

            INSERT INTO users (
                email,
                full_name,
                role,
                is_active,
                created_at
            ) VALUES (
                'test_' || days_ago || '_' || i || '_' || user_role || '@test.com',
                'Test User ' || days_ago || '-' || i,
                user_role,
                TRUE,
                user_date
            );
        END LOOP;
    END LOOP;

    RAISE NOTICE '✅ 90 nouveaux utilisateurs créés';
END $$;

-- 3. GÉNÉRER DES ABONNEMENTS ACTIFS
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    i INTEGER;
    user_id_var UUID;
    plan_id_var UUID;
BEGIN
    -- Récupérer un plan existant
    SELECT id INTO plan_id_var FROM subscription_plans LIMIT 1;

    -- Créer 50 abonnements actifs
    FOR i IN 1..50 LOOP
        -- Prendre un utilisateur au hasard
        SELECT id INTO user_id_var FROM users WHERE role IN ('merchant', 'influencer') ORDER BY RANDOM() LIMIT 1;

        INSERT INTO subscriptions (
            user_id,
            plan_id,
            status,
            current_period_start,
            current_period_end,
            created_at
        ) VALUES (
            user_id_var,
            plan_id_var,
            'active',
            NOW() - INTERVAL '15 days',
            NOW() + INTERVAL '15 days',
            NOW() - INTERVAL '15 days'
        );
    END LOOP;

    RAISE NOTICE '✅ 50 abonnements actifs créés';
END $$;

-- 4. AFFICHER UN RÉSUMÉ DES DONNÉES
-- ----------------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM sales WHERE created_at >= NOW() - INTERVAL '30 days') AS ventes_30j,
    (SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '30 days') AS users_30j,
    (SELECT COUNT(*) FROM subscriptions WHERE status = 'active') AS abonnements_actifs,
    (SELECT SUM(amount) FROM sales WHERE created_at >= NOW() - INTERVAL '30 days') AS revenue_30j;

-- ============================================================================
-- ✅ SCRIPT TERMINÉ !
-- Vos dashboards devraient maintenant afficher des données.
-- ============================================================================
