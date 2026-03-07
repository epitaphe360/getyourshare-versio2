-- ========================================
-- METTRE À JOUR LES USERNAMES RESTANTS
-- ========================================

-- Mettre à jour les 6 influenceurs restants
UPDATE users 
SET username = 'sarah_influencer'
WHERE id = 'ec1c27f6-51e0-402b-8ce4-e3586d7c20d6';

UPDATE users 
SET username = 'influencer_pro_demo'
WHERE id = '7d9e8452-a6e7-4b74-82d9-66d5ec932e19';

UPDATE users 
SET username = 'hassan_oudrhiri'
WHERE id = 'c7c9d24c-5bdf-4408-80d5-4876811f5fd8';

UPDATE users 
SET username = 'karim_benjelloun'
WHERE id = 'ce1760cf-5d03-42a1-8870-37ac4f2001d5';

UPDATE users 
SET username = 'emma_style'
WHERE id = 'b20faedb-02b9-4865-a28b-0155acc4d803';

UPDATE users 
SET username = 'sarah_benali'
WHERE id = '1d35776f-dc5f-49d3-a4e3-676c209c81ed';

-- Vérifier que TOUS les influenceurs ont maintenant un username
SELECT 
    COUNT(*) as total_influencers,
    COUNT(username) as with_username,
    COUNT(*) - COUNT(username) as missing_username
FROM users
WHERE role = 'influencer';

-- Afficher tous les influenceurs avec leurs usernames
SELECT 
    username,
    email,
    role
FROM users
WHERE role = 'influencer'
ORDER BY username;
