-- ========================================
-- INSÉRER SERVICES DE TEST
-- ========================================

-- Récupérer un merchant_id pour les tests
WITH merchant_sample AS (
    SELECT id FROM users WHERE role = 'merchant' LIMIT 1
)

INSERT INTO services (
    merchant_id, name, description, category, 
    price_per_lead, capacity_per_month, 
    lead_requirements, tags, images
) 
SELECT 
    (SELECT id FROM merchant_sample),
    'Consultation Marketing Digital - 1h',
    'Audit complet de votre stratégie digitale avec recommandations personnalisées. Session d''1 heure par visioconférence.',
    'Marketing Digital',
    50.00, -- 50€ par lead qualifié
    20, -- Max 20 leads/mois
    '{"min_budget": 500, "company_type": ["PME", "Startup"], "location": ["Morocco", "France"]}'::jsonb,
    '["marketing", "digital", "consultation", "audit"]'::jsonb,
    '["https://via.placeholder.com/600x400/6366F1/FFFFFF?text=Consultation+Marketing"]'::jsonb

UNION ALL SELECT 
    (SELECT id FROM merchant_sample),
    'Formation E-Commerce Complète',
    'Formation en ligne de 8 semaines pour créer et gérer votre boutique e-commerce. Inclut support et ressources.',
    'Formation',
    150.00,
    10,
    '{"min_budget": 2000, "experience": "débutant", "commitment": "8 semaines"}'::jsonb,
    '["formation", "ecommerce", "vente en ligne"]'::jsonb,
    '["https://via.placeholder.com/600x400/10B981/FFFFFF?text=Formation+E-Commerce"]'::jsonb

UNION ALL SELECT 
    (SELECT id FROM merchant_sample),
    'Coaching Instagram Growth',
    'Programme de coaching personnalisé sur 3 mois pour développer votre présence Instagram et monétiser votre audience.',
    'Coaching',
    200.00,
    5,
    '{"followers": ">1000", "engagement_rate": ">2%", "niche": ["mode", "beauté", "lifestyle"]}'::jsonb,
    '["coaching", "instagram", "réseaux sociaux", "croissance"]'::jsonb,
    '["https://via.placeholder.com/600x400/EC4899/FFFFFF?text=Coaching+Instagram"]'::jsonb

UNION ALL SELECT 
    (SELECT id FROM merchant_sample),
    'Création Site Web Vitrine',
    'Conception et développement de site web professionnel avec design responsive et optimisation SEO.',
    'Développement Web',
    75.00,
    15,
    '{"project_type": "site vitrine", "pages": "5-10", "budget": ">3000"}'::jsonb,
    '["développement", "site web", "design", "SEO"]'::jsonb,
    '["https://via.placeholder.com/600x400/F59E0B/FFFFFF?text=Création+Site+Web"]'::jsonb

UNION ALL SELECT 
    (SELECT id FROM merchant_sample),
    'Design Logo Professionnel',
    'Création de logo unique avec 3 propositions, révisions illimitées et livraison des fichiers sources.',
    'Design Graphique',
    30.00,
    30,
    '{"budget": ">500", "délai": "1-2 semaines", "style": ["moderne", "minimaliste", "corporate"]}'::jsonb,
    '["design", "logo", "branding", "identité visuelle"]'::jsonb,
    '["https://via.placeholder.com/600x400/8B5CF6/FFFFFF?text=Design+Logo"]'::jsonb

UNION ALL SELECT 
    (SELECT id FROM merchant_sample),
    'Rédaction Articles SEO',
    'Rédaction d''articles optimisés SEO de 1000-1500 mots avec recherche de mots-clés incluse.',
    'Rédaction',
    25.00,
    40,
    '{"word_count": "1000-1500", "niche": "tout secteur", "langue": ["français", "arabe"]}'::jsonb,
    '["rédaction", "SEO", "contenu", "articles"]'::jsonb,
    '["https://via.placeholder.com/600x400/14B8A6/FFFFFF?text=Rédaction+SEO"]'::jsonb

UNION ALL SELECT 
    (SELECT id FROM merchant_sample),
    'Gestion Réseaux Sociaux',
    'Gestion complète de vos réseaux sociaux : création de contenu, publication, engagement communauté.',
    'Marketing Digital',
    100.00,
    8,
    '{"platforms": ["Instagram", "Facebook", "LinkedIn"], "posts_per_week": "3-5", "duration": "1 mois minimum"}'::jsonb,
    '["social media", "community management", "contenu", "engagement"]'::jsonb,
    '["https://via.placeholder.com/600x400/3B82F6/FFFFFF?text=Gestion+Réseaux"]'::jsonb

UNION ALL SELECT 
    (SELECT id FROM merchant_sample),
    'Comptabilité PME - Mensuel',
    'Service de comptabilité mensuel pour PME : facturation, déclarations, bilan annuel.',
    'Comptabilité',
    80.00,
    12,
    '{"company_size": "PME", "turnover": "<500k€", "location": "Morocco"}'::jsonb,
    '["comptabilité", "gestion", "fiscalité"]'::jsonb,
    '["https://via.placeholder.com/600x400/EF4444/FFFFFF?text=Comptabilité+PME"]'::jsonb;

-- Vérifier les services créés
SELECT 
    name,
    category,
    price_per_lead || '€' as prix_par_lead,
    capacity_per_month as capacité_mois,
    total_leads as leads_actuels
FROM services
ORDER BY created_at DESC;

-- Compter par catégorie
SELECT 
    category,
    COUNT(*) as nombre_services,
    AVG(price_per_lead) as prix_moyen_lead
FROM services
GROUP BY category
ORDER BY nombre_services DESC;
