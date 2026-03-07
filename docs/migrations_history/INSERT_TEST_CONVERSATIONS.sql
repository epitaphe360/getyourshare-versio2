-- ========================================
-- CRÉER DES CONVERSATIONS DE TEST
-- ========================================

-- Insérer des conversations entre les premiers merchants et influencers
WITH merchant_influencer_pairs AS (
    SELECT 
        m.id as merchant_id,
        i.id as influencer_id,
        m.company_name,
        i.username as influencer_name,
        ROW_NUMBER() OVER () as rn
    FROM 
        (SELECT id, company_name FROM users WHERE role = 'merchant' LIMIT 5) m
    CROSS JOIN 
        (SELECT id, username FROM users WHERE role = 'influencer' LIMIT 4) i
    LIMIT 8
)
INSERT INTO conversations (
    merchant_id,
    influencer_id,
    last_message,
    last_message_at,
    unread_count_merchant,
    unread_count_influencer,
    status
)
SELECT 
    merchant_id,
    influencer_id,
    (CASE rn % 5
        WHEN 0 THEN 'Merci pour votre intérêt ! Je vous envoie les détails de la campagne.'
        WHEN 1 THEN 'Super ! Quand pouvez-vous commencer ?'
        WHEN 2 THEN 'Parfait, je valide votre participation.'
        WHEN 3 THEN 'Le paiement a été effectué. Merci pour votre travail !'
        ELSE 'Bonjour, j''aimerais collaborer avec vous sur une campagne.'
    END) as last_message,
    NOW() - ((rn * 3) || ' hours')::INTERVAL as last_message_at,
    (rn % 3) as unread_count_merchant,
    (CASE WHEN rn % 2 = 0 THEN 1 ELSE 0 END) as unread_count_influencer,
    'active' as status
FROM merchant_influencer_pairs;

-- Insérer des messages pour chaque conversation
WITH conversation_ids AS (
    SELECT 
        id as conversation_id,
        merchant_id,
        influencer_id,
        ROW_NUMBER() OVER (ORDER BY created_at) as conv_num
    FROM conversations
    LIMIT 8
)
INSERT INTO messages (conversation_id, sender_id, content, is_read, created_at)
SELECT 
    conversation_id,
    merchant_id as sender_id,
    'Bonjour, je suis intéressé par une collaboration. Pouvez-vous me parler de votre audience ?' as content,
    true as is_read,
    NOW() - ((conv_num * 5) || ' hours')::INTERVAL as created_at
FROM conversation_ids

UNION ALL

SELECT 
    conversation_id,
    influencer_id as sender_id,
    'Bonjour ! Mon audience est principalement composée de jeunes actifs intéressés par la mode et le lifestyle. J''ai environ 45K followers sur Instagram.' as content,
    true as is_read,
    NOW() - ((conv_num * 5 - 1) || ' hours')::INTERVAL as created_at
FROM conversation_ids

UNION ALL

SELECT 
    conversation_id,
    merchant_id as sender_id,
    'Parfait ! Je propose une commission de 12% sur chaque vente. Êtes-vous intéressé(e) ?' as content,
    (conv_num % 2 = 0) as is_read,
    NOW() - ((conv_num * 5 - 2) || ' hours')::INTERVAL as created_at
FROM conversation_ids

UNION ALL

SELECT 
    conversation_id,
    influencer_id as sender_id,
    'Oui, ça m''intéresse ! Pouvez-vous m''envoyer plus de détails sur les produits ?' as content,
    false as is_read,
    NOW() - ((conv_num * 5 - 3) || ' hours')::INTERVAL as created_at
FROM conversation_ids
WHERE conv_num <= 4;

-- Vérifier les résultats
SELECT 
    c.id,
    m.company_name as merchant,
    i.username as influencer,
    c.last_message,
    c.unread_count_merchant,
    c.unread_count_influencer,
    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
FROM conversations c
JOIN users m ON c.merchant_id = m.id
JOIN users i ON c.influencer_id = i.id
ORDER BY c.last_message_at DESC
LIMIT 10;

SELECT COUNT(*) as total_conversations FROM conversations;
SELECT COUNT(*) as total_messages FROM messages;
