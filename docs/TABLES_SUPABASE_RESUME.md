# 📊 TABLES SUPABASE - RÉSUMÉ COMPLET

## 🎯 OBJECTIF
Ce document liste **TOUTES** les 97 tables nécessaires pour l'application GetYourShare, détectées par analyse automatique du code backend.

## 📁 FICHIER SQL PRINCIPAL
**`CREATE_ALL_TABLES_COMPLETE.sql`** - Script SQL complet à exécuter dans Supabase

---

## 📋 LISTE DES 97 TABLES

### 1. CORE - UTILISATEURS (3 tables)
1. ✅ `users` - Table principale des utilisateurs
2. ✅ `merchants` - Profils marchands  
3. ✅ `influencers` - Profils influenceurs

### 2. PRODUCTS & SERVICES (3 tables)
4. ✅ `products` - Produits des marchands
5. ✅ `services` - Services des marchands
6. ✅ `product_categories` - Catégories de produits

### 3. CAMPAIGNS (3 tables)
7. ✅ `campaigns` - Campagnes marketing
8. ✅ `campaign_products` - Liaison campagnes-produits
9. ✅ `campaign_settings` - Paramètres des campagnes

### 4. TRACKING & CONVERSIONS (6 tables)
10. ✅ `tracking_links` - Liens de tracking principaux
11. ✅ `trackable_links` - Liens traçables (ancienne version)
12. ✅ `conversions` - Conversions/ventes
13. ✅ `click_tracking` - Suivi des clics détaillé
14. ✅ `click_logs` - Logs des clics
15. ✅ `tracking_events` - Événements de tracking

### 5. SALES & COMMISSIONS (3 tables)
16. ✅ `sales` - Ventes réalisées
17. ✅ `commissions` - Commissions calculées
18. ✅ `payouts` - Paiements aux influenceurs

### 6. INVITATIONS & COLLABORATIONS (5 tables)
19. ✅ `invitations` - Invitations marchands → influenceurs
20. ✅ `collaboration_requests` - Demandes de collaboration
21. ✅ `collaboration_invitations` - Invitations génériques
22. ✅ `collaboration_history` - Historique des collaborations
23. ✅ `influencer_agreements` - Accords signés

### 7. AFFILIATION REQUESTS (7 tables)
24. ✅ `affiliation_requests` - Demandes d'affiliation principales
25. ✅ `influencer_affiliation_requests` - Demandes influenceur
26. ✅ `merchant_affiliation_requests` - Demandes marchand
27. ✅ `affiliate_requests` - Demandes affilié
28. ✅ `affiliation_requests_stats` - Statistiques
29. ✅ `affiliation_request_history` - Historique
30. ✅ `affiliate_links` - Liens d'affiliation

### 8. SUBSCRIPTIONS (5 tables)
31. ✅ `subscription_plans` - Plans d'abonnement (Free/Pro/Elite)
32. ✅ `subscriptions` - Abonnements actifs
33. ✅ `subscription_usage` - Utilisation des limites
34. ✅ `subscription_events` - Événements d'abonnement
35. ✅ `subscription_coupons` - Codes promo

### 9. INVOICES & PAYMENTS (7 tables)
36. ✅ `invoices` - Factures utilisateurs
37. ✅ `platform_invoices` - Factures plateforme
38. ✅ `invoice_line_items` - Lignes de facture
39. ✅ `payments` - Paiements génériques
40. ✅ `payment_methods` - Moyens de paiement
41. ✅ `payment_accounts` - Comptes de paiement
42. ✅ `payment_transactions` - Transactions

### 10. LEADS SYSTEM (6 tables)
43. ✅ `leads` - Leads/prospects
44. ✅ `sales_leads` - Leads commerciaux
45. ✅ `lead_validation` - Validation de leads
46. ✅ `merchant_deposits` - Dépôts marchands
47. ✅ `company_deposits` - Dépôts entreprise
48. ✅ `deposit_transactions` - Transactions de dépôts

### 11. SOCIAL MEDIA (5 tables)
49. ✅ `social_connections` - Connexions réseaux sociaux
50. ✅ `social_media_connections` - Connexions détaillées
51. ✅ `social_media_accounts` - Comptes sociaux
52. ✅ `social_media_publications` - Publications
53. ✅ `social_media_stats` - Statistiques sociales

### 12. ADMIN SOCIAL POSTS (2 tables)
54. ✅ `admin_social_posts` - Posts admin
55. ✅ `admin_social_post_templates` - Templates de posts

### 13. SALES REPRESENTATIVES (6 tables)
56. ✅ `sales_representatives` - Représentants commerciaux
57. ✅ `sales_activities` - Activités commerciales
58. ✅ `deals` - Deals/opportunités
59. ✅ `sales_deals` - Deals simplifiés
60. ✅ `sales_targets` - Objectifs commerciaux
61. ✅ `sales_commissions` - Commissions commerciales

### 14. MESSAGING & NOTIFICATIONS (3 tables)
62. ✅ `conversations` - Conversations
63. ✅ `messages` - Messages
64. ✅ `notifications` - Notifications

### 15. REVIEWS & RATINGS (2 tables)
65. ✅ `reviews` - Avis génériques
66. ✅ `product_reviews` - Avis produits

### 16. GAMIFICATION (4 tables)
67. ✅ `user_gamification` - Niveaux/points utilisateurs
68. ✅ `badges` - Badges disponibles
69. ✅ `missions` - Missions/défis
70. ✅ `user_missions` - Missions utilisateurs

### 17. KYC & VERIFICATION (5 tables)
71. ✅ `kyc_submissions` - Soumissions KYC
72. ✅ `user_kyc_profile` - Profils KYC
73. ✅ `user_kyc_documents` - Documents KYC
74. ✅ `kyc_verification_logs` - Logs de vérification
75. ✅ `trust_scores` - Scores de confiance

### 18. GATEWAY & TRANSACTIONS (2 tables)
76. ✅ `gateway_transactions` - Transactions gateway
77. ✅ `gateway_statistics` - Statistiques gateway

### 19. TEAM & COMPANY (3 tables)
78. ✅ `team_members` - Membres d'équipe
79. ✅ `team_invitations` - Invitations équipe
80. ✅ `company_settings` - Paramètres entreprise

### 20. PLATFORM SETTINGS (2 tables)
81. ✅ `platform_settings` - Paramètres plateforme
82. ✅ `settings` - Paramètres génériques

### 21. CONTACT & MODERATION (2 tables)
83. ✅ `contact_messages` - Messages de contact
84. ✅ `moderation_queue` - File de modération

### 22. AUTRES TABLES (6 tables)
85. ✅ `swipe_history` - Historique swipe (type Tinder)
86. ✅ `user_sessions` - Sessions utilisateurs
87. ✅ `webhook_logs` - Logs webhooks
88. ✅ `translations` - Traductions i18n
89. ✅ `match_preferences` - Préférences de matching
90. ✅ `influencer_profiles_extended` - Profils influenceurs étendus
91. ✅ `performance_metrics` - Métriques de performance

### 23. VUES MATÉRIALISÉES (6 vues)
92. ✅ `v_products_full` - Produits avec détails complets
93. ✅ `v_featured_products` - Produits en vedette
94. ✅ `v_deals_of_day` - Deals du jour
95. ✅ `v_admin_social_posts_summary` - Résumé posts admin
96. ✅ `v_admin_social_analytics` - Analytics posts admin
97. ✅ `v_contact_stats` - Statistiques de contact

---

## 🚀 COMMENT UTILISER

### Étape 1: Ouvrir Supabase SQL Editor
1. Connectez-vous à votre projet Supabase
2. Allez dans "SQL Editor"

### Étape 2: Exécuter le script
1. Ouvrez le fichier `CREATE_ALL_TABLES_COMPLETE.sql`
2. Copiez tout le contenu
3. Collez dans l'éditeur SQL de Supabase
4. Cliquez sur "Run" (Exécuter)

### Étape 3: Vérifier
Le script affichera automatiquement:
- Nombre de tables créées
- Nombre de vues créées  
- Nombre d'index créés

---

## ✨ FONCTIONNALITÉS INCLUSES

### 1. Création automatique des tables
- ✅ Toutes les 97 tables avec leurs colonnes
- ✅ Types de données appropriés
- ✅ Contraintes et validations
- ✅ Foreign keys (relations)

### 2. Index pour les performances
- ✅ Index sur toutes les colonnes fréquemment utilisées
- ✅ Index composites pour les recherches complexes
- ✅ Index GIN pour les arrays et JSONB

### 3. Triggers automatiques
- ✅ Trigger `updated_at` sur toutes les tables concernées
- ✅ Mise à jour automatique des timestamps

### 4. Row Level Security (RLS)
- ✅ RLS activé sur toutes les tables
- ✅ Politique par défaut pour les admins

### 5. Données par défaut
- ✅ 3 plans d'abonnement (Free, Pro, Elite)
- ✅ 8 catégories de produits
- ✅ Paramètres de plateforme essentiels

### 6. Vues matérialisées
- ✅ 6 vues pour analytics et dashboards
- ✅ Optimisation des requêtes complexes

---

## 📊 STATISTIQUES

| Catégorie | Nombre |
|-----------|--------|
| **Tables de données** | 91 |
| **Vues matérialisées** | 6 |
| **Total** | **97** |
| **Index créés** | ~120+ |
| **Foreign keys** | ~80+ |
| **Triggers** | ~15 |

---

## 🔧 TABLES PAR FONCTIONNALITÉ

### AUTHENTIFICATION & UTILISATEURS
- users, merchants, influencers
- user_sessions, user_kyc_profile, trust_scores

### MARKETPLACE
- products, services, product_categories
- tracking_links, conversions, sales

### SYSTÈME DE LEADS
- leads, lead_validation, merchant_deposits
- sales_representatives, deals, sales_activities

### ABONNEMENTS & PAIEMENTS
- subscription_plans, subscriptions, invoices
- payments, payouts, gateway_transactions

### COLLABORATIONS
- campaigns, invitations, collaboration_requests
- affiliation_requests, affiliate_links

### SOCIAL MEDIA
- social_connections, social_media_publications
- admin_social_posts, admin_social_post_templates

### GAMIFICATION
- user_gamification, badges, missions, user_missions

### ANALYTICS & TRACKING
- click_tracking, tracking_events, performance_metrics
- Vues matérialisées pour dashboards

---

## ⚠️ NOTES IMPORTANTES

### Tables en doublon (intentionnel)
Certaines tables existent en double car elles sont utilisées dans différents contextes:
- `tracking_links` vs `trackable_links` (migration progressive)
- `leads` vs `sales_leads` (différents workflows)
- `deals` vs `sales_deals` (simplifiée vs complète)

### Tables de liaison
Plusieurs tables servent uniquement de liaison (many-to-many):
- `campaign_products`
- `user_missions`
- `team_members`

### Tables legacy
Certaines tables sont maintenues pour compatibilité:
- `trackable_links` (remplacé par `tracking_links`)
- `click_tracking` (logs simples)

---

## 🔄 MISE À JOUR

Si vous avez déjà des tables existantes:
1. Le script utilise `CREATE TABLE IF NOT EXISTS`
2. Les tables existantes ne seront PAS modifiées
3. Seules les tables manquantes seront créées

Pour forcer une recréation:
```sql
-- ATTENTION: SUPPRIME TOUTES LES DONNÉES!
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
-- Puis exécutez le script complet
```

---

## 📞 SUPPORT

Pour toute question sur la structure des tables:
1. Consultez `LISTE_TABLES_COMPLETE.txt` pour la liste brute
2. Vérifiez `CREATE_ALL_TABLES_COMPLETE.sql` pour les détails
3. Utilisez `extract_all_tables.py` pour re-scanner le backend

---

## ✅ VALIDATION

Après exécution du script, vérifiez:

```sql
-- Compter les tables créées
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- Devrait retourner: ~91

-- Compter les vues
SELECT COUNT(*) FROM information_schema.views 
WHERE table_schema = 'public';
-- Devrait retourner: 6

-- Vérifier les plans d'abonnement
SELECT * FROM subscription_plans;
-- Devrait retourner: Free, Pro, Elite

-- Vérifier les catégories
SELECT * FROM product_categories;
-- Devrait retourner: 8 catégories
```

---

**🎉 TOUTES LES TABLES SONT MAINTENANT PRÊTES! 🎉**

L'application GetYourShare dispose maintenant de toute la structure de données nécessaire pour fonctionner à 100%.
