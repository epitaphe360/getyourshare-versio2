-- ============================================
-- TABLES MANQUANTES POUR COMMERCIAL DASHBOARD
-- À exécuter dans l'éditeur SQL de Supabase
-- ============================================

-- ============================================
-- 1. TABLE commercial_stats
-- Stocke les statistiques agrégées par commercial
-- ============================================
CREATE TABLE IF NOT EXISTS public.commercial_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commercial_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Métriques Leads
    total_leads INTEGER DEFAULT 0,
    new_leads INTEGER DEFAULT 0,
    qualified_leads INTEGER DEFAULT 0,
    converted_leads INTEGER DEFAULT 0,

    -- Métriques Financières
    total_revenue DECIMAL(12,2) DEFAULT 0,
    total_commission DECIMAL(12,2) DEFAULT 0,
    pipeline_value DECIMAL(12,2) DEFAULT 0,
    average_deal_size DECIMAL(12,2) DEFAULT 0,

    -- Métriques Performance
    conversion_rate DECIMAL(5,2) DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    average_sales_cycle_days INTEGER DEFAULT 0,

    -- Métriques Activité
    calls_made INTEGER DEFAULT 0,
    emails_sent INTEGER DEFAULT 0,
    meetings_held INTEGER DEFAULT 0,
    proposals_sent INTEGER DEFAULT 0,

    -- Métriques Tracking Links
    tracking_links_created INTEGER DEFAULT 0,
    tracking_links_clicks INTEGER DEFAULT 0,
    tracking_links_conversions INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT unique_commercial_period UNIQUE(commercial_id, period_start, period_end)
);

-- Index pour commercial_stats
CREATE INDEX IF NOT EXISTS idx_commercial_stats_commercial_id ON public.commercial_stats(commercial_id);
CREATE INDEX IF NOT EXISTS idx_commercial_stats_period ON public.commercial_stats(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_commercial_stats_created_at ON public.commercial_stats(created_at DESC);

-- Commentaires
COMMENT ON TABLE public.commercial_stats IS 'Statistiques agrégées par commercial pour le dashboard';
COMMENT ON COLUMN public.commercial_stats.conversion_rate IS 'Taux de conversion leads -> deals (%)';
COMMENT ON COLUMN public.commercial_stats.win_rate IS 'Taux de gain deals conclus / deals totaux (%)';


-- ============================================
-- 2. TABLE commercial_templates
-- Stocke les templates de communication marketing
-- ============================================
CREATE TABLE IF NOT EXISTS public.commercial_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'email', 'whatsapp', 'linkedin', 'sms', 'script_appel',
        'proposition', 'relance', 'remerciement', 'negociation'
    )),
    content TEXT NOT NULL,
    variables TEXT[], -- Variables dynamiques ex: ['{nom}', '{entreprise}']

    -- Métadonnées
    language TEXT DEFAULT 'fr',
    is_premium BOOLEAN DEFAULT false,
    tier TEXT CHECK (tier IN ('starter', 'pro', 'enterprise', 'all')) DEFAULT 'all',

    -- Usage
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,

    -- Personnalisation
    tone TEXT, -- formel, amical, professionnel
    industry TEXT, -- B2B, B2C, E-commerce, etc.

    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Index pour commercial_templates
CREATE INDEX IF NOT EXISTS idx_commercial_templates_category ON public.commercial_templates(category);
CREATE INDEX IF NOT EXISTS idx_commercial_templates_tier ON public.commercial_templates(tier);
CREATE INDEX IF NOT EXISTS idx_commercial_templates_is_active ON public.commercial_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_commercial_templates_language ON public.commercial_templates(language);

-- Commentaires
COMMENT ON TABLE public.commercial_templates IS 'Templates de communication pour le Commercial Dashboard';
COMMENT ON COLUMN public.commercial_templates.variables IS 'Variables dynamiques à remplacer dans le template';
COMMENT ON COLUMN public.commercial_templates.tier IS 'Niveau d''abonnement requis pour accéder au template';


-- ============================================
-- 3. DONNÉES DE TEST pour commercial_templates
-- ============================================
INSERT INTO public.commercial_templates (title, category, content, variables, language, tier, tone, industry) VALUES
-- STARTER Templates (3)
('Premier Contact Prospect', 'email',
'Bonjour {nom},

Je me permets de vous contacter concernant {entreprise}. Nous aidons les entreprises comme la vôtre à augmenter leurs ventes grâce au marketing d''influence.

Seriez-vous disponible pour un échange de 15 minutes cette semaine ?

Cordialement,
{commercial_nom}',
ARRAY['{nom}', '{entreprise}', '{commercial_nom}'], 'fr', 'starter', 'professionnel', 'B2B'),

('Message WhatsApp Introduction', 'whatsapp',
'Bonjour {nom} 👋

Je suis {commercial_nom} de GetYourShare. Nous avons une solution innovante pour augmenter vos ventes avec des influenceurs qualifiés.

Puis-je vous envoyer une présentation rapide ? 📊',
ARRAY['{nom}', '{commercial_nom}'], 'fr', 'starter', 'amical', 'B2C'),

('Relance Prospect', 'email',
'Bonjour {nom},

Je reviens vers vous suite à mon message du {date}. Avez-vous eu l''occasion d''y réfléchir ?

Je reste à votre disposition.

Bien cordialement,
{commercial_nom}',
ARRAY['{nom}', '{date}', '{commercial_nom}'], 'fr', 'starter', 'professionnel', 'B2B'),

-- PRO Templates (15)
('Proposition Commerciale Détaillée', 'proposition',
'PROPOSITION COMMERCIALE

Client: {entreprise}
Contact: {nom}
Date: {date}

🎯 OBJECTIFS:
- Augmenter les ventes de {pourcentage_objectif}%
- Acquérir {nombre_clients} nouveaux clients
- ROI visé: {roi_objectif}

💡 SOLUTION PROPOSÉE:
Collaboration avec {nombre_influenceurs} influenceurs ciblés dans votre secteur {industrie}.

📊 BUDGET:
Investissement: {budget}€/mois
Commission: {commission}%
Durée: {duree} mois

✅ GARANTIES:
- Influenceurs vérifiés
- Tracking en temps réel
- Support dédié

Restons en contact,
{commercial_nom}',
ARRAY['{entreprise}', '{nom}', '{date}', '{pourcentage_objectif}', '{nombre_clients}', '{roi_objectif}', '{nombre_influenceurs}', '{industrie}', '{budget}', '{commission}', '{duree}', '{commercial_nom}'],
'fr', 'pro', 'professionnel', 'B2B'),

('Script Appel Téléphonique', 'script_appel',
'📞 SCRIPT APPEL DÉCOUVERTE

1. ACCROCHE (15 sec)
Bonjour {nom}, je suis {commercial_nom} de GetYourShare. Je vous appelle car nous travaillons avec des entreprises comme {concurrent} dans le {industrie}.

2. QUALIFICATION (2 min)
- Utilisez-vous déjà le marketing d''influence ?
- Quels sont vos objectifs de croissance ?
- Quel budget allouez-vous actuellement ?

3. PRÉSENTATION RAPIDE (2 min)
Nous connectons les entreprises avec les meilleurs influenceurs. Résultats moyens: +{pourcentage}% de ventes.

4. NEXT STEP
Puis-je vous envoyer une démo de 15 min cette semaine ?',
ARRAY['{nom}', '{commercial_nom}', '{concurrent}', '{industrie}', '{pourcentage}'],
'fr', 'pro', 'professionnel', 'B2B'),

('Email de Remerciement Post-Démo', 'remerciement',
'Bonjour {nom},

Merci pour cet échange enrichissant ce matin ! 🙏

Comme convenu, voici le résumé de notre discussion:
✅ {point_1}
✅ {point_2}
✅ {point_3}

📎 Je vous joins la proposition détaillée.

Je reste disponible pour toute question.

Belle journée,
{commercial_nom}',
ARRAY['{nom}', '{point_1}', '{point_2}', '{point_3}', '{commercial_nom}'],
'fr', 'pro', 'amical', 'B2B'),

-- ENTERPRISE Templates (avec IA)
('Négociation Avancée', 'negociation',
'STRATÉGIE DE NÉGOCIATION

Client: {entreprise} ({secteur})
Décideur: {nom} - {poste}
Budget initial: {budget_initial}€
Budget objectif: {budget_objectif}€

🎯 ARGUMENTS CLÉS:
1. ROI prouvé: {roi}% chez {client_reference}
2. Économie vs pub traditionnelle: {economie}%
3. Flexibilité: engagement sur {duree} mois

💎 VALEUR AJOUTÉE:
- Accès plateforme IA
- Automation complète
- Support dédié 24/7
- Formation équipe

🤝 CONCESSIONS POSSIBLES:
- {concession_1}
- {concession_2}

⏰ URGENCE:
Offre spéciale valable jusqu''au {date_limite}

Closing prévu: {date_closing}
Probabilité: {probabilite}%',
ARRAY['{entreprise}', '{secteur}', '{nom}', '{poste}', '{budget_initial}', '{budget_objectif}', '{roi}', '{client_reference}', '{economie}', '{duree}', '{concession_1}', '{concession_2}', '{date_limite}', '{date_closing}', '{probabilite}'],
'fr', 'enterprise', 'professionnel', 'B2B');

-- Autres templates PRO (on en ajoute quelques-uns de plus pour atteindre 15)
INSERT INTO public.commercial_templates (title, category, content, variables, language, tier, tone) VALUES
('LinkedIn Connection Request', 'linkedin',
'Bonjour {nom},

J''ai remarqué votre expertise en {domaine}. Je connecte les marques avec des influenceurs pour booster leurs ventes.

Connectons-nous ? 🤝',
ARRAY['{nom}', '{domaine}'], 'fr', 'pro', 'professionnel'),

('SMS Rappel RDV', 'sms',
'Bonjour {nom}, rendez-vous confirmé demain à {heure} pour parler de {sujet}. À demain ! {commercial_nom}',
ARRAY['{nom}', '{heure}', '{sujet}', '{commercial_nom}'], 'fr', 'pro', 'amical');


-- ============================================
-- 4. FONCTION TRIGGER pour mettre à jour updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_commercial_stats_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_commercial_stats_timestamp
    BEFORE UPDATE ON public.commercial_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_commercial_stats_updated_at();

CREATE TRIGGER trigger_update_commercial_templates_timestamp
    BEFORE UPDATE ON public.commercial_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_commercial_stats_updated_at();


-- ============================================
-- 5. RLS (Row Level Security) - OPTIONNEL
-- ============================================
-- Décommenter si vous utilisez RLS

-- ALTER TABLE public.commercial_stats ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.commercial_templates ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Commercials can view their own stats" ON public.commercial_stats
--     FOR SELECT USING (auth.uid() = commercial_id OR EXISTS (
--         SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin'
--     ));

-- CREATE POLICY "Everyone can view active templates for their tier" ON public.commercial_templates
--     FOR SELECT USING (is_active = true);


-- ============================================
-- FIN DU SCRIPT
-- ============================================

-- Vérification
SELECT 'Tables créées avec succès!' as status;
SELECT COUNT(*) as templates_count FROM public.commercial_templates;
