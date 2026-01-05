-- Migration: Ajouter commission_rate à la table services
-- Date: 2024-12-06
-- Description: Ajoute la colonne commission_rate pour gérer les commissions sur les services

-- Ajouter la colonne commission_rate
ALTER TABLE services 
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,2) DEFAULT 10.0 CHECK (commission_rate >= 0 AND commission_rate <= 100);

-- Mettre à jour les services existants avec un taux par défaut
UPDATE services 
SET commission_rate = 10.0 
WHERE commission_rate IS NULL;

-- Commenter la colonne
COMMENT ON COLUMN services.commission_rate IS 'Taux de commission en pourcentage pour ce service (0-100)';
