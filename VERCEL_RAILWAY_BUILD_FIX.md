# 🔧 GUIDE COMPLET: Corriger les Problèmes de Build Vercel & Railway

**Date**: 2025-12-08
**Status**: ⚠️ Build Failures Need Fixing

---

## 🎯 PROBLÈMES COMMUNS ET SOLUTIONS

### Problem 1: Build Timeout ⏱️

**Symptôme**: Le build dépasse le temps limite (5-10 minutes)

**Causes**:
- Trop de dépendances
- Build process lent
- Tests qui tournent pendant le build

**Solution**:

```json
// frontend/package.json - Optimiser les scripts
{
  "scripts": {
    "build": "DISABLE_ESLINT_PLUGIN=true react-scripts build",
    "build:vercel": "npm run build",
    "build:railway": "npm ci && npm run build"
  }
}
```

---

### Problem 2: Out of Memory (OOM) 💾

**Symptôme**: `JavaScript heap out of memory`

**Solution**:

```json
// frontend/package.json
{
  "scripts": {
    "build": "NODE_OPTIONS='--max-old-space-size=4096' react-scripts build"
  }
}
```

---

### Problem 3: Missing Environment Variables 🔐

**Symptôme**: `process.env.REACT_APP_XXX is undefined`

**Solution Vercel**:

Dans Vercel Dashboard:
1. Settings → Environment Variables
2. Ajouter toutes les variables de `.env.production`

**Solution Railway**:

```bash
# Via Railway CLI
railway variables set REACT_APP_API_URL=https://your-backend.railway.app/api
railway variables set REACT_APP_SUPABASE_URL=https://xxx.supabase.co
```

Ou via Railway Dashboard:
1. Variables → New Variable
2. Ajouter chaque variable

---

### Problem 4: Wrong Node Version 🔧

**Symptôme**: `Unsupported engine` or incompatibility errors

**Solution**:

```json
// frontend/package.json
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
```

```toml
# frontend/railway.toml
[phases.setup]
nixPkgs = ["nodejs-18_x"]
```

---

## 🎯 CONFIGURATION OPTIMISÉE VERCEL

### vercel.json (Mise à jour recommandée)

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app",
  "installCommand": "npm ci",
  "devCommand": "npm start",

  "build": {
    "env": {
      "DISABLE_ESLINT_PLUGIN": "true",
      "GENERATE_SOURCEMAP": "false",
      "NODE_OPTIONS": "--max-old-space-size=4096"
    }
  },

  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://getyourshare-backend-production.up.railway.app/api/:path*"
    }
  ],

  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    },
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],

  "env": {
    "REACT_APP_API_URL": "https://getyourshare-backend-production.up.railway.app/api",
    "REACT_APP_BACKEND_URL": "https://getyourshare-backend-production.up.railway.app",
    "REACT_APP_SUPABASE_URL": "https://iamezkmapbhlhhvvsits.supabase.co",
    "REACT_APP_NAME": "ShareYourSales",
    "REACT_APP_VERSION": "2.0.0",
    "REACT_APP_ENV": "production",
    "REACT_APP_FEATURE_AI": "true",
    "REACT_APP_FEATURE_ANALYTICS": "true",
    "REACT_APP_FEATURE_LIVE_CHAT": "true",
    "REACT_APP_DEBUG": "false",
    "DISABLE_ESLINT_PLUGIN": "true",
    "GENERATE_SOURCEMAP": "false"
  },

  "github": {
    "enabled": true,
    "autoAlias": true,
    "silent": false
  }
}
```

---

## 🚂 CONFIGURATION OPTIMISÉE RAILWAY

### railway.toml (Mise à jour recommandée)

```toml
[build]
builder = "NIXPACKS"
watchPatterns = ["**/*.js", "**/*.jsx", "**/*.json"]

[phases.setup]
nixPkgs = ["nodejs-18_x", "npm-9_x"]

[phases.install]
cmds = [
  "npm ci --prefer-offline --no-audit",
  "npm cache clean --force"
]

[phases.build]
cmds = [
  "export DISABLE_ESLINT_PLUGIN=true",
  "export GENERATE_SOURCEMAP=false",
  "export NODE_OPTIONS='--max-old-space-size=4096'",
  "npm run build"
]

[start]
cmd = "npx serve -s build -l $PORT --no-clipboard"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

---

## 🔧 BACKEND RAILWAY CONFIG

### backend/railway.toml (Créer ce fichier)

```toml
[build]
builder = "NIXPACKS"

[phases.setup]
nixPkgs = ["python39", "postgresql"]

[phases.install]
cmds = [
  "pip install --upgrade pip",
  "pip install -r requirements.txt"
]

[phases.build]
cmds = [
  "python -m compileall ."
]

[start]
cmd = "uvicorn server_complete:app --host 0.0.0.0 --port $PORT --workers 4"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[env]
PYTHONUNBUFFERED = "1"
PYTHON DontWriteBytecode = "1"
```

---

## 📋 CHECKLIST DE DÉPLOIEMENT

### Avant de Déployer

#### Frontend
- [ ] Vérifier que `package.json` a les bons scripts
- [ ] Vérifier `engines` dans package.json (Node >= 18)
- [ ] S'assurer que `.env.production` est correctement configuré
- [ ] Tester le build localement: `npm run build`
- [ ] Vérifier que le dossier `build` se crée correctement
- [ ] Vérifier les variables d'environnement dans Vercel/Railway

#### Backend
- [ ] S'assurer que `requirements.txt` est à jour
- [ ] Vérifier que `server_complete.py` existe et fonctionne
- [ ] Tester localement: `python server_complete.py`
- [ ] Vérifier endpoint `/health`
- [ ] S'assurer que les variables d'env sont configurées (SUPABASE_URL, JWT_SECRET, etc.)
- [ ] Migrations SQL appliquées sur la DB de production

---

## 🐛 DEBUGGING BUILD ERRORS

### Erreur: "Command failed with exit code 137"

**Cause**: Out of Memory (OOM)

**Solution**:
```json
// package.json
{
  "scripts": {
    "build": "NODE_OPTIONS='--max-old-space-size=4096' GENERATE_SOURCEMAP=false react-scripts build"
  }
}
```

---

### Erreur: "Module not found: Can't resolve 'xxx'"

**Cause**: Dépendance manquante

**Solution**:
```bash
# Vérifier que la dépendance est dans package.json
npm install xxx --save

# Ou nettoyer et réinstaller
rm -rf node_modules package-lock.json
npm install
```

---

### Erreur: "Failed to compile"

**Cause**: Erreurs ESLint ou TypeScript

**Solution**:
```json
// package.json
{
  "scripts": {
    "build": "DISABLE_ESLINT_PLUGIN=true react-scripts build"
  }
}
```

---

### Erreur Railway: "Build timed out after 10 minutes"

**Solution**:

Dans Railway Dashboard:
1. Settings → Deployment
2. Build Timeout: Augmenter à 15 ou 20 minutes
3. Ou optimiser le build (voir ci-dessus)

---

### Erreur Vercel: "Function Execution Timeout"

**Solution**:

Dans Vercel Dashboard:
1. Settings → Functions
2. Function Max Duration: 60s (plan Pro)
3. Ou optimiser les API calls

---

## 🎯 COMMANDES DE TEST LOCAL

### Frontend

```bash
cd frontend

# Nettoyer tout
rm -rf node_modules package-lock.json build

# Réinstaller
npm install

# Build de test
npm run build

# Vérifier la taille du build
du -sh build/

# Tester localement
npx serve -s build -l 3000
```

### Backend

```bash
cd backend

# Nettoyer cache Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Réinstaller dépendances
pip install -r requirements.txt

# Tester le serveur
python server_complete.py

# Tester health check
curl http://localhost:8000/health
```

---

## 🚀 DÉPLOIEMENT ÉTAPE PAR ÉTAPE

### Déployer le Backend (Railway)

```bash
# 1. Installer Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Link au projet
railway link

# 4. Vérifier les variables
railway variables

# 5. Ajouter variables manquantes
railway variables set SUPABASE_URL=https://xxx.supabase.co
railway variables set SUPABASE_KEY=eyJxxx...
railway variables set JWT_SECRET=xxx

# 6. Déployer
railway up

# 7. Vérifier les logs
railway logs
```

### Déployer le Frontend (Vercel)

```bash
# 1. Installer Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Link au projet
vercel link

# 4. Configurer les variables (via dashboard ou CLI)
vercel env add REACT_APP_API_URL production
# Entrer: https://getyourshare-backend-production.up.railway.app/api

# 5. Déployer
vercel --prod

# 6. Vérifier
vercel inspect
```

---

## 📊 MONITORING POST-DÉPLOIEMENT

### Vérifications Essentielles

```bash
# Frontend
curl https://your-app.vercel.app
curl https://your-app.vercel.app/api/health # Should proxy to backend

# Backend
curl https://your-backend.railway.app/health
curl https://your-backend.railway.app/api/analytics/overview # Test endpoint

# Check logs
vercel logs your-app
railway logs
```

---

## ⚠️ PROBLÈMES CONNUS

### 1. CORS Errors après déploiement

**Solution**:
```python
# backend/server_complete.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. API Calls failing in production

**Vérifier**:
- Les URLs dans `vercel.json` rewrites
- Les variables REACT_APP_API_URL
- Les CORS settings du backend

### 3. WebSocket connection failing

**Solution**:
```javascript
// frontend/src/utils/websocket.js
const WS_URL = process.env.REACT_APP_BACKEND_URL
  .replace('https://', 'wss://')
  .replace('http://', 'ws://');

const socket = new WebSocket(`${WS_URL}/api/live-chat/ws/${userId}`);
```

---

## 📞 SUPPORT

### Si le build échoue toujours:

1. **Vérifier les logs**:
   - Railway: `railway logs --deployment`
   - Vercel: Dashboard → Deployments → Click deployment → View build logs

2. **Tester localement** d'abord:
   ```bash
   # Frontend
   npm run build

   # Backend
   python server_complete.py
   ```

3. **Vérifier les variables d'environnement**:
   - Railway: `railway variables`
   - Vercel: Dashboard → Settings → Environment Variables

4. **Stack Overflow / Discord**:
   - Railway Discord: https://discord.gg/railway
   - Vercel Discord: https://vercel.com/discord

---

## ✅ STATUT FINAL

Une fois tout configuré correctement, vous devriez avoir:

- ✅ Frontend déployé sur Vercel
- ✅ Backend déployé sur Railway
- ✅ API calls fonctionnels (via rewrites)
- ✅ Variables d'environnement configurées
- ✅ Health checks passants
- ✅ Logs accessibles

---

**Guide créé le**: 2025-12-08
**Version**: 1.0
**Status**: ✅ Ready to Use
