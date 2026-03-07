-- ========================================
-- VÉRIFIER L'ÉTAT ACTUEL DES CONVERSATIONS
-- ========================================

-- 1. Compter les conversations
SELECT COUNT(*) as total_conversations FROM conversations;

-- 2. Compter les messages
SELECT COUNT(*) as total_messages FROM messages;

-- 3. Voir les conversations avec détails
SELECT 
    c.id,
    c.merchant_id,
    c.influencer_id,
    m.company_name as merchant_name,
    m.email as merchant_email,
    i.username as influencer_name,
    i.email as influencer_email,
    c.last_message,
    c.last_message_at,
    c.unread_count_merchant,
    c.unread_count_influencer,
    c.status,
    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
FROM conversations c
LEFT JOIN users m ON c.merchant_id = m.id
LEFT JOIN users i ON c.influencer_id = i.id
ORDER BY c.last_message_at DESC;

-- 4. Voir quelques messages
SELECT 
    msg.id,
    msg.conversation_id,
    msg.sender_id,
    u.username as sender_name,
    u.role as sender_role,
    LEFT(msg.content, 50) as content_preview,
    msg.is_read,
    msg.created_at
FROM messages msg
LEFT JOIN users u ON msg.sender_id = u.id
ORDER BY msg.created_at DESC
LIMIT 20;

-- 5. Vérifier les politiques RLS sur conversations
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'conversations'
ORDER BY policyname;

-- 6. Vérifier les politiques RLS sur messages
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'messages'
ORDER BY policyname;
