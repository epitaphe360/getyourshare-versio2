# 📐 Architecture ShareYourSales - Documentation Complète

> **Version:** 2.0
> **Dernière mise à jour:** 4 Janvier 2026
> **Statut:** Production-Ready

---

## 🎯 Vue d'Ensemble

ShareYourSales est une plateforme SaaS complète de marketing d'affiliation avec 4 rôles principaux :
- **Admin** - Gestion complète de la plateforme
- **Merchant** - Commerçants créant des campagnes
- **Influencer** - Créateurs de contenu promouvant des produits
- **Commercial** - Représentants commerciaux générant des leads

---

## 📊 Statistiques du Projet

| Métrique | Valeur |
|----------|--------|
| **Pages totales** | 160+ composants |
| **Routes actives** | 139 routes |
| **Dashboards actifs** | 17 dashboards |
| **Services backend** | 22+ services |
| **API Endpoints** | 150+ endpoints |

---

## 🗂️ Structure des Dossiers

```
/frontend/src/
├── /pages/                     # Pages principales (160+ fichiers)
│   ├── /admin/                 # Pages admin (17 fichiers)
│   ├── /dashboards/            # Dashboards par rôle (12 fichiers)
│   ├── /campaigns/             # Gestion campagnes (6 fichiers)
│   ├── /products/              # Gestion produits (2 fichiers)
│   ├── /services/              # Gestion services (3 fichiers)
│   ├── /influencers/           # Gestion influenceurs (3 fichiers)
│   ├── /merchants/             # Gestion marchands (5 fichiers)
│   ├── /affiliates/            # Système affiliés (6 fichiers)
│   ├── /settings/              # Paramètres (15 fichiers)
│   ├── /fiscal/                # Module fiscal (3 fichiers)
│   ├── /invoices/              # Facturation (2 fichiers)
│   ├── /commercial/            # Pages commercial (4 fichiers)
│   ├── /subscription/          # Abonnements (5 fichiers)
│   ├── /company/               # Gestion entreprise (3 fichiers)
│   ├── /performance/           # Analytics (4 fichiers)
│   ├── /logs/                  # Logs & audit (4 fichiers)
│   ├── /marketplace/           # Marketplace (1 fichier)
│   ├── /integrations/          # Hub intégrations (1 fichier)
│   ├── /reports/               # Rapports avancés (1 fichier)
│   ├── /email/                 # Campagnes email (1 fichier)
│   ├── /api/                   # Documentation API (1 fichier)
│   ├── /crm/                   # CRM Dashboard (1 fichier)
│   ├── /inventory/             # Gestion stock (1 fichier)
│   ├── /marketing/             # Marketing automation (1 fichier)
│   └── [Root Pages]            # Auth, Homepage, Public (43 fichiers)
│
├── /components/                # Composants réutilisables
│   ├── /layout/                # Layout & Navigation (9 fichiers)
│   ├── /dashboard/             # Composants dashboard
│   ├── /mobile/                # Vues mobiles
│   ├── /bot/                   # Chatbot widget
│   ├── /social/                # Boutons sociaux
│   └── /common/                # Composants communs
│
├── /context/                   # React Context (Auth, Toast, Currency, etc.)
├── /i18n/                      # Internationalisation (FR/EN/AR)
├── /utils/                     # Utilitaires & helpers
└── /hooks/                     # Custom React hooks

/backend/
├── /services/                  # Services métier (22+ fichiers)
│   ├── email_notification_service.py
│   ├── push_notification_service.py
│   ├── sms_notification_service.py
│   ├── instagram_api_service.py
│   ├── tiktok_api_service.py
│   ├── facebook_graph_api_service.py
│   ├── twitter_api_service.py
│   ├── shopify_integration_service.py
│   ├── woocommerce_integration_service.py
│   ├── prestashop_integration_service.py
│   ├── ai_recommendation_service.py
│   ├── rfm_segmentation_service.py
│   ├── ab_testing_service.py
│   ├── kyc_verification_service.py
│   ├── ocr_document_service.py
│   └── ...
│
├── integrated_services.py      # API Integration Layer (NOUVEAU)
├── server.py                   # FastAPI main server
└── [Other endpoints]           # Endpoints spécialisés
```

---

## 🚀 Dashboards Actifs

### Par Rôle

#### 1. **Dashboard Principal** (`/pages/Dashboard.js`)
- Point d'entrée unique
- Routage automatique vers le dashboard du rôle
- Redirection intelligente

#### 2. **Admin Dashboard** (`/pages/dashboards/AdminDashboardComplete.jsx`)
- Vue d'ensemble complète de la plateforme
- Métriques en temps réel
- Gestion utilisateurs, marchands, campagnes
- Accès à tous les outils admin

#### 3. **Merchant Dashboard** (`/pages/dashboards/MerchantDashboard.js`)
- Vue commerçant
- Gestion produits & campagnes
- Suivi affiliés & conversions
- Analytics de ventes

#### 4. **Influencer Dashboard** (`/pages/dashboards/InfluencerDashboard.js`)
- Vue influenceur
- Mes campagnes actives
- Liens de tracking
- Revenus & conversions

#### 5. **Commercial Dashboard** (`/pages/dashboards/CommercialDashboard.js`)
- Vue représentant commercial
- Gestion leads & prospects
- Suivi commissions
- Pipeline de ventes

### Dashboards Spécialisés

#### 6. **Campaign Dashboard** (`/pages/campaigns/CampaignDashboard.js`)
- Gestion complète des campagnes
- Création & édition
- Analytics par campagne

#### 7. **Admin Social Dashboard** (`/pages/admin/AdminSocialDashboard.js`)
- Métriques réseaux sociaux
- Engagement & reach
- Planification posts

#### 8. **Analytics Dashboard** (`/pages/admin/AnalyticsDashboard.jsx`)
- Rapports avancés
- Visualisations de données
- Export de données

#### 9. **Moderation Dashboard** (`/pages/admin/ModerationDashboard.js`)
- Modération IA automatique
- File d'attente de modération
- Règles de modération

#### 10. **Advanced Analytics Dashboard** (`/pages/AdvancedAnalyticsDashboard.jsx`)
- BI & Intelligence d'affaires
- Prédictions IA
- Segmentation avancée

#### 11. **Mobile Dashboard** (`/components/mobile/MobileDashboard.jsx`)
- Vue mobile optimisée
- Navigation simplifiée
- Accès rapide aux actions

### Dashboards Premium SaaS

#### 12. **Inventory Dashboard** (`/pages/inventory/InventoryDashboard.jsx`)
- Gestion stock en temps réel
- Alertes de stock
- Prévisions de réapprovisionnement

#### 13. **Marketing Dashboard** (`/pages/marketing/MarketingDashboard.jsx`)
- Automation marketing
- Campagnes multi-canaux
- ROI & Attribution

#### 14. **CRM Dashboard** (`/pages/crm/CRMDashboard.jsx`)
- Gestion relation client
- Pipeline commercial
- Automation CRM

### Dashboards Fiscaux

#### 15. **Tax Dashboard** (`/pages/fiscal/TaxDashboard.js`)
- Module fiscal MA/FR/US
- Calcul TVA automatique
- Déclarations fiscales
- Export comptable

#### 16. **Subscription Dashboard** (`/pages/company/SubscriptionDashboard.js`)
- Gestion abonnement utilisateur
- Facturation
- Historique paiements

#### 17. **Company Links Dashboard** (`/pages/company/CompanyLinksDashboard.js`)
- Liens de tracking entreprise
- Statistiques de clics
- Attribution de conversions

---

## 🗺️ Routing - Organisation Complète

### Public Routes (19 routes)
```
/                           → HomepageV2
/login                      → Login
/register                   → Register
/pricing                    → Pricing
/marketplace               → MarketplaceGroupon (Public)
/marketplace/product/:id   → ProductDetail
/contact                   → Contact
/about                     → About
/privacy                   → Privacy
/terms                     → Terms
/legal                     → Legal
/roi-calculator            → ROICalculator
```

### Core Dashboard Routes (6 routes)
```
/dashboard                 → Dashboard (Role Routing Hub)
/dashboard/admin           → AdminDashboard [Admin Only]
/dashboard/merchant        → MerchantDashboard [Merchant + Admin]
/dashboard/influencer      → InfluencerDashboard [Influencer + Admin]
/dashboard/commercial      → CommercialDashboard [Commercial + Admin]
/getting-started           → GettingStarted
```

### Merchant Routes (16 routes)
```
/products                  → ProductsListPage [Merchant + Admin]
/products/create           → CreateProductPage
/products/:id/edit         → CreateProductPage (Edit Mode)

/services                  → ServicesListPage [Merchant + Admin]
/services/create           → CreateServicePage
/services/:id              → ServiceDetailPage
/services/:id/edit         → CreateServicePage (Edit Mode)

/campaigns                 → CampaignDashboard
/campaigns/list            → CampaignsList
/campaigns/create          → CreateCampaignPage [Merchant + Admin]
/campaigns/:id             → CampaignDetailEnhanced

/merchants                 → MerchantsList [Admin Only]
```

### Influencer Routes (9 routes)
```
/influencers               → InfluencersList [Merchant + Admin]
/influencers/search        → InfluencerSearchPage
/influencers/:id           → InfluencerProfilePage
/my-links                  → MyLinks (Tracking Links)
/tracking-links            → TrackingLinks
```

### Affiliate Routes (6 routes)
```
/affiliates                → AffiliatesList [Merchant + Admin]
/affiliates/applications   → AffiliateApplications
/affiliates/payouts        → AffiliatePayouts
/affiliates/coupons        → AffiliateCoupons
/affiliates/lost-orders    → LostOrders [Admin Only]
/affiliates/balance-report → BalanceReport [Admin Only]
```

### Performance & Analytics Routes (4 routes)
```
/performance/conversions        → Conversions
/performance/reports           → Reports
/performance/leads             → Leads [Admin Only]
/performance/mlm-commissions   → MLMCommissions [Merchant + Admin]
```

### Logs & Tracking Routes (4 routes)
```
/logs/clicks               → Clicks [Merchant + Admin]
/logs/postback             → Postback [Merchant + Admin]
/logs/audit                → Audit [Admin Only]
/logs/webhooks             → Webhooks [Admin Only]
```

### Admin Routes (13 routes)
```
/admin/social-dashboard         → AdminSocialDashboard
/admin/users                    → UserManagement
/admin/registration-requests    → RegistrationManagement
/admin/merchants                → MerchantManagement
/admin/analytics                → AnalyticsDashboard ✅ AJOUTÉ
/admin/leads                    → LeadManagement
/admin/moderation               → ModerationDashboard
/admin/products                 → AdminProductsManager
/admin/services                 → ServiceManagement
/admin/subscriptions            → AdminSubscriptionsManager
/admin/subscriptions/analytics  → AdminSubscriptionsAnalytics
/admin/coupons                  → AdminCoupons
```

### Settings Routes (15 routes)
```
/settings/personal             → PersonalSettings
/settings/security             → SecuritySettings
/settings/company              → CompanySettings [Merchant + Admin]
/settings/platform             → PlatformSettings [Admin Only]
/settings/advanced             → AdvancedPlatformSettings [Admin] ✅ AJOUTÉ
/settings/affiliates           → AffiliateSettings [Merchant + Admin]
/settings/registration         → RegistrationSettings [Admin Only]
/settings/mlm                  → MLMSettings [Admin Only]
/settings/traffic-sources      → TrafficSources [Admin Only]
/settings/permissions          → Permissions [Admin Only]
/settings/users                → Users [Admin Only]
/settings/smtp                 → SMTP [Merchant + Admin]
/settings/emails               → Emails [Merchant + Admin]
/settings/white-label          → WhiteLabel [Admin Only]
```

### Fiscal/Invoice Routes (12 routes)
```
/fiscal/admin                  → TaxDashboard [Admin]
/fiscal/merchant               → TaxDashboard [Merchant + Admin]
/fiscal/influencer             → TaxDashboard [Influencer + Admin]
/fiscal/commercial             → TaxDashboard [Commercial + Admin]
/fiscal/invoice/new            → InvoiceGenerator [Merchant + Admin]
/fiscal/vat/calculator         → TaxDashboard (VAT Calc)
/fiscal/vat/declare            → TaxDashboard (VAT Declare)
/fiscal/accounting/export      → TaxDashboard (Export)
/fiscal/settings               → TaxSettings

/invoices/influencers          → InfluencerInvoicesPage [Merchant + Admin]
/invoices/commercials          → CommercialInvoicesPage [Commercial + Admin]
```

### Advanced Features Routes (9 routes)
```
/reports/advanced              → ReportsAdvanced ✅ AJOUTÉ
/integrations                  → IntegrationsHub [Admin + Merchant]
/services-integres             → IntegratedServices [Admin + Merchant] ✅ AJOUTÉ
/email/campaigns               → EmailCampaigns ✅ AJOUTÉ
/api/docs                      → APIDocs ✅ AJOUTÉ
/analytics-pro                 → AdvancedAnalyticsDashboard
/matching                      → InfluencerMatchingPage [Merchant + Admin]
/mobile-dashboard              → MobileDashboard
/features                      → FeaturesHub
```

### Subscription Routes (5 routes)
```
/subscription                  → SubscriptionDashboard
/subscription/manage           → SubscriptionManagement
/subscription/plans            → SubscriptionPlans
/subscription/billing          → BillingHistory
/subscription/cancel           → CancelSubscription
/subscription/cancelled        → SubscriptionCancelled
```

### Premium SaaS Routes (3 routes)
```
/inventory                     → InventoryDashboard [Merchant + Admin]
/marketing                     → MarketingDashboard [Merchant + Admin]
/crm                          → CRMDashboard [Commercial + Admin]
```

### Messaging & Communication (2 routes)
```
/messages                      → MessagingPage
/messages/:conversationId      → MessagingPage (Conversation)
```

### Company Management (2 routes)
```
/team                         → TeamManagement [Merchant + Admin]
/company-links                → CompanyLinksDashboard [Merchant + Admin]
```

---

## 🔐 Contrôle d'Accès par Rôle

### Admin (Accès Complet)
- ✅ Tous les dashboards
- ✅ Tous les outils de gestion
- ✅ Configuration système
- ✅ Analytics avancés
- ✅ Gestion utilisateurs
- **Routes:** ~80+ routes accessibles

### Merchant
- ✅ Dashboard merchant
- ✅ Gestion produits & services
- ✅ Gestion campagnes
- ✅ Gestion affiliés
- ✅ Analytics & rapports
- ✅ Fiscal & facturation
- ✅ Services intégrés (Email, SMS, Social)
- **Routes:** ~50 routes accessibles

### Influencer
- ✅ Dashboard influencer
- ✅ Mes liens de tracking
- ✅ Mes campagnes
- ✅ Performance & conversions
- ✅ Marketplace (navigation)
- ✅ Fiscal personnel
- **Routes:** ~25 routes accessibles

### Commercial
- ✅ Dashboard commercial
- ✅ Gestion leads
- ✅ Tracking & commissions
- ✅ CRM
- ✅ Performance
- ✅ Fiscal & factures
- **Routes:** ~20 routes accessibles

---

## 🎨 Navigation - Sidebar Menu

### Admin Menu (13 sections, ~50 items)
```
✅ Dashboard
✅ Messages
✅ Modération & Support

GESTION MARCHANDS
  ├─ Marchands
  │  ├─ Liste marchands
  │  └─ Demandes inscription
  └─ Campagnes/Offres

CATALOGUE PRODUITS & SERVICES
  ├─ Produits
  ├─ Services
  ├─ Marketplace
  └─ Modération IA

PERFORMANCE & ANALYTICS
  └─ Performance
     ├─ Conversions
     ├─ Commissions MLM
     ├─ Leads
     └─ Rapports

GESTION AFFILIÉS
  └─ Affiliés
     ├─ Liste
     ├─ Demandes
     ├─ Paiements
     ├─ Coupons
     ├─ Commandes Perdues
     └─ Rapport de Solde

SYSTÈME & OUTILS
  ├─ Logs
  │  ├─ Clics
  │  ├─ Postback
  │  ├─ Audit
  │  └─ Webhooks
  ├─ Tracking Links
  ├─ Intégrations
  ├─ Services Intégrés ✅ NOUVEAU
  ├─ Analytics Dashboard ✅ NOUVEAU
  ├─ Rapports Avancés ✅ NOUVEAU
  ├─ Campagnes Email ✅ NOUVEAU
  ├─ API Documentation ✅ NOUVEAU
  └─ Abonnements Plateforme

FISCALITÉ (MA/FR/US)
  └─ Fiscalité & Compta
     ├─ Dashboard Fiscal
     ├─ Facturation
     ├─ Nouvelles Factures
     ├─ Calculateur TVA
     ├─ Déclaration TVA
     ├─ Export Comptable
     ├─ Factures Influenceurs
     ├─ Factures Commerciaux
     └─ Paramètres Fiscaux

CONFIGURATION
  └─ Paramètres
     ├─ Personnel
     ├─ Sécurité
     ├─ Entreprise
     ├─ Plateforme
     ├─ Paramètres Avancés ✅ NOUVEAU
     ├─ Affiliés
     ├─ Inscription
     ├─ MLM
     ├─ Sources de Trafic
     ├─ Permissions
     ├─ Utilisateurs
     ├─ SMTP
     ├─ Emails
     └─ White Label
```

### Merchant Menu (11 items + sous-menus)
```
✅ Getting Started
✅ Dashboard
✅ Messages
✅ Mes Produits
✅ Services
✅ Mes Campagnes
✅ Mes Affiliés (4 sous-items)
✅ Performance (3 sous-items)
✅ Tracking (2 sous-items)
✅ Services Intégrés ✅ NOUVEAU
✅ Intégrations ✅ NOUVEAU
✅ Abonnement
✅ Fiscal (7 sous-items)
✅ Paramètres (6 sous-items)
```

### Influencer Menu (10 items)
```
✅ Getting Started
✅ Dashboard
✅ Messages
✅ Marketplace
✅ Mes Campagnes
✅ Mes Liens
✅ Performance (2 sous-items)
✅ Abonnement
✅ Fiscal (4 sous-items)
✅ Paramètres (2 sous-items)
```

### Commercial Menu (10 items)
```
✅ Getting Started
✅ Dashboard
✅ Messages
✅ Marketplace
✅ Mes Campagnes
✅ Tracking & Commissions
✅ Performance (2 sous-items)
✅ Abonnement
✅ Fiscal (2 sous-items)
✅ Paramètres (2 sous-items)
```

---

## 🔌 Backend Services - API Layer

### Services Intégrés (`/backend/integrated_services.py`)

#### Notifications
```python
POST /api/integrated/notifications/email
POST /api/integrated/notifications/push
POST /api/integrated/notifications/sms
```

#### Social Media
```python
POST /api/integrated/social/post
GET  /api/integrated/social/insights/{platform}/{account_id}
```

#### E-commerce
```python
POST /api/integrated/ecommerce/discount-code
GET  /api/integrated/ecommerce/orders/{platform}/{order_id}
POST /api/integrated/ecommerce/sync-products
```

#### AI & Analytics
```python
POST /api/integrated/ai/recommendations
GET  /api/integrated/ai/customer-segments/{user_id}
POST /api/integrated/ai/ab-test
GET  /api/integrated/ai/ab-test/{test_id}/results
```

#### KYC & Verification
```python
POST /api/integrated/kyc/verify
POST /api/integrated/kyc/ocr-document
GET  /api/integrated/kyc/status/{verification_id}
```

#### Dashboard
```python
GET  /api/integrated/dashboard/services-status
```

---

## 📝 Conventions de Code

### Noms de Fichiers
- **Composants React:** `PascalCase.jsx`
- **Services Backend:** `snake_case.py`
- **Pages:** `PascalCase.jsx` ou `PascalCase.js`
- **Utilitaires:** `camelCase.js`

### Structure Composants React
```jsx
// 1. Imports
import React, { useState } from 'react';

// 2. Component Definition
const ComponentName = () => {
  // 3. Hooks
  const [state, setState] = useState();

  // 4. Handlers
  const handleAction = () => {};

  // 5. Render
  return <div>Content</div>;
};

// 6. Export
export default ComponentName;
```

### Routes Pattern
```jsx
<Route
  path="/feature"
  element={
    <RoleProtectedRoute allowedRoles={['admin', 'merchant']}>
      <FeaturePage />
    </RoleProtectedRoute>
  }
/>
```

---

## 🧹 Nettoyage Effectué (4 Jan 2026)

### Fichiers Supprimés
```
❌ /pages/Dashboard_old_backup.js
❌ /pages/Marketplace_old_backup.js
❌ /pages/dashboards/AdminDashboard.OLD.js
❌ /pages/dashboards/CommercialDashboard.js.bak
❌ /pages/influencer/InfluencerDashboard.jsx (doublon)
❌ /pages/commercial/CommercialDashboard.jsx (doublon)
❌ /pages/SalesRepDashboard.jsx (orphelin)
❌ /pages/MonitoringDashboard.jsx (orphelin)
```

### Documentation Déplacée
```
✅ /pages/dashboards/CHECKLIST_INTEGRATION_ET_TEST.js → /docs/integration/
✅ /pages/dashboards/GUIDE_INTEGRATION_COMPLET.js → /docs/integration/
✅ /pages/dashboards/QUICK_START.js → /docs/integration/
✅ /pages/dashboards/RAPPORT_FINAL_INTEGRATION.js → /docs/integration/
✅ /pages/dashboards/TESTS_PHASES_2_3_4.js → /docs/integration/
```

### Routes Ajoutées au Sidebar
```
✅ /services-integres (Admin + Merchant)
✅ /admin/analytics (Admin)
✅ /reports/advanced (Admin)
✅ /email/campaigns (Admin)
✅ /api/docs (Admin)
✅ /settings/advanced (Admin)
✅ /integrations (Merchant)
```

---

## 🚀 Prochaines Améliorations Recommandées

### Court Terme
1. ✅ Ajouter tests unitaires pour composants critiques
2. ✅ Améliorer documentation API
3. ✅ Optimiser performance (lazy loading)
4. ✅ Ajouter monitoring erreurs (Sentry)

### Moyen Terme
1. Migration complète vers TypeScript
2. Mise en place CI/CD complet
3. Tests E2E avec Playwright
4. Documentation Storybook

### Long Terme
1. Microservices architecture
2. GraphQL API
3. Mobile apps (React Native)
4. Internationalisation complète (10+ langues)

---

## 📞 Contact & Support

**Développeur Principal:** Claude AI
**Stack:** React + FastAPI + PostgreSQL
**Déploiement:** Docker + Kubernetes

---

*Dernière révision: 4 Janvier 2026*
