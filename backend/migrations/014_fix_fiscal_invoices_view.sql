-- ============================================
-- MIGRATION 014: Corriger fiscal_invoices (TABLE → VUE)
-- ============================================

-- ÉTAPE 1: Vérifier si fiscal_invoices est une table avec données
-- Si elle contient des données importantes, décommenter les lignes ci-dessous:
-- INSERT INTO invoices 
-- SELECT * FROM fiscal_invoices 
-- WHERE id NOT IN (SELECT id FROM invoices);

-- ÉTAPE 2: Supprimer la table fiscal_invoices
DROP TABLE IF EXISTS fiscal_invoices CASCADE;

-- ÉTAPE 3: Ajouter les colonnes manquantes à invoices (si pas déjà fait)
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

-- ÉTAPE 4: Créer fiscal_invoices comme VUE (pas table)
CREATE OR REPLACE VIEW fiscal_invoices AS 
SELECT * FROM invoices;

-- ÉTAPE 5: Index pour optimisation
CREATE INDEX IF NOT EXISTS idx_invoices_payment_id ON invoices(payment_id);
CREATE INDEX IF NOT EXISTS idx_invoices_stripe_intent ON invoices(stripe_payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_invoices_paypal_order ON invoices(paypal_order_id);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);

-- ÉTAPE 6: Tables complémentaires
CREATE TABLE IF NOT EXISTS bank_reconciliations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  bank_name TEXT NOT NULL,
  account_number TEXT,
  statement_date DATE NOT NULL,
  statement_file_url TEXT,
  total_transactions INTEGER DEFAULT 0,
  matched_transactions INTEGER DEFAULT 0,
  total_amount DECIMAL(12,2) DEFAULT 0,
  matched_amount DECIMAL(12,2) DEFAULT 0,
  status TEXT DEFAULT 'pending',
  reconciled_at TIMESTAMP,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

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
  used_at TIMESTAMP
);

-- ÉTAPE 7: Contraintes validation (avec gestion d'erreur si existe déjà)
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint 
    WHERE conname = 'check_payment_status' 
    AND conrelid = 'invoices'::regclass
  ) THEN
    ALTER TABLE invoices 
    ADD CONSTRAINT check_payment_status 
    CHECK (payment_status IN ('unpaid', 'pending', 'paid', 'failed', 'refunded', 'partially_refunded'));
  END IF;
END $$;

-- ÉTAPE 8: Index tables nouvelles
CREATE INDEX IF NOT EXISTS idx_bank_reconciliations_user ON bank_reconciliations(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_invoice ON payment_links(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_payment_id ON payment_links(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_status ON payment_links(status);

-- ============================================
-- VÉRIFICATIONS
-- ============================================

-- Vérifier que fiscal_invoices est maintenant une vue
SELECT 
  table_name, 
  table_type,
  CASE 
    WHEN table_type = 'VIEW' THEN '✅ VUE (Correct)'
    WHEN table_type = 'BASE TABLE' THEN '❌ TABLE (Incorrect)'
  END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'fiscal_invoices';

-- Vérifier les colonnes payment
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name LIKE '%payment%'
ORDER BY ordinal_position;

-- ============================================
-- FIN MIGRATION 014
-- ============================================
