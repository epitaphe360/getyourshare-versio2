-- SCRIPT DE RÉPARATION ULTIME : RECRÉATION FORCÉE DE TOUTES LES TABLES DE TEST
-- Ce script supprime et recrée toutes les tables avec le schéma EXACT attendu par le script Python.
-- ATTENTION : Cela effacera les données de test existantes dans ces tables.

-- ==============================================================================
-- 1. NETTOYAGE (DROP)
-- Ordre optimisé pour éviter les deadlocks (enfants d'abord, parents ensuite)
-- ==============================================================================

-- Tables dépendantes (Niveau 2)
DROP TABLE IF EXISTS disputes CASCADE;
DROP TABLE IF EXISTS campaign_influencers CASCADE;
DROP TABLE IF EXISTS webhook_logs CASCADE;
DROP TABLE IF EXISTS workspace_members CASCADE;
DROP TABLE IF EXISTS workspace_comments CASCADE;
DROP TABLE IF EXISTS integration_sync_logs CASCADE;
DROP TABLE IF EXISTS report_runs CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS seo_metadata CASCADE;
DROP TABLE IF EXISTS affiliation_requests CASCADE;
DROP TABLE IF EXISTS qr_scan_events CASCADE;
DROP TABLE IF EXISTS nfc_tap_events CASCADE;
DROP TABLE IF EXISTS sales_assignments CASCADE;

-- Tables principales (Niveau 1)
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS kyc_verifications CASCADE;
DROP TABLE IF EXISTS campaigns CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS trust_scores CASCADE;
DROP TABLE IF EXISTS payment_accounts CASCADE;
DROP TABLE IF EXISTS payout_preferences CASCADE;
DROP TABLE IF EXISTS webhooks CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS rate_limits CASCADE;
DROP TABLE IF EXISTS data_exports CASCADE;
DROP TABLE IF EXISTS security_events CASCADE;
DROP TABLE IF EXISTS promotions CASCADE;
DROP TABLE IF EXISTS commercial_objectives CASCADE;
DROP TABLE IF EXISTS referral_codes CASCADE;
DROP TABLE IF EXISTS live_streams CASCADE;
DROP TABLE IF EXISTS user_badges CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;
DROP TABLE IF EXISTS integrations CASCADE;
DROP TABLE IF EXISTS social_media_accounts CASCADE;
DROP TABLE IF EXISTS offline_actions CASCADE;
DROP TABLE IF EXISTS custom_reports CASCADE;
DROP TABLE IF EXISTS content_templates CASCADE;
DROP TABLE IF EXISTS media_library CASCADE;
DROP TABLE IF EXISTS user_2fa CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS analytics_reports CASCADE;
DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS payment_integrations CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS email_campaigns CASCADE;
DROP TABLE IF EXISTS sms_campaigns CASCADE;
DROP TABLE IF EXISTS product_collections CASCADE;
DROP TABLE IF EXISTS wishlists CASCADE;
DROP TABLE IF EXISTS shipments CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS coupons CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS events CASCADE;

-- ==============================================================================
-- 2. RECRÉATION (CREATE)
-- ==============================================================================

-- 1. TRANSACTIONS
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50),
    amount DECIMAL(10,2),
    currency VARCHAR(10),
    status VARCHAR(50),
    description TEXT,
    reference VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. KYC VERIFICATIONS
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
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    name VARCHAR(255),
    description TEXT,
    budget DECIMAL(10,2),
    spent DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(50),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    target_audience JSONB,
    kpis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. CAMPAIGN INFLUENCERS
CREATE TABLE campaign_influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    influencer_id UUID REFERENCES users(id),
    commission_rate DECIMAL(5,2),
    status VARCHAR(50),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. LEADS
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES users(id),
    merchant_id UUID REFERENCES users(id),
    service_id UUID REFERENCES services(id),
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    status VARCHAR(50),
    quality_score INTEGER,
    source VARCHAR(50),
    notes TEXT,
    metadata JSONB,
    contacted_at TIMESTAMP WITH TIME ZONE,
    qualified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. TRUST SCORES
CREATE TABLE trust_scores (
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
CREATE TABLE payment_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50),
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
CREATE TABLE payout_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    min_payout_amount DECIMAL(10,2) DEFAULT 50.00,
    payout_frequency VARCHAR(50) DEFAULT 'monthly',
    auto_payout BOOLEAN DEFAULT FALSE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. INVOICES
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    subscription_id UUID,
    invoice_number VARCHAR(50) UNIQUE,
    amount DECIMAL(10,2),
    currency VARCHAR(10),
    status VARCHAR(50),
    description TEXT,
    issued_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    due_date TIMESTAMP WITH TIME ZONE,
    items JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. WEBHOOKS
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    url TEXT NOT NULL,
    events JSONB,
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. WEBHOOK LOGS
CREATE TABLE webhook_logs (
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
CREATE TABLE api_keys (
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
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255),
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE,
    "limit" INTEGER,
    blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 14. DATA EXPORTS
CREATE TABLE data_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    export_type VARCHAR(50),
    format VARCHAR(20),
    filters JSONB,
    status VARCHAR(50),
    file_url TEXT,
    row_count INTEGER,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 15. SECURITY EVENTS
CREATE TABLE security_events (
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
CREATE TABLE promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    code VARCHAR(50),
    discount_type VARCHAR(20),
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
CREATE TABLE commercial_objectives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID REFERENCES users(id),
    period VARCHAR(50),
    target_revenue DECIMAL(12,2),
    target_merchants INTEGER,
    target_subscriptions INTEGER,
    current_revenue DECIMAL(12,2) DEFAULT 0,
    current_merchants INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 18. REFERRAL CODES
CREATE TABLE referral_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    code VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 19. LIVE STREAMS
CREATE TABLE live_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES users(id),
    platform VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    stream_url TEXT,
    stream_key VARCHAR(255),
    status VARCHAR(50),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    viewers_count INTEGER DEFAULT 0,
    peak_viewers INTEGER DEFAULT 0,
    products_featured JSONB,
    total_duration INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 20. USER BADGES
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    badge_type VARCHAR(50),
    badge_name VARCHAR(100),
    badge_icon VARCHAR(50),
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    criteria_met JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 21. DISPUTES (Fusion des schémas Phase 8I et Phase 22)
CREATE TABLE disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES transactions(id),
    user_id UUID REFERENCES users(id),
    merchant_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    order_id VARCHAR(50),
    customer_email VARCHAR(255),
    type VARCHAR(50),
    dispute_type VARCHAR(50), -- Alias pour type si nécessaire
    status VARCHAR(50),
    amount DECIMAL(10,2),
    dispute_amount DECIMAL(10,2), -- Alias pour amount
    reason TEXT,
    description TEXT,
    resolution TEXT,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 22. WORKSPACES
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id),
    name VARCHAR(255),
    description TEXT,
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 23. WORKSPACE MEMBERS
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50),
    permissions JSONB,
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    joined_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 24. WORKSPACE COMMENTS
CREATE TABLE workspace_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    user_id UUID REFERENCES users(id),
    entity_type VARCHAR(50),
    entity_id UUID,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 25. INTEGRATIONS
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    provider VARCHAR(50),
    shop_url VARCHAR(255),
    access_token VARCHAR(255),
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    list_id VARCHAR(255), -- Pour Mailchimp
    status VARCHAR(50),
    settings JSONB,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 26. INTEGRATION SYNC LOGS
CREATE TABLE integration_sync_logs (
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
CREATE TABLE social_media_accounts (
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
CREATE TABLE qr_scan_events (
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
CREATE TABLE nfc_tap_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    link_id UUID REFERENCES tracking_links(id),
    nfc_tag_id VARCHAR(100),
    device_info JSONB,
    tapped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 30. OFFLINE ACTIONS
CREATE TABLE offline_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action_type VARCHAR(50),
    payload JSONB,
    synced BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 31. CUSTOM REPORTS
CREATE TABLE custom_reports (
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
CREATE TABLE report_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES custom_reports(id),
    status VARCHAR(50),
    file_url TEXT,
    data JSONB,
    generated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 33. CONTENT TEMPLATES
CREATE TABLE content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    type VARCHAR(50),
    subject VARCHAR(255),
    content TEXT,
    variables JSONB,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 34. MEDIA LIBRARY
CREATE TABLE media_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50),
    filename VARCHAR(255),
    url TEXT,
    size_bytes BIGINT,
    metadata JSONB,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 35. SEO METADATA
CREATE TABLE seo_metadata (
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
CREATE TABLE user_2fa (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    enabled BOOLEAN DEFAULT FALSE,
    method VARCHAR(50),
    secret VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 37. USER SESSIONS
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_token VARCHAR(255),
    ip_address VARCHAR(45),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 38. SALES ASSIGNMENTS
CREATE TABLE sales_assignments (
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
CREATE TABLE affiliation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES users(id),
    merchant_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 40. ANALYTICS REPORTS
CREATE TABLE analytics_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    report_type VARCHAR(50),
    data JSONB,
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,
    generated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 41. SUPPORT TICKETS
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    category VARCHAR(50),
    subject VARCHAR(255),
    description TEXT,
    priority VARCHAR(20),
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 42. PAYMENT INTEGRATIONS
CREATE TABLE payment_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    provider VARCHAR(50),
    public_key VARCHAR(255),
    secret_key VARCHAR(255),
    webhook_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 43. SUBSCRIPTIONS
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50),
    plan_id VARCHAR(50),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 44. EMAIL CAMPAIGNS
CREATE TABLE email_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    subject VARCHAR(255),
    content TEXT,
    status VARCHAR(50),
    sent_count INTEGER DEFAULT 0,
    open_rate DECIMAL(5,2),
    click_rate DECIMAL(5,2),
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 45. SMS CAMPAIGNS
CREATE TABLE sms_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    content TEXT,
    status VARCHAR(50),
    sent_count INTEGER DEFAULT 0,
    cost DECIMAL(10,2),
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 46. PRODUCT COLLECTIONS
CREATE TABLE product_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    name VARCHAR(255),
    slug VARCHAR(255),
    description TEXT,
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 47. WISHLISTS
CREATE TABLE wishlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    is_public BOOLEAN DEFAULT FALSE,
    items JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 48. SHIPMENTS
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(50),
    merchant_id UUID REFERENCES users(id),
    carrier VARCHAR(50),
    tracking_number VARCHAR(100),
    status VARCHAR(50),
    shipped_at TIMESTAMP WITH TIME ZONE,
    estimated_delivery TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 49. WAREHOUSES
CREATE TABLE warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    name VARCHAR(255),
    location VARCHAR(255),
    capacity INTEGER,
    stock_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 50. COUPONS
CREATE TABLE coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id),
    code VARCHAR(50),
    discount_type VARCHAR(50),
    discount_value DECIMAL(10,2),
    min_purchase DECIMAL(10,2),
    usage_limit INTEGER,
    used_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 51. CONVERSATIONS
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user1_id UUID REFERENCES users(id),
    user2_id UUID REFERENCES users(id),
    last_message TEXT,
    last_message_at TIMESTAMP WITH TIME ZONE,
    unread_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 52. EVENTS
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organizer_id UUID REFERENCES users(id),
    title VARCHAR(255),
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    type VARCHAR(50),
    attendees_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- MISE À JOUR TABLE USERS (Colonnes manquantes)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'kyc_verified') THEN
        ALTER TABLE users ADD COLUMN kyc_verified BOOLEAN DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'kyc_verified_at') THEN
        ALTER TABLE users ADD COLUMN kyc_verified_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

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
        'seo_metadata', 'user_2fa', 'user_sessions', 'sales_assignments', 'affiliation_requests',
        'analytics_reports', 'support_tickets', 'payment_integrations', 'subscriptions',
        'email_campaigns', 'sms_campaigns', 'product_collections', 'wishlists', 'shipments',
        'warehouses', 'coupons', 'conversations', 'events'
    ]
    LOOP
        IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = tbl) THEN
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
            EXECUTE format('DROP POLICY IF EXISTS "Enable all for %I" ON %I', tbl, tbl);
            EXECUTE format('CREATE POLICY "Enable all for %I" ON %I FOR ALL USING (true)', tbl, tbl);
        END IF;
    END LOOP;
END $$;

-- RECHARGER LE CACHE DE SCHÉMA (Pour PostgREST)
NOTIFY pgrst, 'reload schema';
