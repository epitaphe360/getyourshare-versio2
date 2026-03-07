# 🚀 GUIDE RAPIDE - ACTIVATION MODÉRATION IA

## ✅ CE QUI EST DÉJÀ FAIT:
- ✓ Backend: `moderation_endpoints.py` intégré dans `server.py`
- ✓ Service IA: `moderation_service.py` avec OpenAI
- ✓ Frontend: Page `/admin/moderation` déjà créée
- ✓ Scripts: `create_test_moderation_products.py` prêt (8 produits)
- ✓ SQL: `CREATE_MODERATION_TABLES_FIXED.sql` créé

---

## 🎯 ÉTAPES À SUIVRE (5 MIN):

### 1️⃣ CRÉER LES TABLES DANS SUPABASE

**A. Ouvrez Supabase Dashboard:**
```
https://supabase.com/dashboard
```

**B. Sélectionnez votre projet**

**C. SQL Editor (menu gauche)**

**D. Copiez et collez ce SQL:**

```sql
-- 📋 Version simplifiée pour test rapide
CREATE TABLE IF NOT EXISTS moderation_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID,
    merchant_id UUID,
    user_id UUID,
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT NOT NULL,
    product_category VARCHAR(100),
    product_price DECIMAL(10, 2),
    product_images JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    ai_decision VARCHAR(20),
    ai_confidence DECIMAL(3, 2),
    ai_risk_level VARCHAR(20),
    ai_flags JSONB,
    ai_reason TEXT,
    ai_recommendation TEXT,
    moderation_method VARCHAR(20),
    admin_decision VARCHAR(20),
    admin_user_id UUID,
    admin_comment TEXT,
    reviewed_at TIMESTAMP,
    submission_attempts INT DEFAULT 1,
    priority INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_moderation_status ON moderation_queue(status);
CREATE INDEX IF NOT EXISTS idx_moderation_merchant ON moderation_queue(merchant_id);
CREATE INDEX IF NOT EXISTS idx_moderation_risk ON moderation_queue(ai_risk_level);

CREATE TABLE IF NOT EXISTS moderation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moderation_id UUID,
    action VARCHAR(50) NOT NULL,
    performed_by UUID,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    comment TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS moderation_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE DEFAULT CURRENT_DATE UNIQUE,
    total_submissions INT DEFAULT 0,
    ai_approved INT DEFAULT 0,
    ai_rejected INT DEFAULT 0,
    admin_approved INT DEFAULT 0,
    admin_rejected INT DEFAULT 0,
    pending INT DEFAULT 0,
    avg_ai_confidence DECIMAL(3, 2),
    avg_review_time_minutes INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**E. Cliquez "Run" ou Ctrl+Enter**

**F. Vérifiez dans "Table Editor":**
- ✅ `moderation_queue`
- ✅ `moderation_history`
- ✅ `moderation_stats`

---

### 2️⃣ CRÉER LES PRODUITS DE TEST

**Dans PowerShell (backend folder):**

```powershell
cd C:\Users\samye\OneDrive\Desktop\v3\getyourshareversion2-\backend
& "..\.venv\Scripts\python.exe" create_test_moderation_products.py
```

**Résultat attendu:**
```
✅ 5 merchants trouvés

🔴 iPhone 15 Pro Max - Prix Exceptionnel
   Prix: 4500.00 MAD | Risque: CRITICAL
   Décision IA: REJECTED ✗ (confiance: 95%)

🟠 Parfum Chanel N°5 - Original
   Prix: 2800.00 MAD | Risque: HIGH
   Décision IA: REJECTED ✗ (confiance: 72%)

🟡 Caftan Marocain Fait Main
   Prix: 1200.00 MAD | Risque: MEDIUM
   Décision IA: APPROVED ✓ (confiance: 88%)

🟢 Ordinateur Portable Dell XPS 15
   Prix: 16500.00 MAD | Risque: LOW
   Décision IA: APPROVED ✓ (confiance: 94%)

[... 4 autres produits ...]

✅ 8/8 PRODUITS CRÉÉS EN MODÉRATION!

📊 RÉPARTITION:
   🔴 Critical: 3
   🟠 High: 2
   🟡 Medium: 1
   🟢 Low: 2
```

---

### 3️⃣ VÉRIFIER DANS LE FRONTEND

**A. Ouvrez l'application:**
```
http://localhost:3000/admin/moderation
```

**B. Vous devriez voir:**
- Dashboard avec 8 produits en attente
- Filtres par niveau de risque (🔴 🟠 🟡 🟢)
- Statistiques: Today's Submissions, Pending, etc.
- Chaque produit avec:
  - Nom, prix, merchant
  - Niveau de risque coloré
  - Raison IA
  - Boutons: Approuver / Rejeter / Détails

**C. Testez l'approbation:**
1. Cliquez sur un produit risque LOW 🟢
2. Cliquez "Approuver"
3. Ajoutez un commentaire (optionnel)
4. Validez
5. Le produit disparaît de la liste pending

---

## 🐛 DÉPANNAGE

### ❌ Erreur: "Could not find the table 'moderation_queue'"
→ Les tables ne sont pas créées dans Supabase
→ Retournez à l'étape 1️⃣

### ❌ Erreur: "0/8 produits créés"
→ Vérifiez que les tables existent:
```sql
SELECT * FROM moderation_queue LIMIT 1;
```

### ❌ Page vide dans le frontend
→ Vérifiez que le backend est lancé (port 8000)
→ Vérifiez la console navigateur (F12)
→ Endpoint devrait être: `GET /api/admin/moderation/pending`

### ❌ Erreur 401 Unauthorized
→ Vous n'êtes pas connecté en tant qu'admin
→ Connectez-vous avec un compte admin

---

## 📦 CONTENU DES 8 PRODUITS DE TEST

| Produit | Prix | Risque | Description |
|---------|------|--------|-------------|
| iPhone 15 Pro Max | 4500 MAD | 🔴 CRITICAL | Prix suspect (marché: 14K-16K) |
| Rolex Submariner | 85000 MAD | 🔴 CRITICAL | Montre luxe, authentification requise |
| Air Jordan 1 Limited | 3800 MAD | 🟠 HIGH | Édition limitée, contrefaçons fréquentes |
| Parfum Chanel N°5 | 2800 MAD | 🟠 HIGH | Produit luxe, certificat à vérifier |
| Caftan Marocain | 1200 MAD | 🟡 MEDIUM | Artisanat local, photos à valider |
| Dell XPS 15 | 16500 MAD | 🟢 LOW | Produit légitime, description technique |
| PlayStation 5 Bundle | 5200 MAD | 🟢 LOW | Occasion 6 mois, facture disponible |
| Sac Guess 2025 | 650 MAD | 🟢 LOW | Accessoire standard conforme |

---

## 🎨 CAPTURES D'ÉCRAN ATTENDUES

**Dashboard Modération:**
```
┌─────────────────────────────────────────────────┐
│  Modération IA des Produits                    │
│  Validation automatique avec intelligence       │
│                                                 │
│  [🔄 Actualiser]  [🔍 Rechercher...]           │
│  [Tous] [🔴Critical] [🟠High] [🟡Medium] [🟢Low]│
│                                                 │
│  📊 Stats: 8 Pending | 0 Approved | 0 Rejected │
│                                                 │
│  🔴 iPhone 15 Pro Max - 4500 MAD               │
│     Risque: CRITICAL | Confiance: 95%          │
│     Prix anormalement bas - possible arnaque    │
│     [✓ Approuver] [✗ Rejeter] [👁️ Détails]     │
│                                                 │
│  🟠 Parfum Chanel N°5 - 2800 MAD               │
│     Risque: HIGH | Confiance: 72%              │
│     Vérifier certificat d'authenticité          │
│     [✓ Approuver] [✗ Rejeter] [👁️ Détails]     │
│                                                 │
│  [...6 autres produits...]                     │
└─────────────────────────────────────────────────┘
```

---

## ✅ VÉRIFICATION FINALE

- [ ] Tables créées dans Supabase (3 tables)
- [ ] Script exécuté avec succès (8/8 produits)
- [ ] Page `/admin/moderation` affiche les produits
- [ ] Filtres par risque fonctionnent
- [ ] Boutons Approuver/Rejeter répondent
- [ ] Stats affichées correctement

---

## 🚀 PROCHAINES ÉTAPES

Après avoir testé la modération:

1. **Intégrer dans création produit** - Ajouter modération lors de `POST /api/products`
2. **Notifications admin** - Email/webhook quand produit en attente
3. **Merchant dashboard** - Voir statut de ses produits en modération
4. **Améliorer IA** - Ajouter analyse d'images avec Vision API
5. **Statistiques avancées** - Graphiques et métriques détaillées

---

**Besoin d'aide?** Vérifiez les logs backend pour plus de détails.
