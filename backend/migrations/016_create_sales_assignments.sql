-- ============================================
-- MIGRATION 016: Table sales_assignments
-- Système d'assignation commerciaux → clients
-- ============================================

-- Table principale: assignations commerciaux
CREATE TABLE IF NOT EXISTS sales_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sales_rep_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  merchant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assigned_at TIMESTAMP DEFAULT NOW(),
  assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'completed')),
  target_revenue DECIMAL(12,2) DEFAULT 0,
  commission_rate DECIMAL(5,2) DEFAULT 10.00,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(sales_rep_id, merchant_id)
);

-- Index pour optimisation
CREATE INDEX IF NOT EXISTS idx_sales_assignments_rep ON sales_assignments(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_sales_assignments_merchant ON sales_assignments(merchant_id);
CREATE INDEX IF NOT EXISTS idx_sales_assignments_status ON sales_assignments(status);
CREATE INDEX IF NOT EXISTS idx_sales_assignments_rep_status ON sales_assignments(sales_rep_id, status);

-- RLS pour sales_assignments
ALTER TABLE sales_assignments ENABLE ROW LEVEL SECURITY;

-- Admin: accès total
CREATE POLICY admin_sales_assignments_all
  ON sales_assignments
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

-- Commercial: voir ses assignations
CREATE POLICY commercial_sales_assignments_own
  ON sales_assignments
  FOR SELECT
  USING (sales_rep_id = auth.uid());

-- Merchant: voir ses commerciaux assignés
CREATE POLICY merchant_sales_assignments_assigned
  ON sales_assignments
  FOR SELECT
  USING (merchant_id = auth.uid());

-- Trigger updated_at
CREATE TRIGGER trg_sales_assignments_updated 
BEFORE UPDATE ON sales_assignments
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Fonction pour auto-assigner commercial lors inscription merchant
CREATE OR REPLACE FUNCTION auto_assign_sales_rep()
RETURNS TRIGGER AS $$
DECLARE
  available_rep_id UUID;
BEGIN
  -- Si nouveau merchant sans commercial assigné
  IF NEW.role IN ('merchant', 'advertiser') AND NEW.commercial_id IS NULL THEN
    -- Trouver commercial avec le moins de clients
    SELECT u.id INTO available_rep_id
    FROM users u
    WHERE u.role = 'commercial'
    AND u.is_active = TRUE
    ORDER BY (
      SELECT COUNT(*) FROM sales_assignments sa
      WHERE sa.sales_rep_id = u.id
      AND sa.status = 'active'
    ) ASC
    LIMIT 1;
    
    -- Si commercial trouvé, créer assignation
    IF available_rep_id IS NOT NULL THEN
      INSERT INTO sales_assignments (
        sales_rep_id,
        merchant_id,
        assigned_by,
        status
      ) VALUES (
        available_rep_id,
        NEW.id,
        NEW.id, -- Auto-assigné
        'active'
      );
      
      -- Mettre à jour commercial_id dans users
      NEW.commercial_id := available_rep_id;
    END IF;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger auto-assignation
CREATE TRIGGER trg_auto_assign_sales_rep
BEFORE INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION auto_assign_sales_rep();

-- Données test (optionnel)
DO $$
DECLARE
  admin_user_id UUID;
  commercial_user_id UUID;
  merchant1_id UUID;
  merchant2_id UUID;
BEGIN
  -- Trouver admin
  SELECT id INTO admin_user_id FROM users WHERE role = 'admin' LIMIT 1;
  
  -- Créer commercial test si n'existe pas
  INSERT INTO users (email, full_name, role, is_active, created_at)
  VALUES ('commercial@getyourshare.com', 'Commercial Demo', 'commercial', TRUE, NOW())
  ON CONFLICT (email) DO UPDATE SET role = 'commercial'
  RETURNING id INTO commercial_user_id;
  
  -- Créer 2 merchants test
  INSERT INTO users (email, full_name, role, is_active, created_at)
  VALUES ('merchant1@test.com', 'Merchant Test 1', 'merchant', TRUE, NOW())
  ON CONFLICT (email) DO UPDATE SET role = 'merchant'
  RETURNING id INTO merchant1_id;
  
  INSERT INTO users (email, full_name, role, is_active, created_at)
  VALUES ('merchant2@test.com', 'Merchant Test 2', 'merchant', TRUE, NOW())
  ON CONFLICT (email) DO UPDATE SET role = 'merchant'
  RETURNING id INTO merchant2_id;
  
  -- Créer assignations
  INSERT INTO sales_assignments (sales_rep_id, merchant_id, assigned_by, status)
  VALUES 
    (commercial_user_id, merchant1_id, admin_user_id, 'active'),
    (commercial_user_id, merchant2_id, admin_user_id, 'active')
  ON CONFLICT (sales_rep_id, merchant_id) DO NOTHING;
  
  RAISE NOTICE '✅ Données test sales_assignments créées';
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE '⚠️  Erreur création données test: %', SQLERRM;
END $$;

-- Maintenant recréer policy commercial avec table existante
DROP POLICY IF EXISTS commercial_invoices_assigned ON invoices;

CREATE POLICY commercial_invoices_assigned
  ON invoices
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users u
      WHERE u.id = auth.uid()
      AND u.role = 'commercial'
      AND (
        -- Factures des merchants qu'il gère
        invoices.user_id IN (
          SELECT merchant_id FROM sales_assignments
          WHERE sales_rep_id = auth.uid()
          AND status = 'active'
        )
      )
    )
  );

-- Vérifications
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'sales_assignments') THEN
    RAISE NOTICE '✅ Table sales_assignments créée avec succès';
  END IF;
  
  IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'sales_assignments') THEN
    RAISE NOTICE '✅ RLS policies sales_assignments actives';
  END IF;
  
  IF EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'commercial_invoices_assigned' AND tablename = 'invoices') THEN
    RAISE NOTICE '✅ Policy commercial_invoices_assigned recréée';
  END IF;
END $$;

-- Commentaires
COMMENT ON TABLE sales_assignments IS 
'Assignations commerciaux → merchants pour gestion clients et commissions';

COMMENT ON COLUMN sales_assignments.target_revenue IS 
'Objectif CA mensuel pour ce client (optionnel)';

COMMENT ON COLUMN sales_assignments.commission_rate IS 
'Taux commission commercial sur CA client (%)';

COMMENT ON FUNCTION auto_assign_sales_rep IS 
'Trigger: auto-assigne commercial disponible lors inscription merchant (load balancing)';

-- ============================================
-- FIN MIGRATION 016
-- ============================================
