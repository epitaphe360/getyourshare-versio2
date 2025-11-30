-- ============================================
-- MIGRATION 010: SYSTÈME FISCAL & COMPTABLE
-- Phase 5G - Multi-pays (Maroc, France, USA)
-- ============================================

-- 1. FISCAL SETTINGS (Configuration fiscale par utilisateur/entreprise)
CREATE TABLE IF NOT EXISTS fiscal_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  country VARCHAR(2) NOT NULL CHECK (country IN ('MA', 'FR', 'US')),
  company_name TEXT NOT NULL,
  tax_id TEXT NOT NULL, -- ICE (Maroc), SIRET (France), EIN (USA)
  vat_number TEXT, -- N° TVA intracommunautaire (France)
  vat_regime TEXT CHECK (vat_regime IN ('normal', 'franchise', 'mini-reel', 'auto-entrepreneur')),
  accounting_start_date DATE NOT NULL,
  fiscal_year_end TEXT DEFAULT '31/12',
  address TEXT,
  city TEXT,
  postal_code TEXT,
  phone TEXT,
  email TEXT,
  currency VARCHAR(3) DEFAULT 'MAD' CHECK (currency IN ('MAD', 'EUR', 'USD')),
  invoice_prefix TEXT DEFAULT 'FA', -- Préfixe factures (FA, FACT, INV)
  next_invoice_number INT DEFAULT 1,
  legal_mentions JSONB, -- Mentions légales personnalisées
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, country)
);

-- 2. VAT RATES (Taux de TVA par catégorie et pays)
CREATE TABLE IF NOT EXISTS vat_rates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country VARCHAR(2) NOT NULL CHECK (country IN ('MA', 'FR', 'US')),
  rate DECIMAL(5,2) NOT NULL,
  category TEXT NOT NULL, -- 'normal', 'intermediate', 'reduced', 'super_reduced', 'sales_tax'
  description TEXT,
  valid_from DATE NOT NULL,
  valid_to DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 3. INVOICES (Factures légales)
CREATE TABLE IF NOT EXISTS invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_number TEXT UNIQUE NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- L'utilisateur qui émet la facture
  client_name TEXT NOT NULL,
  client_email TEXT,
  client_address TEXT,
  client_tax_id TEXT, -- ICE/SIRET/EIN du client
  country TEXT NOT NULL CHECK (country IN ('MA', 'FR', 'US')),
  issue_date DATE NOT NULL,
  due_date DATE NOT NULL,
  amount_ht DECIMAL(12,2) NOT NULL, -- Hors taxes
  vat_rate DECIMAL(5,2) NOT NULL,
  vat_amount DECIMAL(12,2) NOT NULL,
  amount_ttc DECIMAL(12,2) NOT NULL, -- Toutes taxes comprises
  discount_percent DECIMAL(5,2) DEFAULT 0,
  discount_amount DECIMAL(12,2) DEFAULT 0,
  currency VARCHAR(3) DEFAULT 'MAD',
  payment_method TEXT CHECK (payment_method IN ('bank_transfer', 'credit_card', 'cash', 'check', 'other')),
  payment_date DATE,
  payment_reference TEXT,
  status TEXT CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled', 'refunded')) DEFAULT 'draft',
  legal_mentions JSONB, -- Mentions légales spécifiques à cette facture
  notes TEXT,
  pdf_url TEXT, -- URL du PDF généré
  sent_at TIMESTAMP,
  paid_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. INVOICE LINES (Lignes de facture)
CREATE TABLE IF NOT EXISTS invoice_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
  line_number INT NOT NULL,
  description TEXT NOT NULL,
  quantity DECIMAL(10,2) NOT NULL DEFAULT 1,
  unit_price_ht DECIMAL(12,2) NOT NULL,
  vat_rate DECIMAL(5,2) NOT NULL,
  discount_percent DECIMAL(5,2) DEFAULT 0,
  total_ht DECIMAL(12,2) NOT NULL, -- quantity * unit_price_ht * (1 - discount_percent/100)
  total_vat DECIMAL(12,2) NOT NULL,
  total_ttc DECIMAL(12,2) NOT NULL,
  product_reference TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(invoice_id, line_number)
);

-- 5. VAT DECLARATIONS (Déclarations de TVA - CA3, CA12, Quarterly)
CREATE TABLE IF NOT EXISTS vat_declarations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  declaration_type TEXT CHECK (declaration_type IN ('TVA_MONTHLY', 'CA3', 'CA12', 'QUARTERLY_US')) NOT NULL,
  country VARCHAR(2) NOT NULL CHECK (country IN ('MA', 'FR', 'US')),
  
  -- Montants
  vat_collected DECIMAL(12,2) NOT NULL DEFAULT 0, -- TVA collectée (ventes)
  vat_deductible DECIMAL(12,2) NOT NULL DEFAULT 0, -- TVA déductible (achats)
  vat_to_pay DECIMAL(12,2) NOT NULL DEFAULT 0, -- Solde à payer
  
  -- Détails par taux (JSONB pour flexibilité multi-taux)
  vat_by_rate JSONB, -- {20%: {collected: X, deductible: Y}, 10%: {...}}
  
  -- Chiffre d'affaires
  revenue_ht DECIMAL(12,2) DEFAULT 0,
  revenue_ttc DECIMAL(12,2) DEFAULT 0,
  
  -- Statut
  status TEXT CHECK (status IN ('draft', 'submitted', 'paid', 'late')) DEFAULT 'draft',
  submission_date DATE,
  payment_date DATE,
  payment_reference TEXT,
  
  -- Documents
  document_url TEXT, -- PDF de la déclaration
  receipt_url TEXT, -- Reçu de paiement
  
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, country, period_start, period_end)
);

-- 6. WITHHOLDING TAX (Retenue à la source - Influenceurs Maroc)
CREATE TABLE IF NOT EXISTS withholding_tax (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  country VARCHAR(2) DEFAULT 'MA' CHECK (country IN ('MA', 'FR', 'US')),
  
  -- Montants
  gross_amount DECIMAL(12,2) NOT NULL, -- Montant brut des commissions
  withholding_rate DECIMAL(5,2) NOT NULL DEFAULT 10.00, -- 10% au Maroc, 24% USA (backup withholding)
  withholding_amount DECIMAL(12,2) NOT NULL, -- Montant retenu
  net_amount DECIMAL(12,2) NOT NULL, -- Montant net versé
  
  -- Détails
  invoice_ids JSONB, -- Liste des factures concernées
  transactions_count INT DEFAULT 0,
  
  -- Statut
  status TEXT CHECK (status IN ('pending', 'withheld', 'paid', 'declared')) DEFAULT 'pending',
  payment_date DATE,
  declaration_date DATE,
  payment_reference TEXT,
  certificate_url TEXT, -- Attestation de retenue à la source
  
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. ACCOUNTING EXPORTS (Exports comptables - FEC, CSV, Sage, etc.)
CREATE TABLE IF NOT EXISTS accounting_exports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  export_type TEXT CHECK (export_type IN ('fec', 'csv', 'sage', 'ebp', 'cegid', 'excel')) NOT NULL,
  country VARCHAR(2) NOT NULL CHECK (country IN ('MA', 'FR', 'US')),
  
  -- Période
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  fiscal_year TEXT, -- Ex: "2024"
  
  -- Fichier
  file_url TEXT,
  file_name TEXT NOT NULL,
  file_size_kb INT,
  line_count INT,
  
  -- Options d'export (stockées en JSONB pour flexibilité)
  export_options JSONB, -- {delimiter: ';', encoding: 'ISO-8859-1', decimal: ','}
  
  -- Métadonnées
  exported_by UUID REFERENCES users(id) ON DELETE SET NULL,
  exported_at TIMESTAMP DEFAULT NOW(),
  downloaded_at TIMESTAMP,
  download_count INT DEFAULT 0,
  
  -- Validation FEC (pour France)
  is_fec_compliant BOOLEAN DEFAULT true,
  validation_errors JSONB,
  
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES POUR PERFORMANCE
-- ============================================

-- Fiscal Settings
CREATE INDEX IF NOT EXISTS idx_fiscal_settings_user ON fiscal_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_fiscal_settings_country ON fiscal_settings(country);

-- VAT Rates
CREATE INDEX IF NOT EXISTS idx_vat_rates_country ON vat_rates(country);
CREATE INDEX IF NOT EXISTS idx_vat_rates_validity ON vat_rates(valid_from, valid_to);

-- Invoices
-- Invoices
CREATE INDEX IF NOT EXISTS idx_invoices_user ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_country ON invoices(country);
CREATE INDEX IF NOT EXISTS idx_invoices_dates ON invoices(issue_date DESC, due_date);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_date ON invoices(payment_date);
-- Invoice Lines
CREATE INDEX IF NOT EXISTS idx_invoice_lines_invoice ON invoice_lines(invoice_id);

-- VAT Declarations
CREATE INDEX IF NOT EXISTS idx_vat_declarations_user ON vat_declarations(user_id);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_period ON vat_declarations(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_country ON vat_declarations(country);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_status ON vat_declarations(status);

-- Withholding Tax
CREATE INDEX IF NOT EXISTS idx_withholding_tax_user ON withholding_tax(user_id);
CREATE INDEX IF NOT EXISTS idx_withholding_tax_period ON withholding_tax(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_withholding_tax_status ON withholding_tax(status);

-- Accounting Exports
CREATE INDEX IF NOT EXISTS idx_accounting_exports_user ON accounting_exports(user_id);
CREATE INDEX IF NOT EXISTS idx_accounting_exports_period ON accounting_exports(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_accounting_exports_exported_by ON accounting_exports(exported_by);

-- ============================================
-- DONNÉES INITIALES: TAUX DE TVA
-- ============================================

-- MAROC - TVA (valides depuis 2023)
INSERT INTO vat_rates (country, rate, category, description, valid_from) VALUES
('MA', 20.00, 'normal', 'Taux normal TVA Maroc', '2023-01-01'),
('MA', 14.00, 'intermediate', 'Taux intermédiaire TVA Maroc', '2023-01-01'),
('MA', 10.00, 'reduced', 'Taux réduit TVA Maroc', '2023-01-01'),
('MA', 7.00, 'super_reduced', 'Taux super réduit TVA Maroc', '2023-01-01'),
('MA', 0.00, 'zero', 'Exonération TVA Maroc', '2023-01-01')
ON CONFLICT DO NOTHING;

-- FRANCE - TVA (valides depuis 2023)
INSERT INTO vat_rates (country, rate, category, description, valid_from) VALUES
('FR', 20.00, 'normal', 'Taux normal TVA France', '2023-01-01'),
('FR', 10.00, 'intermediate', 'Taux intermédiaire TVA France', '2023-01-01'),
('FR', 5.50, 'reduced', 'Taux réduit TVA France', '2023-01-01'),
('FR', 2.10, 'super_reduced', 'Taux super réduit TVA France', '2023-01-01'),
('FR', 0.00, 'zero', 'Franchise en base TVA France', '2023-01-01')
ON CONFLICT DO NOTHING;

-- USA - Sales Tax (taux variable par État, exemples principaux)
INSERT INTO vat_rates (country, rate, category, description, valid_from) VALUES
('US', 7.25, 'sales_tax', 'California Sales Tax', '2023-01-01'),
('US', 6.00, 'sales_tax', 'New York Sales Tax', '2023-01-01'),
('US', 6.25, 'sales_tax', 'Texas Sales Tax', '2023-01-01'),
('US', 6.00, 'sales_tax', 'Florida Sales Tax', '2023-01-01'),
('US', 0.00, 'zero', 'No Sales Tax (Delaware, Oregon, etc.)', '2023-01-01')
ON CONFLICT DO NOTHING;

-- ============================================
-- TRIGGERS POUR AUTO-UPDATE TIMESTAMPS
-- ============================================

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_fiscal_settings_modtime
BEFORE UPDATE ON fiscal_settings
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_invoices_modtime
BEFORE UPDATE ON invoices
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_vat_declarations_modtime
BEFORE UPDATE ON vat_declarations
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_withholding_tax_modtime
BEFORE UPDATE ON withholding_tax
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- ============================================
-- COMMENTAIRES POUR DOCUMENTATION
-- ============================================

COMMENT ON TABLE fiscal_settings IS 'Configuration fiscale par utilisateur/entreprise (multi-pays)';
COMMENT ON TABLE vat_rates IS 'Taux de TVA/Sales Tax par pays et catégorie avec historique';
COMMENT ON TABLE invoices IS 'Factures légales avec conformité ICE/SIRET/EIN';
COMMENT ON TABLE invoice_lines IS 'Lignes de facture détaillées avec TVA ligne par ligne';
COMMENT ON TABLE vat_declarations IS 'Déclarations de TVA (CA3/CA12/Quarterly) multi-pays';
COMMENT ON TABLE withholding_tax IS 'Retenue à la source (Maroc 10%, USA backup withholding 24%)';
COMMENT ON TABLE accounting_exports IS 'Exports comptables (FEC France obligatoire, CSV, Sage, EBP, Cegid)';

-- ============================================
-- FIN MIGRATION
-- ============================================
-- Migration 010: Système Fiscal & Comptable (7 tables + 15 taux TVA)
