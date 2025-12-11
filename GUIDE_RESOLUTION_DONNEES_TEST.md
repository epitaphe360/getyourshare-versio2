# 🔧 GUIDE DE RÉSOLUTION - DONNÉES DE TEST NON AFFICHÉES

## ⚠️ PROBLÈME IDENTIFIÉ

**Symptôme**: Les données de test ne s'affichent pas dans les dashboards sur le site de production (https://shareyoursales.vercel.app/)

**Causes possibles**:
1. ✅ **Scripts de seed jamais exécutés sur la production** (cause la plus probable)
2. ⚠️ **RLS Policies Supabase trop restrictives** (bloquent l'accès aux données)
3. 🐛 **Bugs frontend** (erreurs JavaScript qui empêchent l'affichage)

---

## 🚀 SOLUTION 1: EXÉCUTER LES SCRIPTS DE SEED (PRIORITÉ 1)

### Étape 1: Configurer l'accès à Supabase

1. **Ouvrir le fichier `.env` dans le dossier `backend/`**
2. **Vérifier que ces variables sont configurées**:
   ```env
   SUPABASE_URL=https://votre-projet.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **Obtenir la SERVICE_KEY (ADMIN)**:
   - Aller sur https://supabase.com/dashboard
   - Sélectionner votre projet
   - Settings > API
   - Copier la **service_role key** (pas la anon key!)
   - C'est la clé ADMIN qui contourne les RLS policies

### Étape 2: Exécuter le script de seed complet

```bash
cd /home/user/getyourshare-versio2/backend

# Installer les dépendances si nécessaire
pip install python-dotenv supabase

# Exécuter le script de seed COMPLET
python generate_all_test_data.py
```

**Ce script va créer**:
- ✅ 1 Admin
- ✅ 6 Merchants (avec différents plans: Free, Pro, Enterprise)
- ✅ 7 Influencers (avec followers, engagement, revenus)
- ✅ 6 Commerciaux
- ✅ 15 Campaigns (actives, draft, completed)
- ✅ 40+ Produits
- ✅ 100+ Sales
- ✅ 80+ Commissions
- ✅ 50+ Leads
- ✅ 30+ Invoices

### Étape 3: Vérifier que les données ont été créées

```bash
# Script de vérification
python check_test_data.py
```

**Sortie attendue**:
```
============================================================
VÉRIFICATION DES DONNÉES DE TEST
============================================================

1. UTILISATEURS:
   Total: 20 utilisateurs
   - admin: 1
   - merchant: 6
   - influencer: 7
   - commercial: 6

2. PRODUITS:
   Total: 40+ produits

3. TRACKING LINKS:
   Total: 30+ liens

4. CONVERSIONS:
   Total: 100+ conversions
   Complétées: 80+
   Commissions totales: 50,000+ MAD
```

---

## 🔐 SOLUTION 2: VÉRIFIER LES RLS POLICIES SUPABASE (PRIORITÉ 2)

### Problème des RLS Policies

Les **Row Level Security (RLS) policies** de Supabase peuvent bloquer l'accès aux données même si elles existent.

### Étapes pour vérifier les RLS Policies:

1. **Aller sur le Dashboard Supabase**:
   - https://supabase.com/dashboard
   - Sélectionner votre projet

2. **Aller dans Authentication > Policies**

3. **Vérifier chaque table**:

#### Table `users`:
```sql
-- Policy de lecture pour TOUS (à ajouter si manquante)
CREATE POLICY "users_read_all"
ON users FOR SELECT
USING (true);

-- OU policy de lecture pour utilisateurs authentifiés
CREATE POLICY "users_read_authenticated"
ON users FOR SELECT
TO authenticated
USING (true);
```

#### Table `products`:
```sql
-- Tous peuvent lire les produits actifs
CREATE POLICY "products_read_active"
ON products FOR SELECT
USING (is_active = true);

-- Merchants peuvent CRUD leurs propres produits
CREATE POLICY "products_merchant_full"
ON products FOR ALL
TO authenticated
USING (auth.uid() = merchant_id);
```

#### Table `conversions`:
```sql
-- Merchants voient leurs conversions
CREATE POLICY "conversions_merchant_read"
ON conversions FOR SELECT
TO authenticated
USING (auth.uid() = merchant_id);

-- Influencers voient leurs conversions
CREATE POLICY "conversions_influencer_read"
ON conversions FOR SELECT
TO authenticated
USING (auth.uid() = influencer_id);
```

#### Table `campaigns`:
```sql
-- Tous peuvent lire les campaigns actives
CREATE POLICY "campaigns_read_active"
ON campaigns FOR SELECT
USING (status = 'active');

-- Merchants CRUD leurs campaigns
CREATE POLICY "campaigns_merchant_full"
ON campaigns FOR ALL
TO authenticated
USING (auth.uid() = merchant_id);
```

### 🚨 ERREUR CONNUE: RLS Recursion sur `users`

**Symptôme**: Erreur "infinite recursion detected" sur la table `users`

**Cause**: Une policy RLS fait référence à elle-même (ex: vérifier `role` dans `users` depuis une policy sur `users`)

**Solution**:
```sql
-- SUPPRIMER les policies problématiques
DROP POLICY IF EXISTS "users_read_own" ON users;
DROP POLICY IF EXISTS "users_read_same_role" ON users;

-- CRÉER une policy simple sans récursion
CREATE POLICY "users_read_simple"
ON users FOR SELECT
USING (true);  -- Tous peuvent lire (ou TO authenticated USING (true))
```

---

## 🐛 SOLUTION 3: VÉRIFIER LES BUGS FRONTEND

### Étapes de débogage:

1. **Ouvrir la Console Développeur du navigateur**:
   - Chrome/Edge: F12 ou Ctrl+Shift+I
   - Firefox: F12
   - Safari: Cmd+Option+I

2. **Aller sur un dashboard** (ex: Admin Dashboard, Merchant Dashboard)

3. **Regarder l'onglet "Console"** pour voir les erreurs JavaScript

4. **Regarder l'onglet "Network"** pour voir les requêtes API:
   - Filtrer par "Fetch/XHR"
   - Cliquer sur une requête
   - Vérifier le Status Code:
     - ✅ 200 = OK
     - ❌ 401 = Non authentifié
     - ❌ 403 = Accès refusé (RLS policies!)
     - ❌ 500 = Erreur serveur

### Erreurs courantes:

#### Erreur 1: "Failed to load data"
**Cause**: API endpoint crashe ou RLS bloque

**Solution**:
- Vérifier les logs backend (Vercel logs)
- Vérifier les RLS policies Supabase

#### Erreur 2: "Cannot read property 'map' of undefined"
**Cause**: Frontend essaie d'afficher `data.map()` mais `data` est undefined/null

**Solution**: Les données ne sont pas retournées par l'API
- Vérifier que les scripts de seed ont été exécutés
- Vérifier les RLS policies

#### Erreur 3: Écran blanc ou spinner infini
**Cause**: Requête API ne se termine jamais ou crash

**Solution**:
- Voir Console pour erreur JavaScript
- Voir Network pour requête bloquée/timeout

---

## 📋 CHECKLIST COMPLÈTE DE RÉSOLUTION

### Étape 1: Base de données
- [ ] Variables `.env` configurées (SUPABASE_URL, SERVICE_KEY)
- [ ] Script `generate_all_test_data.py` exécuté avec succès
- [ ] Script `check_test_data.py` confirme 20+ utilisateurs
- [ ] Script `check_test_data.py` confirme 40+ produits
- [ ] Script `check_test_data.py` confirme 100+ conversions

### Étape 2: RLS Policies
- [ ] Dashboard Supabase > Authentication > Policies vérifié
- [ ] Table `users` a une policy de lecture (sans récursion)
- [ ] Table `products` a une policy de lecture pour `is_active = true`
- [ ] Table `conversions` a des policies pour merchants et influencers
- [ ] Table `campaigns` a une policy de lecture pour `status = 'active'`
- [ ] Aucune erreur "infinite recursion" dans les logs Supabase

### Étape 3: Frontend
- [ ] Console navigateur ouverte (F12)
- [ ] Onglet Network filtré sur Fetch/XHR
- [ ] Toutes les requêtes API retournent 200 OK
- [ ] Aucune erreur JavaScript dans Console
- [ ] Données affichées correctement dans les dashboards

---

## 🎯 COMMANDES RAPIDES

### Exécuter seed complet
```bash
cd backend && python generate_all_test_data.py
```

### Vérifier données créées
```bash
cd backend && python check_test_data.py
```

### Nettoyer données test et recommencer
```bash
cd backend && python generate_all_test_data.py --clean
```

### Logs Vercel (si backend hébergé sur Vercel)
```bash
vercel logs --follow
```

---

## 📞 SI ÇA NE MARCHE TOUJOURS PAS

### Diagnostic avancé:

1. **Exporter les logs Supabase**:
   - Dashboard Supabase > Logs
   - Filtrer par erreurs (Error)
   - Chercher "permission denied" ou "RLS policy"

2. **Tester une requête manuelle**:
   ```sql
   -- Dans SQL Editor Supabase
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM products WHERE is_active = true;
   SELECT COUNT(*) FROM conversions;
   ```

3. **Vérifier que le backend Vercel fonctionne**:
   ```bash
   curl https://shareyoursales.vercel.app/api/health
   # Devrait retourner: {"status": "ok"}
   ```

4. **Tester un endpoint avec les identifiants de test**:
   ```bash
   # Login
   curl -X POST https://shareyoursales.vercel.app/api/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@shareyoursales.com", "password": "admin123"}'

   # Copier le token
   # Tester un endpoint protégé
   curl https://shareyoursales.vercel.app/api/dashboard/stats \
     -H "Authorization: Bearer <token>"
   ```

---

## ✅ RÉSULTAT ATTENDU

Après avoir suivi ce guide:

1. ✅ **Dashboard Admin** affiche:
   - Total utilisateurs: 20+
   - Merchants: 6
   - Influencers: 7
   - Commercials: 6
   - Graphiques de revenus avec données
   - Top produits/influencers visibles

2. ✅ **Dashboard Merchant** affiche:
   - Mes produits: 5-10 produits
   - Mes campaigns: 2-5 campaigns
   - Conversions: 10-30 ventes
   - Graphique des ventes sur 30 jours
   - Top influencers qui vendent mes produits

3. ✅ **Dashboard Influencer** affiche:
   - Mes stats: Revenus, clics, conversions
   - Produits disponibles dans marketplace: 40+
   - Mes liens de tracking: 5-15 liens
   - Commissions à venir
   - Graphique des performances

4. ✅ **Dashboard Commercial** affiche:
   - Mes leads: 10-20 leads
   - Mes tâches: 5-15 tâches
   - Leaderboard: Classement des commerciaux
   - Hot leads prioritaires

---

## 🔥 EN CAS D'URGENCE

Si vraiment RIEN ne fonctionne après avoir tout essayé:

1. **Désactiver TOUTES les RLS policies**:
   ```sql
   -- ATTENTION: À faire seulement en développement!
   ALTER TABLE users DISABLE ROW LEVEL SECURITY;
   ALTER TABLE products DISABLE ROW LEVEL SECURITY;
   ALTER TABLE conversions DISABLE ROW LEVEL SECURITY;
   ALTER TABLE campaigns DISABLE ROW LEVEL SECURITY;
   ```

2. **Tester si les données s'affichent maintenant**

3. **Si OUI**: Le problème vient des RLS policies
   - Réactiver RLS policy par policy
   - Identifier celle qui bloque

4. **Si NON**: Le problème vient des données manquantes ou du frontend
   - Vérifier que seed script a vraiment créé les données
   - Vérifier Console browser pour erreurs JavaScript

---

**Dernière mise à jour**: 2025-12-11
**Fichier**: `/GUIDE_RESOLUTION_DONNEES_TEST.md`
