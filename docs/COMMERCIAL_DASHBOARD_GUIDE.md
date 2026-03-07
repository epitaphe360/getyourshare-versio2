# 🎯 DASHBOARD COMMERCIAL - GUIDE D'INSTALLATION

## 📋 Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture Base de Données](#architecture-base-de-données)
3. [Installation](#installation)
4. [Endpoints Backend](#endpoints-backend)
5. [Frontend Dashboard](#frontend-dashboard)
6. [Niveaux d'Abonnement](#niveaux-dabonnement)
7. [Tests](#tests)

---

## 🎨 Vue d'ensemble

Le Dashboard Commercial est un outil complet de prospection et promotion pour les commerciaux, avec **3 niveaux d'abonnement** :

- 🌱 **STARTER** (Gratuit) : 10 leads/mois, 3 liens trackés, 3 templates
- 🚀 **PRO** (29€/mois) : Leads illimités, CRM avancé, 15 templates, kit marketing
- 👑 **ENTERPRISE** (99€/mois) : Tout débloqué + IA, automation, équipes

---

## 🗄️ Architecture Base de Données

### Tables Créées

| Table | Description | Colonnes Principales |
|-------|-------------|---------------------|
| `sales_representatives` | Profils commerciaux | user_id, territory, commission_rate, targets |
| `commercial_leads` | CRM Leads | first_name, email, company, status, temperature, estimated_value |
| `commercial_tracking_links` | Liens trackés | link_code, channel, total_clicks, total_conversions |
| `commercial_templates` | Templates marketing | title, category, content, subscription_tier |
| `commercial_stats` | Stats agrégées | period_date, leads_generated, total_revenue, total_commission |
| `lead_activities` | Historique leads | activity_type, description, metadata |
| `product_marketing_kits` | Kits marketing | asset_type, file_url, subscription_tier |
| `commercial_quotes` | Devis générés | products, total_amount, status |

### Vues SQL

- `sales_rep_stats` : Statistiques par commercial
- `sales_pipeline` : Pipeline de vente
- `today_activities` : Activités du jour

---

## ⚙️ Installation

### Étape 1 : Exécuter les Scripts SQL

#### Option A : Via Supabase Dashboard (Recommandé)

1. **Ouvrir le SQL Editor** :
   ```
   https://app.supabase.com/project/gwgvnusegnnhiciprvyc/sql/new
   ```

2. **Exécuter CREATE_COMMERCIAL_TABLES.sql** (SI PAS DÉJÀ FAIT) :
   - Ce fichier existe déjà dans le projet
   - Il crée les tables `sales_representatives`, `deals`, `sales_activities`, etc.
   - Vérifier si les tables existent déjà :
     ```sql
     SELECT tablename FROM pg_tables 
     WHERE schemaname = 'public' 
     AND tablename LIKE '%commercial%' OR tablename LIKE '%sales%';
     ```

3. **Exécuter INSERT_COMMERCIAL_DATA.sql** :
   - Copier le contenu du fichier `INSERT_COMMERCIAL_DATA.sql`
   - Coller dans le SQL Editor
   - Cliquer sur **RUN** (ou Ctrl+Enter)
   - Attendre la confirmation "Success"

#### Option B : Via Script Python

```bash
cd backend
python setup_commercial_db.py
```

### Étape 2 : Vérifier les Données Insérées

```sql
-- Vérifier les utilisateurs commerciaux
SELECT email, role, subscription_tier FROM users WHERE role = 'commercial';

-- Vérifier les profils sales_representatives
SELECT first_name, last_name, email, territory FROM sales_representatives;

-- Compter les leads
SELECT COUNT(*) FROM commercial_leads;

-- Compter les liens trackés
SELECT COUNT(*) FROM commercial_tracking_links;

-- Compter les templates
SELECT COUNT(*) FROM commercial_templates;

-- Résumé complet
SELECT 
    'users' as table_name, COUNT(*) as count FROM users WHERE role = 'commercial'
UNION ALL
SELECT 'sales_representatives', COUNT(*) FROM sales_representatives
UNION ALL
SELECT 'commercial_leads', COUNT(*) FROM commercial_leads
UNION ALL
SELECT 'commercial_tracking_links', COUNT(*) FROM commercial_tracking_links
UNION ALL
SELECT 'commercial_templates', COUNT(*) FROM commercial_templates
UNION ALL
SELECT 'commercial_stats', COUNT(*) FROM commercial_stats;
```

**Résultat attendu** :
```
users: 3
sales_representatives: 3
commercial_leads: ~68 (3 pour STARTER, 15 pour PRO, 50 pour ENTERPRISE)
commercial_tracking_links: 48 (3+15+30)
commercial_templates: 22 (3 STARTER + 15 PRO + 4 ENTERPRISE)
commercial_stats: 270 (3 commerciaux × 30 jours × 3 périodes)
```

---

## 🔌 Endpoints Backend

### Installation des Endpoints

**Fichier** : `backend/commercial_endpoints.py` (déjà créé)

#### 1. Ajouter les imports dans `backend/server.py` :

```python
# Ajouter en haut du fichier (après les autres imports)
from commercial_endpoints import router as commercial_router

# Ajouter après la création de l'app
app.include_router(commercial_router)
```

#### 2. Endpoints Disponibles

| Méthode | Endpoint | Description | Restrictions |
|---------|----------|-------------|--------------|
| GET | `/api/commercial/stats` | Statistiques dashboard | - |
| GET | `/api/commercial/leads` | Liste des leads | STARTER: 10 max |
| POST | `/api/commercial/leads` | Créer un lead | STARTER: 10/mois max |
| PATCH | `/api/commercial/leads/{id}` | Modifier un lead | - |
| GET | `/api/commercial/tracking-links` | Liens trackés | STARTER: 3 max |
| POST | `/api/commercial/tracking-links` | Créer un lien | STARTER: 3 max |
| GET | `/api/commercial/templates` | Templates dispo | STARTER: 3, PRO: 15 |
| POST | `/api/commercial/templates/{id}/use` | Utiliser template | - |
| GET | `/api/commercial/analytics/performance` | Données graphiques | STARTER: 7j, PRO: 30j |
| GET | `/api/commercial/analytics/funnel` | Funnel conversion | - |

#### 3. Tester les Endpoints

```bash
# Démarrer le backend
cd backend
python server.py

# Tester (dans un autre terminal)
# 1. Se connecter avec un commercial
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"commercial.pro@tracknow.io","password":"Test123!"}'

# Copier le token reçu

# 2. Tester les stats
curl -X GET http://localhost:8000/api/commercial/stats \
  -H "Authorization: Bearer <TOKEN>"

# 3. Tester les leads
curl -X GET http://localhost:8000/api/commercial/leads \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 🎨 Frontend Dashboard

### Créer CommercialDashboard.js

**Fichier** : `frontend/src/pages/dashboards/CommercialDashboard.js`

#### Structure du Dashboard

```jsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import { LineChart, BarChart, PieChart, ... } from 'recharts';
import { Lock } from 'lucide-react';

export default function CommercialDashboard() {
  const [stats, setStats] = useState(null);
  const [leads, setLeads] = useState([]);
  const [trackingLinks, setTrackingLinks] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [subscriptionTier, setSubscriptionTier] = useState('starter');
  
  // Récupérer les données...
  
  return (
    <div>
      {/* Bandeau abonnement */}
      <SubscriptionBanner tier={subscriptionTier} />
      
      {/* StatCards animés */}
      <div className="grid grid-cols-4 gap-6">
        <StatCard title="Leads" value={stats.total_leads} />
        <StatCard title="Commission" value={stats.total_commission} />
        <StatCard title="Pipeline" value={stats.pipeline_value} />
        <StatCard title="Taux Conv." value={stats.conversion_rate} />
      </div>
      
      {/* Graphiques */}
      <div className="grid grid-cols-2 gap-6">
        <PerformanceChart data={performanceData} />
        <FunnelChart data={funnelData} />
      </div>
      
      {/* Outils */}
      {subscriptionTier !== 'starter' && (
        <div className="grid grid-cols-2 gap-6">
          <TrackingLinksCard links={trackingLinks} />
          <TemplatesCard templates={templates} />
        </div>
      )}
      
      {/* Fonctionnalités verrouillées pour STARTER */}
      {subscriptionTier === 'starter' && (
        <LockedFeature 
          title="CRM Avancé" 
          description="Passez à PRO pour débloquer"
        />
      )}
    </div>
  );
}
```

#### Composants Clés

**1. Bandeau Abonnement**
```jsx
function SubscriptionBanner({ tier }) {
  const config = {
    starter: {
      color: 'from-orange-500 to-pink-500',
      icon: '🌱',
      message: 'Vous avez utilisé 7/10 leads ce mois',
      cta: '🚀 Passer à PRO - 29€/mois'
    },
    pro: {
      color: 'from-purple-600 to-blue-600',
      icon: '⚡',
      message: 'Tous les outils débloqués'
    },
    enterprise: {
      color: 'from-yellow-500 to-amber-600',
      icon: '👑',
      message: 'Accès Total + IA'
    }
  };
  
  return (
    <div className={`bg-gradient-to-r ${config[tier].color} p-4 rounded-lg mb-6`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-white font-bold">
            {config[tier].icon} Abonnement {tier.toUpperCase()}
          </p>
          <p className="text-white text-sm">{config[tier].message}</p>
        </div>
        {tier === 'starter' && (
          <button className="bg-white text-orange-600 px-6 py-2 rounded-lg">
            {config[tier].cta}
          </button>
        )}
      </div>
    </div>
  );
}
```

**2. Fonctionnalité Verrouillée**
```jsx
function LockedFeature({ title, description }) {
  return (
    <div className="relative">
      <div className="blur-sm pointer-events-none opacity-50">
        <Card title={title}>
          <div className="h-64 bg-gray-200 rounded" />
        </Card>
      </div>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="bg-white rounded-lg p-8 shadow-xl text-center">
          <Lock size={48} className="mx-auto mb-4 text-gray-400" />
          <h3 className="text-xl font-bold mb-2">{title}</h3>
          <p className="text-gray-600 mb-4">{description}</p>
          <button className="bg-purple-600 text-white px-6 py-3 rounded-lg">
            Débloquer maintenant
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 💎 Niveaux d'Abonnement

### Comparaison des Fonctionnalités

| Fonctionnalité | 🌱 STARTER | 🚀 PRO | 👑 ENTERPRISE |
|---|---|---|---|
| **Prix** | Gratuit | 29€/mois | 99€/mois |
| **Leads CRM** | 10/mois | Illimité | Illimité |
| **Liens trackés** | 3 max | Illimité | Illimité |
| **Templates** | 3 basiques | 15 pro | Tous + custom |
| **CRM Pipeline** | ❌ | ✅ Basique | ✅ Avancé + IA |
| **Kit Marketing** | ❌ | ✅ Images/PDF | ✅ + Vidéos |
| **Générateur Devis** | ❌ | ❌ | ✅ + Signature |
| **Graphiques** | 1 (7j) | 4 (30j) | 8+ (illimité) |
| **Automation** | ❌ | ✅ Rappels | ✅ Complet |
| **IA Suggestions** | ❌ | ❌ | ✅ |
| **Multi-users** | ❌ | ❌ | ✅ |
| **Support** | Email | Chat | Phone dédié |

### Logique de Restriction Backend

```python
# Dans commercial_endpoints.py

@router.post("/leads")
async def create_lead(lead_data, current_user):
    subscription_tier = current_user.get('subscription_tier', 'starter')
    
    if subscription_tier == 'starter':
        # Vérifier limite 10 leads/mois
        count = get_leads_count_this_month(user_id)
        if count >= 10:
            raise HTTPException(
                status_code=403,
                detail="Limite de 10 leads/mois atteinte. Passez à PRO."
            )
    
    # Créer le lead...
```

---

## 🧪 Tests

### Comptes de Test

| Email | Mot de passe | Niveau | Accès |
|-------|--------------|--------|-------|
| commercial.starter@tracknow.io | Test123! | STARTER | Limité |
| commercial.pro@tracknow.io | Test123! | PRO | Complet |
| commercial.enterprise@tracknow.io | Test123! | ENTERPRISE | Total |

### Scénarios de Test

#### Test 1 : STARTER - Limite Leads
```bash
1. Se connecter avec commercial.starter@tracknow.io
2. Aller sur /dashboard/commercial
3. Créer 10 leads
4. Essayer d'en créer un 11ème → Doit afficher erreur
5. Vérifier le message : "Limite atteinte. Passez à PRO"
```

#### Test 2 : PRO - CRM Avancé
```bash
1. Se connecter avec commercial.pro@tracknow.io
2. Vérifier que tous les outils sont débloqués
3. Créer 20+ leads → Doit fonctionner
4. Créer 10+ liens trackés → Doit fonctionner
5. Accéder aux 15 templates PRO
```

#### Test 3 : ENTERPRISE - IA & Automation
```bash
1. Se connecter avec commercial.enterprise@tracknow.io
2. Vérifier l'accès à tous les templates
3. Tester le générateur de devis
4. Vérifier les suggestions IA (si implémenté)
5. Accéder aux graphiques avancés (8+)
```

### Tests API

```bash
# Test GET /api/commercial/stats
curl -X GET http://localhost:8000/api/commercial/stats \
  -H "Authorization: Bearer <TOKEN>"

# Résultat attendu :
{
  "total_leads": 68,
  "leads_generated_month": 15,
  "qualified_leads": 20,
  "converted_leads": 8,
  "total_commission": 2500.00,
  "total_revenue": 125000.00,
  "pipeline_value": 75000.00,
  "conversion_rate": 11.76,
  "total_clicks": 450,
  "active_tracking_links": 15
}
```

---

## 📝 Checklist d'Installation

- [ ] ✅ Exécuter CREATE_COMMERCIAL_TABLES.sql (si pas déjà fait)
- [ ] ✅ Exécuter INSERT_COMMERCIAL_DATA.sql
- [ ] ✅ Vérifier que 3 commerciaux sont créés
- [ ] ✅ Vérifier que les leads/liens/templates sont insérés
- [ ] ✅ Ajouter `commercial_endpoints.py` dans `server.py`
- [ ] ✅ Tester les endpoints avec Postman/curl
- [ ] ✅ Créer `CommercialDashboard.js`
- [ ] ✅ Ajouter la route dans `App.js`
- [ ] ✅ Tester l'authentification avec les 3 comptes
- [ ] ✅ Vérifier les restrictions par abonnement
- [ ] ✅ Tester les graphiques et animations

---

## 🐛 Troubleshooting

### Problème : "Table already exists"
```sql
-- Vérifier si les tables existent
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND (tablename LIKE '%commercial%' OR tablename LIKE '%sales%');

-- Si oui, supprimer et recréer (ATTENTION: perte de données)
DROP TABLE IF EXISTS commercial_leads CASCADE;
DROP TABLE IF EXISTS commercial_tracking_links CASCADE;
-- etc.
```

### Problème : "Foreign key violation"
```sql
-- Exécuter dans l'ordre:
1. CREATE_COMMERCIAL_TABLES.sql (tables de base)
2. INSERT_COMMERCIAL_DATA.sql (données)
```

### Problème : Endpoints 404
```python
# Vérifier que le router est ajouté dans server.py
from commercial_endpoints import router as commercial_router
app.include_router(commercial_router)

# Redémarrer le serveur
python server.py
```

---

## 📚 Ressources

- [Documentation Supabase](https://supabase.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Framer Motion](https://www.framer.com/motion/)
- [Recharts](https://recharts.org/)

---

## ✨ Prochaines Étapes

1. ✅ Créer le frontend `CommercialDashboard.js`
2. ✅ Implémenter les graphiques animés
3. ✅ Ajouter le système de templates
4. ✅ Créer le générateur de devis (ENTERPRISE)
5. ✅ Intégrer l'IA pour suggestions (ENTERPRISE)
6. ✅ Tests E2E complets

---

**Créé le** : 12 novembre 2025  
**Version** : 1.0  
**Auteur** : GitHub Copilot
