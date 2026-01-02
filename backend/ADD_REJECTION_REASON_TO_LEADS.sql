-- Ajout de la colonne rejection_reason à la table leads
ALTER TABLE public.leads ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
