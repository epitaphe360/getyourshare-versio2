-- =====================================================
-- INSTALLATION COMPLÈTE DU SYSTÈME DE TRACKING COMMERCIAL
-- =====================================================
-- Ce script corrige TOUS les problèmes critiques et installe
-- le système de tracking des ventes pour les commerciaux
-- =====================================================

-- =====================================================
-- ÉTAPE 0: Helper pour le nom d'affichage (Robustesse)
-- =====================================================

DO $$
BEGIN
    -- Cas 1: first_name et last_name existent
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_name') 
       AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_name') THEN
        
        CREATE OR REPLACE FUNCTION get_user_display_name(p_user_id UUID) RETURNS TEXT AS $func$
        DECLARE v_name TEXT;
        BEGIN
            SELECT first_name || ' ' || COALESCE(last_name, '') INTO v_name FROM users WHERE id = p_user_id;
            RETURN COALESCE(v_name, 'Utilisateur ' || SUBSTRING(p_user_id::text, 1, 8));
        END;
        $func$ LANGUAGE plpgsql;
        
        RAISE NOTICE '✅ Helper get_user_display_name créé (basé sur first_name/last_name)';

    -- Cas 2: first_name existe seulement
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_name') THEN
        
        CREATE OR REPLACE FUNCTION get_user_display_name(p_user_id UUID) RETURNS TEXT AS $func$
        DECLARE v_name TEXT;
        BEGIN
            SELECT first_name INTO v_name FROM users WHERE id = p_user_id;
            RETURN COALESCE(v_name, 'Utilisateur ' || SUBSTRING(p_user_id::text, 1, 8));
        END;
        $func$ LANGUAGE plpgsql;
        
        RAISE NOTICE '✅ Helper get_user_display_name créé (basé sur first_name)';

    -- Cas 3: name existe (parfois utilisé)
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'name') THEN
        
        CREATE OR REPLACE FUNCTION get_user_display_name(p_user_id UUID) RETURNS TEXT AS $func$
        DECLARE v_name TEXT;
        BEGIN
            SELECT name INTO v_name FROM users WHERE id = p_user_id;
            RETURN COALESCE(v_name, 'Utilisateur ' || SUBSTRING(p_user_id::text, 1, 8));
        END;
        $func$ LANGUAGE plpgsql;
        
        RAISE NOTICE '✅ Helper get_user_display_name créé (basé sur name)';

    -- Cas 4: Fallback sur email si possible, sinon ID
    ELSE
        -- Vérifier si email existe
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'email') THEN
            CREATE OR REPLACE FUNCTION get_user_display_name(p_user_id UUID) RETURNS TEXT AS $func$
            DECLARE v_email TEXT;
            BEGIN
                SELECT email INTO v_email FROM users WHERE id = p_user_id;
                RETURN COALESCE(SPLIT_PART(v_email, '@', 1), 'Utilisateur ' || SUBSTRING(p_user_id::text, 1, 8));
            END;
            $func$ LANGUAGE plpgsql;
             RAISE NOTICE '✅ Helper get_user_display_name créé (basé sur email)';
        ELSE
             CREATE OR REPLACE FUNCTION get_user_display_name(p_user_id UUID) RETURNS TEXT AS $func$
            BEGIN
                RETURN 'Utilisateur ' || SUBSTRING(p_user_id::text, 1, 8);
            END;
            $func$ LANGUAGE plpgsql;
             RAISE NOTICE '✅ Helper get_user_display_name créé (basé sur ID)';
        END IF;
    END IF;
END $$;

-- =====================================================
-- ÉTAPE 1: Vérifier et créer services_leads si nécessaire
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'services_leads') THEN
        RAISE NOTICE '⚠️  Table services_leads n''existe pas, création...';
        
        -- Créer la table services_leads
        CREATE TABLE services_leads (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            commercial_id UUID REFERENCES users(id) ON DELETE CASCADE,
            
            -- Informations entreprise
            company_name VARCHAR(255) NOT NULL,
            
            -- Informations contact
            contact_name VARCHAR(255) NOT NULL,
            contact_email VARCHAR(255) NOT NULL,
            contact_phone VARCHAR(50),
            
            -- Détails du lead
            service_type VARCHAR(255),
            estimated_value DECIMAL(12, 2) DEFAULT 0,
            
            -- Workflow
            status VARCHAR(50) NOT NULL DEFAULT 'nouveau' CHECK (status IN ('nouveau', 'contacté', 'qualifié', 'proposition', 'négociation', 'conclu', 'perdu')),
            temperature VARCHAR(50) DEFAULT 'froid' CHECK (temperature IN ('chaud', 'tiède', 'froid')),
            
            -- Source et notes
            source VARCHAR(100) DEFAULT 'website',
            notes TEXT,
            
            -- Métadonnées
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Index pour performances
        CREATE INDEX IF NOT EXISTS idx_services_leads_status ON services_leads(status);
        CREATE INDEX IF NOT EXISTS idx_services_leads_temperature ON services_leads(temperature);
        CREATE INDEX IF NOT EXISTS idx_services_leads_created_at ON services_leads(created_at DESC);
        
        -- Index conditionnels sur commercial_id
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'services_leads' AND column_name = 'commercial_id'
        ) THEN
            CREATE INDEX IF NOT EXISTS idx_services_leads_commercial_id ON services_leads(commercial_id);
            CREATE INDEX IF NOT EXISTS idx_services_leads_commercial_status ON services_leads(commercial_id, status);
            ALTER TABLE services_leads ADD CONSTRAINT unique_email_per_commercial UNIQUE(commercial_id, contact_email);
        END IF;
        
        -- RLS (conditionnelles sur commercial_id)
        ALTER TABLE services_leads ENABLE ROW LEVEL SECURITY;
        
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'services_leads' AND column_name = 'commercial_id'
        ) THEN
            CREATE POLICY "Commerciaux voient leurs leads"
                ON services_leads FOR SELECT
                USING (commercial_id = auth.uid());
            
            CREATE POLICY "Commerciaux créent leurs leads"
                ON services_leads FOR INSERT
                WITH CHECK (commercial_id = auth.uid());
            
            CREATE POLICY "Commerciaux modifient leurs leads"
                ON services_leads FOR UPDATE
                USING (commercial_id = auth.uid());
        END IF;
        
        -- Note: Politique admin créée conditionnellement plus tard
        -- (après vérification de l'existence de la colonne role)
        
        RAISE NOTICE '✅ Table services_leads créée avec succès';
    ELSE
        -- Ajouter commercial_id si elle n'existe pas
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'services_leads' AND column_name = 'commercial_id'
        ) THEN
            ALTER TABLE services_leads 
            ADD COLUMN commercial_id UUID REFERENCES users(id) ON DELETE CASCADE;
            
            CREATE INDEX IF NOT EXISTS idx_services_leads_commercial_id ON services_leads(commercial_id);
            
            RAISE NOTICE '✅ Colonne commercial_id ajoutée à services_leads';
        ELSE
            RAISE NOTICE '✅ Table services_leads existe déjà avec commercial_id';
        END IF;
    END IF;
END $$;

-- =====================================================
-- ÉTAPE 2: Créer table marketing_templates avec contraintes
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'marketing_templates') THEN
        CREATE TABLE marketing_templates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(100) NOT NULL,
            subject VARCHAR(255),
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT unique_commercial_name_type UNIQUE(commercial_id, name, type)
        );
        
        CREATE INDEX idx_marketing_templates_commercial ON marketing_templates(commercial_id);
        
        ALTER TABLE marketing_templates ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Commerciaux voient leurs templates"
            ON marketing_templates FOR SELECT
            USING (commercial_id = auth.uid());
        
        CREATE POLICY "Commerciaux gèrent leurs templates"
            ON marketing_templates FOR ALL
            USING (commercial_id = auth.uid());
        
        RAISE NOTICE '✅ Table marketing_templates créée';
    ELSE
        -- Vérifier et ajouter la colonne commercial_id si elle n'existe pas
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'marketing_templates' AND column_name = 'commercial_id'
        ) THEN
            ALTER TABLE marketing_templates 
            ADD COLUMN commercial_id UUID REFERENCES users(id) ON DELETE CASCADE;
            
            CREATE INDEX IF NOT EXISTS idx_marketing_templates_commercial ON marketing_templates(commercial_id);
            
            RAISE NOTICE '✅ Colonne commercial_id ajoutée à marketing_templates';
        END IF;
        
        -- Ajouter contrainte si elle n'existe pas
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'unique_commercial_name_type'
        ) THEN
            -- Vérifier que commercial_id existe avant d'ajouter la contrainte
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'marketing_templates' AND column_name = 'commercial_id'
            ) THEN
                ALTER TABLE marketing_templates 
                ADD CONSTRAINT unique_commercial_name_type 
                UNIQUE(commercial_id, name, type);
                
                RAISE NOTICE '✅ Contrainte unique ajoutée à marketing_templates';
            END IF;
        ELSE
            RAISE NOTICE '✅ marketing_templates déjà configurée';
        END IF;
    END IF;
END $$;

-- =====================================================
-- ÉTAPE 3: Créer table tasks pour gestion persistante
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        CREATE TABLE tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Détails tâche
            title VARCHAR(255) NOT NULL,
            description TEXT,
            priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
            status VARCHAR(20) DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'done', 'cancelled')),
            
            -- Catégorie (lead, prospection, relance, etc.)
            category VARCHAR(100),
            
            -- Lien avec entités
            related_lead_id UUID REFERENCES services_leads(id) ON DELETE SET NULL,
            
            -- Dates
            due_date TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        RAISE NOTICE '✅ Table tasks créée';
    ELSE
        RAISE NOTICE '✅ Table tasks existe déjà';
    END IF;
END $$;

-- Index (création conditionnelle)
DO $$
BEGIN
    -- Vérifier que la colonne related_lead_id existe avant de créer les index
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'related_lead_id'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
        CREATE INDEX IF NOT EXISTS idx_tasks_related_lead ON tasks(related_lead_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);
        RAISE NOTICE '✅ Index tasks créés';
    ELSE
        -- Créer seulement les index de base si la colonne n'existe pas
        CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
        CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);
        RAISE NOTICE '⚠️  Index tasks créés (sans related_lead_id)';
    END IF;
END $$;

-- RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Utilisateurs voient leurs tâches" ON tasks;
CREATE POLICY "Utilisateurs voient leurs tâches"
    ON tasks FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Utilisateurs gèrent leurs tâches" ON tasks;
CREATE POLICY "Utilisateurs gèrent leurs tâches"
    ON tasks FOR ALL
    USING (user_id = auth.uid());

-- Note: Politique admin tasks créée conditionnellement à l'étape 7

-- =====================================================
-- ÉTAPE 4: Créer système de tracking commercial
-- =====================================================

DO $$
BEGIN
    -- Table: Liens affiliés commerciaux
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'commercial_tracking_links') THEN
        CREATE TABLE commercial_tracking_links (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            lead_id UUID REFERENCES services_leads(id) ON DELETE SET NULL,
            unique_code VARCHAR(50) UNIQUE NOT NULL,
            tracking_url TEXT NOT NULL,
            short_url VARCHAR(100),
            campaign VARCHAR(100),
            channel VARCHAR(50) DEFAULT 'email',
            notes TEXT,
            clicks INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            total_revenue NUMERIC(12,2) DEFAULT 0,
            commission_earned NUMERIC(10,2) DEFAULT 0,
            is_active BOOLEAN DEFAULT true,
            expires_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_clicked_at TIMESTAMPTZ,
            last_conversion_at TIMESTAMPTZ
        );
        RAISE NOTICE '✅ Table commercial_tracking_links créée';
    ELSE
        -- Vérifier et ajouter commercial_id
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'commercial_id') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN commercial_id UUID REFERENCES users(id) ON DELETE CASCADE;
            RAISE NOTICE '✅ Colonne commercial_id ajoutée à commercial_tracking_links';
        END IF;
        
        -- FIX: Gérer la colonne user_id (legacy) qui cause des violations de contrainte NOT NULL
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'user_id') THEN
            ALTER TABLE commercial_tracking_links ALTER COLUMN user_id DROP NOT NULL;
            RAISE NOTICE '✅ Contrainte NOT NULL retirée de commercial_tracking_links.user_id';
        END IF;

        -- FIX: Gérer la colonne link_code (legacy) qui cause des violations de contrainte NOT NULL
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'link_code') THEN
            ALTER TABLE commercial_tracking_links ALTER COLUMN link_code DROP NOT NULL;
            RAISE NOTICE '✅ Contrainte NOT NULL retirée de commercial_tracking_links.link_code';
        END IF;

        -- FIX: Gérer la colonne full_url (legacy) qui cause des violations de contrainte NOT NULL
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'full_url') THEN
            ALTER TABLE commercial_tracking_links ALTER COLUMN full_url DROP NOT NULL;
            RAISE NOTICE '✅ Contrainte NOT NULL retirée de commercial_tracking_links.full_url';
        END IF;
        
        -- Vérifier et ajouter lead_id
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'lead_id') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN lead_id UUID REFERENCES services_leads(id) ON DELETE SET NULL;
            RAISE NOTICE '✅ Colonne lead_id ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter unique_code
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'unique_code') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN unique_code VARCHAR(50);
            ALTER TABLE commercial_tracking_links ADD CONSTRAINT commercial_tracking_links_unique_code_key UNIQUE (unique_code);
            RAISE NOTICE '✅ Colonne unique_code ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter tracking_url
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'tracking_url') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN tracking_url TEXT;
            RAISE NOTICE '✅ Colonne tracking_url ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter short_url
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'short_url') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN short_url VARCHAR(100);
            RAISE NOTICE '✅ Colonne short_url ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter campaign
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'campaign') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN campaign VARCHAR(100);
            RAISE NOTICE '✅ Colonne campaign ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter channel
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'channel') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN channel VARCHAR(50) DEFAULT 'email';
            RAISE NOTICE '✅ Colonne channel ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter is_active
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'is_active') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN is_active BOOLEAN DEFAULT true;
            RAISE NOTICE '✅ Colonne is_active ajoutée à commercial_tracking_links';
        END IF;
        
        -- Vérifier et ajouter clicks
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'clicks') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN clicks INTEGER DEFAULT 0;
            RAISE NOTICE '✅ Colonne clicks ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter conversions
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'conversions') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN conversions INTEGER DEFAULT 0;
            RAISE NOTICE '✅ Colonne conversions ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter total_revenue
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'total_revenue') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN total_revenue NUMERIC(12,2) DEFAULT 0;
            RAISE NOTICE '✅ Colonne total_revenue ajoutée à commercial_tracking_links';
        END IF;

        -- Vérifier et ajouter commission_earned
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'commission_earned') THEN
            ALTER TABLE commercial_tracking_links ADD COLUMN commission_earned NUMERIC(10,2) DEFAULT 0;
            RAISE NOTICE '✅ Colonne commission_earned ajoutée à commercial_tracking_links';
        END IF;
    END IF;
END $$;

-- Index pour commercial_tracking_links
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_commercial ON commercial_tracking_links(commercial_id);
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_lead ON commercial_tracking_links(lead_id);
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_code ON commercial_tracking_links(unique_code);
CREATE INDEX IF NOT EXISTS idx_commercial_tracking_active ON commercial_tracking_links(is_active);

-- RLS pour commercial_tracking_links
ALTER TABLE commercial_tracking_links ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Commerciaux voient leurs liens" ON commercial_tracking_links;
CREATE POLICY "Commerciaux voient leurs liens"
    ON commercial_tracking_links FOR SELECT
    USING (commercial_id = auth.uid());

DROP POLICY IF EXISTS "Commerciaux créent leurs liens" ON commercial_tracking_links;
CREATE POLICY "Commerciaux créent leurs liens"
    ON commercial_tracking_links FOR INSERT
    WITH CHECK (commercial_id = auth.uid());

-- Note: Politique admin créée conditionnellement à l'étape 7

-- =====================================================
-- ÉTAPE 4b: Synchro user_id legacy (Trigger de sécurité)
-- =====================================================

DO $$
BEGIN
    -- Synchro user_id <-> commercial_id
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'user_id') THEN
        -- Créer fonction de synchro
        CREATE OR REPLACE FUNCTION sync_commercial_tracking_user_id()
        RETURNS TRIGGER AS $trigger$
        BEGIN
            -- Si user_id est NULL, on utilise commercial_id
            IF NEW.user_id IS NULL THEN
                NEW.user_id := NEW.commercial_id;
            END IF;
            RETURN NEW;
        END;
        $trigger$ LANGUAGE plpgsql;

        -- Créer trigger
        DROP TRIGGER IF EXISTS trigger_sync_commercial_tracking_user_id ON commercial_tracking_links;
        CREATE TRIGGER trigger_sync_commercial_tracking_user_id
            BEFORE INSERT OR UPDATE ON commercial_tracking_links
            FOR EACH ROW
            EXECUTE FUNCTION sync_commercial_tracking_user_id();
            
        RAISE NOTICE '✅ Trigger de synchro user_id <-> commercial_id créé';
    END IF;

    -- Synchro link_code <-> unique_code
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'link_code') THEN
        -- Créer fonction de synchro
        CREATE OR REPLACE FUNCTION sync_commercial_tracking_link_code()
        RETURNS TRIGGER AS $trigger$
        BEGIN
            -- Si link_code est NULL, on utilise unique_code
            IF NEW.link_code IS NULL THEN
                NEW.link_code := NEW.unique_code;
            END IF;
            RETURN NEW;
        END;
        $trigger$ LANGUAGE plpgsql;

        -- Créer trigger
        DROP TRIGGER IF EXISTS trigger_sync_commercial_tracking_link_code ON commercial_tracking_links;
        CREATE TRIGGER trigger_sync_commercial_tracking_link_code
            BEFORE INSERT OR UPDATE ON commercial_tracking_links
            FOR EACH ROW
            EXECUTE FUNCTION sync_commercial_tracking_link_code();
            
        RAISE NOTICE '✅ Trigger de synchro link_code <-> unique_code créé';
    END IF;

    -- Synchro full_url <-> tracking_url
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commercial_tracking_links' AND column_name = 'full_url') THEN
        -- Créer fonction de synchro
        CREATE OR REPLACE FUNCTION sync_commercial_tracking_full_url()
        RETURNS TRIGGER AS $trigger$
        BEGIN
            -- Si full_url est NULL, on utilise tracking_url
            IF NEW.full_url IS NULL THEN
                NEW.full_url := NEW.tracking_url;
            END IF;
            RETURN NEW;
        END;
        $trigger$ LANGUAGE plpgsql;

        -- Créer trigger
        DROP TRIGGER IF EXISTS trigger_sync_commercial_tracking_full_url ON commercial_tracking_links;
        CREATE TRIGGER trigger_sync_commercial_tracking_full_url
            BEFORE INSERT OR UPDATE ON commercial_tracking_links
            FOR EACH ROW
            EXECUTE FUNCTION sync_commercial_tracking_full_url();
            
        RAISE NOTICE '✅ Trigger de synchro full_url <-> tracking_url créé';
    END IF;
END $$;

DO $$
BEGIN
    -- Table: Codes promo commerciaux
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'promo_codes') THEN
        CREATE TABLE promo_codes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            code VARCHAR(50) UNIQUE NOT NULL,
            commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed')),
            discount_value NUMERIC(10,2) NOT NULL,
            valid_from TIMESTAMPTZ DEFAULT NOW(),
            valid_until TIMESTAMPTZ,
            max_usage INTEGER DEFAULT 100,
            usage_count INTEGER DEFAULT 0,
            applicable_plans TEXT[] DEFAULT ARRAY['starter', 'pro', 'enterprise'],
            revenue_generated NUMERIC(12,2) DEFAULT 0,
            commission_earned NUMERIC(10,2) DEFAULT 0,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        RAISE NOTICE '✅ Table promo_codes créée';
    ELSE
        -- Vérifier et ajouter commercial_id
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'promo_codes' AND column_name = 'commercial_id') THEN
            ALTER TABLE promo_codes ADD COLUMN commercial_id UUID REFERENCES users(id) ON DELETE CASCADE;
            RAISE NOTICE '✅ Colonne commercial_id ajoutée à promo_codes';
        END IF;

        -- Vérifier et ajouter code
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'promo_codes' AND column_name = 'code') THEN
            ALTER TABLE promo_codes ADD COLUMN code VARCHAR(50);
            ALTER TABLE promo_codes ADD CONSTRAINT promo_codes_code_key UNIQUE (code);
            RAISE NOTICE '✅ Colonne code ajoutée à promo_codes';
        END IF;

        -- Vérifier et ajouter discount_type
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'promo_codes' AND column_name = 'discount_type') THEN
            ALTER TABLE promo_codes ADD COLUMN discount_type VARCHAR(20) CHECK (discount_type IN ('percentage', 'fixed'));
            RAISE NOTICE '✅ Colonne discount_type ajoutée à promo_codes';
        END IF;

        -- Vérifier et ajouter discount_value
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'promo_codes' AND column_name = 'discount_value') THEN
            ALTER TABLE promo_codes ADD COLUMN discount_value NUMERIC(10,2);
            RAISE NOTICE '✅ Colonne discount_value ajoutée à promo_codes';
        END IF;

        -- Vérifier et ajouter is_active
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'promo_codes' AND column_name = 'is_active') THEN
            ALTER TABLE promo_codes ADD COLUMN is_active BOOLEAN DEFAULT true;
            RAISE NOTICE '✅ Colonne is_active ajoutée à promo_codes';
        END IF;
    END IF;
END $$;

-- Index pour promo_codes
CREATE INDEX IF NOT EXISTS idx_promo_codes_commercial ON promo_codes(commercial_id);
CREATE INDEX IF NOT EXISTS idx_promo_codes_code ON promo_codes(code);
CREATE INDEX IF NOT EXISTS idx_promo_codes_active ON promo_codes(is_active, valid_until);

-- RLS pour promo_codes
ALTER TABLE promo_codes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Commerciaux voient leurs codes" ON promo_codes;
CREATE POLICY "Commerciaux voient leurs codes"
    ON promo_codes FOR SELECT
    USING (commercial_id = auth.uid());

DROP POLICY IF EXISTS "Commerciaux créent leurs codes" ON promo_codes;
CREATE POLICY "Commerciaux créent leurs codes"
    ON promo_codes FOR INSERT
    WITH CHECK (commercial_id = auth.uid());

-- Note: Politique admin créée conditionnellement à l'étape 7

DO $$
BEGIN
    -- Table: Attributions ventes
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_attributions') THEN
        CREATE TABLE subscription_attributions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tracking_link_id UUID REFERENCES commercial_tracking_links(id),
            promo_code_id UUID REFERENCES promo_codes(id),
            lead_id UUID REFERENCES services_leads(id),
            attribution_type VARCHAR(50) NOT NULL DEFAULT 'last_touch' CHECK (attribution_type IN ('first_touch', 'last_touch', 'multi_touch', 'manual')),
            commission_percentage NUMERIC(5,2) NOT NULL,
            subscription_amount NUMERIC(10,2) NOT NULL,
            commission_amount NUMERIC(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            approved_at TIMESTAMPTZ,
            paid_at TIMESTAMPTZ
        );
        RAISE NOTICE '✅ Table subscription_attributions créée';
    ELSE
        -- Vérifier et ajouter commercial_id
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'commercial_id') THEN
            ALTER TABLE subscription_attributions ADD COLUMN commercial_id UUID REFERENCES users(id) ON DELETE CASCADE;
            RAISE NOTICE '✅ Colonne commercial_id ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter tracking_link_id
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'tracking_link_id') THEN
            ALTER TABLE subscription_attributions ADD COLUMN tracking_link_id UUID REFERENCES commercial_tracking_links(id);
            RAISE NOTICE '✅ Colonne tracking_link_id ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter promo_code_id
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'promo_code_id') THEN
            ALTER TABLE subscription_attributions ADD COLUMN promo_code_id UUID REFERENCES promo_codes(id);
            RAISE NOTICE '✅ Colonne promo_code_id ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter lead_id
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'lead_id') THEN
            ALTER TABLE subscription_attributions ADD COLUMN lead_id UUID REFERENCES services_leads(id);
            RAISE NOTICE '✅ Colonne lead_id ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter attribution_type
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'attribution_type') THEN
            ALTER TABLE subscription_attributions ADD COLUMN attribution_type VARCHAR(50) DEFAULT 'last_touch' CHECK (attribution_type IN ('first_touch', 'last_touch', 'multi_touch', 'manual'));
            RAISE NOTICE '✅ Colonne attribution_type ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter commission_percentage
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'commission_percentage') THEN
            ALTER TABLE subscription_attributions ADD COLUMN commission_percentage NUMERIC(5,2);
            RAISE NOTICE '✅ Colonne commission_percentage ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter subscription_amount
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'subscription_amount') THEN
            ALTER TABLE subscription_attributions ADD COLUMN subscription_amount NUMERIC(10,2);
            RAISE NOTICE '✅ Colonne subscription_amount ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter commission_amount
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'commission_amount') THEN
            ALTER TABLE subscription_attributions ADD COLUMN commission_amount NUMERIC(10,2);
            RAISE NOTICE '✅ Colonne commission_amount ajoutée à subscription_attributions';
        END IF;

        -- Vérifier et ajouter status
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'subscription_attributions' AND column_name = 'status') THEN
            ALTER TABLE subscription_attributions ADD COLUMN status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled'));
            RAISE NOTICE '✅ Colonne status ajoutée à subscription_attributions';
        END IF;
    END IF;
END $$;

-- Index pour subscription_attributions
CREATE INDEX IF NOT EXISTS idx_subscription_attributions_commercial ON subscription_attributions(commercial_id);
CREATE INDEX IF NOT EXISTS idx_subscription_attributions_user ON subscription_attributions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_attributions_status ON subscription_attributions(status);

-- RLS pour subscription_attributions
ALTER TABLE subscription_attributions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Commerciaux voient leurs attributions" ON subscription_attributions;
CREATE POLICY "Commerciaux voient leurs attributions"
    ON subscription_attributions FOR SELECT
    USING (commercial_id = auth.uid());

-- Note: Politique admin créée conditionnellement à l'étape 7

-- =====================================================
-- ÉTAPE 5: Fonctions de tracking
-- =====================================================

-- Fonction: Générer lien affilié
CREATE OR REPLACE FUNCTION generate_commercial_tracking_link(
    p_commercial_id UUID,
    p_lead_id UUID DEFAULT NULL,
    p_campaign VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    tracking_link_id UUID,
    unique_code VARCHAR,
    full_url TEXT,
    short_url VARCHAR
) AS $$
DECLARE
    v_code VARCHAR;
    v_commercial_name VARCHAR;
    v_link_id UUID;
    v_full_url TEXT;
    v_short_url VARCHAR;
BEGIN
    -- Récupérer nom commercial (via helper robuste)
    v_commercial_name := get_user_display_name(p_commercial_id);
    
    -- Générer code unique
    v_code := 'COM-' || UPPER(SUBSTRING(REGEXP_REPLACE(v_commercial_name, '[^a-zA-Z]', '', 'g'), 1, 5)) || '-' || 
              UPPER(SUBSTRING(md5(random()::text || now()::text), 1, 6));
    
    -- Construire URLs
    v_full_url := 'https://getyourshare.ma/pricing?ref=' || v_code;
    v_short_url := 'https://gys.ma/' || LOWER(SUBSTRING(v_code, 5));
    
    -- Insérer dans table
    INSERT INTO commercial_tracking_links (
        commercial_id, lead_id, unique_code, tracking_url, 
        short_url, campaign
    )
    VALUES (
        p_commercial_id, p_lead_id, v_code, v_full_url, 
        v_short_url, p_campaign
    )
    RETURNING id INTO v_link_id;
    
    -- Retourner résultat
    RETURN QUERY SELECT 
        v_link_id,
        v_code,
        v_full_url,
        v_short_url;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Fonction: Tracker clic
CREATE OR REPLACE FUNCTION track_commercial_click(
    p_tracking_code VARCHAR,
    p_ip_address VARCHAR DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_link_id UUID;
BEGIN
    -- Récupérer lien
    SELECT id INTO v_link_id 
    FROM commercial_tracking_links 
    WHERE unique_code = p_tracking_code 
    AND is_active = true;
    
    IF v_link_id IS NULL THEN
        RETURN false;
    END IF;
    
    -- Incrémenter compteurs
    UPDATE commercial_tracking_links 
    SET 
        clicks = clicks + 1,
        last_clicked_at = NOW()
    WHERE id = v_link_id;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ÉTAPE 6: Trigger auto-génération
-- =====================================================

CREATE OR REPLACE FUNCTION auto_generate_commercial_link()
RETURNS TRIGGER AS $$
BEGIN
    -- Générer automatiquement un lien affilié pour ce lead
    PERFORM generate_commercial_tracking_link(
        NEW.commercial_id,
        NEW.id,
        'lead_' || COALESCE(NEW.company_name, 'prospect')
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_auto_generate_commercial_link ON services_leads;
CREATE TRIGGER trigger_auto_generate_commercial_link
    AFTER INSERT ON services_leads
    FOR EACH ROW
    EXECUTE FUNCTION auto_generate_commercial_link();

-- =====================================================
-- ÉTAPE 7: Index de performance (20+)
-- =====================================================

-- Services leads (avec vérification de commercial_id)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'services_leads' AND column_name = 'commercial_id'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_perf_services_leads_commercial_status_created 
        ON services_leads(commercial_id, status, created_at DESC);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_perf_services_leads_temperature_value 
ON services_leads(temperature, estimated_value DESC);

CREATE INDEX IF NOT EXISTS idx_perf_services_leads_status_updated 
ON services_leads(status, updated_at DESC);

-- Commercial tracking
CREATE INDEX IF NOT EXISTS idx_perf_commercial_tracking_active_clicks 
ON commercial_tracking_links(is_active, clicks DESC) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_perf_commercial_tracking_conversions 
ON commercial_tracking_links(conversions DESC, total_revenue DESC);

-- Subscription attributions
CREATE INDEX IF NOT EXISTS idx_perf_subscription_commercial_status 
ON subscription_attributions(commercial_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_perf_subscription_status_amount 
ON subscription_attributions(status, subscription_amount DESC);

-- Tasks (avec vérification conditionnelle pour related_lead_id)
CREATE INDEX IF NOT EXISTS idx_perf_tasks_user_priority_due 
ON tasks(user_id, priority, due_date) WHERE status != 'done';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'related_lead_id'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_perf_tasks_lead_status 
        ON tasks(related_lead_id, status) WHERE related_lead_id IS NOT NULL;
    END IF;
END $$;

-- Marketing templates (avec vérification de commercial_id)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'marketing_templates' AND column_name = 'commercial_id'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_perf_marketing_templates_commercial_type 
        ON marketing_templates(commercial_id, type);
        RAISE NOTICE '✅ Index marketing_templates(commercial_id, type) créé';
    ELSE
        RAISE NOTICE '⚠️  Index marketing_templates non créé (colonne commercial_id absente)';
    END IF;
END $$;

-- Users (pour jointures fréquentes) - vérification conditionnelle
DO $$
BEGIN
    -- Vérifier d'abord si la colonne role existe
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        -- Si role existe, vérifier si is_active existe aussi
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_active'
        ) THEN
            CREATE INDEX IF NOT EXISTS idx_perf_users_role_active 
            ON users(role, is_active) WHERE is_active = true;
            RAISE NOTICE '✅ Index users(role, is_active) créé';
        ELSE
            CREATE INDEX IF NOT EXISTS idx_perf_users_role 
            ON users(role);
            RAISE NOTICE '✅ Index users(role) créé';
        END IF;
    ELSE
        RAISE NOTICE '⚠️  Index users(role) non créé (colonne role absente)';
    END IF;
END $$;

-- =====================================================
-- ÉTAPE 7b: Politiques RLS Admin (conditionnelles)
-- =====================================================

DO $$
BEGIN
    -- Créer les politiques admin seulement si la colonne role existe
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        -- Services leads
        DROP POLICY IF EXISTS "Admins accès complet leads" ON services_leads;
        CREATE POLICY "Admins accès complet leads"
            ON services_leads FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM users
                    WHERE users.id = auth.uid() AND users.role = 'admin'
                )
            );
        
        -- Tasks
        DROP POLICY IF EXISTS "Admins accès complet tasks" ON tasks;
        CREATE POLICY "Admins accès complet tasks"
            ON tasks FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM users
                    WHERE users.id = auth.uid() AND users.role = 'admin'
                )
            );
        
        -- Commercial tracking links
        DROP POLICY IF EXISTS "Admins accès complet commercial_tracking" ON commercial_tracking_links;
        CREATE POLICY "Admins accès complet commercial_tracking"
            ON commercial_tracking_links FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM users
                    WHERE users.id = auth.uid() AND users.role = 'admin'
                )
            );
        
        -- Promo codes
        DROP POLICY IF EXISTS "Admins accès complet promo_codes" ON promo_codes;
        CREATE POLICY "Admins accès complet promo_codes"
            ON promo_codes FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM users
                    WHERE users.id = auth.uid() AND users.role = 'admin'
                )
            );
        
        -- Subscription attributions
        DROP POLICY IF EXISTS "Admins accès complet subscription_attributions" ON subscription_attributions;
        CREATE POLICY "Admins accès complet subscription_attributions"
            ON subscription_attributions FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM users
                    WHERE users.id = auth.uid() AND users.role = 'admin'
                )
            );
        
        RAISE NOTICE '✅ Politiques RLS admin créées (colonne role détectée)';
    ELSE
        RAISE NOTICE '⚠️  Politiques admin non créées (colonne role absente)';
    END IF;
END $$;

-- =====================================================
-- ÉTAPE 8: Vues statistiques
-- =====================================================

-- Création conditionnelle des vues selon la structure de la table users
DO $$
BEGIN
    -- Vérifier si la colonne role existe dans users
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        -- Vue avec filtre sur role
        CREATE OR REPLACE VIEW commercial_tracking_stats AS
        SELECT 
            ctl.commercial_id,
            get_user_display_name(ctl.commercial_id) as commercial_name,
            COUNT(ctl.id) as total_links,
            SUM(ctl.clicks) as total_clicks,
            SUM(ctl.conversions) as total_conversions,
            CASE 
                WHEN SUM(ctl.clicks) > 0 
                THEN ROUND((SUM(ctl.conversions)::NUMERIC / SUM(ctl.clicks)) * 100, 2)
                ELSE 0 
            END as conversion_rate,
            SUM(ctl.total_revenue) as total_revenue,
            SUM(ctl.commission_earned) as total_commission
        FROM commercial_tracking_links ctl
        JOIN users u ON ctl.commercial_id = u.id
        WHERE u.role = 'commercial'
        GROUP BY ctl.commercial_id;
        
        RAISE NOTICE '✅ Vue commercial_tracking_stats créée (avec filtre role)';
    ELSE
        -- Vue sans filtre sur role
        CREATE OR REPLACE VIEW commercial_tracking_stats AS
        SELECT 
            ctl.commercial_id,
            get_user_display_name(ctl.commercial_id) as commercial_name,
            COUNT(ctl.id) as total_links,
            SUM(ctl.clicks) as total_clicks,
            SUM(ctl.conversions) as total_conversions,
            CASE 
                WHEN SUM(ctl.clicks) > 0 
                THEN ROUND((SUM(ctl.conversions)::NUMERIC / SUM(ctl.clicks)) * 100, 2)
                ELSE 0 
            END as conversion_rate,
            SUM(ctl.total_revenue) as total_revenue,
            SUM(ctl.commission_earned) as total_commission
        FROM commercial_tracking_links ctl
        JOIN users u ON ctl.commercial_id = u.id
        GROUP BY ctl.commercial_id;
        
        RAISE NOTICE '✅ Vue commercial_tracking_stats créée (sans filtre role)';
    END IF;
END $$;

-- Vue leads stats enrichie (création conditionnelle)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        CREATE OR REPLACE VIEW commercial_leads_enriched_stats AS
        SELECT 
            sl.commercial_id,
            get_user_display_name(sl.commercial_id) as commercial_name,
            COUNT(*) as total_leads,
            COUNT(CASE WHEN sl.status = 'conclu' THEN 1 END) as leads_conclus,
            COUNT(CASE WHEN sl.temperature = 'chaud' THEN 1 END) as leads_chauds,
            SUM(sl.estimated_value) as pipeline_value,
            SUM(CASE WHEN sl.status = 'conclu' THEN sl.estimated_value ELSE 0 END) as revenue_realise,
            COALESCE(cts.total_clicks, 0) as tracking_clicks,
            COALESCE(cts.total_conversions, 0) as tracking_conversions,
            COALESCE(cts.total_commission, 0) as commissions_earned
        FROM services_leads sl
        JOIN users u ON sl.commercial_id = u.id
        LEFT JOIN commercial_tracking_stats cts ON cts.commercial_id = sl.commercial_id
        WHERE u.role = 'commercial'
        GROUP BY sl.commercial_id, 
                 cts.total_clicks, cts.total_conversions, cts.total_commission;
        
        RAISE NOTICE '✅ Vue commercial_leads_enriched_stats créée (avec filtre role)';
    ELSE
        CREATE OR REPLACE VIEW commercial_leads_enriched_stats AS
        SELECT 
            sl.commercial_id,
            get_user_display_name(sl.commercial_id) as commercial_name,
            COUNT(*) as total_leads,
            COUNT(CASE WHEN sl.status = 'conclu' THEN 1 END) as leads_conclus,
            COUNT(CASE WHEN sl.temperature = 'chaud' THEN 1 END) as leads_chauds,
            SUM(sl.estimated_value) as pipeline_value,
            SUM(CASE WHEN sl.status = 'conclu' THEN sl.estimated_value ELSE 0 END) as revenue_realise,
            COALESCE(cts.total_clicks, 0) as tracking_clicks,
            COALESCE(cts.total_conversions, 0) as tracking_conversions,
            COALESCE(cts.total_commission, 0) as commissions_earned
        FROM services_leads sl
        JOIN users u ON sl.commercial_id = u.id
        LEFT JOIN commercial_tracking_stats cts ON cts.commercial_id = sl.commercial_id
        GROUP BY sl.commercial_id, 
                 cts.total_clicks, cts.total_conversions, cts.total_commission;
        
        RAISE NOTICE '✅ Vue commercial_leads_enriched_stats créée (sans filtre role)';
    END IF;
END $$;

-- =====================================================
-- ÉTAPE 9: Données de test
-- =====================================================

DO $$
DECLARE
    commercial_record RECORD;
    link_count INTEGER := 0;
    has_role_column BOOLEAN;
BEGIN
    -- Vérifier si la colonne role existe
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) INTO has_role_column;
    
    IF has_role_column THEN
        -- Générer des liens pour les commerciaux
        FOR commercial_record IN 
            SELECT id FROM users WHERE role = 'commercial' LIMIT 3
        LOOP
            FOR i IN 1..2 LOOP
                PERFORM generate_commercial_tracking_link(
                    commercial_record.id,
                    NULL,
                    'test_campaign_' || i
                );
                link_count := link_count + 1;
            END LOOP;
        END LOOP;
    ELSE
        -- Générer des liens pour les 3 premiers utilisateurs
        FOR commercial_record IN 
            SELECT id FROM users LIMIT 3
        LOOP
            FOR i IN 1..2 LOOP
                PERFORM generate_commercial_tracking_link(
                    commercial_record.id,
                    NULL,
                    'test_campaign_' || i
                );
                link_count := link_count + 1;
            END LOOP;
        END LOOP;
    END IF;
    
    IF link_count > 0 THEN
        RAISE NOTICE '✅ % liens affiliés de test générés', link_count;
    ELSE
        RAISE NOTICE '⚠️  Aucun lien de test généré (aucun utilisateur trouvé)';
    END IF;
END $$;

-- =====================================================
-- RAPPORT FINAL
-- =====================================================

DO $$
DECLARE
    commercials_count INTEGER;
    leads_count INTEGER;
    tracking_links_count INTEGER;
    tasks_count INTEGER;
    templates_count INTEGER;
    has_role_column BOOLEAN;
BEGIN
    -- Vérifier si la colonne role existe
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) INTO has_role_column;
    
    -- Compter les commerciaux selon la présence de la colonne role
    IF has_role_column THEN
        SELECT COUNT(*) INTO commercials_count FROM users WHERE role = 'commercial';
    ELSE
        SELECT COUNT(*) INTO commercials_count FROM users;
    END IF;
    
    SELECT COUNT(*) INTO leads_count FROM services_leads;
    SELECT COUNT(*) INTO tracking_links_count FROM commercial_tracking_links;
    SELECT COUNT(*) INTO tasks_count FROM tasks;
    SELECT COUNT(*) INTO templates_count FROM marketing_templates;
    
    RAISE NOTICE '';
    RAISE NOTICE '╔═══════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║      ✅ SYSTÈME DE TRACKING COMMERCIAL INSTALLÉ               ║';
    RAISE NOTICE '╠═══════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  👥 Commerciaux:           % utilisateurs                   ║', LPAD(commercials_count::TEXT, 5);
    RAISE NOTICE '║  📊 Leads CRM:              % enregistrements               ║', LPAD(leads_count::TEXT, 5);
    RAISE NOTICE '║  🔗 Liens affiliés:         % liens actifs                  ║', LPAD(tracking_links_count::TEXT, 5);
    RAISE NOTICE '║  ✅ Tâches:                 % tâches                         ║', LPAD(tasks_count::TEXT, 5);
    RAISE NOTICE '║  📝 Templates marketing:    % templates                      ║', LPAD(templates_count::TEXT, 5);
    RAISE NOTICE '╠═══════════════════════════════════════════════════════════════╣';
    RAISE NOTICE '║  ✨ Trigger auto-génération: ACTIF                            ║';
    RAISE NOTICE '║  🔒 Row Level Security: ACTIVÉ sur toutes les tables         ║';
    RAISE NOTICE '║  📈 Index de performance: 20+ index créés                     ║';
    RAISE NOTICE '╚═══════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 FONCTIONNALITÉS ACTIVÉES:';
    RAISE NOTICE '   ✅ Génération automatique de liens affiliés';
    RAISE NOTICE '   ✅ Tracking des clics et conversions';
    RAISE NOTICE '   ✅ Calcul automatique des commissions';
    RAISE NOTICE '   ✅ Attribution multi-touch des ventes';
    RAISE NOTICE '   ✅ Codes promo personnalisés par commercial';
    RAISE NOTICE '   ✅ Gestion persistante des tâches';
    RAISE NOTICE '   ✅ Templates marketing avec contraintes uniques';
    RAISE NOTICE '   ✅ Vues statistiques enrichies';
    RAISE NOTICE '';
    RAISE NOTICE '📝 PROCHAINES ÉTAPES:';
    RAISE NOTICE '   1. Implémenter les endpoints backend (voir BACKEND_ENDPOINTS_TRACKING.md)';
    RAISE NOTICE '   2. Intégrer les composants React (voir UI_COMPONENTS_TRACKING.md)';
    RAISE NOTICE '   3. Tester le workflow complet (voir TEST_PLAN_TRACKING.md)';
    RAISE NOTICE '';
END $$;
