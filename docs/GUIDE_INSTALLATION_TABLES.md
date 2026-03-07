# 🚀 GUIDE D'INSTALLATION - TABLES SUPABASE

## 📋 ÉTAPES À SUIVRE

### ✅ ÉTAPE 1: Analyser les tables nécessaires
**Déjà fait!** ✓
- Script `extract_all_tables.py` a scanné tout le backend
- **97 tables uniques** identifiées
- Liste complète dans `LISTE_TABLES_COMPLETE.txt`

---

### ✅ ÉTAPE 2: Préparer le script SQL
**Déjà fait!** ✓
- Script complet: `CREATE_ALL_TABLES_COMPLETE.sql`
- Contient:
  - 91 tables de données
  - 6 vues matérialisées
  - Index pour performances
  - Triggers pour updated_at
  - RLS (Row Level Security)
  - Données par défaut

---

### 🔄 ÉTAPE 3: Exécuter le script dans Supabase

#### 3.1 Ouvrir Supabase
1. Allez sur https://supabase.com
2. Connectez-vous à votre compte
3. Sélectionnez votre projet GetYourShare

#### 3.2 Ouvrir l'éditeur SQL
1. Dans le menu de gauche, cliquez sur **"SQL Editor"**
2. Cliquez sur **"+ New query"** (Nouvelle requête)

#### 3.3 Copier le script
1. Ouvrez le fichier `CREATE_ALL_TABLES_COMPLETE.sql` dans VS Code
2. Sélectionnez tout le contenu (Ctrl+A)
3. Copiez (Ctrl+C)

#### 3.4 Coller et exécuter
1. Collez dans l'éditeur SQL de Supabase (Ctrl+V)
2. Cliquez sur **"Run"** (ou Ctrl+Enter)
3. ⏳ Attendez ~30 secondes (le script est long)
4. Vérifiez qu'il n'y a pas d'erreurs en bas de l'écran

#### 3.5 Résultat attendu
Vous devriez voir un tableau avec 3 lignes:
```
type                | count
--------------------|-------
Tables créées       | 91
Vues créées         | 6
Index créés         | 120+
```

---

### ✅ ÉTAPE 4: Vérifier l'installation

#### Option A: Via l'interface Supabase
1. Allez dans **"Table Editor"** (éditeur de tables)
2. Vérifiez que vous voyez toutes les tables dans la liste de gauche
3. Principales tables à vérifier:
   - `users`
   - `products`
   - `tracking_links`
   - `subscriptions`
   - `subscription_plans`

#### Option B: Via script Python
1. Assurez-vous que votre `.env` est configuré:
   ```
   SUPABASE_URL=https://votre-projet.supabase.co
   SUPABASE_KEY=votre_clé_supabase
   ```

2. Exécutez le script de vérification:
   ```bash
   python verify_supabase_tables.py
   ```

3. Le script affichera:
   - ✅ Liste des tables existantes
   - ❌ Liste des tables manquantes (si any)
   - 📊 Statistiques finales

---

### ✅ ÉTAPE 5: Vérifier les données par défaut

#### 5.1 Plans d'abonnement
```sql
SELECT * FROM subscription_plans ORDER BY price;
```
Devrait retourner 3 plans:
- **Free** (0€/mois) - 5 campagnes, 10 liens
- **Pro** (29.99€/mois) - 20 campagnes, 50 liens
- **Elite** (99.99€/mois) - Illimité

#### 5.2 Catégories de produits
```sql
SELECT * FROM product_categories ORDER BY name;
```
Devrait retourner 8 catégories:
- Beauty, Fashion, Food, Home, Other, Sports, Tech, Travel

#### 5.3 Paramètres de plateforme
```sql
SELECT key, value FROM platform_settings;
```
Devrait retourner:
- `commission_rate`
- `min_payout_amount`
- `platform_name`
- `maintenance_mode`

---

## 🔧 RÉSOLUTION DE PROBLÈMES

### Problème 1: "Permission denied for schema public"
**Solution:**
```sql
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO anon;
GRANT ALL ON SCHEMA public TO authenticated;
```

### Problème 2: "Table already exists"
**Pas un problème!**
- Le script utilise `CREATE TABLE IF NOT EXISTS`
- Les tables existantes ne seront pas modifiées
- Seules les tables manquantes seront créées

### Problème 3: "Function gen_random_uuid() does not exist"
**Solution:**
```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Problème 4: Script trop long / timeout
**Solution:**
Découpez le script en plusieurs parties:
1. Exécutez d'abord les tables 1-20
2. Puis les tables 21-40
3. Puis les tables 41-60
4. Etc.

---

## 📊 TABLES PAR PRIORITÉ

Si vous voulez créer les tables progressivement:

### 🔴 PRIORITÉ HAUTE (essentielles)
```sql
-- Créer d'abord ces tables:
users, merchants, influencers, products, services,
campaigns, tracking_links, conversions, sales,
subscriptions, subscription_plans
```

### 🟡 PRIORITÉ MOYENNE (importantes)
```sql
-- Puis ces tables:
invitations, affiliation_requests, payouts,
leads, notifications, messages
```

### 🟢 PRIORITÉ BASSE (optionnelles)
```sql
-- Enfin ces tables:
gamification tables, KYC tables, moderation_queue,
swipe_history, translations
```

---

## 🎯 CHECKLIST FINALE

Avant de passer à l'étape suivante, vérifiez:

- [ ] ✅ Script SQL exécuté sans erreur
- [ ] ✅ 91+ tables visibles dans Table Editor
- [ ] ✅ 3 plans d'abonnement créés
- [ ] ✅ 8 catégories de produits créées
- [ ] ✅ Script `verify_supabase_tables.py` retourne 100% OK
- [ ] ✅ Table `users` contient des données de test
- [ ] ✅ RLS activé sur les tables sensibles

---

## 📞 PROCHAINES ÉTAPES

Une fois toutes les tables créées:

### 1. Tester les comptes de test
```bash
cd backend
python verify_and_create_accounts.py
```

### 2. Redémarrer le backend
```bash
cd backend
python server.py
```

### 3. Tester les endpoints
- Connexion admin: `POST /api/auth/login`
- Liste produits: `GET /api/marketplace/products`
- Plans d'abonnement: `GET /api/subscriptions/plans`

### 4. Lancer le frontend
```bash
cd frontend
npm start
```

---

## 💾 SAUVEGARDE

**Important:** Avant d'exécuter le script sur votre base de production:

1. Créez une sauvegarde:
   - Dans Supabase: **Settings → Database → Backups**
   - Ou exportez via `pg_dump`

2. Testez d'abord sur un projet Supabase de test

3. Si tout fonctionne, appliquez sur production

---

## 📚 DOCUMENTATION

| Fichier | Description |
|---------|-------------|
| `CREATE_ALL_TABLES_COMPLETE.sql` | Script SQL complet (2500+ lignes) |
| `TABLES_SUPABASE_RESUME.md` | Documentation détaillée (ce fichier) |
| `LISTE_TABLES_COMPLETE.txt` | Liste brute des 97 tables |
| `extract_all_tables.py` | Script d'analyse du backend |
| `verify_supabase_tables.py` | Script de vérification |

---

## ✅ SUCCÈS!

Si toutes les étapes sont complétées:

```
🎉 FÉLICITATIONS! 🎉

Votre base de données Supabase est maintenant complète avec:
✅ 91 tables de données
✅ 6 vues matérialisées
✅ 120+ index pour performances
✅ RLS activé
✅ Données par défaut insérées

Votre application GetYourShare est prête à fonctionner! 🚀
```

---

## 🆘 BESOIN D'AIDE?

Si vous rencontrez des problèmes:

1. Vérifiez les logs d'erreur dans Supabase
2. Exécutez `verify_supabase_tables.py` pour diagnostiquer
3. Consultez la documentation Supabase: https://supabase.com/docs
4. Vérifiez que votre projet Supabase est sur un plan payant si nécessaire

---

**Créé le:** 2025-01-12  
**Version:** 1.0  
**Statut:** ✅ Prêt pour production
