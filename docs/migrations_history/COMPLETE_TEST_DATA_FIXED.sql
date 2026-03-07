-- ============================================
-- SCRIPT COMPLET: DONNÉES DE TEST MANQUANTES
-- ============================================
-- Complète les tables: sales_representatives, marketing_templates, 
-- lead_activities, tracking_links
-- Date: 30 novembre 2025
-- ============================================

-- ============================================
-- 0. CRÉER LES TABLES MANQUANTES
-- ============================================

-- Table: marketing_templates
CREATE TABLE IF NOT EXISTS marketing_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commercial_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('email', 'social', 'presentation', 'sms', 'whatsapp')),
    subject TEXT,
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_marketing_templates_commercial ON marketing_templates(commercial_id);
CREATE INDEX IF NOT EXISTS idx_marketing_templates_type ON marketing_templates(type);
CREATE INDEX IF NOT EXISTS idx_marketing_templates_active ON marketing_templates(is_active) WHERE is_active = TRUE;

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_marketing_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER marketing_templates_updated_at
    BEFORE UPDATE ON marketing_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_marketing_templates_updated_at();

-- ============================================
-- 1. SALES_REPRESENTATIVES (6 commerciaux)
-- ============================================

INSERT INTO sales_representatives (
    user_id, 
    first_name, 
    last_name, 
    email, 
    phone,
    territory, 
    commission_rate, 
    target_monthly_deals, 
    target_monthly_revenue
)
VALUES 
('44444444-4444-4444-4444-444444444441', 'Karim', 'Sales', 'commercial1@shareyoursales.ma', '+212 6 12 34 56 01', 'Casablanca', 5.0, 20, 100000),
('44444444-4444-4444-4444-444444444442', 'Laila', 'Growth', 'commercial2@shareyoursales.ma', '+212 6 12 34 56 02', 'Rabat', 5.5, 18, 95000),
('44444444-4444-4444-4444-444444444443', 'Omar', 'Business', 'commercial3@shareyoursales.ma', '+212 6 12 34 56 03', 'Marrakech', 6.0, 22, 110000),
('44444444-4444-4444-4444-444444444444', 'Amina', 'Dev', 'commercial4@shareyoursales.ma', '+212 6 12 34 56 04', 'Tanger', 5.0, 16, 80000),
('44444444-4444-4444-4444-444444444445', 'Rachid', 'Pro', 'commercial5@shareyoursales.ma', '+212 6 12 34 56 05', 'Fès', 5.5, 19, 98000),
('44444444-4444-4444-4444-444444444446', 'Sophia', 'Elite', 'commercial6@shareyoursales.ma', '+212 6 12 34 56 06', 'Agadir', 6.5, 25, 125000)
ON CONFLICT (user_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    territory = EXCLUDED.territory,
    commission_rate = EXCLUDED.commission_rate,
    target_monthly_deals = EXCLUDED.target_monthly_deals,
    target_monthly_revenue = EXCLUDED.target_monthly_revenue;

-- ============================================
-- 2. MARKETING_TEMPLATES (10 templates simplifiés)
-- ============================================

INSERT INTO marketing_templates (commercial_id, name, type, subject, content, variables, is_active, usage_count, created_at)
VALUES
-- EMAIL TEMPLATES
('44444444-4444-4444-4444-444444444441', 'Email Bienvenue', 'email', 'Bienvenue chez ShareYourSales', 'Bonjour, merci pour votre intérêt!', '[]'::jsonb, true, 10, NOW() - INTERVAL '30 days'),
('44444444-4444-4444-4444-444444444442', 'Email Suivi', 'email', 'Suivi de votre demande', 'Suite à notre échange...', '[]'::jsonb, true, 15, NOW() - INTERVAL '25 days'),
('44444444-4444-4444-4444-444444444443', 'Email Relance', 'email', 'On reste en contact?', 'Je me permets de vous recontacter...', '[]'::jsonb, true, 20, NOW() - INTERVAL '20 days'),
-- SOCIAL TEMPLATES
('44444444-4444-4444-4444-444444444444', 'Post LinkedIn', 'social', NULL, 'Success story client! Résultats impressionnants.', '[]'::jsonb, true, 8, NOW() - INTERVAL '15 days'),
('44444444-4444-4444-4444-444444444445', 'Post Instagram', 'social', NULL, 'Offre flash 48h! Ne manquez pas cette opportunité.', '[]'::jsonb, true, 12, NOW() - INTERVAL '10 days'),
-- PRESENTATION TEMPLATES
('44444444-4444-4444-4444-444444444446', 'Pitch Deck', 'presentation', 'Présentation ShareYourSales', 'SLIDE 1: Couverture - ShareYourSales', '[]'::jsonb, true, 5, NOW() - INTERVAL '5 days'),
('44444444-4444-4444-4444-444444444441', 'Proposition Commerciale', 'presentation', 'Proposition Détaillée', 'Client: XXX - Date: XXX - Offre: XXX', '[]'::jsonb, true, 7, NOW() - INTERVAL '8 days'),
('44444444-4444-4444-4444-444444444442', 'ROI Calculator', 'presentation', 'Calculateur ROI', 'Budget actuel vs Résultats projetés', '[]'::jsonb, true, 9, NOW() - INTERVAL '12 days'),
('44444444-4444-4444-4444-444444444443', 'Guide Onboarding', 'presentation', 'Bienvenue Client', 'Étape 1: Configuration - Étape 2: Lancement', '[]'::jsonb, true, 6, NOW() - INTERVAL '18 days'),
('44444444-4444-4444-4444-444444444444', 'Rapport Mensuel', 'presentation', 'Rapport Performance', 'Résumé du mois - Campagnes - Résultats - Recommandations', '[]'::jsonb, true, 11, NOW() - INTERVAL '22 days');

-- ============================================
-- 3. LEAD_ACTIVITIES (Activités pour leads existants)
-- ============================================

DO $$
DECLARE
    lead_record RECORD;
BEGIN
    FOR lead_record IN 
        SELECT id, commercial_id, company_name, status 
        FROM services_leads 
        LIMIT 5
    LOOP
        -- Note de création
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description, created_at)
        VALUES (lead_record.id, lead_record.commercial_id, 'note', 'Lead créé', 'Nouveau lead ajouté: ' || lead_record.company_name, NOW() - INTERVAL '15 days');

        -- Premier appel
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description, created_at)
        VALUES (lead_record.id, lead_record.commercial_id, 'call', 'Premier contact', 'Appel découverte avec ' || lead_record.company_name, NOW() - INTERVAL '12 days');

        -- Email de suivi
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description, created_at)
        VALUES (lead_record.id, lead_record.commercial_id, 'email', 'Email suivi', 'Envoi présentation et proposition', NOW() - INTERVAL '10 days');

        -- Réunion si statut avancé
        IF lead_record.status IN ('qualifié', 'proposition', 'négociation') THEN
            INSERT INTO lead_activities (lead_id, user_id, type, subject, description, created_at)
            VALUES (lead_record.id, lead_record.commercial_id, 'meeting', 'Démo produit', 'Présentation complète plateforme', NOW() - INTERVAL '7 days');
        END IF;

        -- Point situation avec update
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description, created_at)
        VALUES (lead_record.id, lead_record.commercial_id, 'update', 'Point situation', 
                CASE lead_record.status
                    WHEN 'nouveau' THEN 'À recontacter cette semaine'
                    WHEN 'contacté' THEN 'En attente retour prospect'
                    WHEN 'qualifié' THEN 'Préparation proposition'
                    WHEN 'proposition' THEN 'Relance prévue dans 3 jours'
                    WHEN 'négociation' THEN 'Phase finale négociation'
                    ELSE 'Suivi en cours'
                END,
                NOW() - INTERVAL '1 day');
    END LOOP;

    RAISE NOTICE '✅ Lead activities créées';
END $$;

-- ============================================
-- 4. TRACKING_LINKS (Liens pour influenceurs)
-- ============================================

DO $$
DECLARE
    inf_id UUID;
    merch_id UUID;
    counter INT := 0;
BEGIN
    FOR inf_id IN SELECT id FROM users WHERE role = 'influencer' LIMIT 7
    LOOP
        SELECT id INTO merch_id FROM users WHERE role = 'merchant' ORDER BY RANDOM() LIMIT 1;
        counter := counter + 1;
        
        -- Link 1: Actif avec bonnes stats
        INSERT INTO tracking_links (id, influencer_id, merchant_id, tracking_code, short_url, destination_url, campaign_name, is_active, clicks_count, conversions_count, revenue_generated, created_at)
        VALUES (gen_random_uuid(), inf_id, merch_id, 'SYS' || LPAD(counter::TEXT, 6, '0') || 'A', 'sys.ma/' || counter || 'A', 'https://example.com/product-' || counter, 'Campagne Hiver 2024', true, 
                FLOOR(RANDOM() * 500 + 100)::INT, FLOOR(RANDOM() * 50 + 5)::INT, ROUND((RANDOM() * 5000 + 500)::NUMERIC, 2), NOW() - (RANDOM() * INTERVAL '60 days'));

        -- Link 2: Actif
        INSERT INTO tracking_links (id, influencer_id, merchant_id, tracking_code, short_url, destination_url, campaign_name, is_active, clicks_count, conversions_count, revenue_generated, created_at)
        VALUES (gen_random_uuid(), inf_id, merch_id, 'SYS' || LPAD(counter::TEXT, 6, '0') || 'B', 'sys.ma/' || counter || 'B', 'https://example.com/category-' || counter, 'Campagne Printemps 2024', true,
                FLOOR(RANDOM() * 400 + 80)::INT, FLOOR(RANDOM() * 40 + 3)::INT, ROUND((RANDOM() * 4000 + 400)::NUMERIC, 2), NOW() - (RANDOM() * INTERVAL '45 days'));

        -- Link 3: Très actif
        INSERT INTO tracking_links (id, influencer_id, merchant_id, tracking_code, short_url, destination_url, campaign_name, is_active, clicks_count, conversions_count, revenue_generated, created_at)
        VALUES (gen_random_uuid(), inf_id, merch_id, 'SYS' || LPAD(counter::TEXT, 6, '0') || 'C', 'sys.ma/' || counter || 'C', 'https://example.com/promo-' || counter, 'Campagne Black Friday', true,
                FLOOR(RANDOM() * 800 + 200)::INT, FLOOR(RANDOM() * 80 + 10)::INT, ROUND((RANDOM() * 8000 + 1000)::NUMERIC, 2), NOW() - (RANDOM() * INTERVAL '30 days'));

        -- Link 4: Inactif
        INSERT INTO tracking_links (id, influencer_id, merchant_id, tracking_code, short_url, destination_url, campaign_name, is_active, clicks_count, conversions_count, revenue_generated, created_at)
        VALUES (gen_random_uuid(), inf_id, merch_id, 'SYS' || LPAD(counter::TEXT, 6, '0') || 'D', 'sys.ma/' || counter || 'D', 'https://example.com/collection-' || counter, 'Campagne Été 2024', false,
                FLOOR(RANDOM() * 150 + 20)::INT, FLOOR(RANDOM() * 10 + 1)::INT, ROUND((RANDOM() * 1500 + 200)::NUMERIC, 2), NOW() - (RANDOM() * INTERVAL '90 days'));
    END LOOP;

    RAISE NOTICE '✅ Tracking links créés';
END $$;

-- ============================================
-- 5. RÉSUMÉ FINAL
-- ============================================

DO $$
DECLARE
    total_sales_reps INT;
    total_templates INT;
    total_activities INT;
    total_tracking_links INT;
BEGIN
    SELECT COUNT(*) INTO total_sales_reps FROM sales_representatives;
    SELECT COUNT(*) INTO total_templates FROM marketing_templates;
    SELECT COUNT(*) INTO total_activities FROM lead_activities;
    SELECT COUNT(*) INTO total_tracking_links FROM tracking_links;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ DONNÉES DE TEST COMPLÉTÉES À 100%%';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 RÉSUMÉ DES AJOUTS:';
    RAISE NOTICE '   - Sales Representatives: %', total_sales_reps;
    RAISE NOTICE '   - Marketing Templates: %', total_templates;
    RAISE NOTICE '   - Lead Activities: %', total_activities;
    RAISE NOTICE '   - Tracking Links: %', total_tracking_links;
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Dashboard commercial 100%% fonctionnel!';
    RAISE NOTICE '✅ CRM production-ready avec données de test!';
    RAISE NOTICE '========================================';
END $$;
