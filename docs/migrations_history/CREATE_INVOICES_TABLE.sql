-- ========================================
-- CRÉATION DE LA TABLE INVOICES (FACTURES)
-- ========================================
-- À exécuter dans l'éditeur SQL de Supabase
-- ========================================

-- 1. Créer la table invoices
CREATE TABLE IF NOT EXISTS invoices (
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
    -- Statuts possibles: pending, paid, overdue, cancelled, refunded
    
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

-- 2. Ajouter les contraintes (supprimer d'abord si elles existent)
ALTER TABLE invoices DROP CONSTRAINT IF EXISTS invoices_status_check;
ALTER TABLE invoices 
ADD CONSTRAINT invoices_status_check 
CHECK (status IN ('pending', 'paid', 'overdue', 'cancelled', 'refunded'));

ALTER TABLE invoices DROP CONSTRAINT IF EXISTS invoices_amount_positive;
ALTER TABLE invoices 
ADD CONSTRAINT invoices_amount_positive 
CHECK (amount >= 0);

ALTER TABLE invoices DROP CONSTRAINT IF EXISTS invoices_total_amount_positive;
ALTER TABLE invoices 
ADD CONSTRAINT invoices_total_amount_positive 
CHECK (total_amount >= 0);

-- 3. Créer les index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_invoices_merchant_id ON invoices(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices(due_date);

-- 4. Créer la fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Créer le trigger
DROP TRIGGER IF EXISTS trigger_update_invoices_updated_at ON invoices;
CREATE TRIGGER trigger_update_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_invoices_updated_at();

-- 6. Activer Row Level Security (RLS)
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- 7. Créer les politiques RLS (supprimer d'abord si elles existent)
DROP POLICY IF EXISTS "Admins can view all invoices" ON invoices;
CREATE POLICY "Admins can view all invoices"
    ON invoices FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

DROP POLICY IF EXISTS "Merchants can view their own invoices" ON invoices;
CREATE POLICY "Merchants can view their own invoices"
    ON invoices FOR SELECT
    USING (merchant_id = auth.uid());

DROP POLICY IF EXISTS "Admins can create invoices" ON invoices;
CREATE POLICY "Admins can create invoices"
    ON invoices FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

DROP POLICY IF EXISTS "Admins can update invoices" ON invoices;
CREATE POLICY "Admins can update invoices"
    ON invoices FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- 8. Vérifier que la table a été créée
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'invoices'
ORDER BY ordinal_position;

-- ========================================
-- RÉSULTAT ATTENDU:
-- La table invoices devrait être créée avec:
-- - Toutes les colonnes nécessaires
-- - Contraintes de validation
-- - Index pour les performances
-- - RLS activé avec politiques
-- - Trigger pour updated_at
-- ========================================
