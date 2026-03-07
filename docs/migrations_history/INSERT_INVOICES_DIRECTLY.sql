-- ========================================
-- CRÉER DES FACTURES DE TEST DIRECTEMENT EN SQL
-- ========================================
-- À exécuter dans l'éditeur SQL de Supabase
-- ========================================

-- Récupérer d'abord les IDs des marchands
WITH merchants AS (
    SELECT id, company_name, email
    FROM users
    WHERE role = 'merchant' AND status = 'active'
    LIMIT 12
)
-- Insérer des factures pour chaque marchand
INSERT INTO invoices (
    invoice_number,
    merchant_id,
    amount,
    tax_amount,
    total_amount,
    currency,
    description,
    status,
    due_date,
    paid_at,
    payment_method,
    payment_reference
)
SELECT 
    'INV-' || TO_CHAR(NOW(), 'YYYY') || '-' || LPAD(ROW_NUMBER() OVER ()::TEXT, 4, '0') as invoice_number,
    m.id as merchant_id,
    (CASE (ROW_NUMBER() OVER ()) % 5
        WHEN 0 THEN 1499.00
        WHEN 1 THEN 799.00
        WHEN 2 THEN 1999.00
        WHEN 3 THEN 499.00
        ELSE 1299.00
    END) as amount,
    (CASE (ROW_NUMBER() OVER ()) % 5
        WHEN 0 THEN 299.80
        WHEN 1 THEN 159.80
        WHEN 2 THEN 399.80
        WHEN 3 THEN 99.80
        ELSE 259.80
    END) as tax_amount,
    (CASE (ROW_NUMBER() OVER ()) % 5
        WHEN 0 THEN 1798.80
        WHEN 1 THEN 958.80
        WHEN 2 THEN 2398.80
        WHEN 3 THEN 598.80
        ELSE 1558.80
    END) as total_amount,
    'EUR' as currency,
    (CASE (ROW_NUMBER() OVER ()) % 10
        WHEN 0 THEN 'Campagne publicitaire digitale - Réseaux sociaux'
        WHEN 1 THEN 'Marketing d''influence - Package Premium'
        WHEN 2 THEN 'Création de contenu sponsorisé'
        WHEN 3 THEN 'Campagne marketing multi-canal'
        WHEN 4 THEN 'Services de promotion et visibilité'
        WHEN 5 THEN 'Pack marketing mensuel'
        WHEN 6 THEN 'Campagne Instagram + TikTok'
        WHEN 7 THEN 'Service de gestion de marque'
        WHEN 8 THEN 'Publicité ciblée et analytics'
        ELSE 'Package marketing complet'
    END) as description,
    (CASE 
        WHEN (ROW_NUMBER() OVER ()) % 3 = 0 THEN 'paid'
        WHEN (ROW_NUMBER() OVER ()) % 3 = 1 THEN 'pending'
        ELSE 'paid'
    END) as status,
    NOW() + ((ROW_NUMBER() OVER ()) % 30 || ' days')::INTERVAL as due_date,
    (CASE 
        WHEN (ROW_NUMBER() OVER ()) % 3 != 1 THEN NOW() - ((ROW_NUMBER() OVER ()) % 10 || ' days')::INTERVAL
        ELSE NULL
    END) as paid_at,
    (CASE 
        WHEN (ROW_NUMBER() OVER ()) % 3 != 1 THEN 
            (CASE (ROW_NUMBER() OVER ()) % 3
                WHEN 0 THEN 'card'
                WHEN 1 THEN 'bank_transfer'
                ELSE 'stripe'
            END)
        ELSE NULL
    END) as payment_method,
    (CASE 
        WHEN (ROW_NUMBER() OVER ()) % 3 != 1 THEN 'PAY-' || LPAD((ROW_NUMBER() OVER ())::TEXT, 8, '0')
        ELSE NULL
    END) as payment_reference
FROM merchants m
CROSS JOIN generate_series(1, 3) as series
ORDER BY m.company_name, series;

-- Vérifier le résultat
SELECT 
    i.invoice_number,
    u.company_name,
    i.total_amount,
    i.status,
    i.created_at
FROM invoices i
JOIN users u ON i.merchant_id = u.id
ORDER BY i.created_at DESC
LIMIT 20;

-- Compter le total
SELECT COUNT(*) as total_invoices FROM invoices;
