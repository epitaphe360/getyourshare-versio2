-- ============================================
-- MIGRATION 010: SYSTÈME FISCAL (Version Simple)
-- ============================================

-- 1. Configuration fiscale
CREATE TABLE IF NOT EXISTS fiscal_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  country TEXT NOT NULL,
  company_name TEXT NOT NULL,
  tax_id TEXT,
  vat_number TEXT,
  vat_regime TEXT,
  accounting_start_date DATE DEFAULT CURRENT_DATE,
  fiscal_year_end TEXT DEFAULT '31/12',
  address TEXT,
  city TEXT,
  postal_code TEXT,
  phone TEXT,
  email TEXT,
  currency TEXT DEFAULT 'MAD',
  invoice_prefix TEXT DEFAULT 'FA',
  next_invoice_number INTEGER DEFAULT 1,
  legal_mentions JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Taux de TVA
CREATE TABLE IF NOT EXISTS vat_rates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country TEXT NOT NULL,
  rate DECIMAL(5,2) NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  valid_from DATE DEFAULT CURRENT_DATE,
  valid_to DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Factures
CREATE TABLE IF NOT EXISTS invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_number TEXT UNIQUE NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  client_name TEXT NOT NULL,
  client_email TEXT,
  client_address TEXT,
  client_tax_id TEXT,
  country TEXT NOT NULL,
  issue_date DATE DEFAULT CURRENT_DATE,
  due_date DATE,
  amount_ht DECIMAL(12,2) NOT NULL,
  vat_rate DECIMAL(5,2) NOT NULL,
  vat_amount DECIMAL(12,2) NOT NULL,
  amount_ttc DECIMAL(12,2) NOT NULL,
  discount_percent DECIMAL(5,2) DEFAULT 0,
  discount_amount DECIMAL(12,2) DEFAULT 0,
  currency TEXT DEFAULT 'MAD',
  payment_method TEXT,
  payment_date DATE,
  payment_reference TEXT,
  status TEXT DEFAULT 'draft',
  legal_mentions JSONB,
  notes TEXT,
  pdf_url TEXT,
  sent_at TIMESTAMP,
  paid_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Lignes de facture
CREATE TABLE IF NOT EXISTS invoice_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
  line_number INTEGER NOT NULL,
  description TEXT NOT NULL,
  quantity DECIMAL(10,2) DEFAULT 1,
  unit_price_ht DECIMAL(12,2) NOT NULL,
  vat_rate DECIMAL(5,2) NOT NULL,
  discount_percent DECIMAL(5,2) DEFAULT 0,
  total_ht DECIMAL(12,2) NOT NULL,
  total_vat DECIMAL(12,2) NOT NULL,
  total_ttc DECIMAL(12,2) NOT NULL,
  product_reference TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Déclarations TVA
CREATE TABLE IF NOT EXISTS vat_declarations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  declaration_type TEXT NOT NULL,
  country TEXT NOT NULL,
  vat_collected DECIMAL(12,2) DEFAULT 0,
  vat_deductible DECIMAL(12,2) DEFAULT 0,
  vat_to_pay DECIMAL(12,2) DEFAULT 0,
  vat_by_rate JSONB,
  revenue_ht DECIMAL(12,2) DEFAULT 0,
  revenue_ttc DECIMAL(12,2) DEFAULT 0,
  status TEXT DEFAULT 'draft',
  submission_date DATE,
  payment_date DATE,
  payment_reference TEXT,
  document_url TEXT,
  receipt_url TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. Retenue à la source
CREATE TABLE IF NOT EXISTS withholding_tax (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  country TEXT DEFAULT 'MA',
  gross_amount DECIMAL(12,2) NOT NULL,
  withholding_rate DECIMAL(5,2) DEFAULT 10.00,
  withholding_amount DECIMAL(12,2) NOT NULL,
  net_amount DECIMAL(12,2) NOT NULL,
  invoice_ids JSONB,
  transactions_count INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
  payment_date DATE,
  declaration_date DATE,
  payment_reference TEXT,
  certificate_url TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. Exports comptables
CREATE TABLE IF NOT EXISTS accounting_exports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  export_type TEXT NOT NULL,
  country TEXT NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  fiscal_year TEXT,
  file_url TEXT,
  file_name TEXT NOT NULL,
  file_size_kb INTEGER,
  line_count INTEGER,
  export_options JSONB,
  exported_by UUID REFERENCES users(id) ON DELETE SET NULL,
  exported_at TIMESTAMP DEFAULT NOW(),
  downloaded_at TIMESTAMP,
  download_count INTEGER DEFAULT 0,
  is_fec_compliant BOOLEAN DEFAULT TRUE,
  validation_errors JSONB,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_fiscal_settings_user ON fiscal_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_user ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_country ON invoices(country);
CREATE INDEX IF NOT EXISTS idx_invoice_lines_invoice ON invoice_lines(invoice_id);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_user ON vat_declarations(user_id);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_period ON vat_declarations(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_withholding_tax_user ON withholding_tax(user_id);
CREATE INDEX IF NOT EXISTS idx_accounting_exports_user ON accounting_exports(user_id);

-- ============================================
-- TRIGGERS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_fiscal_settings_updated 
BEFORE UPDATE ON fiscal_settings
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_invoices_updated 
BEFORE UPDATE ON invoices
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_vat_declarations_updated 
BEFORE UPDATE ON vat_declarations
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_withholding_tax_updated 
BEFORE UPDATE ON withholding_tax
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- DONNÉES INITIALES: TAUX TVA
-- ============================================

INSERT INTO vat_rates (country, rate, category, description) VALUES
-- MAROC
('MA', 20.00, 'standard', 'TVA normale Maroc'),
('MA', 14.00, 'intermediate', 'TVA intermédiaire Maroc'),
('MA', 10.00, 'reduced', 'TVA réduite Maroc'),
('MA', 7.00, 'super_reduced', 'TVA super réduite Maroc'),
('MA', 0.00, 'zero', 'Exonération TVA Maroc'),

-- FRANCE
('FR', 20.00, 'standard', 'TVA normale France'),
('FR', 10.00, 'intermediate', 'TVA intermédiaire France'),
('FR', 5.50, 'reduced', 'TVA réduite France'),
('FR', 2.10, 'super_reduced', 'TVA super réduite France'),
('FR', 0.00, 'zero', 'Franchise TVA France'),

-- USA
('US', 7.25, 'california', 'Sales Tax California'),
('US', 6.00, 'texas', 'Sales Tax Texas'),
('US', 6.25, 'illinois', 'Sales Tax Illinois'),
('US', 6.00, 'florida', 'Sales Tax Florida'),
('US', 0.00, 'zero', 'No Sales Tax')
ON CONFLICT DO NOTHING;
