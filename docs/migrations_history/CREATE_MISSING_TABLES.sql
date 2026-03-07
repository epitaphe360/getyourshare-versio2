-- ============================================
-- CRÉATION DES TABLES MANQUANTES UNIQUEMENT
-- ============================================
-- Date: 30 novembre 2025
-- ============================================

-- Table: marketing_templates
CREATE TABLE IF NOT EXISTS marketing_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commercial_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('email', 'social', 'presentation', 'sms', 'whatsapp')),
    subject TEXT,
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour marketing_templates
CREATE INDEX IF NOT EXISTS idx_marketing_templates_commercial ON marketing_templates(commercial_id);
CREATE INDEX IF NOT EXISTS idx_marketing_templates_type ON marketing_templates(type);
CREATE INDEX IF NOT EXISTS idx_marketing_templates_active ON marketing_templates(is_active) WHERE is_active = TRUE;

-- Trigger pour updated_at sur marketing_templates
CREATE OR REPLACE FUNCTION update_marketing_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS marketing_templates_updated_at ON marketing_templates;
CREATE TRIGGER marketing_templates_updated_at
    BEFORE UPDATE ON marketing_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_marketing_templates_updated_at();

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE '✅ Table marketing_templates créée avec succès';
END $$;

-- ============================================
-- TABLES POUR FONCTIONNALITÉS E-COMMERCE
-- ============================================

-- Table wishlists (listes de souhaits des utilisateurs)
CREATE TABLE IF NOT EXISTS wishlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_name VARCHAR(255),
    name VARCHAR(255),
    notes TEXT,
    priority VARCHAR(50), -- 'high', 'medium', 'low'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wishlists_user_id ON wishlists(user_id);

-- Table shipments (expéditions)
CREATE TABLE IF NOT EXISTS shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID,
    tracking_number VARCHAR(255),
    carrier VARCHAR(100),
    service_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    shipped_at TIMESTAMPTZ,
    estimated_delivery TIMESTAMPTZ,
    actual_delivery TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    shipping_cost DECIMAL(10, 2),
    weight_kg DECIMAL(10, 2),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shipments_user_id ON shipments(user_id);
CREATE INDEX IF NOT EXISTS idx_shipments_order_id ON shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_tracking_number ON shipments(tracking_number);

-- Table warehouses (entrepôts)
CREATE TABLE IF NOT EXISTS warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    phone VARCHAR(50),
    email VARCHAR(255),
    capacity_units INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_warehouses_user_id ON warehouses(user_id);
CREATE INDEX IF NOT EXISTS idx_warehouses_is_active ON warehouses(is_active);

-- Table coupons (codes promo/coupons)
CREATE TABLE IF NOT EXISTS coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    discount_type VARCHAR(20),
    discount_value DECIMAL(10, 2),
    min_purchase_amount DECIMAL(10, 2),
    max_uses INTEGER,
    times_used INTEGER DEFAULT 0,
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    applies_to VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupons_user_id ON coupons(user_id);
CREATE INDEX IF NOT EXISTS idx_coupons_is_active ON coupons(is_active);

-- Table invoices (factures) - Si n'existe pas
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invoice_number VARCHAR(100) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2),
    tax_rate DECIMAL(5, 2),
    tax_amount DECIMAL(10, 2),
    total DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(50) DEFAULT 'draft',
    due_date DATE,
    paid_at TIMESTAMPTZ,
    payment_method VARCHAR(100),
    notes TEXT,
    pdf_url TEXT,
    line_items JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

-- Table events (événements/webinaires)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50),
    description TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    location TEXT,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    is_online BOOLEAN DEFAULT false,
    meeting_url TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_start_time ON events(start_time);

-- Message final
DO $$
BEGIN
    RAISE NOTICE '✅ Toutes les tables e-commerce créées avec succès';
    RAISE NOTICE '   - wishlists (listes de souhaits)';
    RAISE NOTICE '   - shipments (expéditions)';
    RAISE NOTICE '   - warehouses (entrepôts)';
    RAISE NOTICE '   - coupons (codes promo)';
    RAISE NOTICE '   - invoices (factures)';
    RAISE NOTICE '   - events (événements)';
END $$;
