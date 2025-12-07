-- ===================================================================================
-- SCENARIO D'AUTOMATISATION COMPLET - GETYOURSHARE
-- VERSION: 2.0 (CORRECTED SCHEMA)
-- DATE: 2024-05-22
-- DESCRIPTION: Ce script execute un test de bout en bout:
--    1. Nettoyage des données de test.
--    2. Création des comptes (Admin, Influenceur, Marchand).
--    3. Simulation paiement abonnement.
--    4. Création catalogue (Produits/Services).
--    5. Génération lien affiliation & Tracking.
--    6. Cycle de vente: Clic -> Conversion -> Distribution des gains.
--    7. Gestion des remboursements (Annulation gains).
--    8. Simulation de retrait.
-- ===================================================================================

-- ===================================================================================
-- PHASE 0 : NETTOYAGE
-- ===================================================================================
\echo 'PHASE 0 : NETTOYAGE...'

-- Suppression des données de test liées aux emails spécifiques
DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email IN ('marchand@test.com', 'influenceur@test.com', 'admin@getyourshare.com'));
DELETE FROM social_media_publications WHERE user_id IN (SELECT id FROM users WHERE email IN ('marchand@test.com', 'influenceur@test.com', 'admin@getyourshare.com'));
DELETE FROM affiliate_links WHERE influencer_id IN (SELECT id FROM users WHERE email IN ('marchand@test.com', 'influenceur@test.com', 'admin@getyourshare.com'));
DELETE FROM products WHERE merchant_id IN (SELECT id FROM users WHERE email IN ('marchand@test.com', 'influenceur@test.com', 'admin@getyourshare.com'));
DELETE FROM services WHERE merchant_id IN (SELECT id FROM users WHERE email IN ('marchand@test.com', 'influenceur@test.com', 'admin@getyourshare.com'));
DELETE FROM users WHERE email IN ('marchand@test.com', 'influenceur@test.com', 'admin@getyourshare.com');

-- ===================================================================================
-- PHASE 1 : SETUP ACTEURS & COMPTES
-- ===================================================================================
\echo 'PHASE 1 : SETUP ACTEURS & COMPTES...'

-- 1.1 Admin
INSERT INTO users (role, email, password_hash, full_name, balance, created_at)
VALUES ('admin', 'admin@getyourshare.com', 'secure_pass', 'Admin Platform', 0.00, NOW());

-- 1.2 Influenceur
INSERT INTO users (role, email, password_hash, full_name, balance, created_at)
VALUES ('influencer', 'influenceur@test.com', 'hashed_password', 'Star Influenceur', 0.00, NOW());

-- 1.3 Marchand
INSERT INTO users (role, email, password_hash, full_name, balance, created_at)
VALUES ('merchant', 'marchand@test.com', 'hashed_password', 'Mon Entreprise', 0.00, NOW());

-- ===================================================================================
-- PHASE 2 : FLUX FINANCIER ENTRANT (ABONNEMENT)
-- ===================================================================================
\echo 'PHASE 2 : FLUX FINANCIER ENTRANT...'

-- 2.1 Paiement Abonnement (29.99$) -> Admin Balance
UPDATE users SET balance = balance + 29.99 WHERE email = 'admin@getyourshare.com';

-- ===================================================================================
-- PHASE 3 : CRÉATION DE L'OFFRE
-- ===================================================================================
\echo 'PHASE 3 : CRÉATION DE L''OFFRE...'

-- 3.1 Produit
INSERT INTO products (merchant_id, name, price, commission_rate)
SELECT id, 'Super Gadget', 100.00, 10.0
FROM users WHERE email = 'marchand@test.com';

-- 3.2 Service
INSERT INTO services (merchant_id, name, price_per_lead, commission_rate)
SELECT id, 'Consultation Expert', 200.00, 15.0
FROM users WHERE email = 'marchand@test.com';

-- ===================================================================================
-- PHASE 4 : PARTENARIAT & TRACKING
-- ===================================================================================
\echo 'PHASE 4 : PARTENARIAT & TRACKING...'

-- 4.1 Publication
INSERT INTO social_media_publications (user_id, product_id, status, platform)
SELECT 
    (SELECT id FROM users WHERE email = 'influenceur@test.com'),
    (SELECT id FROM products WHERE name = 'Super Gadget' LIMIT 1),
    'approved',
    'instagram';

-- 4.2 Affiliate Link
INSERT INTO affiliate_links (influencer_id, product_id, unique_code, url)
SELECT 
    (SELECT id FROM users WHERE email = 'influenceur@test.com'),
    (SELECT id FROM products WHERE name = 'Super Gadget' LIMIT 1),
    'REF-TEST-SQL',
    'https://shareyoursales.ma/r/REF-TEST-SQL';

-- ===================================================================================
-- PHASE 5 : CYCLE DE VENTE COMPLET
-- ===================================================================================
\echo 'PHASE 5 : CYCLE DE VENTE COMPLET...'

-- 5.1 Clic
-- UPDATE affiliate_links SET clicks = clicks + 1 WHERE unique_code = 'REF-TEST-SQL'; -- Column clicks does not exist

INSERT INTO tracking_events (tracking_link_id, event_type, created_at)
SELECT id, 'click', NOW()
FROM affiliate_links WHERE unique_code = 'REF-TEST-SQL';

-- 5.2 Conversion PENDING
INSERT INTO conversions (tracking_link_id, sale_amount, commission_amount, status, created_at)
SELECT id, 100.00, 10.00, 'pending', NOW()
FROM affiliate_links WHERE unique_code = 'REF-TEST-SQL';

-- 5.3 Validation COMPLETED & Distribution
UPDATE conversions SET status = 'paid' 
WHERE tracking_link_id = (SELECT id FROM affiliate_links WHERE unique_code = 'REF-TEST-SQL');

-- Distribution (Calcul manuel pour SQL)
-- Influenceur: +10.00
UPDATE users SET balance = balance + 10.00 WHERE email = 'influenceur@test.com';
-- Admin: +2.00 (2%)
UPDATE users SET balance = balance + 2.00 WHERE email = 'admin@getyourshare.com';
-- Marchand: +88.00 (100 - 10 - 2)
UPDATE users SET balance = balance + 88.00 WHERE email = 'marchand@test.com';

-- ===================================================================================
-- PHASE 6 : REMBOURSEMENT
-- ===================================================================================
\echo 'PHASE 6 : REMBOURSEMENT...'

UPDATE conversions SET status = 'refunded' 
WHERE tracking_link_id = (SELECT id FROM affiliate_links WHERE unique_code = 'REF-TEST-SQL');

-- Annulation des gains
UPDATE users SET balance = balance - 10.00 WHERE email = 'influenceur@test.com';
UPDATE users SET balance = balance - 2.00 WHERE email = 'admin@getyourshare.com';
UPDATE users SET balance = balance - 88.00 WHERE email = 'marchand@test.com';

-- ===================================================================================
-- PHASE 7 : RETRAIT
-- ===================================================================================
\echo 'PHASE 7 : RETRAIT...'

-- Ajout fond test
UPDATE users SET balance = balance + 50.00 WHERE email = 'influenceur@test.com';

-- Retrait valide
UPDATE users SET balance = balance - 50.00 WHERE email = 'influenceur@test.com';

\echo 'SCENARIO TERMINE AVEC SUCCES'
