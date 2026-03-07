-- ========================================
-- CORRIGER LA TABLE INVOICES
-- ========================================
-- Il manque des colonnes !
-- ========================================

-- Supprimer la table existante et la recréer complètement
DROP TABLE IF EXISTS invoices CASCADE;

-- Créer la table avec TOUTES les colonnes
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Informations de base
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    merchant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Montants
    amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Description et détails
    description TEXT,
    notes TEXT,
    
    -- Statut et dates
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    due_date TIMESTAMPTZ NOT NULL,
    paid_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    
    -- Informations de paiement
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    
    -- Métadonnées
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ajouter les contraintes
ALTER TABLE invoices 
ADD CONSTRAINT invoices_status_check 
CHECK (status IN ('pending', 'paid', 'overdue', 'cancelled', 'refunded'));

ALTER TABLE invoices 
ADD CONSTRAINT invoices_amount_positive 
CHECK (amount >= 0);

ALTER TABLE invoices 
ADD CONSTRAINT invoices_total_amount_positive 
CHECK (total_amount >= 0);

-- Créer les index
CREATE INDEX idx_invoices_merchant_id ON invoices(merchant_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_created_at ON invoices(created_at DESC);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);

-- Créer la fonction pour updated_at
CREATE OR REPLACE FUNCTION update_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Créer le trigger
CREATE TRIGGER trigger_update_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_invoices_updated_at();

-- Activer RLS
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Politiques RLS
CREATE POLICY "Admins can view all invoices"
    ON invoices FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

CREATE POLICY "Merchants can view their own invoices"
    ON invoices FOR SELECT
    USING (merchant_id = auth.uid());

CREATE POLICY "Admins can create invoices"
    ON invoices FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

CREATE POLICY "Admins can update invoices"
    ON invoices FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- Vérifier que TOUTES les colonnes sont là
SELECT 
    column_name, 
    data_type
FROM information_schema.columns 
WHERE table_name = 'invoices'
ORDER BY ordinal_position;

-- ========================================
-- APRÈS CETTE EXÉCUTION:
-- Revenez ici et tapez "fait"
-- ========================================
