-- Migration: Ajouter device_type à tracking_events
-- Date: 2024-12-06
-- Description: Ajoute la colonne device_type pour stocker le type d'appareil

ALTER TABLE tracking_events 
ADD COLUMN IF NOT EXISTS device_type TEXT;

COMMENT ON COLUMN tracking_events.device_type IS 'Type d''appareil: mobile, desktop, tablet';
