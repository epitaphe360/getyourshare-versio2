# ✅ Fix pour Déploiement Railway - Healthcheck Failure

## Problème Identifié
Les déploiements échouaient au healthcheck `/health` avec "service unavailable" car:
1. ❌ Dockerfile root utilisait `sh -c` avec variables shell qui ne fonctionnent pas bien sur Railway
2. ❌ Procfile référençait un module `server:app` qui n'existe plus
3. ⚠️ Peut-être des variables d'environnement manquantes

## ✅ Solutions Appliquées

### 1. Dockerfile Root Corrigé
**Fichier**: `Dockerfile`
- ✅ Remplacé `sh -c "uvicorn ..."` par `python run.py`
- ✅ Ajouté `PYTHONUNBUFFERED=1` pour voir les logs en temps réel
- ✅ Ajouté HEALTHCHECK docker pour une meilleure détection
- ✅ run.py gère correctement les variables d'env (PORT, etc.)

### 2. Procfile Mis à Jour
**Fichier**: `Procfile`
- ✅ Changé de: `uvicorn server:app` → `python run.py`
- ✅ run.py gère automatiquement le PORT depuis l'env

### 3. run.py (Backend)
Utilise déjà une approche robuste:
```python
port = int(os.environ.get("PORT", "8000"))
uvicorn.run("server_complete:app", host="0.0.0.0", port=port)
```

## 📋 Checklist Railway Dashboard

✅ **Vérifiez que ces variables sont configurées dans Railway:**

### Obligatoires pour démarrage
- [ ] `PORT=8000` (ou 8001 selon vos tests)
- [ ] `ENVIRONMENT=production`
- [ ] `PYTHONUNBUFFERED=1`

### Critiques pour l'app
- [ ] `SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co`
- [ ] `SUPABASE_KEY=eyJhbGciOi...` (clé anonyme)
- [ ] `SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...`
- [ ] `JWT_SECRET=bFeUjfAZnOEK...` (minimum 32 caractères)

### Optionnels mais recommandés
- [ ] `APP_ENV=production`
- [ ] `LOG_LEVEL=INFO`
- [ ] `CORS_ORIGINS=*` ou spécifiez vos domaines

## 🚀 Étapes pour Redéployer

### Option 1: Via Railway Dashboard
1. Allez à votre project "Getyourshare backend"
2. Cliquez sur "Redeploy" ou poussez un nouveau commit
3. Railway détectera le nouveau Dockerfile
4. Attendez que les logs montrent `✅ Supabase client créé`

### Option 2: Via CLI
```bash
cd backend
railway link  # Si nécessaire
railway up
```

## 📊 Vérification du Déploiement

**Une fois déployé**, vérifiez:

1. **Logs sont visibles**:
   - Cherchez: "🚀 Starting ShareYourSales Backend"
   - Cherchez: "✅ Supabase client créé: True"

2. **Health endpoint répond**:
   - URL: `https://getyourshare-backend-production.up.railway.app/health`
   - Doit retourner: `{"status": "healthy", "service": "ShareYourSales Backend"}`

3. **Pas d'erreurs dans les logs**:
   - Cherchez "ERROR" ou "CRITICAL"
   - Les "WARNING" avec services optionnels (email, etc.) sont OK

## 🔧 Si Ça Échoue Encore

### Debug Step 1: Vérifier les Logs
```
Railway Dashboard 
→ Your Project 
→ Deployments 
→ Latest Failed Deployment 
→ Deploy Logs
```

### Debug Step 2: Chercher l'erreur réelle
Regardez pour:
- `ImportError`: Une dépendance manquante
- `FileNotFoundError`: Fichier mal copié par Docker
- `AttributeError`: Code cassé
- `NameError`: Variables d'env manquantes

### Debug Step 3: Tester Localement
```bash
# À la racine du projet
docker build -t getyourshare:test .
docker run -e PORT=8000 -e SUPABASE_URL=... -e SUPABASE_KEY=... -e JWT_SECRET=... -p 8000:8000 getyourshare:test
```

## 📝 Fichiers Modifiés
- ✅ `Dockerfile` - Corrigé la commande CMD
- ✅ `Procfile` - Mis à jour pour utiliser run.py
- ✅ `backend/run.py` - Déjà correct, gère les variables en Python

## 🎯 Prochaines Étapes
1. Vérifiez que les variables d'env sont dans Railway
2. Poussez un nouveau commit ou redéployez
3. Attendez 5-10 minutes pour le build et déploiement
4. Vérifiez le healthcheck endpoint
5. Si erreur, consultez les logs détaillés

---
**Date**: 2 janvier 2026
**Statut**: ✅ Corrections appliquées, prêt pour redéploiement
