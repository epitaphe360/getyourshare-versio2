# 🔧 GUIDE DE DÉBOGAGE VERCEL - Pourquoi ça ne marche pas

## 🚨 PROBLÈMES POSSIBLES

### Problème 1 : Vercel n'a pas les variables d'environnement dans le Dashboard

**LE PLUS PROBABLE** ⚠️

Le fichier `vercel.json` contient les variables, MAIS Vercel nécessite aussi qu'elles soient configurées dans le **Dashboard Vercel**.

#### ✅ SOLUTION - Configurer les variables dans Vercel Dashboard

1. Allez sur https://vercel.com/getyourshares-projects/getyourshare
2. Cliquez sur **Settings** → **Environment Variables**
3. Ajoutez ces variables pour **Production, Preview, et Development** :

```bash
# CRITIQUE - Sans cette variable, le frontend ne sait pas où est le backend
REACT_APP_BACKEND_URL=https://getyourshare-backend-production.up.railway.app

# Autres variables importantes
REACT_APP_API_URL=https://getyourshare-backend-production.up.railway.app/api
REACT_APP_SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo
REACT_APP_ENV=production
REACT_APP_DEBUG=false
DISABLE_ESLINT_PLUGIN=true
```

4. Après avoir ajouté les variables, **REDÉPLOYEZ** votre application :
   - Allez dans **Deployments**
   - Cliquez sur les 3 points (...) du dernier déploiement
   - Sélectionnez **Redeploy**

---

### Problème 2 : Railway n'a pas redéployé le backend avec les corrections CORS

#### Comment vérifier ?

1. Allez sur https://railway.app/ → Votre projet backend
2. Vérifiez la date du dernier déploiement
3. Le dernier déploiement doit être **APRÈS** le commit `e4a3e60` (corrections CORS)

#### Comment voir les commits ?
```bash
# Nos commits récents :
4aad195 - fix: Add missing REACT_APP_BACKEND_URL to Vercel configuration
e4a3e60 - fix: Add Vercel URL support to CORS configuration
```

#### ✅ SOLUTION - Forcer un redéploiement Railway

**Option A - Depuis Railway Dashboard:**
1. Allez sur https://railway.app/
2. Sélectionnez votre projet backend
3. Cliquez sur **Settings** → **Redeploy**

**Option B - Push un nouveau commit:**
```bash
# Railway redéploie automatiquement à chaque push
git push origin claude/fix-cors-errors-01DWJmJ38egPgfnecoqDQpJ5
```

---

### Problème 3 : Les variables d'environnement Railway sont manquantes

#### ✅ SOLUTION - Vérifier les variables Railway

1. Allez sur https://railway.app/ → Votre projet backend
2. Cliquez sur **Variables**
3. Vérifiez que ces variables existent :

```bash
# Variables CRITIQUES :
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc... (votre clé complète)
SUPABASE_ANON_KEY=eyJhbGc... (votre clé complète)
JWT_SECRET=bFeU... (votre clé complète)
SECRET_KEY=bFeU... (votre clé complète)

# Variables RECOMMANDÉES (pour CORS) :
ENVIRONMENT=production
ENV=production
FRONTEND_URL=https://getyourshare.com
PRODUCTION_URL=https://www.getyourshare.com
```

Si elles manquent, ajoutez-les et Railway redéploiera automatiquement.

---

### Problème 4 : Le déploiement Vercel est basé sur un vieux commit

#### Comment vérifier ?

1. Allez sur https://vercel.com/getyourshares-projects/getyourshare
2. Cliquez sur votre dernier déploiement
3. Regardez le **Git Commit SHA**
4. Il doit être `4aad195` ou plus récent

#### ✅ SOLUTION - Trigger un nouveau déploiement

**Option A - Redéployer depuis Vercel:**
1. Allez dans **Deployments**
2. Cliquez sur les 3 points du dernier déploiement
3. Sélectionnez **Redeploy with existing Build Cache** ou **Redeploy without Cache**

**Option B - Push un nouveau commit:**
```bash
# Vercel redéploie automatiquement à chaque push
git push origin claude/fix-cors-errors-01DWJmJ38egPgfnecoqDQpJ5
```

---

## 🧪 TESTS DE DIAGNOSTIC

### Test 1 : Vérifier que Vercel a la bonne variable

Une fois le site déployé, ouvrez la console du navigateur (F12) sur votre site Vercel et tapez :

```javascript
// Ouvrir la console (F12) et taper :
console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL);
console.log('API URL:', process.env.REACT_APP_API_URL);
```

**Résultat attendu:**
```
Backend URL: https://getyourshare-backend-production.up.railway.app
API URL: https://getyourshare-backend-production.up.railway.app/api
```

**Si vous voyez `undefined`:** Les variables d'environnement ne sont pas configurées dans Vercel Dashboard → Retour au Problème 1

---

### Test 2 : Vérifier que Railway accepte les requêtes de Vercel

Ouvrez un terminal et exécutez :

```bash
curl -X OPTIONS \
  https://getyourshare-backend-production.up.railway.app/api/auth/login \
  -H "Origin: https://getyourshare-7h1z5006j-getyourshares-projects.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -i
```

**Résultat attendu dans les headers:**
```
Access-Control-Allow-Origin: https://getyourshare-7h1z5006j-getyourshares-projects.vercel.app
Access-Control-Allow-Credentials: true
```

**Si vous ne voyez pas ces headers:** Railway n'a pas redéployé avec les corrections CORS → Retour au Problème 2

---

### Test 3 : Vérifier que Railway est en ligne

Ouvrez votre navigateur et allez sur :
```
https://getyourshare-backend-production.up.railway.app/health
```

**Résultat attendu:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T...",
  "service": "ShareYourSales API",
  "database": "Supabase Connected"
}
```

**Si vous voyez une erreur 503 ou timeout:** Railway est down ou n'a pas démarré correctement

---

### Test 4 : Vérifier les logs Railway

1. Allez sur https://railway.app/ → Votre projet backend
2. Cliquez sur **Logs**
3. Recherchez cette ligne au démarrage :

```
CORS allowed origins: ['http://localhost:3000', ..., 'https://getyourshare-7h1z5006j-getyourshares-projects.vercel.app']
```

**Si vous voyez cette ligne:** CORS est correctement configuré ✅

**Si vous ne voyez PAS cette ligne:** Railway utilise encore l'ancienne version → Forcer un redéploiement (Problème 2)

---

## 🎯 CHECKLIST DE RÉSOLUTION

Suivez ces étapes dans l'ordre :

- [ ] **Étape 1** : Configurer les variables d'environnement dans Vercel Dashboard (Problème 1)
- [ ] **Étape 2** : Redéployer Vercel après avoir ajouté les variables
- [ ] **Étape 3** : Vérifier que Railway a redéployé avec les corrections CORS (Problème 2)
- [ ] **Étape 4** : Vérifier les variables d'environnement Railway (Problème 3)
- [ ] **Étape 5** : Tester avec Test 1 (console.log des variables)
- [ ] **Étape 6** : Tester avec Test 2 (curl CORS)
- [ ] **Étape 7** : Tester avec Test 3 (/health endpoint)
- [ ] **Étape 8** : Vérifier les logs Railway (Test 4)
- [ ] **Étape 9** : Essayer de se connecter sur le site Vercel

---

## 📱 ERREURS COMMUNES ET SOLUTIONS

### Erreur : "Failed to load resource: net::ERR_FAILED"

**Cause:** Le frontend essaie de contacter une URL invalide ou undefined

**Solution:** Vérifier que `REACT_APP_BACKEND_URL` est défini dans Vercel Dashboard (Problème 1)

---

### Erreur : "No 'Access-Control-Allow-Origin' header"

**Cause:** Railway n'a pas les corrections CORS ou n'a pas redéployé

**Solution:** Vérifier que Railway a redéployé (Problème 2) et voir les logs

---

### Erreur : "401 Unauthorized" sur /api/auth/me

**Cause Possible 1:** Vous n'êtes pas connecté (normal au premier chargement)

**Cause Possible 2:** Les cookies ne sont pas envoyés correctement (problème CORS)

**Solution:** Vérifier Test 2 (CORS headers) et que `Access-Control-Allow-Credentials: true` est présent

---

### Erreur : "Network Error" dans la console

**Cause:** Le backend Railway est down ou l'URL est incorrecte

**Solution:**
1. Vérifier Test 3 (/health endpoint)
2. Vérifier les logs Railway
3. Vérifier que l'URL Railway est correcte : `https://getyourshare-backend-production.up.railway.app`

---

## 🚀 APRÈS AVOIR TOUT CONFIGURÉ

Une fois que tout est configuré correctement, voici ce qui devrait se passer :

1. **Au chargement du site Vercel:**
   - Le frontend charge avec les bonnes variables d'environnement
   - Il tente de vérifier la session : `GET /api/auth/me`
   - Si pas connecté → Redirige vers login (normal)

2. **À la connexion:**
   - Le frontend envoie : `POST /api/auth/login` avec email/password
   - Railway répond avec les cookies httpOnly
   - L'utilisateur est connecté et redirigé vers le dashboard

3. **Sur le dashboard:**
   - Le frontend charge les données : products, stats, etc.
   - Toutes les requêtes passent sans erreur CORS
   - Les données Supabase s'affichent correctement

---

## 🆘 SI RIEN NE FONCTIONNE

Si après avoir suivi tout ce guide ça ne marche toujours pas, donne-moi :

1. **Les erreurs dans la console Vercel** (F12 → Console)
2. **Les erreurs dans l'onglet Network** (F12 → Network → cliquer sur une requête rouge)
3. **Les logs Railway** (premiers 50 lignes au démarrage)
4. **Le résultat de Test 1** (console.log des variables)
5. **Le résultat de Test 2** (curl CORS)

Je pourrai alors diagnostiquer le problème exact.

---

## 📋 RÉSUMÉ RAPIDE

**Le problème principal est probablement :** Les variables d'environnement ne sont pas dans le Dashboard Vercel

**Solution rapide :**
1. Allez sur Vercel → Settings → Environment Variables
2. Ajoutez `REACT_APP_BACKEND_URL=https://getyourshare-backend-production.up.railway.app`
3. Redéployez

**Ça devrait suffire si Railway a déjà redéployé le backend avec les corrections CORS.**
