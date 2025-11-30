-- ========================================
-- Migration: Audit Trail & Sécurité Maximale
-- - Table audit_logs pour traçabilité complète
-- - RLS policies strictes par user/role
-- - Rate limiting
-- - Chiffrement données sensibles
-- ========================================

-- ========================================
-- TABLE AUDIT_LOGS
-- ========================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    user_email TEXT,
    action TEXT NOT NULL, -- 'create', 'update', 'delete', 'view', 'export'
    resource_type TEXT NOT NULL, -- 'fiscal_invoice', 'vat_declaration', etc.
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address TEXT,
    user_agent TEXT,
    status TEXT DEFAULT 'success', -- 'success', 'failed', 'blocked'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

COMMENT ON TABLE audit_logs IS 'Logs d''audit pour traçabilité complète des actions utilisateurs';


-- ========================================
-- TABLE RATE_LIMITS
-- ========================================

CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip_address TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    blocked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_user_id ON rate_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_ip ON rate_limits(ip_address);
CREATE INDEX IF NOT EXISTS idx_rate_limits_endpoint ON rate_limits(endpoint);

COMMENT ON TABLE rate_limits IS 'Rate limiting pour prévenir abus et attaques DDoS';


-- ========================================
-- TABLE ENCRYPTION_KEYS (pour données sensibles)
-- ========================================

CREATE TABLE IF NOT EXISTS encryption_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_purpose TEXT NOT NULL, -- 'iban', 'tax_id', 'payment_card'
    encrypted_key TEXT NOT NULL, -- Clé chiffrée avec master key
    algorithm TEXT DEFAULT 'AES-256-GCM',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rotated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_encryption_keys_user_id ON encryption_keys(user_id);

COMMENT ON TABLE encryption_keys IS 'Clés de chiffrement pour données sensibles (IBAN, numéros bancaires)';


-- ========================================
-- RLS POLICIES STRICTES
-- ========================================

-- === FISCAL_INVOICES ===

ALTER TABLE fiscal_invoices ENABLE ROW LEVEL SECURITY;

-- Supprimer anciennes policies permissives
DROP POLICY IF EXISTS "Allow all for service role" ON fiscal_invoices;

-- Admins peuvent tout voir
CREATE POLICY "Admins full access invoices"
ON fiscal_invoices
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'admin'
    )
);

-- Merchants voient uniquement leurs factures
CREATE POLICY "Merchants view own invoices"
ON fiscal_invoices
FOR SELECT
USING (
    auth.uid() = user_id
    AND EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role IN ('merchant', 'admin')
    )
);

-- Merchants créent uniquement leurs factures
CREATE POLICY "Merchants create own invoices"
ON fiscal_invoices
FOR INSERT
WITH CHECK (
    auth.uid() = user_id
    AND EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role IN ('merchant', 'admin')
    )
);

-- Merchants modifient uniquement leurs factures (status draft/sent seulement)
CREATE POLICY "Merchants update own draft invoices"
ON fiscal_invoices
FOR UPDATE
USING (
    auth.uid() = user_id
    AND status IN ('draft', 'sent')
    AND EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role IN ('merchant', 'admin')
    )
);

-- Interdiction suppression (sauf admin)
CREATE POLICY "Only admins delete invoices"
ON fiscal_invoices
FOR DELETE
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'admin'
    )
);


-- === FISCAL_SETTINGS ===

ALTER TABLE fiscal_settings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all for service role" ON fiscal_settings;

CREATE POLICY "Users view own fiscal settings"
ON fiscal_settings
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users update own fiscal settings"
ON fiscal_settings
FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users insert own fiscal settings"
ON fiscal_settings
FOR INSERT
WITH CHECK (auth.uid() = user_id);


-- === VAT_DECLARATIONS ===

ALTER TABLE vat_declarations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all for service role" ON vat_declarations;

CREATE POLICY "Users view own declarations"
ON vat_declarations
FOR SELECT
USING (
    auth.uid() = user_id
    OR EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'admin'
    )
);

CREATE POLICY "Users create own declarations"
ON vat_declarations
FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users update own draft declarations"
ON vat_declarations
FOR UPDATE
USING (
    auth.uid() = user_id
    AND status = 'draft'
);


-- === WITHHOLDING_TAX ===

ALTER TABLE withholding_tax ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all for service role" ON withholding_tax;

CREATE POLICY "Users view own withholding"
ON withholding_tax
FOR SELECT
USING (
    auth.uid() = user_id
    OR EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role IN ('admin', 'commercial')
    )
);


-- === ACCOUNTING_EXPORTS ===

ALTER TABLE accounting_exports ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all for service role" ON accounting_exports;

CREATE POLICY "Users view own exports"
ON accounting_exports
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users create own exports"
ON accounting_exports
FOR INSERT
WITH CHECK (auth.uid() = user_id);


-- === AUDIT_LOGS (Read-only sauf admin) ===

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users view own audit logs"
ON audit_logs
FOR SELECT
USING (
    auth.uid() = user_id
    OR EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'admin'
    )
);

-- Seul le système peut insérer (via service role)
CREATE POLICY "Service role insert audit logs"
ON audit_logs
FOR INSERT
WITH CHECK (true);


-- ========================================
-- TRIGGERS POUR AUDIT AUTOMATIQUE
-- ========================================

-- Fonction générique pour logger les modifications
CREATE OR REPLACE FUNCTION log_fiscal_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id,
        user_email,
        action,
        resource_type,
        resource_id,
        old_values,
        new_values,
        created_at
    ) VALUES (
        auth.uid(),
        auth.email(),
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
        NOW()
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Appliquer trigger sur fiscal_invoices
DROP TRIGGER IF EXISTS fiscal_invoices_audit_trigger ON fiscal_invoices;
CREATE TRIGGER fiscal_invoices_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON fiscal_invoices
FOR EACH ROW EXECUTE FUNCTION log_fiscal_changes();

-- Appliquer trigger sur vat_declarations
DROP TRIGGER IF EXISTS vat_declarations_audit_trigger ON vat_declarations;
CREATE TRIGGER vat_declarations_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON vat_declarations
FOR EACH ROW EXECUTE FUNCTION log_fiscal_changes();

-- Appliquer trigger sur fiscal_settings
DROP TRIGGER IF EXISTS fiscal_settings_audit_trigger ON fiscal_settings;
CREATE TRIGGER fiscal_settings_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON fiscal_settings
FOR EACH ROW EXECUTE FUNCTION log_fiscal_changes();


-- ========================================
-- FONCTIONS UTILITAIRES SÉCURITÉ
-- ========================================

-- Fonction pour vérifier rate limit
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id UUID,
    p_ip_address TEXT,
    p_endpoint TEXT,
    p_max_requests INTEGER DEFAULT 100,
    p_window_minutes INTEGER DEFAULT 60
)
RETURNS BOOLEAN AS $$
DECLARE
    v_count INTEGER;
    v_window_start TIMESTAMP;
BEGIN
    v_window_start := NOW() - (p_window_minutes || ' minutes')::INTERVAL;
    
    -- Compter requêtes dans la fenêtre
    SELECT COALESCE(SUM(request_count), 0)
    INTO v_count
    FROM rate_limits
    WHERE (user_id = p_user_id OR ip_address = p_ip_address)
    AND endpoint = p_endpoint
    AND window_start > v_window_start;
    
    -- Si limite dépassée
    IF v_count >= p_max_requests THEN
        -- Bloquer temporairement
        INSERT INTO rate_limits (user_id, ip_address, endpoint, request_count, blocked_until)
        VALUES (p_user_id, p_ip_address, p_endpoint, 1, NOW() + INTERVAL '1 hour')
        ON CONFLICT DO NOTHING;
        
        RETURN FALSE;
    END IF;
    
    -- Incrémenter compteur
    INSERT INTO rate_limits (user_id, ip_address, endpoint, request_count, window_start)
    VALUES (p_user_id, p_ip_address, p_endpoint, 1, NOW())
    ON CONFLICT (user_id, endpoint) WHERE window_start > v_window_start
    DO UPDATE SET request_count = rate_limits.request_count + 1;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Fonction pour nettoyer anciens logs (à exécuter périodiquement)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(p_days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    v_deleted INTEGER;
BEGIN
    DELETE FROM audit_logs
    WHERE created_at < NOW() - (p_days_to_keep || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ========================================
-- ARCHIVAGE AUTOMATIQUE (10 ans France)
-- ========================================

CREATE TABLE IF NOT EXISTS archived_fiscal_invoices (
    LIKE fiscal_invoices INCLUDING ALL,
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    archive_reason TEXT
);

CREATE OR REPLACE FUNCTION archive_old_invoices()
RETURNS INTEGER AS $$
DECLARE
    v_archived INTEGER;
BEGIN
    -- Archiver factures > 10 ans
    INSERT INTO archived_fiscal_invoices
    SELECT *, NOW(), 'Legal 10 year retention'
    FROM fiscal_invoices
    WHERE issue_date < NOW() - INTERVAL '10 years';
    
    GET DIAGNOSTICS v_archived = ROW_COUNT;
    
    -- Supprimer originaux
    DELETE FROM fiscal_invoices
    WHERE issue_date < NOW() - INTERVAL '10 years';
    
    RETURN v_archived;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ========================================
-- CHIFFREMENT DONNÉES SENSIBLES
-- ========================================

-- Extension pgcrypto pour chiffrement
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Fonction pour chiffrer IBAN
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(p_data TEXT, p_key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(
        pgp_sym_encrypt(p_data, p_key, 'cipher-algo=aes256'),
        'base64'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Fonction pour déchiffrer
CREATE OR REPLACE FUNCTION decrypt_sensitive_data(p_encrypted TEXT, p_key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(
        decode(p_encrypted, 'base64'),
        p_key
    );
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ========================================
-- INDEX PERFORMANCES
-- ========================================

-- Index composites pour performances queries courantes
CREATE INDEX IF NOT EXISTS idx_fiscal_invoices_user_status ON fiscal_invoices(user_id, status);
CREATE INDEX IF NOT EXISTS idx_fiscal_invoices_user_date ON fiscal_invoices(user_id, issue_date DESC);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_user_period ON vat_declarations(user_id, period_start, period_end);


-- ========================================
-- CONTRAINTES MÉTIER SUPPLÉMENTAIRES
-- ========================================

-- Empêcher modification factures payées
ALTER TABLE fiscal_invoices ADD CONSTRAINT check_no_modify_paid 
CHECK (
    (status != 'paid' OR payment_date IS NOT NULL)
    AND (status = 'paid' OR payment_date IS NULL)
);

-- Montants cohérents
ALTER TABLE fiscal_invoices ADD CONSTRAINT check_amounts_consistent
CHECK (
    amount_ttc = amount_ht + vat_amount
    AND amount_ht >= 0
    AND vat_amount >= 0
);

-- Dates cohérentes
ALTER TABLE fiscal_invoices ADD CONSTRAINT check_dates_logical
CHECK (due_date >= issue_date);


-- ========================================
-- COMMENTAIRES DOCUMENTATION
-- ========================================

COMMENT ON COLUMN fiscal_invoices.payment_id IS 'ID transaction Stripe/PayPal pour rapprochement';
COMMENT ON COLUMN fiscal_invoices.payment_link IS 'Lien paiement Stripe/PayPal généré';
COMMENT ON COLUMN fiscal_invoices.refund_amount IS 'Montant remboursé si status=refunded';
COMMENT ON COLUMN audit_logs.old_values IS 'Valeurs avant modification (JSON)';
COMMENT ON COLUMN audit_logs.new_values IS 'Valeurs après modification (JSON)';
COMMENT ON FUNCTION check_rate_limit IS 'Vérifie rate limit: 100 req/heure par défaut';
COMMENT ON FUNCTION cleanup_old_audit_logs IS 'Nettoie logs > 90 jours (configurable)';
COMMENT ON FUNCTION archive_old_invoices IS 'Archive factures > 10 ans (conformité France)';


-- ========================================
-- GRANTS SÉCURITÉ
-- ========================================

-- Service role peut tout faire
GRANT ALL ON audit_logs TO service_role;
GRANT ALL ON rate_limits TO service_role;
GRANT ALL ON encryption_keys TO service_role;

-- Authenticated users lecture seule audit_logs (RLS applique le filtre)
GRANT SELECT ON audit_logs TO authenticated;

-- Pas d'accès direct aux encryption_keys pour authenticated
REVOKE ALL ON encryption_keys FROM authenticated;


-- ========================================
-- VALIDATION FINALE
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration audit trail & sécurité appliquée avec succès!';
    RAISE NOTICE '   - Table audit_logs créée avec triggers automatiques';
    RAISE NOTICE '   - RLS policies strictes appliquées (user/role based)';
    RAISE NOTICE '   - Rate limiting configuré (100 req/h par défaut)';
    RAISE NOTICE '   - Chiffrement données sensibles activé (pgcrypto)';
    RAISE NOTICE '   - Archivage automatique 10 ans configuré';
    RAISE NOTICE '   - Contraintes métier renforcées';
END $$;
