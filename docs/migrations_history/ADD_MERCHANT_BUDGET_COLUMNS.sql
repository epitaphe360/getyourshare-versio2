-- ========================================
-- AJOUT DES COLONNES DE BUDGET AUX MERCHANTS
-- ========================================
-- À exécuter dans l'éditeur SQL de Supabase
--
-- Dashboard Supabase > SQL Editor > New Query
-- Collez ce script et cliquez sur "Run"
-- ========================================

-- 1. Ajouter les colonnes de budget à la table users (si elles n'existent pas)
ALTER TABLE users ADD COLUMN IF NOT EXISTS company_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS balance DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_spent DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS campaigns_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';

-- 2. Vérifier que les colonnes ont été ajoutées
SELECT 
    column_name, 
    data_type, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('company_name', 'balance', 'total_spent', 'campaigns_count', 'country', 'status')
ORDER BY column_name;

-- 3. (Optionnel) Afficher les merchants avec leurs nouvelles colonnes
SELECT 
    id,
    email,
    company_name,
    balance,
    total_spent,
    campaigns_count,
    country,
    status,
    created_at
FROM users
WHERE role = 'merchant'
ORDER BY created_at DESC;

-- ========================================
-- RÉSULTAT ATTENDU:
-- Les colonnes devraient maintenant exister:
-- - company_name (VARCHAR)
-- - balance (DECIMAL)
-- - total_spent (DECIMAL)
-- - campaigns_count (INTEGER)
-- - country (VARCHAR)
-- - status (VARCHAR)
-- ========================================
