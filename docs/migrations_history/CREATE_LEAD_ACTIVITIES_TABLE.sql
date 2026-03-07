-- =====================================================
-- CRÉATION TABLE LEAD_ACTIVITIES
-- Historique des activités des leads pour le CRM
-- =====================================================

-- Table pour stocker les activités (appels, emails, réunions, notes)
CREATE TABLE IF NOT EXISTS lead_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES services_leads(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('call', 'email', 'meeting', 'note', 'update')),
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_lead_activities_lead_id ON lead_activities(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_activities_user_id ON lead_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_lead_activities_created_at ON lead_activities(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lead_activities_type ON lead_activities(type);

-- Politique RLS (Row Level Security)
ALTER TABLE lead_activities ENABLE ROW LEVEL SECURITY;

-- Les commerciaux ne voient que les activités de leurs propres leads
CREATE POLICY "Commerciaux voient leurs activités"
    ON lead_activities FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM services_leads
            WHERE services_leads.id = lead_activities.lead_id
            AND services_leads.commercial_id = auth.uid()
        )
    );

-- Les commerciaux peuvent créer des activités sur leurs leads
CREATE POLICY "Commerciaux créent leurs activités"
    ON lead_activities FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM services_leads
            WHERE services_leads.id = lead_activities.lead_id
            AND services_leads.commercial_id = auth.uid()
        )
        AND user_id = auth.uid()
    );

-- Les commerciaux peuvent modifier leurs propres activités
CREATE POLICY "Commerciaux modifient leurs activités"
    ON lead_activities FOR UPDATE
    USING (user_id = auth.uid());

-- Les commerciaux peuvent supprimer leurs propres activités
CREATE POLICY "Commerciaux suppriment leurs activités"
    ON lead_activities FOR DELETE
    USING (user_id = auth.uid());

-- Admins ont accès complet
CREATE POLICY "Admins accès complet activités"
    ON lead_activities FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.role = 'admin'
        )
    );

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_lead_activities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour updated_at
DROP TRIGGER IF EXISTS update_lead_activities_updated_at_trigger ON lead_activities;
CREATE TRIGGER update_lead_activities_updated_at_trigger
    BEFORE UPDATE ON lead_activities
    FOR EACH ROW
    EXECUTE FUNCTION update_lead_activities_updated_at();

-- Fonction pour créer une activité automatique lors de la mise à jour d'un lead
CREATE OR REPLACE FUNCTION create_lead_update_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- Si le statut a changé, créer une activité automatique
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
        VALUES (
            NEW.id,
            NEW.commercial_id,
            'update',
            'Changement de statut',
            format('Statut changé de "%s" à "%s"', OLD.status, NEW.status)
        );
    END IF;
    
    -- Si la température a changé
    IF OLD.temperature IS DISTINCT FROM NEW.temperature THEN
        INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
        VALUES (
            NEW.id,
            NEW.commercial_id,
            'update',
            'Changement de température',
            format('Température changée de "%s" à "%s"', OLD.temperature, NEW.temperature)
        );
    END IF;
    
    -- Si la valeur estimée a changé significativement (>10%)
    IF OLD.estimated_value IS NOT NULL AND NEW.estimated_value IS NOT NULL THEN
        IF ABS(OLD.estimated_value - NEW.estimated_value) > (OLD.estimated_value * 0.1) THEN
            INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
            VALUES (
                NEW.id,
                NEW.commercial_id,
                'update',
                'Modification de la valeur',
                format('Valeur estimée changée de %s€ à %s€', OLD.estimated_value, NEW.estimated_value)
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour créer automatiquement des activités lors des modifications
DROP TRIGGER IF EXISTS create_lead_update_activity_trigger ON services_leads;
CREATE TRIGGER create_lead_update_activity_trigger
    AFTER UPDATE ON services_leads
    FOR EACH ROW
    EXECUTE FUNCTION create_lead_update_activity();

-- Créer une activité automatique lors de la création d'un lead
CREATE OR REPLACE FUNCTION create_lead_creation_activity()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO lead_activities (lead_id, user_id, type, subject, description)
    VALUES (
        NEW.id,
        NEW.commercial_id,
        'note',
        'Lead créé',
        format('Nouveau lead créé : %s (%s)', NEW.company_name, NEW.contact_name)
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour créer une activité à la création du lead
DROP TRIGGER IF EXISTS create_lead_creation_activity_trigger ON services_leads;
CREATE TRIGGER create_lead_creation_activity_trigger
    AFTER INSERT ON services_leads
    FOR EACH ROW
    EXECUTE FUNCTION create_lead_creation_activity();

-- =====================================================
-- DONNÉES DE TEST
-- =====================================================

-- Insérer quelques activités de test (adapter les UUIDs selon votre base)
-- INSERT INTO lead_activities (lead_id, user_id, type, subject, description) VALUES
-- ('lead-uuid-1', 'user-uuid-1', 'call', 'Premier contact téléphonique', 'Discussion très positive, client intéressé par notre offre Premium'),
-- ('lead-uuid-1', 'user-uuid-1', 'email', 'Envoi de la proposition commerciale', 'Proposition envoyée avec devis détaillé et conditions'),
-- ('lead-uuid-1', 'user-uuid-1', 'meeting', 'Réunion de présentation', 'Présentation du produit, démo réussie, client convaincu'),
-- ('lead-uuid-1', 'user-uuid-1', 'note', 'Suivi relance', 'À recontacter la semaine prochaine pour closing');

-- =====================================================
-- VUES UTILES
-- =====================================================

-- Vue pour compter les activités par lead
CREATE OR REPLACE VIEW lead_activities_summary AS
SELECT 
    lead_id,
    COUNT(*) as total_activities,
    COUNT(CASE WHEN type = 'call' THEN 1 END) as total_calls,
    COUNT(CASE WHEN type = 'email' THEN 1 END) as total_emails,
    COUNT(CASE WHEN type = 'meeting' THEN 1 END) as total_meetings,
    COUNT(CASE WHEN type = 'note' THEN 1 END) as total_notes,
    MAX(created_at) as last_activity_date
FROM lead_activities
GROUP BY lead_id;

-- Vue pour les activités récentes (30 derniers jours)
CREATE OR REPLACE VIEW recent_lead_activities AS
SELECT 
    la.*,
    sl.company_name,
    sl.contact_name,
    sl.status as lead_status,
    u.first_name || ' ' || u.last_name as user_name
FROM lead_activities la
JOIN services_leads sl ON la.lead_id = sl.id
JOIN users u ON la.user_id = u.id
WHERE la.created_at >= NOW() - INTERVAL '30 days'
ORDER BY la.created_at DESC;

-- =====================================================
-- STATISTIQUES
-- =====================================================

-- Fonction pour obtenir les stats d'activité d'un commercial
CREATE OR REPLACE FUNCTION get_commercial_activity_stats(commercial_uuid UUID)
RETURNS TABLE (
    total_activities BIGINT,
    activities_this_week BIGINT,
    activities_this_month BIGINT,
    most_active_type VARCHAR,
    avg_activities_per_lead NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_activities,
        COUNT(CASE WHEN la.created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as activities_this_week,
        COUNT(CASE WHEN la.created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as activities_this_month,
        (
            SELECT type 
            FROM lead_activities la2
            JOIN services_leads sl2 ON la2.lead_id = sl2.id
            WHERE sl2.commercial_id = commercial_uuid
            GROUP BY type
            ORDER BY COUNT(*) DESC
            LIMIT 1
        ) as most_active_type,
        ROUND(
            COUNT(*)::NUMERIC / NULLIF(
                (SELECT COUNT(DISTINCT id) FROM services_leads WHERE commercial_id = commercial_uuid),
                0
            ),
            2
        ) as avg_activities_per_lead
    FROM lead_activities la
    JOIN services_leads sl ON la.lead_id = sl.id
    WHERE sl.commercial_id = commercial_uuid;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTAIRES
-- =====================================================

COMMENT ON TABLE lead_activities IS 'Historique des activités (appels, emails, réunions, notes) pour chaque lead du CRM';
COMMENT ON COLUMN lead_activities.type IS 'Type d''activité : call, email, meeting, note, update';
COMMENT ON COLUMN lead_activities.subject IS 'Titre/sujet de l''activité';
COMMENT ON COLUMN lead_activities.description IS 'Description détaillée de l''activité';

-- =====================================================
-- FIN DU SCRIPT
-- =====================================================
