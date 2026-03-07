-- ============================================
-- POPULATION DES DONNÉES POUR LES NOUVELLES FONCTIONNALITÉS
-- (AI, Social Tools, Directories)
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '🚀 Démarrage de la population des données pour les nouvelles fonctionnalités...';
END $$;

-- ============================================
-- 1. ADMIN SOCIAL POSTS
-- ============================================
INSERT INTO admin_social_posts (created_by, title, caption, media_type, campaign_type, status, scheduled_for, published_at, total_views, total_likes)
VALUES
-- Post publié
('11111111-1111-1111-1111-111111111111', 'Lancement Officiel', '🚀 ShareYourSales est officiellement lancé ! Rejoignez la révolution du commerce social au Maroc. 🇲🇦 #ShareYourSales #Maroc #Ecommerce', 'image', 'app_launch', 'published', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', 1500, 340),

-- Post planifié
('11111111-1111-1111-1111-111111111111', 'Webinar Influenceurs', '📅 Ne manquez pas notre webinar exclusif pour les influenceurs ce samedi ! Comment maximiser vos revenus avec l''affiliation. 💰', 'image', 'influencer_recruitment', 'scheduled', NOW() + INTERVAL '2 days', NULL, 0, 0),

-- Brouillon
('11111111-1111-1111-1111-111111111111', 'Promo Été', 'Préparez-vous pour les soldes d''été... (à compléter)', 'image', 'seasonal_promo', 'draft', NULL, NULL, 0, 0),

-- Post recrutement marchands
('11111111-1111-1111-1111-111111111111', 'Appel aux Marchands', '🏪 Commerçants, boostez vos ventes sans risque ! Payez uniquement à la commission. Inscrivez-vous aujourd''hui.', 'carousel', 'merchant_recruitment', 'published', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', 2300, 120);

-- ============================================
-- 2. COMMERCIAL PROFILES
-- ============================================
INSERT INTO commercial_profiles (user_id, headline, bio, city, specialties, years_of_experience, is_available, is_public)
VALUES
('44444444-4444-4444-4444-444444444441', 'Expert Vente B2B & Tech', 'Passionné par la technologie et la vente consultative. J''aide les entreprises tech à croître.', 'Casablanca', '["SaaS", "B2B", "Tech"]', 5, true, true),
('44444444-4444-4444-4444-444444444442', 'Spécialiste Retail & Distribution', '10 ans d''expérience dans le développement de réseaux de distribution au Maroc.', 'Rabat', '["Retail", "FMCG", "Distribution"]', 10, true, true),
('44444444-4444-4444-4444-444444444443', 'Business Developer Senior', 'Expert en négociation et partenariats stratégiques.', 'Marrakech', '["Real Estate", "Luxury", "Hospitality"]', 8, false, true),
('44444444-4444-4444-4444-444444444444', 'Sales Manager', 'Gestion d''équipes commerciales et stratégie de vente.', 'Tanger', '["Management", "Strategy", "Automotive"]', 12, true, true),
('44444444-4444-4444-4444-444444444445', 'Commercial Terrain', 'Proactif et orienté résultats. Je couvre la région Nord.', 'Tétouan', '["Field Sales", "Pharma", "Medical"]', 3, true, true),
('44444444-4444-4444-4444-444444444446', 'Key Account Manager', 'Gestion des grands comptes et fidélisation client.', 'Casablanca', '["Key Accounts", "Banking", "Insurance"]', 7, true, true)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- 3. INFLUENCER PROFILES
-- ============================================
INSERT INTO influencer_profiles (user_id, display_name, headline, bio, city, niches, instagram_handle, instagram_followers, instagram_engagement_rate, is_public)
VALUES
('33333333-3333-3333-3333-333333333333', 'Sarah Lifestyle', 'Fashion & Lifestyle Blogger', 'Partage mes coups de cœur mode et lifestyle à Casablanca.', 'Casablanca', '["Fashion", "Lifestyle", "Beauty"]', '@sarah_lifestyle', 45000, 8.5, true),
('33333333-3333-3333-3333-333333333334', 'Ahmed Tech', 'Tech Reviewer Maroc', 'Tests de smartphones, gadgets et actus tech.', 'Rabat', '["Tech", "Gaming", "Gadgets"]', '@ahmed_tech', 78000, 6.2, true),
('33333333-3333-3333-3333-333333333335', 'Fatima Beauty', 'Makeup Artist & Tips', 'Tutoriels maquillage et soins de la peau.', 'Marrakech', '["Beauty", "Skincare", "Makeup"]', '@fatima_beauty', 62000, 9.1, true),
('33333333-3333-3333-3333-333333333336', 'Youssef Fashion', 'Men Style Guide', 'Conseils mode pour hommes élégants.', 'Casablanca', '["Fashion", "Men Style", "Luxury"]', '@youssef_fashion', 95000, 7.8, true),
('33333333-3333-3333-3333-333333333337', 'Nadia Travel', 'Travel & Food', 'Découverte des meilleurs endroits au Maroc et ailleurs.', 'Agadir', '["Travel", "Food", "Lifestyle"]', '@nadia_travel', 120000, 10.2, true),
('66666666-6666-6666-6666-666666666661', 'Karim Fitness', 'Coach Sportif', 'Motivation, entraînements et nutrition.', 'Casablanca', '["Fitness", "Health", "Sport"]', '@karim_fit', 88000, 7.5, true),
('77777777-7777-7777-7777-777777777771', 'Leila Food', 'Recettes Marocaines', 'Cuisine traditionnelle et moderne.', 'Fès', '["Food", "Cooking", "Recipes"]', '@leila_food', 105000, 8.9, true)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- 4. INFLUENCER PREFERENCES (AI)
-- ============================================
INSERT INTO influencer_preferences (user_id, preferred_categories, audience_age_range, preferred_platforms, min_commission_rate)
VALUES
('33333333-3333-3333-3333-333333333333', ARRAY['Fashion', 'Beauty'], '18-34', ARRAY['instagram', 'tiktok'], 10.0),
('33333333-3333-3333-3333-333333333334', ARRAY['Electronics', 'Gaming'], '18-45', ARRAY['youtube', 'twitter'], 5.0),
('33333333-3333-3333-3333-333333333335', ARRAY['Beauty', 'Wellness'], '25-45', ARRAY['instagram', 'facebook'], 15.0)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- 5. COLLABORATION REQUESTS
-- ============================================
INSERT INTO collaboration_requests (company_id, target_user_id, target_type, message, status, proposed_budget)
VALUES
-- Merchant 1 -> Influencer 1
('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', 'influencer', 'Bonjour Sarah, nous aimerions collaborer pour notre nouvelle collection été.', 'pending', 2000.00),
-- Merchant 2 -> Influencer 2
('22222222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333334', 'influencer', 'Salut Ahmed, intéressé pour tester nos nouveaux écouteurs ?', 'accepted', 1500.00),
-- Merchant 3 -> Commercial 1
('22222222-2222-2222-2222-222222222224', '44444444-4444-4444-4444-444444444441', 'commercial', 'Nous cherchons un expert B2B pour développer notre réseau.', 'negotiating', 5000.00);

-- ============================================
-- 6. PROFILE REVIEWS
-- ============================================
INSERT INTO profile_reviews (profile_user_id, profile_type, reviewer_id, rating, title, comment, professionalism_rating, communication_rating, results_rating, is_public)
VALUES
-- Review sur Influencer 1
('33333333-3333-3333-3333-333333333333', 'influencer', '22222222-2222-2222-2222-222222222224', 5, 'Excellente collaboration', 'Sarah est très professionnelle et sa communauté est très engagée. ROI positif !', 5, 5, 5, true),
-- Review sur Commercial 1
('44444444-4444-4444-4444-444444444441', 'commercial', '22222222-2222-2222-2222-222222222226', 4, 'Bon commercial', 'Karim connaît bien son métier. Résultats satisfaisants.', 5, 4, 4, true);

-- ============================================
-- 7. LIVE SHOPPING SESSIONS
-- ============================================
INSERT INTO live_shopping_sessions (host_id, title, description, platform, status, scheduled_at, commission_boost_percentage)
VALUES
('22222222-2222-2222-2222-222222222224', 'Fashion Show Live', 'Découvrez notre nouvelle collection en direct !', 'instagram', 'scheduled', NOW() + INTERVAL '3 days', 10.0),
('22222222-2222-2222-2222-222222222225', 'Tech Unboxing', 'Déballage des derniers gadgets arrivés en stock.', 'tiktok', 'ended', NOW() - INTERVAL '2 days', 5.0);

-- ============================================
-- 8. AI CONTENT TEMPLATES
-- ============================================
INSERT INTO ai_content_templates (user_id, platform, content_type, title, content, hashtags, generated_by)
VALUES
('33333333-3333-3333-3333-333333333333', 'instagram', 'post', 'Idée Post Mode', '✨ Le style n''est pas une question de marque, c''est une question d''attitude. Découvrez ma sélection du jour ! 👇', ARRAY['#fashion', '#style', '#ootd'], 'gpt-4'),
('22222222-2222-2222-2222-222222222222', 'facebook', 'post', 'Promo Flash', '🚨 VENTE FLASH ! -20% sur tout le magasin pendant 24h seulement. Profitez-en vite ! 🏃‍♂️', ARRAY['#promo', '#soldes', '#deal'], 'gpt-4');

-- ============================================
-- 9. PRODUCT RECOMMENDATIONS (Générer via fonction si possible, sinon insert manuel)
-- ============================================
-- On appelle la fonction pour générer des recs pour quelques influenceurs
SELECT generate_product_recommendations('33333333-3333-3333-3333-333333333333');
SELECT generate_product_recommendations('33333333-3333-3333-3333-333333333334');

DO $$
BEGIN
    RAISE NOTICE '✅ Population des données terminée avec succès !';
END $$;
