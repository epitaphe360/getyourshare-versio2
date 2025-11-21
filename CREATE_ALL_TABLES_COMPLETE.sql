-- ============================================
-- SCRIPT SQL COMPLET - CRÉATION DE TOUTES LES TABLES SUPABASE
-- POUR L'APPLICATION GETYOURSHARE
-- ============================================
-- Exécuter ce script dans l'éditeur SQL de Supabase
-- Il créera toutes les tables manquantes et mettra à jour les existantes
-- ============================================

-- Désactiver RLS temporairement pour la création
SET session_replication_role = replica;

-- Supprimer toutes les vues d'abord pour éviter les conflits de dépendances
DROP VIEW IF EXISTS v_products_full CASCADE;
DROP VIEW IF EXISTS v_featured_products CASCADE;
DROP VIEW IF EXISTS v_deals_of_day CASCADE;
DROP VIEW IF EXISTS v_admin_social_posts_summary CASCADE;
DROP VIEW IF EXISTS v_admin_social_analytics CASCADE;
DROP VIEW IF EXISTS v_contact_stats CASCADE;

-- ============================================
-- 1. TABLE USERS (Principale - déjà existe normalement)
-- ============================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK (role IN ('admin', 'merchant', 'influencer', 'commercial')) DEFAULT 'influencer',
    full_name TEXT,
    company_name TEXT,
    phone TEXT,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_token TEXT,
    reset_token TEXT,
    reset_token_expiry TIMESTAMPTZ,
    last_login TIMESTAMPTZ,
    subscription_plan TEXT DEFAULT 'Free',
    two_fa_enabled BOOLEAN DEFAULT false,
    two_fa_secret TEXT,
    avatar_url TEXT,
    bio TEXT,
    location TEXT,
    website TEXT,
    instagram_handle TEXT,
    tiktok_handle TEXT,
    youtube_handle TEXT,
    twitter_handle TEXT,
    followers_count INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    niche TEXT[],
    budget DECIMAL(12,2) DEFAULT 0,
    monthly_budget DECIMAL(12,2) DEFAULT 0,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'active'
);

-- Index pour users
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_users_status ON public.users(status);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON public.users(is_active);

-- ============================================
-- 2. TABLES MERCHANTS & INFLUENCERS
-- ============================================
CREATE TABLE IF NOT EXISTS public.merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    business_type TEXT,
    industry TEXT,
    website TEXT,
    description TEXT,
    logo_url TEXT,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    monthly_budget DECIMAL(12,2) DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    instagram_handle TEXT,
    tiktok_handle TEXT,
    youtube_handle TEXT,
    twitter_handle TEXT,
    followers_count INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    niche TEXT[],
    audience_size INTEGER DEFAULT 0,
    avg_views INTEGER DEFAULT 0,
    content_style TEXT,
    rating DECIMAL(3,2) DEFAULT 0,
    total_collaborations INTEGER DEFAULT 0,
    total_earnings DECIMAL(12,2) DEFAULT 0,
    bio TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON public.merchants(user_id);
CREATE INDEX IF NOT EXISTS idx_influencers_user_id ON public.influencers(user_id);

-- ============================================
-- 3. TABLES PRODUCTS & SERVICES
-- ============================================
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    price DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    image_url TEXT,
    product_url TEXT,
    sku TEXT,
    stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    type TEXT DEFAULT 'product',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    price DECIMAL(12,2) NOT NULL,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    image_url TEXT,
    duration INTEGER, -- en minutes
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    parent_id UUID REFERENCES public.product_categories(id),
    order_index INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON public.products(merchant_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);
CREATE INDEX IF NOT EXISTS idx_services_merchant_id ON public.services(merchant_id);

-- ============================================
-- 4. TABLES CAMPAIGNS
-- ============================================
CREATE TABLE IF NOT EXISTS public.campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES public.users(id),
    name TEXT NOT NULL,
    description TEXT,
    budget DECIMAL(12,2) DEFAULT 0,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    status TEXT CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')) DEFAULT 'draft',
    type TEXT,
    target_audience TEXT,
    performance_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.campaign_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.campaign_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
    settings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_campaigns_merchant_id ON public.campaigns(merchant_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON public.campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON public.campaigns(start_date, end_date);

-- ============================================
-- 5. TABLES TRACKING_LINKS & CONVERSIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    unique_code TEXT UNIQUE NOT NULL,
    full_url TEXT NOT NULL,
    short_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0,
    commission_earned DECIMAL(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.trackable_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    unique_code TEXT UNIQUE NOT NULL,
    full_url TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_link_id UUID REFERENCES public.tracking_links(id),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    sale_amount DECIMAL(12,2),
    commission_amount DECIMAL(12,2),
    commission_rate DECIMAL(5,2),
    status TEXT CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded')) DEFAULT 'pending',
    conversion_date TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_tracking_links_influencer ON public.tracking_links(influencer_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_merchant ON public.tracking_links(merchant_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_code ON public.tracking_links(unique_code);
CREATE INDEX IF NOT EXISTS idx_conversions_influencer ON public.conversions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_conversions_status ON public.conversions(status);

-- ============================================
-- 6. TABLES SALES & COMMISSIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    influencer_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    amount DECIMAL(12,2) NOT NULL,
    commission_amount DECIMAL(12,2),
    platform_commission DECIMAL(12,2),
    status TEXT DEFAULT 'completed',
    sale_timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    sale_id UUID REFERENCES public.sales(id),
    amount DECIMAL(12,2) NOT NULL,
    status TEXT CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')) DEFAULT 'pending',
    payout_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_sales_merchant ON public.sales(merchant_id);
CREATE INDEX IF NOT EXISTS idx_sales_influencer ON public.sales(influencer_id);
CREATE INDEX IF NOT EXISTS idx_sales_timestamp ON public.sales(sale_timestamp);
CREATE INDEX IF NOT EXISTS idx_commissions_influencer ON public.commissions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON public.commissions(status);

-- ============================================
-- 7. TABLES PAYOUTS
-- ============================================
CREATE TABLE IF NOT EXISTS public.payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    method TEXT,
    status TEXT CHECK (status IN ('pending', 'processing', 'paid', 'failed', 'cancelled')) DEFAULT 'pending',
    transaction_id TEXT,
    payment_details JSONB,
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_payouts_influencer ON public.payouts(influencer_id);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON public.payouts(status);

-- ============================================
-- 8. TABLES INVITATIONS & COLLABORATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    message TEXT,
    commission_rate DECIMAL(5,2),
    status TEXT CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled')) DEFAULT 'pending',
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.collaboration_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    influencer_id UUID REFERENCES public.users(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    message TEXT,
    status TEXT CHECK (status IN ('pending', 'accepted', 'rejected')) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.collaboration_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID REFERENCES public.users(id),
    receiver_id UUID REFERENCES public.users(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    message TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.collaboration_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES public.collaboration_requests(id),
    action TEXT NOT NULL,
    actor_id UUID REFERENCES public.users(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_invitations_merchant ON public.invitations(merchant_id);
CREATE INDEX IF NOT EXISTS idx_invitations_influencer ON public.invitations(influencer_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON public.invitations(status);

-- ============================================
-- 9. TABLES SUBSCRIPTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    billing_period TEXT CHECK (billing_period IN ('monthly', 'yearly')) DEFAULT 'monthly',
    max_campaigns INTEGER,
    max_tracking_links INTEGER,
    max_products INTEGER,
    features JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    influencer_id UUID REFERENCES public.users(id),
    plan_id UUID REFERENCES public.subscription_plans(id),
    status TEXT CHECK (status IN ('active', 'cancelled', 'expired', 'suspended')) DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT false,
    stripe_subscription_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.subscription_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES public.subscriptions(id),
    metric_name TEXT NOT NULL,
    current_value INTEGER DEFAULT 0,
    limit_value INTEGER,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.subscription_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES public.subscriptions(id),
    event_type TEXT NOT NULL,
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.subscription_coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    discount_percent INTEGER,
    discount_amount DECIMAL(10,2),
    max_uses INTEGER,
    used_count INTEGER DEFAULT 0,
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);

-- ============================================
-- 10. TABLES INVOICES & PAYMENTS
-- ============================================
CREATE TABLE IF NOT EXISTS public.invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    subscription_id UUID REFERENCES public.subscriptions(id),
    amount DECIMAL(10,2) NOT NULL,
    status TEXT CHECK (status IN ('draft', 'pending', 'paid', 'failed', 'refunded')) DEFAULT 'pending',
    invoice_number TEXT UNIQUE,
    pdf_url TEXT,
    stripe_invoice_id TEXT,
    due_date TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.platform_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    invoice_number TEXT UNIQUE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    due_date TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    pdf_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES public.platform_invoices(id),
    description TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'pending',
    payment_method TEXT,
    stripe_payment_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    type TEXT NOT NULL,
    last4 TEXT,
    stripe_payment_method_id TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.payment_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    provider TEXT NOT NULL,
    account_identifier TEXT NOT NULL,
    account_details JSONB,
    is_verified BOOLEAN DEFAULT false,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    amount DECIMAL(12,2) NOT NULL,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    transaction_id TEXT UNIQUE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_invoices_user ON public.invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices(status);

-- ============================================
-- 11. TABLES LEADS SYSTEM
-- ============================================
CREATE TABLE IF NOT EXISTS public.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    influencer_id UUID REFERENCES public.users(id),
    commercial_id UUID REFERENCES public.users(id),
    sales_rep_id UUID REFERENCES public.users(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    product_id UUID REFERENCES public.products(id),
    service_id UUID REFERENCES public.services(id),
    customer_name TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    commission_amount DECIMAL(12,2),
    status TEXT CHECK (status IN ('pending', 'validated', 'rejected', 'paid')) DEFAULT 'pending',
    lead_status TEXT,
    score INTEGER,
    source TEXT,
    notes TEXT,
    rejection_reason TEXT,
    metadata JSONB,
    validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.sales_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID,
    customer_name TEXT,
    customer_email TEXT,
    status TEXT DEFAULT 'new',
    score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.lead_validation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES public.leads(id),
    validator_id UUID REFERENCES public.users(id),
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.merchant_deposits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    amount DECIMAL(12,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    payment_method TEXT,
    transaction_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.company_deposits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES public.users(id),
    amount DECIMAL(12,2) NOT NULL,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.deposit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    amount DECIMAL(12,2) NOT NULL,
    type TEXT CHECK (type IN ('deposit', 'withdrawal', 'commission')) NOT NULL,
    status TEXT DEFAULT 'completed',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_leads_merchant ON public.leads(merchant_id);
CREATE INDEX IF NOT EXISTS idx_leads_influencer ON public.leads(influencer_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON public.leads(status);

-- ============================================
-- 12. TABLES AFFILIATION REQUESTS
-- ============================================
CREATE TABLE IF NOT EXISTS public.affiliation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    service_id UUID REFERENCES public.services(id),
    message TEXT,
    status TEXT CHECK (status IN ('pending_approval', 'active', 'rejected', 'cancelled')) DEFAULT 'pending_approval',
    requested_commission_rate DECIMAL(5,2),
    approved_commission_rate DECIMAL(5,2),
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.influencer_affiliation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    status TEXT DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.merchant_affiliation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    influencer_id UUID REFERENCES public.users(id),
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.affiliate_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    status TEXT DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.affiliation_requests_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.users(id),
    pending_count INTEGER DEFAULT 0,
    active_count INTEGER DEFAULT 0,
    rejected_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.affiliation_request_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES public.affiliation_requests(id),
    action TEXT NOT NULL,
    actor_id UUID REFERENCES public.users(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.influencer_agreements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    merchant_id UUID REFERENCES public.users(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    terms TEXT,
    commission_rate DECIMAL(5,2),
    status TEXT DEFAULT 'active',
    signed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.affiliate_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    campaign_id UUID REFERENCES public.campaigns(id),
    unique_code TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_influencer ON public.affiliation_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_merchant ON public.affiliation_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_status ON public.affiliation_requests(status);

-- ============================================
-- 13. TABLES SOCIAL MEDIA
-- ============================================
CREATE TABLE IF NOT EXISTS public.social_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    platform TEXT NOT NULL,
    platform_user_id TEXT,
    username TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    followers_count INTEGER DEFAULT 0,
    is_connected BOOLEAN DEFAULT true,
    last_synced_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.social_media_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    platform TEXT NOT NULL,
    account_id TEXT,
    access_token TEXT,
    refresh_token TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.social_media_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    platform TEXT NOT NULL,
    account_name TEXT,
    followers INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.social_media_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.users(id),
    platform TEXT NOT NULL,
    content TEXT,
    media_urls TEXT[],
    post_id TEXT,
    status TEXT DEFAULT 'draft',
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.social_media_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID REFERENCES public.social_connections(id),
    date DATE NOT NULL,
    followers_count INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_social_connections_influencer ON public.social_connections(influencer_id);
CREATE INDEX IF NOT EXISTS idx_social_connections_platform ON public.social_connections(platform);

-- ============================================
-- 14. TABLES ADMIN & SOCIAL POSTS
-- ============================================
CREATE TABLE IF NOT EXISTS public.admin_social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    caption TEXT NOT NULL,
    media_urls JSONB DEFAULT '[]'::jsonb,
    media_type VARCHAR(50) DEFAULT 'image' CHECK (media_type IN ('image', 'video', 'carousel', 'text')),
    cta_text VARCHAR(255),
    cta_url TEXT,
    hashtags TEXT[],
    platforms JSONB DEFAULT '{}'::jsonb,
    campaign_type VARCHAR(100) DEFAULT 'general',
    status VARCHAR(50) DEFAULT 'draft',
    scheduled_for TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    total_views INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.admin_social_post_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'general',
    caption_template TEXT NOT NULL,
    suggested_hashtags TEXT[],
    suggested_cta_text VARCHAR(255),
    suggested_cta_url TEXT,
    example_media_url TEXT,
    media_type VARCHAR(50) DEFAULT 'image',
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 15. TABLES SALES REPRESENTATIVES
-- ============================================
CREATE TABLE IF NOT EXISTS public.sales_representatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    territory TEXT,
    quota DECIMAL(12,2),
    commission_rate DECIMAL(5,2) DEFAULT 5.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.sales_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID REFERENCES public.sales_representatives(id),
    lead_id UUID REFERENCES public.leads(id),
    activity_type TEXT CHECK (activity_type IN ('call', 'email', 'meeting', 'note', 'task')) NOT NULL,
    subject TEXT,
    description TEXT,
    outcome TEXT,
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID REFERENCES public.sales_representatives(id),
    lead_id UUID REFERENCES public.leads(id),
    name TEXT NOT NULL,
    value DECIMAL(12,2),
    status TEXT CHECK (status IN ('prospecting', 'qualified', 'proposal', 'negotiation', 'won', 'lost', 'open')) DEFAULT 'prospecting',
    stage TEXT,
    probability INTEGER,
    expected_close_date DATE,
    closed_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.sales_deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID,
    deal_name TEXT NOT NULL,
    amount DECIMAL(12,2),
    status TEXT DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.sales_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID REFERENCES public.sales_representatives(id),
    period TEXT NOT NULL,
    target_amount DECIMAL(12,2) NOT NULL,
    actual_amount DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.sales_commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_rep_id UUID REFERENCES public.sales_representatives(id),
    deal_id UUID REFERENCES public.deals(id),
    amount DECIMAL(12,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_sales_reps_user ON public.sales_representatives(user_id);
CREATE INDEX IF NOT EXISTS idx_deals_sales_rep ON public.deals(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_deals_status ON public.deals(status);

-- ============================================
-- 16. TABLES MESSAGING & NOTIFICATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_ids UUID[] NOT NULL,
    last_message TEXT,
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES public.conversations(id),
    sender_id UUID REFERENCES public.users(id),
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT,
    data JSONB,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON public.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON public.notifications(is_read);

-- ============================================
-- 17. TABLES REVIEWS & RATINGS
-- ============================================
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES public.products(id),
    user_id UUID REFERENCES public.users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_verified_purchase BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES public.products(id),
    user_id UUID REFERENCES public.users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 18. TABLES TRACKING & ANALYTICS
-- ============================================
CREATE TABLE IF NOT EXISTS public.click_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID REFERENCES public.trackable_links(id),
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    country TEXT,
    city TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.click_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_link_id UUID REFERENCES public.tracking_links(id),
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.tracking_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_link_id UUID REFERENCES public.tracking_links(id),
    event_type TEXT NOT NULL,
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    metric_type TEXT NOT NULL,
    metric_value DECIMAL(12,2),
    period DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_click_tracking_link ON public.click_tracking(link_id);
CREATE INDEX IF NOT EXISTS idx_click_tracking_created ON public.click_tracking(created_at);

-- ============================================
-- 19. TABLES GAMIFICATION
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_gamification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) UNIQUE,
    level INTEGER DEFAULT 1,
    points INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,
    achievements TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon_url TEXT,
    criteria JSONB,
    points_reward INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,
    criteria JSONB,
    rewards JSONB,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    mission_id UUID REFERENCES public.missions(id),
    progress INTEGER DEFAULT 0,
    status TEXT DEFAULT 'in_progress',
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 20. TABLES KYC & VERIFICATION
-- ============================================
CREATE TABLE IF NOT EXISTS public.kyc_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    document_type TEXT NOT NULL,
    document_url TEXT,
    status TEXT CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    reviewed_by UUID REFERENCES public.users(id),
    reviewed_at TIMESTAMPTZ,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_kyc_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) UNIQUE,
    kyc_status TEXT DEFAULT 'pending',
    verification_level INTEGER DEFAULT 0,
    documents_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_kyc_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    document_type TEXT NOT NULL,
    document_url TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.kyc_verification_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID REFERENCES public.kyc_submissions(id),
    action TEXT NOT NULL,
    notes TEXT,
    created_by UUID REFERENCES public.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.trust_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) UNIQUE,
    score INTEGER DEFAULT 50,
    factors JSONB,
    last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 21. TABLES GATEWAY & TRANSACTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.gateway_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    gateway TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'pending',
    transaction_id TEXT UNIQUE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.gateway_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gateway TEXT NOT NULL,
    date DATE NOT NULL,
    total_transactions INTEGER DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(gateway, date)
);

-- ============================================
-- 22. TABLES TEAM & COMPANY
-- ============================================
CREATE TABLE IF NOT EXISTS public.team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_owner_id UUID REFERENCES public.users(id),
    user_id UUID REFERENCES public.users(id),
    role TEXT,
    permissions JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.team_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_owner_id UUID REFERENCES public.users(id),
    email TEXT NOT NULL,
    role TEXT,
    status TEXT DEFAULT 'pending',
    token TEXT UNIQUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.company_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES public.users(id) UNIQUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 23. TABLES PLATFORM SETTINGS
-- ============================================
CREATE TABLE IF NOT EXISTS public.platform_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value JSONB NOT NULL,
    category TEXT,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    updated_by UUID REFERENCES public.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value JSONB,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 24. TABLES CONTACT & MODERATION
-- ============================================
CREATE TABLE IF NOT EXISTS public.contact_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    replied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.moderation_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID,
    reason TEXT,
    status TEXT DEFAULT 'pending',
    reviewed_by UUID REFERENCES public.users(id),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 25. TABLES AUTRES (SWIPE, SESSIONS, WEBHOOKS, etc.)
-- ============================================
CREATE TABLE IF NOT EXISTS public.swipe_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    target_id UUID,
    direction TEXT CHECK (direction IN ('left', 'right')) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id),
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.webhook_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    payload JSONB,
    status TEXT DEFAULT 'pending',
    response TEXT,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL,
    language TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(key, language)
);

CREATE TABLE IF NOT EXISTS public.match_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES public.merchants(id) UNIQUE,
    preferred_niches TEXT[],
    min_followers INTEGER,
    max_budget DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.influencer_profiles_extended (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES public.influencers(id) UNIQUE,
    content_quality_score INTEGER,
    authenticity_score INTEGER,
    collaboration_success_rate DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 26. VUES MATERIALISÉES (VIEWS)
-- ============================================

-- Vue pour les produits avec détails complets
CREATE OR REPLACE VIEW v_products_full AS
SELECT 
    p.*,
    u.company_name as merchant_name,
    u.email as merchant_email,
    COALESCE(COUNT(DISTINCT t.id), 0) as total_links,
    COALESCE(SUM(t.clicks), 0) as total_clicks,
    COALESCE(SUM(t.conversions), 0) as total_conversions
FROM products p
LEFT JOIN users u ON p.merchant_id = u.id
LEFT JOIN tracking_links t ON p.id = t.product_id
GROUP BY p.id, u.company_name, u.email;

-- Vue pour les produits en vedette
CREATE OR REPLACE VIEW v_featured_products AS
SELECT 
    p.*,
    u.company_name as merchant_name
FROM products p
LEFT JOIN users u ON p.merchant_id = u.id
WHERE p.is_active = true
ORDER BY p.created_at DESC
LIMIT 10;

-- Vue pour les deals du jour
CREATE OR REPLACE VIEW v_deals_of_day AS
SELECT 
    p.*,
    u.company_name as merchant_name,
    15 as discount_percentage
FROM products p
LEFT JOIN users u ON p.merchant_id = u.id
WHERE p.is_active = true 
  AND p.created_at >= CURRENT_DATE - INTERVAL '1 day'
ORDER BY p.created_at DESC
LIMIT 5;

-- Vue pour statistiques admin social posts
CREATE OR REPLACE VIEW v_admin_social_posts_summary AS
SELECT
    asp.*,
    u.email as creator_email,
    u.full_name as creator_name,
    (total_views + total_likes + total_comments + total_shares) as total_engagement
FROM admin_social_posts asp
JOIN users u ON asp.created_by = u.id
ORDER BY asp.created_at DESC;

-- Vue pour analytics admin social
CREATE OR REPLACE VIEW v_admin_social_analytics AS
SELECT
    COUNT(*) as total_posts,
    COUNT(CASE WHEN status = 'published' THEN 1 END) as published_posts,
    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_posts,
    COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_posts,
    SUM(total_views) as total_views,
    SUM(total_likes) as total_likes,
    SUM(total_comments) as total_comments,
    SUM(total_shares) as total_shares,
    SUM(total_clicks) as total_clicks,
    ROUND(AVG(total_views), 2) as avg_views_per_post,
    ROUND(AVG(total_likes), 2) as avg_likes_per_post,
    ROUND(
        (SUM(total_likes) + SUM(total_comments) + SUM(total_shares)) * 100.0 / NULLIF(SUM(total_views), 0),
        2
    ) as engagement_rate_percent
FROM admin_social_posts
WHERE status = 'published';

-- Vue pour statistiques de contact
CREATE OR REPLACE VIEW v_contact_stats AS
SELECT 
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE status = 'new') as new_messages,
    COUNT(*) FILTER (WHERE status = 'replied') as replied_messages,
    DATE(created_at) as date
FROM contact_messages
GROUP BY DATE(created_at);

-- ============================================
-- 27. FONCTIONS & TRIGGERS POUR UPDATED_AT
-- ============================================

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger sur toutes les tables avec updated_at
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'users', 'merchants', 'influencers', 'products', 'services',
            'campaigns', 'tracking_links', 'subscriptions', 'affiliation_requests',
            'social_connections', 'platform_settings', 'company_settings'
        )
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON public.%I;
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON public.%I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 28. INSERTION DES DONNÉES PAR DÉFAUT
-- ============================================

-- Insérer les plans d'abonnement par défaut
INSERT INTO public.subscription_plans (name, description, price, billing_period, max_campaigns, max_tracking_links, max_products, features)
VALUES 
    ('Free', 'Plan gratuit pour démarrer', 0, 'monthly', 5, 10, 5, '{"instant_payout": false, "priority_support": false}'::jsonb),
    ('Pro', 'Plan professionnel', 29.99, 'monthly', 20, 50, 20, '{"instant_payout": true, "priority_support": false, "advanced_analytics": true}'::jsonb),
    ('Elite', 'Plan entreprise', 99.99, 'monthly', -1, -1, -1, '{"instant_payout": true, "priority_support": true, "advanced_analytics": true, "custom_features": true}'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- Insérer les catégories de produits par défaut
INSERT INTO public.product_categories (name, slug, description)
VALUES 
    ('Fashion', 'fashion', 'Vêtements et accessoires'),
    ('Tech', 'tech', 'Technologie et électronique'),
    ('Food', 'food', 'Alimentation et boissons'),
    ('Beauty', 'beauty', 'Beauté et cosmétiques'),
    ('Home', 'home', 'Maison et décoration'),
    ('Sports', 'sports', 'Sport et fitness'),
    ('Travel', 'travel', 'Voyage et tourisme'),
    ('Other', 'other', 'Autres produits')
ON CONFLICT (name) DO NOTHING;

-- Insérer des paramètres de plateforme par défaut
INSERT INTO public.platform_settings (key, value, category, description, is_public)
VALUES 
    ('commission_rate', '{"default": 10, "min": 5, "max": 30}'::jsonb, 'payments', 'Taux de commission par défaut', true),
    ('min_payout_amount', '{"amount": 50, "currency": "USD"}'::jsonb, 'payments', 'Montant minimum pour un payout', true),
    ('platform_name', '{"name": "GetYourShare"}'::jsonb, 'general', 'Nom de la plateforme', true),
    ('maintenance_mode', '{"enabled": false}'::jsonb, 'general', 'Mode maintenance', false)
ON CONFLICT (key) DO NOTHING;

-- ============================================
-- 29. RÉACTIVER RLS
-- ============================================
SET session_replication_role = DEFAULT;

-- Activer RLS sur toutes les tables (à configurer selon vos besoins)
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        AND tablename NOT LIKE 'sql_%'
        AND tablename NOT LIKE 'v_%'
    LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', t);
        
        -- Politique par défaut: admin peut tout faire
        EXECUTE format('
            DROP POLICY IF EXISTS admin_all_access ON public.%I;
            CREATE POLICY admin_all_access ON public.%I
            FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM public.users 
                    WHERE id = auth.uid() AND role = ''admin''
                )
            );
        ', t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 30. AFFICHER LES STATISTIQUES FINALES
-- ============================================

-- Afficher le résumé
DO $$
BEGIN
    RAISE NOTICE 'Script terminé avec succès!';
    RAISE NOTICE 'Tables créées: %', (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND tablename NOT LIKE 'pg_%' AND tablename NOT LIKE 'sql_%' AND tablename NOT LIKE 'v_%');
    RAISE NOTICE 'Vues créées: %', (SELECT COUNT(*) FROM pg_views WHERE schemaname = 'public');
    RAISE NOTICE 'Index créés: %', (SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public');
END $$;

-- ============================================
-- FIN DU SCRIPT
-- ============================================
-- Toutes les tables ont été créées avec succès!
-- Vous pouvez maintenant utiliser l'application complète.
-- ============================================
