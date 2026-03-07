-- ============================================
-- SCRIPT DE CORRECTION DU SCHÉMA DE BASE DE DONNÉES
-- ============================================
-- Ce script corrige les erreurs "column does not exist" et "record has no field"
-- Il doit être exécuté dans l'éditeur SQL de Supabase.
-- ============================================

BEGIN;

-- 1. Ajouter la colonne commercial_id à la table users (si manquante)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'commercial_id') THEN
        ALTER TABLE public.users ADD COLUMN commercial_id UUID REFERENCES public.users(id) ON DELETE SET NULL;
        RAISE NOTICE '✅ Colonne commercial_id ajoutée à users';
    END IF;
END $$;

-- 2. Ajouter la colonne commercial_id à la table leads (si manquante)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'commercial_id') THEN
        ALTER TABLE public.leads ADD COLUMN commercial_id UUID REFERENCES public.users(id) ON DELETE SET NULL;
        CREATE INDEX IF NOT EXISTS idx_leads_commercial_id ON public.leads(commercial_id);
        RAISE NOTICE '✅ Colonne commercial_id ajoutée à leads';
    END IF;
END $$;

-- 3. Ajouter la colonne sales_rep_id à la table leads (si manquante)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'sales_rep_id') THEN
        ALTER TABLE public.leads ADD COLUMN sales_rep_id UUID REFERENCES public.users(id) ON DELETE SET NULL;
        CREATE INDEX IF NOT EXISTS idx_leads_sales_rep_id ON public.leads(sales_rep_id);
        RAISE NOTICE '✅ Colonne sales_rep_id ajoutée à leads';
    END IF;
END $$;

-- 4. Mettre à jour la contrainte de rôle sur la table users
DO $$
BEGIN
    ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_role_check;
    ALTER TABLE public.users ADD CONSTRAINT users_role_check 
    CHECK (role IN ('admin', 'merchant', 'influencer', 'commercial', 'affiliate'));
    RAISE NOTICE '✅ Contrainte users_role_check mise à jour';
END $$;

-- 5. Recréer la fonction auto_assign_sales_rep pour s'assurer qu'elle est valide
CREATE OR REPLACE FUNCTION auto_assign_sales_rep()
RETURNS TRIGGER AS $$
DECLARE
  available_rep_id UUID;
BEGIN
  -- Si nouveau merchant sans commercial assigné
  -- Note: NEW.commercial_id est maintenant valide car la colonne existe
  IF NEW.role IN ('merchant', 'advertiser') AND NEW.commercial_id IS NULL THEN
    -- Trouver commercial avec le moins de clients
    SELECT u.id INTO available_rep_id
    FROM users u
    WHERE u.role = 'commercial'
    AND u.is_active = TRUE
    ORDER BY (
      SELECT COUNT(*) FROM sales_assignments sa
      WHERE sa.sales_rep_id = u.id
      AND sa.status = 'active'
    ) ASC
    LIMIT 1;
    
    -- Si commercial trouvé, créer assignation
    IF available_rep_id IS NOT NULL THEN
      INSERT INTO sales_assignments (
        sales_rep_id,
        merchant_id,
        assigned_by,
        status
      ) VALUES (
        available_rep_id,
        NEW.id,
        NEW.id, -- Auto-assigné
        'active'
      );
      
      -- Mettre à jour commercial_id dans users
      NEW.commercial_id := available_rep_id;
    END IF;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;

DO $$
BEGIN
    RAISE NOTICE '🎉 Correction du schéma terminée avec succès!';
END $$;
