# Configuration Déploiement Vercel - ShareYourSales Frontend

## 🚀 Variables d'environnement à configurer dans Vercel

### Dans Vercel Dashboard → Settings → Environment Variables

Ajoutez ces variables pour **Production** :

```env
# Backend API
REACT_APP_API_URL=https://getyourshare-backend-production.up.railway.app/api
REACT_APP_BACKEND_URL=https://getyourshare-backend-production.up.railway.app

# Supabase
REACT_APP_SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo

# Application
REACT_APP_NAME=ShareYourSales
REACT_APP_VERSION=1.0.0
REACT_APP_ENV=production

# Features
REACT_APP_FEATURE_MLM=false
REACT_APP_FEATURE_ANALYTICS=true
REACT_APP_FEATURE_AI_MARKETING=false

# Build settings
DISABLE_ESLINT_PLUGIN=true
REACT_APP_DEBUG=false
```

## 📋 Étapes de déploiement

### 1. Dans Vercel Dashboard

1. **Import Project** depuis GitHub
   - Repository : `epitaphe360/getyourshare-versio2`
   - Root Directory : `frontend`
   - Framework Preset : **Create React App**

2. **Build & Development Settings**
   - Build Command : `npm run build`
   - Output Directory : `build`
   - Install Command : `npm install`
   - Development Command : `npm start`

3. **Environment Variables**
   - Copiez toutes les variables ci-dessus dans la section Environment Variables
   - Scope : **Production**

4. **Git Configuration**
   - ✅ Auto-deploy enabled (deploy on push to main)
   - Branch : `main` ou votre branche de production

### 2. Dans Railway Backend - Mise à jour CORS

**Important** : Ajoutez le domaine Vercel dans la variable `CORS_ORIGINS` de Railway :

1. Allez dans Railway → Service Backend → Variables
2. Trouvez ou créez la variable `CORS_ORIGINS`
3. Valeur :
```
https://votre-app.vercel.app,http://localhost:3000,https://considerate-luck-production.up.railway.app
```

**Note** : Remplacez `votre-app.vercel.app` par votre vrai domaine Vercel une fois déployé.

### 3. Après le premier déploiement Vercel

Une fois Vercel déployé, vous obtiendrez un domaine comme :
- `shareyoursales.vercel.app` (production)
- `shareyoursales-git-main.vercel.app` (preview)

**Action requise** :
1. Copiez le domaine de production Vercel
2. Ajoutez-le dans Railway → Backend → Variable `CORS_ORIGINS`
3. Railway redéploiera automatiquement

## ✅ Vérification

Une fois tout configuré, testez :

1. **Frontend Vercel** : Ouvrez votre app Vercel
2. **Connexion Backend** : Essayez de vous connecter
3. **Console Browser** : Vérifiez qu'il n'y a pas d'erreurs CORS
4. **Network Tab** : Les requêtes vers Railway doivent réussir (status 200)

## 🔧 Commandes Git pour déploiement auto

Le déploiement Vercel est automatique sur push. Pour déployer :

```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel détectera le push et déploiera automatiquement.

## 🌐 Domaine Custom (optionnel)

Pour ajouter votre propre domaine :
1. Vercel Dashboard → Settings → Domains
2. Ajoutez votre domaine
3. Configurez les DNS selon les instructions Vercel
4. Mettez à jour `CORS_ORIGINS` dans Railway avec votre domaine custom
