-- ================================================
-- SCRIPT DE DIAGNOSTIC ET CORRECTION
-- Table SUBSCRIPTIONS
-- ================================================

-- 1. Vérifier si la table subscriptions existe
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        RAISE NOTICE '✓ Table subscriptions existe';
        
        -- Vérifier si la colonne plan_id existe
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'plan_id') THEN
            RAISE NOTICE '✓ Colonne plan_id existe';
        ELSE
            RAISE NOTICE '✗ Colonne plan_id MANQUANTE - AJOUT EN COURS...';
        END IF;
    ELSE
        RAISE NOTICE '✗ Table subscriptions n''existe pas encore';
    END IF;
END $$;

-- 2. OPTION A: Supprimer et recréer la table (SI VIDE OU PAS IMPORTANTE)
-- ATTENTION: Ceci supprime toutes les données!
-- Décommentez si vous voulez supprimer la table existante:
-- DROP TABLE IF EXISTS subscriptions CASCADE;

-- 3. OPTION B: Ajouter les colonnes manquantes (SI TABLE A DES DONNÉES)
-- Ajouter plan_id si manquant
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'plan_id') THEN
        -- D'abord, vérifier que subscription_plans existe
        IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'subscription_plans') THEN
            ALTER TABLE subscriptions ADD COLUMN plan_id UUID;
            
            -- Récupérer l'ID du plan Free par défaut
            UPDATE subscriptions 
            SET plan_id = (SELECT id FROM subscription_plans WHERE name = 'Free' LIMIT 1)
            WHERE plan_id IS NULL;
            
            -- Ajouter la contrainte NOT NULL après avoir rempli les valeurs
            ALTER TABLE subscriptions ALTER COLUMN plan_id SET NOT NULL;
            
            -- Ajouter la contrainte FK
            ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_plan_id_fkey 
                FOREIGN KEY (plan_id) REFERENCES subscription_plans(id);
            
            RAISE NOTICE '✓ Colonne plan_id ajoutée avec succès';
        ELSE
            RAISE EXCEPTION 'Table subscription_plans n''existe pas. Créez-la d''abord!';
        END IF;
    END IF;
END $$;

-- 4. Ajouter les autres colonnes si manquantes
DO $$
BEGIN
    -- started_at
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'started_at') THEN
        ALTER TABLE subscriptions ADD COLUMN started_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
        RAISE NOTICE '✓ Colonne started_at ajoutée';
    END IF;
    
    -- expires_at
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'expires_at') THEN
        ALTER TABLE subscriptions ADD COLUMN expires_at TIMESTAMPTZ;
        RAISE NOTICE '✓ Colonne expires_at ajoutée';
    END IF;
    
    -- trial_ends_at
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'trial_ends_at') THEN
        ALTER TABLE subscriptions ADD COLUMN trial_ends_at TIMESTAMPTZ;
        RAISE NOTICE '✓ Colonne trial_ends_at ajoutée';
    END IF;
    
    -- cancelled_at
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'cancelled_at') THEN
        ALTER TABLE subscriptions ADD COLUMN cancelled_at TIMESTAMPTZ;
        RAISE NOTICE '✓ Colonne cancelled_at ajoutée';
    END IF;
    
    -- cancellation_reason
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'cancellation_reason') THEN
        ALTER TABLE subscriptions ADD COLUMN cancellation_reason TEXT;
        RAISE NOTICE '✓ Colonne cancellation_reason ajoutée';
    END IF;
    
    -- payment_method
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'payment_method') THEN
        ALTER TABLE subscriptions ADD COLUMN payment_method TEXT;
        RAISE NOTICE '✓ Colonne payment_method ajoutée';
    END IF;
    
    -- stripe_subscription_id
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'stripe_subscription_id') THEN
        ALTER TABLE subscriptions ADD COLUMN stripe_subscription_id TEXT;
        RAISE NOTICE '✓ Colonne stripe_subscription_id ajoutée';
    END IF;
    
    -- stripe_customer_id
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'stripe_customer_id') THEN
        ALTER TABLE subscriptions ADD COLUMN stripe_customer_id TEXT;
        RAISE NOTICE '✓ Colonne stripe_customer_id ajoutée';
    END IF;
    
    -- auto_renew
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'auto_renew') THEN
        ALTER TABLE subscriptions ADD COLUMN auto_renew BOOLEAN DEFAULT TRUE;
        RAISE NOTICE '✓ Colonne auto_renew ajoutée';
    END IF;
END $$;

-- 5. Créer les index (seulement si la table existe)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        -- Index user_id
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_subscriptions_user') THEN
            CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
            RAISE NOTICE '✓ Index idx_subscriptions_user créé';
        END IF;
        
        -- Index plan_id (seulement si la colonne existe)
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'plan_id') THEN
            IF NOT EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_subscriptions_plan') THEN
                CREATE INDEX idx_subscriptions_plan ON subscriptions(plan_id);
                RAISE NOTICE '✓ Index idx_subscriptions_plan créé';
            END IF;
        END IF;
        
        -- Index status
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_subscriptions_status') THEN
            CREATE INDEX idx_subscriptions_status ON subscriptions(status);
            RAISE NOTICE '✓ Index idx_subscriptions_status créé';
        END IF;
        
        -- Index expires_at
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'expires_at') THEN
            IF NOT EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_subscriptions_expires') THEN
                CREATE INDEX idx_subscriptions_expires ON subscriptions(expires_at);
                RAISE NOTICE '✓ Index idx_subscriptions_expires créé';
            END IF;
        END IF;
        
        -- Index UNIQUE
        IF EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'subscriptions' AND column_name = 'plan_id'
        ) AND EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'subscriptions' AND column_name = 'started_at'
        ) THEN
            IF NOT EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_subscriptions_unique_user_plan_start') THEN
                CREATE UNIQUE INDEX idx_subscriptions_unique_user_plan_start 
                    ON subscriptions(user_id, plan_id, started_at);
                RAISE NOTICE '✓ Index UNIQUE idx_subscriptions_unique_user_plan_start créé';
            END IF;
        END IF;
    END IF;
END $$;

-- 6. Créer le trigger pour updated_at
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        -- Créer la fonction si elle n'existe pas
        CREATE OR REPLACE FUNCTION update_subscriptions_updated_at()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;
        
        -- Supprimer le trigger s'il existe
        DROP TRIGGER IF EXISTS subscriptions_updated_at ON subscriptions;
        
        -- Créer le trigger
        CREATE TRIGGER subscriptions_updated_at
            BEFORE UPDATE ON subscriptions
            FOR EACH ROW
            EXECUTE FUNCTION update_subscriptions_updated_at();
        
        RAISE NOTICE '✓ Trigger subscriptions_updated_at créé';
    END IF;
END $$;

-- 7. RÉSUMÉ
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'RÉSUMÉ DE LA CORRECTION';
    RAISE NOTICE '========================================';
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        SELECT COUNT(*) INTO v_count FROM subscriptions;
        RAISE NOTICE 'Table subscriptions: ✓ Existe avec % ligne(s)', v_count;
        
        -- Vérifier toutes les colonnes importantes
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'plan_id') THEN
            RAISE NOTICE 'Colonne plan_id: ✓ Présente';
        ELSE
            RAISE NOTICE 'Colonne plan_id: ✗ MANQUANTE';
        END IF;
        
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'subscriptions' AND column_name = 'started_at') THEN
            RAISE NOTICE 'Colonne started_at: ✓ Présente';
        ELSE
            RAISE NOTICE 'Colonne started_at: ✗ MANQUANTE';
        END IF;
    ELSE
        RAISE NOTICE 'Table subscriptions: ✗ N''existe pas';
        RAISE NOTICE 'Exécutez d''abord CREATE_INFLUENCER_TABLES.sql après avoir créé subscription_plans';
    END IF;
    
    RAISE NOTICE '========================================';
END $$;
