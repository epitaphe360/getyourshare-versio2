-- ========================================
-- SCRIPT SQL POUR AJOUTER LE RÔLE 'COMMERCIAL'
-- ========================================
-- À exécuter dans l'éditeur SQL de Supabase
--
-- Dashboard Supabase > SQL Editor > New Query
-- Collez ce script et cliquez sur "Run"
-- ========================================

-- 1. Supprimer l'ancienne contrainte sur les rôles
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- 2. Ajouter la nouvelle contrainte incluant 'commercial'
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('admin', 'merchant', 'influencer', 'commercial', 'affiliate'));

-- 3. Vérifier que la contrainte a été créée
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint 
WHERE conrelid = 'users'::regclass 
AND conname = 'users_role_check';

-- 4. (Optionnel) Afficher les rôles actuels dans la base
SELECT DISTINCT role, COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;

-- ========================================
-- RÉSULTAT ATTENDU:
-- La contrainte devrait maintenant accepter:
-- admin, merchant, influencer, commercial, affiliate
-- ========================================
