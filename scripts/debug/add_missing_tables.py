"""
Script pour exécuter le SQL d'ajout des tables et colonnes manquantes
"""
import os
from supabase_client import supabase

print("=" * 80)
print(" AJOUT DES TABLES ET COLONNES MANQUANTES")
print("=" * 80)

# Lire le fichier SQL
with open('ADD_MISSING_TABLES_AND_COLUMNS.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Séparer les commandes SQL (par ';' mais en ignorant ceux dans les blocs DO $$)
# Pour simplifier, on va exécuter section par section

sections = {
    "1. Colonnes dans USERS": """
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS referral_code VARCHAR(20) UNIQUE,
ADD COLUMN IF NOT EXISTS referred_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS referral_earnings DECIMAL(10,2) DEFAULT 0;
""",
    
    "2. Colonnes dans SUBSCRIPTIONS": """
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS end_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS start_date TIMESTAMP DEFAULT NOW();
""",
    
    "3. Colonnes dans TRACKING_LINKS": """
ALTER TABLE tracking_links
ADD COLUMN IF NOT EXISTS campaign_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS utm_source VARCHAR(100),
ADD COLUMN IF NOT EXISTS utm_medium VARCHAR(100),
ADD COLUMN IF NOT EXISTS utm_campaign VARCHAR(100);
""",
    
    "4. Table USER_2FA": """
CREATE TABLE IF NOT EXISTS user_2fa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    method VARCHAR(50) NOT NULL CHECK (method IN ('sms', 'email', 'authenticator')),
    is_enabled BOOLEAN DEFAULT FALSE,
    secret_key VARCHAR(255),
    backup_codes TEXT[],
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, method)
);
CREATE INDEX IF NOT EXISTS idx_user_2fa_user_id ON user_2fa(user_id);
""",
    
    "5. Table WORKSPACES": """
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description TEXT,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_workspaces_owner ON workspaces(owner_id);
""",
    
    "6. Table WORKSPACE_MEMBERS": """
CREATE TABLE IF NOT EXISTS workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    permissions JSONB DEFAULT '{}',
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user ON workspace_members(user_id);
""",
    
    "7. Table INTEGRATIONS": """
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(100) NOT NULL CHECK (platform IN ('shopify', 'woocommerce', 'stripe', 'paypal', 'mailchimp', 'google_analytics')),
    credentials JSONB NOT NULL,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    connected_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform)
);
CREATE INDEX IF NOT EXISTS idx_integrations_user ON integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_integrations_platform ON integrations(platform);
""",
    
    "8. Table QR_SCAN_EVENTS": """
CREATE TABLE IF NOT EXISTS qr_scan_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_link_id UUID REFERENCES tracking_links(id) ON DELETE CASCADE,
    qr_code_url TEXT NOT NULL,
    scanned_at TIMESTAMP DEFAULT NOW(),
    device_type VARCHAR(50),
    location JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_qr_scan_events_link ON qr_scan_events(tracking_link_id);
CREATE INDEX IF NOT EXISTS idx_qr_scan_events_date ON qr_scan_events(scanned_at);
""",
    
    "9. Table CUSTOM_REPORTS": """
CREATE TABLE IF NOT EXISTS custom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL CHECK (type IN ('sales', 'commissions', 'traffic', 'conversions', 'custom')),
    filters JSONB DEFAULT '{}',
    columns JSONB DEFAULT '[]',
    schedule VARCHAR(50),
    format VARCHAR(20) CHECK (format IN ('pdf', 'csv', 'excel', 'json')),
    is_active BOOLEAN DEFAULT TRUE,
    last_generated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_custom_reports_user ON custom_reports(user_id);
""",
    
    "10. Table TRUST_SCORES": """
CREATE TABLE IF NOT EXISTS trust_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    average_rating DECIMAL(3,2) DEFAULT 0,
    total_reviews INTEGER DEFAULT 0,
    verification_level VARCHAR(50) DEFAULT 'unverified' CHECK (verification_level IN ('unverified', 'email', 'phone', 'id', 'full')),
    fraud_flags INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    response_time INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_trust_scores_user ON trust_scores(user_id);
""",
    
    "11. Table PAYMENT_ACCOUNTS": """
CREATE TABLE IF NOT EXISTS payment_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('bank_transfer', 'paypal', 'stripe', 'wise', 'crypto')),
    account_holder VARCHAR(255) NOT NULL,
    account_number VARCHAR(100),
    bank_name VARCHAR(255),
    iban VARCHAR(34),
    bic VARCHAR(11),
    paypal_email VARCHAR(255),
    crypto_address VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_payment_accounts_user ON payment_accounts(user_id);
""",
    
    "12. Table PRODUCT_REVIEWS": """
CREATE TABLE IF NOT EXISTS product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(product_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_product_reviews_product ON product_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_user ON product_reviews(user_id);
""",
    
    "13. Table CAMPAIGNS": """
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) CHECK (type IN ('email', 'sms', 'social', 'influencer', 'mixed')),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),
    budget DECIMAL(10,2) DEFAULT 0,
    spent DECIMAL(10,2) DEFAULT 0,
    target_audience JSONB DEFAULT '{}',
    kpis JSONB DEFAULT '{}',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_campaigns_user ON campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
""",
    
    "14. Table LEADS": """
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID REFERENCES services(id) ON DELETE SET NULL,
    influencer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES users(id) ON DELETE CASCADE,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(50),
    budget DECIMAL(10,2),
    message TEXT,
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
    source VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_leads_service ON leads(service_id);
CREATE INDEX IF NOT EXISTS idx_leads_influencer ON leads(influencer_id);
CREATE INDEX IF NOT EXISTS idx_leads_merchant ON leads(merchant_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
""",
    
    "15. Table CONTENT_TEMPLATES": """
CREATE TABLE IF NOT EXISTS content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) CHECK (type IN ('email', 'sms', 'social_post', 'landing_page')),
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    category VARCHAR(100),
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_content_templates_user ON content_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_content_templates_type ON content_templates(type);
""",
    
    "16. Codes de parrainage": """
UPDATE users 
SET referral_code = UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8))
WHERE referral_code IS NULL;
"""
}

success_count = 0
error_count = 0
errors = []

for section_name, sql in sections.items():
    print(f"\n▶ {section_name}")
    try:
        # Exécuter via RPC ou directement
        result = supabase.rpc('exec_sql', {'query': sql}).execute()
        print(f"  ✅ Succès")
        success_count += 1
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg or "duplicate" in error_msg.lower():
            print(f"  ℹ️  Déjà existant (ignoré)")
            success_count += 1
        else:
            print(f"  ❌ Erreur: {error_msg[:100]}")
            errors.append((section_name, error_msg))
            error_count += 1

print("\n" + "=" * 80)
print(f" RÉSUMÉ: {success_count} réussies, {error_count} échecs")
print("=" * 80)

if errors:
    print("\n⚠️  ERREURS DÉTAILLÉES:")
    for section, error in errors:
        print(f"\n{section}:")
        print(f"  {error[:200]}")

print("\n✅ Script terminé")
