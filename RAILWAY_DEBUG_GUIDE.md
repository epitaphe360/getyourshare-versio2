# 🔍 Guide de Debug Railway - Diagnostic Pas à Pas

## 🚨 Situation Actuelle

Le healthcheck échoue après 30 secondes. Voici comment diagnostiquer et corriger.

---

## 📊 Étape 1 : Vérifier les Logs Railway

### Comment voir les logs :

1. Allez sur Railway Dashboard
2. Cliquez sur votre service backend
3. Cliquez sur l'onglet **"Deployments"**
4. Cliquez sur le dernier déploiement (celui qui est en cours ou qui a échoué)
5. Scrollez jusqu'en bas pour voir les logs en temps réel

### Que chercher dans les logs :

#### ✅ Logs de Succès (ce que vous VOULEZ voir) :
```
Starting backend build...
Successfully installed fastapi uvicorn...
Starting server...
✅ Supabase client créé: True
✅ JWT_SECRET chargé avec succès
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### ❌ Logs d'Erreur (problèmes communs) :

**Problème 1 : Variables manquantes**
```
🔴 ERREUR CRITIQUE: JWT_SECRET non défini
⚠️  Supabase non disponible
KeyError: 'SUPABASE_URL'
```
**Solution** : Configurez les variables d'environnement (voir RAILWAY_CONFIG_URGENTE.md)

**Problème 2 : Erreur d'import**
```
ModuleNotFoundError: No module named 'fastapi'
ImportError: cannot import name 'something'
```
**Solution** : Vérifiez que requirements.txt contient toutes les dépendances

**Problème 3 : Erreur de syntaxe**
```
SyntaxError: invalid syntax
IndentationError: unexpected indent
```
**Solution** : Corrigée dans le dernier commit, redéployez

**Problème 4 : Port déjà utilisé**
```
OSError: [Errno 48] Address already in use
```
**Solution** : Railway devrait gérer ça automatiquement

---

## 🧪 Étape 2 : Test avec Serveur Minimal

Si les logs ne sont pas clairs, testez avec un serveur minimal.

### Option A : Via Railway Dashboard

1. Railway Dashboard → Service → Settings
2. Trouvez "Start Command"
3. Changez temporairement de :
   ```
   uvicorn server_complete:app --host 0.0.0.0 --port ${PORT:-8000}
   ```
   à :
   ```
   python health_server.py
   ```
4. Sauvegardez et attendez le redéploiement
5. Testez : `curl https://votre-url.up.railway.app/health`

### Option B : Via railway.toml

Créez un fichier `railway.toml.test` :
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "backend/Dockerfile"
dockerContext = "backend"

[deploy]
startCommand = "python health_server.py"
restartPolicyType = "ON_FAILURE"
healthcheckPath = "/health"
healthcheckTimeout = 100
```

Le serveur minimal (`health_server.py`) :
- ✅ Démarre TOUJOURS (pas de dépendances complexes)
- ✅ Affiche quelles variables sont configurées
- ✅ Endpoint `/env-check` pour vérifier la config

---

## 🔬 Étape 3 : Vérifier les Variables Manuellement

### Via Railway Dashboard :

1. Service → Variables
2. Vérifiez que ces variables existent :
   - ✅ SUPABASE_URL
   - ✅ SUPABASE_KEY
   - ✅ SUPABASE_SERVICE_ROLE_KEY
   - ✅ JWT_SECRET
   - ✅ PORT (automatique)

### Tester la config avec le serveur minimal :

Une fois `health_server.py` déployé, testez :
```bash
curl https://votre-url.up.railway.app/env-check
```

Résultat attendu :
```json
{
  "environment_variables": {
    "SUPABASE_URL": "SET (43 chars)",
    "SUPABASE_KEY": "SET (256 chars)",
    "SUPABASE_SERVICE_ROLE_KEY": "SET (256 chars)",
    "JWT_SECRET": "SET (86 chars)",
    "CORS_ORIGINS": "SET (65 chars)",
    "PORT": "SET (4 chars)"
  },
  "all_required_set": true
}
```

Si `all_required_set: false`, vous savez quelles variables manquent !

---

## 🛠️ Étape 4 : Tests Progressifs

### Test 1 : Le Dockerfile build-t-il ?

Dans les logs Railway, cherchez :
```
Successfully built [hash]
Successfully tagged [image]
```

Si ça échoue → Problème Dockerfile
Si ça réussit → Continuez

### Test 2 : Le serveur démarre-t-il ?

Dans les logs, cherchez :
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Si ça n'apparaît pas → L'application crash au démarrage
Si ça apparaît → Continuez

### Test 3 : Le endpoint /health répond-il ?

Depuis votre terminal :
```bash
curl -v https://getyourshare-backend-production.up.railway.app/health
```

**Résultat attendu :**
```
< HTTP/2 200
< content-type: application/json
...
{"status":"healthy","service":"ShareYourSales Backend"}
```

**Si erreur 503 (Service Unavailable)** → Le serveur n'a pas démarré
**Si timeout** → Problème réseau ou mauvais port
**Si 404** → Endpoint n'existe pas (problème de code)
**Si 200** → ✅ Tout fonctionne !

---

## 🚑 Étape 5 : Solutions par Symptôme

### Symptôme : "Service Unavailable" (503)

**Causes possibles :**
1. Variables d'environnement manquantes
2. Erreur Python au démarrage
3. Serveur crash immédiatement

**Solutions :**
1. Vérifiez les variables (Étape 3)
2. Regardez les logs pour erreurs Python
3. Testez avec `health_server.py`

### Symptôme : "Timeout" ou pas de réponse

**Causes possibles :**
1. Mauvais port
2. Application ne bind pas sur 0.0.0.0
3. Firewall

**Solutions :**
1. Vérifiez que `PORT` est bien défini automatiquement par Railway
2. Vérifiez que le code utilise `${PORT:-8000}`
3. Railway gère le firewall, mais vérifiez les settings

### Symptôme : Build échoue

**Causes possibles :**
1. requirements.txt manquants
2. Dockerfile invalide
3. Pas assez de mémoire

**Solutions :**
1. Vérifiez `backend/requirements.txt`
2. Testez le Dockerfile localement si possible
3. Upgrader le plan Railway si nécessaire

---

## 📝 Checklist de Debug

Cochez au fur et à mesure :

**Build & Deploy :**
- [ ] Le build Docker réussit (logs Railway)
- [ ] L'image est créée sans erreurs
- [ ] Le déploiement démarre

**Configuration :**
- [ ] SUPABASE_URL est défini
- [ ] SUPABASE_KEY est défini
- [ ] SUPABASE_SERVICE_ROLE_KEY est défini
- [ ] JWT_SECRET est défini (64+ chars)
- [ ] CORS_ORIGINS est défini
- [ ] PORT est automatique (ne pas le définir manuellement)

**Serveur :**
- [ ] Les logs montrent "Uvicorn running"
- [ ] Aucune erreur Python dans les logs
- [ ] Le healthcheck path est `/health` (pas `/api/health`)

**Réseau :**
- [ ] `curl https://URL/health` retourne 200
- [ ] Le JSON retourné contient `"status":"healthy"`
- [ ] Pas de timeout (< 30 secondes)

**Si tout est coché et ça ne marche pas :**
- [ ] Redéployez manuellement (Railway → Settings → Redeploy)
- [ ] Essayez le serveur minimal `health_server.py`
- [ ] Contactez le support Railway avec les logs

---

## 💡 Commandes Utiles

### Tester le healthcheck manuellement :
```bash
curl -v https://getyourshare-backend-production.up.railway.app/health
```

### Tester l'API principale :
```bash
curl https://getyourshare-backend-production.up.railway.app/api/health
```

### Tester la config (si health_server déployé) :
```bash
curl https://getyourshare-backend-production.up.railway.app/env-check
```

### Voir les headers de réponse :
```bash
curl -I https://getyourshare-backend-production.up.railway.app/health
```

---

## 🎯 Prochaines Actions

1. **MAINTENANT** : Vérifiez les logs Railway
2. **Si erreurs de variables** : Configurez les variables (RAILWAY_CONFIG_URGENTE.md)
3. **Si pas de logs clairs** : Déployez `health_server.py` pour tester
4. **Si ça marche avec health_server** : Revenez à `server_complete.py`
5. **Si ça ne marche toujours pas** : Partagez les logs complets

---

## 📞 Informations à Partager si Besoin d'Aide

Si vous avez besoin d'aide supplémentaire, partagez :
1. Les 50 dernières lignes des logs Railway
2. Le résultat de `curl -v https://votre-url/health`
3. Capture d'écran de Railway → Variables
4. Message d'erreur exact du healthcheck

**Avec ces infos, on pourra diagnostiquer précisément le problème ! 🔍**
