-- =====================================================
-- INSERTION DONNÉES DE TEST - DASHBOARD COMMERCIAL
-- =====================================================
-- À exécuter APRÈS CREATE_COMMERCIAL_TABLES.sql
-- =====================================================

-- 1. Créer 3 utilisateurs commerciaux avec différents niveaux d'abonnement
-- =====================================================

-- Commercial STARTER (Gratuit)
INSERT INTO users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.starter@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K', -- password: Test123!
    'commercial',
    'starter',
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Commercial PRO
INSERT INTO users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.pro@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K', -- password: Test123!
    'commercial',
    'pro',
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Commercial ENTERPRISE
INSERT INTO users (email, password_hash, role, subscription_tier, created_at) 
VALUES (
    'commercial.enterprise@getyourshare.com',
    '$2b$12$LQv3c1yYqAI9E3AzOqPmxevJLpzDrBOZh.PGJNRfKpN.w8xfS7W8K', -- password: Test123!
    'commercial',
    'enterprise',
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- 2. Créer les profils sales_representatives
-- =====================================================

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id,
    'Ahmed',
    'Benali',
    'commercial.starter@getyourshare.com',
    '+212 6 12 34 56 78',
    'Casablanca',
    5.0,
    10,
    50000,
    TRUE
FROM users u WHERE u.email = 'commercial.starter@getyourshare.com'
ON CONFLICT DO NOTHING;

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id,
    'Fatima',
    'Zahra',
    'commercial.pro@getyourshare.com',
    '+212 6 23 45 67 89',
    'Rabat',
    7.5,
    20,
    150000,
    TRUE
FROM users u WHERE u.email = 'commercial.pro@getyourshare.com'
ON CONFLICT DO NOTHING;

INSERT INTO sales_representatives (
    user_id, first_name, last_name, email, phone, territory, 
    commission_rate, target_monthly_deals, target_monthly_revenue, is_active
)
SELECT 
    u.id,
    'Youssef',
    'Alami',
    'commercial.enterprise@getyourshare.com',
    '+212 6 34 56 78 90',
    'Marrakech',
    10.0,
    50,
    500000,
    TRUE
FROM users u WHERE u.email = 'commercial.enterprise@getyourshare.com'
ON CONFLICT DO NOTHING;

-- 3. Templates de contenu marketing
-- =====================================================

-- Templates STARTER (gratuits - 3 seulement)
INSERT INTO commercial_templates (title, category, template_type, content, subscription_tier) VALUES
('Post Facebook Simple', 'facebook', 'post', '🔥 Découvrez {product_name} à seulement {price}€ ! 
✨ Profitez de cette offre exclusive maintenant !
👉 Cliquez ici : {link}', 'starter'),

('Message WhatsApp Basique', 'whatsapp', 'message', 'Bonjour ! Je vous présente {product_name}, un produit fantastique à {price}€.
Intéressé(e) ? Répondez-moi pour plus d''infos ! 😊', 'starter'),

('Email Simple', 'email', 'email_body', 'Bonjour,

Je tenais à vous présenter {product_name}.

Prix: {price}€
Commission: {commission}€

Cordialement', 'starter');

-- Templates PRO (15 modèles)
INSERT INTO commercial_templates (title, category, template_type, content, subscription_tier) VALUES
('Post LinkedIn Professionnel', 'linkedin', 'post', '🚀 Nouveauté dans mon réseau !

Je suis ravi de partager {product_name} avec vous.

✅ {benefit_1}
✅ {benefit_2}
✅ {benefit_3}

Prix exceptionnel: {price}€

Contactez-moi en MP pour une démonstration ! 💼

#Business #Innovation #Vente', 'pro'),

('Story Instagram Engageante', 'instagram', 'story', '✨ ALERTE NOUVEAUTÉ ✨

{product_name}

Prix: {price}€ 
Ma commission: {commission}€

Swipe up 👆 pour commander !

#nouveauté #promo', 'pro'),

('Email de Relance 1', 'email', 'email_body', 'Bonjour {contact_name},

Je reviens vers vous concernant {product_name}.

Avez-vous eu le temps d''y réfléchir ?

Je reste disponible pour répondre à vos questions.

Meilleurs salutations,
{sales_rep_name}', 'pro'),

('Email de Relance 2', 'email', 'email_body', 'Bonjour {contact_name},

J''espère que vous allez bien.

Je souhaitais savoir si vous aviez besoin d''informations complémentaires sur {product_name}.

N''hésitez pas à me contacter.

Cordialement,
{sales_rep_name}', 'pro'),

('WhatsApp Business Pro', 'whatsapp', 'message', '👋 Bonjour {contact_name} !

Je vous contacte pour vous présenter {product_name}.

🎯 Avantages:
• {benefit_1}
• {benefit_2}
• {benefit_3}

💰 Prix: {price}€
⏱️ Offre valable jusqu''au {date}

Souhaitez-vous une démonstration ?', 'pro'),

('Message de Prospection Cold', 'linkedin', 'message', 'Bonjour {contact_name},

J''ai remarqué votre profil et je pense que {product_name} pourrait intéresser {company_name}.

Seriez-vous disponible pour un échange de 15 minutes cette semaine ?

Bien à vous,
{sales_rep_name}', 'pro'),

('Email Présentation Produit', 'email', 'email_body', 'Objet: {product_name} - Solution pour {company_name}

Bonjour {contact_name},

Je me permets de vous contacter pour vous présenter {product_name}.

Notre solution permet de:
• {benefit_1}
• {benefit_2}
• {benefit_3}

Prix: {price}€
ROI estimé: {roi}%

Puis-je vous proposer une démonstration ?

Cordialement,
{sales_rep_name}
{phone}', 'pro'),

('SMS de Rappel RDV', 'sms', 'message', 'Bonjour {contact_name}, je vous confirme notre RDV du {date} à {time} pour parler de {product_name}. À bientôt ! - {sales_rep_name}', 'pro'),

('Post Facebook Promo', 'facebook', 'post', '🎉 OFFRE SPÉCIALE 🎉

{product_name} en PROMOTION !

❌ Prix normal: {old_price}€
✅ Prix promo: {price}€

🔥 Économisez {discount}€ !

⏰ Offre limitée jusqu''au {date}

👉 Commandez maintenant : {link}

#promo #bonplan #affaire', 'pro'),

('Email de Remerciement', 'email', 'email_body', 'Bonjour {contact_name},

Je vous remercie pour votre confiance et votre achat de {product_name}.

Si vous avez des questions, je reste à votre disposition.

Excellente journée !

{sales_rep_name}', 'pro'),

('Message Cross-Sell', 'whatsapp', 'message', 'Bonjour {contact_name} ! 😊

Puisque vous avez aimé {product_1}, je pense que {product_2} pourrait aussi vous intéresser !

Ils se complètent parfaitement.

Prix spécial clients: {price}€

Intéressé(e) ?', 'pro'),

('Email Objection Prix', 'email', 'email_body', 'Bonjour {contact_name},

Je comprends votre préoccupation concernant le prix.

Voici pourquoi {product_name} vaut son investissement:

1. {value_prop_1}
2. {value_prop_2}
3. {value_prop_3}

De plus, nous proposons un paiement en plusieurs fois.

Pouvons-nous en discuter ?

Cordialement,
{sales_rep_name}', 'pro'),

('Post LinkedIn Témoignage', 'linkedin', 'post', '⭐⭐⭐⭐⭐

Un de mes clients vient de me partager son expérience avec {product_name} :

"{testimonial}"

Résultat: {result}

Vous aussi, profitez de cette solution !

Contactez-moi en MP. 💬

#succès #client #business', 'pro'),

('Email Urgence', 'email', 'email_body', 'Objet: ⏰ DERNIÈRES HEURES - {product_name}

Bonjour {contact_name},

L''offre sur {product_name} se termine dans {hours} heures !

Prix exceptionnel: {price}€ au lieu de {old_price}€

Ne manquez pas cette opportunité.

Commandez maintenant: {link}

Cordialement,
{sales_rep_name}', 'pro'),

('SMS Suivi Livraison', 'sms', 'message', 'Bonjour ! Votre commande {product_name} sera livrée demain. Suivi: {tracking_link}. Des questions ? Appelez-moi ! - {sales_rep_name}', 'pro');

-- Templates ENTERPRISE (illimités - exemples avancés)
INSERT INTO commercial_templates (title, category, template_type, content, subscription_tier) VALUES
('Email Multitouch Séquence 1', 'email', 'email_body', 'Objet: {contact_name}, découvrez comment {company_name} peut économiser {savings}€

Bonjour {contact_name},

J''ai analysé votre secteur ({industry}) et identifié une opportunité.

{product_name} permet aux entreprises comme {company_name} de:
• Réduire les coûts de {percentage}%
• Augmenter la productivité de {productivity}%
• ROI en {roi_months} mois

Cas client similaire: {case_study}

Disponible pour un appel de 15 min cette semaine ?

Meilleurs salutations,
{sales_rep_name}
{title} chez {company}
{phone} | {email}', 'enterprise'),

('Proposition Commerciale Automatique', 'email', 'email_body', 'Objet: Proposition commerciale - {product_name} pour {company_name}

Bonjour {contact_name},

Suite à notre échange, voici ma proposition:

📦 SOLUTION: {product_name}

💼 POUR: {company_name} ({company_size} employés)

🎯 OBJECTIFS:
• {objective_1}
• {objective_2}
• {objective_3}

💰 INVESTISSEMENT:
Prix: {price}€ HT
Remise: -{discount}%
Prix final: {final_price}€ HT

⏱️ DÉPLOIEMENT: {timeline}

📈 ROI ESTIMÉ: {roi}% en {roi_months} mois

📄 Proposition détaillée: {proposal_link}

Discutons-en ?

Cordialement,
{sales_rep_name}', 'enterprise'),

('Message LinkedIn Personnalisé IA', 'linkedin', 'message', 'Bonjour {contact_name},

J''ai remarqué que {company_name} est en pleine croissance dans {industry}.

Félicitations pour {recent_achievement} ! 🎉

Je travaille avec des entreprises similaires comme {competitor_1} et {competitor_2}.

{product_name} les a aidées à:
• {result_1}
• {result_2}

Seriez-vous ouvert(e) à un échange de 10 minutes ?

Je pense pouvoir vous apporter de la valeur.

Meilleurs salutations,
{sales_rep_name}', 'enterprise'),

('Email Post-Demo', 'email', 'email_body', 'Objet: Merci pour la démo {product_name} !

Bonjour {contact_name},

Merci d''avoir assisté à la démonstration de {product_name}.

📋 RÉCAPITULATIF:
• Points clés discutés: {key_points}
• Vos besoins: {needs}
• Notre solution: {solution}

📹 Replay de la démo: {replay_link}
📄 Documentation: {docs_link}
💾 Ressources: {resources_link}

🚀 PROCHAINES ÉTAPES:
1. {next_step_1}
2. {next_step_2}
3. {next_step_3}

📅 Proposition de RDV: {meeting_slots}

Des questions ?

Cordialement,
{sales_rep_name}', 'enterprise');

-- 4. Créer des leads pour chaque commercial
-- =====================================================

-- Leads pour STARTER (max 10 selon limite)
INSERT INTO commercial_leads (
    user_id, first_name, last_name, email, phone, company, 
    status, temperature, source, estimated_value, notes
)
SELECT 
    sr.user_id,
    'Mohammed',
    'Idrissi',
    'mohammed@entreprise1.ma',
    '+212 6 11 22 33 44',
    'Tech Solutions Maroc',
    'nouveau',
    'froid',
    'linkedin',
    15000,
    'Contact initial via LinkedIn'
FROM sales_representatives sr WHERE sr.email = 'commercial.starter@getyourshare.com';

INSERT INTO commercial_leads (
    user_id, first_name, last_name, email, phone, company, 
    status, temperature, source, estimated_value
)
SELECT 
    sr.user_id,
    'Amina',
    'Benjelloun',
    'amina@startup.ma',
    '+212 6 22 33 44 55',
    'Startup Innovante',
    'qualifie',
    'tiede',
    'email',
    8000
FROM sales_representatives sr WHERE sr.email = 'commercial.starter@getyourshare.com';

INSERT INTO commercial_leads (
    user_id, first_name, last_name, email, phone, company, 
    status, temperature, source, estimated_value
)
SELECT 
    sr.user_id,
    'Hassan',
    'Ouazzani',
    'hassan@digital.ma',
    '+212 6 33 44 55 66',
    'Digital Agency',
    'en_negociation',
    'chaud',
    'referral',
    25000
FROM sales_representatives sr WHERE sr.email = 'commercial.starter@getyourshare.com';

-- Plus de leads pour PRO et ENTERPRISE
INSERT INTO commercial_leads (
    user_id, first_name, last_name, email, phone, company, 
    status, temperature, source, estimated_value, notes
)
SELECT 
    sr.user_id,
    unnest(ARRAY['Karim', 'Laila', 'Omar', 'Nadia', 'Rachid', 'Sofia', 'Tariq', 'Yasmine', 'Zakaria', 'Malika', 
                  'Fouad', 'Hind', 'Mehdi', 'Khadija', 'Youssef']),
    unnest(ARRAY['Alaoui', 'Bennani', 'Chraibi', 'Drissi', 'Fassi', 'Guessous', 'Hajji', 'Idrissi', 'Jallal', 'Kettani',
                  'Lahlou', 'Mahjoub', 'Naciri', 'Ouahabi', 'Qotbi']),
    unnest(ARRAY['karim@company.ma', 'laila@business.ma', 'omar@tech.ma', 'nadia@digital.ma', 'rachid@solutions.ma',
                  'sofia@services.ma', 'tariq@group.ma', 'yasmine@consulting.ma', 'zakaria@agency.ma', 'malika@partners.ma',
                  'fouad@ventures.ma', 'hind@marketing.ma', 'mehdi@sales.ma', 'khadija@trading.ma', 'youssef@commerce.ma']),
    '+212 6 ' || lpad((random()*100000000)::bigint::text, 8, '0'),
    unnest(ARRAY['Alpha Corp', 'Beta Solutions', 'Gamma Tech', 'Delta Services', 'Epsilon Group',
                  'Zeta Consulting', 'Eta Ventures', 'Theta Partners', 'Iota Marketing', 'Kappa Trading',
                  'Lambda Digital', 'Mu Agency', 'Nu Business', 'Xi Commerce', 'Omicron Industries']),
    unnest(ARRAY['nouveau', 'qualifie', 'en_negociation', 'nouveau', 'qualifie',
                  'en_negociation', 'conclu', 'nouveau', 'qualifie', 'perdu',
                  'nouveau', 'en_negociation', 'qualifie', 'nouveau', 'conclu']),
    unnest(ARRAY['froid', 'tiede', 'chaud', 'froid', 'tiede',
                  'chaud', 'chaud', 'froid', 'tiede', 'froid',
                  'tiede', 'chaud', 'tiede', 'froid', 'chaud']),
    unnest(ARRAY['linkedin', 'email', 'whatsapp', 'referral', 'event',
                  'linkedin', 'email', 'whatsapp', 'linkedin', 'email',
                  'referral', 'event', 'linkedin', 'whatsapp', 'email']),
    (random() * 50000 + 5000)::NUMERIC(10,2),
    'Lead généré pour test'
FROM sales_representatives sr WHERE sr.email = 'commercial.pro@getyourshare.com';

-- Encore plus de leads pour ENTERPRISE
INSERT INTO commercial_leads (
    user_id, first_name, last_name, email, phone, company, 
    status, temperature, source, estimated_value
)
SELECT 
    sr.user_id,
    'Client ' || generate_series,
    'Test ' || generate_series,
    'client' || generate_series || '@example.com',
    '+212 6 ' || lpad(generate_series::text, 8, '0'),
    'Company ' || generate_series,
    (ARRAY['nouveau', 'qualifie', 'en_negociation', 'conclu'])[1 + floor(random()*4)::int],
    (ARRAY['froid', 'tiede', 'chaud'])[1 + floor(random()*3)::int],
    (ARRAY['linkedin', 'email', 'whatsapp', 'referral', 'event'])[1 + floor(random()*5)::int],
    (random() * 100000 + 10000)::NUMERIC(10,2)
FROM sales_representatives sr, generate_series(1, 50)
WHERE sr.email = 'commercial.enterprise@getyourshare.com';

-- 5. Créer des liens trackés
-- =====================================================

-- 3 liens pour STARTER (limite atteinte)
INSERT INTO commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, total_clicks, total_conversions, total_revenue
)
SELECT 
    sr.user_id,
    p.id,
    'TRACK-' || substr(md5(random()::text), 1, 8),
    'https://tracknow.io/ref/' || substr(md5(random()::text), 1, 8),
    (ARRAY['whatsapp', 'linkedin', 'facebook'])[idx],
    (ARRAY['Campagne WhatsApp', 'Campagne LinkedIn', 'Campagne Facebook'])[idx],
    floor(random() * 50)::int,
    floor(random() * 5)::int,
    (random() * 5000)::NUMERIC(10,2)
FROM sales_representatives sr
CROSS JOIN LATERAL (SELECT id FROM products ORDER BY random() LIMIT 1) p
CROSS JOIN LATERAL generate_series(1, 3) idx
WHERE sr.email = 'commercial.starter@getyourshare.com';

-- Plus de liens pour PRO (15 liens)
INSERT INTO commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, total_clicks, total_conversions, total_revenue
)
SELECT 
    sr.user_id,
    p.id,
    'TRACK-PRO-' || substr(md5(random()::text), 1, 8),
    'https://tracknow.io/ref/' || substr(md5(random()::text), 1, 8),
    (ARRAY['whatsapp', 'linkedin', 'facebook', 'email', 'sms'])[1 + floor(random()*5)::int],
    'Campagne ' || generate_series,
    floor(random() * 200)::int,
    floor(random() * 20)::int,
    (random() * 15000)::NUMERIC(10,2)
FROM sales_representatives sr
CROSS JOIN LATERAL (SELECT id FROM products ORDER BY random() LIMIT 1) p
CROSS JOIN generate_series(1, 15)
WHERE sr.email = 'commercial.pro@getyourshare.com';

-- Encore plus pour ENTERPRISE (30 liens)
INSERT INTO commercial_tracking_links (
    user_id, product_id, link_code, full_url, channel, campaign_name, total_clicks, total_conversions, total_revenue
)
SELECT 
    sr.user_id,
    p.id,
    'TRACK-ENT-' || substr(md5(random()::text), 1, 8),
    'https://tracknow.io/ref/' || substr(md5(random()::text), 1, 8),
    (ARRAY['whatsapp', 'linkedin', 'facebook', 'email', 'sms'])[1 + floor(random()*5)::int],
    'Campagne Enterprise ' || generate_series,
    floor(random() * 500)::int,
    floor(random() * 50)::int,
    (random() * 50000)::NUMERIC(10,2)
FROM sales_representatives sr
CROSS JOIN LATERAL (SELECT id FROM products ORDER BY random() LIMIT 1) p
CROSS JOIN generate_series(1, 30)
WHERE sr.email = 'commercial.enterprise@getyourshare.com';

-- 6. Créer des statistiques agrégées (pour les graphiques)
-- =====================================================

-- Stats des 30 derniers jours pour chaque commercial
INSERT INTO commercial_stats (
    user_id, period, period_date, leads_generated, leads_qualified, leads_converted,
    total_revenue, total_commission, total_clicks, pipeline_value
)
SELECT 
    sr.user_id,
    'daily',
    CURRENT_DATE - i,
    CASE 
        WHEN sr.email = 'commercial.starter@getyourshare.com' THEN floor(random() * 3)::int
        WHEN sr.email = 'commercial.pro@getyourshare.com' THEN floor(random() * 10)::int
        ELSE floor(random() * 20)::int
    END,
    CASE 
        WHEN sr.email = 'commercial.starter@getyourshare.com' THEN floor(random() * 2)::int
        WHEN sr.email = 'commercial.pro@getyourshare.com' THEN floor(random() * 5)::int
        ELSE floor(random() * 15)::int
    END,
    CASE 
        WHEN sr.email = 'commercial.starter@getyourshare.com' THEN floor(random() * 1)::int
        WHEN sr.email = 'commercial.pro@getyourshare.com' THEN floor(random() * 3)::int
        ELSE floor(random() * 8)::int
    END,
    CASE 
        WHEN sr.email = 'commercial.starter@getyourshare.com' THEN (random() * 5000)::NUMERIC(10,2)
        WHEN sr.email = 'commercial.pro@getyourshare.com' THEN (random() * 15000)::NUMERIC(10,2)
        ELSE (random() * 50000)::NUMERIC(10,2)
    END,
    CASE 
        WHEN sr.email = 'commercial.starter@getyourshare.com' THEN (random() * 250)::NUMERIC(10,2)
        WHEN sr.email = 'commercial.pro@getyourshare.com' THEN (random() * 1125)::NUMERIC(10,2)
        ELSE (random() * 5000)::NUMERIC(10,2)
    END,
    CASE 
        WHEN sr.email = 'commercial.starter@getyourshare.com' THEN floor(random() * 50)::int
        WHEN sr.email = 'commercial.pro@getyourshare.com' THEN floor(random() * 200)::int
        ELSE floor(random() * 500)::int
    END,
    CASE 
        WHEN sr.email = 'commercial.starter@getyourshare.com' THEN (random() * 20000)::NUMERIC(10,2)
        WHEN sr.email = 'commercial.pro@getyourshare.com' THEN (random() * 75000)::NUMERIC(10,2)
        ELSE (random() * 250000)::NUMERIC(10,2)
    END
FROM sales_representatives sr
CROSS JOIN generate_series(0, 29) i;

-- =====================================================
-- FIN DE L'INSERTION
-- =====================================================

-- Vérification des données
SELECT 
    'users' as table_name,
    COUNT(*) as count
FROM users WHERE role = 'commercial'
UNION ALL
SELECT 
    'sales_representatives',
    COUNT(*)
FROM sales_representatives
UNION ALL
SELECT 
    'commercial_leads',
    COUNT(*)
FROM commercial_leads
UNION ALL
SELECT 
    'commercial_tracking_links',
    COUNT(*)
FROM commercial_tracking_links
UNION ALL
SELECT 
    'commercial_templates',
    COUNT(*)
FROM commercial_templates
UNION ALL
SELECT 
    'commercial_stats',
    COUNT(*)
FROM commercial_stats;
