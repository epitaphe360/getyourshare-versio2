-- ============================================
-- TABLE: payment_transactions
-- Stockage des transactions de paiement Maroc
-- ============================================

CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Informations provider
    provider VARCHAR(50) NOT NULL, -- cmi, payzen, orange_money, inwi_money, maroc_telecom
    provider_transaction_id VARCHAR(255),
    order_id VARCHAR(255) UNIQUE,

    -- Montant
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'MAD',

    -- Statut
    status VARCHAR(50) NOT NULL DEFAULT 'initiated', -- initiated, pending, completed, failed, refunded

    -- Données
    payment_data JSONB, -- Données de création du paiement
    callback_data JSONB, -- Données du callback
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    CONSTRAINT payment_transactions_amount_positive CHECK (amount > 0)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id
    ON payment_transactions(user_id);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_provider
    ON payment_transactions(provider);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_status
    ON payment_transactions(status);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_order_id
    ON payment_transactions(order_id);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_created_at
    ON payment_transactions(created_at DESC);

-- Index composé pour recherches fréquentes
CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_status
    ON payment_transactions(user_id, status);

-- ============================================
-- TRIGGER: Mise à jour automatique de updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_payment_transaction_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();

    -- Si le statut passe à completed, enregistrer completed_at
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        NEW.completed_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_payment_transaction_updated_at
    BEFORE UPDATE ON payment_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_payment_transaction_updated_at();

-- ============================================
-- VUES UTILES
-- ============================================

-- Vue des paiements par provider
CREATE OR REPLACE VIEW payment_stats_by_provider AS
SELECT
    provider,
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_count,
    SUM(amount) FILTER (WHERE status = 'completed') as total_amount,
    AVG(amount) FILTER (WHERE status = 'completed') as avg_amount,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::numeric /
        NULLIF(COUNT(*), 0) * 100,
        2
    ) as success_rate
FROM payment_transactions
GROUP BY provider;

-- Vue des paiements par utilisateur
CREATE OR REPLACE VIEW user_payment_summary AS
SELECT
    user_id,
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_transactions,
    SUM(amount) FILTER (WHERE status = 'completed') as total_spent,
    MAX(created_at) as last_payment_date
FROM payment_transactions
GROUP BY user_id;

-- ============================================
-- FONCTION: Obtenir l'historique de paiement d'un utilisateur
-- ============================================

CREATE OR REPLACE FUNCTION get_user_payment_history(
    p_user_id UUID,
    p_limit INT DEFAULT 50,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    provider VARCHAR(50),
    amount DECIMAL(10, 2),
    currency VARCHAR(10),
    status VARCHAR(50),
    order_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pt.id,
        pt.provider,
        pt.amount,
        pt.currency,
        pt.status,
        pt.order_id,
        pt.created_at
    FROM payment_transactions pt
    WHERE pt.user_id = p_user_id
    ORDER BY pt.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FONCTION: Stats globales des paiements
-- ============================================

CREATE OR REPLACE FUNCTION get_payment_global_stats(
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    total_transactions BIGINT,
    completed_transactions BIGINT,
    failed_transactions BIGINT,
    total_revenue DECIMAL(10, 2),
    avg_transaction_amount DECIMAL(10, 2),
    success_rate DECIMAL(5, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) as total_transactions,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_transactions,
        COUNT(*) FILTER (WHERE status = 'failed') as failed_transactions,
        COALESCE(SUM(amount) FILTER (WHERE status = 'completed'), 0) as total_revenue,
        COALESCE(AVG(amount) FILTER (WHERE status = 'completed'), 0) as avg_transaction_amount,
        ROUND(
            COUNT(*) FILTER (WHERE status = 'completed')::numeric /
            NULLIF(COUNT(*), 0) * 100,
            2
        ) as success_rate
    FROM payment_transactions
    WHERE
        (p_start_date IS NULL OR created_at >= p_start_date)
        AND created_at <= p_end_date;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- DONNÉES DE TEST (optionnel - pour développement)
-- ============================================

-- Exemple de comment insérer une transaction de test
-- INSERT INTO payment_transactions (user_id, provider, order_id, amount, status)
-- VALUES (
--     (SELECT id FROM users WHERE role = 'merchant' LIMIT 1),
--     'cmi',
--     'TEST_ORDER_' || NOW()::TEXT,
--     150.00,
--     'completed'
-- );

-- ============================================
-- PERMISSIONS (Row Level Security)
-- ============================================

-- Activer RLS
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;

-- Policy: Les utilisateurs peuvent voir leurs propres transactions
CREATE POLICY payment_transactions_user_select ON payment_transactions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Les admins peuvent voir toutes les transactions
CREATE POLICY payment_transactions_admin_select ON payment_transactions
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role IN ('admin', 'superadmin')
        )
    );

-- Policy: Les utilisateurs peuvent créer leurs propres transactions
CREATE POLICY payment_transactions_user_insert ON payment_transactions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Les admins peuvent mettre à jour les transactions
CREATE POLICY payment_transactions_admin_update ON payment_transactions
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role IN ('admin', 'superadmin')
        )
    );

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE payment_transactions IS 'Stocke toutes les transactions de paiement via les gateways marocains (CMI, PayZen, Orange Money, Inwi Money, Maroc Telecom Cash)';
COMMENT ON COLUMN payment_transactions.provider IS 'Provider de paiement: cmi, payzen, orange_money, inwi_money, maroc_telecom';
COMMENT ON COLUMN payment_transactions.provider_transaction_id IS 'ID de transaction fourni par le provider';
COMMENT ON COLUMN payment_transactions.order_id IS 'ID de commande unique généré par notre système';
COMMENT ON COLUMN payment_transactions.status IS 'Statut: initiated, pending, completed, failed, refunded';
COMMENT ON COLUMN payment_transactions.payment_data IS 'Données JSON de la création du paiement';
COMMENT ON COLUMN payment_transactions.callback_data IS 'Données JSON reçues du callback provider';
