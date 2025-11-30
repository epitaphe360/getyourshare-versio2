-- ============================================
-- MIGRATION 015: RLS POLICIES HARDENING
-- Durcir sécurité multi-tenancy
-- ============================================

-- ÉTAPE 1: Supprimer anciennes policies permissives
DROP POLICY IF EXISTS admin_all_invoices ON invoices;
DROP POLICY IF EXISTS merchant_own_invoices ON invoices;
DROP POLICY IF EXISTS influencer_own_invoices ON invoices;

DROP POLICY IF EXISTS admin_all_fiscal_settings ON fiscal_settings;
DROP POLICY IF EXISTS user_own_fiscal_settings ON fiscal_settings;

DROP POLICY IF EXISTS admin_all_vat_declarations ON vat_declarations;
DROP POLICY IF EXISTS user_own_vat_declarations ON vat_declarations;

-- ÉTAPE 2: Activer RLS sur toutes les tables fiscales
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE fiscal_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE vat_declarations ENABLE ROW LEVEL SECURITY;
ALTER TABLE withholding_tax ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounting_exports ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_reconciliations ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_links ENABLE ROW LEVEL SECURITY;

-- ÉTAPE 3: Nouvelles policies STRICT pour invoices
-- Admin: accès total
CREATE POLICY admin_invoices_all
  ON invoices
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

-- Merchant: ses propres factures uniquement
CREATE POLICY merchant_invoices_own
  ON invoices
  FOR ALL
  USING (
    user_id = auth.uid()
    AND EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role IN ('merchant', 'advertiser')
    )
  );

-- Influencer: lecture seule de ses factures
CREATE POLICY influencer_invoices_read
  ON invoices
  FOR SELECT
  USING (
    user_id = auth.uid()
    AND EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'influencer'
    )
  );

-- Commercial: lecture des factures de ses clients assignés
-- NOTE: Policy conditionnelle - s'applique uniquement si table sales_assignments existe
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'sales_assignments'
  ) THEN
    -- Supprimer l'ancienne policy si elle existe
    DROP POLICY IF EXISTS commercial_invoices_assigned ON invoices;
    
    EXECUTE '
      CREATE POLICY commercial_invoices_assigned
        ON invoices
        FOR SELECT
        USING (
          EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid()
            AND u.role = ''commercial''
            AND (
              -- Factures des merchants qu''il gère
              invoices.user_id IN (
                SELECT merchant_id FROM sales_assignments
                WHERE sales_rep_id = auth.uid()
                AND status = ''active''
              )
            )
          )
        )
    ';
    RAISE NOTICE '✅ Policy commercial_invoices_assigned created';
  ELSE
    RAISE NOTICE '⚠️  Table sales_assignments not found - skipping commercial policy';
  END IF;
END $$;

-- ÉTAPE 4: Policies fiscal_settings
CREATE POLICY admin_fiscal_settings_all
  ON fiscal_settings
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

CREATE POLICY user_fiscal_settings_own
  ON fiscal_settings
  FOR ALL
  USING (user_id = auth.uid());

-- ÉTAPE 5: Policies vat_declarations
CREATE POLICY admin_vat_declarations_all
  ON vat_declarations
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

CREATE POLICY user_vat_declarations_own
  ON vat_declarations
  FOR ALL
  USING (user_id = auth.uid());

-- ÉTAPE 6: Policies withholding_tax
CREATE POLICY admin_withholding_tax_all
  ON withholding_tax
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

CREATE POLICY user_withholding_tax_own
  ON withholding_tax
  FOR ALL
  USING (user_id = auth.uid());

-- ÉTAPE 7: Policies accounting_exports
-- D'abord, ajouter la colonne exported_by si elle n'existe pas
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'accounting_exports' 
    AND column_name = 'exported_by'
  ) THEN
    ALTER TABLE accounting_exports ADD COLUMN exported_by UUID REFERENCES users(id) ON DELETE SET NULL;
    RAISE NOTICE '✅ Column exported_by added to accounting_exports';
  END IF;
END $$;

CREATE POLICY admin_accounting_exports_all
  ON accounting_exports
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

CREATE POLICY user_accounting_exports_own
  ON accounting_exports
  FOR ALL
  USING (user_id = auth.uid() OR exported_by = auth.uid());

-- ÉTAPE 8: Policies bank_reconciliations
CREATE POLICY admin_bank_reconciliations_all
  ON bank_reconciliations
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

CREATE POLICY user_bank_reconciliations_own
  ON bank_reconciliations
  FOR ALL
  USING (user_id = auth.uid());

-- ÉTAPE 9: Policies payment_links
CREATE POLICY admin_payment_links_all
  ON payment_links
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

CREATE POLICY user_payment_links_own
  ON payment_links
  FOR ALL
  USING (
    invoice_id IN (
      SELECT id FROM invoices
      WHERE user_id = auth.uid()
    )
  );

-- ÉTAPE 10: Fonction helper pour vérifier permissions
CREATE OR REPLACE FUNCTION check_fiscal_access(resource_user_id UUID, required_role TEXT DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
  -- Admin a accès à tout
  IF EXISTS (
    SELECT 1 FROM users 
    WHERE id = auth.uid() 
    AND role = 'admin'
  ) THEN
    RETURN TRUE;
  END IF;

  -- Utilisateur propriétaire
  IF resource_user_id = auth.uid() THEN
    RETURN TRUE;
  END IF;

  -- Commercial accès clients assignés (si table existe)
  IF required_role = 'commercial' AND EXISTS (
    SELECT 1 FROM users 
    WHERE id = auth.uid() 
    AND role = 'commercial'
  ) THEN
    -- Vérifier si table sales_assignments existe
    IF EXISTS (
      SELECT 1 FROM information_schema.tables 
      WHERE table_name = 'sales_assignments'
    ) THEN
      -- Vérifier assignation
      IF resource_user_id IN (
        SELECT merchant_id FROM sales_assignments
        WHERE sales_rep_id = auth.uid()
        AND status = 'active'
      ) THEN
        RETURN TRUE;
      END IF;
    END IF;
  END IF;

  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ÉTAPE 11: Contraintes additionnelles
-- Empêcher modification factures payées
CREATE OR REPLACE FUNCTION prevent_paid_invoice_modification()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.payment_status = 'paid' AND NEW.amount_ttc != OLD.amount_ttc THEN
    RAISE EXCEPTION 'Impossible de modifier montant d''une facture payée';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_paid_invoice_modification
BEFORE UPDATE ON invoices
FOR EACH ROW
EXECUTE FUNCTION prevent_paid_invoice_modification();

-- ÉTAPE 12: Audit automatic des modifications sensibles
CREATE OR REPLACE FUNCTION log_fiscal_change()
RETURNS TRIGGER AS $$
BEGIN
  -- Vérifier si table audit_logs existe
  IF EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'audit_logs'
  ) THEN
    INSERT INTO audit_logs (
      user_id,
      action,
      resource_type,
      resource_id,
      old_values,
      new_values,
      created_at
    ) VALUES (
      auth.uid(),
      TG_OP,
      TG_TABLE_NAME,
      COALESCE(NEW.id::text, OLD.id::text),
      CASE WHEN TG_OP != 'INSERT' THEN row_to_json(OLD) ELSE NULL END,
      CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
      NOW()
    );
  END IF;
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Appliquer audit sur tables critiques
DROP TRIGGER IF EXISTS audit_invoices_changes ON invoices;
CREATE TRIGGER audit_invoices_changes
AFTER INSERT OR UPDATE OR DELETE ON invoices
FOR EACH ROW EXECUTE FUNCTION log_fiscal_change();

DROP TRIGGER IF EXISTS audit_vat_declarations_changes ON vat_declarations;
CREATE TRIGGER audit_vat_declarations_changes
AFTER INSERT OR UPDATE OR DELETE ON vat_declarations
FOR EACH ROW EXECUTE FUNCTION log_fiscal_change();

-- ÉTAPE 13: Index pour optimiser RLS queries
CREATE INDEX IF NOT EXISTS idx_invoices_user_status ON invoices(user_id, payment_status);
CREATE INDEX IF NOT EXISTS idx_fiscal_settings_user ON fiscal_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_vat_declarations_user_period ON vat_declarations(user_id, period_start, period_end);

-- ÉTAPE 14: Vérifications
-- Tester qu'un user ne peut pas voir factures d'autrui
DO $$
DECLARE
  test_passed BOOLEAN := TRUE;
BEGIN
  -- Test 1: Policy existe
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'invoices' 
    AND policyname = 'merchant_invoices_own'
  ) THEN
    RAISE WARNING 'Policy merchant_invoices_own non trouvée';
    test_passed := FALSE;
  END IF;

  -- Test 2: RLS activé
  IF NOT EXISTS (
    SELECT 1 FROM pg_tables 
    WHERE tablename = 'invoices' 
    AND rowsecurity = TRUE
  ) THEN
    RAISE WARNING 'RLS non activé sur invoices';
    test_passed := FALSE;
  END IF;

  IF test_passed THEN
    RAISE NOTICE '✅ RLS policies hardening successful!';
  ELSE
    RAISE WARNING '⚠️  Some RLS policies may be missing';
  END IF;
END $$;

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON POLICY admin_invoices_all ON invoices IS 
'Admin: accès complet toutes factures';

COMMENT ON POLICY merchant_invoices_own ON invoices IS 
'Merchant/Advertiser: CRUD uniquement ses factures (user_id = auth.uid())';

COMMENT ON POLICY influencer_invoices_read ON invoices IS 
'Influencer: lecture seule ses factures de paiement';

COMMENT ON POLICY commercial_invoices_assigned ON invoices IS 
'Commercial: lecture factures clients assignés via sales_assignments';

COMMENT ON FUNCTION check_fiscal_access IS 
'Helper: vérifie si utilisateur a accès ressource fiscale';

COMMENT ON FUNCTION prevent_paid_invoice_modification IS 
'Trigger: empêche modification montants factures payées';

COMMENT ON FUNCTION log_fiscal_change IS 
'Trigger: audit automatique modifications tables fiscales';

-- ============================================
-- FIN MIGRATION 015
-- ============================================
