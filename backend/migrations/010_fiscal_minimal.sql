-- Tables fiscales (version minimale)

CREATE TABLE IF NOT EXISTS fiscal_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  country TEXT,
  company_name TEXT,
  tax_id TEXT,
  vat_number TEXT,
  vat_regime TEXT,
  accounting_start_date DATE,
  fiscal_year_end TEXT,
  currency TEXT,
  invoice_prefix TEXT,
  next_invoice_number INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vat_rates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country TEXT,
  rate DECIMAL(5,2),
  category TEXT,
  description TEXT,
  valid_from DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fiscal_invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_number TEXT UNIQUE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  client_name TEXT,
  client_email TEXT,
  country TEXT,
  issue_date DATE,
  due_date DATE,
  amount_ht DECIMAL(12,2),
  vat_rate DECIMAL(5,2),
  vat_amount DECIMAL(12,2),
  amount_ttc DECIMAL(12,2),
  currency TEXT,
  payment_method TEXT,
  payment_date DATE,
  status TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fiscal_invoice_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES fiscal_invoices(id) ON DELETE CASCADE,
  line_number INTEGER,
  description TEXT,
  quantity DECIMAL(10,2),
  unit_price_ht DECIMAL(12,2),
  vat_rate DECIMAL(5,2),
  total_ht DECIMAL(12,2),
  total_vat DECIMAL(12,2),
  total_ttc DECIMAL(12,2),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vat_declarations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE,
  period_end DATE,
  declaration_type TEXT,
  country TEXT,
  vat_collected DECIMAL(12,2),
  vat_deductible DECIMAL(12,2),
  vat_to_pay DECIMAL(12,2),
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS withholding_tax (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE,
  period_end DATE,
  country TEXT,
  gross_amount DECIMAL(12,2),
  withholding_rate DECIMAL(5,2),
  withholding_amount DECIMAL(12,2),
  net_amount DECIMAL(12,2),
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS accounting_exports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  export_type TEXT,
  country TEXT,
  period_start DATE,
  period_end DATE,
  file_name TEXT,
  exported_at TIMESTAMP DEFAULT NOW()
);

-- Index simples
CREATE INDEX IF NOT EXISTS idx_fiscal_invoices_user ON fiscal_invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_fiscal_invoices_status ON fiscal_invoices(status);
CREATE INDEX IF NOT EXISTS idx_fiscal_invoice_lines_invoice ON fiscal_invoice_lines(invoice_id);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_user ON vat_declarations(user_id);
