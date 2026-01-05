-- ============================================================================
-- TABLE: influencer_invoices
-- Description: Stocke les factures générées lors des paiements aux influenceurs
-- Pour la conformité fiscale (Maroc, France, USA)
-- ============================================================================

-- Supprimer la table si elle existe (pour développement)
-- DROP TABLE IF EXISTS influencer_invoices;

-- Créer la table des factures influenceurs
CREATE TABLE IF NOT EXISTS influencer_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Numéro de facture unique (format: INV-YYYY-NNNNN)
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Références
    payout_id UUID REFERENCES payouts(id) ON DELETE SET NULL,
    influencer_id UUID NOT NULL,
    merchant_id UUID,
    
    -- Montants
    gross_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    net_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    
    -- Informations influenceur (snapshot au moment de la facture)
    influencer_name VARCHAR(255),
    influencer_email VARCHAR(255),
    influencer_address TEXT,
    influencer_country VARCHAR(2) DEFAULT 'FR',
    influencer_tax_id VARCHAR(100),
    influencer_tax_status VARCHAR(50) DEFAULT 'individual',
    
    -- Informations marchand (snapshot au moment de la facture)
    merchant_name VARCHAR(255),
    merchant_email VARCHAR(255),
    merchant_address TEXT,
    merchant_tax_id VARCHAR(100),
    
    -- Période couverte par la facture
    period_start DATE,
    period_end DATE,
    
    -- Description de la prestation
    description TEXT DEFAULT 'Commission d''affiliation',
    
    -- Détails des taxes (JSON)
    tax_details JSONB DEFAULT '[]'::jsonb,
    
    -- Fichier PDF
    pdf_url TEXT,
    pdf_generated BOOLEAN DEFAULT FALSE,
    
    -- Statut de la facture
    status VARCHAR(20) DEFAULT 'generated' CHECK (status IN ('draft', 'generated', 'sent', 'paid', 'cancelled')),
    
    -- Date de la facture
    invoice_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_invoices_influencer ON influencer_invoices(influencer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_merchant ON influencer_invoices(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON influencer_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_invoices_number ON influencer_invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_country ON influencer_invoices(influencer_country);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON influencer_invoices(status);

-- Note: Pour filtrer par année, utilisez: WHERE invoice_date >= '2025-01-01' AND invoice_date < '2026-01-01'
-- ou créez une colonne calculée invoice_year si nécessaire

-- Trigger pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_influencer_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_influencer_invoices_updated_at ON influencer_invoices;
CREATE TRIGGER trigger_update_influencer_invoices_updated_at
    BEFORE UPDATE ON influencer_invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_influencer_invoices_updated_at();

-- Commentaires pour documentation
COMMENT ON TABLE influencer_invoices IS 'Factures générées lors des paiements aux influenceurs pour conformité fiscale';
COMMENT ON COLUMN influencer_invoices.invoice_number IS 'Numéro de facture unique au format INV-YYYY-NNNNN';
COMMENT ON COLUMN influencer_invoices.influencer_country IS 'Code pays ISO 2 lettres (MA, FR, US)';
COMMENT ON COLUMN influencer_invoices.tax_details IS 'Détails des taxes appliquées en JSON';
COMMENT ON COLUMN influencer_invoices.influencer_tax_id IS 'ICE (Maroc), SIRET (France), SSN/EIN (USA)';

-- ============================================================================
-- Exemple de données de test
-- ============================================================================

-- INSERT INTO influencer_invoices (
--     invoice_number,
--     influencer_id,
--     merchant_id,
--     gross_amount,
--     tax_amount,
--     net_amount,
--     currency,
--     influencer_name,
--     influencer_email,
--     influencer_country,
--     influencer_tax_id,
--     merchant_name,
--     description,
--     tax_details
-- ) VALUES (
--     'INV-2025-00001',
--     'uuid-influencer-1',
--     'uuid-merchant-1',
--     15000.00,
--     1500.00,
--     13500.00,
--     'MAD',
--     'Fatima El Amrani',
--     'fatima@example.com',
--     'MA',
--     '001234567890123',
--     'Tech Shop SARL',
--     'Commission affiliation Q4 2024',
--     '[{"name": "Retenue à la source (10%)", "rate": 10, "amount": 1500}]'::jsonb
-- );

-- ============================================================================
-- Politiques RLS (Row Level Security)
-- ============================================================================

-- Activer RLS
ALTER TABLE influencer_invoices ENABLE ROW LEVEL SECURITY;

-- Politique pour les admins (tout voir)
CREATE POLICY admin_all_invoices ON influencer_invoices
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- Politique pour les marchands (voir leurs factures)
CREATE POLICY merchant_own_invoices ON influencer_invoices
    FOR SELECT
    TO authenticated
    USING (
        merchant_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- Politique pour les influenceurs (voir leurs propres factures)
CREATE POLICY influencer_own_invoices ON influencer_invoices
    FOR SELECT
    TO authenticated
    USING (
        influencer_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- ============================================================================
-- Vue pour faciliter les requêtes
-- ============================================================================

CREATE OR REPLACE VIEW v_influencer_invoices_summary AS
SELECT 
    ii.id,
    ii.invoice_number,
    ii.invoice_date,
    ii.influencer_name,
    ii.influencer_country,
    ii.influencer_tax_id,
    ii.gross_amount,
    ii.tax_amount,
    ii.net_amount,
    ii.currency,
    ii.status,
    ii.description,
    ii.merchant_name,
    EXTRACT(YEAR FROM ii.invoice_date) as invoice_year,
    EXTRACT(MONTH FROM ii.invoice_date) as invoice_month
FROM influencer_invoices ii
ORDER BY ii.invoice_date DESC;

-- ============================================================================
-- Fonction pour générer le prochain numéro de facture
-- ============================================================================

CREATE OR REPLACE FUNCTION get_next_invoice_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    current_year INT;
    next_seq INT;
    invoice_num VARCHAR(50);
BEGIN
    current_year := EXTRACT(YEAR FROM NOW());
    
    -- Récupérer le dernier numéro de séquence pour l'année en cours
    SELECT COALESCE(
        MAX(
            CAST(
                SPLIT_PART(invoice_number, '-', 3) AS INT
            )
        ), 0
    ) + 1
    INTO next_seq
    FROM influencer_invoices
    WHERE invoice_number LIKE 'INV-' || current_year || '-%';
    
    -- Formater le numéro de facture
    invoice_num := 'INV-' || current_year || '-' || LPAD(next_seq::TEXT, 5, '0');
    
    RETURN invoice_num;
END;
$$ LANGUAGE plpgsql;

-- Exemple d'utilisation:
-- SELECT get_next_invoice_number(); -- Retourne 'INV-2025-00001'
