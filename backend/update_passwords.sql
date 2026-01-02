-- ============================================================================
-- MISE À JOUR DES MOTS DE PASSE POUR LANCEMENT RAPIDE
-- ============================================================================
-- Nouveau mot de passe: Test123!
-- Hash bcrypt généré pour "Test123!"
-- ============================================================================

-- IMPORTANT: Ce hash correspond au mot de passe "Test123!"
-- Généré avec bcrypt: bcrypt.hashpw(b"Test123!", bcrypt.gensalt())

-- Mettre à jour TOUS les utilisateurs avec le nouveau mot de passe
UPDATE users
SET password_hash = '$2b$12$.JnsORn742tocce/LsmglepdDWoPFNvylXL5RdQytGWO5ghriap5G'
WHERE email IN (
    'admin@getyourshare.com',
    'hassan.oudrhiri@getyourshare.com',
    'sarah.benali@getyourshare.com',
    'karim.benjelloun@getyourshare.com',
    'boutique.maroc@getyourshare.com',
    'luxury.crafts@getyourshare.com',
    'electro.maroc@getyourshare.com',
    'sofia.chakir@getyourshare.com'
);

-- Vérifier les comptes mis à jour
SELECT
    email,
    role,
    is_active,
    email_verified,
    created_at
FROM users
WHERE email LIKE '%@getyourshare.com'
ORDER BY role, email;

-- ============================================================================
-- RÉSUMÉ
-- ============================================================================
-- Mot de passe universel: Test123!
--
-- Comptes disponibles:
-- - admin@getyourshare.com (ADMIN)
-- - hassan.oudrhiri@getyourshare.com (INFLUENCER - Starter)
-- - sarah.benali@getyourshare.com (INFLUENCER - Pro)
-- - karim.benjelloun@getyourshare.com (INFLUENCER - Pro)
-- - boutique.maroc@getyourshare.com (MERCHANT - Starter)
-- - luxury.crafts@getyourshare.com (MERCHANT - Pro)
-- - electro.maroc@getyourshare.com (MERCHANT - Enterprise)
-- - sofia.chakir@getyourshare.com (ADMIN/COMMERCIAL)
-- ============================================================================
