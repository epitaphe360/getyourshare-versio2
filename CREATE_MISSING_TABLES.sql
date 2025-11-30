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
