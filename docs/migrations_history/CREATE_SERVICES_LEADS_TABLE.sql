-- =====================================================
-- CRÉATION TABLE SERVICES_LEADS
-- Table principale pour les leads du CRM commercial
-- =====================================================

-- Supprimer la table si elle existe (pour recréation propre)
DROP TABLE IF EXISTS services_leads CASCADE;

-- Créer la table services_leads
CREATE TABLE services_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commercial_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Index sur l'email pour éviter les doublons
    CONSTRAINT unique_email_per_commercial UNIQUE(commercial_id, contact_email)
);

-- =====================================================
-- INDEX POUR PERFORMANCES
-- =====================================================

CREATE INDEX idx_services_leads_commercial_id ON services_leads(commercial_id);
CREATE INDEX idx_services_leads_status ON services_leads(status);
CREATE INDEX idx_services_leads_temperature ON services_leads(temperature);
CREATE INDEX idx_services_leads_created_at ON services_leads(created_at DESC);
CREATE INDEX idx_services_leads_estimated_value ON services_leads(estimated_value DESC);
CREATE INDEX idx_services_leads_contact_email ON services_leads(contact_email);
CREATE INDEX idx_services_leads_company_name ON services_leads(company_name);

-- Index composite pour requêtes fréquentes
CREATE INDEX idx_services_leads_commercial_status ON services_leads(commercial_id, status);
CREATE INDEX idx_services_leads_commercial_created ON services_leads(commercial_id, created_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE services_leads ENABLE ROW LEVEL SECURITY;

-- Les commerciaux ne voient que leurs propres leads
CREATE POLICY "Commerciaux voient leurs leads"
    ON services_leads FOR SELECT
    USING (commercial_id = auth.uid());

-- Les commerciaux peuvent créer des leads
CREATE POLICY "Commerciaux créent leurs leads"
    ON services_leads FOR INSERT
    WITH CHECK (commercial_id = auth.uid());

-- Les commerciaux peuvent modifier leurs propres leads
CREATE POLICY "Commerciaux modifient leurs leads"
    ON services_leads FOR UPDATE
    USING (commercial_id = auth.uid());

-- Les commerciaux peuvent supprimer leurs propres leads
CREATE POLICY "Commerciaux suppriment leurs leads"
    ON services_leads FOR DELETE
    USING (commercial_id = auth.uid());

-- Les admins ont accès complet
CREATE POLICY "Admins accès complet leads"
    ON services_leads FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role = 'admin'
        )
    );

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_services_leads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour updated_at
DROP TRIGGER IF EXISTS update_services_leads_updated_at_trigger ON services_leads;
CREATE TRIGGER update_services_leads_updated_at_trigger
    BEFORE UPDATE ON services_leads
    FOR EACH ROW
    EXECUTE FUNCTION update_services_leads_updated_at();

-- =====================================================
-- VUES UTILES
-- =====================================================

-- Vue pour les statistiques par commercial
CREATE OR REPLACE VIEW commercial_leads_stats AS
SELECT 
    commercial_id,
    COUNT(*) as total_leads,
    COUNT(CASE WHEN status = 'nouveau' THEN 1 END) as leads_nouveaux,
    COUNT(CASE WHEN status = 'contacté' THEN 1 END) as leads_contactes,
    COUNT(CASE WHEN status = 'qualifié' THEN 1 END) as leads_qualifies,
    COUNT(CASE WHEN status = 'proposition' THEN 1 END) as leads_proposition,
    COUNT(CASE WHEN status = 'négociation' THEN 1 END) as leads_negociation,
    COUNT(CASE WHEN status = 'conclu' THEN 1 END) as leads_conclus,
    COUNT(CASE WHEN status = 'perdu' THEN 1 END) as leads_perdus,
    COUNT(CASE WHEN temperature = 'chaud' THEN 1 END) as leads_chauds,
    COUNT(CASE WHEN temperature = 'tiède' THEN 1 END) as leads_tiedes,
    COUNT(CASE WHEN temperature = 'froid' THEN 1 END) as leads_froids,
    SUM(estimated_value) as valeur_totale,
    SUM(CASE WHEN status = 'conclu' THEN estimated_value ELSE 0 END) as revenu_realise,
    SUM(CASE WHEN status IN ('qualifié', 'proposition', 'négociation') THEN estimated_value ELSE 0 END) as pipeline_value,
    AVG(estimated_value) as valeur_moyenne,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as leads_ce_mois
FROM services_leads
GROUP BY commercial_id;

-- Vue pour les leads récents (30 derniers jours)
CREATE OR REPLACE VIEW recent_leads AS
SELECT 
    sl.*,
    u.first_name || ' ' || u.last_name as commercial_name,
    u.email as commercial_email
FROM services_leads sl
JOIN users u ON sl.commercial_id = u.id
WHERE sl.created_at >= NOW() - INTERVAL '30 days'
ORDER BY sl.created_at DESC;

-- Vue pour les leads chauds en pipeline
CREATE OR REPLACE VIEW hot_leads_pipeline AS
SELECT 
    sl.*,
    u.first_name || ' ' || u.last_name as commercial_name
FROM services_leads sl
JOIN users u ON sl.commercial_id = u.id
WHERE sl.temperature = 'chaud'
AND sl.status IN ('qualifié', 'proposition', 'négociation')
ORDER BY sl.estimated_value DESC;

-- =====================================================
-- FONCTIONS UTILES
-- =====================================================

-- Fonction pour obtenir le pipeline d'un commercial
CREATE OR REPLACE FUNCTION get_commercial_pipeline(commercial_uuid UUID)
RETURNS TABLE (
    stage VARCHAR,
    count BIGINT,
    total_value NUMERIC,
    percentage NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH pipeline_data AS (
        SELECT 
            status,
            COUNT(*) as cnt,
            SUM(estimated_value) as val
        FROM services_leads
        WHERE commercial_id = commercial_uuid
        AND status IN ('nouveau', 'contacté', 'qualifié', 'proposition', 'négociation', 'conclu')
        GROUP BY status
    ),
    total_leads AS (
        SELECT COUNT(*) as total FROM services_leads WHERE commercial_id = commercial_uuid
    )
    SELECT 
        pd.status::VARCHAR as stage,
        pd.cnt as count,
        pd.val as total_value,
        ROUND((pd.cnt::NUMERIC / NULLIF(tl.total, 0)) * 100, 2) as percentage
    FROM pipeline_data pd
    CROSS JOIN total_leads tl
    ORDER BY 
        CASE pd.status
            WHEN 'nouveau' THEN 1
            WHEN 'contacté' THEN 2
            WHEN 'qualifié' THEN 3
            WHEN 'proposition' THEN 4
            WHEN 'négociation' THEN 5
            WHEN 'conclu' THEN 6
        END;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir le taux de conversion
CREATE OR REPLACE FUNCTION get_conversion_rate(commercial_uuid UUID)
RETURNS NUMERIC AS $$
DECLARE
    total_leads INTEGER;
    converted_leads INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_leads
    FROM services_leads
    WHERE commercial_id = commercial_uuid;
    
    SELECT COUNT(*) INTO converted_leads
    FROM services_leads
    WHERE commercial_id = commercial_uuid
    AND status = 'conclu';
    
    IF total_leads = 0 THEN
        RETURN 0;
    END IF;
    
    RETURN ROUND((converted_leads::NUMERIC / total_leads) * 100, 2);
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir le lead le plus chaud
CREATE OR REPLACE FUNCTION get_hot_lead(commercial_uuid UUID)
RETURNS TABLE (
    lead_id UUID,
    company_name VARCHAR,
    contact_name VARCHAR,
    contact_email VARCHAR,
    contact_phone VARCHAR,
    estimated_value NUMERIC,
    status VARCHAR,
    temperature VARCHAR,
    days_since_created INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sl.id,
        sl.company_name,
        sl.contact_name,
        sl.contact_email,
        sl.contact_phone,
        sl.estimated_value,
        sl.status,
        sl.temperature,
        EXTRACT(DAY FROM NOW() - sl.created_at)::INTEGER as days_since_created
    FROM services_leads sl
    WHERE sl.commercial_id = commercial_uuid
    AND sl.temperature = 'chaud'
    AND sl.status IN ('qualifié', 'proposition', 'négociation')
    ORDER BY sl.estimated_value DESC, sl.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- DONNÉES DE TEST
-- =====================================================

-- Insérer des leads de test (adapter les UUIDs selon votre base)
-- Récupérer d'abord un commercial de test
DO $$
DECLARE
    test_commercial_id UUID;
BEGIN
    -- Trouver un utilisateur commercial ou créer un test
    SELECT id INTO test_commercial_id
    FROM users
    WHERE role = 'commercial'
    LIMIT 1;
    
    -- Si un commercial existe, créer des leads de test
    IF test_commercial_id IS NOT NULL THEN
        INSERT INTO services_leads (commercial_id, company_name, contact_name, contact_email, contact_phone, service_type, estimated_value, status, temperature, source, notes)
        VALUES
            (test_commercial_id, 'Tech Corp', 'Jean Dupont', 'jean.dupont@techcorp.fr', '+33 6 12 34 56 78', 'Marketing Digital', 5000, 'qualifié', 'chaud', 'website', 'Client très intéressé, relancer la semaine prochaine'),
            (test_commercial_id, 'Innovation SAS', 'Marie Martin', 'marie@innovation-sas.fr', '+33 6 98 76 54 32', 'Développement Web', 8000, 'proposition', 'chaud', 'referral', 'Devis envoyé, attente de retour'),
            (test_commercial_id, 'Digital Solutions', 'Pierre Durand', 'pierre.durand@digital-solutions.com', '+33 6 11 22 33 44', 'SEO', 3000, 'contacté', 'tiède', 'cold_call', 'Premier contact positif'),
            (test_commercial_id, 'Web Agency', 'Sophie Bernard', 'sophie@webagency.fr', NULL, 'Social Media', 2500, 'nouveau', 'froid', 'linkedin', 'Lead entrant depuis LinkedIn'),
            (test_commercial_id, 'E-commerce Pro', 'Luc Petit', 'luc.petit@ecommerce-pro.fr', '+33 6 55 66 77 88', 'Publicité Facebook', 6000, 'négociation', 'chaud', 'website', 'En phase finale de négociation')
        ON CONFLICT (commercial_id, contact_email) DO NOTHING;
        
        RAISE NOTICE 'Leads de test créés pour le commercial %', test_commercial_id;
    ELSE
        RAISE NOTICE 'Aucun commercial trouvé, impossible de créer des leads de test';
    END IF;
END $$;

-- =====================================================
-- COMMENTAIRES
-- =====================================================

COMMENT ON TABLE services_leads IS 'Table principale des leads pour le système CRM commercial';
COMMENT ON COLUMN services_leads.commercial_id IS 'ID du commercial propriétaire du lead';
COMMENT ON COLUMN services_leads.company_name IS 'Nom de l''entreprise du lead';
COMMENT ON COLUMN services_leads.contact_name IS 'Nom du contact principal';
COMMENT ON COLUMN services_leads.contact_email IS 'Email du contact (unique par commercial)';
COMMENT ON COLUMN services_leads.status IS 'Statut du lead dans le pipeline (nouveau, contacté, qualifié, proposition, négociation, conclu, perdu)';
COMMENT ON COLUMN services_leads.temperature IS 'Température du lead (chaud, tiède, froid)';
COMMENT ON COLUMN services_leads.estimated_value IS 'Valeur estimée du deal en euros';
COMMENT ON COLUMN services_leads.source IS 'Source d''acquisition du lead (website, referral, cold_call, linkedin, etc.)';

-- =====================================================
-- VÉRIFICATION
-- =====================================================

-- Vérifier que tout fonctionne
SELECT 'Table services_leads créée avec succès!' as message;
SELECT 'Nombre de leads:' as info, COUNT(*) as count FROM services_leads;
SELECT 'Nombre de politiques RLS:' as info, COUNT(*) as count FROM pg_policies WHERE tablename = 'services_leads';
SELECT 'Nombre d''index:' as info, COUNT(*) as count FROM pg_indexes WHERE tablename = 'services_leads';

-- =====================================================
-- FIN DU SCRIPT
-- =====================================================
