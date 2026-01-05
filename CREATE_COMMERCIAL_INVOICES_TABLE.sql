-- ============================================================================
-- TABLE: commercial_invoices
-- Description: Stocke les factures générées lors des paiements de commissions
-- aux commerciaux (sales representatives) pour la conformité fiscale
-- Supporte: Maroc (MA), France (FR), États-Unis (US)
-- ============================================================================

-- Supprimer la table si elle existe (pour développement)
-- DROP TABLE IF EXISTS commercial_invoices;

-- Créer la table des factures commerciaux
CREATE TABLE IF NOT EXISTS commercial_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Numéro de facture unique (format: COM-YYYY-NNNNN)
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Références
    commission_id UUID,  -- Référence à sales_commissions si applicable
    commercial_id UUID NOT NULL,  -- Référence à users (role = commercial/sales_rep)
    deal_id UUID,  -- Référence au deal associé
    lead_id UUID,  -- Référence au lead associé
    
    -- Type de commission
    commission_type VARCHAR(50) DEFAULT 'commission' CHECK (commission_type IN ('lead', 'subscription', 'bonus', 'commission')),
    
    -- Montants
    gross_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    net_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    
    -- Informations commercial (snapshot au moment de la facture)
    commercial_name VARCHAR(255),
    commercial_email VARCHAR(255),
    commercial_phone VARCHAR(50),
    commercial_address TEXT,
    commercial_country VARCHAR(2) DEFAULT 'FR',
    commercial_tax_id VARCHAR(100),
    commercial_tax_status VARCHAR(50) DEFAULT 'individual',
    
    -- Informations entreprise émettrice (GetYourShare)
    company_name VARCHAR(255) DEFAULT 'GetYourShare',
    company_address TEXT,
    company_tax_id VARCHAR(100),
    
    -- Période couverte par la facture
    period_start DATE,
    period_end DATE,
    
    -- Description de la prestation
    description TEXT DEFAULT 'Commission commerciale',
    
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
CREATE INDEX IF NOT EXISTS idx_com_invoices_commercial ON commercial_invoices(commercial_id);
CREATE INDEX IF NOT EXISTS idx_com_invoices_date ON commercial_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_com_invoices_number ON commercial_invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_com_invoices_country ON commercial_invoices(commercial_country);
CREATE INDEX IF NOT EXISTS idx_com_invoices_status ON commercial_invoices(status);
CREATE INDEX IF NOT EXISTS idx_com_invoices_type ON commercial_invoices(commission_type);
CREATE INDEX IF NOT EXISTS idx_com_invoices_deal ON commercial_invoices(deal_id);
CREATE INDEX IF NOT EXISTS idx_com_invoices_lead ON commercial_invoices(lead_id);

-- Trigger pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_commercial_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_commercial_invoices_updated_at ON commercial_invoices;
CREATE TRIGGER trigger_update_commercial_invoices_updated_at
    BEFORE UPDATE ON commercial_invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_commercial_invoices_updated_at();

-- Commentaires pour documentation
COMMENT ON TABLE commercial_invoices IS 'Factures générées lors des paiements de commissions aux commerciaux pour conformité fiscale';
COMMENT ON COLUMN commercial_invoices.invoice_number IS 'Numéro de facture unique au format COM-YYYY-NNNNN';
COMMENT ON COLUMN commercial_invoices.commercial_country IS 'Code pays ISO 2 lettres (MA, FR, US)';
COMMENT ON COLUMN commercial_invoices.commission_type IS 'Type: lead (commission lead), subscription (commission abonnement), bonus (prime), commission (autre)';
COMMENT ON COLUMN commercial_invoices.tax_details IS 'Détails des taxes appliquées en JSON';
COMMENT ON COLUMN commercial_invoices.commercial_tax_id IS 'ICE (Maroc), SIRET (France), SSN/EIN (USA)';

-- ============================================================================
-- Politiques RLS (Row Level Security)
-- ============================================================================

-- Activer RLS
ALTER TABLE commercial_invoices ENABLE ROW LEVEL SECURITY;

-- Politique pour les admins (tout voir)
CREATE POLICY admin_all_com_invoices ON commercial_invoices
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- Politique pour les commerciaux (voir leurs propres factures)
CREATE POLICY commercial_own_invoices ON commercial_invoices
    FOR SELECT
    TO authenticated
    USING (
        commercial_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- ============================================================================
-- Vue pour faciliter les requêtes
-- ============================================================================

CREATE OR REPLACE VIEW v_commercial_invoices_summary AS
SELECT 
    ci.id,
    ci.invoice_number,
    ci.invoice_date,
    ci.commercial_name,
    ci.commercial_country,
    ci.commercial_tax_id,
    ci.commission_type,
    ci.gross_amount,
    ci.tax_amount,
    ci.net_amount,
    ci.currency,
    ci.status,
    ci.description,
    ci.company_name,
    EXTRACT(YEAR FROM ci.invoice_date) as invoice_year,
    EXTRACT(MONTH FROM ci.invoice_date) as invoice_month
FROM commercial_invoices ci
ORDER BY ci.invoice_date DESC;

-- ============================================================================
-- Fonction pour générer le prochain numéro de facture commercial
-- ============================================================================

CREATE OR REPLACE FUNCTION get_next_commercial_invoice_number()
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
    FROM commercial_invoices
    WHERE invoice_number LIKE 'COM-' || current_year || '-%';
    
    -- Formater le numéro de facture
    invoice_num := 'COM-' || current_year || '-' || LPAD(next_seq::TEXT, 5, '0');
    
    RETURN invoice_num;
END;
$$ LANGUAGE plpgsql;

-- Exemple d'utilisation:
-- SELECT get_next_commercial_invoice_number(); -- Retourne 'COM-2025-00001'

-- ============================================================================
-- Exemple de données de test
-- ============================================================================

-- INSERT INTO commercial_invoices (
--     invoice_number,
--     commercial_id,
--     commission_type,
--     gross_amount,
--     tax_amount,
--     net_amount,
--     currency,
--     commercial_name,
--     commercial_email,
--     commercial_country,
--     commercial_tax_id,
--     description,
--     tax_details
-- ) VALUES (
--     'COM-2025-00001',
--     'uuid-commercial-1',
--     'lead',
--     5000.00,
--     500.00,
--     4500.00,
--     'MAD',
--     'Sofia Chakir',
--     'sofia@example.com',
--     'MA',
--     '001234567890456',
--     'Commission sur lead qualifié - Tech Shop SARL',
--     '[{"name": "Retenue à la source (10%)", "rate": 10, "amount": 500}]'::jsonb
-- );
