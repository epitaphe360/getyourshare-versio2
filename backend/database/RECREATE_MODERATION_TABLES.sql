-- ============================================
-- RECRÉATION COMPLÈTE DES TABLES DE MODÉRATION
-- À exécuter dans Supabase SQL Editor
-- ============================================

-- 1. Nettoyage (Attention: supprime les données existantes)
DROP VIEW IF EXISTS v_daily_moderation_stats;
DROP VIEW IF EXISTS v_pending_moderation;
DROP TABLE IF EXISTS moderation_history;
DROP TABLE IF EXISTS moderation_stats;
DROP TABLE IF EXISTS moderation_queue;

-- 2. Table principale
CREATE TABLE moderation_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Références (optionnelles pour éviter les erreurs de contrainte si les tables manquent)
    product_id UUID,
    merchant_id UUID,
    user_id UUID,
    
    -- Données produit
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    product_category VARCHAR(100),
    product_price DECIMAL(10, 2),
    product_images JSONB,
    
    -- Modération IA
    status VARCHAR(50) DEFAULT 'pending',
    ai_decision VARCHAR(20),
    ai_confidence DECIMAL(3, 2),
    ai_risk_level VARCHAR(20),
    ai_flags JSONB,
    ai_reason TEXT,
    ai_recommendation TEXT,
    moderation_method VARCHAR(20),
    
    -- Décision Admin
    admin_decision VARCHAR(20),
    admin_user_id UUID,
    admin_comment TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    submission_attempts INT DEFAULT 1,
    priority INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Index
CREATE INDEX idx_moderation_status ON moderation_queue(status);
CREATE INDEX idx_moderation_merchant ON moderation_queue(merchant_id);
CREATE INDEX idx_moderation_risk ON moderation_queue(ai_risk_level);

-- 4. Table Historique
CREATE TABLE moderation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moderation_id UUID REFERENCES moderation_queue(id) ON DELETE CASCADE,
    action VARCHAR(50),
    performed_by UUID,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    comment TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Table Stats
CREATE TABLE moderation_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE DEFAULT CURRENT_DATE,
    total_submissions INT DEFAULT 0,
    ai_approved INT DEFAULT 0,
    ai_rejected INT DEFAULT 0,
    admin_approved INT DEFAULT 0,
    admin_rejected INT DEFAULT 0,
    pending INT DEFAULT 0,
    avg_ai_confidence DECIMAL(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date)
);

-- 6. Vue Pending (pour le dashboard)
CREATE OR REPLACE VIEW v_pending_moderation AS
SELECT 
    mq.*,
    m.company_name as merchant_name,
    u.email as merchant_email,
    EXTRACT(EPOCH FROM (NOW() - mq.created_at))/3600 as hours_pending
FROM moderation_queue mq
LEFT JOIN merchants m ON mq.merchant_id = m.id
LEFT JOIN users u ON mq.user_id = u.id
WHERE mq.status = 'pending';

-- 7. Vue Stats (pour le dashboard)
CREATE OR REPLACE VIEW v_daily_moderation_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'approved') as approved,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
    AVG(ai_confidence) as avg_confidence
FROM moderation_queue
GROUP BY DATE(created_at);

-- 8. Fonction d'approbation
CREATE OR REPLACE FUNCTION approve_moderation(
    p_moderation_id UUID,
    p_admin_user_id UUID,
    p_comment TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE moderation_queue
    SET 
        status = 'approved',
        admin_decision = 'approved',
        admin_user_id = p_admin_user_id,
        admin_comment = p_comment,
        reviewed_at = NOW()
    WHERE id = p_moderation_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- 9. Fonction de rejet
CREATE OR REPLACE FUNCTION reject_moderation(
    p_moderation_id UUID,
    p_admin_user_id UUID,
    p_comment TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE moderation_queue
    SET 
        status = 'rejected',
        admin_decision = 'rejected',
        admin_user_id = p_admin_user_id,
        admin_comment = p_comment,
        reviewed_at = NOW()
    WHERE id = p_moderation_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
