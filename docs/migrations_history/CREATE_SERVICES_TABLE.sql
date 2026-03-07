-- ========================================
-- CRÉER TABLE SERVICES (séparée de products)
-- ========================================

-- Services = prestations payées par lead
-- Différent des produits qui sont payés par commission %

CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    
    -- Informations de base
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) CHECK (category IN (
        'Consultation', 'Formation', 'Coaching', 
        'Marketing Digital', 'Développement Web', 
        'Design Graphique', 'Rédaction', 'Traduction',
        'Comptabilité', 'Juridique', 'Immobilier', 'Autre'
    )),
    
    -- Tarification PAR LEAD (pas de commission %)
    price_per_lead DECIMAL(10, 2) NOT NULL, -- Prix payé à l'influenceur par lead qualifié
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Lead qualification criteria
    lead_requirements JSONB DEFAULT '{}', -- Critères de qualification du lead
    -- Exemple: {"min_budget": 1000, "location": "Morocco", "company_size": "10-50"}
    
    -- Médias
    images JSONB DEFAULT '[]',
    videos JSONB DEFAULT '[]',
    
    -- Disponibilité
    is_available BOOLEAN DEFAULT true,
    capacity_per_month INTEGER, -- Nombre max de leads/mois (null = illimité)
    
    -- Métriques
    total_leads INTEGER DEFAULT 0,
    total_leads_qualified INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    
    -- Metadata
    slug VARCHAR(255) UNIQUE,
    tags JSONB DEFAULT '[]',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_services_merchant_id ON services(merchant_id);
CREATE INDEX IF NOT EXISTS idx_services_category ON services(category);

-- Fonction de mise à jour automatique de updated_at
CREATE OR REPLACE FUNCTION update_services_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_services_timestamp
    BEFORE UPDATE ON services
    FOR EACH ROW
    EXECUTE FUNCTION update_services_updated_at();

-- Row Level Security
ALTER TABLE services ENABLE ROW LEVEL SECURITY;

-- Policies RLS
-- 1. Tout le monde peut voir les services disponibles (désactivé temporairement)
-- CREATE POLICY "Services disponibles visibles par tous"
--     ON services FOR SELECT
--     USING (is_available = true);

-- 2. Admin voit tout
CREATE POLICY "Admin voit tous les services"
    ON services FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- 3. Merchant voit/modifie ses propres services
CREATE POLICY "Merchant voit ses services"
    ON services FOR SELECT
    USING (merchant_id = auth.uid());

CREATE POLICY "Merchant crée ses services"
    ON services FOR INSERT
    WITH CHECK (merchant_id = auth.uid());

CREATE POLICY "Merchant modifie ses services"
    ON services FOR UPDATE
    USING (merchant_id = auth.uid());

CREATE POLICY "Merchant supprime ses services"
    ON services FOR DELETE
    USING (merchant_id = auth.uid());
