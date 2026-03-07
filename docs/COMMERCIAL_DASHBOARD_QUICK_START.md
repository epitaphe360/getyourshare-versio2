# 🚀 Dashboard Commercial - Démarrage Rapide

## ✅ Statut : PRÊT À TESTER

Tous les fichiers sont créés et intégrés. Voici comment démarrer :

---

## 📋 ÉTAPE 1 : Exécuter le SQL (5 minutes)

### ⚠️ IMPORTANT : 2 Scripts SQL à exécuter dans l'ordre

### Étape 1.1 : Ajouter la colonne subscription_tier

1. **Ouvrir l'éditeur SQL** :
   ```
   https://app.supabase.com/project/gwgvnusegnnhiciprvyc/sql/new
   ```

2. **Copier le contenu de** : `ADD_SUBSCRIPTION_TIER_COLUMN.sql`

3. **Coller dans l'éditeur et cliquer "RUN"**

4. **Vérifier le message** :
   ```
   ✅ "subscription_tier column added successfully!"
   ```

### Étape 1.2 : Insérer les données de test

1. **Dans le même éditeur SQL, créer un nouveau query**

2. **Copier le contenu de** : `INSERT_COMMERCIAL_DATA.sql`

3. **Coller dans l'éditeur et cliquer "RUN"**

4. **Vérifier l'insertion** :
   ```sql
   -- Devrait retourner 3
   SELECT COUNT(*) FROM users WHERE role = 'commercial';
   
   -- Devrait retourner 68
   SELECT COUNT(*) FROM commercial_leads;
   
   -- Devrait retourner 48
   SELECT COUNT(*) FROM commercial_tracking_links;
   
   -- Vérifier les tiers
   SELECT email, subscription_tier FROM users WHERE role = 'commercial';
   ```

### Option B : Via Python (Alternative)

```bash
cd backend
python setup_commercial_db.py
# Suivre les instructions affichées
```

---

## 🖥️ ÉTAPE 2 : Démarrer le Backend (2 minutes)

```bash
cd backend
python server.py
```

**Vérifier que vous voyez** :
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test rapide de l'endpoint** :
```bash
# Ouvrir http://127.0.0.1:8000/docs
# Chercher "/api/commercial/stats"
# Devrait être listé dans la documentation
```

---

## 🎨 ÉTAPE 3 : Démarrer le Frontend (2 minutes)

```bash
cd frontend
npm start
```

**Vérifier que vous voyez** :
```
Compiled successfully!
Local: http://localhost:3000
```

---

## 🧪 ÉTAPE 4 : Tester les 3 Niveaux d'Abonnement (15 minutes)

### Test 1 : STARTER (Gratuit) 🌱

1. **Connexion** :
   - Email : `commercial.starter@getyourshare.com`
   - Mot de passe : `Test123!`

2. **Naviguer vers** : `/dashboard/commercial`

3. **Vérifications** :
   - [ ] Banner orange "STARTER" affiché
   - [ ] Message "7/10 leads utilisés ce mois"
   - [ ] Bouton "Passer à PRO" visible
   - [ ] 4 StatCards avec animations CountUp
   - [ ] Graphique Performance : 7 derniers jours uniquement
   - [ ] Graphique Funnel : VERROUILLÉ (flou + icône 🔒)
   - [ ] Tableau "Liens Trackés" : 3 liens affichés
   - [ ] Bouton "Créer Lien" DÉSACTIVÉ avec badge "3/3"
   - [ ] Section "CRM Leads" : VERROUILLÉE (flou + bouton "Débloquer")

4. **Test des Limites** :
   - Cliquer "Ajouter Lead"
   - Remplir le formulaire
   - Créer 3 leads supplémentaires (total = 10)
   - **Essayer de créer le 11ème lead** → devrait afficher toast d'erreur :
     ```
     ❌ Limite atteinte. Passez à PRO pour créer des leads illimités.
     ```

---

### Test 2 : PRO (29€/mois) ⚡

1. **Déconnexion puis Connexion** :
   - Email : `commercial.pro@getyourshare.com`
   - Mot de passe : `Test123!`

2. **Vérifications** :
   - [ ] Banner violet/bleu "PRO ⚡" affiché
   - [ ] PAS de message de limite
   - [ ] 4 StatCards avec des valeurs différentes
   - [ ] Graphique Performance : 30 derniers jours
   - [ ] Graphique Funnel : DÉVERROUILLÉ et visible
   - [ ] Tableau "Liens Trackés" : 15 liens affichés
   - [ ] Bouton "Créer Lien" ACTIF (pas de badge)
   - [ ] Section "CRM Leads" : VISIBLE avec tableau de 15 leads
   - [ ] Colonnes leads : Contact, Entreprise, Statut, Température, Valeur

3. **Test CRM** :
   - Tableau visible avec 15 leads
   - Filtres de statut (qualifié, en_negociation, etc.)
   - Badges colorés : 🟢 conclu, 🟡 en_negociation, 🔵 qualifié
   - Température : 🔥 chaud, ☀️ tiede, ❄️ froid

4. **Test Templates** :
   - Cliquer "📄 Templates"
   - Modal s'ouvre avec grille de templates
   - Devrait afficher : **18 templates** (3 STARTER + 15 PRO)
   - Cliquer "Copier" sur un template → toast "Copié !"

---

### Test 3 : ENTERPRISE (99€/mois) 👑

1. **Connexion** :
   - Email : `commercial.enterprise@getyourshare.com`
   - Mot de passe : `Test123!`

2. **Vérifications** :
   - [ ] Banner jaune/ambre "ENTERPRISE 👑" affiché
   - [ ] Graphique Performance : 30 jours
   - [ ] Tableau "Liens Trackés" : 30 liens affichés
   - [ ] Section "CRM Leads" : 50 leads affichés
   - [ ] Bouton "🤖 Générateur Devis" : ACTIF (pas désactivé)
   - [ ] Templates : **22 templates** (tous)

3. **Données Volumineuses** :
   - Vérifier que le tableau de leads défile bien (50 leads)
   - Performance chart avec données complètes (30 jours)
   - Total Commission devrait être le plus élevé

---

## 🐛 Résolution de Problèmes

### Problème : "Module not found: commercial_endpoints"

```bash
# Vérifier que le fichier existe
ls backend/commercial_endpoints.py

# Redémarrer le backend
cd backend
python server.py
```

---

### Problème : "Cannot read property 'subscription_tier' of undefined"

**Cause** : localStorage n'a pas l'objet user

**Solution** : Se déconnecter/reconnecter

```javascript
// Vérifier dans DevTools Console :
JSON.parse(localStorage.getItem('user'))
// Devrait retourner : {id: "...", email: "...", role: "commercial", subscription_tier: "pro"}
```

---

### Problème : "403 Forbidden" sur les endpoints

**Cause** : Token JWT invalide ou rôle incorrect

**Solution** :
1. Ouvrir DevTools → Network
2. Cliquer sur requête API
3. Vérifier Header `Authorization: Bearer <token>`
4. Si token manquant → se reconnecter

---

### Problème : Les graphiques ne s'affichent pas

**Cause** : Données API dans mauvais format

**Solution** :
```javascript
// Dans DevTools Console :
fetch('/api/commercial/analytics/performance', {
  headers: {Authorization: 'Bearer ' + JSON.parse(localStorage.getItem('token'))}
})
.then(r => r.json())
.then(console.log)

// Vérifier format :
[{date: "2025-01-12", revenue: 1500, leads: 8}, ...]
```

---

### Problème : Animations ne fonctionnent pas

**Vérifier les dépendances** :
```bash
cd frontend
npm list framer-motion react-countup recharts

# Si manquant :
npm install framer-motion react-countup recharts
```

---

## 📊 Critères de Succès

- ✅ 3 comptes commerciaux se connectent avec succès
- ✅ STARTER affiche limites ("7/10 leads", bouton désactivé)
- ✅ PRO déverrouille toutes les fonctionnalités
- ✅ ENTERPRISE affiche données volumineuses (50 leads)
- ✅ Animations CountUp fonctionnent sur les StatCards
- ✅ Graphiques Recharts s'affichent avec gradients
- ✅ Modal Templates s'ouvre et affiche templates filtrés
- ✅ Création de lead fonctionne (et limite STARTER est respectée)
- ✅ Aucune erreur dans la console

---

## 📁 Fichiers Créés dans cette Session

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `INSERT_COMMERCIAL_DATA.sql` | 442 | Données de test (3 users, 68 leads, 48 links) |
| `backend/commercial_endpoints.py` | 750 | 10 endpoints API avec validation abonnement |
| `frontend/src/pages/dashboards/CommercialDashboard.js` | 1013 | Dashboard complet avec animations |
| `COMMERCIAL_DASHBOARD_GUIDE.md` | 1500+ | Documentation complète |
| `backend/setup_commercial_db.py` | 50 | Script d'aide pour SQL |

---

## 🚀 Prochaines Étapes (Après Tests)

### 1. Ajouter Navigation Sidebar
```javascript
// Dans Sidebar.js
{user.role === 'commercial' && (
  <NavItem to="/dashboard/commercial" icon={<Briefcase />}>
    Dashboard Commercial
  </NavItem>
)}
```

### 2. Intégrer Paiement Stripe (Optionnel)
- Créer modal "Upgrade to PRO"
- Ajouter Stripe Checkout
- Webhook pour mettre à jour subscription_tier

### 3. Ajouter Export de Données
```javascript
// Bouton Export CSV
const exportLeads = () => {
  const csv = leads.map(l => 
    `${l.first_name},${l.last_name},${l.email},${l.company}`
  ).join('\n');
  downloadCSV(csv, 'leads.csv');
};
```

---

## 📞 Support

**Si vous rencontrez un problème** :
1. Vérifier les critères de succès ci-dessus
2. Consulter la section "Résolution de Problèmes"
3. Ouvrir DevTools Console pour voir les erreurs
4. Vérifier que les 3 étapes (SQL → Backend → Frontend) sont complètes

**Fichiers de référence** :
- Documentation complète : `COMMERCIAL_DASHBOARD_GUIDE.md`
- Structure base de données : `CREATE_COMMERCIAL_TABLES.sql`
- Données de test : `INSERT_COMMERCIAL_DATA.sql`

---

## ✨ Résumé

Vous avez maintenant un **Dashboard Commercial complet** avec :
- 🎯 3 niveaux d'abonnement (STARTER/PRO/ENTERPRISE)
- 📊 Statistiques en temps réel avec animations
- 🔗 Gestion de liens trackés
- 👥 CRM avec pipeline de ventes
- 📄 Templates marketing
- 📈 Analytics de performance
- 🔒 Restrictions par abonnement

**Temps estimé pour tester complètement** : ~30 minutes

Bon test ! 🚀
