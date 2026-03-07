-- FICHIER COMPLET POUR CRÉER TOUTES LES TABLES MANQUANTES POUR LES TESTS
-- Exécutez ce script dans Supabase pour activer tous les tests ignorés

-- 1. TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50), -- 'credit', 'debit', 'commission', 'payout', 'refund'
    amount DECIMAL(10,2),
    status VARCHAR(50), -- 'pending', 'completed', 'failed'
    description TEXT,
    reference_id UUID, -- ID de la commande, du payout, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. KYC VERIFICATIONS (Version compatible test)
DROP TABLE IF EXISTS kyc_verifications CASCADE;
CREATE TABLE kyc_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50),
    document_type VARCHAR(50),
    document_number VARCHAR(100),
    full_name VARCHAR(255),
    date_of_birth DATE,
    address TEXT,
    phone_number VARCHAR(50),
    verification_code VARCHAR(50),
    submitted_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. CAMPAIGNS
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    name VARCHAR(255),
    description TEXT,
    budget DECIMAL(10,2),
    spent DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(50), -- 'draft', 'active', 'paused', 'completed'
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    target_audience JSONB,
    kpis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. CAMPAIGN INFLUENCERS
CREATE TABLE IF NOT EXISTS campaign_influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    influencer_id UUID REFERENCES users(id),
    commission_rate DECIMAL(5,2),
    status VARCHAR(50), -- 'invited', 'active', 'declined'
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. LEADS
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES users(id),
    merchant_id UUID REFERENCES users(id),
    service_id UUID REFERENCES services(id),
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    status VARCHAR(50), -- 'new', 'contacted', 'qualified', 'converted', 'lost'
    quality_score INTEGER,
    source VARCHAR(50),
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. TRUST SCORES
CREATE TABLE IF NOT EXISTS trust_scores (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    score INTEGER DEFAULT 0,
    verified_email BOOLEAN DEFAULT FALSE,
    verified_phone BOOLEAN DEFAULT FALSE,
    verified_social BOOLEAN DEFAULT FALSE,
    verified_business BOOLEAN DEFAULT FALSE,
    kyc_completed BOOLEAN DEFAULT FALSE,
    successful_conversions INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    successful_orders INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    refund_rate DECIMAL(5,2) DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,
    badges JSONB DEFAULT '[]',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. PAYMENT ACCOUNTS
CREATE TABLE IF NOT EXISTS payment_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50), -- 'bank_account', 'mobile_money', 'stripe', 'paypal'
    provider VARCHAR(50),
    account_holder VARCHAR(255),
    account_number VARCHAR(255),
    account_id VARCHAR(255),
    bank_name VARCHAR(255),
    is_default BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. PAYOUT PREFERENCES
CREATE TABLE IF NOT EXISTS payout_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    min_payout_amount DECIMAL(10,2) DEFAULT 50.00,
    payout_frequency VARCHAR(50) DEFAULT 'monthly', -- 'weekly', 'monthly', 'manual'
    auto_payout BOOLEAN DEFAULT FALSE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. INVOICES
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    invoice_number VARCHAR(50) UNIQUE,
    amount DECIMAL(10,2),
    status VARCHAR(50), -- 'draft', 'sent', 'paid', 'overdue', 'cancelled'
    issued_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    due_date TIMESTAMP WITH TIME ZONE,
    items JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. WEBHOOKS
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    url TEXT NOT NULL,
    events JSONB, -- Array of event names
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. WEBHOOK LOGS
CREATE TABLE IF NOT EXISTS webhook_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhooks(id),
    event_type VARCHAR(100),
    payload JSONB,
    status_code INTEGER,
    response TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 12. API KEYS
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key VARCHAR(255) UNIQUE,
    secret_hash VARCHAR(255),
    name VARCHAR(255),
    permissions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 13. RATE LIMITS
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255),
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE,
    limit_count INTEGER, -- Renamed from 'limit' to avoid reserved keyword issues if any
    blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 14. DATA EXPORTS
CREATE TABLE IF NOT EXISTS data_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    export_type VARCHAR(50),
    format VARCHAR(20),
    filters JSONB,
    status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    file_url TEXT,
    row_count INTEGER,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 15. SECURITY EVENTS
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(100),
    risk_score INTEGER,
    reason VARCHAR(255),
    ip_address VARCHAR(45),
    blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 16. PROMOTIONS
CREATE TABLE IF NOT EXISTS promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    code VARCHAR(50),
    discount_type VARCHAR(20), -- 'percentage', 'fixed'
    discount_value DECIMAL(10,2),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_limit INTEGER,
    used_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 17. COMMERCIAL OBJECTIVES
CREATE TABLE IF NOT EXISTS commercial_objectives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID REFERENCES users(id),
    period VARCHAR(50), -- 'Q1-2024', '2024-01', etc.
    target_revenue DECIMAL(12,2),
    target_merchants INTEGER,
    target_subscriptions INTEGER,
    current_revenue DECIMAL(12,2) DEFAULT 0,
    current_merchants INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 18. REFERRAL CODES
CREATE TABLE IF NOT EXISTS referral_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    code VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 19. LIVE STREAMS
CREATE TABLE IF NOT EXISTS live_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES users(id),
    platform VARCHAR(50), -- 'facebook', 'tiktok', 'instagram', 'youtube'
    title VARCHAR(255),
    description TEXT,
    stream_url TEXT,
    stream_key VARCHAR(255),
    status VARCHAR(50), -- 'scheduled', 'live', 'ended'
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    viewers_count INTEGER DEFAULT 0,
    peak_viewers INTEGER DEFAULT 0,
    products_featured JSONB, -- Array of product IDs
    total_duration INTEGER, -- Seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 20. USER BADGES
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    badge_type VARCHAR(50),
    badge_name VARCHAR(100),
    badge_icon VARCHAR(50), -- Emoji or URL
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    criteria_met JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 21. DISPUTES
CREATE TABLE IF NOT EXISTS disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES transactions(id),
    user_id UUID REFERENCES users(id), -- Celui qui ouvre le litige
    merchant_id UUID REFERENCES users(id), -- Contre qui
    type VARCHAR(50),
    status VARCHAR(50), -- 'open', 'resolved', 'closed'
    amount DECIMAL(10,2),
    reason TEXT,
    resolution TEXT,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 22. WORKSPACES
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id),
    name VARCHAR(255),
    description TEXT,
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 23. WORKSPACE MEMBERS
CREATE TABLE IF NOT EXISTS workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50), -- 'admin', 'manager', 'member'
    permissions JSONB,
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    joined_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 24. WORKSPACE COMMENTS
CREATE TABLE IF NOT EXISTS workspace_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    user_id UUID REFERENCES users(id),
    entity_type VARCHAR(50), -- 'campaign', 'product', etc.
    entity_id UUID,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 25. INTEGRATIONS
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    platform VARCHAR(50), -- 'shopify', 'woocommerce', etc.
    shop_url VARCHAR(255),
    access_token VARCHAR(255),
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    status VARCHAR(50),
    settings JSONB,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 26. INTEGRATION SYNC LOGS
CREATE TABLE IF NOT EXISTS integration_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES integrations(id),
    sync_type VARCHAR(50),
    status VARCHAR(50),
    items_synced INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 27. SOCIAL MEDIA ACCOUNTS
CREATE TABLE IF NOT EXISTS social_media_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    platform VARCHAR(50),
    handle VARCHAR(255),
    access_token VARCHAR(255),
    followers_count INTEGER,
    status VARCHAR(50),
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 28. QR SCAN EVENTS
CREATE TABLE IF NOT EXISTS qr_scan_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    link_id UUID REFERENCES tracking_links(id),
    scan_method VARCHAR(50),
    device_info JSONB,
    location JSONB,
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 29. NFC TAP EVENTS
CREATE TABLE IF NOT EXISTS nfc_tap_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    link_id UUID REFERENCES tracking_links(id),
    nfc_tag_id VARCHAR(100),
    device_info JSONB,
    tapped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 30. OFFLINE ACTIONS
CREATE TABLE IF NOT EXISTS offline_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action_type VARCHAR(50),
    payload JSONB,
    synced BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 31. CUSTOM REPORTS
CREATE TABLE IF NOT EXISTS custom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    type VARCHAR(50),
    filters JSONB,
    schedule VARCHAR(50),
    recipients JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 32. REPORT RUNS
CREATE TABLE IF NOT EXISTS report_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES custom_reports(id),
    status VARCHAR(50),
    file_url TEXT,
    data JSONB,
    generated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 33. CONTENT TEMPLATES
CREATE TABLE IF NOT EXISTS content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    type VARCHAR(50), -- 'email', 'sms', 'social'
    subject VARCHAR(255),
    content TEXT,
    variables JSONB,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 34. MEDIA LIBRARY
CREATE TABLE IF NOT EXISTS media_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50), -- 'image', 'video', 'document'
    filename VARCHAR(255),
    url TEXT,
    size_bytes BIGINT,
    metadata JSONB,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 35. SEO METADATA
CREATE TABLE IF NOT EXISTS seo_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    meta_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords JSONB,
    og_image TEXT,
    canonical_url TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 36. USER 2FA
CREATE TABLE IF NOT EXISTS user_2fa (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    enabled BOOLEAN DEFAULT FALSE,
    method VARCHAR(50), -- 'totp', 'sms', 'email'
    secret VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 37. USER SESSIONS
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_token VARCHAR(255),
    ip_address VARCHAR(45),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 38. SALES ASSIGNMENTS
CREATE TABLE IF NOT EXISTS sales_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID REFERENCES users(id),
    merchant_id UUID REFERENCES users(id),
    status VARCHAR(50),
    commission_rate DECIMAL(5,2),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 39. AFFILIATION REQUESTS
CREATE TABLE IF NOT EXISTS affiliation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES users(id),
    merchant_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    status VARCHAR(50), -- 'pending', 'active', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ACTIVER RLS POUR TOUTES LES TABLES
DO $$
DECLARE
    tbl text;
BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'transactions', 'kyc_verifications', 'campaigns', 'campaign_influencers', 'leads', 
        'trust_scores', 'payment_accounts', 'payout_preferences', 'invoices', 'webhooks', 
        'webhook_logs', 'api_keys', 'rate_limits', 'data_exports', 'security_events', 
        'promotions', 'commercial_objectives', 'referral_codes', 'live_streams', 'user_badges', 
        'disputes', 'workspaces', 'workspace_members', 'workspace_comments', 'integrations', 
        'integration_sync_logs', 'social_media_accounts', 'qr_scan_events', 'nfc_tap_events', 
        'offline_actions', 'custom_reports', 'report_runs', 'content_templates', 'media_library', 
        'seo_metadata', 'user_2fa', 'user_sessions', 'sales_assignments', 'affiliation_requests'
    ]
    LOOP
        IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = tbl) THEN
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
            EXECUTE format('DROP POLICY IF EXISTS "Enable all for %I" ON %I', tbl, tbl);
            EXECUTE format('CREATE POLICY "Enable all for %I" ON %I FOR ALL USING (true)', tbl, tbl);
        END IF;
    END LOOP;
END $$;
