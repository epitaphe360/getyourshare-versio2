-- Migration: Ajouter colonnes de tracking à tracking_events
-- Date: 2024-12-06
-- Description: Ajoute les colonnes browser, device, country, city, referrer pour le tracking détaillé

-- Ajouter les colonnes manquantes
ALTER TABLE tracking_events 
ADD COLUMN IF NOT EXISTS browser TEXT,
ADD COLUMN IF NOT EXISTS device TEXT,
ADD COLUMN IF NOT EXISTS country TEXT,
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS referrer TEXT;

-- Commenter les colonnes
COMMENT ON COLUMN tracking_events.browser IS 'Navigateur utilisé pour l''événement';
COMMENT ON COLUMN tracking_events.device IS 'Type d''appareil (Desktop, Mobile, Tablet)';
COMMENT ON COLUMN tracking_events.country IS 'Pays de provenance de l''événement';
COMMENT ON COLUMN tracking_events.city IS 'Ville de provenance de l''événement';
COMMENT ON COLUMN tracking_events.referrer IS 'URL de provenance de l''événement';
