-- Vérifier quels sont les influencer_id dans les conversations
SELECT DISTINCT 
    c.influencer_id,
    u.username,
    u.email,
    u.role
FROM conversations c
LEFT JOIN users u ON c.influencer_id = u.id
LIMIT 10;

-- Vérifier combien d'influencers existent
SELECT COUNT(*) as total_influencers 
FROM users 
WHERE role = 'influencer';

-- Afficher quelques influencers
SELECT id, username, email 
FROM users 
WHERE role = 'influencer' 
LIMIT 5;
