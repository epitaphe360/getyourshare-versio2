-- ========================================
-- METTRE À JOUR LES USERNAMES DES INFLUENCEURS
-- ========================================

-- Mettre à jour les usernames basés sur les emails
UPDATE users 
SET username = 'affiliate_user'
WHERE id = '0b9963d6-ded5-442b-bc80-217ecdb94cc8';

UPDATE users 
SET username = 'influencer_pro'
WHERE id = '2b706014-c3e1-4026-b38f-af779c4a8a73';

UPDATE users 
SET username = 'lucas_tech'
WHERE id = 'fd2e8ff0-8b0d-4295-a71b-531fc1a86ba7';

UPDATE users 
SET username = 'julie_beauty'
WHERE id = '6c35cb22-0a78-4921-8e1c-d3e979016544';

UPDATE users 
SET username = 'influencer_starter'
WHERE id = 'de768fff-1b5e-41ab-bb7e-08623c663a1d';

-- Vérifier les mises à jour
SELECT 
    id,
    username,
    email,
    role
FROM users
WHERE role = 'influencer'
ORDER BY username;
