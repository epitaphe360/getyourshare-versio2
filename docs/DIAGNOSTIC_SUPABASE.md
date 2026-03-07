# 🔴 DIAGNOSTIC CRITIQUE: Problème d'Accès Base de Données Supabase

**Date:** 2025-11-10
**Statut:** ⚠️ BLOQUANT - Nécessite action immédiate

---

## 📊 Résumé Exécutif

Le backend démarre **avec succès** mais **TOUTES les requêtes à la base de données** retournent une erreur `403 Forbidden - Access denied`. Même avec le `service_role_key` (droits admin complets), l'accès est refusé.

## ✅ Ce Qui Fonctionne

1. **Backend lance correctement**
   ```
   INFO: Application startup complete.
   ✅ Scheduler LEADS démarré avec succès!
   ✅ Tous les endpoints chargés
   ```

2. **Dépendances installées**
   - Toutes les dépendances Python sont installées
   - Imports corrigés et fonctionnels

3. **Configuration Supabase présente**
   ```
   SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=[PRÉSENTE]
   SUPABASE_ANON_KEY=[PRÉSENTE]
   ```

## ❌ Problème Identifié

### Erreur Type
```
HTTP/2 403 Forbidden
error={'message': 'JSON could not be generated', 'code': 403,
       'hint': 'Refer to full message for details',
       'details': "b'Access denied'"}
```

### Tables Affectées
- ❌ `users` table: 403 Forbidden
- ❌ `products` table: 403 Forbidden
- ❌ `v_products_full` view: 403 Forbidden
- ⚠️ **Toutes les tables retournent 403**

### Requête Exemple
```
GET https://iamezkmapbhlhhvvsits.supabase.co/rest/v1/products
Headers: apikey=service_role_key
Response: 403 Forbidden - Access denied
```

## 🔍 Causes Possibles

### 1. Projet Supabase Pausé/Désactivé ⚠️
Le projet Supabase peut être en pause si:
- Plan gratuit et inactif depuis 7+ jours
- Limite de requêtes dépassée
- Problème de facturation

**Solution:** Vérifier statut sur https://app.supabase.com/project/iamezkmapbhlhhvvsits

### 2. Base de Données Non Initialisée
Les tables n'existent peut-être pas encore dans la base.

**Test:**
```bash
# Se connecter à Supabase Dashboard
# Table Editor → Vérifier présence des tables
```

Tables attendues:
- users
- products
- merchants
- campaigns
- leads
- deposits
- agreements

### 3. Row Level Security (RLS) Trop Restrictif
Même si service_role devrait bypasser RLS, des configurations peuvent bloquer.

**Solution:**
```sql
-- Temporairement désactiver RLS pour tester
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
```

### 4. Clés API Invalides/Expirées
Les clés dans .env peuvent être incorrectes.

**Vérification:**
1. Aller sur Supabase Dashboard
2. Settings → API
3. Comparer les clés avec .env

### 5. Problème Réseau/Firewall
Le conteneur Docker peut ne pas avoir accès externe.

**Test:**
```bash
curl https://iamezkmapbhlhhvvsits.supabase.co
# Devrait retourner une page HTML, pas une erreur réseau
```

## 🛠️ Plan d'Action - ACTIONS REQUISES

### PRIORITÉ 1: Vérifier Projet Actif
1. Ouvrir https://app.supabase.com/project/iamezkmapbhlhhvvsits
2. Vérifier status du projet
3. Si "Paused" → Cliquer "Restore Project"

### PRIORITÉ 2: Vérifier Tables Existent
1. Dans Supabase Dashboard
2. Table Editor (menu gauche)
3. Vérifier que les tables users, products, etc. existent
4. Si aucune table → Exécuter les migrations SQL

### PRIORITÉ 3: Vérifier Clés API
1. Settings → API
2. Copier `service_role` key
3. Comparer avec `SUPABASE_SERVICE_ROLE_KEY` dans .env
4. Si différent → Mettre à jour .env

### PRIORITÉ 4: Tester RLS
Si les tables existent:
```sql
-- Dans SQL Editor
SELECT * FROM products LIMIT 1;
-- Devrait retourner des données ou "table vide", pas 403

-- Désactiver temporairement RLS
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
```

### PRIORITÉ 5: Migrations Base de Données
Si les tables n'existent pas, exécuter:
```bash
# Si vous avez des fichiers migration
cd backend
# Chercher schéma SQL
find . -name "*.sql" -o -name "schema.sql"
```

## 📝 Tests de Validation

Une fois le problème résolu, tester:

```bash
# Test 1: Connexion basique
curl -H "apikey: YOUR_SERVICE_ROLE_KEY" \
     https://iamezkmapbhlhhvvsits.supabase.co/rest/v1/users?select=id&limit=1

# Test 2: Endpoint marketplace
curl http://localhost:8000/api/marketplace/products

# Test 3: Health check
curl http://localhost:8000/health
```

## 🔗 Ressources Utiles

- **Supabase Dashboard:** https://app.supabase.com/project/iamezkmapbhlhhvvsits
- **Documentation RLS:** https://supabase.com/docs/guides/auth/row-level-security
- **API Settings:** https://app.supabase.com/project/iamezkmapbhlhhvvsits/settings/api
- **Database:** https://app.supabase.com/project/iamezkmapbhlhhvvsits/editor

## 💡 Note Importante

**Le backend fonctionne correctement** - c'est uniquement un problème de configuration/accès Supabase. Une fois résolu:
- Tous les endpoints fonctionneront
- Le marketplace affichera les produits
- L'authentification sera opérationnelle

## 📞 Support

Si le problème persiste après ces vérifications:
1. Exporter les logs Supabase (Dashboard → Logs)
2. Vérifier quota du plan gratuit
3. Contacter support Supabase si nécessaire

---

**Status:** EN ATTENTE D'ACTION UTILISATEUR
