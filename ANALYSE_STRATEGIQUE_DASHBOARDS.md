# 🎯 ANALYSE STRATÉGIQUE COMPLÈTE DES DASHBOARDS

## Date: 28 Novembre 2025

---

## 📊 STRUCTURE DES ABONNEMENTS PAR RÔLE

### 1. MERCHANT (Annonceur/Marchand)

| Plan | Prix | Produits | Campagnes | Affiliés | Features |
|------|------|----------|-----------|----------|----------|
| **Freemium** | 0€ | 5 | 1 | 10 | Stats basiques |
| **Standard** | 49€/mois | 20 | 5 | 50 | Analytics avancés |
| **Premium** | 149€/mois | Illimité | Illimité | 200 | Analytics Pro, Referral |
| **Enterprise** | 499€/mois | Illimité | Illimité | Illimité | Matching, Live Shopping, API |

### 2. INFLUENCER (Influenceur)

| Plan | Prix | Commission | Campagnes | Features |
|------|------|------------|-----------|----------|
| **Free** | 0€ | 5% fee | 5 | Stats basiques, Marketplace |
| **Pro** | 29€/mois | 3% fee | 20 | Analytics Pro, Payout Instant |
| **Elite** | 99€/mois | 0% fee | Illimité | Matching IA, Marketing IA, Live Shopping |

### 3. COMMERCIAL (Apporteur d'affaires)

| Plan | Prix | Leads/mois | Liens trackés | Features |
|------|------|------------|---------------|----------|
| **Starter** | 0€ | 10 | 3 | Stats basiques, 3 templates |
| **Pro** | 29€/mois | Illimité | Illimité | CRM avancé, 15 templates, Kit marketing |
| **Enterprise** | 99€/mois | Illimité | Illimité | IA, Automation, Générateur devis |

---

## 🔴 PROBLÈMES IDENTIFIÉS PAR DASHBOARD

### MERCHANT DASHBOARD - `MerchantDashboard.js`

#### ✅ CE QUI FONCTIONNE
- [x] Récupération des stats via `/api/analytics/merchant/performance`
- [x] Récupération des produits via `/api/marketplace/products`
- [x] Récupération des ventes via `/api/analytics/merchant/sales-chart`
- [x] Récupération abonnement via `/api/subscriptions/current`
- [x] Fonction `checkAccess()` pour gater les fonctionnalités

#### ❌ PROBLÈMES
1. **ROI calculé localement** - Estimation fixe au lieu de données réelles
2. **Trends hardcodés** - Pas de vraies tendances vs mois dernier
3. **Referral data** - Appel API mais peut échouer silencieusement

#### 📝 CORRECTIONS NÉCESSAIRES
- Ajouter endpoint pour calcul ROI réel
- Calculer les tendances côté backend

---

### INFLUENCER DASHBOARD - `InfluencerDashboard.js`

#### ✅ CE QUI FONCTIONNE
- [x] Récupération stats via `/api/analytics/influencer/overview`
- [x] Récupération liens via `/api/affiliate-links`
- [x] Récupération abonnement via `/api/subscriptions/current`
- [x] Fonction `checkAccess()` présente
- [x] Mode Matching avec vraies données API (CORRIGÉ)

#### ❌ PROBLÈMES RESTANTS
1. **Gains ce Mois** - Utilise `stats?.total_earnings * 0.25` (ESTIMATION)
2. **Trends** - "+X% vs mois dernier" peut être hardcodé
3. **Certains appels API peuvent échouer** - `/api/referrals/dashboard/`, `/api/ai/...`

#### 📝 CORRECTIONS NÉCESSAIRES
- Créer endpoint `/api/analytics/influencer/monthly-earnings`
- Retourner les vraies tendances depuis le backend

---

### COMMERCIAL DASHBOARD - `CommercialDashboard.js`

#### ✅ CE QUI FONCTIONNE
- [x] Récupération stats via `/api/commercial/stats`
- [x] Récupération leads via `/api/commercial/leads`
- [x] Récupération liens via `/api/commercial/tracking-links`
- [x] Récupération templates via `/api/commercial/templates`
- [x] Gating par `subscriptionTier` (starter/pro/enterprise)

#### ❌ PROBLÈMES
1. **Récupère tier depuis localStorage** au lieu de l'API
2. **Pas de Promise.allSettled** - Si un appel échoue, tout échoue
3. **Funnel data** - Dépend entièrement de `/api/commercial/analytics/funnel`

#### 📝 CORRECTIONS NÉCESSAIRES
- Utiliser `/api/subscriptions/current` au lieu de localStorage
- Ajouter Promise.allSettled pour robustesse
- Ajouter fallback si endpoints échouent

---

### ADMIN DASHBOARD - `AdminDashboard.js`

#### ✅ CE QUI FONCTIONNE
- [x] Récupération overview via `/api/analytics/overview`
- [x] Récupération merchants/influencers
- [x] Charts revenue et categories
- [x] Promise.allSettled utilisé

#### ❌ PROBLÈMES
1. **Trends mockés** - `user_growth_rate: 12.5`, `conversion_trend: 5.2`
2. **Export PDF basique** - Génère un fichier .txt, pas un vrai PDF

#### 📝 CORRECTIONS NÉCESSAIRES
- Calculer les vraies tendances côté backend
- Améliorer l'export (optionnel)

---

## 🛠️ PLAN D'ACTION IMMÉDIAT

### PRIORITÉ 1 - FIXES CRITIQUES

1. **CommercialDashboard** - Utiliser API pour subscription tier
2. **Tous dashboards** - Retirer les trends hardcodés
3. **Backend** - Créer endpoints manquants pour tendances

### PRIORITÉ 2 - AMÉLIORATIONS

1. Ajouter skeleton loaders uniformes
2. Améliorer gestion d'erreurs avec messages clairs
3. Ajouter cache pour éviter re-fetch excessifs

### PRIORITÉ 3 - FEATURES

1. Export PDF/Excel fonctionnel
2. Notifications temps réel
3. Widget gamification complet

---

## 📋 MATRICE FONCTIONNALITÉS / PLANS

### MERCHANT

| Fonctionnalité | Freemium | Standard | Premium | Enterprise |
|----------------|----------|----------|---------|------------|
| Dashboard Base | ✅ | ✅ | ✅ | ✅ |
| Stats Ventes | ✅ | ✅ | ✅ | ✅ |
| Gestion Produits | 5 max | 20 max | ♾️ | ♾️ |
| Campagnes | 1 max | 5 max | ♾️ | ♾️ |
| Analytics Pro | ❌ | ❌ | ✅ | ✅ |
| Referral Program | ❌ | ❌ | ✅ | ✅ |
| Matching Tinder | ❌ | ❌ | ❌ | ✅ |
| Live Shopping | ❌ | ❌ | ❌ | ✅ |

### INFLUENCER

| Fonctionnalité | Free | Pro | Elite |
|----------------|------|-----|-------|
| Dashboard Base | ✅ | ✅ | ✅ |
| Marketplace | ✅ | ✅ | ✅ |
| Stats Gains | ✅ | ✅ | ✅ |
| Paiement Mobile | ✅ | ✅ | ✅ |
| Payout Instant | ❌ | ✅ | ✅ |
| Analytics Pro | ❌ | ✅ | ✅ |
| Matching Swipe | ❌ | ❌ | ✅ |
| IA Marketing | ❌ | ❌ | ✅ |

### COMMERCIAL

| Fonctionnalité | Starter | Pro | Enterprise |
|----------------|---------|-----|------------|
| Dashboard Base | ✅ | ✅ | ✅ |
| Stats Leads | ✅ | ✅ | ✅ |
| Liens Trackés | 3 max | ♾️ | ♾️ |
| Leads/mois | 10 | ♾️ | ♾️ |
| CRM Avancé | ❌ | ✅ | ✅ |
| Templates | 3 | 15 | ♾️ |
| Pipeline Funnel | ❌ | ✅ | ✅ |
| Générateur Devis | ❌ | ❌ | ✅ |
| IA Suggestions | ❌ | ❌ | ✅ |

---

## ✅ CHECKLIST DE VALIDATION

- [ ] Tous les dashboards chargent sans erreur 500
- [ ] Toutes les données viennent de l'API (pas de mock)
- [ ] Les fonctionnalités sont correctement gatées par plan
- [ ] Les skeleton loaders s'affichent pendant le chargement
- [ ] Les erreurs affichent des messages utilisateur-friendly
- [ ] Le design est cohérent entre les dashboards
- [ ] Les graphiques s'affichent même sans données (empty state)

