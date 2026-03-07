-- PARTIE 2 : CORRECTION DES CONTRAINTES
-- Exécutez ce bloc en deuxième

-- 1. Supprimer la contrainte existante (si elle existe) pour éviter les conflits
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_subscription_tier_check;

-- 2. Normaliser les données (tout en minuscule)
UPDATE users SET subscription_tier = 'free' WHERE subscription_tier ILIKE 'free';
UPDATE users SET subscription_tier = 'pro' WHERE subscription_tier ILIKE 'pro';
UPDATE users SET subscription_tier = 'enterprise' WHERE subscription_tier ILIKE 'enterprise';

-- 3. Corriger les valeurs aberrantes (tout ce qui n'est pas free/pro/enterprise devient free)
UPDATE users 
SET subscription_tier = 'free' 
WHERE subscription_tier NOT IN ('free', 'pro', 'enterprise') 
   OR subscription_tier IS NULL;

-- 4. Ajouter la contrainte stricte (minuscules uniquement)
ALTER TABLE users ADD CONSTRAINT users_subscription_tier_check 
CHECK (subscription_tier IN ('free', 'pro', 'enterprise'));

-- 5. Même logique pour WORKSPACE_MEMBERS
ALTER TABLE workspace_members DROP CONSTRAINT IF EXISTS workspace_members_role_check;

UPDATE workspace_members SET role = 'admin' WHERE role ILIKE 'admin';
UPDATE workspace_members SET role = 'member' WHERE role ILIKE 'member';
UPDATE workspace_members SET role = 'viewer' WHERE role ILIKE 'viewer';
UPDATE workspace_members SET role = 'manager' WHERE role ILIKE 'manager';
UPDATE workspace_members SET role = 'editor' WHERE role ILIKE 'editor';

UPDATE workspace_members 
SET role = 'member' 
WHERE role NOT IN ('admin', 'member', 'viewer', 'manager', 'editor')
   OR role IS NULL;

ALTER TABLE workspace_members ADD CONSTRAINT workspace_members_role_check 
CHECK (role IN ('admin', 'member', 'viewer', 'manager', 'editor'));
