-- =====================================================
-- AJOUTER LA COLONNE subscription_tier À LA TABLE users
-- =====================================================
-- À exécuter AVANT INSERT_COMMERCIAL_DATA.sql
-- =====================================================

-- Vérifier si la colonne existe déjà et l'ajouter si nécessaire
DO $$ 
BEGIN
    -- Ajouter la colonne subscription_tier si elle n'existe pas
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'subscription_tier'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN subscription_tier TEXT 
        CHECK (subscription_tier IN ('starter', 'pro', 'enterprise')) 
        DEFAULT 'starter';
        
        RAISE NOTICE 'Colonne subscription_tier ajoutée avec succès';
    ELSE
        RAISE NOTICE 'La colonne subscription_tier existe déjà';
    END IF;
END $$;

-- Créer un index pour optimiser les requêtes par tier
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier 
ON public.users(subscription_tier);

-- Mettre à jour les utilisateurs existants avec un tier par défaut
UPDATE public.users 
SET subscription_tier = 'starter' 
WHERE subscription_tier IS NULL;

-- Vérification
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'users' 
  AND column_name = 'subscription_tier';

-- Afficher le résultat
SELECT 'subscription_tier column added successfully!' as status;
