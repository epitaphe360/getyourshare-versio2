# 🚀 Guide de Déploiement Vercel - ShareYourSales

## ✅ Configuration Préparée

Tous les fichiers de configuration ont été créés automatiquement :

- ✅ `vercel.json` - Configuration Vercel complète
- ✅ `frontend/.env.production` - Variables d'environnement production
- ✅ Backend Railway configuré : `getyourshare-backend-production.up.railway.app`

---

## 🎯 Option 1 : Déploiement via Interface Web Vercel (RECOMMANDÉ)

### Étape 1 : Connecter votre dépôt GitHub

1. Allez sur [vercel.com](https://vercel.com)
2. Cliquez sur **"Add New Project"**
3. Sélectionnez **"Import Git Repository"**
4. Choisissez votre repo : `epitaphe360/getyourshare-versio2`

### Étape 2 : Configuration du Projet

Vercel va détecter automatiquement la configuration depuis `vercel.json`, mais vérifiez :

| Paramètre | Valeur |
|-----------|--------|
| **Framework Preset** | Create React App |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `build` |
| **Install Command** | `npm install` |

### Étape 3 : Variables d'Environnement

Les variables sont déjà dans `vercel.json`, mais vous pouvez les ajouter manuellement :

```bash
REACT_APP_API_URL=https://getyourshare-backend-production.up.railway.app/api
REACT_APP_SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REACT_APP_NAME=ShareYourSales
REACT_APP_VERSION=1.0.0
REACT_APP_ENV=production
DISABLE_ESLINT_PLUGIN=true
```

### Étape 4 : Déployer

Cliquez sur **"Deploy"** et attendez 2-3 minutes.

✅ Votre URL sera : `https://getyourshare-versio2.vercel.app`

---

## 🎯 Option 2 : Déploiement via CLI Vercel

### Obtenir un Token Valide

Le token fourni (`O0sBOF9tJcu74F9w9yKfuScF`) semble invalide.

Pour obtenir un nouveau token :

```bash
vercel login
```

Ou générez un token sur :
👉 https://vercel.com/account/tokens

### Déployer avec le CLI

```bash
# Se connecter
vercel login

# Aller dans le dossier frontend
cd frontend

# Lier le projet (première fois)
vercel link

# Déployer en production
vercel --prod
```

---

## 🎯 Option 3 : Déploiement Automatique (CI/CD)

Le fichier `vercel.json` à la racine configure :

- ✅ Build automatique du frontend
- ✅ Variables d'environnement
- ✅ Routing SPA (Single Page Application)
- ✅ Headers de sécurité
- ✅ Cache optimisé

### Configuration Automatique GitHub

1. Push votre code sur GitHub :
   ```bash
   git push origin claude/fix-dockerfile-backend-path-013XYT37munJSQSYVTq1BnTs
   ```

2. Allez sur Vercel Dashboard
3. Importez le repo
4. Chaque push déclenchera un déploiement automatique ✨

---

## 🔐 Vérification Post-Déploiement

Une fois déployé, testez :

### 1. Healthcheck Backend
```bash
curl https://getyourshare-backend-production.up.railway.app/health
```

Devrait retourner :
```json
{"status": "healthy", "service": "ShareYourSales Backend"}
```

### 2. API Backend
```bash
curl https://getyourshare-backend-production.up.railway.app/api/health
```

### 3. Frontend Vercel
Visitez votre URL Vercel et vérifiez :
- ✅ Page d'accueil charge
- ✅ Pas d'erreurs console
- ✅ API calls fonctionnent

---

## 🐛 Troubleshooting

### Erreur : "Module not found"
```bash
cd frontend
npm install
vercel --prod
```

### Erreur : "Build failed"
Vérifiez les logs Vercel et assurez-vous que :
- ✅ `DISABLE_ESLINT_PLUGIN=true` est défini
- ✅ Toutes les dépendances sont dans `package.json`

### Erreur : "API calls failing"
Vérifiez que l'URL backend est correcte :
```javascript
// Dans le code frontend
console.log(process.env.REACT_APP_API_URL)
// Devrait afficher : https://getyourshare-backend-production.up.railway.app/api
```

---

## 📝 Notes Importantes

1. **Token Vercel** : Le token fourni n'est pas valide. Utilisez l'interface web ou générez un nouveau token.

2. **Backend Railway** : Assurez-vous que votre backend Railway est bien déployé et accessible.

3. **CORS** : Le backend doit autoriser l'origine Vercel. Ajoutez dans Railway :
   ```bash
   CORS_ORIGINS=https://getyourshare-versio2.vercel.app,https://*.vercel.app
   ```

4. **Build Time** : Le premier build peut prendre 3-5 minutes.

---

## ✅ Checklist de Déploiement

- [ ] Backend Railway déployé et accessible
- [ ] Healthcheck `/health` fonctionne
- [ ] Variables d'environnement configurées sur Vercel
- [ ] Repo GitHub connecté à Vercel
- [ ] Premier déploiement réussi
- [ ] Frontend accessible sur URL Vercel
- [ ] API calls fonctionnent
- [ ] Pas d'erreurs console
- [ ] Tests manuels OK

---

## 🎉 Félicitations !

Une fois déployé, votre application sera accessible à :

**Frontend** : `https://getyourshare-versio2.vercel.app`
**Backend** : `https://getyourshare-backend-production.up.railway.app`

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs Vercel : `vercel logs`
2. Vérifiez les logs Railway dans le dashboard
3. Testez le backend manuellement avec `curl`
4. Vérifiez la console navigateur pour les erreurs frontend
