-- ============================================
-- SCRIPT 2/4 : INSERTION DES DONNÉES DE TEST - PRODUITS & CAMPAGNES
-- PARTIE 2 : Products, Services, Campaigns, Tracking Links
-- ============================================

-- ============================================
-- 1. INSERTION DES PRODUITS (25 produits répartis sur 5 marchands)
-- ============================================

-- Produits Fashion Store Paris (Merchant 1)
INSERT INTO public.products (merchant_id, name, description, category, price, commission_rate, image_url, product_url, sku, stock, is_active, type, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222222', 'Robe d''été élégante', 'Robe légère parfaite pour l''été', 'Fashion', 79.99, 12.00, 'https://via.placeholder.com/300/FF6B9D/FFFFFF?text=Robe', 'https://fashionstore.com/robe-ete', 'FS-ROBE-001', 45, true, 'product', NOW() - INTERVAL '4 months'),
    ('22222222-2222-2222-2222-222222222222', 'Sac à main luxe', 'Sac à main en cuir véritable', 'Fashion', 149.99, 12.00, 'https://via.placeholder.com/300/FF6B9D/FFFFFF?text=Sac', 'https://fashionstore.com/sac-luxe', 'FS-SAC-001', 30, true, 'product', NOW() - INTERVAL '3 months'),
    ('22222222-2222-2222-2222-222222222222', 'Chaussures tendance', 'Sneakers design moderne', 'Fashion', 89.99, 12.00, 'https://via.placeholder.com/300/FF6B9D/FFFFFF?text=Chaussures', 'https://fashionstore.com/sneakers', 'FS-SHOE-001', 60, true, 'product', NOW() - INTERVAL '2 months'),
    ('22222222-2222-2222-2222-222222222222', 'Veste en jean', 'Veste denim classique', 'Fashion', 69.99, 12.00, 'https://via.placeholder.com/300/FF6B9D/FFFFFF?text=Veste', 'https://fashionstore.com/veste-jean', 'FS-VEST-001', 50, true, 'product', NOW() - INTERVAL '1 month'),
    ('22222222-2222-2222-2222-222222222222', 'Accessoires mode', 'Set d''accessoires fashion', 'Fashion', 39.99, 12.00, 'https://via.placeholder.com/300/FF6B9D/FFFFFF?text=Accessoires', 'https://fashionstore.com/accessoires', 'FS-ACC-001', 100, true, 'product', NOW() - INTERVAL '15 days');

-- Produits Tech Gadgets Pro (Merchant 2)
INSERT INTO public.products (merchant_id, name, description, category, price, commission_rate, image_url, product_url, sku, stock, is_active, type, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222223', 'Smartphone Pro Max', 'Dernier smartphone haute performance', 'Tech', 999.99, 15.00, 'https://via.placeholder.com/300/4A90E2/FFFFFF?text=Phone', 'https://techgadgets.com/smartphone-pro', 'TG-PHONE-001', 25, true, 'product', NOW() - INTERVAL '4 months'),
    ('22222222-2222-2222-2222-222222222223', 'Casque audio sans fil', 'Casque Bluetooth avec réduction de bruit', 'Tech', 199.99, 15.00, 'https://via.placeholder.com/300/4A90E2/FFFFFF?text=Headphone', 'https://techgadgets.com/casque-audio', 'TG-AUDIO-001', 50, true, 'product', NOW() - INTERVAL '3 months'),
    ('22222222-2222-2222-2222-222222222223', 'Montre connectée', 'Smartwatch avec suivi fitness', 'Tech', 299.99, 15.00, 'https://via.placeholder.com/300/4A90E2/FFFFFF?text=Watch', 'https://techgadgets.com/smartwatch', 'TG-WATCH-001', 40, true, 'product', NOW() - INTERVAL '2 months'),
    ('22222222-2222-2222-2222-222222222223', 'Tablette graphique', 'Tablette pour créatifs et designers', 'Tech', 449.99, 15.00, 'https://via.placeholder.com/300/4A90E2/FFFFFF?text=Tablet', 'https://techgadgets.com/tablette', 'TG-TAB-001', 20, true, 'product', NOW() - INTERVAL '1 month'),
    ('22222222-2222-2222-2222-222222222223', 'Drone caméra 4K', 'Drone avec caméra haute résolution', 'Tech', 599.99, 15.00, 'https://via.placeholder.com/300/4A90E2/FFFFFF?text=Drone', 'https://techgadgets.com/drone-4k', 'TG-DRONE-001', 15, true, 'product', NOW() - INTERVAL '20 days');

-- Produits Beauty Paris (Merchant 3)
INSERT INTO public.products (merchant_id, name, description, category, price, commission_rate, image_url, product_url, sku, stock, is_active, type, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222224', 'Sérum anti-âge premium', 'Sérum visage aux actifs naturels', 'Beauty', 89.99, 10.00, 'https://via.placeholder.com/300/F5A623/FFFFFF?text=Serum', 'https://beautyparis.com/serum-antiage', 'BP-SER-001', 80, true, 'product', NOW() - INTERVAL '3 months'),
    ('22222222-2222-2222-2222-222222222224', 'Coffret maquillage', 'Set complet de maquillage professionnel', 'Beauty', 129.99, 10.00, 'https://via.placeholder.com/300/F5A623/FFFFFF?text=Makeup', 'https://beautyparis.com/coffret-makeup', 'BP-MAK-001', 60, true, 'product', NOW() - INTERVAL '2 months'),
    ('22222222-2222-2222-2222-222222222224', 'Parfum luxe femme', 'Eau de parfum signature', 'Beauty', 119.99, 10.00, 'https://via.placeholder.com/300/F5A623/FFFFFF?text=Perfume', 'https://beautyparis.com/parfum-luxe', 'BP-PARF-001', 50, true, 'product', NOW() - INTERVAL '1 month'),
    ('22222222-2222-2222-2222-222222222224', 'Crème hydratante bio', 'Crème visage certifiée bio', 'Beauty', 49.99, 10.00, 'https://via.placeholder.com/300/F5A623/FFFFFF?text=Cream', 'https://beautyparis.com/creme-bio', 'BP-CRE-001', 100, true, 'product', NOW() - INTERVAL '25 days'),
    ('22222222-2222-2222-2222-222222222224', 'Kit soins cheveux', 'Routine capillaire complète', 'Beauty', 79.99, 10.00, 'https://via.placeholder.com/300/F5A623/FFFFFF?text=Hair', 'https://beautyparis.com/kit-cheveux', 'BP-HAIR-001', 70, true, 'product', NOW() - INTERVAL '10 days');

-- Produits Sport Shop Elite (Merchant 4)
INSERT INTO public.products (merchant_id, name, description, category, price, commission_rate, image_url, product_url, sku, stock, is_active, type, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222225', 'Tapis de yoga premium', 'Tapis antidérapant écologique', 'Sports', 59.99, 8.00, 'https://via.placeholder.com/300/7ED321/FFFFFF?text=Yoga', 'https://sportshop.com/tapis-yoga', 'SS-YOGA-001', 90, true, 'product', NOW() - INTERVAL '2 months'),
    ('22222222-2222-2222-2222-222222222225', 'Set d''haltères ajustables', 'Haltères 2-20kg réglables', 'Sports', 149.99, 8.00, 'https://via.placeholder.com/300/7ED321/FFFFFF?text=Weights', 'https://sportshop.com/halteres', 'SS-HALT-001', 40, true, 'product', NOW() - INTERVAL '1 month'),
    ('22222222-2222-2222-2222-222222222225', 'Vélo d''appartement', 'Vélo spinning connecté', 'Sports', 399.99, 8.00, 'https://via.placeholder.com/300/7ED321/FFFFFF?text=Bike', 'https://sportshop.com/velo-appart', 'SS-BIKE-001', 15, true, 'product', NOW() - INTERVAL '15 days'),
    ('22222222-2222-2222-2222-222222222225', 'Tenue sport complète', 'Ensemble legging + brassière', 'Sports', 79.99, 8.00, 'https://via.placeholder.com/300/7ED321/FFFFFF?text=Outfit', 'https://sportshop.com/tenue-sport', 'SS-OUT-001', 80, true, 'product', NOW() - INTERVAL '20 days'),
    ('22222222-2222-2222-2222-222222222225', 'Montre GPS running', 'Montre sport avec GPS intégré', 'Sports', 249.99, 8.00, 'https://via.placeholder.com/300/7ED321/FFFFFF?text=GPS', 'https://sportshop.com/montre-gps', 'SS-GPS-001', 30, true, 'product', NOW() - INTERVAL '10 days');

-- Produits Food Delights (Merchant 5)
INSERT INTO public.products (merchant_id, name, description, category, price, commission_rate, image_url, product_url, sku, stock, is_active, type, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222226', 'Coffret chocolats artisanaux', 'Sélection de chocolats fins', 'Food', 49.99, 11.00, 'https://via.placeholder.com/300/D0021B/FFFFFF?text=Chocolat', 'https://fooddelights.com/chocolats', 'FD-CHOC-001', 120, true, 'product', NOW() - INTERVAL '1 month'),
    ('22222222-2222-2222-2222-222222222226', 'Panier découverte terroir', 'Produits du terroir français', 'Food', 89.99, 11.00, 'https://via.placeholder.com/300/D0021B/FFFFFF?text=Panier', 'https://fooddelights.com/panier-terroir', 'FD-PAN-001', 60, true, 'product', NOW() - INTERVAL '20 days'),
    ('22222222-2222-2222-2222-222222222226', 'Vins grands crus', 'Sélection de vins premium', 'Food', 149.99, 11.00, 'https://via.placeholder.com/300/D0021B/FFFFFF?text=Wine', 'https://fooddelights.com/vins-crus', 'FD-VIN-001', 40, true, 'product', NOW() - INTERVAL '15 days'),
    ('22222222-2222-2222-2222-222222222226', 'Huile d''olive bio', 'Huile d''olive extra vierge', 'Food', 29.99, 11.00, 'https://via.placeholder.com/300/D0021B/FFFFFF?text=Oil', 'https://fooddelights.com/huile-olive', 'FD-OIL-001', 100, true, 'product', NOW() - INTERVAL '10 days'),
    ('22222222-2222-2222-2222-222222222226', 'Coffret thés premium', 'Collection de thés rares', 'Food', 39.99, 11.00, 'https://via.placeholder.com/300/D0021B/FFFFFF?text=Tea', 'https://fooddelights.com/thes-premium', 'FD-TEA-001', 90, true, 'product', NOW() - INTERVAL '5 days');

-- ============================================
-- 2. INSERTION DES SERVICES (5 services)
-- ============================================
INSERT INTO public.services (merchant_id, name, description, category, price, commission_rate, pricing_model, image_url, duration, is_active, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222222', 'Consultation stylist personnel', 'Séance de conseil en mode', 'Fashion', 0.00, 12.00, 'per_lead', 'https://via.placeholder.com/300/FF6B9D/FFFFFF?text=Stylist', 60, true, NOW() - INTERVAL '2 months'),
    ('22222222-2222-2222-2222-222222222223', 'Installation tech à domicile', 'Configuration de vos appareils', 'Tech', 80.00, 15.00, 'fixed_price', 'https://via.placeholder.com/300/4A90E2/FFFFFF?text=Install', 90, true, NOW() - INTERVAL '1 month'),
    ('22222222-2222-2222-2222-222222222224', 'Soin visage personnalisé', 'Traitement beauté sur mesure', 'Beauty', 120.00, 10.00, 'fixed_price', 'https://via.placeholder.com/300/F5A623/FFFFFF?text=Facial', 75, true, NOW() - INTERVAL '3 weeks'),
    ('22222222-2222-2222-2222-222222222225', 'Coaching sportif privé', 'Séance de sport personnalisée', 'Sports', 60.00, 8.00, 'fixed_price', 'https://via.placeholder.com/300/7ED321/FFFFFF?text=Coaching', 45, true, NOW() - INTERVAL '2 weeks'),
    ('22222222-2222-2222-2222-222222222226', 'Cours de cuisine gastronomique', 'Atelier culinaire avec chef', 'Food', 180.00, 11.00, 'fixed_price', 'https://via.placeholder.com/300/D0021B/FFFFFF?text=Cooking', 120, true, NOW() - INTERVAL '1 week');

-- ============================================
-- 3. INSERTION DES CAMPAGNES (10 campagnes)
-- ============================================
INSERT INTO public.campaigns (id, merchant_id, influencer_id, name, description, budget, commission_rate, start_date, end_date, status, type, target_audience, performance_metrics, created_at)
VALUES 
    ('c1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', 'Campagne Été Fashion', 'Promotion collection été 2024', 5000.00, 12.00, NOW() - INTERVAL '2 months', NOW() + INTERVAL '1 month', 'active', 'seasonal', 'Femmes 18-35 ans', '{"impressions": 125000, "clicks": 8500, "conversions": 234}', NOW() - INTERVAL '2 months'),
    ('c2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333334', 'Tech Innovation 2024', 'Lancement nouveaux gadgets', 10000.00, 15.00, NOW() - INTERVAL '1 month', NOW() + INTERVAL '2 months', 'active', 'product_launch', 'Tech enthusiasts 20-45 ans', '{"impressions": 450000, "clicks": 32000, "conversions": 678}', NOW() - INTERVAL '1 month'),
    ('c3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333333', 'Beauty Essentials', 'Must-have produits beauté', 3000.00, 10.00, NOW() - INTERVAL '3 weeks', NOW() + INTERVAL '5 weeks', 'active', 'awareness', 'Femmes 25-40 ans', '{"impressions": 89000, "clicks": 5600, "conversions": 145}', NOW() - INTERVAL '3 weeks'),
    ('c4444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222225', '33333333-3333-3333-3333-333333333336', 'Défi Fitness 30 jours', 'Programme remise en forme', 2000.00, 8.00, NOW() - INTERVAL '2 weeks', NOW() + INTERVAL '6 weeks', 'active', 'challenge', 'Sportifs débutants 18-50 ans', '{"impressions": 67000, "clicks": 4200, "conversions": 98}', NOW() - INTERVAL '2 weeks'),
    ('c5555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222226', '33333333-3333-3333-3333-333333333337', 'Gastronomie Française', 'Découverte produits terroir', 4000.00, 11.00, NOW() - INTERVAL '10 days', NOW() + INTERVAL '50 days', 'active', 'discovery', 'Food lovers 30-60 ans', '{"impressions": 156000, "clicks": 9800, "conversions": 267}', NOW() - INTERVAL '10 days'),
    ('c6666666-6666-6666-6666-666666666666', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333335', 'Rentrée Mode', 'Collection automne-hiver', 6000.00, 12.00, NOW() + INTERVAL '1 week', NOW() + INTERVAL '3 months', 'draft', 'seasonal', 'Hommes et Femmes 18-40 ans', '{}', NOW() - INTERVAL '5 days'),
    ('c7777777-7777-7777-7777-777777777777', '22222222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333334', 'Black Friday Tech', 'Méga promos tech', 15000.00, 15.00, NOW() + INTERVAL '2 months', NOW() + INTERVAL '2 months 3 days', 'draft', 'sales_event', 'Tous publics tech', '{}', NOW() - INTERVAL '1 week'),
    ('c8888888-8888-8888-8888-888888888888', '22222222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333333', 'Routine beauté matinale', 'Soins du matin essentiels', 2500.00, 10.00, NOW() - INTERVAL '1 month', NOW() - INTERVAL '1 day', 'completed', 'tutorial', 'Femmes 20-35 ans', '{"impressions": 78000, "clicks": 4900, "conversions": 123}', NOW() - INTERVAL '2 months'),
    ('c9999999-9999-9999-9999-999999999999', '22222222-2222-2222-2222-222222222225', '33333333-3333-3333-3333-333333333336', 'Marathon Training', 'Préparation marathon 2024', 3500.00, 8.00, NOW() - INTERVAL '3 months', NOW() - INTERVAL '1 week', 'completed', 'training', 'Coureurs confirmés', '{"impressions": 45000, "clicks": 3100, "conversions": 67}', NOW() - INTERVAL '4 months'),
    ('ca111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222226', '33333333-3333-3333-3333-333333333337', 'Fêtes gourmandes', 'Sélection fêtes de fin d''année', 5000.00, 11.00, NOW() + INTERVAL '1 month', NOW() + INTERVAL '3 months', 'draft', 'seasonal', 'Familles et gourmets', '{}', NOW() - INTERVAL '3 days');

-- ============================================
-- 4. ASSOCIATION PRODUITS AUX CAMPAGNES
-- ============================================
INSERT INTO public.campaign_products (campaign_id, product_id, created_at)
SELECT 
    'c1111111-1111-1111-1111-111111111111',
    id,
    NOW()
FROM public.products
WHERE merchant_id = '22222222-2222-2222-2222-222222222222'
LIMIT 3;

INSERT INTO public.campaign_products (campaign_id, product_id, created_at)
SELECT 
    'c2222222-2222-2222-2222-222222222222',
    id,
    NOW()
FROM public.products
WHERE merchant_id = '22222222-2222-2222-2222-222222222223'
LIMIT 4;

INSERT INTO public.campaign_products (campaign_id, product_id, created_at)
SELECT 
    'c3333333-3333-3333-3333-333333333333',
    id,
    NOW()
FROM public.products
WHERE merchant_id = '22222222-2222-2222-2222-222222222224'
LIMIT 3;

-- ============================================
-- 5. INSERTION DES TRACKING LINKS (15 liens)
-- ============================================
INSERT INTO public.tracking_links (influencer_id, merchant_id, product_id, campaign_id, unique_code, full_url, short_url, clicks, conversions, revenue, commission_earned, is_active, created_at)
SELECT 
    c.influencer_id,
    c.merchant_id,
    p.id,
    c.id,
    'TRK-' || substr(md5(random()::text), 1, 8),
    'https://getyourshare.com/track/' || substr(md5(random()::text), 1, 8),
    'https://gys.io/' || substr(md5(random()::text), 1, 6),
    floor(random() * 500 + 100)::integer,
    floor(random() * 50 + 5)::integer,
    (random() * 5000 + 1000)::decimal(12,2),
    (random() * 500 + 50)::decimal(12,2),
    true,
    NOW() - (random() * INTERVAL '60 days')
FROM public.campaigns c
JOIN public.products p ON p.merchant_id = c.merchant_id
WHERE c.status = 'active'
LIMIT 15;

-- ============================================
-- FIN DU SCRIPT PARTIE 2
-- ============================================
-- Produits créés: 25 produits + 5 services
-- Campagnes créées: 10 campagnes
-- Tracking links: 15 liens actifs
-- Prêt pour la PARTIE 3: Sales, Commissions, Leads
-- ============================================
