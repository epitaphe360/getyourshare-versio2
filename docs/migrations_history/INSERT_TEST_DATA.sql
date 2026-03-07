-- ============================================
-- DONNÉES DE TEST - DASHBOARD INFLUENCEUR & COMMERCIAL
-- ============================================
-- Exécuter après avoir créé toutes les tables
-- Remplacer les UUID par des vrais IDs de votre base

-- ============================================
-- PARTIE 1: DONNÉES INFLUENCEUR
-- ============================================

-- Note: Remplacer 'YOUR_INFLUENCER_USER_ID' par un vrai ID d'un user avec role='influencer'
-- Note: Remplacer 'YOUR_MERCHANT_ID' et 'YOUR_PRODUCT_ID' par des vrais IDs

-- 1. Créer des tracking links pour l'influenceur
INSERT INTO tracking_links (influencer_id, product_id, merchant_id, tracking_code, created_at)
VALUES 
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_PRODUCT_ID_1', 'YOUR_MERCHANT_ID_1', 'INF2024ABC', NOW() - INTERVAL '30 days'),
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_PRODUCT_ID_2', 'YOUR_MERCHANT_ID_1', 'INF2024DEF', NOW() - INTERVAL '25 days'),
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_PRODUCT_ID_3', 'YOUR_MERCHANT_ID_2', 'INF2024GHI', NOW() - INTERVAL '20 days'),
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_PRODUCT_ID_4', 'YOUR_MERCHANT_ID_2', 'INF2024JKL', NOW() - INTERVAL '15 days'),
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_PRODUCT_ID_5', 'YOUR_MERCHANT_ID_3', 'INF2024MNO', NOW() - INTERVAL '10 days');

-- 2. Créer des conversions (clics + ventes)
-- Note: Récupérer les IDs des tracking_links créés ci-dessus

DO $$
DECLARE
    link1_id UUID;
    link2_id UUID;
    link3_id UUID;
BEGIN
    -- Récupérer les IDs des liens créés
    SELECT id INTO link1_id FROM tracking_links WHERE tracking_code = 'INF2024ABC';
    SELECT id INTO link2_id FROM tracking_links WHERE tracking_code = 'INF2024DEF';
    SELECT id INTO link3_id FROM tracking_links WHERE tracking_code = 'INF2024GHI';
    
    -- Conversions pour link1 (8 clics, 2 ventes)
    INSERT INTO conversions (tracking_link_id, influencer_id, commission_amount, status, created_at)
    VALUES 
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '29 days'),
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '28 days'),
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 45.50, 'completed', NOW() - INTERVAL '27 days'),
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '26 days'),
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '25 days'),
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 52.30, 'completed', NOW() - INTERVAL '24 days'),
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '23 days'),
        (link1_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '22 days');
    
    -- Conversions pour link2 (12 clics, 4 ventes)
    INSERT INTO conversions (tracking_link_id, influencer_id, commission_amount, status, created_at)
    VALUES 
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '24 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 32.00, 'completed', NOW() - INTERVAL '23 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '22 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 28.50, 'completed', NOW() - INTERVAL '21 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '20 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '19 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 41.20, 'completed', NOW() - INTERVAL '18 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '17 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '16 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 38.90, 'completed', NOW() - INTERVAL '15 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '14 days'),
        (link2_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '13 days');
    
    -- Conversions pour link3 (15 clics, 5 ventes)
    INSERT INTO conversions (tracking_link_id, influencer_id, commission_amount, status, created_at)
    VALUES 
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '19 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '18 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 55.80, 'completed', NOW() - INTERVAL '17 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '16 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 48.30, 'completed', NOW() - INTERVAL '15 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '14 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '13 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 62.10, 'completed', NOW() - INTERVAL '12 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '11 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 39.90, 'completed', NOW() - INTERVAL '10 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '9 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '8 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 44.50, 'completed', NOW() - INTERVAL '7 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '6 days'),
        (link3_id, 'YOUR_INFLUENCER_USER_ID', 0, 'clicked', NOW() - INTERVAL '5 days');
END $$;

-- 3. Créer des invitations
INSERT INTO invitations (influencer_id, merchant_id, product_id, commission_rate, status, message, created_at, expires_at)
VALUES 
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_MERCHANT_ID_1', 'YOUR_PRODUCT_ID_1', 8.5, 'pending', 
     'Nous aimerions collaborer avec vous pour promouvoir nos produits auprès de votre audience.', 
     NOW() - INTERVAL '5 days', NOW() + INTERVAL '25 days'),
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_MERCHANT_ID_2', 'YOUR_PRODUCT_ID_2', 10.0, 'pending', 
     'Bonjour, votre profil correspond parfaitement à notre marque. Intéressé(e) par un partenariat?', 
     NOW() - INTERVAL '3 days', NOW() + INTERVAL '27 days'),
    ('YOUR_INFLUENCER_USER_ID', 'YOUR_MERCHANT_ID_3', 'YOUR_PRODUCT_ID_3', 7.5, 'accepted', 
     'Nous vous proposons une collaboration exclusive avec un taux de commission attractif.', 
     NOW() - INTERVAL '10 days', NOW() + INTERVAL '20 days');

-- 4. Créer un payout (déjà payé)
INSERT INTO payouts (influencer_id, amount, status, requested_at, paid_at, payment_method, currency)
VALUES 
    ('YOUR_INFLUENCER_USER_ID', 150.00, 'paid', NOW() - INTERVAL '15 days', NOW() - INTERVAL '10 days', 'bank_transfer', 'EUR');

-- 5. Créer une subscription (Plan Pro)
DO $$
DECLARE
    pro_plan_id UUID;
BEGIN
    SELECT id INTO pro_plan_id FROM subscription_plans WHERE name = 'Pro';
    
    IF pro_plan_id IS NOT NULL THEN
        INSERT INTO subscriptions (user_id, plan_id, status, started_at, ends_at)
        VALUES 
            ('YOUR_INFLUENCER_USER_ID', pro_plan_id, 'active', NOW() - INTERVAL '15 days', NOW() + INTERVAL '15 days');
    END IF;
END $$;

-- ============================================
-- PARTIE 2: DONNÉES COMMERCIAL
-- ============================================

-- Note: Remplacer 'YOUR_COMMERCIAL_USER_ID' par un vrai ID d'un user avec role='sales_rep' ou 'commercial'

-- 1. Créer le sales_representative
INSERT INTO sales_representatives (user_id, first_name, last_name, email, territory, commission_rate, target_monthly_deals, target_monthly_revenue, hired_at)
VALUES 
    ('YOUR_COMMERCIAL_USER_ID', 'Mohamed', 'Benali', 'mohamed.benali@tracknow.io', 'Casablanca', 5.0, 20, 100000, NOW() - INTERVAL '6 months');

-- 2. Créer des leads
DO $$
DECLARE
    sales_rep_id UUID;
BEGIN
    SELECT id INTO sales_rep_id FROM sales_representatives WHERE user_id = 'YOUR_COMMERCIAL_USER_ID';
    
    IF sales_rep_id IS NOT NULL THEN
        -- Leads dans différents statuts
        INSERT INTO leads (sales_rep_id, contact_name, contact_email, company_name, lead_status, score, estimated_value, created_at)
        VALUES 
            -- New leads (5)
            (sales_rep_id, 'Ahmed Alami', 'ahmed@techcorp.ma', 'TechCorp Maroc', 'new', 45, 25000, NOW() - INTERVAL '2 days'),
            (sales_rep_id, 'Fatima Zahra', 'fatima@startupma.com', 'StartupMa', 'new', 38, 15000, NOW() - INTERVAL '1 day'),
            (sales_rep_id, 'Youssef Tazi', 'youssef@innovate.ma', 'Innovate Solutions', 'new', 52, 35000, NOW() - INTERVAL '3 days'),
            (sales_rep_id, 'Salma Bennani', 'salma@digitalma.ma', 'Digital Morocco', 'new', 41, 18000, NOW() - INTERVAL '2 days'),
            (sales_rep_id, 'Karim Fassi', 'karim@ecommerce.ma', 'E-Commerce Plus', 'new', 48, 28000, NOW() - INTERVAL '1 day'),
            
            -- Contacted leads (8)
            (sales_rep_id, 'Nadia Cherif', 'nadia@retailshop.ma', 'Retail Shop Maroc', 'contacted', 62, 42000, NOW() - INTERVAL '5 days'),
            (sales_rep_id, 'Omar Benjelloun', 'omar@fashionma.com', 'Fashion Morocco', 'contacted', 55, 32000, NOW() - INTERVAL '6 days'),
            (sales_rep_id, 'Laila Mansouri', 'laila@beautystore.ma', 'Beauty Store', 'contacted', 58, 38000, NOW() - INTERVAL '4 days'),
            (sales_rep_id, 'Hassan Idrissi', 'hassan@techgadgets.ma', 'Tech Gadgets', 'contacted', 51, 27000, NOW() - INTERVAL '7 days'),
            (sales_rep_id, 'Zineb Alaoui', 'zineb@homestyle.ma', 'Home Style', 'contacted', 64, 45000, NOW() - INTERVAL '5 days'),
            (sales_rep_id, 'Mehdi Berrada', 'mehdi@sportszone.ma', 'Sports Zone', 'contacted', 49, 22000, NOW() - INTERVAL '6 days'),
            (sales_rep_id, 'Amina Tahiri', 'amina@kidsworld.ma', 'Kids World', 'contacted', 56, 31000, NOW() - INTERVAL '4 days'),
            (sales_rep_id, 'Rachid Mouline', 'rachid@autoparts.ma', 'Auto Parts Pro', 'contacted', 53, 36000, NOW() - INTERVAL '8 days'),
            
            -- Qualified leads (6)
            (sales_rep_id, 'Samira Bouazza', 'samira@healthcare.ma', 'Healthcare Solutions', 'qualified', 75, 58000, NOW() - INTERVAL '12 days'),
            (sales_rep_id, 'Yassine Lahlou', 'yassine@education.ma', 'Education Plus', 'qualified', 71, 48000, NOW() - INTERVAL '10 days'),
            (sales_rep_id, 'Khadija Aziz', 'khadija@finance.ma', 'Finance Morocco', 'qualified', 78, 65000, NOW() - INTERVAL '14 days'),
            (sales_rep_id, 'Amine Sekkat', 'amine@travel.ma', 'Travel Agency Ma', 'qualified', 68, 41000, NOW() - INTERVAL '11 days'),
            (sales_rep_id, 'Ilham Ziani', 'ilham@restaurant.ma', 'Restaurant Group', 'qualified', 73, 52000, NOW() - INTERVAL '13 days'),
            (sales_rep_id, 'Bilal Kettani', 'bilal@construction.ma', 'Construction Co', 'qualified', 69, 47000, NOW() - INTERVAL '9 days'),
            
            -- Proposal leads (4)
            (sales_rep_id, 'Sofia Idrissi', 'sofia@luxury.ma', 'Luxury Brands Ma', 'proposal', 82, 75000, NOW() - INTERVAL '18 days'),
            (sales_rep_id, 'Tarik Hamdaoui', 'tarik@electronics.ma', 'Electronics Hub', 'proposal', 79, 68000, NOW() - INTERVAL '16 days'),
            (sales_rep_id, 'Meryem Naciri', 'meryem@furniture.ma', 'Furniture Palace', 'proposal', 81, 72000, NOW() - INTERVAL '17 days'),
            (sales_rep_id, 'Adil Bensouda', 'adil@jewelry.ma', 'Jewelry Boutique', 'proposal', 76, 61000, NOW() - INTERVAL '15 days'),
            
            -- Negotiation leads (3)
            (sales_rep_id, 'Hanae Chraibi', 'hanae@pharma.ma', 'Pharma Distribution', 'negotiation', 88, 95000, NOW() - INTERVAL '22 days'),
            (sales_rep_id, 'Samir Berrada', 'samir@wholesale.ma', 'Wholesale Morocco', 'negotiation', 85, 88000, NOW() - INTERVAL '20 days'),
            (sales_rep_id, 'Imane Lahlou', 'imane@cosmetics.ma', 'Cosmetics Empire', 'negotiation', 87, 92000, NOW() - INTERVAL '21 days');
    END IF;
END $$;

-- 3. Créer des deals
DO $$
DECLARE
    sales_rep_id UUID;
    lead_id UUID;
BEGIN
    SELECT id INTO sales_rep_id FROM sales_representatives WHERE user_id = 'YOUR_COMMERCIAL_USER_ID';
    
    IF sales_rep_id IS NOT NULL THEN
        -- Deals Won (8 ce mois)
        INSERT INTO deals (sales_rep_id, contact_name, company_name, value, status, stage, probability, expected_close_date, closed_date, created_at)
        VALUES 
            (sales_rep_id, 'Client Won 1', 'Company A', 45000, 'won', 'closing', 100, NOW() - INTERVAL '10 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '30 days'),
            (sales_rep_id, 'Client Won 2', 'Company B', 38000, 'won', 'closing', 100, NOW() - INTERVAL '12 days', NOW() - INTERVAL '8 days', NOW() - INTERVAL '35 days'),
            (sales_rep_id, 'Client Won 3', 'Company C', 52000, 'won', 'closing', 100, NOW() - INTERVAL '8 days', NOW() - INTERVAL '3 days', NOW() - INTERVAL '28 days'),
            (sales_rep_id, 'Client Won 4', 'Company D', 41000, 'won', 'closing', 100, NOW() - INTERVAL '14 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '40 days'),
            (sales_rep_id, 'Client Won 5', 'Company E', 48000, 'won', 'closing', 100, NOW() - INTERVAL '6 days', NOW() - INTERVAL '2 days', NOW() - INTERVAL '25 days'),
            (sales_rep_id, 'Client Won 6', 'Company F', 55000, 'won', 'closing', 100, NOW() - INTERVAL '15 days', NOW() - INTERVAL '12 days', NOW() - INTERVAL '42 days'),
            (sales_rep_id, 'Client Won 7', 'Company G', 43000, 'won', 'closing', 100, NOW() - INTERVAL '9 days', NOW() - INTERVAL '4 days', NOW() - INTERVAL '32 days'),
            (sales_rep_id, 'Client Won 8', 'Company H', 50000, 'won', 'closing', 100, NOW() - INTERVAL '7 days', NOW() - INTERVAL '1 day', NOW() - INTERVAL '27 days'),
            
            -- Deals Open (5)
            (sales_rep_id, 'Client Prospect 1', 'Prospect A', 65000, 'open', 'negotiation', 75, NOW() + INTERVAL '10 days', NULL, NOW() - INTERVAL '20 days'),
            (sales_rep_id, 'Client Prospect 2', 'Prospect B', 58000, 'open', 'proposal', 60, NOW() + INTERVAL '15 days', NULL, NOW() - INTERVAL '18 days'),
            (sales_rep_id, 'Client Prospect 3', 'Prospect C', 72000, 'open', 'negotiation', 80, NOW() + INTERVAL '8 days', NULL, NOW() - INTERVAL '22 days'),
            (sales_rep_id, 'Client Prospect 4', 'Prospect D', 48000, 'open', 'qualification', 50, NOW() + INTERVAL '20 days', NULL, NOW() - INTERVAL '15 days'),
            (sales_rep_id, 'Client Prospect 5', 'Prospect E', 85000, 'open', 'negotiation', 85, NOW() + INTERVAL '5 days', NULL, NOW() - INTERVAL '25 days'),
            
            -- Deals Lost (2)
            (sales_rep_id, 'Client Lost 1', 'Lost Company A', 35000, 'lost', 'negotiation', 0, NOW() - INTERVAL '5 days', NOW() - INTERVAL '3 days', NOW() - INTERVAL '45 days'),
            (sales_rep_id, 'Client Lost 2', 'Lost Company B', 28000, 'lost', 'proposal', 0, NOW() - INTERVAL '8 days', NOW() - INTERVAL '6 days', NOW() - INTERVAL '50 days');
    END IF;
END $$;

-- 4. Créer des activités (calls, meetings, tasks)
DO $$
DECLARE
    sales_rep_id UUID;
BEGIN
    SELECT id INTO sales_rep_id FROM sales_representatives WHERE user_id = 'YOUR_COMMERCIAL_USER_ID';
    
    IF sales_rep_id IS NOT NULL THEN
        -- Appels ce mois (45 appels)
        INSERT INTO sales_activities (sales_rep_id, activity_type, subject, outcome, completed_at, duration_minutes, created_at)
        SELECT 
            sales_rep_id,
            'call',
            'Appel de prospection',
            'completed',
            NOW() - (random() * INTERVAL '30 days'),
            FLOOR(random() * 30 + 5)::INTEGER,
            NOW() - (random() * INTERVAL '30 days')
        FROM generate_series(1, 45);
        
        -- Meetings ce mois (12 meetings)
        INSERT INTO sales_activities (sales_rep_id, activity_type, subject, outcome, completed_at, duration_minutes, created_at)
        SELECT 
            sales_rep_id,
            'meeting',
            'Rendez-vous client',
            'completed',
            NOW() - (random() * INTERVAL '30 days'),
            FLOOR(random() * 60 + 30)::INTEGER,
            NOW() - (random() * INTERVAL '30 days')
        FROM generate_series(1, 12);
        
        -- Calls scheduled today (3)
        INSERT INTO sales_activities (sales_rep_id, activity_type, subject, outcome, scheduled_at, created_at)
        VALUES 
            (sales_rep_id, 'call', 'Appel de suivi - TechCorp', 'scheduled', NOW() + INTERVAL '2 hours', NOW()),
            (sales_rep_id, 'call', 'Appel prospection - StartupMa', 'scheduled', NOW() + INTERVAL '4 hours', NOW()),
            (sales_rep_id, 'call', 'Appel closing - Luxury Brands', 'scheduled', NOW() + INTERVAL '6 hours', NOW());
        
        -- Meetings scheduled today (2)
        INSERT INTO sales_activities (sales_rep_id, activity_type, subject, outcome, scheduled_at, created_at)
        VALUES 
            (sales_rep_id, 'meeting', 'Meeting présentation - Pharma Distribution', 'scheduled', NOW() + INTERVAL '3 hours', NOW()),
            (sales_rep_id, 'meeting', 'Meeting négociation - Wholesale Morocco', 'scheduled', NOW() + INTERVAL '5 hours', NOW());
        
        -- Tasks pending (4)
        INSERT INTO sales_activities (sales_rep_id, activity_type, subject, outcome, scheduled_at, created_at)
        VALUES 
            (sales_rep_id, 'task', 'Envoyer devis - Company A', 'scheduled', NOW(), NOW()),
            (sales_rep_id, 'task', 'Préparer proposition - Company B', 'scheduled', NOW(), NOW()),
            (sales_rep_id, 'task', 'Relancer lead - Company C', 'scheduled', NOW(), NOW()),
            (sales_rep_id, 'task', 'Compléter CRM - Company D', 'scheduled', NOW(), NOW());
    END IF;
END $$;

-- 5. Créer des targets
DO $$
DECLARE
    sales_rep_id UUID;
BEGIN
    SELECT id INTO sales_rep_id FROM sales_representatives WHERE user_id = 'YOUR_COMMERCIAL_USER_ID';
    
    IF sales_rep_id IS NOT NULL THEN
        -- Target mensuel (mois actuel)
        INSERT INTO sales_targets (sales_rep_id, period_type, period_start, period_end, deals_target, revenue_target, calls_target, meetings_target)
        VALUES 
            (sales_rep_id, 'monthly', date_trunc('month', NOW()), date_trunc('month', NOW()) + INTERVAL '1 month', 20, 100000, 100, 30);
    END IF;
END $$;

-- ============================================
-- AFFICHER RÉSUMÉ DES DONNÉES CRÉÉES
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'DONNÉES DE TEST CRÉÉES AVEC SUCCÈS!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'INFLUENCEUR:';
    RAISE NOTICE '- % tracking_links créés', (SELECT COUNT(*) FROM tracking_links);
    RAISE NOTICE '- % conversions créées', (SELECT COUNT(*) FROM conversions);
    RAISE NOTICE '- % invitations créées', (SELECT COUNT(*) FROM invitations);
    RAISE NOTICE '- % payouts créés', (SELECT COUNT(*) FROM payouts);
    RAISE NOTICE '';
    RAISE NOTICE 'COMMERCIAL:';
    RAISE NOTICE '- % sales_representatives créés', (SELECT COUNT(*) FROM sales_representatives);
    RAISE NOTICE '- % leads créés', (SELECT COUNT(*) FROM leads);
    RAISE NOTICE '- % deals créés', (SELECT COUNT(*) FROM deals);
    RAISE NOTICE '- % activities créées', (SELECT COUNT(*) FROM sales_activities);
    RAISE NOTICE '- % targets créés', (SELECT COUNT(*) FROM sales_targets);
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'PROCHAINE ÉTAPE:';
    RAISE NOTICE 'Tester les endpoints dans Postman ou le frontend';
    RAISE NOTICE '========================================';
END $$;
