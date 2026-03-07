-- ========================================
-- SCRIPT SQL POUR CORRIGER LES PLANS D'ABONNEMENT
-- ========================================

-- 1. Supprimer la contrainte sur subscription_plan
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_subscription_plan_check;

-- 2. Ajouter la nouvelle contrainte avec tous les plans
ALTER TABLE users ADD CONSTRAINT users_subscription_plan_check 
CHECK (subscription_plan IN ('free', 'starter', 'professional', 'premium', 'enterprise'));

-- 3. Vérifier
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint 
WHERE conrelid = 'users'::regclass 
AND conname = 'users_subscription_plan_check';
