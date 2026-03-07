-- ============================================
-- SCRIPT 1/4 : INSERTION DES DONNÉES DE TEST - UTILISATEURS
-- PARTIE 1 : Users, Merchants, Influencers, Commerciaux
-- ============================================

-- ============================================
-- 1. INSERTION DES UTILISATEURS (Admin, Merchants, Influencers, Commerciaux)
-- ============================================

-- Admin
INSERT INTO public.users (id, email, password_hash, role, full_name, company_name, phone, is_active, is_verified, subscription_plan, created_at)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'admin@getyourshare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'admin', 'John Admin', 'GetYourShare', '+33612345678', true, true, 'Elite', NOW() - INTERVAL '6 months');

-- Marchands (Merchants)
INSERT INTO public.users (id, email, password_hash, role, full_name, company_name, phone, is_active, is_verified, subscription_plan, budget, monthly_budget, commission_rate, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222222', 'merchant1@fashionstore.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'merchant', 'Sophie Martin', 'Fashion Store Paris', '+33612345001', true, true, 'Pro', 50000.00, 5000.00, 12.00, NOW() - INTERVAL '5 months'),
    ('22222222-2222-2222-2222-222222222223', 'merchant2@techgadgets.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'merchant', 'Marc Dubois', 'Tech Gadgets Pro', '+33612345002', true, true, 'Elite', 100000.00, 10000.00, 15.00, NOW() - INTERVAL '4 months'),
    ('22222222-2222-2222-2222-222222222224', 'merchant3@beautyparis.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'merchant', 'Julie Leclerc', 'Beauty Paris', '+33612345003', true, true, 'Pro', 30000.00, 3000.00, 10.00, NOW() - INTERVAL '3 months'),
    ('22222222-2222-2222-2222-222222222225', 'merchant4@sportshop.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'merchant', 'Thomas Bernard', 'Sport Shop Elite', '+33612345004', true, true, 'Free', 15000.00, 1500.00, 8.00, NOW() - INTERVAL '2 months'),
    ('22222222-2222-2222-2222-222222222226', 'merchant5@fooddelights.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'merchant', 'Emma Rousseau', 'Food Delights', '+33612345005', true, true, 'Pro', 40000.00, 4000.00, 11.00, NOW() - INTERVAL '1 month');

-- Influenceurs
INSERT INTO public.users (id, email, password_hash, role, full_name, phone, is_active, is_verified, subscription_plan, instagram_handle, tiktok_handle, youtube_handle, twitter_handle, followers_count, engagement_rate, niche, bio, location, website, created_at)
VALUES 
    ('33333333-3333-3333-3333-333333333333', 'influencer1@fashion.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'influencer', 'Marie Dupont', '+33612340001', true, true, 'Pro', '@marie_fashion', '@mariestyle', 'MarieFashionTV', '@mariefashion', 250000, 4.5, ARRAY['Fashion', 'Beauty'], 'Passionnée de mode et beauté 🌟', 'Paris, France', 'https://mariefashion.com', NOW() - INTERVAL '8 months'),
    ('33333333-3333-3333-3333-333333333334', 'influencer2@tech.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'influencer', 'Pierre Tech', '+33612340002', true, true, 'Elite', '@pierre_tech', '@pierretech', 'PierreTechReview', '@pierretech', 500000, 5.2, ARRAY['Tech'], 'Expert tech et gadgets 💻📱', 'Lyon, France', 'https://pierretech.fr', NOW() - INTERVAL '10 months'),
    ('33333333-3333-3333-3333-333333333335', 'influencer3@lifestyle.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'influencer', 'Laura Lifestyle', '+33612340003', true, true, 'Pro', '@laura_life', '@lauralifestyle', 'LauraLife', '@lauralife', 180000, 3.8, ARRAY['Home', 'Travel'], 'Lifestyle & Travel Blogger ✈️🏡', 'Nice, France', 'https://lauralife.com', NOW() - INTERVAL '7 months'),
    ('33333333-3333-3333-3333-333333333336', 'influencer4@fitness.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'influencer', 'Alex Fitness', '+33612340004', true, true, 'Free', '@alex_fit', '@alexfitness', 'AlexFitPro', '@alexfit', 120000, 4.2, ARRAY['Sports'], 'Coach sportif & nutrition 💪🥗', 'Marseille, France', 'https://alexfitness.fr', NOW() - INTERVAL '5 months'),
    ('33333333-3333-3333-3333-333333333337', 'influencer5@food.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'influencer', 'Chef Antoine', '+33612340005', true, true, 'Pro', '@chef_antoine', '@chefantoine', 'ChefAntoineCuisine', '@chefantoine', 300000, 4.8, ARRAY['Food'], 'Chef cuisinier & Food Blogger 👨‍🍳🍽️', 'Bordeaux, France', 'https://chefantoine.com', NOW() - INTERVAL '9 months');

-- Commerciaux (Sales Representatives)
INSERT INTO public.users (id, email, password_hash, role, full_name, phone, is_active, is_verified, subscription_plan, commission_rate, created_at)
VALUES 
    ('44444444-4444-4444-4444-444444444444', 'commercial1@getyourshare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'commercial', 'Lucas Commercial', '+33612350001', true, true, 'Elite', 5.00, NOW() - INTERVAL '6 months'),
    ('44444444-4444-4444-4444-444444444445', 'commercial2@getyourshare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'commercial', 'Claire Vente', '+33612350002', true, true, 'Elite', 5.50, NOW() - INTERVAL '5 months'),
    ('44444444-4444-4444-4444-444444444446', 'commercial3@getyourshare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy', 'commercial', 'David Sales', '+33612350003', true, true, 'Elite', 4.50, NOW() - INTERVAL '4 months');

-- ============================================
-- 2. INSERTION DES DÉTAILS MERCHANTS
-- ============================================
INSERT INTO public.merchants (id, user_id, company_name, business_type, industry, website, description, logo_url, commission_rate, monthly_budget, total_spent, rating, total_sales, is_verified, created_at)
VALUES 
    (gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'Fashion Store Paris', 'E-commerce', 'Fashion', 'https://fashionstore.com', 'Boutique de mode parisienne proposant les dernières tendances', 'https://via.placeholder.com/150/FF6B9D/FFFFFF?text=FS', 12.00, 5000.00, 23500.50, 4.5, 156, true, NOW() - INTERVAL '5 months'),
    (gen_random_uuid(), '22222222-2222-2222-2222-222222222223', 'Tech Gadgets Pro', 'E-commerce', 'Technology', 'https://techgadgets.com', 'Leader des gadgets high-tech et électronique', 'https://via.placeholder.com/150/4A90E2/FFFFFF?text=TG', 15.00, 10000.00, 45780.00, 4.8, 289, true, NOW() - INTERVAL '4 months'),
    (gen_random_uuid(), '22222222-2222-2222-2222-222222222224', 'Beauty Paris', 'E-commerce', 'Beauty', 'https://beautyparis.com', 'Produits de beauté et cosmétiques premium', 'https://via.placeholder.com/150/F5A623/FFFFFF?text=BP', 10.00, 3000.00, 12340.75, 4.3, 98, true, NOW() - INTERVAL '3 months'),
    (gen_random_uuid(), '22222222-2222-2222-2222-222222222225', 'Sport Shop Elite', 'Retail', 'Sports', 'https://sportshop.com', 'Équipement sportif pour tous les niveaux', 'https://via.placeholder.com/150/7ED321/FFFFFF?text=SS', 8.00, 1500.00, 8920.00, 4.1, 67, true, NOW() - INTERVAL '2 months'),
    (gen_random_uuid(), '22222222-2222-2222-2222-222222222226', 'Food Delights', 'E-commerce', 'Food', 'https://fooddelights.com', 'Produits gastronomiques et spécialités françaises', 'https://via.placeholder.com/150/D0021B/FFFFFF?text=FD', 11.00, 4000.00, 18650.25, 4.6, 134, true, NOW() - INTERVAL '1 month');

-- ============================================
-- 3. INSERTION DES DÉTAILS INFLUENCERS
-- ============================================
INSERT INTO public.influencers (id, user_id, instagram_handle, tiktok_handle, youtube_handle, twitter_handle, followers_count, engagement_rate, niche, audience_size, avg_views, content_style, rating, total_collaborations, total_earnings, bio, created_at)
VALUES 
    (gen_random_uuid(), '33333333-3333-3333-3333-333333333333', '@marie_fashion', '@mariestyle', 'MarieFashionTV', '@mariefashion', 250000, 4.5, ARRAY['Fashion', 'Beauty'], 280000, 35000, 'Lifestyle & Fashion', 4.7, 45, 12500.00, 'Passionnée de mode et beauté 🌟', NOW() - INTERVAL '8 months'),
    (gen_random_uuid(), '33333333-3333-3333-3333-333333333334', '@pierre_tech', '@pierretech', 'PierreTechReview', '@pierretech', 500000, 5.2, ARRAY['Tech'], 550000, 75000, 'Tech Reviews', 4.9, 67, 28750.50, 'Expert tech et gadgets 💻📱', NOW() - INTERVAL '10 months'),
    (gen_random_uuid(), '33333333-3333-3333-3333-333333333335', '@laura_life', '@lauralifestyle', 'LauraLife', '@lauralife', 180000, 3.8, ARRAY['Home', 'Travel'], 200000, 22000, 'Lifestyle Vlogs', 4.4, 32, 8900.75, 'Lifestyle & Travel Blogger ✈️🏡', NOW() - INTERVAL '7 months'),
    (gen_random_uuid(), '33333333-3333-3333-3333-333333333336', '@alex_fit', '@alexfitness', 'AlexFitPro', '@alexfit', 120000, 4.2, ARRAY['Sports'], 135000, 18000, 'Fitness Training', 4.5, 28, 6200.00, 'Coach sportif & nutrition 💪🥗', NOW() - INTERVAL '5 months'),
    (gen_random_uuid(), '33333333-3333-3333-3333-333333333337', '@chef_antoine', '@chefantoine', 'ChefAntoineCuisine', '@chefantoine', 300000, 4.8, ARRAY['Food'], 320000, 45000, 'Cooking Tutorials', 4.8, 52, 15600.25, 'Chef cuisinier & Food Blogger 👨‍🍳🍽️', NOW() - INTERVAL '9 months');

-- ============================================
-- 4. INSERTION DES SALES REPRESENTATIVES (Commerciaux)
-- ============================================
INSERT INTO public.sales_representatives (id, user_id, territory, quota, commission_rate, is_active, created_at)
VALUES 
    (gen_random_uuid(), '44444444-4444-4444-4444-444444444444', 'Paris & Île-de-France', 50000.00, 5.00, true, NOW() - INTERVAL '6 months'),
    (gen_random_uuid(), '44444444-4444-4444-4444-444444444445', 'Sud de la France', 45000.00, 5.50, true, NOW() - INTERVAL '5 months'),
    (gen_random_uuid(), '44444444-4444-4444-4444-444444444446', 'Ouest & Centre', 40000.00, 4.50, true, NOW() - INTERVAL '4 months');

-- ============================================
-- 5. INSERTION DES SUBSCRIPTIONS POUR LES UTILISATEURS
-- ============================================
INSERT INTO public.subscriptions (user_id, plan_id, status, current_period_start, current_period_end, created_at)
SELECT 
    u.id,
    (SELECT id FROM public.subscription_plans WHERE name = u.subscription_plan LIMIT 1),
    'active',
    NOW() - INTERVAL '1 month',
    NOW() + INTERVAL '1 month',
    u.created_at
FROM public.users u
WHERE u.subscription_plan IN ('Free', 'Pro', 'Elite');

-- ============================================
-- 6. INSERTION DES PROFILS KYC
-- ============================================
INSERT INTO public.user_kyc_profile (user_id, kyc_status, verification_level, documents_verified, created_at)
SELECT id, 'approved', 3, true, created_at
FROM public.users
WHERE role IN ('merchant', 'influencer', 'commercial') AND is_verified = true;

-- ============================================
-- 7. INSERTION DES TRUST SCORES
-- ============================================
INSERT INTO public.trust_scores (user_id, score, factors, last_calculated_at, created_at)
SELECT 
    id, 
    CASE 
        WHEN role = 'admin' THEN 100
        WHEN role = 'commercial' THEN 95
        WHEN role = 'merchant' THEN 85 + (RANDOM() * 10)::INTEGER
        WHEN role = 'influencer' THEN 80 + (RANDOM() * 15)::INTEGER
        ELSE 50
    END,
    jsonb_build_object(
        'verified_account', true,
        'completed_collaborations', RANDOM() * 50,
        'positive_reviews', RANDOM() * 100,
        'response_rate', 85 + RANDOM() * 15
    ),
    NOW(),
    created_at
FROM public.users;

-- ============================================
-- FIN DU SCRIPT PARTIE 1
-- ============================================
-- Utilisateurs créés: 1 Admin + 5 Merchants + 5 Influencers + 3 Commerciaux = 14 utilisateurs
-- Prêt pour la PARTIE 2: Produits, Services, Campagnes
-- ============================================
