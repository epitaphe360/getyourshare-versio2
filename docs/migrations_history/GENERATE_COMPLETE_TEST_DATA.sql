-- ============================================
-- GÉNÉRATION COMPLÈTE DES DONNÉES DE TEST
-- ============================================
-- Ce script peuple TOUTES les tables avec des données cohérentes
-- pour tester tous les dashboards (Admin, Merchant, Influencer, Commercial)

-- ============================================
-- 1. UTILISATEURS (20 users de test)
-- ============================================

-- 1 Admin
INSERT INTO users (id, email, password_hash, role, full_name, company_name, subscription_plan, avatar_url, created_at)
VALUES 
('11111111-1111-1111-1111-111111111111', 'admin@shareyoursales.ma', '$2b$10$dummyhash', 'admin', 'Admin SYS', 'ShareYourSales Admin', 'Enterprise', 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin', NOW());

-- 5 Merchants (différents tiers d'abonnement)
INSERT INTO users (id, email, password_hash, role, full_name, company_name, subscription_plan, avatar_url, created_at)
VALUES
-- FREE tier
('22222222-2222-2222-2222-222222222222', 'merchant1@example.com', '$2b$10$dummyhash', 'merchant', 'Tech Manager', 'TechStyle Morocco', 'Free', 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant1', NOW() - INTERVAL '30 days'),
('22222222-2222-2222-2222-222222222223', 'merchant2@example.com', '$2b$10$dummyhash', 'merchant', 'Beauty Owner', 'BeautyBox Casablanca', 'Free', 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant2', NOW() - INTERVAL '25 days'),

-- PRO tier  
('22222222-2222-2222-2222-222222222224', 'merchant3@example.com', '$2b$10$dummyhash', 'merchant', 'Fashion Director', 'FashionHub Marrakech', 'Pro', 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant3', NOW() - INTERVAL '20 days'),
('22222222-2222-2222-2222-222222222225', 'merchant4@example.com', '$2b$10$dummyhash', 'merchant', 'Electro CEO', 'ElectroShop Rabat', 'Pro', 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant4', NOW() - INTERVAL '15 days'),

-- ENTERPRISE tier
('22222222-2222-2222-2222-222222222226', 'merchant5@example.com', '$2b$10$dummyhash', 'merchant', 'Mega Manager', 'MegaStore Tanger', 'Enterprise', 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant5', NOW() - INTERVAL '10 days');

-- 5 Influencers
INSERT INTO users (id, email, password_hash, role, full_name, instagram_handle, followers_count, engagement_rate, avatar_url, created_at)
VALUES
('33333333-3333-3333-3333-333333333333', 'influencer1@example.com', '$2b$10$dummyhash', 'influencer', 'Sarah Lifestyle', '@sarah_lifestyle', 45000, 8.5, 'https://api.dicebear.com/7.x/avataaars/svg?seed=sarah', NOW() - INTERVAL '28 days'),
('33333333-3333-3333-3333-333333333334', 'influencer2@example.com', '$2b$10$dummyhash', 'influencer', 'Ahmed Tech Reviews', '@ahmed_tech', 78000, 6.2, 'https://api.dicebear.com/7.x/avataaars/svg?seed=ahmed', NOW() - INTERVAL '22 days'),
('33333333-3333-3333-3333-333333333335', 'influencer3@example.com', '$2b$10$dummyhash', 'influencer', 'Fatima Beauty', '@fatima_beauty', 62000, 9.1, 'https://api.dicebear.com/7.x/avataaars/svg?seed=fatima', NOW() - INTERVAL '18 days'),
('33333333-3333-3333-3333-333333333336', 'influencer4@example.com', '$2b$10$dummyhash', 'influencer', 'Youssef Fashion', '@youssef_fashion', 95000, 7.8, 'https://api.dicebear.com/7.x/avataaars/svg?seed=youssef', NOW() - INTERVAL '14 days'),
('33333333-3333-3333-3333-333333333337', 'influencer5@example.com', '$2b$10$dummyhash', 'influencer', 'Nadia Travel', '@nadia_travel', 120000, 10.2, 'https://api.dicebear.com/7.x/avataaars/svg?seed=nadia', NOW() - INTERVAL '10 days');

-- 6 Commerciaux
INSERT INTO users (id, email, password_hash, role, full_name, company_name, avatar_url, created_at)
VALUES
('44444444-4444-4444-4444-444444444441', 'commercial1@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Karim Sales', 'ShareYourSales', 'https://api.dicebear.com/7.x/avataaars/svg?seed=com1', NOW() - INTERVAL '60 days'),
('44444444-4444-4444-4444-444444444442', 'commercial2@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Laila Growth', 'ShareYourSales', 'https://api.dicebear.com/7.x/avataaars/svg?seed=com2', NOW() - INTERVAL '55 days'),
('44444444-4444-4444-4444-444444444443', 'commercial3@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Omar Business', 'ShareYourSales', 'https://api.dicebear.com/7.x/avataaars/svg?seed=com3', NOW() - INTERVAL '50 days'),
('44444444-4444-4444-4444-444444444444', 'commercial4@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Amina Dev', 'ShareYourSales', 'https://api.dicebear.com/7.x/avataaars/svg?seed=com4', NOW() - INTERVAL '45 days'),
('44444444-4444-4444-4444-444444444445', 'commercial5@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Rachid Pro', 'ShareYourSales', 'https://api.dicebear.com/7.x/avataaars/svg?seed=com5', NOW() - INTERVAL '40 days'),
('44444444-4444-4444-4444-444444444446', 'commercial6@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Sophia Elite', 'ShareYourSales', 'https://api.dicebear.com/7.x/avataaars/svg?seed=com6', NOW() - INTERVAL '35 days');

-- 3 Utilisateurs supplémentaires
INSERT INTO users (id, email, password_hash, role, full_name, company_name, subscription_plan, instagram_handle, followers_count, engagement_rate, avatar_url, created_at)
VALUES
('55555555-5555-5555-5555-555555555551', 'merchant6@example.com', '$2b$10$dummyhash', 'merchant', 'Sport Manager', 'SportGear Fes', 'Pro', NULL, NULL, NULL, 'https://api.dicebear.com/7.x/avataaars/svg?seed=sport', NOW() - INTERVAL '12 days'),
('66666666-6666-6666-6666-666666666661', 'influencer6@example.com', '$2b$10$dummyhash', 'influencer', 'Karim Fitness', NULL, NULL, '@karim_fit', 88000, 7.5, 'https://api.dicebear.com/7.x/avataaars/svg?seed=karim', NOW() - INTERVAL '9 days'),
('77777777-7777-7777-7777-777777777771', 'influencer7@example.com', '$2b$10$dummyhash', 'influencer', 'Leila Food', NULL, NULL, '@leila_food', 105000, 8.9, 'https://api.dicebear.com/7.x/avataaars/svg?seed=leila', NOW() - INTERVAL '7 days');

-- ============================================
-- 2. CAMPAIGNS (15 campaigns variées)
-- ============================================

INSERT INTO campaigns (id, merchant_id, name, description, budget, commission_rate, start_date, end_date, status, created_at)
VALUES
-- Merchant 1 (FREE) - Limité à 2 campaigns
('c1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Campagne Été 2024', 'Promotion vêtements d''été', 5000.00, 10.0, NOW() - INTERVAL '20 days', NOW() + INTERVAL '10 days', 'active', NOW() - INTERVAL '20 days'),
('c1111111-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222222', 'Black Friday Tech', 'Soldes accessoires tech', 3000.00, 12.0, NOW() - INTERVAL '5 days', NOW() + INTERVAL '25 days', 'active', NOW() - INTERVAL '5 days'),

-- Merchant 2 (FREE)
('c2222222-2222-2222-2222-222222222221', '22222222-2222-2222-2222-222222222223', 'Beauté Printemps', 'Nouveaux produits cosmétiques', 4000.00, 15.0, NOW() - INTERVAL '15 days', NOW() + INTERVAL '15 days', 'active', NOW() - INTERVAL '15 days'),

-- Merchant 3 (PRO) - Plus de campaigns
('c3333333-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222224', 'Fashion Week', 'Collection automne-hiver', 10000.00, 18.0, NOW() - INTERVAL '25 days', NOW() + INTERVAL '5 days', 'active', NOW() - INTERVAL '25 days'),
('c3333333-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222224', 'Promo Accessoires', 'Sacs et chaussures', 6000.00, 14.0, NOW() - INTERVAL '10 days', NOW() + INTERVAL '20 days', 'active', NOW() - INTERVAL '10 days'),
('c3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222224', 'Soldes Fin Saison', 'Déstockage -50%', 8000.00, 20.0, NOW() + INTERVAL '5 days', NOW() + INTERVAL '35 days', 'pending', NOW() - INTERVAL '2 days'),

-- Merchant 4 (PRO)
('c4444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222225', 'Électro Deals', 'High-tech à prix cassés', 12000.00, 16.0, NOW() - INTERVAL '18 days', NOW() + INTERVAL '12 days', 'active', NOW() - INTERVAL '18 days'),
('c4444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222225', 'Gaming Week', 'Consoles et jeux', 9000.00, 13.0, NOW() - INTERVAL '8 days', NOW() + INTERVAL '22 days', 'active', NOW() - INTERVAL '8 days'),

-- Merchant 5 (ENTERPRISE) - Nombreuses campaigns
('c5555555-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226', 'Mega Promo Hiver', 'Toutes catégories -30%', 25000.00, 22.0, NOW() - INTERVAL '30 days', NOW() + INTERVAL '30 days', 'active', NOW() - INTERVAL '30 days'),
('c5555555-5555-5555-5555-555555555552', '22222222-2222-2222-2222-222222222226', 'Électroménager Premium', 'Grandes marques', 18000.00, 17.0, NOW() - INTERVAL '12 days', NOW() + INTERVAL '18 days', 'active', NOW() - INTERVAL '12 days'),
('c5555555-5555-5555-5555-555555555553', '22222222-2222-2222-2222-222222222226', 'Mode Luxe', 'Vêtements haut de gamme', 15000.00, 25.0, NOW() - INTERVAL '6 days', NOW() + INTERVAL '24 days', 'active', NOW() - INTERVAL '6 days'),
('c5555555-5555-5555-5555-555555555554', '22222222-2222-2222-2222-222222222226', 'Sport & Fitness', 'Équipement sportif', 10000.00, 19.0, NOW() + INTERVAL '10 days', NOW() + INTERVAL '40 days', 'pending', NOW() - INTERVAL '1 day'),

-- Merchant 6 (PRO)
('c6666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555551', 'Running Essentials', 'Chaussures et vêtements course', 7000.00, 15.0, NOW() - INTERVAL '14 days', NOW() + INTERVAL '16 days', 'active', NOW() - INTERVAL '14 days'),
('c6666666-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551', 'Yoga & Pilates', 'Équipement wellness', 5500.00, 18.0, NOW() - INTERVAL '7 days', NOW() + INTERVAL '23 days', 'active', NOW() - INTERVAL '7 days'),

-- Campaign terminée (pour historique)
('c7777777-7777-7777-7777-777777777771', '22222222-2222-2222-2222-222222222224', 'Promo Rentrée 2024', 'Back to school', 5000.00, 12.0, NOW() - INTERVAL '60 days', NOW() - INTERVAL '30 days', 'completed', NOW() - INTERVAL '60 days');

-- ============================================
-- 3. PRODUCTS (30 produits variés)
-- ============================================

INSERT INTO products (id, merchant_id, name, description, price, commission_rate, image_url, category, created_at)
VALUES
-- Merchant 1 products
('p1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'T-Shirt Premium Cotton', 'T-shirt 100% coton biologique', 250.00, 10.0, 'https://picsum.photos/seed/tshirt1/400/400', 'Fashion', NOW() - INTERVAL '20 days'),
('p1111111-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222222', 'Jean Slim Fit', 'Jean denim stretch confortable', 450.00, 10.0, 'https://picsum.photos/seed/jean1/400/400', 'Fashion', NOW() - INTERVAL '18 days'),
('p1111111-1111-1111-1111-111111111113', '22222222-2222-2222-2222-222222222222', 'Casque Bluetooth', 'Audio sans fil haute qualité', 850.00, 12.0, 'https://picsum.photos/seed/headphone1/400/400', 'Electronics', NOW() - INTERVAL '5 days'),

-- Merchant 2 products
('p2222222-2222-2222-2222-222222222221', '22222222-2222-2222-2222-222222222223', 'Sérum Visage Anti-âge', 'Formule enrichie vitamine C', 380.00, 15.0, 'https://picsum.photos/seed/serum1/400/400', 'Beauty', NOW() - INTERVAL '15 days'),
('p2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222223', 'Palette Maquillage', '12 couleurs nude', 320.00, 15.0, 'https://picsum.photos/seed/palette1/400/400', 'Beauty', NOW() - INTERVAL '14 days'),
('p2222222-2222-2222-2222-222222222223', '22222222-2222-2222-2222-222222222223', 'Crème Hydratante Bio', 'Peaux sensibles certifiée bio', 280.00, 15.0, 'https://picsum.photos/seed/cream1/400/400', 'Beauty', NOW() - INTERVAL '12 days'),

-- Merchant 3 products  
('p3333333-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222224', 'Robe Cocktail Élégante', 'Parfaite pour soirées', 1200.00, 18.0, 'https://picsum.photos/seed/dress1/400/400', 'Fashion', NOW() - INTERVAL '25 days'),
('p3333333-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222224', 'Sac à Main Cuir', 'Cuir véritable italien', 1500.00, 18.0, 'https://picsum.photos/seed/bag1/400/400', 'Fashion', NOW() - INTERVAL '23 days'),
('p3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222224', 'Escarpins Talons Hauts', 'Confort et élégance', 950.00, 18.0, 'https://picsum.photos/seed/shoes1/400/400', 'Fashion', NOW() - INTERVAL '20 days'),
('p3333333-3333-3333-3333-333333333334', '22222222-2222-2222-2222-222222222224', 'Veste Blazer Femme', 'Coupe moderne professionnelle', 1800.00, 14.0, 'https://picsum.photos/seed/blazer1/400/400', 'Fashion', NOW() - INTERVAL '10 days'),

-- Merchant 4 products
('p4444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222225', 'Smartphone 5G Pro', 'Dernière génération', 5500.00, 16.0, 'https://picsum.photos/seed/phone1/400/400', 'Electronics', NOW() - INTERVAL '18 days'),
('p4444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222225', 'Laptop Gaming RGB', '16GB RAM, RTX Graphics', 12000.00, 16.0, 'https://picsum.photos/seed/laptop1/400/400', 'Electronics', NOW() - INTERVAL '17 days'),
('p4444444-4444-4444-4444-444444444443', '22222222-2222-2222-2222-222222222225', 'Tablette 10 pouces', 'Écran AMOLED', 3200.00, 16.0, 'https://picsum.photos/seed/tablet1/400/400', 'Electronics', NOW() - INTERVAL '15 days'),
('p4444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222225', 'Console Gaming Pro', 'Dernière génération', 4500.00, 13.0, 'https://picsum.photos/seed/console1/400/400', 'Electronics', NOW() - INTERVAL '8 days'),
('p4444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222225', 'Montre Connectée Sport', 'GPS, cardio, waterproof', 2200.00, 13.0, 'https://picsum.photos/seed/watch1/400/400', 'Electronics', NOW() - INTERVAL '7 days'),

-- Merchant 5 products
('p5555555-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226', 'Réfrigérateur Premium', 'Double porte, No Frost', 8500.00, 22.0, 'https://picsum.photos/seed/fridge1/400/400', 'Home', NOW() - INTERVAL '30 days'),
('p5555555-5555-5555-5555-555555555552', '22222222-2222-2222-2222-222222222226', 'Machine à Laver 10kg', 'Classe A+++', 6200.00, 22.0, 'https://picsum.photos/seed/washing1/400/400', 'Home', NOW() - INTERVAL '28 days'),
('p5555555-5555-5555-5555-555555555553', '22222222-2222-2222-2222-222222222226', 'TV 4K 55 pouces', 'Smart TV OLED', 9800.00, 17.0, 'https://picsum.photos/seed/tv1/400/400', 'Electronics', NOW() - INTERVAL '12 days'),
('p5555555-5555-5555-5555-555555555554', '22222222-2222-2222-2222-222222222226', 'Aspirateur Robot', 'Navigation intelligente', 3500.00, 17.0, 'https://picsum.photos/seed/vacuum1/400/400', 'Home', NOW() - INTERVAL '11 days'),
('p5555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222226', 'Costume Homme Luxe', 'Laine italienne premium', 5500.00, 25.0, 'https://picsum.photos/seed/suit1/400/400', 'Fashion', NOW() - INTERVAL '6 days'),
('p5555555-5555-5555-5555-555555555556', '22222222-2222-2222-2222-222222222226', 'Chaussures Cuir Luxe', 'Fait main artisanal', 3200.00, 25.0, 'https://picsum.photos/seed/leather1/400/400', 'Fashion', NOW() - INTERVAL '5 days'),

-- Merchant 6 products
('p6666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555551', 'Chaussures Running Pro', 'Amorti maximal', 1200.00, 15.0, 'https://picsum.photos/seed/running1/400/400', 'Sports', NOW() - INTERVAL '14 days'),
('p6666666-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551', 'Tapis Yoga Premium', 'Antidérapant écologique', 450.00, 18.0, 'https://picsum.photos/seed/yoga1/400/400', 'Sports', NOW() - INTERVAL '13 days'),
('p6666666-6666-6666-6666-666666666663', '55555555-5555-5555-5555-555555555551', 'Haltères Réglables', 'De 5 à 25kg', 1800.00, 15.0, 'https://picsum.photos/seed/weights1/400/400', 'Sports', NOW() - INTERVAL '12 days'),
('p6666666-6666-6666-6666-666666666664', '55555555-5555-5555-5555-555555555551', 'Montre GPS Running', 'Autonomie 20h', 2500.00, 18.0, 'https://picsum.photos/seed/gpswatch1/400/400', 'Sports', NOW() - INTERVAL '7 days'),

-- Produits variés additionnels
('p7777777-7777-7777-7777-777777777771', '22222222-2222-2222-2222-222222222224', 'Lunettes de Soleil Ray', 'Protection UV 100%', 680.00, 14.0, 'https://picsum.photos/seed/sunglasses1/400/400', 'Fashion', NOW() - INTERVAL '10 days'),
('p8888888-8888-8888-8888-888888888881', '22222222-2222-2222-2222-222222222225', 'Écouteurs True Wireless', 'Réduction bruit active', 1500.00, 16.0, 'https://picsum.photos/seed/earbuds1/400/400', 'Electronics', NOW() - INTERVAL '9 days'),
('p9999999-9999-9999-9999-999999999991', '22222222-2222-2222-2222-222222222223', 'Parfum Femme Luxe 50ml', 'Notes florales orientales', 950.00, 15.0, 'https://picsum.photos/seed/perfume1/400/400', 'Beauty', NOW() - INTERVAL '8 days'),
('pa111111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222226', 'Four Micro-ondes', 'Grill multifonction', 1800.00, 17.0, 'https://picsum.photos/seed/microwave1/400/400', 'Home', NOW() - INTERVAL '4 days');

-- ============================================
-- 4. COMMISSIONS (40 commissions)
-- ============================================

INSERT INTO commissions (id, influencer_id, amount, status, created_at, product_id, merchant_id)
VALUES
-- Influencer 1 commissions
('com11111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 125.00, 'paid', NOW() - INTERVAL '18 days', 'p1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'),
('com11111-1111-1111-1111-111111111112', '33333333-3333-3333-3333-333333333333', 270.00, 'paid', NOW() - INTERVAL '16 days', 'p3333333-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222224'),
('com11111-1111-1111-1111-111111111113', '33333333-3333-3333-3333-333333333333', 450.00, 'pending', NOW() - INTERVAL '5 days', 'p4444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222225'),
('com11111-1111-1111-1111-111111111114', '33333333-3333-3333-3333-333333333333', 165.00, 'paid', NOW() - INTERVAL '12 days', 'p2222222-2222-2222-2222-222222222221', '22222222-2222-2222-2222-222222222223'),
('com11111-1111-1111-1111-111111111115', '33333333-3333-3333-3333-333333333333', 850.00, 'pending', NOW() - INTERVAL '3 days', 'p5555555-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226'),

-- Influencer 2 commissions
('com22222-2222-2222-2222-222222222221', '33333333-3333-3333-3333-333333333334', 320.00, 'paid', NOW() - INTERVAL '15 days', 'p4444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222225'),
('com22222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333334', 180.00, 'paid', NOW() - INTERVAL '14 days', 'p6666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555551'),
('com22222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333334', 560.00, 'pending', NOW() - INTERVAL '6 days', 'p5555555-5555-5555-5555-555555555553', '22222222-2222-2222-2222-222222222226'),
('com22222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333334', 95.00, 'paid', NOW() - INTERVAL '11 days', 'p2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222223'),
('com22222-2222-2222-2222-222222222225', '33333333-3333-3333-3333-333333333334', 215.00, 'paid', NOW() - INTERVAL '10 days', 'p3333333-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222224'),
('com22222-2222-2222-2222-222222222226', '33333333-3333-3333-3333-333333333334', 425.00, 'pending', NOW() - INTERVAL '4 days', 'p5555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222226'),

-- Influencer 3 commissions
('com33333-3333-3333-3333-333333333331', '33333333-3333-3333-3333-333333333335', 195.00, 'paid', NOW() - INTERVAL '17 days', 'p6666666-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551'),
('com33333-3333-3333-3333-333333333332', '33333333-3333-3333-3333-333333333335', 760.00, 'paid', NOW() - INTERVAL '13 days', 'p4444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222225'),
('com33333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333335', 285.00, 'pending', NOW() - INTERVAL '7 days', 'p3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222224'),
('com33333-3333-3333-3333-333333333334', '33333333-3333-3333-3333-333333333335', 640.00, 'paid', NOW() - INTERVAL '9 days', 'p5555555-5555-5555-5555-555555555552', '22222222-2222-2222-2222-222222222226'),
('com33333-3333-3333-3333-333333333335', '33333333-3333-3333-3333-333333333335', 135.00, 'pending', NOW() - INTERVAL '2 days', 'p1111111-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222222'),

-- Influencer 4 commissions
('com44444-4444-4444-4444-444444444441', '33333333-3333-3333-3333-333333333336', 520.00, 'paid', NOW() - INTERVAL '19 days', 'p4444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222225'),
('com44444-4444-4444-4444-444444444442', '33333333-3333-3333-3333-333333333336', 375.00, 'paid', NOW() - INTERVAL '16 days', 'p6666666-6666-6666-6666-666666666663', '55555555-5555-5555-5555-555555555551'),
('com44444-4444-4444-4444-444444444443', '33333333-3333-3333-3333-333333333336', 890.00, 'pending', NOW() - INTERVAL '8 days', 'p5555555-5555-5555-5555-555555555556', '22222222-2222-2222-2222-222222222226'),
('com44444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333336', 240.00, 'paid', NOW() - INTERVAL '14 days', 'p8888888-8888-8888-8888-888888888881', '22222222-2222-2222-2222-222222222225'),
('com44444-4444-4444-4444-444444444445', '33333333-3333-3333-3333-333333333336', 465.00, 'paid', NOW() - INTERVAL '11 days', 'p6666666-6666-6666-6666-666666666664', '55555555-5555-5555-5555-555555555551'),
('com44444-4444-4444-4444-444444444446', '33333333-3333-3333-3333-333333333336', 325.00, 'pending', NOW() - INTERVAL '4 days', 'p3333333-3333-3333-3333-333333333334', '22222222-2222-2222-2222-222222222224'),

-- Influencer 5 commissions
('com55555-5555-5555-5555-555555555551', '33333333-3333-3333-3333-333333333337', 1250.00, 'paid', NOW() - INTERVAL '20 days', 'p5555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222226'),
('com55555-5555-5555-5555-555555555552', '33333333-3333-3333-3333-333333333337', 680.00, 'paid', NOW() - INTERVAL '17 days', 'p4444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222225'),
('com55555-5555-5555-5555-555555555553', '33333333-3333-3333-3333-333333333337', 1550.00, 'pending', NOW() - INTERVAL '9 days', 'p5555555-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226'),
('com55555-5555-5555-5555-555555555554', '33333333-3333-3333-3333-333333333337', 295.00, 'paid', NOW() - INTERVAL '13 days', 'p pa111111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222226'),
('com55555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333337', 425.00, 'pending', NOW() - INTERVAL '5 days', 'p7777777-7777-7777-7777-777777777771', '22222222-2222-2222-2222-222222222224'),

-- Influencer 6 commissions
('com66666-6666-6666-6666-666666666661', '66666666-6666-6666-6666-666666666661', 340.00, 'paid', NOW() - INTERVAL '18 days', 'p6666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555551'),
('com66666-6666-6666-6666-666666666662', '66666666-6666-6666-6666-666666666661', 580.00, 'paid', NOW() - INTERVAL '15 days', 'p5555555-5555-5555-5555-555555555554', '22222222-2222-2222-2222-222222222226'),
('com66666-6666-6666-6666-666666666663', '66666666-6666-6666-6666-666666666661', 215.00, 'pending', NOW() - INTERVAL '6 days', 'p3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222224'),
('com66666-6666-6666-6666-666666666664', '66666666-6666-6666-6666-666666666661', 390.00, 'paid', NOW() - INTERVAL '10 days', 'p4444444-4444-4444-4444-444444444443', '22222222-2222-2222-2222-222222222225'),

-- Influencer 7 commissions
('com77777-7777-7777-7777-777777777771', '77777777-7777-7777-7777-777777777771', 485.00, 'paid', NOW() - INTERVAL '16 days', 'p5555555-5555-5555-5555-555555555556', '22222222-2222-2222-2222-222222222226'),
('com77777-7777-7777-7777-777777777772', '77777777-7777-7777-7777-777777777771', 275.00, 'paid', NOW() - INTERVAL '12 days', 'p6666666-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551'),
('com77777-7777-7777-7777-777777777773', '77777777-7777-7777-7777-777777777771', 640.00, 'pending', NOW() - INTERVAL '7 days', 'p4444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222225'),
('com77777-7777-7777-7777-777777777774', '77777777-7777-7777-7777-777777777771', 190.00, 'pending', NOW() - INTERVAL '3 days', 'p2222222-2222-2222-2222-222222222223', '22222222-2222-2222-2222-222222222223');

-- ============================================
-- 5. LEADS (20 leads pour commerciaux)
-- ============================================

INSERT INTO leads (id, commercial_id, merchant_id, company_name, contact_email, contact_phone, status, notes, created_at, last_contact_date)
VALUES
-- Commercial 1 leads
('lead1111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222222', 'TechStyle Morocco', 'contact@techstyle.ma', '+212 6 12 34 56 78', 'converted', 'Client converti en PRO', NOW() - INTERVAL '30 days', NOW() - INTERVAL '2 days'),
('lead1111-1111-1111-1111-111111111112', '44444444-4444-4444-4444-444444444441', NULL, 'Fashion Trends', 'info@fashiontrends.ma', '+212 6 23 45 67 89', 'qualified', 'Très intéressé par offre PRO', NOW() - INTERVAL '10 days', NOW() - INTERVAL '1 day'),
('lead1111-1111-1111-1111-111111111113', '44444444-4444-4444-4444-444444444441', NULL, 'Beauty Express', 'hello@beautyexpress.ma', '+212 6 34 56 78 90', 'contacted', 'Premier contact effectué', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('lead1111-1111-1111-1111-111111111114', '44444444-4444-4444-4444-444444444441', NULL, 'Electro Plus', 'contact@electroplus.ma', '+212 6 45 67 89 01', 'new', 'Prospect découvert via LinkedIn', NOW() - INTERVAL '2 days', NULL),

-- Commercial 2 leads
('lead2222-2222-2222-2222-222222222221', '44444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222224', 'FashionHub Marrakech', 'info@fashionhub.ma', '+212 6 56 78 90 12', 'converted', 'Converti en ENTERPRISE', NOW() - INTERVAL '25 days', NOW() - INTERVAL '3 days'),
('lead2222-2222-2222-2222-222222222222', '44444444-4444-4444-4444-444444444442', NULL, 'Mega Deals', 'sales@megadeals.ma', '+212 6 67 89 01 23', 'qualified', 'Budget confirmé 15000 DH/mois', NOW() - INTERVAL '12 days', NOW() - INTERVAL '1 day'),
('lead2222-2222-2222-2222-222222222223', '44444444-4444-4444-4444-444444444442', NULL, 'Sport Zone', 'contact@sportzone.ma', '+212 6 78 90 12 34', 'contacted', 'RDV prévu semaine prochaine', NOW() - INTERVAL '7 days', NOW() - INTERVAL '3 days'),
('lead2222-2222-2222-2222-222222222224', '44444444-4444-4444-4444-444444444442', NULL, 'Home Decor Pro', 'info@homedecorpro.ma', '+212 6 89 01 23 45', 'lost', 'Prix trop élevé pour eux', NOW() - INTERVAL '15 days', NOW() - INTERVAL '10 days'),

-- Commercial 3 leads
('lead3333-3333-3333-3333-333333333331', '44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555551', 'SportGear Fes', 'hello@sportgear.ma', '+212 6 90 12 34 56', 'converted', 'Inscrit formule PRO', NOW() - INTERVAL '20 days', NOW() - INTERVAL '1 day'),
('lead3333-3333-3333-3333-333333333332', '44444444-4444-4444-4444-444444444443', NULL, 'Gadget Store', 'contact@gadgetstore.ma', '+212 6 01 23 45 67', 'qualified', 'Intéressé par ENTERPRISE', NOW() - INTERVAL '8 days', NOW() - INTERVAL '2 days'),
('lead3333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444443', NULL, 'Luxury Brands MA', 'vip@luxurybrands.ma', '+212 6 12 34 56 78', 'contacted', 'Demande démo personnalisée', NOW() - INTERVAL '6 days', NOW() - INTERVAL '4 days'),

-- Commercial 4 leads
('lead4444-4444-4444-4444-444444444441', '44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222226', 'MegaStore Tanger', 'pro@megastore.ma', '+212 6 23 45 67 89', 'converted', 'Upgrade vers ENTERPRISE', NOW() - INTERVAL '35 days', NOW() - INTERVAL '5 days'),
('lead4444-4444-4444-4444-444444444442', '44444444-4444-4444-4444-444444444444', NULL, 'Kids Fashion', 'contact@kidsfashion.ma', '+212 6 34 56 78 90', 'qualified', 'Budget 8000 DH confirmé', NOW() - INTERVAL '14 days', NOW() - INTERVAL '2 days'),
('lead4444-4444-4444-4444-444444444443', '44444444-4444-4444-4444-444444444444', NULL, 'Food Delivery Plus', 'sales@fooddelivery.ma', '+212 6 45 67 89 01', 'new', 'Lead entrant formulaire site', NOW() - INTERVAL '1 day', NULL),

-- Commercial 5 leads
('lead5555-5555-5555-5555-555555555551', '44444444-4444-4444-4444-444444444445', NULL, 'Book Store Online', 'hello@bookstore.ma', '+212 6 56 78 90 12', 'qualified', 'Cherche solution marketing', NOW() - INTERVAL '11 days', NOW() - INTERVAL '3 days'),
('lead5555-5555-5555-5555-555555555552', '44444444-4444-4444-4444-444444444445', NULL, 'Pet Shop Morocco', 'info@petshop.ma', '+212 6 67 89 01 23', 'contacted', 'Email envoyé, en attente retour', NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days'),
('lead5555-5555-5555-5555-555555555553', '44444444-4444-4444-4444-444444444445', NULL, 'Garden Center', 'contact@gardencenter.ma', '+212 6 78 90 12 34', 'lost', 'Préfère solution concurrente', NOW() - INTERVAL '18 days', NOW() - INTERVAL '12 days'),

-- Commercial 6 leads
('lead6666-6666-6666-6666-666666666661', '44444444-4444-4444-4444-444444444446', NULL, 'Auto Parts Shop', 'sales@autoparts.ma', '+212 6 89 01 23 45', 'qualified', 'Présentation effectuée', NOW() - INTERVAL '13 days', NOW() - INTERVAL '4 days'),
('lead6666-6666-6666-6666-666666666662', '44444444-4444-4444-4444-444444444446', NULL, 'Mobile Accessories', 'info@mobileacc.ma', '+212 6 90 12 34 56', 'contacted', 'Appel téléphonique fait', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
('lead6666-6666-6666-6666-666666666663', '44444444-4444-4444-4444-444444444446', NULL, 'Travel Agency Pro', 'booking@travelagency.ma', '+212 6 01 23 45 67', 'new', 'Référé par client existant', NOW() - INTERVAL '3 days', NULL);

-- ============================================
-- 6. INVOICES (15 factures)
-- ============================================

-- NOTE: La table invoices doit contenir: subscription_id, amount, status, due_date, paid_at
-- Si la structure est différente, ajuster selon schema réel

INSERT INTO invoices (id, subscription_id, amount, status, due_date, paid_at, created_at)
VALUES
-- Factures merchants FREE (petits montants)
('inv11111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 0.00, 'paid', NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days', NOW() - INTERVAL '30 days'),
('inv11112-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222223', 0.00, 'paid', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '25 days'),

-- Factures merchants PRO (499 DH/mois)
('inv22221-2222-2222-2222-222222222221', '22222222-2222-2222-2222-222222222224', 499.00, 'paid', NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days', NOW() - INTERVAL '20 days'),
('inv22222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222224', 499.00, 'paid', NOW() + INTERVAL '15 days', NULL, NOW() - INTERVAL '5 days'),
('inv33331-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222225', 499.00, 'paid', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '15 days'),
('inv33332-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222225', 499.00, 'pending', NOW() + INTERVAL '20 days', NULL, NOW() - INTERVAL '2 days'),
('inv44441-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555551', 499.00, 'paid', NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days', NOW() - INTERVAL '12 days'),

-- Factures merchants ENTERPRISE (1499 DH/mois)
('inv55551-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226', 1499.00, 'paid', NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days', NOW() - INTERVAL '30 days'),
('inv55552-5555-5555-5555-555555555552', '22222222-2222-2222-2222-222222222226', 1499.00, 'paid', NOW() + INTERVAL '5 days', NOW() - INTERVAL '1 day', NOW() - INTERVAL '5 days'),
('inv55553-5555-5555-5555-555555555553', '22222222-2222-2222-2222-222222222226', 1499.00, 'pending', NOW() + INTERVAL '35 days', NULL, NOW()),

-- Factures en retard
('inv66661-6666-6666-6666-666666666661', '22222222-2222-2222-2222-222222222224', 499.00, 'overdue', NOW() - INTERVAL '5 days', NULL, NOW() - INTERVAL '35 days'),
('inv66662-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551', 499.00, 'overdue', NOW() - INTERVAL '10 days', NULL, NOW() - INTERVAL '40 days'),

-- Factures annulées
('inv77771-7777-7777-7777-777777777771', '22222222-2222-2222-2222-222222222223', 0.00, 'cancelled', NOW() - INTERVAL '15 days', NULL, NOW() - INTERVAL '20 days'),
('inv77772-7777-7777-7777-777777777772', '22222222-2222-2222-2222-222222222225', 499.00, 'cancelled', NOW() - INTERVAL '12 days', NULL, NOW() - INTERVAL '18 days'),

-- Factures futures
('inv88881-8888-8888-8888-888888888881', '22222222-2222-2222-2222-222222222222', 0.00, 'pending', NOW() + INTERVAL '30 days', NULL, NOW());

-- ============================================
-- RÉSUMÉ DES DONNÉES GÉNÉRÉES
-- ============================================

DO $$
DECLARE
    total_users INT;
    total_campaigns INT;
    total_products INT;
    total_commissions INT;
    total_payouts INT;
    total_conversations INT;
    total_messages INT;
    total_leads INT;
    total_invoices INT;
BEGIN
    SELECT COUNT(*) INTO total_users FROM users;
    SELECT COUNT(*) INTO total_campaigns FROM campaigns;
    SELECT COUNT(*) INTO total_products FROM products;
    SELECT COUNT(*) INTO total_commissions FROM commissions;
    SELECT COUNT(*) INTO total_payouts FROM payouts;
    SELECT COUNT(*) INTO total_conversations FROM conversations;
    SELECT COUNT(*) INTO total_messages FROM messages;
    SELECT COUNT(*) INTO total_leads FROM leads;
    SELECT COUNT(*) INTO total_invoices FROM invoices;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ DONNÉES DE TEST GÉNÉRÉES AVEC SUCCÈS';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'RÉSUMÉ:';
    RAISE NOTICE '  - Users: %', total_users;
    RAISE NOTICE '  - Campaigns: %', total_campaigns;
    RAISE NOTICE '  - Products: %', total_products;
    RAISE NOTICE '  - Commissions: %', total_commissions;
    RAISE NOTICE '  - Payouts: %', total_payouts;
    RAISE NOTICE '  - Conversations: %', total_conversations;
    RAISE NOTICE '  - Messages: %', total_messages;
    RAISE NOTICE '  - Leads: %', total_leads;
    RAISE NOTICE '  - Invoices: %', total_invoices;
    RAISE NOTICE '';
    RAISE NOTICE 'PAR RÔLE:';
    RAISE NOTICE '  - Admin: 1';
    RAISE NOTICE '  - Merchants: 6 (2 FREE, 3 PRO, 1 ENTERPRISE)';
    RAISE NOTICE '  - Influencers: 7';
    RAISE NOTICE '  - Commerciaux: 6';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
