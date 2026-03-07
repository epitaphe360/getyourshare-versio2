-- ============================================
-- SCRIPT INSERTION: DONNÉES DE TEST UNIQUEMENT
-- ============================================
-- Insère les données dans: sales_representatives, marketing_templates, 
-- lead_activities, tracking_links
-- Date: 30 novembre 2025
-- Prérequis: Toutes les tables doivent déjà exister
-- ============================================

-- ============================================
-- 1. SALES_REPRESENTATIVES (6 commerciaux)
-- ============================================

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, 
    territory, commission_rate, target_monthly_deals, target_monthly_revenue
)
SELECT 
    u.id, 'Karim', 'Benali', 'karim.benali@getyourshare.ma', '+212661234567',
    'Casablanca', 5.5, 20, 100000
FROM users u WHERE u.email = 'commercial1@getyourshare.ma'
ON CONFLICT (user_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    territory = EXCLUDED.territory;

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, 
    territory, commission_rate, target_monthly_deals, target_monthly_revenue
)
SELECT 
    u.id, 'Laila', 'Alaoui', 'laila.alaoui@getyourshare.ma', '+212662345678',
    'Rabat', 6.0, 18, 90000
FROM users u WHERE u.email = 'commercial2@getyourshare.ma'
ON CONFLICT (user_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    territory = EXCLUDED.territory;

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, 
    territory, commission_rate, target_monthly_deals, target_monthly_revenue
)
SELECT 
    u.id, 'Omar', 'Tazi', 'omar.tazi@getyourshare.ma', '+212663456789',
    'Marrakech', 5.0, 25, 125000
FROM users u WHERE u.email = 'commercial3@getyourshare.ma'
ON CONFLICT (user_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    territory = EXCLUDED.territory;

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, 
    territory, commission_rate, target_monthly_deals, target_monthly_revenue
)
SELECT 
    u.id, 'Amina', 'Chraibi', 'amina.chraibi@getyourshare.ma', '+212664567890',
    'Tanger', 5.8, 16, 80000
FROM users u WHERE u.email = 'commercial4@getyourshare.ma'
ON CONFLICT (user_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    territory = EXCLUDED.territory;

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, 
    territory, commission_rate, target_monthly_deals, target_monthly_revenue
)
SELECT 
    u.id, 'Rachid', 'Fassi', 'rachid.fassi@getyourshare.ma', '+212665678901',
    'Fès', 6.5, 22, 110000
FROM users u WHERE u.email = 'commercial5@getyourshare.ma'
ON CONFLICT (user_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    territory = EXCLUDED.territory;

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, 
    territory, commission_rate, target_monthly_deals, target_monthly_revenue
)
SELECT 
    u.id, 'Sophia', 'Andaloussi', 'sophia.andaloussi@getyourshare.ma', '+212666789012',
    'Agadir', 5.3, 19, 95000
FROM users u WHERE u.email = 'commercial6@getyourshare.ma'
ON CONFLICT (user_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    territory = EXCLUDED.territory;

-- ============================================
-- 2. MARKETING_TEMPLATES (10 modèles)
-- ============================================

DO $$
DECLARE
    commercial_uuid UUID;
BEGIN
    -- Récupérer un commercial existant
    SELECT id INTO commercial_uuid FROM users WHERE role = 'commercial' LIMIT 1;
    
    IF commercial_uuid IS NULL THEN
        RAISE EXCEPTION 'Aucun commercial trouvé';
    END IF;

    -- Insérer les templates
    INSERT INTO marketing_templates (commercial_id, name, type, subject, content, variables, usage_count, created_at)
    VALUES
        (commercial_uuid, 'Email Bienvenue', 'email', 'Bienvenue chez GetYourShare', 'Bonjour, nous sommes ravis de vous accueillir.', '["company_name", "contact_name"]'::jsonb, 15, NOW() - INTERVAL '25 days'),
        (commercial_uuid, 'Email Suivi', 'email', 'Suite à notre conversation', 'Suite à notre échange, voici la proposition.', '["company_name", "proposal_link"]'::jsonb, 12, NOW() - INTERVAL '20 days'),
        (commercial_uuid, 'Email Relance', 'email', 'Avez-vous des questions?', 'Je me permets de revenir vers vous concernant notre offre.', '["contact_name"]'::jsonb, 8, NOW() - INTERVAL '15 days'),
        (commercial_uuid, 'Post LinkedIn', 'social', NULL, 'Découvrez comment GetYourShare transforme le marketing d''affiliation.', '["company_name"]'::jsonb, 20, NOW() - INTERVAL '30 days'),
        (commercial_uuid, 'Post Facebook', 'social', NULL, 'Rejoignez des centaines d''entreprises qui font confiance à GetYourShare.', '[]'::jsonb, 18, NOW() - INTERVAL '28 days'),
        (commercial_uuid, 'Présentation Standard', 'presentation', NULL, 'Présentation complète de notre plateforme et de ses fonctionnalités.', '["company_name", "industry"]'::jsonb, 10, NOW() - INTERVAL '22 days'),
        (commercial_uuid, 'Présentation Premium', 'presentation', NULL, 'Présentation détaillée de l''offre Premium avec ROI.', '["company_name", "revenue_target"]'::jsonb, 7, NOW() - INTERVAL '18 days'),
        (commercial_uuid, 'Présentation Démo', 'presentation', NULL, 'Support pour la démonstration en direct de la plateforme.', '[]'::jsonb, 5, NOW() - INTERVAL '12 days'),
        (commercial_uuid, 'Présentation ROI', 'presentation', NULL, 'Focus sur le retour sur investissement et les bénéfices.', '["estimated_revenue"]'::jsonb, 6, NOW() - INTERVAL '10 days'),
        (commercial_uuid, 'Présentation Onboarding', 'presentation', NULL, 'Guide d''intégration pour les nouveaux clients.', '["company_name", "start_date"]'::jsonb, 9, NOW() - INTERVAL '5 days');
    
    RAISE NOTICE '✅ % templates marketing insérés', 10;
END $$;

-- ============================================
-- 3. LEAD_ACTIVITIES (5 activités par lead)
-- ============================================

DO $$
DECLARE
    lead_record RECORD;
    activity_count INTEGER := 0;
BEGIN
    -- Boucle sur les 5 premiers leads
    FOR lead_record IN 
        SELECT id, commercial_id, company_name, status 
        FROM services_leads 
        ORDER BY created_at DESC 
        LIMIT 5
    LOOP
        -- Activité 1: Note de création
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
        VALUES (
            lead_record.id,
            lead_record.commercial_id,
            'note',
            'Lead créé',
            format('Nouveau lead %s ajouté au pipeline', lead_record.company_name)
        );
        
        -- Activité 2: Appel téléphonique
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
        VALUES (
            lead_record.id,
            lead_record.commercial_id,
            'call',
            'Appel de découverte',
            CASE 
                WHEN lead_record.status = 'nouveau' THEN 'Premier contact établi, lead intéressé par notre solution'
                WHEN lead_record.status = 'contacté' THEN 'Discussion approfondie sur les besoins et objectifs'
                ELSE 'Échange constructif, lead très engagé'
            END
        );
        
        -- Activité 3: Email
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
        VALUES (
            lead_record.id,
            lead_record.commercial_id,
            'email',
            'Envoi proposition commerciale',
            format('Proposition personnalisée envoyée à %s', lead_record.company_name)
        );
        
        -- Activité 4: Réunion (si qualifié)
        IF lead_record.status IN ('qualifié', 'proposition', 'négociation') THEN
            INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
            VALUES (
                lead_record.id,
                lead_record.commercial_id,
                'meeting',
                'Démo produit',
                'Présentation détaillée de la plateforme, démo bien reçue'
            );
        END IF;
        
        -- Activité 5: Update de statut
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
        VALUES (
            lead_record.id,
            lead_record.commercial_id,
            'update',
            'Point d''avancement',
            format('Lead %s, prochaine étape définie', lead_record.status)
        );
        
        activity_count := activity_count + 5;
    END LOOP;
    
    RAISE NOTICE '✅ % activités de lead insérées', activity_count;
END $$;

-- ============================================
-- 4. TRACKING_LINKS (4 liens par influenceur)
-- ============================================

DO $$
DECLARE
    influencer_record RECORD;
    merchant_uuid UUID;
    link_count INTEGER := 0;
    i INTEGER;
BEGIN
    -- Récupérer un marchand
    SELECT id INTO merchant_uuid FROM users WHERE role = 'merchant' LIMIT 1;
    
    IF merchant_uuid IS NULL THEN
        RAISE EXCEPTION 'Aucun marchand trouvé';
    END IF;
    
    -- Boucle sur les 7 premiers influenceurs
    FOR influencer_record IN 
        SELECT id FROM users WHERE role = 'influencer' LIMIT 7
    LOOP
        -- Créer 4 liens par influenceur
        FOR i IN 1..4 LOOP
            INSERT INTO tracking_links (
                influencer_id, merchant_id, unique_code, full_url, 
                short_url, is_active, clicks, conversions, revenue
            )
            VALUES (
                influencer_record.id,
                merchant_uuid,
                format('TRK-%s-%s', upper(substring(influencer_record.id::text, 1, 8)), i),
                format('https://getyourshare.ma/products?ref=%s', md5(random()::text)),
                format('https://gys.ma/%s', md5(random()::text)),
                (random() > 0.3), -- 70% actifs
                floor(random() * 800 + 20)::INTEGER,
                floor(random() * 80 + 1)::INTEGER,
                (random() * 8000 + 200)::NUMERIC(12,2)
            )
            ON CONFLICT (unique_code) DO UPDATE SET
                clicks = EXCLUDED.clicks,
                conversions = EXCLUDED.conversions,
                revenue = EXCLUDED.revenue,
                is_active = EXCLUDED.is_active;
            
            link_count := link_count + 1;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE '✅ % liens de tracking insérés', link_count;
END $$;

-- ============================================
-- 5. RÉSUMÉ FINAL
-- ============================================

DO $$
DECLARE
    sales_reps_count INTEGER;
    templates_count INTEGER;
    activities_count INTEGER;
    links_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO sales_reps_count FROM sales_representatives;
    SELECT COUNT(*) INTO templates_count FROM marketing_templates;
    SELECT COUNT(*) INTO activities_count FROM lead_activities;
    SELECT COUNT(*) INTO links_count FROM tracking_links;
    
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════╗';
    RAISE NOTICE '║  ✅ DONNÉES DE TEST COMPLÉTÉES À 100%%     ║';
    RAISE NOTICE '╠════════════════════════════════════════════╣';
    RAISE NOTICE '║  📊 Sales Representatives:  %              ║', LPAD(sales_reps_count::TEXT, 12);
    RAISE NOTICE '║  📧 Marketing Templates:    %              ║', LPAD(templates_count::TEXT, 12);
    RAISE NOTICE '║  📝 Lead Activities:        %              ║', LPAD(activities_count::TEXT, 12);
    RAISE NOTICE '║  🔗 Tracking Links:         %              ║', LPAD(links_count::TEXT, 12);
    RAISE NOTICE '╚════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $$;
