-- Migration: Ajout de colonnes pour enrichir la table campaigns
-- Date: 2024-12-03

-- Ajouter la colonne campaign_type pour le type de campagne
ALTER TABLE campaigns 
ADD COLUMN IF NOT EXISTS campaign_type VARCHAR(100);

-- Ajouter la colonne category pour la catégorie de produits
ALTER TABLE campaigns 
ADD COLUMN IF NOT EXISTS category VARCHAR(100);

-- Ajouter la colonne commission_rate pour le taux de commission
ALTER TABLE campaigns 
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5, 2) DEFAULT 10.00;

-- Ajouter la colonne performance_metrics pour stocker les métriques JSON
ALTER TABLE campaigns 
ADD COLUMN IF NOT EXISTS performance_metrics JSONB DEFAULT '{}';

-- Ajouter la colonne products_count pour le nombre de produits
ALTER TABLE campaigns 
ADD COLUMN IF NOT EXISTS products_count INTEGER DEFAULT 0;

-- Mettre à jour les valeurs par défaut pour les campagnes existantes
UPDATE campaigns 
SET campaign_type = 'Saisonnière' 
WHERE campaign_type IS NULL;

UPDATE campaigns 
SET category = 'Général' 
WHERE category IS NULL;

UPDATE campaigns 
SET commission_rate = 15.00 
WHERE commission_rate IS NULL OR commission_rate = 0;

UPDATE campaigns 
SET products_count = 10 
WHERE products_count = 0;

-- Créer un index sur les colonnes fréquemment utilisées
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_type ON campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON campaigns(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_campaigns_merchant ON campaigns(merchant_id);

COMMENT ON COLUMN campaigns.campaign_type IS 'Type de campagne: Soldes, Lancement Produit, Saisonnière, Flash, Event Spécial';
COMMENT ON COLUMN campaigns.category IS 'Catégorie de produits ciblés';
COMMENT ON COLUMN campaigns.commission_rate IS 'Taux de commission pour les affiliés (%)';
COMMENT ON COLUMN campaigns.performance_metrics IS 'Métriques JSON: clicks, conversions, revenue, spent, roi, participants, etc.';
COMMENT ON COLUMN campaigns.products_count IS 'Nombre de produits inclus dans la campagne';
