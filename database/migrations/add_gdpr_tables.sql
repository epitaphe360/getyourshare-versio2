-- Migration: Tables GDPR/RGPD Compliance
-- Date: 2025-12-07
-- Description: Tables pour conformité GDPR (consentements, suppressions, audit)

-- ============================================
-- TABLE USER_CONSENTS (Consentements cookies/GDPR)
-- ============================================

CREATE TABLE IF NOT EXISTS user_consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Type de consentement
    consent_type VARCHAR(50) NOT NULL DEFAULT 'cookies', -- cookies, marketing, data_processing

    -- Cookies granulaires
    necessary_cookies BOOLEAN DEFAULT TRUE, -- Toujours TRUE
    analytics_cookies BOOLEAN DEFAULT FALSE,
    marketing_cookies BOOLEAN DEFAULT FALSE,
    personalization_cookies BOOLEAN DEFAULT FALSE,

    -- Métadonnées consentement
    consent_date TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,

    -- Révocation
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_user_consents_user ON user_consents(user_id);
CREATE INDEX IF NOT EXISTS idx_user_consents_type ON user_consents(consent_type);
CREATE INDEX IF NOT EXISTS idx_user_consents_date ON user_consents(consent_date);

-- Contrainte unique: Un seul consentement par type par user
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_consents_unique ON user_consents(user_id, consent_type)
WHERE revoked = FALSE;

-- RLS
ALTER TABLE user_consents ENABLE ROW LEVEL SECURITY;

-- Policy: User peut voir ses consentements
CREATE POLICY user_consents_user_read ON user_consents
    FOR SELECT
    USING (user_id = auth.uid());

-- Policy: User peut créer/modifier ses consentements
CREATE POLICY user_consents_user_write ON user_consents
    FOR ALL
    USING (user_id = auth.uid());

-- Policy: Admin peut tout voir
CREATE POLICY user_consents_admin_all ON user_consents
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role = 'admin'
        )
    );


-- ============================================
-- TABLE GDPR_DELETION_REQUESTS (Demandes suppression)
-- ============================================

CREATE TABLE IF NOT EXISTS gdpr_deletion_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    user_email VARCHAR(255),

    -- Type de suppression
    deletion_type VARCHAR(20) NOT NULL, -- 'full' ou 'anonymize'
    status VARCHAR(20) DEFAULT 'processing', -- processing, completed, failed

    -- Raison
    reason TEXT,

    -- Dates
    requested_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,

    -- Résultats
    deleted_tables JSONB,
    error TEXT,

    -- Métadonnées
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_gdpr_deletions_user ON gdpr_deletion_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_gdpr_deletions_status ON gdpr_deletion_requests(status);
CREATE INDEX IF NOT EXISTS idx_gdpr_deletions_date ON gdpr_deletion_requests(requested_at);

-- RLS: Table accessible seulement par admins (données sensibles)
ALTER TABLE gdpr_deletion_requests ENABLE ROW LEVEL SECURITY;

-- Policy: Admin uniquement
CREATE POLICY gdpr_deletions_admin_only ON gdpr_deletion_requests
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role = 'admin'
        )
    );


-- ============================================
-- TABLE AUDIT_LOGS (Logs d'audit GDPR)
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Action
    action VARCHAR(100) NOT NULL, -- login, logout, data_export, consent_update, etc.
    resource_type VARCHAR(50), -- users, products, invoices, etc.
    resource_id UUID,

    -- Détails
    details JSONB DEFAULT '{}',

    -- Métadonnées requête
    ip_address INET,
    user_agent TEXT,
    method VARCHAR(10), -- GET, POST, PUT, DELETE
    endpoint VARCHAR(255),

    -- Success/Failure
    status VARCHAR(20) DEFAULT 'success', -- success, failure, error
    error_message TEXT,

    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index (performance)
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_date ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip ON audit_logs(ip_address);

-- Partitionnement par mois (pour performance)
-- TODO: Mettre en place quand la table devient grosse

-- RLS
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Policy: User peut voir ses propres logs
CREATE POLICY audit_logs_user_read ON audit_logs
    FOR SELECT
    USING (user_id = auth.uid());

-- Policy: Admin peut tout voir
CREATE POLICY audit_logs_admin_all ON audit_logs
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role = 'admin'
        )
    );


-- ============================================
-- TABLE LOGIN_HISTORY (Historique connexions)
-- ============================================

CREATE TABLE IF NOT EXISTS login_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Type d'événement
    event_type VARCHAR(50) NOT NULL, -- login, logout, login_failed, password_reset, 2fa_enabled

    -- Métadonnées
    ip_address INET,
    user_agent TEXT,
    country VARCHAR(2),
    city VARCHAR(100),
    device_type VARCHAR(50), -- desktop, mobile, tablet

    -- Success/Failure
    success BOOLEAN DEFAULT TRUE,
    failure_reason VARCHAR(255),

    -- 2FA
    two_factor_used BOOLEAN DEFAULT FALSE,

    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_login_history_user ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_date ON login_history(created_at);
CREATE INDEX IF NOT EXISTS idx_login_history_event ON login_history(event_type);
CREATE INDEX IF NOT EXISTS idx_login_history_ip ON login_history(ip_address);

-- RLS
ALTER TABLE login_history ENABLE ROW LEVEL SECURITY;

-- Policy: User peut voir son historique
CREATE POLICY login_history_user_read ON login_history
    FOR SELECT
    USING (user_id = auth.uid());

-- Policy: Admin peut tout voir
CREATE POLICY login_history_admin_all ON login_history
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role = 'admin'
        )
    );


-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Update timestamp user_consents
CREATE OR REPLACE FUNCTION update_user_consents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_consents_updated_at
    BEFORE UPDATE ON user_consents
    FOR EACH ROW
    EXECUTE FUNCTION update_user_consents_updated_at();


-- Trigger: Update timestamp gdpr_deletion_requests
CREATE OR REPLACE FUNCTION update_gdpr_deletions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();

    -- Auto-set completed_at si status = completed
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        NEW.completed_at = NOW();
    END IF;

    -- Auto-set failed_at si status = failed
    IF NEW.status = 'failed' AND OLD.status != 'failed' THEN
        NEW.failed_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_gdpr_deletions_updated_at
    BEFORE UPDATE ON gdpr_deletion_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_gdpr_deletions_updated_at();


-- ============================================
-- FONCTION: Nettoyer vieux logs (GDPR - minimisation)
-- ============================================

CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(
    retention_months INTEGER DEFAULT 25 -- 25 mois max (GDPR cookies)
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
    v_cutoff_date TIMESTAMP;
BEGIN
    v_cutoff_date := NOW() - INTERVAL '1 month' * retention_months;

    DELETE FROM audit_logs
    WHERE created_at < v_cutoff_date
    AND action NOT IN ('gdpr_data_export', 'account_deletion'); -- Garder les actions GDPR importantes

    GET DIAGNOSTICS v_count = ROW_COUNT;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- VUES
-- ============================================

-- Vue: Statistiques consentements
CREATE OR REPLACE VIEW consent_statistics AS
SELECT
    consent_type,
    COUNT(*) AS total_consents,
    SUM(CASE WHEN analytics_cookies THEN 1 ELSE 0 END) AS analytics_accepted,
    SUM(CASE WHEN marketing_cookies THEN 1 ELSE 0 END) AS marketing_accepted,
    SUM(CASE WHEN personalization_cookies THEN 1 ELSE 0 END) AS personalization_accepted,
    SUM(CASE WHEN revoked THEN 1 ELSE 0 END) AS revoked_count,
    ROUND(AVG(CASE WHEN analytics_cookies THEN 100 ELSE 0 END), 2) AS analytics_rate,
    ROUND(AVG(CASE WHEN marketing_cookies THEN 100 ELSE 0 END), 2) AS marketing_rate,
    ROUND(AVG(CASE WHEN personalization_cookies THEN 100 ELSE 0 END), 2) AS personalization_rate
FROM user_consents
GROUP BY consent_type;


-- Vue: Dashboard GDPR admin
CREATE OR REPLACE VIEW gdpr_admin_dashboard AS
SELECT
    (SELECT COUNT(*) FROM user_consents WHERE consent_type = 'cookies') AS total_cookie_consents,
    (SELECT COUNT(*) FROM user_consents WHERE marketing_cookies = TRUE) AS marketing_consents,
    (SELECT COUNT(*) FROM gdpr_deletion_requests WHERE status = 'completed') AS total_deletions,
    (SELECT COUNT(*) FROM gdpr_deletion_requests WHERE status = 'processing') AS pending_deletions,
    (SELECT COUNT(*) FROM audit_logs WHERE action = 'gdpr_data_export') AS total_data_exports,
    (SELECT COUNT(*) FROM login_history WHERE created_at > NOW() - INTERVAL '30 days') AS logins_last_30_days;


-- ============================================
-- DONNÉES INITIALES
-- ============================================

-- Exemple de consentement par défaut (optionnel)
-- Les users qui s'inscrivent maintenant auront un consentement "necessary only" par défaut


-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON TABLE user_consents IS 'Consentements cookies et GDPR des utilisateurs (granulaire)';
COMMENT ON TABLE gdpr_deletion_requests IS 'Demandes de suppression de compte (Right to be forgotten)';
COMMENT ON TABLE audit_logs IS 'Logs d\'audit pour traçabilité GDPR';
COMMENT ON TABLE login_history IS 'Historique des connexions utilisateurs (sécurité + GDPR)';

COMMENT ON COLUMN user_consents.necessary_cookies IS 'Cookies essentiels (toujours TRUE, non désactivables)';
COMMENT ON COLUMN user_consents.analytics_cookies IS 'Google Analytics, statistiques (optionnel)';
COMMENT ON COLUMN user_consents.marketing_cookies IS 'Publicité ciblée, remarketing (optionnel)';
COMMENT ON COLUMN user_consents.personalization_cookies IS 'Préférences UX, personnalisation (optionnel)';

COMMENT ON COLUMN gdpr_deletion_requests.deletion_type IS 'full = suppression totale, anonymize = anonymisation';
COMMENT ON COLUMN gdpr_deletion_requests.deleted_tables IS 'Liste des tables supprimées (JSON)';
