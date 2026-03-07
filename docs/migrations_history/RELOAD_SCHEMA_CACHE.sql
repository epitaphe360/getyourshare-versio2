-- ========================================
-- RECHARGER LE CACHE DU SCHÉMA POSTGREST
-- ========================================
-- À exécuter dans l'éditeur SQL de Supabase
-- ========================================

-- Cette commande force PostgREST à recharger son cache du schéma
-- C'est nécessaire après avoir créé de nouvelles tables ou colonnes
NOTIFY pgrst, 'reload schema';

-- ========================================
-- INSTRUCTIONS:
-- ========================================
-- 1. Allez sur https://supabase.com/dashboard
-- 2. Sélectionnez votre projet
-- 3. Cliquez sur "SQL Editor" dans le menu de gauche
-- 4. Copiez-collez cette commande: NOTIFY pgrst, 'reload schema';
-- 5. Cliquez sur "Run" (bouton vert)
-- 6. Attendez 2-3 secondes
-- 7. Revenez ici et tapez "fait" dans le chat
-- ========================================

-- ALTERNATIVE SI CELA NE FONCTIONNE PAS:
-- 1. Allez dans Settings > General
-- 2. Cliquez sur "Pause project"
-- 3. Attendez 30 secondes
-- 4. Cliquez sur "Resume project"
-- 5. Attendez que le projet redémarre (2-3 minutes)
-- ========================================
