-- ============================================
-- SYSTÈME DE GESTION DES SERVICES (LEADS)
-- Tables : services, leads, service_recharges, service_extras
-- ============================================

-- Créer la table categories si elle n'existe pas
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table : services
-- Stocke les services proposés par les marchands avec système de dépôt pour leads
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Info service
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    images TEXT[], -- Array d'URLs d'images
    categorie_id UUID REFERENCES categories(id),
    localisation VARCHAR(255),
    conditions TEXT,
    
    -- Marchand (référence vers users qui ont role='merchant')
    marchand_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Système financier LEADS
    depot_initial DECIMAL(10, 2) NOT NULL DEFAULT 0, -- Dépôt de garantie
    depot_actuel DECIMAL(10, 2) NOT NULL DEFAULT 0,  -- Solde restant
    prix_par_lead DECIMAL(10, 2) NOT NULL,           -- Prix par demande client
    commission_rate DECIMAL(5, 2) DEFAULT 20.00,     -- % de commission
    
    -- Calculs automatiques
    leads_possibles INTEGER GENERATED ALWAYS AS (FLOOR(depot_actuel / NULLIF(prix_par_lead, 0))) STORED,
    leads_recus INTEGER DEFAULT 0,                    -- Compteur de leads reçus
    
    -- Stats
    taux_conversion DECIMAL(5, 2) DEFAULT 0,          -- % de leads convertis
    
    -- Formulaire personnalisé (JSON)
    formulaire_champs JSONB DEFAULT '[]'::jsonb,
    
    -- Statuts
    statut VARCHAR(50) DEFAULT 'actif' CHECK (statut IN ('actif', 'inactif', 'epuise', 'expire')),
    
    -- Dates
    date_debut TIMESTAMP DEFAULT NOW(),
    date_expiration TIMESTAMP,
    date_alerte_envoyee TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table : leads
-- Stocke les demandes des clients (prospects) pour les services
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relations
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    marchand_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Info client
    nom_client VARCHAR(255) NOT NULL,
    email_client VARCHAR(255) NOT NULL,
    telephone_client VARCHAR(50) NOT NULL,
    donnees_formulaire JSONB DEFAULT '{}'::jsonb, -- Champs personnalisés
    
    -- Gestion financière
    cout_lead DECIMAL(10, 2) NOT NULL, -- Montant déduit du dépôt
    
    -- Statut du lead
    statut VARCHAR(50) DEFAULT 'nouveau' CHECK (statut IN ('nouveau', 'en_cours', 'converti', 'perdu', 'spam')),
    
    -- Dates
    date_reception TIMESTAMP DEFAULT NOW(),
    date_conversion TIMESTAMP,
    date_perdu TIMESTAMP,
    
    -- Suivi marchand
    notes_marchand TEXT,
    note_qualite INTEGER CHECK (note_qualite BETWEEN 1 AND 5),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table : service_recharges
-- Historique des recharges de dépôt par les marchands
CREATE TABLE IF NOT EXISTS service_recharges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    marchand_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    montant DECIMAL(10, 2) NOT NULL,
    ancien_solde DECIMAL(10, 2) NOT NULL,
    nouveau_solde DECIMAL(10, 2) NOT NULL,
    
    leads_ajoutes INTEGER, -- Nombre de leads supplémentaires achetés
    
    -- Paiement
    methode_paiement VARCHAR(50),
    transaction_id VARCHAR(255),
    statut_paiement VARCHAR(50) DEFAULT 'en_attente' CHECK (statut_paiement IN ('en_attente', 'reussi', 'echoue')),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table : service_extras
-- Extras/Boosts marketing achetés pour un service
CREATE TABLE IF NOT EXISTS service_extras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    marchand_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    type VARCHAR(100) NOT NULL, -- 'mise_en_avant', 'badge_hot', 'push_notification', 'top_categorie', etc.
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    prix DECIMAL(10, 2) NOT NULL,
    
    date_debut TIMESTAMP DEFAULT NOW(),
    date_fin TIMESTAMP,
    actif BOOLEAN DEFAULT true,
    
    -- Paiement
    transaction_id VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEX pour optimiser les requêtes
-- ============================================

CREATE INDEX idx_services_marchand ON services(marchand_id);
CREATE INDEX idx_services_statut ON services(statut);
CREATE INDEX idx_services_categorie ON services(categorie_id);
CREATE INDEX idx_services_depot_actuel ON services(depot_actuel);

CREATE INDEX idx_leads_service ON leads(service_id);
CREATE INDEX idx_leads_marchand ON leads(marchand_id);
CREATE INDEX idx_leads_statut ON leads(statut);
CREATE INDEX idx_leads_email ON leads(email_client);
CREATE INDEX idx_leads_date ON leads(date_reception);

CREATE INDEX idx_recharges_service ON service_recharges(service_id);
CREATE INDEX idx_recharges_marchand ON service_recharges(marchand_id);

CREATE INDEX idx_extras_service ON service_extras(service_id);
CREATE INDEX idx_extras_actif ON service_extras(actif);

-- ============================================
-- TRIGGERS pour automatisations
-- ============================================

-- Trigger : Mise à jour du updated_at automatique
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger : Déduire du dépôt quand un lead est créé
CREATE OR REPLACE FUNCTION deduct_lead_cost()
RETURNS TRIGGER AS $$
BEGIN
    -- Déduire le coût du lead du dépôt du service
    UPDATE services
    SET depot_actuel = depot_actuel - NEW.cout_lead,
        leads_recus = leads_recus + 1,
        updated_at = NOW()
    WHERE id = NEW.service_id;
    
    -- Vérifier si le service est épuisé
    UPDATE services
    SET statut = 'epuise'
    WHERE id = NEW.service_id
    AND depot_actuel <= 0;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_deduct_lead_cost AFTER INSERT ON leads
    FOR EACH ROW EXECUTE FUNCTION deduct_lead_cost();

-- Trigger : Calculer le taux de conversion automatiquement
CREATE OR REPLACE FUNCTION update_conversion_rate()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE services
    SET taux_conversion = (
        SELECT CASE 
            WHEN COUNT(*) = 0 THEN 0
            ELSE (COUNT(*) FILTER (WHERE statut = 'converti')::DECIMAL / COUNT(*)) * 100
        END
        FROM leads
        WHERE service_id = NEW.service_id
    )
    WHERE id = NEW.service_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_conversion_rate AFTER UPDATE ON leads
    FOR EACH ROW WHEN (OLD.statut IS DISTINCT FROM NEW.statut)
    EXECUTE FUNCTION update_conversion_rate();

-- Trigger : Ajouter au dépôt lors d'une recharge
CREATE OR REPLACE FUNCTION add_recharge_to_deposit()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.statut_paiement = 'reussi' THEN
        UPDATE services
        SET depot_actuel = depot_actuel + NEW.montant,
            statut = 'actif',
            updated_at = NOW()
        WHERE id = NEW.service_id;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_add_recharge AFTER INSERT OR UPDATE ON service_recharges
    FOR EACH ROW WHEN (NEW.statut_paiement = 'reussi')
    EXECUTE FUNCTION add_recharge_to_deposit();

-- ============================================
-- VUES UTILES
-- ============================================

-- Vue : Services avec infos complètes
CREATE OR REPLACE VIEW view_services_complete AS
SELECT 
    s.*,
    u.email as marchand_email,
    m.company_name as marchand_company,
    c.name as categorie_nom,
    (SELECT COUNT(*) FROM leads WHERE service_id = s.id) as total_leads,
    (SELECT COUNT(*) FROM leads WHERE service_id = s.id AND statut = 'converti') as leads_convertis,
    (SELECT COUNT(*) FROM service_extras WHERE service_id = s.id AND actif = true) as extras_actifs
FROM services s
LEFT JOIN users u ON s.marchand_id = u.id
LEFT JOIN merchants m ON m.user_id = u.id
LEFT JOIN categories c ON s.categorie_id = c.id;

-- Vue : Leads avec détails service et marchand
CREATE OR REPLACE VIEW view_leads_complete AS
SELECT 
    l.*,
    s.nom as service_nom,
    s.images as service_images,
    u.email as marchand_email,
    m.company_name as marchand_company
FROM leads l
JOIN services s ON l.service_id = s.id
JOIN users u ON l.marchand_id = u.id
LEFT JOIN merchants m ON m.user_id = u.id;

-- ============================================
-- FONCTION : Alertes automatiques solde faible
-- ============================================

CREATE OR REPLACE FUNCTION check_low_balance_alerts()
RETURNS void AS $$
BEGIN
    -- Envoyer des alertes pour les services avec solde < 20%
    UPDATE services
    SET date_alerte_envoyee = NOW()
    WHERE statut = 'actif'
    AND (depot_actuel / NULLIF(depot_initial, 0)) < 0.20
    AND (date_alerte_envoyee IS NULL OR date_alerte_envoyee < NOW() - INTERVAL '7 days');
    
    -- Vous pouvez ajouter une notification ici
END;
$$ language 'plpgsql';

-- ============================================
-- DONNÉES DE TEST (optionnel)
-- ============================================

-- Insérer des catégories de services si elles n'existent pas
INSERT INTO categories (name, description) VALUES
    ('Beauté & Bien-être', 'Services de beauté, spa, massage, coiffure'),
    ('Restauration', 'Restaurants, cafés, traiteurs'),
    ('Sport & Fitness', 'Salles de sport, coachs, activités sportives'),
    ('Loisirs', 'Divertissement, activités, événements')
ON CONFLICT (name) DO NOTHING;

COMMENT ON TABLE services IS 'Services proposés par les marchands avec système de paiement par lead';
COMMENT ON TABLE leads IS 'Demandes de clients (prospects) pour les services';
COMMENT ON TABLE service_recharges IS 'Historique des recharges de dépôt par les marchands';
COMMENT ON TABLE service_extras IS 'Extras marketing achetés pour booster un service';
