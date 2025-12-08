-- ============================================
-- Migration 005: Ensure All Required Tables Exist
-- Date: 2025-12-08
-- Description: Creates all missing tables with proper columns (idempotent)
-- ============================================

-- Enable UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- LIVE CHAT TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS chat_rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id TEXT UNIQUE NOT NULL,
    room_type TEXT NOT NULL,
    created_by UUID,
    participants UUID[] NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id TEXT NOT NULL,
    user_id UUID,
    content TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for chat
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_chat_messages_room') THEN
        CREATE INDEX idx_chat_messages_room ON chat_messages(room_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_chat_messages_user') THEN
        CREATE INDEX idx_chat_messages_user ON chat_messages(user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_chat_messages_created') THEN
        CREATE INDEX idx_chat_messages_created ON chat_messages(created_at DESC);
    END IF;
END $$;

-- ============================================
-- CUSTOMER SERVICE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number TEXT UNIQUE NOT NULL,
    user_id UUID,
    subject TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    assigned_to UUID,
    sla_due_at TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS support_ticket_replies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID,
    user_id UUID,
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    attachments JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- AI CHATBOT TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS chatbot_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    intent TEXT,
    confidence DECIMAL(5,4),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- GAMIFICATION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS gamification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    badge_id TEXT NOT NULL,
    earned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

CREATE TABLE IF NOT EXISTS points_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    points INTEGER NOT NULL,
    reason TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- KYC VERIFICATION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS kyc_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    document_type TEXT NOT NULL,
    document_id TEXT,
    document_number TEXT,
    country TEXT,
    date_of_birth DATE,
    front_image_url TEXT,
    back_image_url TEXT,
    selfie_url TEXT,
    status TEXT DEFAULT 'pending',
    verification_method TEXT,
    verified_at TIMESTAMP,
    verified_by UUID,
    reviewed_at TIMESTAMP,
    reviewed_by UUID,
    rejection_reason TEXT,
    submitted_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- ============================================
-- MOBILE FEATURES TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    to_number TEXT NOT NULL,
    from_number TEXT,
    message TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    status TEXT DEFAULT 'pending',
    whatsapp_message_id TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mobile_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    provider TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_id TEXT,
    status TEXT DEFAULT 'pending',
    reference TEXT UNIQUE,
    callback_url TEXT,
    metadata JSONB DEFAULT '{}',
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- SOCIAL MEDIA TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS social_media_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    platform TEXT NOT NULL,
    platform_user_id TEXT,
    platform_username TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    status TEXT DEFAULT 'connected',
    permissions JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    connected_at TIMESTAMP DEFAULT NOW(),
    last_sync_at TIMESTAMP,
    UNIQUE(user_id, platform)
);

CREATE TABLE IF NOT EXISTS social_media_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    connection_id UUID,
    platform TEXT NOT NULL,
    content TEXT NOT NULL,
    media_urls JSONB DEFAULT '[]',
    platform_post_id TEXT,
    status TEXT DEFAULT 'pending',
    scheduled_for TIMESTAMP,
    published_at TIMESTAMP,
    error_message TEXT,
    engagement JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TEAM MANAGEMENT TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_owner_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role TEXT NOT NULL,
    permissions JSONB DEFAULT '[]',
    joined_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_owner_id, user_id)
);

CREATE TABLE IF NOT EXISTS team_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_owner_id UUID NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    permissions JSONB DEFAULT '[]',
    token TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending',
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ADVANCED ANALYTICS TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS ab_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    created_by UUID,
    variants JSONB NOT NULL,
    traffic_split JSONB NOT NULL,
    metric TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    results JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ab_test_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_id UUID NOT NULL,
    user_id UUID NOT NULL,
    variant_id TEXT NOT NULL,
    assigned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(test_id, user_id)
);

-- ============================================
-- ADMIN DASHBOARD TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS moderation_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type TEXT NOT NULL,
    content_id UUID NOT NULL,
    reported_by UUID,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'normal',
    reason TEXT,
    moderated_by UUID,
    moderated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id UUID,
    target_user_id UUID,
    reason TEXT,
    ip_address TEXT,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    source TEXT,
    trace_id TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    user_id UUID,
    request_path TEXT,
    request_method TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- WEBHOOK LOGS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_id TEXT,
    shop_domain TEXT,
    source TEXT,
    payload JSONB NOT NULL,
    processed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- E-COMMERCE INTEGRATIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS ecommerce_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    platform TEXT NOT NULL,
    shop_url TEXT,
    api_key TEXT,
    api_secret TEXT,
    access_token TEXT,
    status TEXT DEFAULT 'connected',
    last_sync_at TIMESTAMP,
    sync_settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    connected_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

-- ============================================
-- PAYMENT TRANSACTIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    payment_method TEXT NOT NULL,
    provider TEXT,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'MAD',
    status TEXT DEFAULT 'pending',
    session_id TEXT,
    payment_intent_id TEXT,
    stripe_session_id TEXT,
    paypal_sale_id TEXT,
    payment_id TEXT,
    refund_id TEXT,
    amount_received DECIMAL(10,2),
    failure_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- SUBSCRIPTIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    stripe_subscription_id TEXT UNIQUE,
    stripe_customer_id TEXT,
    plan_id TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CREATE ALL INDEXES (IF NOT EXISTS)
-- ============================================

DO $$
DECLARE
    idx_record RECORD;
    idx_queries TEXT[] := ARRAY[
        'CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status)',
        'CREATE INDEX IF NOT EXISTS idx_support_tickets_assigned ON support_tickets(assigned_to)',
        'CREATE INDEX IF NOT EXISTS idx_support_tickets_created ON support_tickets(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_support_ticket_replies_ticket ON support_ticket_replies(ticket_id)',
        'CREATE INDEX IF NOT EXISTS idx_chatbot_history_user ON chatbot_history(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_chatbot_history_session ON chatbot_history(session_id)',
        'CREATE INDEX IF NOT EXISTS idx_chatbot_history_created ON chatbot_history(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_gamification_user ON gamification(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_gamification_points ON gamification(points DESC)',
        'CREATE INDEX IF NOT EXISTS idx_gamification_level ON gamification(level DESC)',
        'CREATE INDEX IF NOT EXISTS idx_user_badges_user ON user_badges(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_points_history_user ON points_history(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_kyc_user ON kyc_verifications(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_kyc_status ON kyc_verifications(status)',
        'CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_user ON whatsapp_messages(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_status ON whatsapp_messages(status)',
        'CREATE INDEX IF NOT EXISTS idx_mobile_payments_user ON mobile_payments(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_mobile_payments_status ON mobile_payments(status)',
        'CREATE INDEX IF NOT EXISTS idx_mobile_payments_reference ON mobile_payments(reference)',
        'CREATE INDEX IF NOT EXISTS idx_social_connections_user ON social_media_connections(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_social_connections_platform ON social_media_connections(platform)',
        'CREATE INDEX IF NOT EXISTS idx_social_posts_user ON social_media_posts(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_media_posts(status)',
        'CREATE INDEX IF NOT EXISTS idx_team_members_owner ON team_members(team_owner_id)',
        'CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_team_invitations_owner ON team_invitations(team_owner_id)',
        'CREATE INDEX IF NOT EXISTS idx_team_invitations_token ON team_invitations(token)',
        'CREATE INDEX IF NOT EXISTS idx_team_invitations_status ON team_invitations(status)',
        'CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status)',
        'CREATE INDEX IF NOT EXISTS idx_ab_tests_created ON ab_tests(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_ab_test_assignments_test ON ab_test_assignments(test_id)',
        'CREATE INDEX IF NOT EXISTS idx_ab_test_assignments_user ON ab_test_assignments(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_moderation_queue_status ON moderation_queue(status)',
        'CREATE INDEX IF NOT EXISTS idx_moderation_queue_type ON moderation_queue(content_type)',
        'CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)',
        'CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level)',
        'CREATE INDEX IF NOT EXISTS idx_system_logs_created ON system_logs(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_error_logs_type ON error_logs(error_type)',
        'CREATE INDEX IF NOT EXISTS idx_error_logs_created ON error_logs(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_webhook_logs_provider ON webhook_logs(provider)',
        'CREATE INDEX IF NOT EXISTS idx_webhook_logs_event ON webhook_logs(event_type)',
        'CREATE INDEX IF NOT EXISTS idx_webhook_logs_processed ON webhook_logs(processed_at)',
        'CREATE INDEX IF NOT EXISTS idx_webhook_logs_created ON webhook_logs(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_ecommerce_integrations_user ON ecommerce_integrations(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_ecommerce_integrations_platform ON ecommerce_integrations(platform)',
        'CREATE INDEX IF NOT EXISTS idx_payment_transactions_user ON payment_transactions(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status)',
        'CREATE INDEX IF NOT EXISTS idx_payment_transactions_session ON payment_transactions(session_id)',
        'CREATE INDEX IF NOT EXISTS idx_payment_transactions_created ON payment_transactions(created_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)',
        'CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_sub ON subscriptions(stripe_subscription_id)'
    ];
BEGIN
    FOREACH idx_record IN ARRAY idx_queries
    LOOP
        EXECUTE idx_record;
    END LOOP;
END $$;

-- ============================================
-- END OF MIGRATION
-- ============================================

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 005 completed successfully';
    RAISE NOTICE '✅ All tables and indexes have been created';
END $$;
