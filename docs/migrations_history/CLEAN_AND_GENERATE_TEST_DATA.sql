-- ============================================
-- NETTOYAGE PUIS GÃ‰NÃ‰RATION COMPLÃˆTE DES DONNÃ‰ES DE TEST
-- ============================================
-- Ce script nettoie d'abord les anciennes donnÃ©es puis insÃ¨re de nouvelles donnÃ©es de test

-- ============================================
-- Ã‰TAPE 1: NETTOYAGE DES DONNÃ‰ES EXISTANTES
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'ðŸ§¹ Nettoyage des donnÃ©es existantes...';
END $$;

-- Supprimer dans l'ordre inverse des dÃ©pendances (IMPORTANT: respecter les foreign keys)

-- 1. D'abord les commissions (qui dÃ©pendent de sales)
DELETE FROM commissions WHERE id::text LIKE 'com%';

-- 1b. Supprimer TOUTES les commissions liÃ©es aux sales des marchands de test
DELETE FROM commissions WHERE sale_id IN (
    SELECT id FROM sales WHERE merchant_id IN (
        '11111111-1111-1111-1111-111111111111',
        '22222222-2222-2222-2222-222222222222',
        '22222222-2222-2222-2222-222222222223',
        '22222222-2222-2222-2222-222222222224',
        '22222222-2222-2222-2222-222222222225',
        '22222222-2222-2222-2222-222222222226',
        '55555555-5555-5555-5555-555555555551'
    )
);

-- 1b. Supprimer TOUTES les commissions des influenceurs de test
DELETE FROM commissions WHERE influencer_id IN (
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 2. Ensuite les sales (maintenant qu'aucune commission ne les rÃ©fÃ©rence)
DELETE FROM sales WHERE id::text LIKE 'sale%';

-- 2b. Supprimer TOUTES les sales des marchands de test
DELETE FROM sales WHERE merchant_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551'
);

-- 2c. Supprimer TOUTES les sales des influenceurs de test
DELETE FROM sales WHERE influencer_id IN (
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 3. Supprimer les invitations et collaboration_requests (qui dÃ©pendent de campaigns)
DELETE FROM invitations WHERE campaign_id IN (SELECT id FROM campaigns WHERE id::text LIKE 'c%');
DELETE FROM collaboration_requests WHERE campaign_id IN (SELECT id FROM campaigns WHERE id::text LIKE 'c%');

-- 3b. Supprimer les demandes d'affiliation des marchands de test
DELETE FROM affiliation_requests WHERE merchant_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551'
);

-- 3c. Supprimer les demandes d'affiliation des influenceurs de test
DELETE FROM affiliation_requests WHERE influencer_id IN (
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 4. Les autres tables sans dÃ©pendances critiques
DELETE FROM products WHERE id::text LIKE 'p%';
DELETE FROM campaigns WHERE id::text LIKE 'c%';

-- 5. Supprimer les conversions des utilisateurs de test (marchands)
DELETE FROM conversions WHERE merchant_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551'
);

-- 6. Supprimer TOUTES les invoices des utilisateurs de test (pas seulement celles avec 'i00%')
DELETE FROM invoices WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 6. Supprimer les subscriptions (qui dÃ©pendent de users)
DELETE FROM subscriptions WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 7. Supprimer TOUS les leads des commerciaux de test (par commercial_id, pas seulement ceux avec 'lead%')
DELETE FROM leads WHERE commercial_id IN (
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446'
);

-- 8. Supprimer les messages envoyés par les utilisateurs de test
DELETE FROM messages WHERE sender_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 9. Supprimer les notifications des utilisateurs de test
DELETE FROM notifications WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 10. Supprimer les données de gamification des utilisateurs de test
DELETE FROM user_gamification WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 11. Supprimer les profils KYC des utilisateurs de test
DELETE FROM user_kyc_profile WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 12. Supprimer les scores de confiance des utilisateurs de test
DELETE FROM trust_scores WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 13. Supprimer les dÃ©pÃ´ts des marchands de test
DELETE FROM merchant_deposits WHERE merchant_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551'
);

-- 14. Supprimer les transactions de dÃ©pÃ´t des marchands de test
DELETE FROM deposit_transactions WHERE merchant_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551'
);

-- 15. Supprimer les missions des utilisateurs de test
DELETE FROM user_missions WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 16. Supprimer les transactions gateway des utilisateurs de test
DELETE FROM gateway_transactions WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 17. Supprimer les reviews des utilisateurs de test
DELETE FROM reviews WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 18. Supprimer les product_reviews des utilisateurs de test
DELETE FROM product_reviews WHERE user_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 18b. Supprimer les stats réseaux sociaux des influenceurs de test
DELETE FROM social_media_stats WHERE connection_id IN (
    SELECT id FROM social_connections WHERE influencer_id IN (
        '33333333-3333-3333-3333-333333333333',
        '33333333-3333-3333-3333-333333333334',
        '33333333-3333-3333-3333-333333333335',
        '33333333-3333-3333-3333-333333333336',
        '33333333-3333-3333-3333-333333333337',
        '66666666-6666-6666-6666-666666666661',
        '77777777-7777-7777-7777-777777777771'
    )
);

-- 18c. Supprimer les connexions sociales des influenceurs de test
DELETE FROM social_connections WHERE influencer_id IN (
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 19. Supprimer les utilisateurs de test (garder ceux des conversations existantes si nÃ©cessaire)
DELETE FROM users WHERE id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222223',
    '22222222-2222-2222-2222-222222222224',
    '22222222-2222-2222-2222-222222222225',
    '22222222-2222-2222-2222-222222222226',
    '55555555-5555-5555-5555-555555555551',
    '44444444-4444-4444-4444-444444444441',
    '44444444-4444-4444-4444-444444444442',
    '44444444-4444-4444-4444-444444444443',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- Mettre Ã  jour les utilisateurs existants (ceux des conversations)
-- UPDATE users 
-- SET 
--     password_hash = '$2b$10$dummyhash',
--     is_active = true,
--     is_verified = true
-- WHERE id IN (
--     '33333333-3333-3333-3333-333333333333',
--     '33333333-3333-3333-3333-333333333334',
--     '33333333-3333-3333-3333-333333333335',
--     '33333333-3333-3333-3333-333333333336',
--     '33333333-3333-3333-3333-333333333337',
--     '66666666-6666-6666-6666-666666666661',
--     '77777777-7777-7777-7777-777777777771'
-- );

DO $$
BEGIN
    RAISE NOTICE 'âœ… Nettoyage terminÃ©';
    RAISE NOTICE '';
    RAISE NOTICE 'ðŸ“Š Insertion des nouvelles donnÃ©es...';
END $$;

-- ============================================
-- Ã‰TAPE 2: INSERTION DES NOUVELLES DONNÃ‰ES
-- ============================================

-- 1. ADMIN + MERCHANTS + COMMERCIAUX
INSERT INTO users (id, email, password_hash, role, full_name, company_name, subscription_plan, is_active, is_verified, avatar_url, monthly_budget, created_at)
VALUES 
-- Admin
('11111111-1111-1111-1111-111111111111', 'admin@shareyoursales.ma', '$2b$10$dummyhash', 'admin', 'Admin SYS', 'ShareYourSales Admin', 'Enterprise', true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin', NULL, NOW()),

-- Merchants FREE
('22222222-2222-2222-2222-222222222222', 'merchant1@example.com', '$2b$10$dummyhash', 'merchant', 'Tech Manager', 'TechStyle Morocco', 'Free', true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant1', 0, NOW() - INTERVAL '30 days'),
('22222222-2222-2222-2222-222222222223', 'merchant2@example.com', '$2b$10$dummyhash', 'merchant', 'Beauty Owner', 'BeautyBox Casablanca', 'Free', true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant2', 0, NOW() - INTERVAL '25 days'),

-- Merchants PRO
('22222222-2222-2222-2222-222222222224', 'merchant3@example.com', '$2b$10$dummyhash', 'merchant', 'Fashion Director', 'FashionHub Marrakech', 'Pro', true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant3', 10000, NOW() - INTERVAL '20 days'),
('22222222-2222-2222-2222-222222222225', 'merchant4@example.com', '$2b$10$dummyhash', 'merchant', 'Electro CEO', 'ElectroShop Rabat', 'Pro', true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant4', 12000, NOW() - INTERVAL '15 days'),
('55555555-5555-5555-5555-555555555551', 'merchant6@example.com', '$2b$10$dummyhash', 'merchant', 'Sport Manager', 'SportGear Fes', 'Pro', true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=sport', 8000, NOW() - INTERVAL '12 days'),

-- Merchant ENTERPRISE
('22222222-2222-2222-2222-222222222226', 'merchant5@example.com', '$2b$10$dummyhash', 'merchant', 'Mega Manager', 'MegaStore Tanger', 'Enterprise', true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=merchant5', 25000, NOW() - INTERVAL '10 days'),

-- Commerciaux
('44444444-4444-4444-4444-444444444441', 'commercial1@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Karim Sales', 'ShareYourSales', NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=com1', NULL, NOW() - INTERVAL '60 days'),
('44444444-4444-4444-4444-444444444442', 'commercial2@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Laila Growth', 'ShareYourSales', NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=com2', NULL, NOW() - INTERVAL '55 days'),
('44444444-4444-4444-4444-444444444443', 'commercial3@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Omar Business', 'ShareYourSales', NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=com3', NULL, NOW() - INTERVAL '50 days'),
('44444444-4444-4444-4444-444444444444', 'commercial4@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Amina Dev', 'ShareYourSales', NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=com4', NULL, NOW() - INTERVAL '45 days'),
('44444444-4444-4444-4444-444444444445', 'commercial5@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Rachid Pro', 'ShareYourSales', NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=com5', NULL, NOW() - INTERVAL '40 days'),
('44444444-4444-4444-4444-444444444446', 'commercial6@shareyoursales.ma', '$2b$10$dummyhash', 'commercial', 'Sophia Elite', 'ShareYourSales', NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=com6', NULL, NOW() - INTERVAL '35 days'),

-- Influencers
('33333333-3333-3333-3333-333333333333', 'influencer1@shareyoursales.ma', '$2b$10$dummyhash', 'influencer', 'Sarah Lifestyle', NULL, NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=inf1', NULL, NOW() - INTERVAL '60 days'),
('33333333-3333-3333-3333-333333333334', 'influencer2@shareyoursales.ma', '$2b$10$dummyhash', 'influencer', 'Ahmed Tech Reviews', NULL, NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=inf2', NULL, NOW() - INTERVAL '60 days'),
('33333333-3333-3333-3333-333333333335', 'influencer3@shareyoursales.ma', '$2b$10$dummyhash', 'influencer', 'Fatima Beauty', NULL, NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=inf3', NULL, NOW() - INTERVAL '60 days'),
('33333333-3333-3333-3333-333333333336', 'influencer4@shareyoursales.ma', '$2b$10$dummyhash', 'influencer', 'Youssef Fashion', NULL, NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=inf4', NULL, NOW() - INTERVAL '60 days'),
('33333333-3333-3333-3333-333333333337', 'influencer5@shareyoursales.ma', '$2b$10$dummyhash', 'influencer', 'Nadia Travel', NULL, NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=inf5', NULL, NOW() - INTERVAL '60 days'),
('66666666-6666-6666-6666-666666666661', 'influencer6@shareyoursales.ma', '$2b$10$dummyhash', 'influencer', 'Karim Fitness', NULL, NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=inf6', NULL, NOW() - INTERVAL '60 days'),
('77777777-7777-7777-7777-777777777771', 'influencer7@shareyoursales.ma', '$2b$10$dummyhash', 'influencer', 'Leila Food', NULL, NULL, true, true, 'https://api.dicebear.com/7.x/avataaars/svg?seed=inf7', NULL, NOW() - INTERVAL '60 days');

-- 2. Mettre Ã  jour les INFLUENCERS existants
UPDATE users 
SET 
    password_hash = '$2b$10$dummyhash',
    full_name = CASE id
        WHEN '33333333-3333-3333-3333-333333333333' THEN 'Sarah Lifestyle'
        WHEN '33333333-3333-3333-3333-333333333334' THEN 'Ahmed Tech Reviews'
        WHEN '33333333-3333-3333-3333-333333333335' THEN 'Fatima Beauty'
        WHEN '33333333-3333-3333-3333-333333333336' THEN 'Youssef Fashion'
        WHEN '33333333-3333-3333-3333-333333333337' THEN 'Nadia Travel'
        WHEN '66666666-6666-6666-6666-666666666661' THEN 'Karim Fitness'
        WHEN '77777777-7777-7777-7777-777777777771' THEN 'Leila Food'
    END,
    instagram_handle = CASE id
        WHEN '33333333-3333-3333-3333-333333333333' THEN '@sarah_lifestyle'
        WHEN '33333333-3333-3333-3333-333333333334' THEN '@ahmed_tech'
        WHEN '33333333-3333-3333-3333-333333333335' THEN '@fatima_beauty'
        WHEN '33333333-3333-3333-3333-333333333336' THEN '@youssef_fashion'
        WHEN '33333333-3333-3333-3333-333333333337' THEN '@nadia_travel'
        WHEN '66666666-6666-6666-6666-666666666661' THEN '@karim_fit'
        WHEN '77777777-7777-7777-7777-777777777771' THEN '@leila_food'
    END,
    followers_count = CASE id
        WHEN '33333333-3333-3333-3333-333333333333' THEN 45000
        WHEN '33333333-3333-3333-3333-333333333334' THEN 78000
        WHEN '33333333-3333-3333-3333-333333333335' THEN 62000
        WHEN '33333333-3333-3333-3333-333333333336' THEN 95000
        WHEN '33333333-3333-3333-3333-333333333337' THEN 120000
        WHEN '66666666-6666-6666-6666-666666666661' THEN 88000
        WHEN '77777777-7777-7777-7777-777777777771' THEN 105000
    END,
    engagement_rate = CASE id
        WHEN '33333333-3333-3333-3333-333333333333' THEN 8.5
        WHEN '33333333-3333-3333-3333-333333333334' THEN 6.2
        WHEN '33333333-3333-3333-3333-333333333335' THEN 9.1
        WHEN '33333333-3333-3333-3333-333333333336' THEN 7.8
        WHEN '33333333-3333-3333-3333-333333333337' THEN 10.2
        WHEN '66666666-6666-6666-6666-666666666661' THEN 7.5
        WHEN '77777777-7777-7777-7777-777777777771' THEN 8.9
    END,
    is_active = true,
    is_verified = true
WHERE id IN (
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335',
    '33333333-3333-3333-3333-333333333336',
    '33333333-3333-3333-3333-333333333337',
    '66666666-6666-6666-6666-666666666661',
    '77777777-7777-7777-7777-777777777771'
);

-- 3. CAMPAIGNS (15)
INSERT INTO campaigns (id, merchant_id, name, description, budget, commission_rate, start_date, end_date, status, created_at)
VALUES
('c1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Campagne Ã‰tÃ© 2024', 'Promotion vÃªtements d''Ã©tÃ©', 5000.00, 10.0, NOW() - INTERVAL '20 days', NOW() + INTERVAL '10 days', 'active', NOW() - INTERVAL '20 days'),
('c1111111-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222222', 'Black Friday Tech', 'Soldes accessoires tech', 3000.00, 12.0, NOW() - INTERVAL '5 days', NOW() + INTERVAL '25 days', 'active', NOW() - INTERVAL '5 days'),
('c2222222-2222-2222-2222-222222222221', '22222222-2222-2222-2222-222222222223', 'BeautÃ© Printemps', 'Nouveaux produits cosmÃ©tiques', 4000.00, 15.0, NOW() - INTERVAL '15 days', NOW() + INTERVAL '15 days', 'active', NOW() - INTERVAL '15 days'),
('c3333333-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222224', 'Fashion Week', 'Collection automne-hiver', 10000.00, 18.0, NOW() - INTERVAL '25 days', NOW() + INTERVAL '5 days', 'active', NOW() - INTERVAL '25 days'),
('c3333333-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222224', 'Promo Accessoires', 'Sacs et chaussures', 6000.00, 14.0, NOW() - INTERVAL '10 days', NOW() + INTERVAL '20 days', 'active', NOW() - INTERVAL '10 days'),
('c3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222224', 'Soldes Fin Saison', 'DÃ©stockage -50%', 8000.00, 20.0, NOW() + INTERVAL '5 days', NOW() + INTERVAL '35 days', 'draft', NOW() - INTERVAL '2 days'),
('c4444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222225', 'Ã‰lectro Deals', 'High-tech Ã  prix cassÃ©s', 12000.00, 16.0, NOW() - INTERVAL '18 days', NOW() + INTERVAL '12 days', 'active', NOW() - INTERVAL '18 days'),
('c4444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222225', 'Gaming Week', 'Consoles et jeux', 9000.00, 13.0, NOW() - INTERVAL '8 days', NOW() + INTERVAL '22 days', 'active', NOW() - INTERVAL '8 days'),
('c5555555-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226', 'Mega Promo Hiver', 'Toutes catÃ©gories -30%', 25000.00, 22.0, NOW() - INTERVAL '30 days', NOW() + INTERVAL '30 days', 'active', NOW() - INTERVAL '30 days'),
('c5555555-5555-5555-5555-555555555552', '22222222-2222-2222-2222-222222222226', 'Ã‰lectromÃ©nager Premium', 'Grandes marques', 18000.00, 17.0, NOW() - INTERVAL '12 days', NOW() + INTERVAL '18 days', 'active', NOW() - INTERVAL '12 days'),
('c5555555-5555-5555-5555-555555555553', '22222222-2222-2222-2222-222222222226', 'Mode Luxe', 'VÃªtements haut de gamme', 15000.00, 25.0, NOW() - INTERVAL '6 days', NOW() + INTERVAL '24 days', 'active', NOW() - INTERVAL '6 days'),
('c5555555-5555-5555-5555-555555555554', '22222222-2222-2222-2222-222222222226', 'Sport & Fitness', 'Ã‰quipement sportif', 10000.00, 19.0, NOW() + INTERVAL '10 days', NOW() + INTERVAL '40 days', 'draft', NOW() - INTERVAL '1 day'),
('c6666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555551', 'Running Essentials', 'Chaussures et vÃªtements course', 7000.00, 15.0, NOW() - INTERVAL '14 days', NOW() + INTERVAL '16 days', 'active', NOW() - INTERVAL '14 days'),
('c6666666-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551', 'Yoga & Pilates', 'Ã‰quipement wellness', 5500.00, 18.0, NOW() - INTERVAL '7 days', NOW() + INTERVAL '23 days', 'active', NOW() - INTERVAL '7 days'),
('c7777777-7777-7777-7777-777777777771', '22222222-2222-2222-2222-222222222224', 'Promo RentrÃ©e 2024', 'Back to school', 5000.00, 12.0, NOW() - INTERVAL '60 days', NOW() - INTERVAL '30 days', 'completed', NOW() - INTERVAL '60 days');

-- 4. PRODUCTS (30)
INSERT INTO products (id, merchant_id, name, description, price, commission_rate, image_url, category, is_active, created_at)
VALUES
-- Merchant 1 (3 produits)
('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'T-Shirt Premium Cotton', 'T-shirt 100% coton biologique', 250.00, 10.0, 'https://picsum.photos/seed/tshirt1/400/400', 'Fashion', true, NOW() - INTERVAL '20 days'),
('11111111-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222222', 'Jean Slim Fit', 'Jean denim stretch confortable', 450.00, 10.0, 'https://picsum.photos/seed/jean1/400/400', 'Fashion', true, NOW() - INTERVAL '18 days'),
('11111111-1111-1111-1111-111111111113', '22222222-2222-2222-2222-222222222222', 'Casque Bluetooth', 'Audio sans fil haute qualitÃ©', 850.00, 12.0, 'https://picsum.photos/seed/headphone1/400/400', 'Electronics', true, NOW() - INTERVAL '5 days'),

-- Merchant 2 (3 produits)
('22222222-2222-2222-2222-222222222221', '22222222-2222-2222-2222-222222222223', 'SÃ©rum Visage Anti-Ã¢ge', 'Formule enrichie vitamine C', 380.00, 15.0, 'https://picsum.photos/seed/serum1/400/400', 'Beauty', true, NOW() - INTERVAL '15 days'),
('22222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222223', 'Palette Maquillage', '12 couleurs nude', 320.00, 15.0, 'https://picsum.photos/seed/palette1/400/400', 'Beauty', true, NOW() - INTERVAL '14 days'),
('22222222-2222-2222-2222-222222222223', '22222222-2222-2222-2222-222222222223', 'CrÃ¨me Hydratante Bio', 'Peaux sensibles certifiÃ©e bio', 280.00, 15.0, 'https://picsum.photos/seed/cream1/400/400', 'Beauty', true, NOW() - INTERVAL '12 days'),

-- Merchant 3 (4 produits)
('33333333-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222224', 'Robe Cocktail Ã‰lÃ©gante', 'Parfaite pour soirÃ©es', 1200.00, 18.0, 'https://picsum.photos/seed/dress1/400/400', 'Fashion', true, NOW() - INTERVAL '25 days'),
('33333333-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222224', 'Sac Ã  Main Cuir', 'Cuir vÃ©ritable italien', 1500.00, 18.0, 'https://picsum.photos/seed/bag1/400/400', 'Fashion', true, NOW() - INTERVAL '23 days'),
('33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222224', 'Escarpins Talons Hauts', 'Confort et Ã©lÃ©gance', 950.00, 18.0, 'https://picsum.photos/seed/shoes1/400/400', 'Fashion', true, NOW() - INTERVAL '20 days'),
('33333333-3333-3333-3333-333333333334', '22222222-2222-2222-2222-222222222224', 'Veste Blazer Femme', 'Coupe moderne professionnelle', 1800.00, 14.0, 'https://picsum.photos/seed/blazer1/400/400', 'Fashion', true, NOW() - INTERVAL '10 days'),

-- Merchant 4 (5 produits)
('44444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222225', 'Smartphone 5G Pro', 'DerniÃ¨re gÃ©nÃ©ration', 5500.00, 16.0, 'https://picsum.photos/seed/phone1/400/400', 'Electronics', true, NOW() - INTERVAL '18 days'),
('44444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222225', 'Laptop Gaming RGB', '16GB RAM, RTX Graphics', 12000.00, 16.0, 'https://picsum.photos/seed/laptop1/400/400', 'Electronics', true, NOW() - INTERVAL '17 days'),
('44444444-4444-4444-4444-444444444443', '22222222-2222-2222-2222-222222222225', 'Tablette 10 pouces', 'Ã‰cran AMOLED', 3200.00, 16.0, 'https://picsum.photos/seed/tablet1/400/400', 'Electronics', true, NOW() - INTERVAL '15 days'),
('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222225', 'Console Gaming Pro', 'DerniÃ¨re gÃ©nÃ©ration', 4500.00, 13.0, 'https://picsum.photos/seed/console1/400/400', 'Electronics', true, NOW() - INTERVAL '8 days'),
('44444444-4444-4444-4444-444444444445', '22222222-2222-2222-2222-222222222225', 'Montre ConnectÃ©e Sport', 'GPS, cardio, waterproof', 2200.00, 13.0, 'https://picsum.photos/seed/watch1/400/400', 'Electronics', true, NOW() - INTERVAL '7 days'),

-- Merchant 5 (6 produits)
('55555555-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226', 'RÃ©frigÃ©rateur Premium', 'Double porte, No Frost', 8500.00, 22.0, 'https://picsum.photos/seed/fridge1/400/400', 'Home', true, NOW() - INTERVAL '30 days'),
('55555555-5555-5555-5555-555555555552', '22222222-2222-2222-2222-222222222226', 'Machine Ã  Laver 10kg', 'Classe A+++', 6200.00, 22.0, 'https://picsum.photos/seed/washing1/400/400', 'Home', true, NOW() - INTERVAL '28 days'),
('55555555-5555-5555-5555-555555555553', '22222222-2222-2222-2222-222222222226', 'TV 4K 55 pouces', 'Smart TV OLED', 9800.00, 17.0, 'https://picsum.photos/seed/tv1/400/400', 'Electronics', true, NOW() - INTERVAL '12 days'),
('55555555-5555-5555-5555-555555555554', '22222222-2222-2222-2222-222222222226', 'Aspirateur Robot', 'Navigation intelligente', 3500.00, 17.0, 'https://picsum.photos/seed/vacuum1/400/400', 'Home', true, NOW() - INTERVAL '11 days'),
('55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222226', 'Costume Homme Luxe', 'Laine italienne premium', 5500.00, 25.0, 'https://picsum.photos/seed/suit1/400/400', 'Fashion', true, NOW() - INTERVAL '6 days'),
('55555555-5555-5555-5555-555555555556', '22222222-2222-2222-2222-222222222226', 'Chaussures Cuir Luxe', 'Fait main artisanal', 3200.00, 25.0, 'https://picsum.photos/seed/leather1/400/400', 'Fashion', true, NOW() - INTERVAL '5 days'),

-- Merchant 6 (4 produits)
('66666666-6666-6666-6666-666666666661', '55555555-5555-5555-5555-555555555551', 'Chaussures Running Pro', 'Amorti maximal', 1200.00, 15.0, 'https://picsum.photos/seed/running1/400/400', 'Sports', true, NOW() - INTERVAL '14 days'),
('66666666-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551', 'Tapis Yoga Premium', 'AntidÃ©rapant Ã©cologique', 450.00, 18.0, 'https://picsum.photos/seed/yoga1/400/400', 'Sports', true, NOW() - INTERVAL '13 days'),
('66666666-6666-6666-6666-666666666663', '55555555-5555-5555-5555-555555555551', 'HaltÃ¨res RÃ©glables', 'De 5 Ã  25kg', 1800.00, 15.0, 'https://picsum.photos/seed/weights1/400/400', 'Sports', true, NOW() - INTERVAL '12 days'),
('66666666-6666-6666-6666-666666666664', '55555555-5555-5555-5555-555555555551', 'Montre GPS Running', 'Autonomie 20h', 2500.00, 18.0, 'https://picsum.photos/seed/gpswatch1/400/400', 'Sports', true, NOW() - INTERVAL '7 days'),

-- Produits variÃ©s (5 produits)
('77777777-7777-7777-7777-777777777771', '22222222-2222-2222-2222-222222222224', 'Lunettes de Soleil Ray', 'Protection UV 100%', 680.00, 14.0, 'https://picsum.photos/seed/sunglasses1/400/400', 'Fashion', true, NOW() - INTERVAL '10 days'),
('88888888-8888-8888-8888-888888888881', '22222222-2222-2222-2222-222222222225', 'Ã‰couteurs True Wireless', 'RÃ©duction bruit active', 1500.00, 16.0, 'https://picsum.photos/seed/earbuds1/400/400', 'Electronics', true, NOW() - INTERVAL '9 days'),
('99999999-9999-9999-9999-999999999991', '22222222-2222-2222-2222-222222222223', 'Parfum Femme Luxe 50ml', 'Notes florales orientales', 950.00, 15.0, 'https://picsum.photos/seed/perfume1/400/400', 'Beauty', true, NOW() - INTERVAL '8 days'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222226', 'Four Micro-ondes', 'Grill multifonction', 1800.00, 17.0, 'https://picsum.photos/seed/microwave1/400/400', 'Home', true, NOW() - INTERVAL '4 days');

-- 5. SALES puis COMMISSIONS (CrÃ©er des sales d'abord pour avoir les sale_id)
-- InsÃ©rer quelques sales d'abord
INSERT INTO sales (id, merchant_id, influencer_id, product_id, amount, commission_amount, platform_commission, status, sale_timestamp, created_at)
VALUES
('aaaa1111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 250.00, 25.00, 2.50, 'completed', NOW() - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('aaaa2222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333332', 1500.00, 270.00, 15.00, 'completed', NOW() - INTERVAL '16 days', NOW() - INTERVAL '16 days'),
('aaaa3333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222225', '33333333-3333-3333-3333-333333333334', '44444444-4444-4444-4444-444444444441', 5500.00, 880.00, 55.00, 'completed', NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days');

-- Maintenant insÃ©rer les commissions (version simplifiÃ©e - 20 commissions au lieu de 40)
INSERT INTO commissions (id, influencer_id, sale_id, amount, status, payout_date, created_at)
VALUES
-- Influencer 1 (Sarah) - 5 commissions
('bbb11111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'aaaa1111-1111-1111-1111-111111111111', 125.00, 'paid', NOW() - INTERVAL '10 days', NOW() - INTERVAL '18 days'),
('bbb11111-1111-1111-1111-111111111112', '33333333-3333-3333-3333-333333333333', 'aaaa2222-2222-2222-2222-222222222222', 270.00, 'paid', NOW() - INTERVAL '8 days', NOW() - INTERVAL '16 days'),
('bbb11111-1111-1111-1111-111111111113', '33333333-3333-3333-3333-333333333333', NULL, 450.00, 'pending', NULL, NOW() - INTERVAL '5 days'),
('bbb11111-1111-1111-1111-111111111114', '33333333-3333-3333-3333-333333333333', NULL, 165.00, 'paid', NOW() - INTERVAL '6 days', NOW() - INTERVAL '12 days'),
('bbb11111-1111-1111-1111-111111111115', '33333333-3333-3333-3333-333333333333', NULL, 850.00, 'pending', NULL, NOW() - INTERVAL '3 days'),

-- Influencer 2 (Ahmed) - 5 commissions
('bbb22222-2222-2222-2222-222222222221', '33333333-3333-3333-3333-333333333334', 'aaaa3333-3333-3333-3333-333333333333', 320.00, 'paid', NOW() - INTERVAL '7 days', NOW() - INTERVAL '15 days'),
('bbb22222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333334', NULL, 180.00, 'paid', NOW() - INTERVAL '9 days', NOW() - INTERVAL '14 days'),
('bbb22222-2222-2222-2222-222222222223', '33333333-3333-3333-3333-333333333334', NULL, 560.00, 'approved', NULL, NOW() - INTERVAL '6 days'),
('bbb22222-2222-2222-2222-222222222224', '33333333-3333-3333-3333-333333333334', NULL, 95.00, 'paid', NOW() - INTERVAL '5 days', NOW() - INTERVAL '11 days'),
('bbb22222-2222-2222-2222-222222222225', '33333333-3333-3333-3333-333333333334', NULL, 215.00, 'approved', NULL, NOW() - INTERVAL '10 days'),

-- Autres influencers (10 commissions variÃ©es)
('bbb33333-3333-3333-3333-333333333331', '33333333-3333-3333-3333-333333333335', NULL, 195.00, 'paid', NOW() - INTERVAL '12 days', NOW() - INTERVAL '17 days'),
('bbb33333-3333-3333-3333-333333333332', '33333333-3333-3333-3333-333333333335', NULL, 760.00, 'paid', NOW() - INTERVAL '8 days', NOW() - INTERVAL '13 days'),
('bbb44444-4444-4444-4444-444444444441', '33333333-3333-3333-3333-333333333336', NULL, 520.00, 'paid', NOW() - INTERVAL '14 days', NOW() - INTERVAL '19 days'),
('bbb44444-4444-4444-4444-444444444442', '33333333-3333-3333-3333-333333333336', NULL, 375.00, 'approved', NULL, NOW() - INTERVAL '16 days'),
('bbb55555-5555-5555-5555-555555555551', '33333333-3333-3333-3333-333333333337', NULL, 1250.00, 'paid', NOW() - INTERVAL '15 days', NOW() - INTERVAL '20 days'),
('bbb55555-5555-5555-5555-555555555552', '33333333-3333-3333-3333-333333333337', NULL, 680.00, 'paid', NOW() - INTERVAL '11 days', NOW() - INTERVAL '17 days'),
('bbb66666-6666-6666-6666-666666666661', '66666666-6666-6666-6666-666666666661', NULL, 340.00, 'approved', NULL, NOW() - INTERVAL '18 days'),
('bbb66666-6666-6666-6666-666666666662', '66666666-6666-6666-6666-666666666661', NULL, 580.00, 'paid', NOW() - INTERVAL '10 days', NOW() - INTERVAL '15 days'),
('bbb77777-7777-7777-7777-777777777771', '77777777-7777-7777-7777-777777777771', NULL, 485.00, 'paid', NOW() - INTERVAL '9 days', NOW() - INTERVAL '16 days'),
('bbb77777-7777-7777-7777-777777777772', '77777777-7777-7777-7777-777777777771', NULL, 275.00, 'approved', NULL, NOW() - INTERVAL '12 days');

-- 6. LEADS (20 leads)
INSERT INTO leads (id, commercial_id, merchant_id, customer_name, customer_email, customer_phone, status, lead_status, score, source, notes, created_at)
VALUES
-- Commercial 1 - 4 leads
('cccc1111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222222', 'TechStyle Morocco', 'contact@techstyle.ma', '+212 6 12 34 56 78', 'validated', 'converted', 95, 'Referral', 'Client converti en PRO', NOW() - INTERVAL '30 days'),
('cccc1111-1111-1111-1111-111111111112', '44444444-4444-4444-4444-444444444441', NULL, 'Fashion Trends', 'info@fashiontrends.ma', '+212 6 23 45 67 89', 'pending', 'qualified', 80, 'LinkedIn', 'TrÃ¨s intÃ©ressÃ© par offre PRO', NOW() - INTERVAL '10 days'),
('cccc1111-1111-1111-1111-111111111113', '44444444-4444-4444-4444-444444444441', NULL, 'Beauty Express', 'hello@beautyexpress.ma', '+212 6 34 56 78 90', 'pending', 'contacted', 65, 'Website', 'Premier contact effectuÃ©', NOW() - INTERVAL '5 days'),
('cccc1111-1111-1111-1111-111111111114', '44444444-4444-4444-4444-444444444441', NULL, 'Electro Plus', 'contact@electroplus.ma', '+212 6 45 67 89 01', 'pending', 'new', 50, 'LinkedIn', 'Prospect dÃ©couvert via LinkedIn', NOW() - INTERVAL '2 days'),

-- Commercial 2 - 4 leads
('cccc2222-2222-2222-2222-222222222221', '44444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222224', 'FashionHub Marrakech', 'info@fashionhub.ma', '+212 6 56 78 90 12', 'validated', 'converted', 98, 'Referral', 'Converti en ENTERPRISE', NOW() - INTERVAL '25 days'),
('cccc2222-2222-2222-2222-222222222222', '44444444-4444-4444-4444-444444444442', NULL, 'Mega Deals', 'sales@megadeals.ma', '+212 6 67 89 01 23', 'pending', 'qualified', 85, 'Cold Call', 'Budget confirmÃ© 15000 DH/mois', NOW() - INTERVAL '12 days'),
('cccc2222-2222-2222-2222-222222222223', '44444444-4444-4444-4444-444444444442', NULL, 'Sport Zone', 'contact@sportzone.ma', '+212 6 78 90 12 34', 'pending', 'contacted', 70, 'Website', 'RDV prÃ©vu semaine prochaine', NOW() - INTERVAL '7 days'),
('cccc2222-2222-2222-2222-222222222224', '44444444-4444-4444-4444-444444444442', NULL, 'Home Decor Pro', 'info@homedecorpro.ma', '+212 6 89 01 23 45', 'rejected', 'lost', 40, 'Website', 'Prix trop Ã©levÃ© pour eux', NOW() - INTERVAL '15 days'),

-- Autres commerciaux (12 leads supplÃ©mentaires - pattern similaire)
('cccc3333-3333-3333-3333-333333333331', '44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555551', 'SportGear Fes', 'hello@sportgear.ma', '+212 6 90 12 34 56', 'validated', 'converted', 92, 'Referral', 'Inscrit formule PRO', NOW() - INTERVAL '20 days'),
('cccc3333-3333-3333-3333-333333333332', '44444444-4444-4444-4444-444444444443', NULL, 'Gadget Store', 'contact@gadgetstore.ma', '+212 6 01 23 45 67', 'pending', 'qualified', 78, 'LinkedIn', 'IntÃ©ressÃ© par ENTERPRISE', NOW() - INTERVAL '8 days'),
('cccc4444-4444-4444-4444-444444444441', '44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222226', 'MegaStore Tanger', 'pro@megastore.ma', '+212 6 23 45 67 89', 'validated', 'converted', 96, 'Cold Call', 'Upgrade vers ENTERPRISE', NOW() - INTERVAL '35 days'),
('cccc4444-4444-4444-4444-444444444442', '44444444-4444-4444-4444-444444444444', NULL, 'Kids Fashion', 'contact@kidsfashion.ma', '+212 6 34 56 78 90', 'pending', 'qualified', 82, 'Website', 'Budget 8000 DH confirmÃ©', NOW() - INTERVAL '14 days'),
('cccc5555-5555-5555-5555-555555555551', '44444444-4444-4444-4444-444444444445', NULL, 'Book Store Online', 'hello@bookstore.ma', '+212 6 56 78 90 12', 'pending', 'qualified', 75, 'LinkedIn', 'Cherche solution marketing', NOW() - INTERVAL '11 days'),
('cccc5555-5555-5555-5555-555555555552', '44444444-4444-4444-4444-444444444445', NULL, 'Pet Shop Morocco', 'info@petshop.ma', '+212 6 67 89 01 23', 'pending', 'contacted', 68, 'Website', 'Email envoyÃ©, en attente retour', NOW() - INTERVAL '9 days'),
('cccc6666-6666-6666-6666-666666666661', '44444444-4444-4444-4444-444444444446', NULL, 'Auto Parts Shop', 'sales@autoparts.ma', '+212 6 89 01 23 45', 'pending', 'qualified', 73, 'Referral', 'PrÃ©sentation effectuÃ©e', NOW() - INTERVAL '13 days'),
('cccc6666-6666-6666-6666-666666666662', '44444444-4444-4444-4444-444444444446', NULL, 'Mobile Accessories', 'info@mobileacc.ma', '+212 6 90 12 34 56', 'pending', 'contacted', 62, 'Cold Call', 'Appel tÃ©lÃ©phonique fait', NOW() - INTERVAL '4 days');

-- 7. INVOICES (15 factures)
INSERT INTO invoices (id, user_id, subscription_id, amount, status, invoice_number, due_date, paid_at, created_at)
VALUES
-- Merchants FREE (0â‚¬)
('i0011111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', NULL, 0.00, 'paid', 'i00-2024-0001', NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days', NOW() - INTERVAL '30 days'),
('i0011112-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222223', NULL, 0.00, 'paid', 'i00-2024-0002', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '25 days'),

-- Merchants PRO (499 DH)
('i0022221-2222-2222-2222-222222222221', '22222222-2222-2222-2222-222222222224', NULL, 499.00, 'paid', 'i00-2024-0003', NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days', NOW() - INTERVAL '20 days'),
('i0022222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222224', NULL, 499.00, 'pending', 'i00-2024-0004', NOW() + INTERVAL '15 days', NULL, NOW() - INTERVAL '5 days'),
('i0033331-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222225', NULL, 499.00, 'paid', 'i00-2024-0005', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '15 days'),
('i0033332-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222225', NULL, 499.00, 'pending', 'i00-2024-0006', NOW() + INTERVAL '20 days', NULL, NOW() - INTERVAL '2 days'),
('i0044441-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555551', NULL, 499.00, 'paid', 'i00-2024-0007', NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days', NOW() - INTERVAL '12 days'),

-- Merchant ENTERPRISE (1499 DH)
('i0055551-5555-5555-5555-555555555551', '22222222-2222-2222-2222-222222222226', NULL, 1499.00, 'paid', 'i00-2024-0008', NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days', NOW() - INTERVAL '30 days'),
('i0055552-5555-5555-5555-555555555552', '22222222-2222-2222-2222-222222222226', NULL, 1499.00, 'paid', 'i00-2024-0009', NOW() + INTERVAL '5 days', NOW() - INTERVAL '1 day', NOW() - INTERVAL '5 days'),
('i0055553-5555-5555-5555-555555555553', '22222222-2222-2222-2222-222222222226', NULL, 1499.00, 'pending', 'i00-2024-0010', NOW() + INTERVAL '35 days', NULL, NOW()),

-- Factures en retard/annulÃ©es
('i0066661-6666-6666-6666-666666666661', '22222222-2222-2222-2222-222222222224', NULL, 499.00, 'failed', 'i00-2024-0011', NOW() - INTERVAL '5 days', NULL, NOW() - INTERVAL '35 days'),
('i0066662-6666-6666-6666-666666666662', '55555555-5555-5555-5555-555555555551', NULL, 499.00, 'failed', 'i00-2024-0012', NOW() - INTERVAL '10 days', NULL, NOW() - INTERVAL '40 days'),
('i0088881-8888-8888-8888-888888888881', '22222222-2222-2222-2222-222222222222', NULL, 0.00, 'pending', 'i00-2024-0013', NOW() + INTERVAL '30 days', NULL, NOW());

-- ============================================
-- RÃ‰SUMÃ‰ FINAL
-- ============================================

DO $$
DECLARE
    total_users INT;
    total_campaigns INT;
    total_products INT;
    total_commissions INT;
    total_leads INT;
    total_invoices INT;
BEGIN
    SELECT COUNT(*) INTO total_users FROM users;
    SELECT COUNT(*) INTO total_campaigns FROM campaigns;
    SELECT COUNT(*) INTO total_products FROM products;
    SELECT COUNT(*) INTO total_commissions FROM commissions;
    SELECT COUNT(*) INTO total_leads FROM leads;
    SELECT COUNT(*) INTO total_invoices FROM invoices;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'âœ… DONNÃ‰ES DE TEST GÃ‰NÃ‰RÃ‰ES AVEC SUCCÃˆS';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'ðŸ“Š RÃ‰SUMÃ‰:';
    RAISE NOTICE '   - Users: % (1 admin, 6 merchants, 7 influencers, 6 commerciaux)', total_users;
    RAISE NOTICE '   - Campaigns: %', total_campaigns;
    RAISE NOTICE '   - Products: %', total_products;
    RAISE NOTICE '   - Commissions: %', total_commissions;
    RAISE NOTICE '   - Leads: %', total_leads;
    RAISE NOTICE '   - Invoices: %', total_invoices;
    RAISE NOTICE '';
    RAISE NOTICE 'ðŸ’³ PAR SUBSCRIPTION:';
    RAISE NOTICE '   - Free: 2 merchants (0â‚¬/mois)';
    RAISE NOTICE '   - Pro: 3 merchants (499 DH/mois)';
    RAISE NOTICE '   - Enterprise: 1 merchant (1499 DH/mois)';
    RAISE NOTICE '';
    RAISE NOTICE 'ðŸŽ¯ Vous pouvez maintenant tester les dashboards!';
    RAISE NOTICE '========================================';
END $$;


