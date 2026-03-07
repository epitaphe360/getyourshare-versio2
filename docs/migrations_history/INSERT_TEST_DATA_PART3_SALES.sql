-- ============================================
-- SCRIPT 3/4 : INSERTION DES DONNÉES DE TEST - VENTES & COMMISSIONS
-- PARTIE 3 : Conversions, Sales, Commissions, Payouts, Leads, Transactions
-- ============================================

-- ============================================
-- 1. INSERTION DES CONVERSIONS (30 conversions)
-- ============================================
INSERT INTO public.conversions (tracking_link_id, influencer_id, merchant_id, product_id, sale_amount, commission_amount, commission_rate, status, created_at)
SELECT 
    tl.id,
    tl.influencer_id,
    tl.merchant_id,
    tl.product_id,
    (random() * 500 + 50)::decimal(12,2),
    (random() * 75 + 5)::decimal(12,2),
    CASE 
        WHEN tl.merchant_id = '22222222-2222-2222-2222-222222222222' THEN 12.00
        WHEN tl.merchant_id = '22222222-2222-2222-2222-222222222223' THEN 15.00
        WHEN tl.merchant_id = '22222222-2222-2222-2222-222222222224' THEN 10.00
        WHEN tl.merchant_id = '22222222-2222-2222-2222-222222222225' THEN 8.00
        ELSE 11.00
    END,
    CASE (random() * 3)::integer
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'completed'
        WHEN 2 THEN 'cancelled'
        ELSE 'refunded'
    END,
    NOW() - (random() * INTERVAL '45 days')
FROM public.tracking_links tl
LIMIT 30;

-- ============================================
-- 2. INSERTION DES VENTES (25 sales)
-- ============================================
INSERT INTO public.sales (merchant_id, influencer_id, product_id, amount, commission_amount, platform_commission, status, created_at)
SELECT 
    m.id,
    i.id,
    p.id,
    (random() * 800 + 100)::decimal(12,2) as amount,
    (random() * 120 + 10)::decimal(12,2) as commission_amount,
    (random() * 20 + 5)::decimal(12,2) as platform_commission,
    'completed',
    NOW() - (random() * INTERVAL '50 days')
FROM (SELECT id FROM public.users WHERE role = 'merchant' ORDER BY random() LIMIT 5) m
CROSS JOIN (SELECT id FROM public.users WHERE role = 'influencer' ORDER BY random() LIMIT 5) i
CROSS JOIN LATERAL (SELECT id FROM public.products WHERE merchant_id = m.id ORDER BY random() LIMIT 1) p
LIMIT 25;

-- ============================================
-- 3. INSERTION DES COMMISSIONS (25 commissions correspondantes)
-- ============================================
INSERT INTO public.commissions (sale_id, influencer_id, amount, status, payout_date, created_at)
SELECT 
    s.id,
    s.influencer_id,
    s.commission_amount,
    CASE (random() * 3)::integer
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'approved'
        WHEN 2 THEN 'paid'
        ELSE 'cancelled'
    END,
    CASE 
        WHEN random() > 0.5 THEN NOW() - (random() * INTERVAL '20 days')
        ELSE NULL
    END,
    s.created_at + INTERVAL '1 day'
FROM public.sales s
WHERE s.status = 'completed'
LIMIT 25;

-- ============================================
-- 4. INSERTION DES PAYOUTS (10 demandes de paiement)
-- ============================================
INSERT INTO public.payouts (influencer_id, amount, status, method, payment_details, requested_at, processed_at, created_at)
VALUES 
    ('33333333-3333-3333-3333-333333333333', 1250.50, 'paid', 'bank_transfer', '{"iban": "FR76XXXXXXXXXXXXXXX", "bic": "BNPAFRPP"}', NOW() - INTERVAL '30 days', NOW() - INTERVAL '25 days', NOW() - INTERVAL '30 days'),
    ('33333333-3333-3333-3333-333333333334', 2340.00, 'paid', 'paypal', '{"email": "pierre.tech@email.com"}', NOW() - INTERVAL '20 days', NOW() - INTERVAL '18 days', NOW() - INTERVAL '20 days'),
    ('33333333-3333-3333-3333-333333333335', 890.75, 'processing', 'bank_transfer', '{"iban": "FR76XXXXXXXXXXXXXXX", "bic": "BNPAFRPP"}', NOW() - INTERVAL '5 days', NULL, NOW() - INTERVAL '5 days'),
    ('33333333-3333-3333-3333-333333333336', 1567.25, 'paid', 'paypal', '{"email": "alex.fitness@email.com"}', NOW() - INTERVAL '15 days', NOW() - INTERVAL '12 days', NOW() - INTERVAL '15 days'),
    ('33333333-3333-3333-3333-333333333337', 3120.00, 'paid', 'bank_transfer', '{"iban": "FR76XXXXXXXXXXXXXXX", "bic": "BNPAFRPP"}', NOW() - INTERVAL '25 days', NOW() - INTERVAL '22 days', NOW() - INTERVAL '25 days'),
    ('33333333-3333-3333-3333-333333333333', 745.00, 'pending', 'bank_transfer', '{"iban": "FR76XXXXXXXXXXXXXXX", "bic": "BNPAFRPP"}', NOW() - INTERVAL '3 days', NULL, NOW() - INTERVAL '3 days'),
    ('33333333-3333-3333-3333-333333333334', 1890.50, 'processing', 'paypal', '{"email": "pierre.tech@email.com"}', NOW() - INTERVAL '7 days', NULL, NOW() - INTERVAL '7 days'),
    ('33333333-3333-3333-3333-333333333335', 650.00, 'paid', 'bank_transfer', '{"iban": "FR76XXXXXXXXXXXXXXX", "bic": "BNPAFRPP"}', NOW() - INTERVAL '40 days', NOW() - INTERVAL '35 days', NOW() - INTERVAL '40 days'),
    ('33333333-3333-3333-3333-333333333336', 980.75, 'pending', 'paypal', '{"email": "alex.fitness@email.com"}', NOW() - INTERVAL '2 days', NULL, NOW() - INTERVAL '2 days'),
    ('33333333-3333-3333-3333-333333333337', 2250.00, 'processing', 'bank_transfer', '{"iban": "FR76XXXXXXXXXXXXXXX", "bic": "BNPAFRPP"}', NOW() - INTERVAL '10 days', NULL, NOW() - INTERVAL '10 days');

-- ============================================
-- 5. INSERTION DES LEADS (30 leads avec commercial_id)
-- ============================================
INSERT INTO public.leads (commercial_id, merchant_id, customer_name, customer_email, customer_phone, lead_status, source, notes, score, created_at)
VALUES 
    -- Leads de Lucas Commercial
    ('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', 'Sophie Boutique - Boutique Mode Paris', 'sophie@boutique.com', '+33612345001', 'qualified', 'cold_call', 'Intéressée par abonnement Pro', 85, NOW() - INTERVAL '10 days'),
    ('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222223', 'Marc Informatique - IT Solutions', 'marc@info.com', '+33612345002', 'contacted', 'referral', 'Besoin solution affiliation tech', 70, NOW() - INTERVAL '15 days'),
    ('44444444-4444-4444-4444-444444444444', NULL, 'Julie Commerce - E-commerce France', 'julie@commerce.fr', '+33612345003', 'new', 'website', 'Demande de démo', 60, NOW() - INTERVAL '1 day'),
    ('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222224', 'Claire Beauty - Beauty Concept Store', 'claire@beauty.fr', '+33612345004', 'negotiating', 'linkedin', 'Négociation tarifs Elite', 90, NOW() - INTERVAL '20 days'),
    ('44444444-4444-4444-4444-444444444444', NULL, 'Thomas Shop - Multi Shop Online', 'thomas@shop.com', '+33612345005', 'qualified', 'email_campaign', 'Intéressé par marketplace', 75, NOW() - INTERVAL '8 days'),
    ('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222225', 'Laura Sport - Sport Distribution', 'laura@sport.fr', '+33612345006', 'contacted', 'trade_show', 'Rencontrée au salon Paris', 65, NOW() - INTERVAL '12 days'),
    ('44444444-4444-4444-4444-444444444444', NULL, 'David Retail - Retail Group', 'david@retail.com', '+33612345007', 'new', 'website', 'Formulaire contact rempli', 50, NOW() - INTERVAL '2 days'),
    ('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222226', 'Emma Gourmet - Gourmet Delices', 'emma@gourmet.fr', '+33612345008', 'qualified', 'cold_call', 'Budget confirmé 5K/mois', 88, NOW() - INTERVAL '5 days'),
    ('44444444-4444-4444-4444-444444444444', NULL, 'Nicolas Digital - Digital Agency', 'nicolas@digital.fr', '+33612345009', 'lost', 'linkedin', 'Pas de budget actuellement', 30, NOW() - INTERVAL '45 days'),
    ('44444444-4444-4444-4444-444444444444', NULL, 'Marie Trends - Trends Fashion', 'marie@trends.com', '+33612345010', 'contacted', 'referral', 'Référée par Sophie', 72, NOW() - INTERVAL '6 days'),
    
    -- Leads de Claire Vente
    ('44444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222222', 'Pierre Mode - Mode Masculine', 'pierre@mode.fr', '+33612345011', 'negotiating', 'linkedin', 'Veut tester 3 mois', 82, NOW() - INTERVAL '18 days'),
    ('44444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222223', 'Alice Tech - TechStore Pro', 'alice@tech.com', '+33612345012', 'qualified', 'trade_show', 'Salon VivaTech 2024', 80, NOW() - INTERVAL '10 days'),
    ('44444444-4444-4444-4444-444444444445', NULL, 'Bob Startup - Startup Innovante', 'bob@startup.io', '+33612345013', 'contacted', 'email_campaign', 'Startup en levée de fonds', 68, NOW() - INTERVAL '14 days'),
    ('44444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222224', 'Sarah Cosmetics - Cosmetics Lab', 'sarah@cosmetics.fr', '+33612345014', 'qualified', 'referral', 'Recommandée par Claire Beauty', 85, NOW() - INTERVAL '9 days'),
    ('44444444-4444-4444-4444-444444444445', NULL, 'Lucas Market - Market Place', 'lucas@market.com', '+33612345015', 'new', 'website', 'Demande information tarifs', 55, NOW() - INTERVAL '1 day'),
    ('44444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222225', 'Eva Fitness - Fitness Studio Chain', 'eva@fitness.fr', '+33612345016', 'negotiating', 'cold_call', 'Négociation contrat annuel', 92, NOW() - INTERVAL '22 days'),
    ('44444444-4444-4444-4444-444444444445', NULL, 'Max Commerce - Commerce Solutions', 'max@commerce.com', '+33612345017', 'contacted', 'linkedin', 'Demande case studies', 70, NOW() - INTERVAL '11 days'),
    ('44444444-4444-4444-4444-444444444445', NULL, 'Lisa Organic - Organic Products', 'lisa@organic.fr', '+33612345018', 'qualified', 'trade_show', 'Salon Bio&Co', 78, NOW() - INTERVAL '13 days'),
    ('44444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222226', 'Paul Gourmet - Gourmet Express', 'paul@gourmet.com', '+33612345019', 'contacted', 'email_campaign', 'Intéressé par food niche', 73, NOW() - INTERVAL '16 days'),
    ('44444444-4444-4444-4444-444444444445', NULL, 'Anna Design - Design Studio', 'anna@design.fr', '+33612345020', 'lost', 'cold_call', 'Pas pertinent pour eux', 25, NOW() - INTERVAL '50 days'),
    
    -- Leads de David Sales
    ('44444444-4444-4444-4444-444444444446', '22222222-2222-2222-2222-222222222222', 'Hugo Fashion - Fashion Forward', 'hugo@fashion.fr', '+33612345021', 'qualified', 'referral', 'Référé par Pierre Mode', 86, NOW() - INTERVAL '7 days'),
    ('44444444-4444-4444-4444-444444444446', '22222222-2222-2222-2222-222222222223', 'Isabelle Gadgets - Gadgets World', 'isabelle@gadgets.com', '+33612345022', 'negotiating', 'linkedin', 'Veut essai gratuit 1 mois', 88, NOW() - INTERVAL '19 days'),
    ('44444444-4444-4444-4444-444444444446', NULL, 'Jacques Store - Multi Store France', 'jacques@store.fr', '+33612345023', 'contacted', 'trade_show', 'Salon E-commerce Paris', 66, NOW() - INTERVAL '17 days'),
    ('44444444-4444-4444-4444-444444444446', '22222222-2222-2222-2222-222222222224', 'Camille Beauty - Beauty Lab Paris', 'camille@beauty.com', '+33612345024', 'qualified', 'cold_call', 'Budget confirmé', 84, NOW() - INTERVAL '8 days'),
    ('44444444-4444-4444-4444-444444444446', NULL, 'Olivier Digital - Digital Commerce', 'olivier@digital.com', '+33612345025', 'new', 'website', 'Inscription newsletter', 52, NOW() - INTERVAL '2 days'),
    ('44444444-4444-4444-4444-444444444446', '22222222-2222-2222-2222-222222222225', 'Nathalie Sport - Sport Max', 'nathalie@sport.com', '+33612345026', 'contacted', 'email_campaign', 'Ouverte à discussion', 71, NOW() - INTERVAL '12 days'),
    ('44444444-4444-4444-4444-444444444446', NULL, 'Victor Tech - Tech Innovators', 'victor@tech.fr', '+33612345027', 'qualified', 'referral', 'Recommandé par Alice Tech', 81, NOW() - INTERVAL '10 days'),
    ('44444444-4444-4444-4444-444444444446', '22222222-2222-2222-2222-222222222226', 'Sophie Food - Food Paradise', 'sophie@food.fr', '+33612345028', 'negotiating', 'cold_call', 'Négociation remise volume', 89, NOW() - INTERVAL '21 days'),
    ('44444444-4444-4444-4444-444444444446', NULL, 'Martin Business - Business Group', 'martin@business.com', '+33612345029', 'contacted', 'linkedin', 'Demande présentation', 69, NOW() - INTERVAL '15 days'),
    ('44444444-4444-4444-4444-444444444446', NULL, 'Céline Market - Market Solutions', 'celine@market.fr', '+33612345030', 'new', 'website', 'Formulaire démo', 58, NOW() - INTERVAL '1 day');

-- ============================================
-- 6. INSERTION DES DÉPÔTS MARCHANDS (10 deposits)
-- ============================================
INSERT INTO public.merchant_deposits (merchant_id, amount, status, payment_method, transaction_id, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222222', 500.00, 'completed', 'credit_card', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '50 days'),
    ('22222222-2222-2222-2222-222222222223', 1000.00, 'completed', 'bank_transfer', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '45 days'),
    ('22222222-2222-2222-2222-222222222224', 300.00, 'completed', 'paypal', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '40 days'),
    ('22222222-2222-2222-2222-222222222225', 750.00, 'completed', 'credit_card', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '35 days'),
    ('22222222-2222-2222-2222-222222222226', 600.00, 'completed', 'bank_transfer', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '30 days'),
    ('22222222-2222-2222-2222-222222222222', 400.00, 'pending', 'credit_card', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '2 days'),
    ('22222222-2222-2222-2222-222222222223', 1200.00, 'processing', 'bank_transfer', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '5 days'),
    ('22222222-2222-2222-2222-222222222224', 350.00, 'completed', 'paypal', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '10 days'),
    ('22222222-2222-2222-2222-222222222225', 800.00, 'processing', 'credit_card', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '3 days'),
    ('22222222-2222-2222-2222-222222222226', 550.00, 'completed', 'bank_transfer', 'TXN-' || substr(md5(random()::text), 1, 12), NOW() - INTERVAL '15 days');

-- ============================================
-- 7. INSERTION DES DEPOSIT TRANSACTIONS (20 transactions variées)
-- ============================================
INSERT INTO public.deposit_transactions (merchant_id, type, amount, status, description, created_at)
SELECT 
    u.id,
    CASE (random() * 2)::integer
        WHEN 0 THEN 'deposit'
        WHEN 1 THEN 'withdrawal'
        ELSE 'commission'
    END,
    (random() * 1000 + 50)::decimal(12,2),
    CASE (random() * 1)::integer
        WHEN 0 THEN 'completed'
        ELSE 'completed'
    END,
    'Transaction automatique système',
    NOW() - (random() * INTERVAL '60 days')
FROM public.users u
WHERE u.role = 'merchant'
LIMIT 20;

-- ============================================
-- 8. INSERTION DES INVOICES (15 factures)
-- ============================================
INSERT INTO public.invoices (user_id, subscription_id, amount, status, invoice_number, due_date, paid_at, created_at)
SELECT 
    s.user_id,
    s.id,
    CASE 
        WHEN sp.name = 'Free' THEN 0.00
        WHEN sp.name = 'Pro' THEN 49.99
        WHEN sp.name = 'Elite' THEN 99.99
        ELSE 0.00
    END,
    CASE (random() * 3)::integer
        WHEN 0 THEN 'paid'
        WHEN 1 THEN 'pending'
        WHEN 2 THEN 'failed'
        ELSE 'draft'
    END,
    'INV-' || to_char(NOW(), 'YYYY') || '-' || lpad(floor(random() * 10000)::text, 5, '0'),
    NOW() + INTERVAL '30 days',
    CASE 
        WHEN random() > 0.3 THEN NOW() - (random() * INTERVAL '10 days')
        ELSE NULL
    END,
    NOW() - (random() * INTERVAL '30 days')
FROM public.subscriptions s
JOIN public.subscription_plans sp ON s.plan_id = sp.id
WHERE sp.name IN ('Pro', 'Elite')
LIMIT 15;

-- ============================================
-- FIN DU SCRIPT PARTIE 3
-- ============================================
-- Conversions: 30 créées
-- Sales: 25 ventes
-- Commissions: 25 commissions
-- Payouts: 10 demandes de paiement
-- Leads: 30 leads répartis sur 3 commerciaux
-- Deposits: 10 dépôts marchands
-- Transactions: 20 transactions
-- Invoices: 15 factures
-- Prêt pour la PARTIE 4: Social Media, Gamification, Ecosystem
-- ============================================
