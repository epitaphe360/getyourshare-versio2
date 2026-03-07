-- ================================================
-- TABLES POUR DASHBOARD COMMERCIAL (SALES REP)
-- ================================================
-- Créer ces tables dans cet ordre (à cause des FK)
-- ================================================

-- 1. SALES REPRESENTATIVES (Commerciaux)
-- ================================================
CREATE TABLE IF NOT EXISTS sales_representatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    territory TEXT, -- 'Casablanca', 'Rabat', 'Marrakech', 'Tanger', 'Fès', 'National', etc.
    team_id UUID, -- Pour gérer les équipes de vente
    manager_id UUID REFERENCES sales_representatives(id), -- Hiérarchie
    commission_rate NUMERIC(5,2) DEFAULT 5.00 CHECK (commission_rate >= 0 AND commission_rate <= 100),
    base_salary NUMERIC(12,2),
    target_monthly_deals INTEGER DEFAULT 20,
    target_monthly_revenue NUMERIC(12,2) DEFAULT 100000,
    target_monthly_calls INTEGER DEFAULT 100,
    target_monthly_meetings INTEGER DEFAULT 20,
    employment_type TEXT DEFAULT 'full_time' CHECK (employment_type IN ('full_time', 'part_time', 'contractor', 'intern')),
    is_active BOOLEAN DEFAULT TRUE,
    hired_at TIMESTAMPTZ DEFAULT NOW(),
    terminated_at TIMESTAMPTZ,
    bio TEXT,
    avatar_url TEXT,
    linkedin_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_sales_reps_user ON sales_representatives(user_id);
CREATE INDEX IF NOT EXISTS idx_sales_reps_territory ON sales_representatives(territory);
CREATE INDEX IF NOT EXISTS idx_sales_reps_team ON sales_representatives(team_id);
CREATE INDEX IF NOT EXISTS idx_sales_reps_manager ON sales_representatives(manager_id);
CREATE INDEX IF NOT EXISTS idx_sales_reps_active ON sales_representatives(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_sales_reps_email ON sales_representatives(email);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_sales_reps_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sales_reps_updated_at
    BEFORE UPDATE ON sales_representatives
    FOR EACH ROW
    EXECUTE FUNCTION update_sales_reps_updated_at();


-- 2. MODIFIER LA TABLE LEADS (Ajouter colonnes manquantes)
-- ================================================
-- Vérifier si la table leads existe déjà
DO $$ 
BEGIN
    -- Ajouter colonnes si elles n'existent pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'sales_rep_id') THEN
        ALTER TABLE leads ADD COLUMN sales_rep_id UUID REFERENCES sales_representatives(id) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'score') THEN
        ALTER TABLE leads ADD COLUMN score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'lead_status') THEN
        ALTER TABLE leads ADD COLUMN lead_status TEXT DEFAULT 'new' CHECK (lead_status IN ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost', 'disqualified'));
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'contact_name') THEN
        ALTER TABLE leads ADD COLUMN contact_name TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'contact_email') THEN
        ALTER TABLE leads ADD COLUMN contact_email TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'contact_phone') THEN
        ALTER TABLE leads ADD COLUMN contact_phone TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'company_name') THEN
        ALTER TABLE leads ADD COLUMN company_name TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'company_size') THEN
        ALTER TABLE leads ADD COLUMN company_size TEXT CHECK (company_size IN ('1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'));
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'industry') THEN
        ALTER TABLE leads ADD COLUMN industry TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'estimated_value') THEN
        ALTER TABLE leads ADD COLUMN estimated_value NUMERIC(12,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'probability') THEN
        ALTER TABLE leads ADD COLUMN probability INTEGER DEFAULT 50 CHECK (probability >= 0 AND probability <= 100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'source') THEN
        ALTER TABLE leads ADD COLUMN source TEXT; -- 'website', 'referral', 'cold_call', 'linkedin', 'event', etc.
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'last_contacted_at') THEN
        ALTER TABLE leads ADD COLUMN last_contacted_at TIMESTAMPTZ;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'next_follow_up_at') THEN
        ALTER TABLE leads ADD COLUMN next_follow_up_at TIMESTAMPTZ;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'notes') THEN
        ALTER TABLE leads ADD COLUMN notes TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'tags') THEN
        ALTER TABLE leads ADD COLUMN tags TEXT[];
    END IF;
END $$;

-- Index sur leads
CREATE INDEX IF NOT EXISTS idx_leads_sales_rep ON leads(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(lead_status);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_next_follow_up ON leads(next_follow_up_at);


-- 3. DEALS (Opportunités de vente)
-- ================================================
CREATE TABLE IF NOT EXISTS deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sales_rep_id UUID NOT NULL REFERENCES sales_representatives(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    merchant_id UUID REFERENCES merchants(id) ON DELETE SET NULL,
    contact_name TEXT NOT NULL,
    contact_email TEXT,
    contact_phone TEXT,
    company_name TEXT,
    title TEXT NOT NULL, -- Nom du deal
    description TEXT,
    value NUMERIC(12,2) NOT NULL CHECK (value >= 0),
    currency TEXT DEFAULT 'MAD',
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'won', 'lost')),
    stage TEXT NOT NULL DEFAULT 'prospection' CHECK (stage IN ('prospection', 'qualification', 'proposal', 'negotiation', 'closing', 'closed')),
    probability INTEGER DEFAULT 50 CHECK (probability >= 0 AND probability <= 100),
    expected_close_date DATE,
    actual_close_date DATE,
    closed_at TIMESTAMPTZ,
    won_reason TEXT,
    lost_reason TEXT,
    competitor TEXT, -- Si perdu, à quel concurrent
    products_interested TEXT[], -- Array de produits intéressés
    contract_value NUMERIC(12,2),
    contract_signed BOOLEAN DEFAULT FALSE,
    contract_signed_at TIMESTAMPTZ,
    contract_url TEXT,
    commission_rate NUMERIC(5,2),
    commission_amount NUMERIC(12,2),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    tags TEXT[],
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_deals_sales_rep ON deals(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_deals_lead ON deals(lead_id);
CREATE INDEX IF NOT EXISTS idx_deals_merchant ON deals(merchant_id);
CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage);
CREATE INDEX IF NOT EXISTS idx_deals_expected_close ON deals(expected_close_date);
CREATE INDEX IF NOT EXISTS idx_deals_closed_at ON deals(closed_at DESC);
CREATE INDEX IF NOT EXISTS idx_deals_priority ON deals(priority);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_deals_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER deals_updated_at
    BEFORE UPDATE ON deals
    FOR EACH ROW
    EXECUTE FUNCTION update_deals_updated_at();


-- 4. SALES ACTIVITIES (Activités commerciales)
-- ================================================
CREATE TABLE IF NOT EXISTS sales_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sales_rep_id UUID NOT NULL REFERENCES sales_representatives(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('call', 'email', 'meeting', 'task', 'note', 'demo', 'proposal_sent', 'contract_sent', 'follow_up')),
    subject TEXT,
    description TEXT,
    outcome TEXT, -- 'completed', 'scheduled', 'cancelled', 'no_answer', 'voicemail', 'interested', 'not_interested'
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    duration_minutes INTEGER,
    location TEXT, -- Pour les meetings
    meeting_url TEXT, -- Lien Zoom/Meet
    call_recording_url TEXT,
    email_sent_to TEXT,
    email_subject TEXT,
    attendees TEXT[], -- Pour les meetings
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_sent_at TIMESTAMPTZ,
    next_action TEXT,
    next_action_date TIMESTAMPTZ,
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_activities_sales_rep ON sales_activities(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_activities_lead ON sales_activities(lead_id);
CREATE INDEX IF NOT EXISTS idx_activities_deal ON sales_activities(deal_id);
CREATE INDEX IF NOT EXISTS idx_activities_type ON sales_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_scheduled ON sales_activities(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_activities_completed ON sales_activities(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_activities_priority ON sales_activities(priority);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_sales_activities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sales_activities_updated_at
    BEFORE UPDATE ON sales_activities
    FOR EACH ROW
    EXECUTE FUNCTION update_sales_activities_updated_at();


-- 5. SALES TARGETS (Objectifs commerciaux)
-- ================================================
CREATE TABLE IF NOT EXISTS sales_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sales_rep_id UUID NOT NULL REFERENCES sales_representatives(id) ON DELETE CASCADE,
    period_type TEXT NOT NULL CHECK (period_type IN ('monthly', 'quarterly', 'yearly')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    deals_target INTEGER,
    revenue_target NUMERIC(12,2),
    calls_target INTEGER,
    meetings_target INTEGER,
    emails_target INTEGER,
    demos_target INTEGER,
    proposals_target INTEGER,
    custom_targets JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sales_rep_id, period_type, period_start)
);

-- Index
CREATE INDEX IF NOT EXISTS idx_targets_sales_rep ON sales_targets(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_targets_period ON sales_targets(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_targets_type ON sales_targets(period_type);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_sales_targets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sales_targets_updated_at
    BEFORE UPDATE ON sales_targets
    FOR EACH ROW
    EXECUTE FUNCTION update_sales_targets_updated_at();


-- 6. SALES COMMISSIONS (Commissions gagnées)
-- ================================================
CREATE TABLE IF NOT EXISTS sales_commissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sales_rep_id UUID NOT NULL REFERENCES sales_representatives(id) ON DELETE CASCADE,
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    currency TEXT DEFAULT 'MAD',
    commission_rate NUMERIC(5,2) NOT NULL,
    deal_value NUMERIC(12,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
    earned_date DATE NOT NULL,
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    paid_at TIMESTAMPTZ,
    payment_method TEXT,
    payment_reference TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_commissions_sales_rep ON sales_commissions(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_commissions_deal ON sales_commissions(deal_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON sales_commissions(status);
CREATE INDEX IF NOT EXISTS idx_commissions_earned_date ON sales_commissions(earned_date DESC);
CREATE INDEX IF NOT EXISTS idx_commissions_paid_at ON sales_commissions(paid_at DESC);


-- 7. SALES TEAMS (Équipes de vente)
-- ================================================
CREATE TABLE IF NOT EXISTS sales_teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    team_lead_id UUID REFERENCES sales_representatives(id),
    territory TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    target_monthly_revenue NUMERIC(12,2),
    target_monthly_deals INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_teams_lead ON sales_teams(team_lead_id);
CREATE INDEX IF NOT EXISTS idx_teams_active ON sales_teams(is_active) WHERE is_active = TRUE;

-- Ajouter FK vers sales_teams dans sales_representatives (si pas déjà fait)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'sales_representatives_team_id_fkey'
    ) THEN
        ALTER TABLE sales_representatives 
        ADD CONSTRAINT sales_representatives_team_id_fkey 
        FOREIGN KEY (team_id) REFERENCES sales_teams(id);
    END IF;
END $$;


-- 8. LEAD SCORING RULES (Règles de scoring des leads)
-- ================================================
CREATE TABLE IF NOT EXISTS lead_scoring_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL CHECK (rule_type IN ('demographic', 'behavioral', 'firmographic', 'engagement')),
    condition_field TEXT NOT NULL, -- 'company_size', 'industry', 'email_opened', etc.
    condition_operator TEXT NOT NULL CHECK (condition_operator IN ('equals', 'contains', 'greater_than', 'less_than', 'in', 'not_in')),
    condition_value TEXT,
    score_points INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_scoring_rules_type ON lead_scoring_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_scoring_rules_active ON lead_scoring_rules(is_active) WHERE is_active = TRUE;

-- Insérer quelques règles par défaut
INSERT INTO lead_scoring_rules (rule_name, rule_type, condition_field, condition_operator, condition_value, score_points) VALUES
('Grande entreprise', 'firmographic', 'company_size', 'in', '501-1000,1000+', 20),
('Entreprise moyenne', 'firmographic', 'company_size', 'in', '51-200,201-500', 15),
('Email ouvert', 'engagement', 'email_opened', 'equals', 'true', 10),
('Lien cliqué', 'engagement', 'link_clicked', 'equals', 'true', 15),
('Visite site web', 'behavioral', 'website_visited', 'equals', 'true', 5),
('Téléchargement ressource', 'behavioral', 'resource_downloaded', 'equals', 'true', 20),
('Demande de démo', 'behavioral', 'demo_requested', 'equals', 'true', 30)
ON CONFLICT DO NOTHING;


-- ================================================
-- VUES UTILES POUR PERFORMANCES
-- ================================================

-- Vue: Stats commercial
CREATE OR REPLACE VIEW sales_rep_stats AS
SELECT 
    sr.id as sales_rep_id,
    sr.user_id,
    sr.first_name,
    sr.last_name,
    sr.territory,
    COUNT(DISTINCT l.id) as total_leads,
    COUNT(DISTINCT CASE WHEN l.lead_status = 'qualified' THEN l.id END) as qualified_leads,
    COUNT(DISTINCT d.id) as total_deals,
    COUNT(DISTINCT CASE WHEN d.status = 'won' THEN d.id END) as won_deals,
    COUNT(DISTINCT CASE WHEN d.status = 'lost' THEN d.id END) as lost_deals,
    COALESCE(SUM(CASE WHEN d.status = 'won' THEN d.value ELSE 0 END), 0) as total_revenue,
    COALESCE(SUM(CASE WHEN d.status = 'won' THEN d.commission_amount ELSE 0 END), 0) as total_commission,
    COALESCE(AVG(CASE WHEN d.status = 'won' THEN d.value END), 0) as avg_deal_size,
    CASE 
        WHEN COUNT(DISTINCT l.id) > 0 
        THEN ROUND((COUNT(DISTINCT CASE WHEN d.status = 'won' THEN d.id END)::NUMERIC / COUNT(DISTINCT l.id)::NUMERIC * 100), 2)
        ELSE 0 
    END as conversion_rate
FROM sales_representatives sr
LEFT JOIN leads l ON l.sales_rep_id = sr.id
LEFT JOIN deals d ON d.sales_rep_id = sr.id
GROUP BY sr.id, sr.user_id, sr.first_name, sr.last_name, sr.territory;


-- Vue: Pipeline commercial
CREATE OR REPLACE VIEW sales_pipeline AS
SELECT 
    sr.id as sales_rep_id,
    d.stage,
    COUNT(d.id) as deals_count,
    COALESCE(SUM(d.value), 0) as total_value,
    COALESCE(AVG(d.value), 0) as avg_value,
    COALESCE(AVG(d.probability), 0) as avg_probability
FROM sales_representatives sr
LEFT JOIN deals d ON d.sales_rep_id = sr.id AND d.status = 'open'
GROUP BY sr.id, d.stage;


-- Vue: Activités du jour
CREATE OR REPLACE VIEW today_activities AS
SELECT 
    sa.*,
    sr.first_name || ' ' || sr.last_name as sales_rep_name,
    l.contact_name as lead_name,
    d.title as deal_title
FROM sales_activities sa
JOIN sales_representatives sr ON sr.id = sa.sales_rep_id
LEFT JOIN leads l ON l.id = sa.lead_id
LEFT JOIN deals d ON d.id = sa.deal_id
WHERE DATE(sa.scheduled_at) = CURRENT_DATE
ORDER BY sa.scheduled_at;


-- ================================================
-- FONCTIONS UTILES
-- ================================================

-- Fonction: Calculer le score d'un lead
CREATE OR REPLACE FUNCTION calculate_lead_score(p_lead_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_score INTEGER := 0;
    v_lead RECORD;
    v_rule RECORD;
BEGIN
    SELECT * FROM leads WHERE id = p_lead_id INTO v_lead;
    
    IF v_lead IS NULL THEN
        RETURN 0;
    END IF;
    
    -- Appliquer les règles de scoring
    FOR v_rule IN SELECT * FROM lead_scoring_rules WHERE is_active = TRUE ORDER BY priority DESC LOOP
        -- Logique simplifiée - à adapter selon vos besoins
        IF v_rule.condition_field = 'company_size' AND v_rule.condition_operator = 'in' THEN
            IF v_lead.company_size = ANY(string_to_array(v_rule.condition_value, ',')) THEN
                v_score := v_score + v_rule.score_points;
            END IF;
        END IF;
    END LOOP;
    
    -- Limiter le score entre 0 et 100
    v_score := GREATEST(0, LEAST(100, v_score));
    
    -- Mettre à jour le score dans la table leads
    UPDATE leads SET score = v_score WHERE id = p_lead_id;
    
    RETURN v_score;
END;
$$ LANGUAGE plpgsql;


-- Fonction: Créer objectifs mensuels automatiques
CREATE OR REPLACE FUNCTION create_monthly_targets()
RETURNS VOID AS $$
DECLARE
    v_rep RECORD;
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    v_start_date := DATE_TRUNC('month', CURRENT_DATE)::DATE;
    v_end_date := (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE;
    
    FOR v_rep IN SELECT * FROM sales_representatives WHERE is_active = TRUE LOOP
        INSERT INTO sales_targets (
            sales_rep_id, 
            period_type, 
            period_start, 
            period_end,
            deals_target,
            revenue_target,
            calls_target,
            meetings_target
        ) VALUES (
            v_rep.id,
            'monthly',
            v_start_date,
            v_end_date,
            v_rep.target_monthly_deals,
            v_rep.target_monthly_revenue,
            v_rep.target_monthly_calls,
            v_rep.target_monthly_meetings
        )
        ON CONFLICT (sales_rep_id, period_type, period_start) DO NOTHING;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- ================================================
-- COMMENTAIRES & DOCUMENTATION
-- ================================================

COMMENT ON TABLE sales_representatives IS 'Commerciaux de la plateforme';
COMMENT ON TABLE deals IS 'Opportunités de vente (deals/opportunités)';
COMMENT ON TABLE sales_activities IS 'Activités commerciales (appels, emails, meetings, etc.)';
COMMENT ON TABLE sales_targets IS 'Objectifs mensuels/trimestriels des commerciaux';
COMMENT ON TABLE sales_commissions IS 'Commissions gagnées par les commerciaux';
COMMENT ON TABLE sales_teams IS 'Équipes de vente';
COMMENT ON TABLE lead_scoring_rules IS 'Règles de scoring automatique des leads';

-- ================================================
-- FIN DU SCRIPT
-- ================================================
-- Exécuter ce script dans l'ordre
-- Vérifier les erreurs avant de continuer
-- ================================================
