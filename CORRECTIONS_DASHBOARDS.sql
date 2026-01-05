-- ============================================
-- CONTRAINTE UNIQUE MARKETING_TEMPLATES
-- ============================================
-- Empêche les doublons de templates avec même nom pour un commercial

-- Ajouter contrainte unique sur (commercial_id, name)
ALTER TABLE marketing_templates 
ADD CONSTRAINT unique_commercial_template_name 
UNIQUE (commercial_id, name);

-- ============================================
-- TABLE TASKS PERSISTANTE
-- ============================================
-- Remplace génération dynamique par table persistante

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES services_leads(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) CHECK (type IN ('call', 'email', 'meeting', 'follow_up', 'proposal', 'contract', 'other')),
    priority VARCHAR(20) CHECK (priority IN ('basse', 'moyenne', 'haute', 'urgente')) DEFAULT 'moyenne',
    status VARCHAR(20) CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')) DEFAULT 'pending',
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_lead_id ON tasks(lead_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

-- Trigger updated_at
CREATE OR REPLACE FUNCTION update_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tasks_updated_at_trigger ON tasks;
CREATE TRIGGER tasks_updated_at_trigger
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();

-- RLS Policies
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- L'utilisateur ne voit que ses propres tâches
CREATE POLICY "Users see own tasks"
    ON tasks FOR SELECT
    USING (user_id = auth.uid());

-- L'utilisateur peut créer ses propres tâches
CREATE POLICY "Users create own tasks"
    ON tasks FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- L'utilisateur peut modifier ses propres tâches
CREATE POLICY "Users update own tasks"
    ON tasks FOR UPDATE
    USING (user_id = auth.uid());

-- L'utilisateur peut supprimer ses propres tâches
CREATE POLICY "Users delete own tasks"
    ON tasks FOR DELETE
    USING (user_id = auth.uid());

-- Admins ont accès complet
CREATE POLICY "Admins full access tasks"
    ON tasks FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role = 'admin'
        )
    );

-- ============================================
-- INDEXES MANQUANTS POUR PERFORMANCES
-- ============================================

-- services_leads
CREATE INDEX IF NOT EXISTS idx_services_leads_commercial_id ON services_leads(commercial_id);
CREATE INDEX IF NOT EXISTS idx_services_leads_status ON services_leads(status);
CREATE INDEX IF NOT EXISTS idx_services_leads_created_at ON services_leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_services_leads_temperature ON services_leads(temperature);
CREATE INDEX IF NOT EXISTS idx_services_leads_commercial_status ON services_leads(commercial_id, status);

-- lead_activities
CREATE INDEX IF NOT EXISTS idx_lead_activities_lead_id ON lead_activities(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_activities_user_id ON lead_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_lead_activities_type ON lead_activities(type);
CREATE INDEX IF NOT EXISTS idx_lead_activities_created_at ON lead_activities(created_at DESC);

-- tracking_links
CREATE INDEX IF NOT EXISTS idx_tracking_links_influencer_id ON tracking_links(influencer_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_merchant_id ON tracking_links(merchant_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_is_active ON tracking_links(is_active);
CREATE INDEX IF NOT EXISTS idx_tracking_links_unique_code ON tracking_links(unique_code);

-- sales_representatives
CREATE INDEX IF NOT EXISTS idx_sales_reps_user_id ON sales_representatives(user_id);
CREATE INDEX IF NOT EXISTS idx_sales_reps_is_active ON sales_representatives(is_active);

-- marketing_templates
CREATE INDEX IF NOT EXISTS idx_marketing_templates_commercial_id ON marketing_templates(commercial_id);
CREATE INDEX IF NOT EXISTS idx_marketing_templates_type ON marketing_templates(type);
CREATE INDEX IF NOT EXISTS idx_marketing_templates_is_active ON marketing_templates(is_active);

-- users
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login DESC);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================
-- MESSAGE FINAL
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Corrections appliquées avec succès:';
    RAISE NOTICE '  - Contrainte unique marketing_templates';
    RAISE NOTICE '  - Table tasks créée';
    RAISE NOTICE '  - Indexes de performance ajoutés';
END $$;
