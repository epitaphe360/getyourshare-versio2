-- ========================================
-- RECRÉER TABLE SERVICES (VERSION SIMPLE)
-- ========================================

-- Supprimer la table existante
DROP TABLE IF EXISTS services CASCADE;

-- Créer la table avec toutes les colonnes
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price_per_lead DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    lead_requirements JSONB DEFAULT '{}',
    images JSONB DEFAULT '[]',
    videos JSONB DEFAULT '[]',
    is_available BOOLEAN DEFAULT true,
    capacity_per_month INTEGER,
    total_leads INTEGER DEFAULT 0,
    total_leads_qualified INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    slug VARCHAR(255) UNIQUE,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_services_merchant_id ON services(merchant_id);
CREATE INDEX idx_services_category ON services(category);

-- Vérifier la structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'services' 
ORDER BY ordinal_position;
