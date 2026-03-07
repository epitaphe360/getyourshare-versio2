-- ========================================
-- AJOUT DES COLONNES POUR LES INFLUENCEURS
-- ========================================
-- À exécuter dans l'éditeur SQL de Supabase
-- ========================================

-- 1. Ajouter les colonnes pour les influenceurs (si elles n'existent pas)
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS followers_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS engagement_rate DECIMAL(5,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_earned DECIMAL(10,2) DEFAULT 0;

-- 2. Vérifier que les colonnes ont été ajoutées
SELECT 
    column_name, 
    data_type, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('first_name', 'last_name', 'followers_count', 'engagement_rate', 'total_earned')
ORDER BY column_name;

-- 3. (Optionnel) Afficher les influenceurs avec leurs nouvelles colonnes
SELECT 
    id,
    email,
    first_name,
    last_name,
    company_name,
    followers_count,
    engagement_rate,
    balance,
    total_earned,
    country,
    status,
    created_at
FROM users
WHERE role = 'influencer'
ORDER BY created_at DESC;

-- ========================================
-- RÉSULTAT ATTENDU:
-- Les colonnes devraient maintenant exister:
-- - first_name (VARCHAR)
-- - last_name (VARCHAR)
-- - followers_count (INTEGER)
-- - engagement_rate (DECIMAL)
-- - total_earned (DECIMAL)
-- ========================================
