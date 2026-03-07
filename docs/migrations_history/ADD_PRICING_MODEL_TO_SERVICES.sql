-- ============================================
-- Migration: Ajouter le modèle de tarification aux services
-- ============================================

-- Ajouter la colonne pricing_model à la table services
ALTER TABLE public.services 
ADD COLUMN IF NOT EXISTS pricing_model TEXT 
CHECK (pricing_model IN ('fixed_price', 'per_lead', 'subscription', 'commission_only')) 
DEFAULT 'fixed_price';

-- Ajouter un commentaire pour expliquer les valeurs possibles
COMMENT ON COLUMN public.services.pricing_model IS 
'Type de tarification: fixed_price (prix fixe), per_lead (par lead généré), subscription (abonnement), commission_only (commission uniquement)';

-- Mettre à jour le service "Consultation stylist personnel" pour utiliser le paiement par lead
UPDATE public.services 
SET pricing_model = 'per_lead'
WHERE name = 'Consultation stylist personnel';

-- Mettre le prix à 0 pour les services par lead (seulement commission)
UPDATE public.services 
SET price = 0.00
WHERE pricing_model = 'per_lead';

-- Vérifier les mises à jour
SELECT id, name, description, price, commission_rate, pricing_model
FROM public.services
WHERE name = 'Consultation stylist personnel';
