# 🚀 Configuration des Variables d'Environnement Vercel

## Guide Rapide d'Installation

### Méthode 1: Via Vercel Dashboard (Recommandé)

1. **Accédez à votre projet Vercel**
   ```
   https://vercel.com/dashboard
   ```

2. **Allez dans Settings → Environment Variables**

3. **Copiez les variables depuis `.env.vercel`**

   Pour chaque variable, cliquez sur "Add New" et copiez:

   | Variable | Valeur | Environnements |
   |----------|--------|----------------|
   | `REACT_APP_API_URL` | `https://getyourshare-backend-production.up.railway.app/api` | Production, Preview |
   | `REACT_APP_BACKEND_URL` | `https://getyourshare-backend-production.up.railway.app` | Production, Preview |
   | `REACT_APP_SUPABASE_URL` | `https://iamezkmapbhlhhvvsits.supabase.co` | Production, Preview, Development |
   | `REACT_APP_SUPABASE_ANON_KEY` | `eyJhbGciOi...` (voir .env.vercel) | Production, Preview, Development |
   | `REACT_APP_NAME` | `ShareYourSales` | Production, Preview, Development |
   | `REACT_APP_VERSION` | `1.0.0` | Production, Preview, Development |
   | `REACT_APP_ENV` | `production` | Production |
   | `REACT_APP_FEATURE_MLM` | `false` | Production, Preview, Development |
   | `REACT_APP_FEATURE_ANALYTICS` | `true` | Production, Preview, Development |
   | `REACT_APP_FEATURE_AI_MARKETING` | `false` | Production, Preview, Development |
   | `REACT_APP_DEBUG` | `false` | Production, Preview |
   | `DISABLE_ESLINT_PLUGIN` | `true` | Production, Preview, Development |

4. **Redéployez votre application**
   - Cliquez sur "Deployments"
   - Sélectionnez le dernier déploiement
   - Cliquez sur les 3 points (...) → "Redeploy"

---

### Méthode 2: Via Vercel CLI (Plus Rapide)

#### Installation de Vercel CLI
```bash
npm install -g vercel
vercel login
```

#### Configuration Automatique
```bash
# Production
vercel env add REACT_APP_API_URL production
# Copiez-collez: https://getyourshare-backend-production.up.railway.app/api

vercel env add REACT_APP_BACKEND_URL production
# Copiez-collez: https://getyourshare-backend-production.up.railway.app

vercel env add REACT_APP_SUPABASE_URL production
# Copiez-collez: https://iamezkmapbhlhhvvsits.supabase.co

vercel env add REACT_APP_SUPABASE_ANON_KEY production
# Copiez-collez la clé depuis .env.vercel

vercel env add REACT_APP_NAME production
# ShareYourSales

vercel env add REACT_APP_VERSION production
# 1.0.0

vercel env add REACT_APP_ENV production
# production

vercel env add REACT_APP_FEATURE_MLM production
# false

vercel env add REACT_APP_FEATURE_ANALYTICS production
# true

vercel env add REACT_APP_FEATURE_AI_MARKETING production
# false

vercel env add REACT_APP_DEBUG production
# false

vercel env add DISABLE_ESLINT_PLUGIN production
# true
```

#### Redéploiement
```bash
vercel --prod
```

---

### Méthode 3: Import en Masse (Vercel CLI v28+)

Créez un fichier temporaire `.env.production.local`:
```bash
cp .env.vercel .env.production.local
```

Puis importez avec:
```bash
vercel env pull .env.production.local
```

---

## 🔍 Vérification

### 1. Vérifier les variables sur Vercel
```bash
vercel env ls
```

### 2. Vérifier dans le build
Après déploiement, ouvrez la console du navigateur et tapez:
```javascript
console.log(process.env)
```

Vous devriez voir toutes les variables `REACT_APP_*`

---

## ⚠️ Sécurité

### Variables Publiques (Safe)
Ces variables sont **publiques** et exposées dans le bundle JavaScript:
- ✅ `REACT_APP_API_URL`
- ✅ `REACT_APP_SUPABASE_URL`
- ✅ `REACT_APP_SUPABASE_ANON_KEY` (clé anonyme Supabase)
- ✅ Toutes les variables `REACT_APP_*`

### Variables Privées (Backend Only)
**NE JAMAIS** mettre dans le frontend:
- ❌ `SUPABASE_SERVICE_ROLE_KEY`
- ❌ `JWT_SECRET`
- ❌ Clés API privées (Stripe Secret, etc.)

---

## 🔄 Mise à Jour des Variables

### Après modification sur Vercel:
1. Les variables sont appliquées au **prochain déploiement**
2. Pour appliquer immédiatement: **Redéployez manuellement**

### Commandes utiles:
```bash
# Lister toutes les variables
vercel env ls

# Supprimer une variable
vercel env rm VARIABLE_NAME production

# Mettre à jour (supprimer puis ajouter)
vercel env rm REACT_APP_API_URL production
vercel env add REACT_APP_API_URL production
```

---

## 📊 Environnements Vercel

| Environnement | Quand l'utiliser |
|---------------|------------------|
| **Production** | Site en ligne (branche main) |
| **Preview** | Pull Requests / branches de dev |
| **Development** | Développement local avec `vercel dev` |

**Conseil**: Configurez toutes les variables pour **Production et Preview** minimum.

---

## 🆘 Troubleshooting

### Problème: Variables non disponibles
**Solution**: Vérifiez que vous avez sélectionné les bons environnements

### Problème: Build échoue avec erreur ESLint
**Solution**: Assurez-vous que `DISABLE_ESLINT_PLUGIN=true` est défini

### Problème: 404 sur /about
**Solution**: Les fichiers `_redirects` et `404.html` gèrent ça. Si le problème persiste, videz le cache Vercel en redéployant sans cache.

### Problème: CORS errors
**Solution**: Vérifiez que `REACT_APP_BACKEND_URL` pointe vers le bon backend

---

## 📚 Documentation

- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)
- [Create React App Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [Supabase Client Setup](https://supabase.com/docs/reference/javascript/initializing)

---

## ✅ Checklist de Déploiement

- [ ] Toutes les variables ajoutées sur Vercel Dashboard
- [ ] Variables configurées pour Production et Preview
- [ ] Application redéployée
- [ ] Tests du site en production: https://votre-site.vercel.app
- [ ] Vérification console browser pour erreurs
- [ ] Test navigation /about, /pricing, /contact
- [ ] Test connexion/inscription
- [ ] Vérification backend connectivity

---

🎉 **Une fois configuré, Vercel rebuildera automatiquement à chaque push Git!**
