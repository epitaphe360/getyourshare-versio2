-- ============================================
-- MIGRATION 013: Ajout colonnes paiement et webhooks
-- ============================================

-- Ajouter colonnes manquantes à la table invoices
ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS payment_id TEXT,
ADD COLUMN IF NOT EXISTS payment_provider TEXT,
ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'unpaid',
ADD COLUMN IF NOT EXISTS stripe_payment_intent_id TEXT,
ADD COLUMN IF NOT EXISTS paypal_order_id TEXT,
ADD COLUMN IF NOT EXISTS payment_link TEXT,
ADD COLUMN IF NOT EXISTS webhook_received_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(12,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS refund_reason TEXT,
ADD COLUMN IF NOT EXISTS bank_reconciliation_id UUID,
ADD COLUMN IF NOT EXISTS reminder_sent_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_reminder_sent_at TIMESTAMP;

-- Créer vue fiscal_invoices (alias pour compatibilité)
CREATE OR REPLACE VIEW fiscal_invoices AS 
SELECT * FROM invoices;

-- Index pour optimiser les requêtes webhooks
CREATE INDEX IF NOT EXISTS idx_invoices_payment_id ON invoices(payment_id);
CREATE INDEX IF NOT EXISTS idx_invoices_stripe_intent ON invoices(stripe_payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_invoices_paypal_order ON invoices(paypal_order_id);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);

-- Table reconciliation bancaire (si pas existante)
CREATE TABLE IF NOT EXISTS bank_reconciliations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  bank_name TEXT NOT NULL,
  account_number TEXT,
  statement_date DATE NOT NULL,
  statement_file_url TEXT,
  total_transactions INTEGER DEFAULT 0,
  matched_transactions INTEGER DEFAULT 0,
  unmatched_transactions INTEGER DEFAULT 0,
  total_amount DECIMAL(12,2) DEFAULT 0,
  matched_amount DECIMAL(12,2) DEFAULT 0,
  unmatched_amount DECIMAL(12,2) DEFAULT 0,
  status TEXT DEFAULT 'pending',
  reconciled_at TIMESTAMP,
  reconciled_by UUID REFERENCES users(id) ON DELETE SET NULL,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Table transactions bancaires importées
CREATE TABLE IF NOT EXISTS bank_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reconciliation_id UUID REFERENCES bank_reconciliations(id) ON DELETE CASCADE,
  transaction_date DATE NOT NULL,
  value_date DATE,
  description TEXT NOT NULL,
  reference TEXT,
  debit_amount DECIMAL(12,2) DEFAULT 0,
  credit_amount DECIMAL(12,2) DEFAULT 0,
  balance DECIMAL(12,2),
  currency TEXT DEFAULT 'MAD',
  matched_invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
  match_confidence DECIMAL(3,2),
  match_method TEXT,
  is_matched BOOLEAN DEFAULT FALSE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table liens de paiement
CREATE TABLE IF NOT EXISTS payment_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
  payment_provider TEXT NOT NULL,
  payment_link TEXT NOT NULL,
  payment_id TEXT UNIQUE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  currency TEXT DEFAULT 'MAD',
  status TEXT DEFAULT 'pending',
  expires_at TIMESTAMP,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  used_at TIMESTAMP,
  cancelled_at TIMESTAMP
);

-- Index tables nouvelles
CREATE INDEX IF NOT EXISTS idx_bank_reconciliations_user ON bank_reconciliations(user_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_reconciliation ON bank_transactions(reconciliation_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_matched ON bank_transactions(is_matched);
CREATE INDEX IF NOT EXISTS idx_payment_links_invoice ON payment_links(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_payment_id ON payment_links(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_status ON payment_links(status);

-- Triggers updated_at
CREATE TRIGGER trg_bank_reconciliations_updated 
BEFORE UPDATE ON bank_reconciliations
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Contraintes validation
ALTER TABLE invoices 
ADD CONSTRAINT check_payment_status 
CHECK (payment_status IN ('unpaid', 'pending', 'paid', 'failed', 'refunded', 'partially_refunded'));

ALTER TABLE invoices
ADD CONSTRAINT check_refund_amount_positive
CHECK (refund_amount >= 0);

ALTER TABLE invoices
ADD CONSTRAINT check_refund_not_exceeds_amount
CHECK (refund_amount <= amount_ttc);

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON COLUMN invoices.payment_id IS 'ID unique du paiement (Stripe/PayPal)';
COMMENT ON COLUMN invoices.payment_provider IS 'Fournisseur: stripe, paypal, bank_transfer, cash';
COMMENT ON COLUMN invoices.payment_status IS 'Statut: unpaid, pending, paid, failed, refunded';
COMMENT ON COLUMN invoices.stripe_payment_intent_id IS 'Stripe PaymentIntent ID';
COMMENT ON COLUMN invoices.paypal_order_id IS 'PayPal Order ID';
COMMENT ON COLUMN invoices.payment_link IS 'URL lien paiement envoyé au client';
COMMENT ON COLUMN invoices.webhook_received_at IS 'Date réception webhook paiement';
COMMENT ON COLUMN invoices.bank_reconciliation_id IS 'Référence rapprochement bancaire';
COMMENT ON COLUMN invoices.reminder_sent_count IS 'Nombre relances envoyées';
COMMENT ON COLUMN invoices.last_reminder_sent_at IS 'Date dernière relance';

COMMENT ON TABLE bank_reconciliations IS 'Rapprochements bancaires mensuels';
COMMENT ON TABLE bank_transactions IS 'Transactions importées depuis relevés bancaires';
COMMENT ON TABLE payment_links IS 'Liens paiement Stripe/PayPal générés';

-- ============================================
-- FIN MIGRATION 013
-- ============================================
