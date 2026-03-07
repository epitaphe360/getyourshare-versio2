# 🧪 GUIDE DE TEST COMPLET - ShareYourSales

## Identifiants de Test

```
Admin: admin@shareyoursales.com / admin123
Influencer: (à créer ou utiliser compte existant)
Commercial: (à créer ou utiliser compte existant)
Merchant: (à créer ou utiliser compte existant)
```

---

## 📋 TESTS À EFFECTUER PAR SESSION

### SESSION 1: DASHBOARD ADMIN

#### Login Admin
1. ✅ Aller sur https://shareyoursales.vercel.app/
2. ✅ Login: `admin@shareyoursales.com` / `admin123`
3. ✅ Vérifier redirection vers Dashboard Admin

#### Onglet Overview
1. ✅ Vérifier que les stats s'affichent (revenus, users, produits)
2. ✅ Vérifier les graphiques (revenus, utilisateurs)
3. ✅ Vérifier activité récente
4. ❌ **BUG POTENTIEL**: Si erreur 403/500, noter le message exact

#### Onglet Users
1. ✅ Vérifier liste des utilisateurs
2. ✅ Cliquer sur "Ajouter utilisateur"
3. ✅ Essayer de créer un nouvel utilisateur
4. ❌ **BUG POTENTIEL**: Vérifier validation email/mot de passe

#### Onglet Merchants
1. ✅ Vérifier liste des marchands
2. ✅ Essayer de valider/rejeter un marchand
3. ❌ **BUG POTENTIEL**: Vérifier que le statut change

#### Onglet Products
1. ✅ Vérifier liste des produits
2. ✅ Cliquer "Ajouter produit"
3. ✅ Remplir formulaire (nom, prix, commission, catégorie)
4. ✅ Upload image (si disponible)
5. ✅ Sauvegarder
6. ❌ **BUG POTENTIEL**: Vérifier que le produit apparaît dans la liste

#### Onglet Services
1. ✅ Vérifier liste des services
2. ✅ Essayer d'ajouter un service
3. ❌ **BUG POTENTIEL**: Vérifier différence avec produits

#### Onglet Subscriptions
1. ✅ Vérifier liste des abonnements actifs
2. ✅ Essayer export CSV
3. ❌ **BUG POTENTIEL**: Vérifier que CSV se télécharge correctement

#### Onglet Registrations
1. ✅ Vérifier inscriptions en attente
2. ✅ Essayer de valider/rejeter
3. ❌ **BUG POTENTIEL**: Vérifier notification à l'utilisateur

#### Onglet Finance
1. ✅ Vérifier transactions
2. ✅ Vérifier graphiques financiers
3. ✅ Essayer export données
4. ❌ **BUG POTENTIEL**: Vérifier calculs commissions

#### Onglet Analytics
1. ✅ Vérifier analytics avancées
2. ✅ Changer période (7j, 30j, 90j)
3. ✅ Vérifier tous les graphiques se mettent à jour
4. ❌ **BUG POTENTIEL**: Données manquantes ou incohérentes

#### Onglet Support
1. ✅ Vérifier tickets support
2. ✅ Essayer de répondre à un ticket
3. ✅ Changer statut (ouvert → résolu)
4. ❌ **BUG POTENTIEL**: Vérifier notifications

#### Onglet Live Chat
1. ✅ Ouvrir live chat
2. ✅ Envoyer message
3. ❌ **BUG POTENTIEL**: Vérifier temps réel (websockets)

---

### SESSION 2: DASHBOARD INFLUENCER

#### Login Influencer
1. ✅ Se connecter avec compte influencer
2. ✅ Vérifier redirection vers Dashboard Influencer

#### Vue Générale
1. ✅ Vérifier stats (clics, conversions, commissions)
2. ✅ Vérifier graphiques
3. ❌ **BUG POTENTIEL**: Données à zéro alors qu'il y a activité

#### Liens d'Affiliation
1. ✅ Voir liste des liens
2. ✅ Cliquer "Copier lien"
3. ✅ Vérifier notification "Copié"
4. ✅ Essayer le lien copié dans un nouvel onglet
5. ❌ **BUG POTENTIEL**: Lien ne redirige pas ou erreur 404

#### Demande de Paiement
1. ✅ Cliquer "Demander paiement"
2. ✅ Entrer montant
3. ✅ Vérifier montant minimum (devrait être défini)
4. ✅ Sélectionner méthode (EUR, MAD mobile)
5. ✅ Soumettre
6. ❌ **BUG POTENTIEL**: Erreur "Montant supérieur au solde"
7. ❌ **BUG POTENTIEL**: Notification paiement mobile ne s'ouvre pas

#### Parrainage
1. ✅ Voir section "Mon Code de Parrainage"
2. ✅ Copier code referral
3. ✅ Vérifier statistiques (parrainages, gains)
4. ✅ Voir réseau multi-niveaux
5. ❌ **BUG POTENTIEL**: Stats à zéro ou erreur API

#### Recommandations IA
1. ✅ Voir section "Produits Recommandés"
2. ✅ Vérifier 3-5 produits affichés
3. ✅ Voir score de matching (0-100)
4. ✅ Voir raisons de recommandation
5. ❌ **BUG POTENTIEL**: Aucun produit ou produits non pertinents

#### Live Shopping
1. ✅ Voir "Événements Live à venir"
2. ✅ Vérifier liste
3. ❌ **BUG POTENTIEL**: Erreur chargement

#### Swipe Matching (Tinder-style)
1. ✅ Voir campagnes suggérées
2. ✅ Swiper droite (accepter)
3. ✅ Swiper gauche (refuser)
4. ❌ **BUG POTENTIEL**: Cartes ne se chargent pas

---

### SESSION 3: DASHBOARD COMMERCIAL

#### Login Commercial
1. ✅ Se connecter avec compte commercial
2. ✅ Vérifier Dashboard Commercial

#### Pipeline de Ventes
1. ✅ Voir pipeline (prospect → négociation → closing → gagné/perdu)
2. ✅ Vérifier montants par stage
3. ❌ **BUG POTENTIEL**: Pipeline vide ou erreur

#### Gestion Leads
1. ✅ Voir liste leads
2. ✅ Cliquer "Ajouter Lead"
3. ✅ Remplir (nom, email, téléphone, température: hot/warm/cold)
4. ✅ Sauvegarder
5. ❌ **BUG POTENTIEL**: Lead ne s'ajoute pas ou erreur
6. ❌ **BUG POTENTIEL**: Message erreur pas user-friendly (code API brut)

#### Tracking Links
1. ✅ Voir liens trackés
2. ✅ Cliquer "Créer lien"
3. ✅ Entrer URL et nom
4. ✅ Générer
5. ✅ Vérifier code unique généré
6. ❌ **BUG POTENTIEL**: Erreur si limite atteinte (plan Starter: 3 liens max)

#### Templates Emails
1. ✅ Voir bibliothèque templates
2. ✅ Ouvrir un template
3. ✅ Essayer de modifier
4. ❌ **BUG POTENTIEL**: Templates non chargeables

#### Performance Charts
1. ✅ Voir graphique performance (30/60/90 jours)
2. ✅ Changer période
3. ❌ **BUG POTENTIEL**: Graphique ne se met pas à jour

#### Quota Mensuel
1. ✅ Voir barre progression quota
2. ✅ Vérifier pourcentage
3. ❌ **BUG POTENTIEL**: Calcul incorrect

#### Tasks
1. ✅ Voir liste tâches
2. ✅ Cocher une tâche terminée
3. ❌ **BUG POTENTIEL**: Tâche ne se marque pas comme terminée

#### Leaderboard
1. ✅ Voir classement équipe
2. ✅ Voir votre position
3. ❌ **BUG POTENTIEL**: Positions incorrectes

---

### SESSION 4: DASHBOARD MERCHANT

#### Login Merchant
1. ✅ Se connecter avec compte merchant
2. ✅ Vérifier Dashboard Merchant

#### Catalogue Produits
1. ✅ Voir liste produits
2. ✅ Ajouter produit
3. ❌ **BUG POTENTIEL**: **CRITIQUE - RÉCURSION INFINIE** si plan inconnu (déjà corrigé dans le code)

#### Réseau Affiliés
1. ✅ Voir affiliés actifs
2. ✅ Inviter influencer
3. ❌ **BUG POTENTIEL**: Invitation non envoyée

#### Création Campagne
1. ✅ Cliquer "Créer campagne"
2. ✅ Remplir (nom, budget, objectif, dates)
3. ✅ Sauvegarder
4. ❌ **BUG POTENTIEL**: Vérifier limitations par plan (Freemium: 1, Standard: 5, Premium: 20, Enterprise: illimité)

#### Collaborations
1. ✅ Voir demandes collaboration reçues
2. ✅ Accepter/Rejeter
3. ✅ Essayer counter-offer
4. ❌ **BUG POTENTIEL**: Counter-offer ne s'envoie pas

#### ROI Calculator
1. ✅ Ouvrir calculateur
2. ✅ Entrer budget (ex: 1000€)
3. ✅ Entrer panier moyen (ex: 50€)
4. ✅ Sélectionner industrie (fashion, beauty, tech, etc.)
5. ✅ Sélectionner type campagne (influencer, ads, email)
6. ✅ Calculer
7. ✅ Vérifier résultats (clics estimés, conversions, ROI %)
8. ❌ **BUG POTENTIEL**: Résultats incohérents ou négatifs

#### Analytics Pro
1. ✅ Voir analytics avancées (uniquement Premium+)
2. ✅ Vérifier graphiques
3. ❌ **BUG POTENTIEL**: Fonctionnalité lockée mais accessible

#### Matching System
1. ✅ Trouver influenceurs (uniquement Enterprise)
2. ❌ **BUG POTENTIEL**: Système pas fonctionnel

#### Parrainage
1. ✅ Voir programme parrainage (uniquement Premium+)
2. ❌ **BUG POTENTIEL**: Stats erronnées

#### Live Shopping
1. ✅ Planifier événement live (uniquement Enterprise)
2. ❌ **BUG POTENTIEL**: Planification échoue

---

### SESSION 5: FONCTIONNALITÉS SPÉCIALES

#### Content Studio

##### QR Code Generation
1. ✅ Aller sur Content Studio
2. ✅ Cliquer "Générer QR Code"
3. ✅ Entrer URL (ex: produit)
4. ✅ Sélectionner style (modern, classic, gradient)
5. ✅ Générer
6. ✅ Télécharger QR code
7. ❌ **BUG POTENTIEL**: QR code ne se génère pas ou erreur

##### Watermark
1. ✅ Upload image ou sélectionner depuis bibliothèque
2. ✅ Cliquer "Ajouter Watermark"
3. ✅ Entrer texte (ex: @username)
4. ✅ Sélectionner position (top-left, bottom-right, etc.)
5. ✅ Ajuster opacité
6. ✅ Appliquer
7. ✅ Télécharger image watermarkée
8. ❌ **BUG POTENTIEL**: **DÉJÀ CORRIGÉ** - Watermark s'applique vraiment maintenant (pas juste rename)

##### Post Scheduling
1. ✅ Composer post
2. ✅ Upload image
3. ✅ Sélectionner plateformes (Instagram, Facebook, TikTok, LinkedIn)
4. ✅ Choisir date/heure
5. ✅ Planifier
6. ❌ **BUG POTENTIEL**: Post ne se sauvegarde pas en BDD
7. ❌ **BUG POTENTIEL**: Aucun cron job pour publier (TODO dans le code)

##### A/B Testing
1. ✅ Créer 2 variantes (A et B)
2. ✅ Lancer test
3. ✅ Attendre résultats (ou simuler avec données existantes)
4. ✅ Voir métriques (impressions, clics, conversions, CTR, CR)
5. ✅ Voir gagnant
6. ❌ **BUG POTENTIEL**: **DÉJÀ CORRIGÉ** - Métriques viennent de la BDD maintenant (pas mock)

#### Live Shopping

##### Créer Session Live
1. ✅ Aller sur Live Shopping
2. ✅ Cliquer "Créer Session Live"
3. ✅ Sélectionner plateforme (Instagram, TikTok, YouTube, Facebook)
4. ✅ Entrer titre et description
5. ✅ Sélectionner produits à présenter
6. ✅ Choisir date/heure
7. ✅ Créer
8. ❌ **BUG POTENTIEL**: Session crée en BDD mais API externe (Instagram, etc.) en mode DEMO si pas de tokens configurés

##### Pendant le Live
1. ✅ Voir viewers en temps réel
2. ✅ Voir commandes en direct
3. ✅ Boost commission (+5% automatique)
4. ❌ **BUG POTENTIEL**: Stats temps réel pas à jour

##### Après le Live
1. ✅ Voir statistiques finales
2. ✅ Voir total viewers, peak viewers, orders, commissions
3. ❌ **BUG POTENTIEL**: Stats incohérentes

---

## 🐛 BUGS DÉJÀ CORRIGÉS (À VÉRIFIER)

### ✅ BUG #1: Récursion Infinie MerchantDashboard
**Fichier**: `frontend/src/pages/dashboards/MerchantDashboard.js`
**Lignes**: 110, 145
**Fix**: Retourne valeurs par défaut au lieu de s'appeler récursivement
**Test**: Se connecter merchant avec plan inconnu → devrait afficher Freemium par défaut (pas crash)

### ✅ BUG #2: Watermark Fake
**Fichier**: `backend/content_studio_endpoints.py`
**Fix**: Applique vraie watermark avec PIL
**Test**: Uploader image, appliquer watermark → devrait voir le watermark réellement appliqué

### ✅ BUG #3: A/B Testing Mock Data
**Fichier**: `backend/services/content_studio_service.py`
**Fix**: Query BDD `scheduled_posts` pour vraies métriques
**Test**: Lancer A/B test → devrait voir données réelles (ou zeros si pas de posts schedulés)

---

## 📊 CHECKLIST RAPIDE

### APIs à Tester en Priorité

```bash
# Dashboard Admin
GET /api/analytics/overview
GET /api/admin/users
GET /api/admin/products
GET /api/admin/analytics

# Dashboard Influencer
GET /api/analytics/influencer/overview
GET /api/affiliate-links
GET /api/referrals/dashboard/{userId}
GET /api/ai/product-recommendations/{userId}
POST /api/payouts/request

# Dashboard Commercial
GET /api/commercial/stats
GET /api/commercial/leads
GET /api/commercial/pipeline
POST /api/commercial/leads
POST /api/commercial/tracking-links

# Dashboard Merchant
GET /api/marketplace/products
GET /api/analytics/merchant/sales-chart
POST /api/products

# Content Studio
POST /api/content-studio/generate-qr-code
POST /api/content-studio/add-watermark
POST /api/content-studio/schedule-post
POST /api/content-studio/ab-test/analyze

# Live Shopping
POST /api/live-shopping/create-session
GET /api/live-shopping/sessions

# ROI Calculator
POST /api/roi/calculate

# Parrainage
POST /api/referrals/generate-code
GET /api/referrals/stats
```

---

## 📝 FORMAT DE RAPPORT DE BUG

Pour chaque bug trouvé, noter :

```
BUG #X: [Titre court]
----------------------------------------
URL: https://shareyoursales.vercel.app/...
Page: Dashboard Admin / Onglet Users
Action: Cliquer "Ajouter utilisateur"
Résultat Attendu: Modal s'ouvre avec formulaire
Résultat Obtenu: Erreur 500 / Message "undefined" / Rien ne se passe
Console Erreur: [copier erreur depuis F12 Console]
Network Erreur: [copier erreur depuis F12 Network]
Capture d'écran: [si possible]
----------------------------------------
```

---

## ⚡ TESTS CRITIQUES (À FAIRE EN PREMIER)

1. ✅ Login admin fonctionne
2. ✅ Dashboard Admin s'affiche sans erreur
3. ✅ Peut créer un produit
4. ✅ Peut créer un utilisateur
5. ✅ Génération QR Code fonctionne
6. ✅ Watermark s'applique réellement
7. ✅ ROI Calculator donne résultats cohérents
8. ✅ Liens d'affiliation se génèrent
9. ✅ Demande paiement influencer fonctionne
10. ✅ Parrainage affiche stats

---

**IMPORTANT**: Tester sur navigateur avec F12 ouvert (Console + Network) pour capturer TOUTES les erreurs !
