-- ============================================
-- SCRIPT DE CORRECTION DU SCHÉMA (PHASE 12 & AUTRES)
-- ============================================

-- 1. Ajouter low_stock_alert à PRODUCTS
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS low_stock_alert BOOLEAN DEFAULT FALSE;

-- 2. Ajouter quality_score à LEADS
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0;

-- 3. Ajouter refund_rate à TRUST_SCORES
ALTER TABLE trust_scores 
ADD COLUMN IF NOT EXISTS refund_rate DECIMAL(5,2) DEFAULT 0;

-- 4. Ajouter account_id à PAYMENT_ACCOUNTS
ALTER TABLE payment_accounts 
ADD COLUMN IF NOT EXISTS account_id VARCHAR(255);

-- 5. Ajouter scan_method à QR_SCAN_EVENTS
ALTER TABLE qr_scan_events 
ADD COLUMN IF NOT EXISTS scan_method VARCHAR(50);

-- 6. Ajouter status à INTEGRATIONS
ALTER TABLE integrations 
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';

-- 7. Corriger CUSTOM_REPORTS (type nullable ou default)
ALTER TABLE custom_reports 
ALTER COLUMN type DROP NOT NULL;

-- 8. Corriger CONTENT_TEMPLATES (id default)
ALTER TABLE content_templates 
ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- 9. Corriger contrainte USERS (subscription_tier)
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_subscription_tier_check;
ALTER TABLE users ADD CONSTRAINT users_subscription_tier_check CHECK (subscription_tier IN ('free', 'pro', 'enterprise', 'Free', 'Pro', 'Enterprise'));

-- 10. Corriger contrainte WORKSPACE_MEMBERS (role)
ALTER TABLE workspace_members DROP CONSTRAINT IF EXISTS workspace_members_role_check;
ALTER TABLE workspace_members ADD CONSTRAINT workspace_members_role_check CHECK (role IN ('admin', 'member', 'viewer', 'manager', 'editor'));

-- 11. Créer tables manquantes si elles n'existent toujours pas (sécurité)
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(10,2),
    status VARCHAR(50),
    issued_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP,
    due_date TIMESTAMP,
    items JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS webhook_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhooks(id),
    event VARCHAR(100),
    payload JSONB,
    response_status INTEGER,
    response_body TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    scopes JSONB DEFAULT '[]',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255),
    window_start TIMESTAMP,
    request_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50),
    file_url TEXT,
    requested_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Activer RLS pour tout ce beau monde
DO $$
DECLARE
    tbl text;
BEGIN
    FOREACH tbl IN ARRAY ARRAY['products', 'leads', 'trust_scores', 'payment_accounts', 'qr_scan_events', 'integrations', 'custom_reports', 'content_templates', 'invoices', 'webhook_logs', 'api_keys', 'rate_limits', 'data_exports']
    LOOP
        IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = tbl) THEN
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
            EXECUTE format('DROP POLICY IF EXISTS "Enable all for %I" ON %I', tbl, tbl);
            EXECUTE format('CREATE POLICY "Enable all for %I" ON %I FOR ALL USING (true)', tbl, tbl);
        END IF;
    END LOOP;
END $$;
