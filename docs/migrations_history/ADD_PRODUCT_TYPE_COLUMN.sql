-- ========================================
-- AJOUTER COLONNE TYPE POUR PRODUITS/SERVICES
-- ========================================

-- Ajouter la colonne type si elle n'existe pas déjà
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'products' AND column_name = 'type'
    ) THEN
        ALTER TABLE products 
        ADD COLUMN type VARCHAR(20) DEFAULT 'product' CHECK (type IN ('product', 'service'));
        
        COMMENT ON COLUMN products.type IS 'Type: product (produit physique) ou service (prestation)';
    END IF;
END $$;

-- Mettre à jour les produits existants
-- Par défaut tout est "product" sauf les formations et consultations
UPDATE products 
SET type = 'service'
WHERE name ILIKE '%formation%' 
   OR name ILIKE '%consultation%'
   OR name ILIKE '%coaching%'
   OR name ILIKE '%accompagnement%'
   OR category = 'Services'
   OR description ILIKE '%service%'
   OR description ILIKE '%prestation%';

-- Vérifier les résultats
SELECT 
    type,
    COUNT(*) as total,
    STRING_AGG(DISTINCT category, ', ') as categories
FROM products
GROUP BY type;

-- Afficher quelques exemples de chaque type
SELECT 
    type,
    name,
    category,
    price
FROM products
ORDER BY type, name
LIMIT 20;
