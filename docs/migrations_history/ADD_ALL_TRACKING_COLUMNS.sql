-- Migration COMPLÈTE: Ajouter toutes les colonnes tracking à tracking_events
-- Date: 2024-12-06

-- Ajouter toutes les colonnes manquantes en une seule fois
ALTER TABLE tracking_events 
ADD COLUMN IF NOT EXISTS browser TEXT,
ADD COLUMN IF NOT EXISTS device TEXT,
ADD COLUMN IF NOT EXISTS device_type TEXT,
ADD COLUMN IF NOT EXISTS country TEXT,
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS referrer TEXT;

-- Commentaires
COMMENT ON COLUMN tracking_events.browser IS 'Navigateur utilisé';
COMMENT ON COLUMN tracking_events.device IS 'Appareil utilisé';
COMMENT ON COLUMN tracking_events.device_type IS 'Type: mobile, desktop, tablet';
COMMENT ON COLUMN tracking_events.country IS 'Pays de provenance';
COMMENT ON COLUMN tracking_events.city IS 'Ville de provenance';
COMMENT ON COLUMN tracking_events.referrer IS 'URL de provenance';
