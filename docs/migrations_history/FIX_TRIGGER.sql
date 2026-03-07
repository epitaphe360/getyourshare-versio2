-- ============================================
-- CORRECTION DU TRIGGER D'ASSIGNATION AUTOMATIQUE
-- ============================================
-- Le trigger doit être AFTER INSERT et non BEFORE INSERT
-- car la table sales_assignments a une clé étrangère vers users
-- ============================================

BEGIN;

-- 1. Supprimer l'ancien trigger
DROP TRIGGER IF EXISTS trg_auto_assign_sales_rep ON public.users;

-- 2. Recréer la fonction pour qu'elle retourne NULL (pour un trigger AFTER)
-- ou garder NEW, ça marche aussi pour AFTER mais c'est ignoré.
-- On va juste changer le moment du trigger.

-- 3. Créer le trigger en AFTER INSERT
CREATE TRIGGER trg_auto_assign_sales_rep
AFTER INSERT ON public.users
FOR EACH ROW
EXECUTE FUNCTION auto_assign_sales_rep();

COMMIT;

DO $$
BEGIN
    RAISE NOTICE '✅ Trigger trg_auto_assign_sales_rep corrigé (passé en AFTER INSERT)';
END $$;
