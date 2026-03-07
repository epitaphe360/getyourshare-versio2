-- ============================================
-- SCRIPT 4/4 : INSERTION DES DONNÉES DE TEST - ÉCOSYSTÈME COMPLET
-- PARTIE 4 : Social Media, Gamification, Messages, Reviews, Analytics, Admin
-- ============================================

-- ============================================
-- 1. SOCIAL CONNECTIONS (Comptes sociaux des influenceurs)
-- ============================================
INSERT INTO public.social_connections (influencer_id, platform, username, platform_user_id, followers_count, is_connected, last_synced_at, metadata, created_at)
VALUES 
    -- Marie Fashion (influencer 1)
    ('33333333-3333-3333-3333-333333333333', 'instagram', 'marie_fashion_paris', 'ig_marie_fashion', 250000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://instagram.com/marie_fashion_paris", "engagement_rate": 4.5, "is_verified": true}'::jsonb, NOW() - INTERVAL '6 months'),
    ('33333333-3333-3333-3333-333333333333', 'tiktok', 'mariefashion', 'tt_mariefashion', 180000, true, NOW() - INTERVAL '2 days', '{"profile_url": "https://tiktok.com/@mariefashion", "engagement_rate": 6.2, "is_verified": true}'::jsonb, NOW() - INTERVAL '5 months'),
    ('33333333-3333-3333-3333-333333333333', 'youtube', 'MarieFashionTV', 'yt_mariefashiontv', 95000, true, NOW() - INTERVAL '3 days', '{"profile_url": "https://youtube.com/c/MarieFashionTV", "engagement_rate": 3.8, "is_verified": false}'::jsonb, NOW() - INTERVAL '4 months'),
    
    -- Pierre Tech (influencer 2)
    ('33333333-3333-3333-3333-333333333334', 'instagram', 'pierre_tech_review', 'ig_pierre_tech', 500000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://instagram.com/pierre_tech_review", "engagement_rate": 5.8, "is_verified": true}'::jsonb, NOW() - INTERVAL '8 months'),
    ('33333333-3333-3333-3333-333333333334', 'youtube', 'PierreTechReviews', 'yt_pierretech', 450000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://youtube.com/c/PierreTechReviews", "engagement_rate": 7.2, "is_verified": true}'::jsonb, NOW() - INTERVAL '7 months'),
    ('33333333-3333-3333-3333-333333333334', 'twitter', 'PierreTech', 'tw_pierretech', 120000, true, NOW() - INTERVAL '2 days', '{"profile_url": "https://twitter.com/PierreTech", "engagement_rate": 4.1, "is_verified": true}'::jsonb, NOW() - INTERVAL '6 months'),
    
    -- Laura Lifestyle (influencer 3)
    ('33333333-3333-3333-3333-333333333335', 'instagram', 'laura_lifestyle', 'ig_laura_lifestyle', 180000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://instagram.com/laura_lifestyle", "engagement_rate": 5.2, "is_verified": true}'::jsonb, NOW() - INTERVAL '5 months'),
    ('33333333-3333-3333-3333-333333333335', 'tiktok', 'lauralifestyle', 'tt_lauralifestyle', 220000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://tiktok.com/@lauralifestyle", "engagement_rate": 8.5, "is_verified": true}'::jsonb, NOW() - INTERVAL '4 months'),
    
    -- Alex Fitness (influencer 4)
    ('33333333-3333-3333-3333-333333333336', 'instagram', 'alex_fitness_coach', 'ig_alex_fitness', 120000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://instagram.com/alex_fitness_coach", "engagement_rate": 6.8, "is_verified": true}'::jsonb, NOW() - INTERVAL '4 months'),
    ('33333333-3333-3333-3333-333333333336', 'youtube', 'AlexFitnessChannel', 'yt_alex_fitness', 85000, true, NOW() - INTERVAL '2 days', '{"profile_url": "https://youtube.com/c/AlexFitnessChannel", "engagement_rate": 5.5, "is_verified": false}'::jsonb, NOW() - INTERVAL '3 months'),
    ('33333333-3333-3333-3333-333333333336', 'tiktok', 'alexfitness', 'tt_alexfitness', 95000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://tiktok.com/@alexfitness", "engagement_rate": 7.9, "is_verified": true}'::jsonb, NOW() - INTERVAL '2 months'),
    
    -- Chef Antoine (influencer 5)
    ('33333333-3333-3333-3333-333333333337', 'instagram', 'chef_antoine_cuisine', 'ig_chef_antoine', 300000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://instagram.com/chef_antoine_cuisine", "engagement_rate": 5.4, "is_verified": true}'::jsonb, NOW() - INTERVAL '7 months'),
    ('33333333-3333-3333-3333-333333333337', 'youtube', 'ChefAntoineCuisine', 'yt_chef_antoine', 280000, true, NOW() - INTERVAL '1 day', '{"profile_url": "https://youtube.com/c/ChefAntoineCuisine", "engagement_rate": 6.1, "is_verified": true}'::jsonb, NOW() - INTERVAL '6 months'),
    ('33333333-3333-3333-3333-333333333337', 'facebook', 'ChefAntoine', 'fb_chef_antoine', 150000, true, NOW() - INTERVAL '3 days', '{"profile_url": "https://facebook.com/ChefAntoine", "engagement_rate": 3.2, "is_verified": false}'::jsonb, NOW() - INTERVAL '5 months');

-- ============================================
-- 2. SOCIAL MEDIA STATS (Statistiques historiques)
-- ============================================
INSERT INTO public.social_media_stats (connection_id, date, followers_count, engagement_rate, impressions, reach, posts_count, created_at)
SELECT 
    sc.id,
    generate_series(NOW() - INTERVAL '30 days', NOW(), INTERVAL '5 days')::date,
    sc.followers_count + floor(random() * 1000 - 500)::integer,
    (random() * 10 + 2)::decimal(5,2),
    floor(random() * 500000 + 50000)::integer,
    floor(random() * 300000 + 30000)::integer,
    floor(random() * 20 + 5)::integer,
    NOW()
FROM public.social_connections sc
LIMIT 50;

-- ============================================
-- 3. INVITATIONS (10 invitations merchant→influencer)
-- ============================================
INSERT INTO public.invitations (merchant_id, influencer_id, product_id, campaign_id, message, commission_rate, status, responded_at, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222222' LIMIT 1), (SELECT id FROM public.campaigns WHERE merchant_id = '22222222-2222-2222-2222-222222222222' AND status = 'active' LIMIT 1), 'Nous aimerions collaborer avec vous pour notre nouvelle collection', 15.00, 'accepted', NOW() - INTERVAL '13 days', NOW() - INTERVAL '15 days'),
    ('22222222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333334', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222223' LIMIT 1), (SELECT id FROM public.campaigns WHERE merchant_id = '22222222-2222-2222-2222-222222222223' AND status = 'active' LIMIT 1), 'Vos reviews tech sont excellentes, collaboration ?', 20.00, 'accepted', NOW() - INTERVAL '8 days', NOW() - INTERVAL '10 days'),
    ('22222222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333335', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222224' LIMIT 1), (SELECT id FROM public.campaigns WHERE merchant_id = '22222222-2222-2222-2222-222222222224' AND status = 'active' LIMIT 1), 'Promotion de nos produits beauté ensemble ?', 12.00, 'pending', NULL, NOW() - INTERVAL '3 days'),
    ('22222222-2222-2222-2222-222222222225', '33333333-3333-3333-3333-333333333336', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222225' LIMIT 1), (SELECT id FROM public.campaigns WHERE merchant_id = '22222222-2222-2222-2222-222222222225' AND status = 'active' LIMIT 1), 'Équipements sportifs pour votre communauté fitness', 18.00, 'accepted', NOW() - INTERVAL '5 days', NOW() - INTERVAL '7 days'),
    ('22222222-2222-2222-2222-222222222226', '33333333-3333-3333-3333-333333333337', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222226' LIMIT 1), (SELECT id FROM public.campaigns WHERE merchant_id = '22222222-2222-2222-2222-222222222226' AND status = 'active' LIMIT 1), 'Produits gourmets pour vos recettes ?', 25.00, 'accepted', NOW() - INTERVAL '4 days', NOW() - INTERVAL '6 days'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333334', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222222' LIMIT 1 OFFSET 1), NULL, 'Nouveau produit mode tech fusion', 15.00, 'pending', NULL, NOW() - INTERVAL '2 days'),
    ('22222222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333335', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222223' LIMIT 1 OFFSET 1), NULL, 'Gadgets tech pour lifestyle influencers', 18.00, 'pending', NULL, NOW() - INTERVAL '1 day'),
    ('22222222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333336', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222224' LIMIT 1 OFFSET 1), NULL, 'Cosmétiques sport & beauté', 14.00, 'rejected', NOW() - INTERVAL '4 days', NOW() - INTERVAL '5 days'),
    ('22222222-2222-2222-2222-222222222225', '33333333-3333-3333-3333-333333333337', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222225' LIMIT 1 OFFSET 1), NULL, 'Nutrition sportive pour cuisiniers', 16.00, 'pending', NULL, NOW() - INTERVAL '2 days'),
    ('22222222-2222-2222-2222-222222222226', '33333333-3333-3333-3333-333333333333', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222226' LIMIT 1 OFFSET 1), NULL, 'Accessoires cuisine mode', 22.00, 'cancelled', NOW() - INTERVAL '1 day', NOW() - INTERVAL '4 days');

-- ============================================
-- 4. COLLABORATION REQUESTS (15 demandes de collaboration)
-- ============================================
INSERT INTO public.collaboration_requests (influencer_id, merchant_id, campaign_id, message, status, created_at)
SELECT 
    i.id,
    m.id,
    c.id,
    'Je serais très intéressé(e) pour promouvoir vos produits. Mon audience correspond parfaitement à votre cible.',
    CASE (random() * 3)::integer
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'accepted'
        ELSE 'rejected'
    END,
    NOW() - (random() * INTERVAL '30 days')
FROM (SELECT id FROM public.users WHERE role = 'influencer' ORDER BY random() LIMIT 5) i
CROSS JOIN (SELECT id FROM public.users WHERE role = 'merchant' ORDER BY random() LIMIT 3) m
CROSS JOIN LATERAL (SELECT id FROM public.campaigns WHERE merchant_id = m.id AND status = 'active' LIMIT 1) c
LIMIT 15;

-- ============================================
-- 5. AFFILIATION REQUESTS (10 demandes d'affiliation)
-- ============================================
INSERT INTO public.affiliation_requests (influencer_id, merchant_id, product_id, service_id, message, status, requested_commission_rate, approved_commission_rate, responded_at, created_at, updated_at)
VALUES 
    ('33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222222' LIMIT 1), NULL, 'Je voudrais devenir affilié pour votre marque de mode', 'active', 15.00, 15.00, NOW() - INTERVAL '10 days', NOW() - INTERVAL '15 days', NOW() - INTERVAL '10 days'),
    ('33333333-3333-3333-3333-333333333334', '22222222-2222-2222-2222-222222222223', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222223' LIMIT 1), NULL, 'Passionné de tech, je voudrais promouvoir vos produits', 'active', 20.00, 18.00, NOW() - INTERVAL '8 days', NOW() - INTERVAL '12 days', NOW() - INTERVAL '8 days'),
    ('33333333-3333-3333-3333-333333333335', '22222222-2222-2222-2222-222222222224', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222224' LIMIT 1), NULL, 'Mon audience adore la beauté, collaboration idéale', 'pending_approval', 12.00, NULL, NULL, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    ('33333333-3333-3333-3333-333333333336', '22222222-2222-2222-2222-222222222225', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222225' LIMIT 1), NULL, 'Coach fitness, je veux promouvoir vos équipements', 'active', 18.00, 16.00, NOW() - INTERVAL '5 days', NOW() - INTERVAL '9 days', NOW() - INTERVAL '5 days'),
    ('33333333-3333-3333-3333-333333333337', '22222222-2222-2222-2222-222222222226', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222226' LIMIT 1), NULL, 'Chef cuisinier, parfait pour vos produits gourmets', 'active', 25.00, 25.00, NOW() - INTERVAL '6 days', NOW() - INTERVAL '11 days', NOW() - INTERVAL '6 days'),
    ('33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222223', NULL, (SELECT id FROM public.services WHERE merchant_id = '22222222-2222-2222-2222-222222222223' LIMIT 1), 'Intéressée par vos gadgets tech', 'rejected', 20.00, NULL, NOW() - INTERVAL '7 days', NOW() - INTERVAL '14 days', NOW() - INTERVAL '7 days'),
    ('33333333-3333-3333-3333-333333333334', '22222222-2222-2222-2222-222222222224', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222224' LIMIT 1 OFFSET 1), NULL, 'Demande de partenariat beauté tech', 'pending_approval', 14.00, NULL, NULL, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
    ('33333333-3333-3333-3333-333333333335', '22222222-2222-2222-2222-222222222225', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222225' LIMIT 1 OFFSET 1), NULL, 'Lifestyle & fitness, synergie parfaite', 'pending_approval', 15.00, NULL, NULL, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    ('33333333-3333-3333-3333-333333333336', '22222222-2222-2222-2222-222222222226', NULL, (SELECT id FROM public.services WHERE merchant_id = '22222222-2222-2222-2222-222222222226' LIMIT 1), 'Sport & nutrition, excellent match', 'active', 22.00, 20.00, NOW() - INTERVAL '4 days', NOW() - INTERVAL '8 days', NOW() - INTERVAL '4 days'),
    ('33333333-3333-3333-3333-333333333337', '22222222-2222-2222-2222-222222222222', (SELECT id FROM public.products WHERE merchant_id = '22222222-2222-2222-2222-222222222222' LIMIT 1 OFFSET 1), NULL, 'Cuisine & mode de vie, collaboration intéressante', 'pending_approval', 18.00, NULL, NULL, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days');

-- ============================================
-- 6. REVIEWS (20 avis sur les produits)
-- ============================================
-- Note: La table reviews est uniquement pour les avis produits, pas les avis utilisateurs
INSERT INTO public.reviews (product_id, user_id, rating, comment, is_verified_purchase, created_at)
SELECT 
    p.id,
    (CASE (random() * 9)::integer
        WHEN 0 THEN '33333333-3333-3333-3333-333333333333'
        WHEN 1 THEN '33333333-3333-3333-3333-333333333334'
        WHEN 2 THEN '33333333-3333-3333-3333-333333333335'
        WHEN 3 THEN '33333333-3333-3333-3333-333333333336'
        WHEN 4 THEN '33333333-3333-3333-3333-333333333337'
        WHEN 5 THEN '22222222-2222-2222-2222-222222222222'
        WHEN 6 THEN '22222222-2222-2222-2222-222222222223'
        WHEN 7 THEN '22222222-2222-2222-2222-222222222224'
        ELSE '22222222-2222-2222-2222-222222222225'
    END)::UUID,
    floor(random() * 2 + 4)::integer, -- 4 ou 5 étoiles
    CASE floor(random() * 5)::integer
        WHEN 0 THEN 'Produit excellent ! Je recommande vivement.'
        WHEN 1 THEN 'Très satisfait de mon achat. Qualité au top.'
        WHEN 2 THEN 'Super produit, conforme à la description.'
        WHEN 3 THEN 'Bon rapport qualité-prix. Content de mon achat.'
        ELSE 'Parfait ! Exactement ce que je cherchais.'
    END,
    random() > 0.3, -- 70% verified purchases
    NOW() - (random() * INTERVAL '40 days')
FROM public.products p
ORDER BY random()
LIMIT 20;

-- ============================================
-- 7. PRODUCT REVIEWS (15 avis supplémentaires avec review détaillé)
-- ============================================
INSERT INTO public.product_reviews (product_id, user_id, rating, review, created_at)
SELECT 
    p.id,
    (CASE (random() * 9)::integer
        WHEN 0 THEN '33333333-3333-3333-3333-333333333333'
        WHEN 1 THEN '33333333-3333-3333-3333-333333333334'
        WHEN 2 THEN '33333333-3333-3333-3333-333333333335'
        WHEN 3 THEN '33333333-3333-3333-3333-333333333336'
        WHEN 4 THEN '33333333-3333-3333-3333-333333333337'
        WHEN 5 THEN '22222222-2222-2222-2222-222222222222'
        WHEN 6 THEN '22222222-2222-2222-2222-222222222223'
        WHEN 7 THEN '22222222-2222-2222-2222-222222222224'
        ELSE '22222222-2222-2222-2222-222222222225'
    END)::UUID,
    floor(random() * 2 + 4)::integer, -- 4 ou 5 étoiles
    CASE floor(random() * 5)::integer
        WHEN 0 THEN 'Produit excellent ! Je recommande vivement à tous ceux qui cherchent qualité et performance.'
        WHEN 1 THEN 'Très satisfait de mon achat. Qualité au top, livraison rapide et emballage soigné.'
        WHEN 2 THEN 'Super produit, conforme à la description. Correspond parfaitement à mes attentes.'
        WHEN 3 THEN 'Bon rapport qualité-prix. Content de mon achat, je recommanderai sans hésiter.'
        ELSE 'Parfait ! Exactement ce que je cherchais. Dépassé mes espérances, vraiment satisfait.'
    END,
    NOW() - (random() * INTERVAL '40 days')
FROM public.products p
ORDER BY random()
LIMIT 15;

-- ============================================
-- 8. CONVERSATIONS (10 conversations)
-- ============================================
INSERT INTO public.conversations (participant_ids, last_message, last_message_at, created_at)
VALUES 
    (ARRAY['33333333-3333-3333-3333-333333333333'::UUID, '22222222-2222-2222-2222-222222222222'::UUID], 'Merci pour votre réponse rapide !', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '5 days'),
    (ARRAY['33333333-3333-3333-3333-333333333334'::UUID, '22222222-2222-2222-2222-222222222223'::UUID], 'Parfait, je commence la campagne demain', NOW() - INTERVAL '5 hours', NOW() - INTERVAL '3 days'),
    (ARRAY['33333333-3333-3333-3333-333333333335'::UUID, '22222222-2222-2222-2222-222222222224'::UUID], 'D''accord pour ces conditions', NOW() - INTERVAL '1 day', NOW() - INTERVAL '7 days'),
    (ARRAY['33333333-3333-3333-3333-333333333336'::UUID, '22222222-2222-2222-2222-222222222225'::UUID], 'Super, hâte de démarrer !', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 days'),
    (ARRAY['33333333-3333-3333-3333-333333333337'::UUID, '22222222-2222-2222-2222-222222222226'::UUID], 'Je vais créer le contenu ce week-end', NOW() - INTERVAL '8 hours', NOW() - INTERVAL '1 day'),
    (ARRAY['44444444-4444-4444-4444-444444444444'::UUID, '22222222-2222-2222-2222-222222222222'::UUID], 'Voici la proposition commerciale', NOW() - INTERVAL '1 day', NOW() - INTERVAL '10 days'),
    (ARRAY['44444444-4444-4444-4444-444444444445'::UUID, '22222222-2222-2222-2222-222222222223'::UUID], 'Quand pouvons-nous faire une démo ?', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '4 days'),
    (ARRAY['44444444-4444-4444-4444-444444444446'::UUID, '22222222-2222-2222-2222-222222222224'::UUID], 'Merci pour votre intérêt', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '6 days'),
    (ARRAY['33333333-3333-3333-3333-333333333333'::UUID, '33333333-3333-3333-3333-333333333334'::UUID], 'On collabore sur cette campagne ?', NOW() - INTERVAL '2 days', NOW() - INTERVAL '8 days'),
    (ARRAY['22222222-2222-2222-2222-222222222222'::UUID, '22222222-2222-2222-2222-222222222223'::UUID], 'Échange de bonnes pratiques', NOW() - INTERVAL '4 days', NOW() - INTERVAL '15 days');

-- ============================================
-- 9. MESSAGES (30 messages dans les conversations)
-- ============================================
INSERT INTO public.messages (conversation_id, sender_id, content, is_read, created_at)
SELECT 
    c.id,
    CASE (random())::integer WHEN 0 THEN c.participant_ids[1] ELSE c.participant_ids[2] END,
    CASE floor(random() * 8)::integer
        WHEN 0 THEN 'Bonjour, je suis intéressé par une collaboration'
        WHEN 1 THEN 'Quels sont les détails de votre offre ?'
        WHEN 2 THEN 'Parfait, je suis d''accord avec ces conditions'
        WHEN 3 THEN 'Pouvez-vous m''envoyer plus d''informations ?'
        WHEN 4 THEN 'Merci pour votre réponse rapide'
        WHEN 5 THEN 'Je vais commencer la campagne la semaine prochaine'
        WHEN 6 THEN 'Excellent ! Hâte de travailler ensemble'
        ELSE 'D''accord, je vous tiens au courant'
    END,
    random() > 0.3,
    NOW() - (random() * INTERVAL '10 days')
FROM public.conversations c
CROSS JOIN generate_series(1, 3) -- 3 messages par conversation
LIMIT 30;

-- ============================================
-- 10. NOTIFICATIONS (40 notifications variées)
-- ============================================
INSERT INTO public.notifications (user_id, type, title, message, is_read, created_at)
SELECT 
    u.id,
    CASE (random() * 7)::integer
        WHEN 0 THEN 'new_sale'
        WHEN 1 THEN 'new_commission'
        WHEN 2 THEN 'campaign_approved'
        WHEN 3 THEN 'payout_processed'
        WHEN 4 THEN 'new_message'
        WHEN 5 THEN 'new_review'
        WHEN 6 THEN 'milestone_reached'
        ELSE 'system_update'
    END,
    CASE (random() * 5)::integer
        WHEN 0 THEN 'Nouvelle vente !'
        WHEN 1 THEN 'Commission validée'
        WHEN 2 THEN 'Campagne approuvée'
        WHEN 3 THEN 'Paiement traité'
        ELSE 'Nouveau message'
    END,
    CASE (random() * 5)::integer
        WHEN 0 THEN 'Vous avez réalisé une nouvelle vente de 149.99€'
        WHEN 1 THEN 'Votre commission de 45.50€ a été validée'
        WHEN 2 THEN 'Votre campagne "Été 2024" a été approuvée'
        WHEN 3 THEN 'Votre paiement de 1250€ a été traité'
        ELSE 'Vous avez reçu un nouveau message'
    END,
    random() > 0.4,
    NOW() - (random() * INTERVAL '20 days')
FROM public.users u
CROSS JOIN generate_series(1, 4) -- 4 notifications par utilisateur
WHERE u.role IN ('merchant', 'influencer', 'commercial')
LIMIT 40;

-- ============================================
-- 11. USER GAMIFICATION (Gamification pour tous les utilisateurs)
-- ============================================
INSERT INTO public.user_gamification (user_id, points, level, streak_days, last_activity_date, achievements, created_at, updated_at)
SELECT 
    id,
    floor(random() * 5000 + 500)::integer,
    floor(random() * 10 + 1)::integer,
    floor(random() * 30)::integer,
    NOW()::date - floor(random() * 7)::integer,
    ARRAY['first_sale', 'early_adopter', 'top_performer']::text[],
    NOW() - INTERVAL '3 months',
    NOW() - INTERVAL '1 day'
FROM public.users
WHERE role IN ('merchant', 'influencer', 'commercial');

-- ============================================
-- 12. BADGES (10 badges disponibles)
-- ============================================
INSERT INTO public.badges (name, description, icon_url, criteria, points_reward, is_active, created_at)
VALUES 
    ('First Sale', 'Réalisez votre première vente', 'https://via.placeholder.com/100/4CAF50/FFFFFF?text=1st', '{"min_sales": 1}', 50, true, NOW() - INTERVAL '6 months'),
    ('Top Seller', 'Réalisez 100 ventes', 'https://via.placeholder.com/100/FF9800/FFFFFF?text=100', '{"min_sales": 100}', 500, true, NOW() - INTERVAL '6 months'),
    ('Influencer Pro', 'Atteignez 50k followers', 'https://via.placeholder.com/100/2196F3/FFFFFF?text=50K', '{"min_followers": 50000}', 300, true, NOW() - INTERVAL '6 months'),
    ('Early Adopter', 'Inscrit dans les 100 premiers', 'https://via.placeholder.com/100/9C27B0/FFFFFF?text=EA', '{"user_rank": 100}', 1000, true, NOW() - INTERVAL '6 months'),
    ('Campaign Master', 'Créez 10 campagnes réussies', 'https://via.placeholder.com/100/F44336/FFFFFF?text=10C', '{"min_campaigns": 10}', 400, true, NOW() - INTERVAL '5 months'),
    ('Social Star', 'Connectez 3 réseaux sociaux', 'https://via.placeholder.com/100/00BCD4/FFFFFF?text=3S', '{"min_socials": 3}', 200, true, NOW() - INTERVAL '5 months'),
    ('Payout King', 'Recevez 10 paiements', 'https://via.placeholder.com/100/FFEB3B/000000?text=$10', '{"min_payouts": 10}', 600, true, NOW() - INTERVAL '4 months'),
    ('Review Champion', 'Obtenez 50 avis 5 étoiles', 'https://via.placeholder.com/100/FF5722/FFFFFF?text=5★', '{"min_reviews": 50, "min_rating": 5}', 350, true, NOW() - INTERVAL '4 months'),
    ('Collaboration Hero', '20 collaborations réussies', 'https://via.placeholder.com/100/8BC34A/FFFFFF?text=20', '{"min_collabs": 20}', 450, true, NOW() - INTERVAL '3 months'),
    ('Referral Master', 'Parrainez 10 utilisateurs', 'https://via.placeholder.com/100/3F51B5/FFFFFF?text=10R', '{"min_referrals": 10}', 800, true, NOW() - INTERVAL '3 months');

-- ============================================
-- 13. MISSIONS (5 missions actives)
-- ============================================
INSERT INTO public.missions (title, description, type, criteria, rewards, start_date, end_date, is_active, created_at)
VALUES 
    ('Summer Sales Challenge', 'Réalisez 10 ventes en juillet', 'sales', '{"min_sales": 10, "period": "2024-07"}', '{"points": 500, "badge": "Summer Champion"}', NOW() - INTERVAL '1 month', NOW() + INTERVAL '1 month', true, NOW() - INTERVAL '1 month'),
    ('Social Growth Sprint', 'Gagnez 5000 followers ce mois', 'growth', '{"min_followers_gain": 5000, "period": "monthly"}', '{"points": 300, "badge": "Growth Master"}', NOW() - INTERVAL '15 days', NOW() + INTERVAL '15 days', true, NOW() - INTERVAL '15 days'),
    ('Collaboration Quest', 'Acceptez 3 nouvelles collaborations', 'collaboration', '{"min_collaborations": 3}', '{"points": 200, "discount": "20% off Elite"}', NOW() - INTERVAL '10 days', NOW() + INTERVAL '20 days', true, NOW() - INTERVAL '10 days'),
    ('Perfect Rating', 'Maintenez une note de 5/5 sur 20 avis', 'quality', '{"min_rating": 5, "min_reviews": 20}', '{"points": 600, "badge": "Quality Star"}', NOW() - INTERVAL '20 days', NOW() + INTERVAL '40 days', true, NOW() - INTERVAL '20 days'),
    ('Revenue Milestone', 'Générez 10000€ de CA ce trimestre', 'revenue', '{"min_revenue": 10000, "period": "quarter"}', '{"points": 1000, "cash_bonus": 100}', NOW() - INTERVAL '2 months', NOW() + INTERVAL '1 month', true, NOW() - INTERVAL '2 months');

-- ============================================
-- 14. USER MISSIONS (Attribution des missions aux utilisateurs)
-- ============================================
INSERT INTO public.user_missions (user_id, mission_id, progress, status, completed_at, created_at)
SELECT 
    u.id,
    m.id,
    floor(random() * 100)::integer,
    CASE (random() * 3)::integer
        WHEN 0 THEN 'in_progress'
        WHEN 1 THEN 'completed'
        ELSE 'pending'
    END,
    CASE 
        WHEN random() < 0.33 THEN NOW() - (random() * INTERVAL '10 days')
        ELSE NULL
    END,
    NOW() - (random() * INTERVAL '15 days')
FROM (SELECT id FROM public.users WHERE role IN ('merchant', 'influencer') ORDER BY random() LIMIT 8) u
CROSS JOIN (SELECT id FROM public.missions WHERE is_active = true ORDER BY random() LIMIT 2) m;

-- ============================================
-- 15. GATEWAY TRANSACTIONS (15 transactions de paiement)
-- ============================================
INSERT INTO public.gateway_transactions (user_id, gateway, transaction_id, amount, currency, status, metadata, created_at)
SELECT 
    u.id,
    CASE (random() * 2)::integer
        WHEN 0 THEN 'stripe'
        WHEN 1 THEN 'paypal'
        ELSE 'bank_transfer'
    END,
    'txn_' || substr(md5(random()::text), 1, 24),
    (random() * 500 + 50)::decimal(12,2),
    'EUR',
    CASE (random() * 3)::integer
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'completed'
        WHEN 2 THEN 'failed'
        ELSE 'refunded'
    END,
    jsonb_build_object(
        'customer_id', 'cus_' || substr(md5(random()::text), 1, 12),
        'invoice_id', 'inv_' || substr(md5(random()::text), 1, 12),
        'payment_method', CASE (random() * 3)::integer
            WHEN 0 THEN 'credit_card'
            WHEN 1 THEN 'paypal'
            ELSE 'bank_transfer'
        END
    ),
    NOW() - (random() * INTERVAL '30 days')
FROM public.users u
WHERE u.role IN ('merchant', 'influencer')
ORDER BY random()
LIMIT 15;

-- ============================================
-- 16. WEBHOOK LOGS (20 webhooks d'événements)
-- ============================================
INSERT INTO public.webhook_logs (event_type, payload, status, response, attempts, created_at)
SELECT 
    CASE (random() * 5)::integer
        WHEN 0 THEN 'sale.created'
        WHEN 1 THEN 'commission.approved'
        WHEN 2 THEN 'payout.processed'
        WHEN 3 THEN 'campaign.completed'
        WHEN 4 THEN 'user.registered'
        ELSE 'subscription.renewed'
    END,
    jsonb_build_object(
        'endpoint', 'https://api.example.com/webhooks/' || substr(md5(random()::text), 1, 8),
        'event', 'sale.created',
        'data', jsonb_build_object('amount', 149.99, 'product_id', 'prod_123')
    ),
    CASE (random() * 2)::integer
        WHEN 0 THEN 'success'
        ELSE 'failed'
    END,
    CASE (random() * 2)::integer
        WHEN 0 THEN '{"status": 200, "body": "OK"}'
        ELSE '{"status": 500, "error": "Internal server error"}'
    END,
    floor(random() * 3)::integer,
    NOW() - (random() * INTERVAL '10 days')
FROM generate_series(1, 20);

-- ============================================
-- FIN DU SCRIPT PARTIE 4
-- ============================================
-- Social Connections: 14 comptes sociaux
-- Social Media Stats: 50 statistiques
-- Invitations: 10 invitations
-- Collaboration Requests: 15 demandes
-- Affiliation Requests: 10 demandes
-- Reviews: 20 avis (marchands + influenceurs)
-- Product Reviews: 15 avis produits
-- Conversations: 10 conversations
-- Messages: 30 messages
-- Notifications: 40 notifications
-- User Gamification: tous les utilisateurs
-- Badges: 10 badges
-- Missions: 5 missions actives
-- User Missions: associations utilisateur-mission
-- Gateway Transactions: 15 transactions
-- Webhook Logs: 20 webhooks
-- ============================================
-- TABLES NON EXISTANTES (SUPPRIMÉES DU SCRIPT):
-- - activity_logs: table non créée dans le schéma
-- - admin_policies: table non créée dans le schéma
-- - dispute_resolutions: table non créée dans le schéma
-- - analytics_events: table non créée dans le schéma
-- ============================================
-- 🎉 BASE DE DONNÉES COMPLÈTEMENT REMPLIE ! 🎉
-- Toutes les tables EXISTANTES dans le schéma ont été remplies
-- ============================================
