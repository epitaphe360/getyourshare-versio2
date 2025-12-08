-- Migration: Création table invoices pour génération PDF factures
-- Date: 2025-12-07
-- Description: Table pour stocker les factures générées (MA/FR/US)

-- ============================================
-- TABLE INVOICES
-- ============================================

-- Drop existing invoices table if it exists with wrong structure
DROP TABLE IF EXISTS invoices CASCADE;

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    merchant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Type et statut
    invoice_type VARCHAR(20) DEFAULT 'sale', -- sale, service, deposit
    status VARCHAR(20) DEFAULT 'generated', -- generated, sent, paid, overdue, voided
    country VARCHAR(2) NOT NULL, -- MA, FR, US

    -- Montants
    total_ht DECIMAL(12, 2) NOT NULL DEFAULT 0,
    total_vat DECIMAL(12, 2) DEFAULT 0,
    total_ttc DECIMAL(12, 2) DEFAULT 0,

    -- Fichier PDF
    pdf_url TEXT,
    pdf_path TEXT,

    -- Dates
    invoice_date TIMESTAMP DEFAULT NOW(),
    due_date TIMESTAMP,
    sent_at TIMESTAMP,
    paid_at TIMESTAMP,
    voided_at TIMESTAMP,

    -- Paiement
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    payment_terms TEXT,

    -- Annulation
    void_reason TEXT,

    -- Métadonnées
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_invoices_merchant ON invoices(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_client ON invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_invoices_country ON invoices(country);

-- RLS (Row Level Security) - Désactivé pour simplicité
-- ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Policy: Merchant peut voir ses factures
-- CREATE POLICY invoices_merchant_read ON invoices
--     FOR SELECT
--     USING (merchant_id = auth.uid());

-- Policy: Merchant peut créer ses factures
-- CREATE POLICY invoices_merchant_create ON invoices
--     FOR INSERT
--     WITH CHECK (merchant_id = auth.uid());

-- Policy: Merchant peut modifier ses factures
-- CREATE POLICY invoices_merchant_update ON invoices
--     FOR UPDATE
--     USING (merchant_id = auth.uid());

-- Policy: Client peut voir ses factures
-- CREATE POLICY invoices_client_read ON invoices
--     FOR SELECT
--     USING (client_id = auth.uid());

-- Policy: Admin peut tout voir
-- CREATE POLICY invoices_admin_all ON invoices
--     FOR ALL
--     USING (
--         EXISTS (
--             SELECT 1 FROM users
--             WHERE users.id = auth.uid()
--             AND users.role = 'admin'
--         )
--     );

-- ============================================
-- TRIGGER UPDATE TIMESTAMP
-- ============================================

CREATE OR REPLACE FUNCTION update_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_invoices_updated_at();

-- ============================================
-- TRIGGER AUTO-CALCUL TOTAL TTC
-- ============================================

CREATE OR REPLACE FUNCTION calculate_invoice_totals()
RETURNS TRIGGER AS $$
BEGIN
    -- Si total_vat et total_ht fournis, calculer total_ttc
    IF NEW.total_ht IS NOT NULL AND NEW.total_vat IS NOT NULL THEN
        NEW.total_ttc = NEW.total_ht + NEW.total_vat;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_invoice_totals
    BEFORE INSERT OR UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION calculate_invoice_totals();

-- ============================================
-- FONCTION: Générer prochain numéro facture
-- ============================================

CREATE OR REPLACE FUNCTION get_next_invoice_number(
    p_merchant_id UUID,
    p_country VARCHAR(2)
)
RETURNS VARCHAR AS $$
DECLARE
    v_year INTEGER;
    v_last_sequence INTEGER;
    v_next_sequence INTEGER;
    v_invoice_number VARCHAR(50);
BEGIN
    v_year := EXTRACT(YEAR FROM NOW());

    -- Récupérer le dernier numéro de l'année en cours
    SELECT COALESCE(
        MAX(
            CAST(
                SPLIT_PART(invoice_number, '-', 3) AS INTEGER
            )
        ),
        0
    )
    INTO v_last_sequence
    FROM invoices
    WHERE merchant_id = p_merchant_id
    AND country = p_country
    AND invoice_number LIKE (v_year::VARCHAR || '-' || p_country || '-%');

    -- Incrémenter
    v_next_sequence := v_last_sequence + 1;

    -- Formater: YYYY-CC-NNNNN (ex: 2025-MA-00001)
    v_invoice_number := v_year::VARCHAR || '-' || p_country || '-' || LPAD(v_next_sequence::VARCHAR, 5, '0');

    RETURN v_invoice_number;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Marquer factures overdue
-- ============================================

CREATE OR REPLACE FUNCTION mark_overdue_invoices()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE invoices
    SET status = 'overdue'
    WHERE status IN ('generated', 'sent')
    AND due_date < NOW()
    AND due_date IS NOT NULL;

    GET DIAGNOSTICS v_count = ROW_COUNT;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VUES UTILES (désactivées - à créer après vérification de la structure)
-- ============================================

-- Vue: Factures avec infos merchant et client
-- DROP VIEW IF EXISTS invoices_detailed CASCADE;
-- CREATE OR REPLACE VIEW invoices_detailed AS
-- SELECT
--     i.*,
--     m.email AS merchant_email,
--     m.first_name AS merchant_first_name,
--     m.last_name AS merchant_last_name,
--     c.email AS client_email,
--     c.first_name AS client_first_name,
--     c.last_name AS client_last_name
-- FROM invoices i
-- LEFT JOIN users m ON i.merchant_id = m.id
-- LEFT JOIN users c ON i.client_id = c.id;

-- Vue: Statistiques factures par merchant
-- DROP VIEW IF EXISTS invoice_stats_by_merchant CASCADE;
-- CREATE OR REPLACE VIEW invoice_stats_by_merchant AS
-- SELECT
--     merchant_id,
--     COUNT(*) AS total_invoices,
--     SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid_invoices,
--     SUM(CASE WHEN status IN ('generated', 'sent') THEN 1 ELSE 0 END) AS pending_invoices,
--     SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END) AS overdue_invoices,
--     SUM(total_ht) AS total_amount_ht,
--     SUM(total_ttc) AS total_amount_ttc,
--     SUM(CASE WHEN status = 'paid' THEN total_ttc ELSE 0 END) AS paid_amount,
--     SUM(CASE WHEN status IN ('generated', 'sent', 'overdue') THEN total_ttc ELSE 0 END) AS pending_amount
-- FROM invoices
-- GROUP BY merchant_id;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE invoices IS 'Factures PDF conformes multi-pays (MA/FR/US)';
COMMENT ON COLUMN invoices.invoice_number IS 'Numéro chronologique unique (ex: 2025-MA-00001)';
COMMENT ON COLUMN invoices.country IS 'Pays de la facture (MA=Maroc, FR=France, US=USA)';
COMMENT ON COLUMN invoices.total_ht IS 'Montant Hors Taxes';
COMMENT ON COLUMN invoices.total_vat IS 'Montant TVA (ou Sales Tax pour US)';
COMMENT ON COLUMN invoices.total_ttc IS 'Montant TTC (Total avec taxes)';
COMMENT ON COLUMN invoices.pdf_path IS 'Chemin dans Supabase Storage';
COMMENT ON COLUMN invoices.metadata IS 'Données supplémentaires (payment_terms, line_items, etc.)';
