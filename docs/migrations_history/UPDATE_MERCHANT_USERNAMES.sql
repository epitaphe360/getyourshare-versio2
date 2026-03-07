-- ========================================
-- METTRE À JOUR LES USERNAMES DES MERCHANTS
-- ========================================

-- Mettre à jour les merchants qui n'ont pas de username
-- Utiliser company_name comme base pour username avec un suffixe unique

UPDATE users 
SET username = LOWER(REPLACE(REPLACE(company_name, ' ', '_'), '-', '_')) || '_' || SUBSTRING(id::text, 1, 8)
WHERE role = 'merchant' 
AND (username IS NULL OR username = '');

-- Vérifier les merchants
SELECT 
    id,
    username,
    email,
    company_name,
    role
FROM users
WHERE role = 'merchant'
ORDER BY company_name
LIMIT 10;

-- Compter combien ont maintenant un username
SELECT 
    COUNT(*) as total_merchants,
    COUNT(username) as with_username,
    COUNT(*) - COUNT(username) as missing_username
FROM users
WHERE role = 'merchant';
