-- ============================================
-- MIGRATIONS IDEMPOTENTES (SAFE) - ShareYourSales
-- Généré automatiquement
-- Peut être exécuté plusieurs fois sans erreur
-- ============================================


-- ============================================
-- MIGRATION: 001_base_schema.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- ============================================
-- SHAREYOURSALES DATABASE SCHEMA (PostgreSQL/Supabase)
-- ============================================

-- ============================================
-- 1. USERS & AUTHENTICATION
-- ============================================

-- Table principale des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'merchant', 'influencer')),
    phone VARCHAR(20),
    phone_verified BOOLEAN DEFAULT FALSE,
    two_fa_enabled BOOLEAN DEFAULT TRUE,
    two_fa_code VARCHAR(6),
    two_fa_expires_at TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions de connexion
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. MERCHANTS/COMPANIES
-- ============================================

CREATE TABLE IF NOT EXISTS merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    category VARCHAR(100) CHECK (category IN (
        'E-commerce',
        'Services en ligne',
        'Voyage et tourisme',
        'Mode et lifestyle',
        'Beauté et bien-être',
        'Technologie',
        'Finance et assurance',
        'Santé et bien-être',
        'Alimentation et boissons',
        'Divertissement et médias',
        'Automobile',
        'Immobilier',
        'Sport et fitness',
        'Éducation',
        'Bricolage et décoration'
    )),
    address TEXT,
    tax_id VARCHAR(50),
    website VARCHAR(255),
    logo_url TEXT,
    description TEXT,
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('free', 'starter', 'pro', 'enterprise')),
    subscription_status VARCHAR(50) DEFAULT 'active',
    commission_rate DECIMAL(5, 2) DEFAULT 5.00, -- Frais plateforme (%)
    monthly_fee DECIMAL(10, 2) DEFAULT 0.00,
    total_sales DECIMAL(15, 2) DEFAULT 0.00,
    total_commission_paid DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. INFLUENCERS
-- ============================================

CREATE TABLE IF NOT EXISTS influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    bio TEXT,
    profile_picture_url TEXT,
    category VARCHAR(100), -- Mode, Beauté, Fitness, etc.
    influencer_type VARCHAR(50) CHECK (influencer_type IN ('nano', 'micro', 'macro', 'mega')),
    audience_size INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2) DEFAULT 0.00,
    subscription_plan VARCHAR(50) CHECK (subscription_plan IN ('starter', 'pro')),
    subscription_status VARCHAR(50) DEFAULT 'active',
    platform_fee_rate DECIMAL(5, 2) DEFAULT 5.00, -- Frais plateforme (%)
    monthly_fee DECIMAL(10, 2) DEFAULT 9.90,
    
    -- Réseaux sociaux (JSON)
    social_links JSONB DEFAULT '{}', -- {instagram: "url", youtube: "url", tiktok: "url"}
    
    -- Statistiques globales
    total_clicks INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_earnings DECIMAL(15, 2) DEFAULT 0.00,
    balance DECIMAL(15, 2) DEFAULT 0.00, -- Solde disponible
    
    -- Méthodes de paiement
    payment_method VARCHAR(50), -- PayPal, Bank, Crypto
    payment_details JSONB, -- Détails sécurisés du paiement
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. PRODUCTS
-- ============================================

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) CHECK (category IN (
        'Mode', 'Beauté', 'Technologie', 'Alimentation', 
        'Artisanat', 'Sport', 'Santé', 'Maison', 'Autre'
    )),
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Commission pour les affiliés
    commission_rate DECIMAL(5, 2) NOT NULL, -- 10-25%
    commission_type VARCHAR(20) CHECK (commission_type IN ('percentage', 'fixed')),
    
    -- Médias
    images JSONB DEFAULT '[]', -- Array d'URLs d'images
    videos JSONB DEFAULT '[]', -- Array d'URLs de vidéos
    
    -- Caractéristiques
    specifications JSONB, -- Détails techniques
    
    -- Stock & Disponibilité
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    
    -- SEO
    slug VARCHAR(255) UNIQUE,
    meta_description TEXT,
    
    -- Statistiques
    total_views INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. TRACKABLE LINKS (Liens d'affiliation)
-- ============================================

CREATE TABLE IF NOT EXISTS trackable_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    -- Lien unique
    unique_code VARCHAR(50) UNIQUE NOT NULL, -- Code unique crypté
    full_url TEXT NOT NULL, -- URL complète
    short_url TEXT, -- URL raccourcie (optionnel)
    
    -- Offres spéciales
    has_discount BOOLEAN DEFAULT FALSE,
    discount_code VARCHAR(50),
    discount_percentage DECIMAL(5, 2),
    
    -- Statistiques de performance
    clicks INTEGER DEFAULT 0,
    unique_clicks INTEGER DEFAULT 0, -- Clics uniques (IP tracking)
    sales INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    total_revenue DECIMAL(15, 2) DEFAULT 0.00,
    total_commission DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP, -- Expiration du lien (optionnel)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(product_id, influencer_id)
);

-- ============================================
-- 6. SALES (Ventes)
-- ============================================

CREATE TABLE IF NOT EXISTS sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID REFERENCES trackable_links(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    influencer_id UUID REFERENCES influencers(id) ON DELETE SET NULL,
    merchant_id UUID REFERENCES merchants(id) ON DELETE SET NULL,
    
    -- Informations client
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    customer_ip INET,
    
    -- Détails de la vente
    quantity INTEGER DEFAULT 1,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Commissions
    influencer_commission DECIMAL(10, 2) NOT NULL,
    platform_commission DECIMAL(10, 2) NOT NULL,
    merchant_revenue DECIMAL(10, 2) NOT NULL,
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('pending', 'completed', 'refunded', 'cancelled')),
    payment_status VARCHAR(50) CHECK (payment_status IN ('pending', 'paid')),
    
    -- Timestamps
    sale_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_processed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 7. COMMISSIONS (Paiements aux influenceurs)
-- ============================================

CREATE TABLE IF NOT EXISTS commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
    
    -- Paiement
    payment_method VARCHAR(50), -- PayPal, Bank Transfer, Crypto
    transaction_id VARCHAR(255), -- ID transaction externe
    paid_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. ENGAGEMENT METRICS
-- ============================================

CREATE TABLE IF NOT EXISTS engagement_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID REFERENCES trackable_links(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    -- Métriques d'engagement
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    
    -- Métriques de conversion
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    
    -- ROI
    roi_percentage DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Valeur économique
    vep_value DECIMAL(15, 2) DEFAULT 0.00, -- Valeur Économique de la Visibilité
    
    -- CPA (Coût par acquisition)
    cpa DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Date
    metric_date DATE DEFAULT CURRENT_DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(link_id, metric_date)
);

-- ============================================
-- 9. CAMPAIGNS (Campagnes marketing)
-- ============================================

CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Budget
    budget DECIMAL(15, 2),
    spent DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Période
    start_date DATE,
    end_date DATE,
    
    -- Ciblage
    target_audience JSONB, -- {age_range, gender, interests, location}
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    
    -- Performance
    total_clicks INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    total_revenue DECIMAL(15, 2) DEFAULT 0.00,
    roi DECIMAL(10, 2) DEFAULT 0.00,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 10. AI ANALYTICS (Analyses IA)
-- ============================================

CREATE TABLE IF NOT EXISTS ai_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    
    -- Prédictions
    predicted_sales INTEGER,
    trend_score DECIMAL(5, 2), -- Score de tendance (-100 à +100)
    
    -- Recommandations
    recommended_strategy TEXT,
    recommended_budget DECIMAL(15, 2),
    recommended_influencers JSONB, -- Array d'IDs d'influenceurs
    
    -- Insights
    audience_insights JSONB, -- Données démographiques prédites
    competitor_analysis JSONB,
    
    -- Période d'analyse
    analysis_period_start DATE,
    analysis_period_end DATE,
    
    -- Confiance
    confidence_score DECIMAL(5, 2), -- 0-100%
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 11. SUBSCRIPTIONS (Abonnements)
-- ============================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    plan_type VARCHAR(50) CHECK (plan_type IN (
        'free', 'starter', 'pro', 'enterprise',
        'influencer_starter', 'influencer_pro'
    )),
    
    -- Tarification
    monthly_fee DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 2), -- Frais plateforme (%)
    
    -- Limites du plan
    max_products INTEGER,
    max_links INTEGER,
    max_users INTEGER,
    
    -- Features
    features JSONB, -- Array de features incluses
    
    -- Période
    start_date DATE NOT NULL,
    end_date DATE,
    next_billing_date DATE,
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),
    
    -- Paiement
    payment_method VARCHAR(50),
    last_payment_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 12. PAYMENTS (Historique des paiements)
-- ============================================

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    
    -- Montant
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Type
    payment_type VARCHAR(50) CHECK (payment_type IN ('subscription', 'commission', 'refund')),
    
    -- Méthode
    payment_method VARCHAR(50) CHECK (payment_method IN ('credit_card', 'paypal', 'bank_transfer', 'crypto')),
    
    -- Transaction
    transaction_id VARCHAR(255) UNIQUE,
    gateway_response JSONB, -- Réponse du gateway de paiement
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    
    -- Détails
    description TEXT,
    
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 13. REVIEWS & RATINGS
-- ============================================

CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    
    -- Vérification
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    
    -- Modération
    is_approved BOOLEAN DEFAULT TRUE,
    
    -- Utile
    helpful_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 14. CATEGORIES
-- ============================================

CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    icon_url TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 15. CLICKS TRACKING (Détails des clics)
-- ============================================

CREATE TABLE IF NOT EXISTS click_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID REFERENCES trackable_links(id) ON DELETE CASCADE,
    
    -- Informations client
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    
    -- Géolocalisation
    country VARCHAR(2),
    city VARCHAR(100),
    
    -- Device
    device_type VARCHAR(50), -- Mobile, Desktop, Tablet
    os VARCHAR(50),
    browser VARCHAR(50),
    
    -- Session
    session_id VARCHAR(255),
    is_unique_visitor BOOLEAN DEFAULT TRUE,
    
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES pour Performance
-- ============================================

-- Users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Merchants
CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON merchants(user_id);
CREATE INDEX IF NOT EXISTS idx_merchants_category ON merchants(category);

-- Influencers
CREATE INDEX IF NOT EXISTS idx_influencers_user_id ON influencers(user_id);
CREATE INDEX IF NOT EXISTS idx_influencers_username ON influencers(username);
CREATE INDEX IF NOT EXISTS idx_influencers_type ON influencers(influencer_type);

-- Products
CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON products(merchant_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);

-- Trackable Links
CREATE INDEX IF NOT EXISTS idx_trackable_links_code ON trackable_links(unique_code);
CREATE INDEX IF NOT EXISTS idx_trackable_links_product ON trackable_links(product_id);
CREATE INDEX IF NOT EXISTS idx_trackable_links_influencer ON trackable_links(influencer_id);

-- Sales
CREATE INDEX IF NOT EXISTS idx_sales_link_id ON sales(link_id);
CREATE INDEX IF NOT EXISTS idx_sales_influencer_id ON sales(influencer_id);
CREATE INDEX IF NOT EXISTS idx_sales_merchant_id ON sales(merchant_id);
CREATE INDEX IF NOT EXISTS idx_sales_timestamp ON sales(sale_timestamp);
CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(status);

-- Commissions
CREATE INDEX IF NOT EXISTS idx_commissions_influencer_id ON commissions(influencer_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON commissions(status);

-- Click Tracking
CREATE INDEX IF NOT EXISTS idx_click_tracking_link_id ON click_tracking(link_id);
CREATE INDEX IF NOT EXISTS idx_click_tracking_ip ON click_tracking(ip_address);
CREATE INDEX IF NOT EXISTS idx_click_tracking_date ON click_tracking(clicked_at);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger aux tables concernées
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS update_merchants_updated_at ON merchants;
CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON merchants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS update_influencers_updated_at ON influencers;
CREATE TRIGGER update_influencers_updated_at BEFORE UPDATE ON influencers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS update_trackable_links_updated_at ON trackable_links;
CREATE TRIGGER update_trackable_links_updated_at BEFORE UPDATE ON trackable_links FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS pour Rapports
-- ============================================

-- Vue: Performance des influenceurs
CREATE VIEW influencer_performance AS
SELECT 
    i.id,
    i.username,
    i.full_name,
    i.influencer_type,
    i.category,
    COUNT(DISTINCT tl.id) as total_links,
    SUM(tl.clicks) as total_clicks,
    SUM(tl.sales) as total_sales,
    SUM(tl.total_revenue) as total_revenue,
    SUM(tl.total_commission) as total_commission,
    i.balance,
    i.total_earnings
FROM influencers i
LEFT JOIN trackable_links tl ON i.id = tl.influencer_id
GROUP BY i.id;

-- Vue: Performance des produits
CREATE VIEW product_performance AS
SELECT 
    p.id,
    p.name,
    p.category,
    m.company_name as merchant_name,
    COUNT(DISTINCT tl.id) as total_links,
    SUM(tl.clicks) as total_clicks,
    SUM(tl.sales) as total_sales,
    SUM(tl.total_revenue) as total_revenue,
    AVG(r.rating) as average_rating,
    COUNT(r.id) as review_count
FROM products p
JOIN merchants m ON p.merchant_id = m.id
LEFT JOIN trackable_links tl ON p.id = tl.product_id
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.id, m.company_name;

-- Vue: Dashboard Admin
CREATE VIEW admin_dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM users WHERE role = 'influencer') as total_influencers,
    (SELECT COUNT(*) FROM users WHERE role = 'merchant') as total_merchants,
    (SELECT COUNT(*) FROM products WHERE is_available = TRUE) as active_products,
    (SELECT SUM(total_revenue) FROM trackable_links) as total_platform_revenue,
    (SELECT SUM(total_commission) FROM trackable_links) as total_commissions_paid,
    (SELECT COUNT(*) FROM sales WHERE status = 'completed') as total_sales,
    (SELECT COUNT(*) FROM trackable_links WHERE is_active = TRUE) as active_links;

-- ============================================
-- SEED DATA (Données initiales)
-- ============================================

-- Table de configuration SMTP (ajoutée après déploiement initial)
CREATE TABLE IF NOT EXISTS smtp_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    host VARCHAR(255) NOT NULL DEFAULT 'smtp.gmail.com',
    port INTEGER NOT NULL DEFAULT 587,
    username VARCHAR(255),
    password VARCHAR(255),
    from_email VARCHAR(255) NOT NULL DEFAULT 'noreply@shareyoursales.com',
    from_name VARCHAR(255) NOT NULL DEFAULT 'Share Your Sales',
    encryption VARCHAR(10) CHECK (encryption IN ('tls', 'ssl', 'none')) DEFAULT 'tls',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catégories de base
INSERT INTO categories (name, slug, description, display_order) VALUES
('Mode', 'mode', 'Vêtements, accessoires, chaussures', 1),
('Beauté', 'beaute', 'Cosmétiques, soins, parfums', 2),
('Technologie', 'technologie', 'Électronique, gadgets, informatique', 3),
('Alimentation', 'alimentation', 'Produits alimentaires, boissons', 4),
('Artisanat', 'artisanat', 'Produits artisanaux, fait main', 5),
('Sport', 'sport', 'Équipements sportifs, fitness', 6),
('Maison', 'maison', 'Décoration, meubles, électroménager', 7),
('Santé', 'sante', 'Compléments, bien-être', 8);

-- Admin par défaut (mot de passe: Admin123!)
INSERT INTO users (email, password_hash, role, phone, phone_verified) VALUES
('admin@shareyoursales.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIiLDDyQRW', 'admin', '+33600000000', TRUE);



-- ============================================
-- MIGRATION: 002_add_smtp_settings.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- =============================================================================
-- Migration 002: Configuration SMTP
-- Description: Ajoute la table smtp_settings pour la configuration email
-- Date: 2025-10-27
-- =============================================================================

CREATE TABLE IF NOT EXISTS smtp_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    host VARCHAR(255) NOT NULL DEFAULT 'smtp.gmail.com',
    port INTEGER NOT NULL DEFAULT 587,
    username VARCHAR(255),
    password VARCHAR(255),
    from_email VARCHAR(255) NOT NULL DEFAULT 'noreply@shareyoursales.com',
    from_name VARCHAR(255) NOT NULL DEFAULT 'Share Your Sales',
    encryption VARCHAR(10) CHECK (encryption IN ('tls', 'ssl', 'none')) DEFAULT 'tls',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_smtp_settings_user_id ON smtp_settings(user_id);

-- Commentaire
COMMENT ON TABLE smtp_settings IS 'Configuration SMTP pour l''envoi d''emails par utilisateur';

-- =============================================================================
-- Fin de la migration 002
-- =============================================================================



-- ============================================
-- MIGRATION: 003_add_email_verification.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- =============================================================================
-- Migration: Email Verification Support
-- Description: Adds columns required to manage email verification workflow.
-- Date: 2025-10-26
-- =============================================================================

-- 1. Columns for email verification state
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS verification_token TEXT,
    ADD COLUMN IF NOT EXISTS verification_expires TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS verification_sent_at TIMESTAMP WITH TIME ZONE;

-- 2. Ensure future rows default to not verified
ALTER TABLE users ALTER COLUMN email_verified SET DEFAULT FALSE;

-- 3. Backfill legacy rows so existing accounts remain usable
UPDATE users
SET email_verified = COALESCE(email_verified, TRUE)
WHERE email_verified IS NULL;

-- 4. Index token lookups for verification endpoints
CREATE INDEX IF NOT EXISTS idx_users_verification_token
    ON users(verification_token)
    WHERE verification_token IS NOT NULL;



-- ============================================
-- MIGRATION: 004_add_company_settings.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- Migration: Ajout de la table company_settings pour les paramètres d'entreprise
-- Date: 2025-10-23
-- Description: Permet aux merchants de configurer les informations de leur entreprise

-- Créer la table company_settings
CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    email VARCHAR(255),
    address TEXT,
    tax_id VARCHAR(50),
    currency VARCHAR(3) DEFAULT 'MAD',
    phone VARCHAR(20),
    website VARCHAR(255),
    logo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Un seul paramètre par utilisateur
    UNIQUE(user_id)
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_company_settings_user_id ON company_settings(user_id);

-- Commentaires
COMMENT ON TABLE company_settings IS 'Paramètres de l''entreprise pour chaque merchant';
COMMENT ON COLUMN company_settings.user_id IS 'ID de l''utilisateur (merchant)';
COMMENT ON COLUMN company_settings.name IS 'Nom de l''entreprise';
COMMENT ON COLUMN company_settings.email IS 'Email de contact de l''entreprise';
COMMENT ON COLUMN company_settings.address IS 'Adresse complète de l''entreprise';
COMMENT ON COLUMN company_settings.tax_id IS 'Numéro de TVA ou identifiant fiscal';
COMMENT ON COLUMN company_settings.currency IS 'Devise par défaut (EUR, USD, GBP, MAD)';
COMMENT ON COLUMN company_settings.phone IS 'Numéro de téléphone de l''entreprise';
COMMENT ON COLUMN company_settings.website IS 'Site web de l''entreprise';
COMMENT ON COLUMN company_settings.logo_url IS 'URL du logo de l''entreprise';



-- ============================================
-- MIGRATION: 005_add_all_settings_tables.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- ============================================
-- MIGRATION: Ajout tables de settings
-- Date: 2025-10-23
-- Description: Tables pour tous les paramètres d'application
-- ============================================

-- Table permissions_settings
CREATE TABLE IF NOT EXISTS permissions_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    visible_screens JSONB DEFAULT '{"performance": true, "clicks": true, "impressions": false, "conversions": true, "leads": true, "references": true, "campaigns": true, "lost_orders": false}'::jsonb,
    visible_fields JSONB DEFAULT '{"conversion_amount": true, "short_link": true, "conversion_order_id": true}'::jsonb,
    authorized_actions JSONB DEFAULT '{"api_access": true, "view_personal_info": true}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table affiliate_settings
CREATE TABLE IF NOT EXISTS affiliate_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    min_withdrawal DECIMAL(10,2) DEFAULT 50.00,
    auto_approval BOOLEAN DEFAULT FALSE,
    email_verification BOOLEAN DEFAULT TRUE,
    payment_mode VARCHAR(20) CHECK (payment_mode IN ('on_demand', 'automatic')) DEFAULT 'on_demand',
    single_campaign_mode BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table registration_settings
CREATE TABLE IF NOT EXISTS registration_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    allow_affiliate_registration BOOLEAN DEFAULT TRUE,
    allow_advertiser_registration BOOLEAN DEFAULT TRUE,
    require_invitation BOOLEAN DEFAULT FALSE,
    require_2fa BOOLEAN DEFAULT FALSE,
    country_required BOOLEAN DEFAULT TRUE,
    company_name_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table mlm_settings
CREATE TABLE IF NOT EXISTS mlm_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    mlm_enabled BOOLEAN DEFAULT TRUE,
    levels JSONB DEFAULT '[
        {"level": 1, "percentage": 10, "enabled": true},
        {"level": 2, "percentage": 5, "enabled": true},
        {"level": 3, "percentage": 2.5, "enabled": true},
        {"level": 4, "percentage": 0, "enabled": false},
        {"level": 5, "percentage": 0, "enabled": false},
        {"level": 6, "percentage": 0, "enabled": false},
        {"level": 7, "percentage": 0, "enabled": false},
        {"level": 8, "percentage": 0, "enabled": false},
        {"level": 9, "percentage": 0, "enabled": false},
        {"level": 10, "percentage": 0, "enabled": false}
    ]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table whitelabel_settings
CREATE TABLE IF NOT EXISTS whitelabel_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#3b82f6',
    secondary_color VARCHAR(7) DEFAULT '#1e40af',
    accent_color VARCHAR(7) DEFAULT '#10b981',
    company_name VARCHAR(255) DEFAULT 'Share Your Sales Platform',
    custom_domain VARCHAR(255) DEFAULT 'track.votredomaine.com',
    ssl_enabled BOOLEAN DEFAULT TRUE,
    custom_email_domain VARCHAR(255) DEFAULT 'noreply@votredomaine.com',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer les index
CREATE INDEX IF NOT EXISTS idx_permissions_settings_user_id ON permissions_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_affiliate_settings_user_id ON affiliate_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_registration_settings_user_id ON registration_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_mlm_settings_user_id ON mlm_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_whitelabel_settings_user_id ON whitelabel_settings(user_id);

-- Ajouter les triggers pour updated_at (avec DROP IF EXISTS pour éviter les erreurs)
DROP TRIGGER IF EXISTS update_permissions_settings_updated_at ON permissions_settings;
CREATE TRIGGER update_permissions_settings_updated_at 
    BEFORE UPDATE ON permissions_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_affiliate_settings_updated_at ON affiliate_settings;
CREATE TRIGGER update_affiliate_settings_updated_at 
    BEFORE UPDATE ON affiliate_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_registration_settings_updated_at ON registration_settings;
CREATE TRIGGER update_registration_settings_updated_at 
    BEFORE UPDATE ON registration_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mlm_settings_updated_at ON mlm_settings;
CREATE TRIGGER update_mlm_settings_updated_at 
    BEFORE UPDATE ON mlm_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_whitelabel_settings_updated_at ON whitelabel_settings;
CREATE TRIGGER update_whitelabel_settings_updated_at 
    BEFORE UPDATE ON whitelabel_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Vérification
SELECT 'Toutes les tables de settings créées avec succès!' as status;



-- ============================================
-- MIGRATION: 006_create_subscription_and_support_tables.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- Migration SQL pour créer les tables d'abonnements, support, vidéos et documentation
-- À exécuter dans Supabase Dashboard > SQL Editor

-- ============================================================
-- TABLE: user_subscriptions
-- ============================================================
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type TEXT NOT NULL CHECK (plan_type IN ('free', 'starter', 'pro', 'enterprise', 'merchant_basic', 'merchant_standard', 'merchant_premium', 'merchant_enterprise')),
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled', 'expired', 'pending')) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    auto_renew BOOLEAN DEFAULT true,
    payment_method TEXT,
    last_payment_date TIMESTAMP,
    next_billing_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: support_tickets
-- ============================================================
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('technical', 'billing', 'account', 'feature_request', 'other')),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'waiting_response', 'resolved', 'closed')) DEFAULT 'open',
    description TEXT NOT NULL,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- ============================================================
-- TABLE: ticket_messages
-- ============================================================
CREATE TABLE IF NOT EXISTS ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    attachments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: video_tutorials
-- ============================================================
CREATE TABLE IF NOT EXISTS video_tutorials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    video_url TEXT NOT NULL,
    thumbnail_url TEXT,
    duration INTEGER, -- en secondes
    category TEXT NOT NULL CHECK (category IN ('getting_started', 'influencer', 'merchant', 'admin', 'advanced')),
    difficulty TEXT NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')) DEFAULT 'beginner',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_published BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: video_progress
-- ============================================================
CREATE TABLE IF NOT EXISTS video_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES video_tutorials(id) ON DELETE CASCADE,
    progress_seconds INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT false,
    last_watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, video_id)
);

-- ============================================================
-- TABLE: documentation_articles
-- ============================================================
CREATE TABLE IF NOT EXISTS documentation_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('getting_started', 'influencer', 'merchant', 'api', 'troubleshooting', 'faq')),
    tags TEXT[],
    views INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT true,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEX POUR PERFORMANCE
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_assigned ON support_tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket ON ticket_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_user ON ticket_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_video_tutorials_category ON video_tutorials(category);
CREATE INDEX IF NOT EXISTS idx_video_tutorials_published ON video_tutorials(is_published);
CREATE INDEX IF NOT EXISTS idx_video_progress_user ON video_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_video_progress_video ON video_progress(video_id);
CREATE INDEX IF NOT EXISTS idx_documentation_slug ON documentation_articles(slug);
CREATE INDEX IF NOT EXISTS idx_documentation_category ON documentation_articles(category);
CREATE INDEX IF NOT EXISTS idx_documentation_published ON documentation_articles(is_published);

-- ============================================================
-- TRIGGERS POUR UPDATED_AT
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_user_subscriptions_updated_at ON user_subscriptions;
CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_support_tickets_updated_at ON support_tickets;
CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_video_tutorials_updated_at ON video_tutorials;
CREATE TRIGGER update_video_tutorials_updated_at BEFORE UPDATE ON video_tutorials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_documentation_articles_updated_at ON documentation_articles;
CREATE TRIGGER update_documentation_articles_updated_at BEFORE UPDATE ON documentation_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VÉRIFICATION
-- ============================================================
SELECT 
    'user_subscriptions' as table_name,
    COUNT(*) as row_count
FROM user_subscriptions
UNION ALL
SELECT 'support_tickets', COUNT(*) FROM support_tickets
UNION ALL
SELECT 'ticket_messages', COUNT(*) FROM ticket_messages
UNION ALL
SELECT 'video_tutorials', COUNT(*) FROM video_tutorials
UNION ALL
SELECT 'video_progress', COUNT(*) FROM video_progress
UNION ALL
SELECT 'documentation_articles', COUNT(*) FROM documentation_articles;



-- ⏭️  MIGRATION VIDE: 007_add_tracking_tables.sql


-- ============================================
-- MIGRATION: 008_cleanup_old_affiliation_system.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- Migration pour nettoyer l'ancien système dual-table d'affiliation
-- Supprimer l'ancienne table affiliation_requests et toutes les références associées

-- Supprimer la table affiliation_requests si elle existe
DROP TABLE IF EXISTS affiliation_requests CASCADE;

-- Supprimer les anciennes vues si elles existent encore (au cas où)
DROP VIEW IF EXISTS old_affiliation_requests CASCADE;
DROP VIEW IF EXISTS old_merchant_affiliation_requests CASCADE;

-- Supprimer les anciennes fonctions si elles existent encore
DROP FUNCTION IF EXISTS old_create_affiliation_request(UUID, UUID, TEXT) CASCADE;
DROP FUNCTION IF EXISTS old_approve_affiliation_request(UUID, TEXT, UUID) CASCADE;
DROP FUNCTION IF EXISTS old_reject_affiliation_request(UUID, TEXT, UUID) CASCADE;

-- Commentaire sur la migration
COMMENT ON DATABASE postgres IS 'Système d''affiliation unifié migré - ancienne table affiliation_requests supprimée';



-- ============================================
-- MIGRATION: 009_add_affiliation_requests.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- ============================================
-- SYSTÈME DE DEMANDES D'AFFILIATION
-- Date: 2025-10-23
-- ============================================

-- Table pour les demandes d'affiliation
CREATE TABLE IF NOT EXISTS affiliation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    
    -- Informations de la demande
    message TEXT, -- Message de l'influenceur au marchand
    influencer_stats JSONB, -- Statistiques de l'influenceur (followers, engagement, etc.)
    
    -- Statut de la demande
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    
    -- Réponse du marchand
    merchant_response TEXT,
    reviewed_at TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    UNIQUE(influencer_id, product_id), -- Un influenceur ne peut faire qu'une demande par produit
    CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled'))
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_influencer ON affiliation_requests(influencer_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_merchant ON affiliation_requests(merchant_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_product ON affiliation_requests(product_id);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_status ON affiliation_requests(status);
CREATE INDEX IF NOT EXISTS idx_affiliation_requests_created ON affiliation_requests(created_at DESC);

-- Table pour l'historique des demandes
CREATE TABLE IF NOT EXISTS affiliation_request_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES affiliation_requests(id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by UUID REFERENCES users(id),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_affiliation_request_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour updated_at
DROP TRIGGER IF EXISTS update_affiliation_request_modtime ON affiliation_requests;
CREATE TRIGGER update_affiliation_request_modtime
    BEFORE UPDATE ON affiliation_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_affiliation_request_timestamp();

-- Trigger pour créer un lien de tracking automatiquement après approbation
CREATE OR REPLACE FUNCTION create_tracking_link_on_approval()
RETURNS TRIGGER AS $$
BEGIN
    -- Si la demande vient d'être approuvée
    IF NEW.status = 'approved' AND OLD.status = 'pending' THEN
        -- Créer un lien de tracking dans trackable_links
        INSERT INTO trackable_links (
            influencer_id,
            product_id,
            unique_code,
            is_active
        )
        VALUES (
            NEW.influencer_id,
            NEW.product_id,
            substring(md5(random()::text || NEW.influencer_id::text || NEW.product_id::text) from 1 for 8),
            true
        );
        
        -- Enregistrer dans l'historique
        INSERT INTO affiliation_request_history (
            request_id,
            old_status,
            new_status,
            changed_by,
            comment
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            NEW.reviewed_by,
            'Demande approuvée - Lien de tracking créé automatiquement'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS auto_create_tracking_link ON affiliation_requests;
CREATE TRIGGER auto_create_tracking_link
    AFTER UPDATE ON affiliation_requests
    FOR EACH ROW
    WHEN (NEW.status = 'approved' AND OLD.status != 'approved')
    EXECUTE FUNCTION create_tracking_link_on_approval();

-- Vue pour les statistiques des demandes
CREATE OR REPLACE VIEW affiliation_requests_stats AS
SELECT 
    merchant_id,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_requests,
    COUNT(*) FILTER (WHERE status = 'approved') as approved_requests,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_requests,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
        NULLIF(COUNT(*) FILTER (WHERE status != 'pending')::numeric, 0) * 100, 
        2
    ) as approval_rate
FROM affiliation_requests
GROUP BY merchant_id;

-- Vue détaillée des demandes pour les influenceurs
CREATE OR REPLACE VIEW influencer_affiliation_requests AS
SELECT 
    ar.id,
    ar.influencer_id,
    ar.product_id,
    ar.merchant_id,
    ar.status,
    ar.message,
    ar.merchant_response,
    ar.created_at,
    ar.reviewed_at,
    
    -- Informations produit
    p.name as product_name,
    p.description as product_description,
    p.commission_rate,
    p.price as product_price,
    
    -- Informations marchand
    m.company_name as merchant_company
    
FROM affiliation_requests ar
LEFT JOIN products p ON ar.product_id = p.id
LEFT JOIN merchants m ON ar.merchant_id = m.id;

-- Vue détaillée des demandes pour les marchands
CREATE OR REPLACE VIEW merchant_affiliation_requests AS
SELECT 
    ar.id,
    ar.influencer_id,
    ar.product_id,
    ar.merchant_id,
    ar.status,
    ar.message,
    ar.influencer_stats,
    ar.merchant_response,
    ar.created_at,
    ar.reviewed_at,
    
    -- Informations influenceur
    u.email as influencer_email,
    inf.full_name as influencer_name,
    inf.profile_picture_url as influencer_avatar,
    
    -- Informations produit
    p.name as product_name,
    p.commission_rate,
    p.price as product_price,
    
    -- Statistiques influenceur (si disponibles)
    (ar.influencer_stats->>'followers')::integer as followers_count,
    (ar.influencer_stats->>'engagement_rate')::numeric as engagement_rate,
    ar.influencer_stats->>'platforms' as platforms
    
FROM affiliation_requests ar
LEFT JOIN influencers inf ON ar.influencer_id = inf.id
LEFT JOIN users u ON inf.user_id = u.id
LEFT JOIN products p ON ar.product_id = p.id;

COMMENT ON TABLE affiliation_requests IS 'Demandes d''affiliation des influenceurs pour les produits';
COMMENT ON COLUMN affiliation_requests.status IS 'pending: en attente, approved: approuvée, rejected: refusée, cancelled: annulée';
COMMENT ON COLUMN affiliation_requests.influencer_stats IS 'Statistiques JSON de l''influenceur (followers, engagement, etc.)';



-- ============================================
-- MIGRATION: 010_modify_trackable_links_unified.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- ============================================
-- MODIFICATION SYSTÈME AFFILIATION UNIFIÉ
-- Date: 2025-10-23
-- ============================================

-- ÉTAPE 1: Supprimer les vues qui dépendent de trackable_links (si elles existent)
DROP VIEW IF EXISTS merchant_affiliation_requests CASCADE;
DROP VIEW IF EXISTS affiliation_requests_stats CASCADE;
DROP VIEW IF EXISTS influencer_affiliation_requests CASCADE;

-- ÉTAPE 2: Vérifier si trackable_links est une vue ou une table
-- Si c'est une vue, la supprimer et créer la table
DO $$
BEGIN
    -- Vérifier si trackable_links est une vue
    IF EXISTS (
        SELECT 1 FROM information_schema.views 
        WHERE table_schema = 'public' 
        AND table_name = 'trackable_links'
    ) THEN
        -- C'est une vue, la supprimer
        DROP VIEW IF EXISTS trackable_links CASCADE;
        RAISE NOTICE 'Vue trackable_links supprimée';
    END IF;
END $$;

-- ÉTAPE 3: Ajouter les colonnes nécessaires pour les demandes d'affiliation
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS influencer_message TEXT;
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS merchant_response TEXT;
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS reviewed_by UUID REFERENCES users(id);

-- Ajouter la colonne status si elle n'existe pas
ALTER TABLE trackable_links ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending_approval';

-- Modifier le statut par défaut et les contraintes
ALTER TABLE trackable_links ALTER COLUMN status SET DEFAULT 'pending_approval';
ALTER TABLE trackable_links DROP CONSTRAINT IF EXISTS trackable_links_status_check;
ALTER TABLE trackable_links ADD CONSTRAINT trackable_links_status_check
    CHECK (status IN ('pending_approval', 'active', 'rejected', 'inactive'));

-- Créer un index pour les statuts
CREATE INDEX IF NOT EXISTS idx_trackable_links_status ON trackable_links(status);

-- Vue pour les demandes d'affiliation des marchands (remplace merchant_affiliation_requests)
CREATE OR REPLACE VIEW merchant_affiliation_requests AS
SELECT
    tl.id,
    tl.influencer_id,
    tl.product_id,
    tl.status,
    tl.influencer_message,
    tl.merchant_response,
    tl.created_at,
    tl.reviewed_at,

    -- Informations influenceur
    u.email as influencer_email,
    inf.full_name as influencer_name,
    inf.profile_picture_url as influencer_avatar,

    -- Informations produit
    p.name as product_name,
    p.commission_rate,
    p.price as product_price,

    -- Informations marchand (pour filtrage)
    p.merchant_id

FROM trackable_links tl
LEFT JOIN influencers inf ON tl.influencer_id = inf.id
LEFT JOIN users u ON inf.user_id = u.id
LEFT JOIN products p ON tl.product_id = p.id
WHERE tl.status IN ('pending_approval', 'active', 'rejected');

-- Vue pour les statistiques des demandes d'affiliation
CREATE OR REPLACE VIEW affiliation_requests_stats AS
SELECT
    p.merchant_id,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE tl.status = 'pending_approval') as pending_requests,
    COUNT(*) FILTER (WHERE tl.status = 'active') as approved_requests,
    COUNT(*) FILTER (WHERE tl.status = 'rejected') as rejected_requests,
    ROUND(
        COUNT(*) FILTER (WHERE tl.status = 'active')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE tl.status IN ('active', 'rejected'))::numeric, 0) * 100,
        2
    ) as approval_rate
FROM trackable_links tl
LEFT JOIN products p ON tl.product_id = p.id
WHERE tl.status IN ('pending_approval', 'active', 'rejected')
GROUP BY p.merchant_id;

-- Fonction pour approuver une demande d'affiliation (modifie le statut et génère le short_code)
CREATE OR REPLACE FUNCTION approve_affiliation_request(
    p_request_id UUID,
    p_merchant_response TEXT,
    p_reviewed_by UUID
) RETURNS VOID AS $$
DECLARE
    v_influencer_id UUID;
    v_product_id UUID;
BEGIN
    -- Récupérer les informations de la demande
    SELECT influencer_id, product_id INTO v_influencer_id, v_product_id
    FROM trackable_links
    WHERE id = p_request_id AND status = 'pending_approval';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Demande non trouvée ou déjà traitée';
    END IF;

    -- Générer le short_code unique et approuver
    UPDATE trackable_links SET
        status = 'active',
        merchant_response = p_merchant_response,
        reviewed_at = CURRENT_TIMESTAMP,
        reviewed_by = p_reviewed_by,
        unique_code = substring(md5(random()::text || v_influencer_id::text || v_product_id::text || CURRENT_TIMESTAMP::text) from 1 for 8),
        is_active = true
    WHERE id = p_request_id;

END;
$$ LANGUAGE plpgsql;

-- Fonction pour refuser une demande d'affiliation
CREATE OR REPLACE FUNCTION reject_affiliation_request(
    p_request_id UUID,
    p_merchant_response TEXT,
    p_reviewed_by UUID
) RETURNS VOID AS $$
BEGIN
    UPDATE trackable_links SET
        status = 'rejected',
        merchant_response = p_merchant_response,
        reviewed_at = CURRENT_TIMESTAMP,
        reviewed_by = p_reviewed_by
    WHERE id = p_request_id AND status = 'pending_approval';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Demande non trouvée ou déjà traitée';
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE trackable_links IS 'Liens de tracking et demandes d''affiliation unifiées';
COMMENT ON COLUMN trackable_links.status IS 'pending_approval: en attente, active: approuvé, rejected: refusé, inactive: inactif';
COMMENT ON COLUMN trackable_links.influencer_message IS 'Message de l''influenceur lors de la demande';
COMMENT ON COLUMN trackable_links.merchant_response IS 'Réponse du marchand (approbation ou refus)';



-- ============================================
-- MIGRATION: 011_add_payment_columns.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- ============================================
-- MIGRATION: Ajout des colonnes pour paiements automatiques
-- Date: 2025-10-23
-- ============================================

-- 1. Ajouter colonne updated_at aux sales si manquante
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='sales' AND column_name='updated_at') THEN
        ALTER TABLE sales ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- 2. Ajouter colonne approved_at aux commissions si manquante
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='commissions' AND column_name='approved_at') THEN
        ALTER TABLE commissions ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;
    END IF;
END $$;

-- 3. Créer la table payouts si elle n'existe pas
CREATE TABLE IF NOT EXISTS payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    
    -- Montant
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Statut du paiement
    status VARCHAR(50) CHECK (status IN ('pending', 'processing', 'approved', 'paid', 'rejected', 'failed')),
    
    -- Méthode
    payment_method VARCHAR(50),
    
    -- Transaction
    transaction_id VARCHAR(255),
    
    -- Dates
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    paid_at TIMESTAMP,
    
    -- Notes
    notes TEXT,
    is_automatic BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Créer la table notifications si elle n'existe pas
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Type de notification
    type VARCHAR(50) NOT NULL,
    
    -- Contenu
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Lien optionnel
    link VARCHAR(500),
    
    -- Statut
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Métadonnées
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Ajouter index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_payouts_influencer ON payouts(influencer_id);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_sales_status_created ON sales(status, created_at);
CREATE INDEX IF NOT EXISTS idx_sales_influencer ON sales(influencer_id);

-- 6. Ajouter les colonnes payment_details si manquantes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='influencers' AND column_name='payment_details') THEN
        ALTER TABLE influencers ADD COLUMN IF NOT EXISTS payment_details JSONB;
    END IF;
END $$;

-- 7. Mettre à jour les sales existantes sans updated_at
UPDATE sales 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- 8. Afficher le résumé
DO $$
DECLARE
    sales_count INTEGER;
    commissions_count INTEGER;
    payouts_count INTEGER;
    notifications_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO sales_count FROM sales;
    SELECT COUNT(*) INTO commissions_count FROM commissions;
    SELECT COUNT(*) INTO payouts_count FROM payouts;
    SELECT COUNT(*) INTO notifications_count FROM notifications;
    
    RAISE NOTICE '============================================';
    RAISE NOTICE 'MIGRATION TERMINÉE AVEC SUCCÈS';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Ventes: %', sales_count;
    RAISE NOTICE 'Commissions: %', commissions_count;
    RAISE NOTICE 'Payouts: %', payouts_count;
    RAISE NOTICE 'Notifications: %', notifications_count;
    RAISE NOTICE '============================================';
END $$;



-- ============================================
-- MIGRATION: 012_add_payment_gateways.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- ============================================================================
-- MIGRATION: Système de Gateways de Paiement Multi-Gateway (Maroc)
-- Description: Support CMI, PayZen, Société Générale Maroc
-- Date: 2025-10-23
-- ============================================================================

-- ============================================================================
-- 1. ALTER TABLE: merchants - Ajouter configuration gateway
-- ============================================================================
ALTER TABLE merchants
ADD COLUMN IF NOT EXISTS payment_gateway VARCHAR(50) DEFAULT 'manual',
ADD COLUMN IF NOT EXISTS gateway_config JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS auto_debit_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS gateway_activated_at TIMESTAMP;

COMMENT ON COLUMN merchants.payment_gateway IS 'Gateway utilisé: manual, cmi, payzen, sg_maroc';
COMMENT ON COLUMN merchants.gateway_config IS 'Configuration JSON du gateway (API keys, merchant IDs, etc.)';
COMMENT ON COLUMN merchants.auto_debit_enabled IS 'Si TRUE, prélèvement automatique activé';

-- ============================================================================
-- 2. CREATE TABLE: platform_invoices
-- Description: Factures émises par la plateforme aux merchants
-- ============================================================================
CREATE TABLE IF NOT EXISTS platform_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    
    -- Numérotation
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    
    -- Période facturée
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Montants
    total_sales_amount DECIMAL(10, 2) DEFAULT 0,
    platform_commission DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    
    -- Devise
    currency VARCHAR(3) DEFAULT 'MAD',
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    -- Status possibles: pending, sent, viewed, paid, overdue, cancelled
    
    -- Paiement
    payment_method VARCHAR(50),  -- manual, cmi, payzen, sg_maroc
    paid_at TIMESTAMP,
    payment_reference VARCHAR(255),
    
    -- Fichiers
    pdf_url TEXT,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_platform_invoices_merchant ON platform_invoices(merchant_id);
CREATE INDEX IF NOT EXISTS idx_platform_invoices_status ON platform_invoices(status);
CREATE INDEX IF NOT EXISTS idx_platform_invoices_due_date ON platform_invoices(due_date);
CREATE INDEX IF NOT EXISTS idx_platform_invoices_number ON platform_invoices(invoice_number);

-- ============================================================================
-- 3. CREATE TABLE: invoice_line_items
-- Description: Détail des lignes de facture (ventes individuelles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES platform_invoices(id) ON DELETE CASCADE,
    sale_id UUID REFERENCES sales(id) ON DELETE SET NULL,
    
    -- Détails
    description TEXT NOT NULL,
    sale_date DATE,
    sale_amount DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 2),
    commission_amount DECIMAL(10, 2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invoice_line_items_invoice ON invoice_line_items(invoice_id);
CREATE INDEX IF NOT EXISTS idx_invoice_line_items_sale ON invoice_line_items(sale_id);

-- ============================================================================
-- 4. CREATE TABLE: gateway_transactions
-- Description: Historique des transactions avec les gateways de paiement
-- ============================================================================
CREATE TABLE IF NOT EXISTS gateway_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES platform_invoices(id) ON DELETE SET NULL,
    
    -- Gateway
    gateway VARCHAR(50) NOT NULL,  -- cmi, payzen, sg_maroc
    transaction_id VARCHAR(255),  -- ID externe du gateway
    order_id VARCHAR(255),  -- ID de commande interne
    
    -- Montants
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'MAD',
    fees DECIMAL(10, 2) DEFAULT 0,
    net_amount DECIMAL(10, 2),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    -- Status possibles: pending, processing, completed, failed, refunded, cancelled
    failure_reason TEXT,
    
    -- URLs
    payment_url TEXT,
    redirect_url TEXT,
    
    -- Données
    request_payload JSONB,
    response_payload JSONB,
    webhook_payload JSONB,
    
    -- Sécurité
    signature VARCHAR(500),
    ip_address VARCHAR(45),
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gateway_transactions_merchant ON gateway_transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_gateway_transactions_invoice ON gateway_transactions(invoice_id);
CREATE INDEX IF NOT EXISTS idx_gateway_transactions_status ON gateway_transactions(status);
CREATE INDEX IF NOT EXISTS idx_gateway_transactions_gateway ON gateway_transactions(gateway);
CREATE INDEX IF NOT EXISTS idx_gateway_transactions_transaction_id ON gateway_transactions(transaction_id);

-- ============================================================================
-- 5. CREATE TABLE: payment_gateway_logs
-- Description: Logs détaillés des communications avec les gateways
-- ============================================================================
CREATE TABLE IF NOT EXISTS payment_gateway_logs (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID REFERENCES gateway_transactions(id) ON DELETE CASCADE,
    
    -- Type d'événement
    event_type VARCHAR(100) NOT NULL,
    -- Types: api_request, api_response, webhook_received, signature_verified, error
    
    -- Données
    request_url TEXT,
    request_method VARCHAR(10),
    request_headers JSONB,
    request_body JSONB,
    response_status INTEGER,
    response_headers JSONB,
    response_body JSONB,
    
    -- Erreur
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- Performance
    response_time_ms INTEGER,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_gateway_logs_transaction ON payment_gateway_logs(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payment_gateway_logs_event_type ON payment_gateway_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_payment_gateway_logs_created_at ON payment_gateway_logs(created_at DESC);

-- ============================================================================
-- 6. CREATE FUNCTION: Generate Invoice Number
-- Description: Génère un numéro de facture unique (Format: INV-2025-10-0001)
-- ============================================================================
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    current_year VARCHAR(4);
    current_month VARCHAR(2);
    last_number INTEGER;
    new_number VARCHAR(4);
BEGIN
    current_year := TO_CHAR(CURRENT_DATE, 'YYYY');
    current_month := TO_CHAR(CURRENT_DATE, 'MM');
    
    -- Récupérer le dernier numéro du mois
    SELECT COALESCE(
        MAX(
            CAST(
                SUBSTRING(invoice_number FROM '[0-9]+$') AS INTEGER
            )
        ), 0
    ) INTO last_number
    FROM platform_invoices
    WHERE invoice_number LIKE 'INV-' || current_year || '-' || current_month || '-%';
    
    -- Incrémenter
    new_number := LPAD((last_number + 1)::TEXT, 4, '0');
    
    RETURN 'INV-' || current_year || '-' || current_month || '-' || new_number;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. CREATE FUNCTION: Auto-update updated_at
-- Description: Trigger pour mettre à jour automatiquement updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer aux tables appropriées
CREATE TRIGGER update_platform_invoices_updated_at
    BEFORE UPDATE ON platform_invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gateway_transactions_updated_at
    BEFORE UPDATE ON gateway_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. MATERIALIZED VIEW: Gateway Statistics
-- Description: Statistiques agrégées par gateway
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS gateway_statistics CASCADE;

CREATE MATERIALIZED VIEW gateway_statistics AS
SELECT
    gt.gateway,
    COUNT(DISTINCT gt.id) AS total_transactions,
    COUNT(DISTINCT CASE WHEN gt.status = 'completed' THEN gt.id END) AS successful_transactions,
    COUNT(DISTINCT CASE WHEN gt.status = 'failed' THEN gt.id END) AS failed_transactions,
    ROUND(
        COUNT(DISTINCT CASE WHEN gt.status = 'completed' THEN gt.id END)::NUMERIC * 100.0 /
        NULLIF(COUNT(DISTINCT gt.id), 0),
        2
    ) AS success_rate,
    SUM(CASE WHEN gt.status = 'completed' THEN gt.amount ELSE 0 END) AS total_amount_processed,
    SUM(CASE WHEN gt.status = 'completed' THEN gt.fees ELSE 0 END) AS total_fees_paid,
    SUM(CASE WHEN gt.status = 'completed' THEN gt.net_amount ELSE 0 END) AS total_net_amount,
    AVG(CASE WHEN gt.status = 'completed' THEN EXTRACT(EPOCH FROM (gt.completed_at - gt.initiated_at)) END) AS avg_completion_time_seconds,
    MAX(gt.created_at) AS last_transaction_date
FROM gateway_transactions gt
GROUP BY gt.gateway;

CREATE INDEX IF NOT EXISTS idx_gateway_statistics_gateway ON gateway_statistics(gateway);

-- ============================================================================
-- 9. MATERIALIZED VIEW: Merchant Payment Summary
-- Description: Résumé des paiements par merchant
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS merchant_payment_summary CASCADE;

CREATE MATERIALIZED VIEW merchant_payment_summary AS
SELECT
    m.id AS merchant_id,
    m.company_name,
    m.payment_gateway,
    m.auto_debit_enabled,
    
    -- Factures
    COUNT(DISTINCT pi.id) AS total_invoices,
    COUNT(DISTINCT CASE WHEN pi.status = 'paid' THEN pi.id END) AS paid_invoices,
    COUNT(DISTINCT CASE WHEN pi.status = 'overdue' THEN pi.id END) AS overdue_invoices,
    
    -- Montants
    SUM(CASE WHEN pi.status = 'paid' THEN pi.total_amount ELSE 0 END) AS total_paid,
    SUM(CASE WHEN pi.status IN ('pending', 'sent', 'viewed') THEN pi.total_amount ELSE 0 END) AS total_pending,
    SUM(CASE WHEN pi.status = 'overdue' THEN pi.total_amount ELSE 0 END) AS total_overdue,
    
    -- Dates
    MAX(pi.paid_at) AS last_payment_date,
    MIN(CASE WHEN pi.status = 'overdue' THEN pi.due_date END) AS earliest_overdue_date
    
FROM merchants m
LEFT JOIN platform_invoices pi ON m.id = pi.merchant_id
GROUP BY m.id, m.company_name, m.payment_gateway, m.auto_debit_enabled;

CREATE INDEX IF NOT EXISTS idx_merchant_payment_summary_merchant ON merchant_payment_summary(merchant_id);

-- ============================================================================
-- 10. INSERT: Données de configuration initiales
-- ============================================================================

-- Ajouter les gateways disponibles dans une table de référence
CREATE TABLE IF NOT EXISTS payment_gateway_configs (
    id SERIAL PRIMARY KEY,
    gateway_code VARCHAR(50) UNIQUE NOT NULL,
    gateway_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    countries VARCHAR(10)[] DEFAULT ARRAY['MA'],
    currencies VARCHAR(3)[] DEFAULT ARRAY['MAD'],
    fee_percentage DECIMAL(5, 2),
    fee_fixed DECIMAL(10, 2),
    settlement_days INTEGER,
    supports_split_payment BOOLEAN DEFAULT FALSE,
    configuration_fields JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO payment_gateway_configs (gateway_code, gateway_name, description, fee_percentage, fee_fixed, settlement_days, supports_split_payment, configuration_fields) VALUES
('cmi', 'CMI - Centre Monétique Interbancaire', 'Solution de paiement nationale marocaine', 1.75, 0, 2, FALSE, 
 '{"required_fields": ["cmi_merchant_id", "cmi_api_key", "cmi_store_key", "cmi_terminal_id"]}'),
 
('payzen', 'PayZen / Lyra', 'Solution de paiement française populaire au Maroc', 2.00, 0, 1, TRUE,
 '{"required_fields": ["payzen_shop_id", "payzen_api_key", "payzen_secret_key", "payzen_mode"]}'),
 
('sg_maroc', 'Société Générale Maroc - e-Payment', 'TPE virtuel + API Société Générale', 2.00, 0, 2, FALSE,
 '{"required_fields": ["sg_merchant_code", "sg_terminal_id", "sg_api_username", "sg_api_password", "sg_certificate"]}'),
 
('manual', 'Paiement Manuel', 'Facturation et suivi manuel des paiements', 0, 0, 30, FALSE,
 '{"required_fields": []}');

-- ============================================================================
-- 11. MIGRATION SUMMARY
-- ============================================================================
-- ✅ Tables créées:
--   - platform_invoices (factures plateforme)
--   - invoice_line_items (détails factures)
--   - gateway_transactions (transactions gateways)
--   - payment_gateway_logs (logs communications)
--   - payment_gateway_configs (configurations gateways)
--
-- ✅ Colonnes ajoutées à merchants:
--   - payment_gateway
--   - gateway_config
--   - auto_debit_enabled
--   - gateway_activated_at
--
-- ✅ Fonctions créées:
--   - generate_invoice_number()
--   - update_updated_at_column()
--
-- ✅ Vues matérialisées:
--   - gateway_statistics
--   - merchant_payment_summary
--
-- ✅ Indexes créés pour performance
--
-- ✅ Triggers créés pour auto-update
--
-- ============================================================================



-- ============================================
-- MIGRATION: 013_enable_2fa_for_all.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- ============================================
-- ACTIVATION 2FA POUR TOUS LES UTILISATEURS
-- Date: 2025-10-23
-- ============================================

-- Vérifier l'état actuel
SELECT 
    email,
    role,
    two_fa_enabled,
    CASE 
        WHEN two_fa_enabled THEN '✅ Activée'
        ELSE '❌ Désactivée'
    END as statut_2fa
FROM users
ORDER BY role, email;

-- Activer la 2FA pour tous les utilisateurs
UPDATE users
SET two_fa_enabled = true
WHERE two_fa_enabled = false OR two_fa_enabled IS NULL;

-- Vérifier le résultat
SELECT 
    role,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE two_fa_enabled = true) as avec_2fa,
    COUNT(*) FILTER (WHERE two_fa_enabled = false OR two_fa_enabled IS NULL) as sans_2fa
FROM users
GROUP BY role;

-- Afficher tous les utilisateurs avec leur statut 2FA
SELECT 
    email,
    role,
    two_fa_enabled,
    created_at
FROM users
ORDER BY created_at DESC;

COMMENT ON TABLE users IS 'Table des utilisateurs - 2FA activée pour tous les comptes';



-- ============================================
-- MIGRATION: 015_add_services_to_affiliation.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- Migration to add service_id to affiliation tables
-- Date: 2025-12-05

-- 1. Update affiliation_requests
ALTER TABLE affiliation_requests 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

ALTER TABLE affiliation_requests 
ALTER COLUMN product_id DROP NOT NULL;

ALTER TABLE affiliation_requests 
DROP CONSTRAINT IF EXISTS affiliation_requests_influencer_id_product_id_key;

ALTER TABLE affiliation_requests 
ADD CONSTRAINT affiliation_requests_target_check 
CHECK (
    (product_id IS NOT NULL AND service_id IS NULL) OR 
    (product_id IS NULL AND service_id IS NOT NULL)
);

ALTER TABLE affiliation_requests 
ADD CONSTRAINT affiliation_requests_unique_target 
UNIQUE (influencer_id, product_id, service_id);

-- 2. Update affiliate_links
ALTER TABLE affiliate_links 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

ALTER TABLE affiliate_links 
ALTER COLUMN product_id DROP NOT NULL;

ALTER TABLE affiliate_links 
ADD CONSTRAINT affiliate_links_target_check 
CHECK (
    (product_id IS NOT NULL AND service_id IS NULL) OR 
    (product_id IS NULL AND service_id IS NOT NULL)
);

-- 3. Update trackable_links (if used)
ALTER TABLE trackable_links 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

ALTER TABLE trackable_links 
ALTER COLUMN product_id DROP NOT NULL;

-- 4. Update trigger function for auto-approval
CREATE OR REPLACE FUNCTION create_tracking_link_on_approval()
RETURNS TRIGGER AS $$
BEGIN
    -- Si la demande vient d'être approuvée
    IF NEW.status = 'approved' AND OLD.status = 'pending' THEN
        -- Créer un lien de tracking dans trackable_links (et affiliate_links pour synchro)
        -- Note: On insère dans affiliate_links car c'est ce que l'API utilise
        INSERT INTO affiliate_links (
            influencer_id,
            product_id,
            service_id,
            unique_code,
            is_active,
            created_at
        )
        VALUES (
            NEW.influencer_id,
            NEW.product_id,
            NEW.service_id,
            substring(md5(random()::text || NEW.influencer_id::text || COALESCE(NEW.product_id::text, NEW.service_id::text)) from 1 for 8),
            true,
            NOW()
        );
        
        -- Enregistrer dans l'historique
        INSERT INTO affiliation_request_history (
            request_id,
            old_status,
            new_status,
            changed_by,
            comment
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            NEW.reviewed_by,
            'Demande approuvée - Lien de tracking créé automatiquement'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



-- ============================================
-- MIGRATION: 016_add_service_id_to_publications.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- Migration to add service_id and ensure product_id exists in social_media_publications
-- Date: 2025-12-05

-- 1. Ensure product_id exists (it might be missing based on error)
ALTER TABLE social_media_publications 
ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES products(id) ON DELETE SET NULL;

-- 2. Add service_id
ALTER TABLE social_media_publications 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

-- [AUTOMATION STEP 2 & 3]: This column allows linking a publication directly to a Service, 
-- enabling the "Influencer Request" scenario for services, distinct from products.

-- 3. Make product_id nullable (it should be already if we just added it, but if it existed as NOT NULL, this fixes it)
ALTER TABLE social_media_publications 
ALTER COLUMN product_id DROP NOT NULL;

-- 4. Same for tracking_links
ALTER TABLE tracking_links 
ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES products(id) ON DELETE SET NULL;

-- [AUTOMATION STEP 4]: Stores the reference for QR Code generation specific to a Product.

ALTER TABLE tracking_links 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

-- [AUTOMATION STEP 4]: Stores the reference for QR Code generation specific to a Service.

ALTER TABLE tracking_links 
ALTER COLUMN product_id DROP NOT NULL;

-- 5. Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_publications_service_id ON social_media_publications(service_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_service_id ON tracking_links(service_id);



-- ============================================
-- MIGRATION: 021_add_transaction_functions.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- =============================================================================
-- Migration: Transactional helpers for sales & payouts
-- Description: Adds stored procedures to guarantee atomic operations when
--              creating sales and approving payouts.
-- Date: 2025-10-26
-- =============================================================================

CREATE OR REPLACE FUNCTION create_sale_transaction(
    p_link_id UUID,
    p_product_id UUID,
    p_influencer_id UUID,
    p_merchant_id UUID,
    p_amount NUMERIC,
    p_currency TEXT DEFAULT 'EUR',
    p_quantity INTEGER DEFAULT 1,
    p_customer_email TEXT DEFAULT NULL,
    p_customer_name TEXT DEFAULT NULL,
    p_payment_status TEXT DEFAULT 'pending',
    p_status TEXT DEFAULT 'completed'
)
RETURNS sales AS $$
DECLARE
    v_product RECORD;
    v_link RECORD;
    v_sale sales%ROWTYPE;
    v_commission_rate NUMERIC;
    v_commission_type TEXT;
    v_influencer_commission NUMERIC;
    v_platform_commission NUMERIC;
    v_merchant_revenue NUMERIC;
BEGIN
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Le montant de la vente doit être supérieur à 0.';
    END IF;

    IF COALESCE(p_quantity, 1) <= 0 THEN
        RAISE EXCEPTION 'La quantité doit être positive.';
    END IF;

    IF p_status NOT IN ('pending', 'completed', 'refunded', 'cancelled') THEN
        RAISE EXCEPTION 'Statut de vente % non supporté', p_status;
    END IF;

    IF p_payment_status NOT IN ('pending', 'paid') THEN
        RAISE EXCEPTION 'Statut de paiement % non supporté', p_payment_status;
    END IF;

    SELECT commission_rate, COALESCE(commission_type, 'percentage') AS commission_type
         , merchant_id
    INTO v_product
    FROM products
    WHERE id = p_product_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product % introuvable', p_product_id;
    END IF;

    IF v_product.merchant_id <> p_merchant_id THEN
        RAISE EXCEPTION 'Le produit % appartient à un autre marchand.', p_product_id;
    END IF;

    SELECT product_id, influencer_id
    INTO v_link
    FROM trackable_links
    WHERE id = p_link_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Lien tracké % introuvable', p_link_id;
    END IF;

    IF v_link.product_id <> p_product_id THEN
        RAISE EXCEPTION 'Le lien tracké ne correspond pas au produit indiqué.';
    END IF;

    IF v_link.influencer_id <> p_influencer_id THEN
        RAISE EXCEPTION 'Le lien tracké ne correspond pas à l''influenceur indiqué.';
    END IF;

    v_commission_rate := COALESCE(v_product.commission_rate, 0);
    v_commission_type := v_product.commission_type;

    IF v_commission_type = 'fixed' THEN
        v_influencer_commission := ROUND(v_commission_rate, 2);
    ELSE
        v_influencer_commission := ROUND(p_amount * (v_commission_rate / 100), 2);
    END IF;

    v_platform_commission := ROUND(p_amount * 0.05, 2);
    v_merchant_revenue := ROUND(p_amount - v_influencer_commission - v_platform_commission, 2);

    INSERT INTO sales (
        link_id,
        product_id,
        influencer_id,
        merchant_id,
        customer_email,
        customer_name,
        quantity,
        amount,
        currency,
        influencer_commission,
        platform_commission,
        merchant_revenue,
        status,
        payment_status,
        sale_timestamp,
        created_at
    )
    VALUES (
        p_link_id,
        p_product_id,
        p_influencer_id,
        p_merchant_id,
        p_customer_email,
        p_customer_name,
        COALESCE(p_quantity, 1),
        p_amount,
        p_currency,
        v_influencer_commission,
        v_platform_commission,
        v_merchant_revenue,
        p_status,
        p_payment_status,
        NOW(),
        NOW()
    )
    RETURNING * INTO v_sale;

    INSERT INTO commissions (
        sale_id,
        influencer_id,
        amount,
        currency,
        status,
        created_at
    )
    VALUES (
        v_sale.id,
        p_influencer_id,
        v_influencer_commission,
        p_currency,
        'pending',
        NOW()
    );

    UPDATE trackable_links
    SET
        sales = COALESCE(sales, 0) + 1,
        total_revenue = COALESCE(total_revenue, 0) + p_amount,
        total_commission = COALESCE(total_commission, 0) + v_influencer_commission,
        conversion_rate = CASE
            WHEN COALESCE(clicks, 0) > 0
                THEN ROUND(((COALESCE(sales, 0) + 1)::NUMERIC / COALESCE(clicks, 1)) * 100, 2)
            ELSE conversion_rate
        END,
        updated_at = NOW()
    WHERE id = p_link_id;

    UPDATE influencers
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        total_earnings = COALESCE(total_earnings, 0) + v_influencer_commission,
        balance = COALESCE(balance, 0) + v_influencer_commission,
        updated_at = NOW()
    WHERE id = p_influencer_id;

    UPDATE merchants
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        updated_at = NOW()
    WHERE id = p_merchant_id;

    UPDATE products
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        updated_at = NOW()
    WHERE id = p_product_id;

    RETURN v_sale;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION approve_payout_transaction(
    p_commission_id UUID,
    p_status TEXT DEFAULT 'approved'
)
RETURNS BOOLEAN AS $$
DECLARE
    v_commission RECORD;
BEGIN
    SELECT
        c.id,
        c.sale_id,
        c.influencer_id,
        c.amount,
        c.currency,
        c.status,
        s.merchant_id,
        i.balance AS influencer_balance
    INTO v_commission
    FROM commissions c
    LEFT JOIN sales s ON s.id = c.sale_id
    JOIN influencers i ON i.id = c.influencer_id
    WHERE c.id = p_commission_id
    FOR UPDATE OF c, i;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Commission % introuvable', p_commission_id;
    END IF;

    IF v_commission.influencer_balance IS NULL THEN
        RAISE EXCEPTION 'Influenceur introuvable pour la commission %', p_commission_id;
    END IF;

    IF v_commission.status = 'paid' AND p_status <> 'paid' THEN
        RAISE EXCEPTION 'La commission % a déjà été réglée et ne peut pas changer de statut.', p_commission_id;
    END IF;

    IF p_status = v_commission.status THEN
        RETURN TRUE;
    END IF;

    IF v_commission.amount <= 0 THEN
        RAISE EXCEPTION 'Montant invalide pour la commission %', p_commission_id;
    END IF;

    IF p_status NOT IN ('approved', 'paid', 'rejected', 'pending') THEN
        RAISE EXCEPTION 'Statut % non supporté', p_status;
    END IF;

    -- Gestion des transitions de statut avec ajustement du solde
    IF p_status = 'approved' AND v_commission.status = 'pending' THEN
        IF COALESCE(v_commission.influencer_balance, 0) < v_commission.amount THEN
            RAISE EXCEPTION 'Solde insuffisant pour approuver la commission %', p_commission_id;
        END IF;
        UPDATE influencers
        SET balance = COALESCE(balance, 0) - v_commission.amount
        WHERE id = v_commission.influencer_id;
    ELSIF p_status = 'pending' AND v_commission.status = 'approved' THEN
        UPDATE influencers
        SET balance = COALESCE(balance, 0) + v_commission.amount
        WHERE id = v_commission.influencer_id;
    ELSIF p_status = 'rejected' AND v_commission.status = 'approved' THEN
        UPDATE influencers
        SET balance = COALESCE(balance, 0) + v_commission.amount
        WHERE id = v_commission.influencer_id;
    ELSIF p_status = 'rejected' AND v_commission.status = 'pending' THEN
        -- Aucun ajustement, on libère simplement la commission
        NULL;
    ELSIF p_status = 'paid' AND v_commission.status <> 'approved' THEN
        RAISE EXCEPTION 'La commission doit être approuvée avant d''être payée.';
    ELSIF p_status = 'paid' AND v_commission.status = 'approved' THEN
        IF v_commission.merchant_id IS NOT NULL THEN
            UPDATE merchants
            SET
                total_commission_paid = COALESCE(total_commission_paid, 0) + v_commission.amount,
                updated_at = NOW()
            WHERE id = v_commission.merchant_id;
        END IF;
    END IF;

    UPDATE commissions
    SET
        status = p_status,
        approved_at = CASE
            WHEN p_status = 'approved' AND v_commission.status = 'pending' THEN NOW()
            WHEN p_status IN ('pending', 'rejected') THEN NULL
            ELSE approved_at
        END,
        paid_at = CASE
            WHEN p_status = 'paid' THEN NOW()
            WHEN p_status IN ('pending', 'rejected') THEN NULL
            ELSE paid_at
        END
    WHERE id = p_commission_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Notes d'utilisation
-- 1. create_sale_transaction :
--    - Déclencher lors de la validation d'une vente traquée.
--    - Garantit la création de la vente, de la commission et la mise à jour
--      des métriques clés (lien, influenceur, marchand, produit) en une seule
--      transaction.
--    - Exemple d'appel :
--        SELECT create_sale_transaction(
--            p_link_id => '...UUID...',
--            p_product_id => '...UUID...',
--            p_influencer_id => '...UUID...',
--            p_merchant_id => '...UUID...',
--            p_amount => 199.90,
--            p_currency => 'EUR',
--            p_quantity => 1,
--            p_customer_email => 'client@example.com',
--            p_customer_name => 'Client Demo'
--        );
--
-- 2. approve_payout_transaction :
--    - À utiliser dans le workflow d'approbation des retraits.
--    - Gère les transitions de statut autorisées et l'ajustement du solde
--      disponible de l'influenceur.
--    - Exemple d'appel :
--        SELECT approve_payout_transaction(
--            p_commission_id => '...UUID...',
--            p_status => 'approved'
--        );
--
-- 3. Rollback manuel (DOWN) :
--    - DROP FUNCTION IF EXISTS create_sale_transaction(
--        UUID, UUID, UUID, UUID, NUMERIC, TEXT, INTEGER,
--        TEXT, TEXT, TEXT, TEXT
--      );
--    - DROP FUNCTION IF EXISTS approve_payout_transaction(UUID, TEXT);
-- ============================================================================



-- ============================================
-- MIGRATION: 022_update_transaction_functions.sql
-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)
-- ============================================

-- =============================================================================
-- Migration: Update transaction functions (remove metadata parameter)
-- Description: Drops old version of create_sale_transaction with metadata
--              and recreates it without that parameter to match schema.
-- Date: 2025-10-27
-- =============================================================================

-- Drop the old version with metadata parameter
DROP FUNCTION IF EXISTS create_sale_transaction(
    UUID, UUID, UUID, UUID, NUMERIC, TEXT, INTEGER,
    TEXT, TEXT, TEXT, TEXT, JSONB
);

-- Recreate the function without metadata
CREATE OR REPLACE FUNCTION create_sale_transaction(
    p_link_id UUID,
    p_product_id UUID,
    p_influencer_id UUID,
    p_merchant_id UUID,
    p_amount NUMERIC,
    p_currency TEXT DEFAULT 'EUR',
    p_quantity INTEGER DEFAULT 1,
    p_customer_email TEXT DEFAULT NULL,
    p_customer_name TEXT DEFAULT NULL,
    p_payment_status TEXT DEFAULT 'pending',
    p_status TEXT DEFAULT 'completed'
)
RETURNS sales AS $$
DECLARE
    v_product RECORD;
    v_link RECORD;
    v_sale sales%ROWTYPE;
    v_commission_rate NUMERIC;
    v_commission_type TEXT;
    v_influencer_commission NUMERIC;
    v_platform_commission NUMERIC;
    v_merchant_revenue NUMERIC;
BEGIN
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Le montant de la vente doit être supérieur à 0.';
    END IF;

    IF COALESCE(p_quantity, 1) <= 0 THEN
        RAISE EXCEPTION 'La quantité doit être positive.';
    END IF;

    IF p_status NOT IN ('pending', 'completed', 'refunded', 'cancelled') THEN
        RAISE EXCEPTION 'Statut de vente % non supporté', p_status;
    END IF;

    IF p_payment_status NOT IN ('pending', 'paid') THEN
        RAISE EXCEPTION 'Statut de paiement % non supporté', p_payment_status;
    END IF;

    SELECT commission_rate, COALESCE(commission_type, 'percentage') AS commission_type
         , merchant_id
    INTO v_product
    FROM products
    WHERE id = p_product_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product % introuvable', p_product_id;
    END IF;

    IF v_product.merchant_id <> p_merchant_id THEN
        RAISE EXCEPTION 'Le produit % appartient à un autre marchand.', p_product_id;
    END IF;

    SELECT product_id, influencer_id
    INTO v_link
    FROM trackable_links
    WHERE id = p_link_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Lien tracké % introuvable', p_link_id;
    END IF;

    IF v_link.product_id <> p_product_id THEN
        RAISE EXCEPTION 'Le lien tracké ne correspond pas au produit indiqué.';
    END IF;

    IF v_link.influencer_id <> p_influencer_id THEN
        RAISE EXCEPTION 'Le lien tracké ne correspond pas à l''influenceur indiqué.';
    END IF;

    v_commission_rate := COALESCE(v_product.commission_rate, 0);
    v_commission_type := v_product.commission_type;

    IF v_commission_type = 'fixed' THEN
        v_influencer_commission := ROUND(v_commission_rate, 2);
    ELSE
        v_influencer_commission := ROUND(p_amount * (v_commission_rate / 100), 2);
    END IF;

    v_platform_commission := ROUND(p_amount * 0.05, 2);
    v_merchant_revenue := ROUND(p_amount - v_influencer_commission - v_platform_commission, 2);

    INSERT INTO sales (
        link_id,
        product_id,
        influencer_id,
        merchant_id,
        customer_email,
        customer_name,
        quantity,
        amount,
        currency,
        influencer_commission,
        platform_commission,
        merchant_revenue,
        status,
        payment_status,
        sale_timestamp,
        created_at
    )
    VALUES (
        p_link_id,
        p_product_id,
        p_influencer_id,
        p_merchant_id,
        p_customer_email,
        p_customer_name,
        COALESCE(p_quantity, 1),
        p_amount,
        p_currency,
        v_influencer_commission,
        v_platform_commission,
        v_merchant_revenue,
        p_status,
        p_payment_status,
        NOW(),
        NOW()
    )
    RETURNING * INTO v_sale;

    INSERT INTO commissions (
        sale_id,
        influencer_id,
        amount,
        currency,
        status,
        created_at
    )
    VALUES (
        v_sale.id,
        p_influencer_id,
        v_influencer_commission,
        p_currency,
        'pending',
        NOW()
    );

    UPDATE trackable_links
    SET
        sales = COALESCE(sales, 0) + 1,
        total_revenue = COALESCE(total_revenue, 0) + p_amount,
        total_commission = COALESCE(total_commission, 0) + v_influencer_commission,
        conversion_rate = CASE
            WHEN COALESCE(clicks, 0) > 0
                THEN ROUND(((COALESCE(sales, 0) + 1)::NUMERIC / COALESCE(clicks, 1)) * 100, 2)
            ELSE conversion_rate
        END,
        updated_at = NOW()
    WHERE id = p_link_id;

    UPDATE influencers
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        total_earnings = COALESCE(total_earnings, 0) + v_influencer_commission,
        balance = COALESCE(balance, 0) + v_influencer_commission,
        updated_at = NOW()
    WHERE id = p_influencer_id;

    UPDATE merchants
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        updated_at = NOW()
    WHERE id = p_merchant_id;

    UPDATE products
    SET
        total_sales = COALESCE(total_sales, 0) + 1,
        updated_at = NOW()
    WHERE id = p_product_id;

    RETURN v_sale;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Fin de la migration
-- ============================================================================


