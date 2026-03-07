-- PARTIE 3 : CRÉATION DES TABLES MANQUANTES ET SÉCURITÉ
-- Exécutez ce bloc en dernier

-- FIX CRITIQUE 1: Contrainte FK users_referred_by_fkey
-- Permet la suppression d'utilisateurs qui ont parrainé d'autres
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_referred_by_fkey;
ALTER TABLE users ADD CONSTRAINT users_referred_by_fkey 
  FOREIGN KEY (referred_by) REFERENCES users(id) ON DELETE SET NULL;

-- FIX CRITIQUE 2: Colonne reviews_count manquante
ALTER TABLE trust_scores ADD COLUMN IF NOT EXISTS reviews_count INTEGER DEFAULT 0;

-- FIX CRITIQUE 3: Colonne user_id manquante
ALTER TABLE qr_scan_events ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- FIX CRITIQUE 4: Colonne marchand_id nullable
ALTER TABLE leads ALTER COLUMN marchand_id DROP NOT NULL;

-- FIX CRITIQUE 5: Colonne credentials nullable
ALTER TABLE integrations ALTER COLUMN credentials DROP NOT NULL;

-- FIX CRITIQUE 6: Colonne category nullable
ALTER TABLE content_templates ALTER COLUMN category DROP NOT NULL;

-- TABLE CRITIQUE: disputes pour support client
CREATE TABLE IF NOT EXISTS disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID,
    raised_by UUID REFERENCES users(id),
    against UUID REFERENCES users(id),
    reason TEXT,
    status VARCHAR(50) DEFAULT 'open',
    resolution TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- TABLE: promotions pour marketing
CREATE TABLE IF NOT EXISTS promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(20), -- percentage, fixed
    discount_value DECIMAL(10,2),
    min_purchase DECIMAL(10,2),
    max_uses INTEGER,
    uses_count INTEGER DEFAULT 0,
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- TABLE: live_streams pour streaming
CREATE TABLE IF NOT EXISTS live_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id UUID REFERENCES users(id),
    title VARCHAR(255),
    description TEXT,
    stream_url TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    viewers_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- TABLE: user_badges pour gamification
ALTER TABLE user_badges ADD COLUMN IF NOT EXISTS badge_icon TEXT;

-- TABLE: report_runs pour reporting avancé
CREATE TABLE IF NOT EXISTS report_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES custom_reports(id),
    status VARCHAR(50),
    result_url TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- TABLE: workspace_comments pour collaboration
CREATE TABLE IF NOT EXISTS workspace_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    user_id UUID REFERENCES users(id),
    content TEXT,
    parent_id UUID REFERENCES workspace_comments(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

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

-- Activer RLS
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
