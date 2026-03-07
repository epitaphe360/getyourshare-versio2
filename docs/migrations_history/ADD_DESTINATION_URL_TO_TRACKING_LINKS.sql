-- Migration: Ajouter destination_url à la table tracking_links
-- Date: 2024-12-06
-- Description: Ajoute la colonne destination_url pour stocker l'URL de destination des liens de tracking

-- Ajouter la colonne destination_url
ALTER TABLE tracking_links 
ADD COLUMN IF NOT EXISTS destination_url TEXT;

-- Mettre à jour les liens existants avec l'URL complète comme destination par défaut
UPDATE tracking_links 
SET destination_url = full_url 
WHERE destination_url IS NULL;

-- Commenter la colonne
COMMENT ON COLUMN tracking_links.destination_url IS 'URL de destination vers laquelle le lien de tracking redirige';
