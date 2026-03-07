-- ============================================
-- CORRECTION FINALE DU SCHÉMA DE BASE DE DONNÉES
-- ============================================
-- Ajout de la colonne lead_status manquante
-- ============================================

BEGIN;

-- Ajouter la colonne lead_status à la table leads (si manquante)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'lead_status') THEN
        ALTER TABLE public.leads ADD COLUMN lead_status TEXT DEFAULT 'new';
        CREATE INDEX IF NOT EXISTS idx_leads_lead_status ON public.leads(lead_status);
        RAISE NOTICE '✅ Colonne lead_status ajoutée à leads';
    END IF;
END $$;

COMMIT;

DO $$
BEGIN
    RAISE NOTICE '🎉 Correction finale terminée!';
END $$;
