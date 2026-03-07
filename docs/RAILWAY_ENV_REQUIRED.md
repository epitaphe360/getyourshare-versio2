# 🚂 Variables d'Environnement Railway - Configuration Requise

## ⚠️ IMPORTANT : Variables Obligatoires

Pour que l'application démarre correctement sur Railway, vous **DEVEZ** configurer ces variables d'environnement dans votre projet Railway.

---

## 🔐 Variables Essentielles (OBLIGATOIRES)

### 1. Supabase (Base de données)

```bash
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_SERVICE_ROLE_KEY=votre_service_role_key_ici
SUPABASE_KEY=votre_anon_key_ici
```

**Où trouver ces clés ?**
1. Allez sur https://supabase.com/dashboard
2. Sélectionnez votre projet `iamezkmapbhlhhvvsits`
3. Settings → API
4. Copiez :
   - `URL` → SUPABASE_URL
   - `service_role key` → SUPABASE_SERVICE_ROLE_KEY
   - `anon public key` → SUPABASE_KEY

⚠️ **ATTENTION** : Ne partagez JAMAIS le `service_role_key` publiquement !

---

### 2. JWT Secret (Authentification)

```bash
JWT_SECRET=votre_secret_jwt_tres_long_minimum_64_caracteres_pour_securite_maximale
```

**Comment générer un JWT_SECRET sécurisé ?**

Option 1 - Python :
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Option 2 - OpenSSL :
```bash
openssl rand -base64 64
```

Option 3 - Node.js :
```bash
node -e "console.log(require('crypto').randomBytes(64).toString('base64'))"
```

**Exemple de JWT_SECRET valide :**
```
wK8PmVXh9TA_qRnY2c4dBfE6gL1jH3iN5oM7pQ8rS9tU0vW1xY2zA3bC4dE5fG6hI7jK8lM9nO0pQ1rS2tU3vW4xY5zA
```

---

### 3. CORS (Pour Vercel)

```bash
CORS_ORIGINS=https://getyourshare-versio2.vercel.app,https://*.vercel.app,http://localhost:3000
```

Cette variable permet à votre frontend Vercel de communiquer avec le backend Railway.

---

## 🔧 Variables Optionnelles (Recommandées)

### Port (automatique sur Railway)
```bash
PORT=8000
```
⚠️ Railway définit cette variable automatiquement, ne pas modifier.

### JWT Expiration
```bash
JWT_EXPIRATION=86400
```
Durée de validité du token en secondes (86400 = 24 heures)

### Environment
```bash
ENVIRONMENT=production
DEBUG=false
```

---

## 📋 Comment Configurer les Variables sur Railway

### Via l'Interface Web (RECOMMANDÉ)

1. Allez sur votre projet Railway : https://railway.app/project/[votre-projet-id]
2. Cliquez sur votre service backend
3. Allez dans l'onglet **"Variables"**
4. Cliquez sur **"+ New Variable"**
5. Ajoutez chaque variable une par une :
   - **Variable** : `SUPABASE_URL`
   - **Value** : `https://iamezkmapbhlhhvvsits.supabase.co`
6. Cliquez sur **"Add"**
7. Répétez pour toutes les variables

### Via Railway CLI

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Se connecter
railway login

# Lier le projet
railway link

# Ajouter les variables
railway variables set SUPABASE_URL="https://iamezkmapbhlhhvvsits.supabase.co"
railway variables set SUPABASE_SERVICE_ROLE_KEY="votre_service_role_key"
railway variables set SUPABASE_KEY="votre_anon_key"
railway variables set JWT_SECRET="votre_jwt_secret"
railway variables set CORS_ORIGINS="https://getyourshare-versio2.vercel.app,https://*.vercel.app"

# Redéployer
railway up
```

---

## ✅ Vérification Post-Configuration

### 1. Vérifier que toutes les variables sont définies

Dans Railway Dashboard → Variables, vous devriez voir :
- ✅ SUPABASE_URL
- ✅ SUPABASE_SERVICE_ROLE_KEY
- ✅ SUPABASE_KEY
- ✅ JWT_SECRET
- ✅ CORS_ORIGINS
- ✅ PORT (automatique)

### 2. Redéployer

Après avoir ajouté les variables :
1. Railway détectera les changements
2. Il va automatiquement redéployer
3. Attendez 2-3 minutes

### 3. Tester le Healthcheck

```bash
curl https://getyourshare-backend-production.up.railway.app/health
```

Devrait retourner :
```json
{"status": "healthy", "service": "ShareYourSales Backend"}
```

### 4. Vérifier les Logs

Dans Railway Dashboard → Logs, vous devriez voir :
```
✅ Supabase client créé: True
✅ JWT_SECRET chargé avec succès (86 caractères)
✅ Server started successfully
```

---

## 🐛 Troubleshooting

### Healthcheck Failed - Service Unavailable

**Problème** : L'application ne démarre pas

**Solutions** :
1. ✅ Vérifiez que `SUPABASE_URL`, `SUPABASE_KEY` et `JWT_SECRET` sont définis
2. ✅ Vérifiez que `JWT_SECRET` fait au moins 32 caractères
3. ✅ Consultez les logs Railway pour voir l'erreur exacte
4. ✅ Assurez-vous que le Dockerfile build sans erreurs

### CORS Errors dans le Frontend

**Problème** : Le frontend ne peut pas communiquer avec le backend

**Solution** :
```bash
# Ajouter dans Railway
CORS_ORIGINS=https://votre-domaine-vercel.vercel.app,https://*.vercel.app
```

### JWT Secret Error

**Problème** : "JWT_SECRET non défini" ou "JWT_SECRET trop court"

**Solution** :
Générez un secret de minimum 64 caractères :
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## 📝 Template Complet

Copiez-collez ce template et remplacez les valeurs :

```bash
# ========================================
# RAILWAY ENVIRONMENT VARIABLES
# ========================================

# Supabase (OBLIGATOIRE)
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhb...votre_service_role_key
SUPABASE_KEY=eyJhb...votre_anon_key

# JWT (OBLIGATOIRE - Générez avec: python -c "import secrets; print(secrets.token_urlsafe(64))")
JWT_SECRET=wK8PmVXh9TA_qRnY2c4dBfE6gL1jH3iN5oM7pQ8rS9tU0vW1xY2zA3bC4dE5fG6hI7jK8lM9nO0pQ1rS2tU3vW4xY5zA

# CORS (OBLIGATOIRE pour le frontend)
CORS_ORIGINS=https://getyourshare-versio2.vercel.app,https://*.vercel.app,http://localhost:3000

# Optionnel
JWT_EXPIRATION=86400
ENVIRONMENT=production
DEBUG=false
```

---

## 🎯 Ordre d'Importance

1. **CRITIQUE** (Application ne démarre pas sans) :
   - SUPABASE_URL
   - SUPABASE_SERVICE_ROLE_KEY
   - SUPABASE_KEY
   - JWT_SECRET

2. **IMPORTANT** (Fonctionnalités limitées sans) :
   - CORS_ORIGINS

3. **OPTIONNEL** (Améliorations) :
   - JWT_EXPIRATION
   - ENVIRONMENT
   - DEBUG

---

## 📞 Support

Si après configuration l'application ne démarre toujours pas :

1. Vérifiez les logs Railway
2. Testez le healthcheck : `curl https://votre-url.up.railway.app/health`
3. Vérifiez que toutes les variables sont bien définies (pas de typos)
4. Redéployez manuellement depuis Railway Dashboard

---

## ✅ Checklist Finale

Avant de considérer la configuration terminée :

- [ ] SUPABASE_URL défini et valide
- [ ] SUPABASE_SERVICE_ROLE_KEY défini
- [ ] SUPABASE_KEY défini
- [ ] JWT_SECRET généré (minimum 64 caractères)
- [ ] CORS_ORIGINS inclut l'URL Vercel
- [ ] Application redéployée
- [ ] Healthcheck retourne 200 OK
- [ ] Logs Railway ne montrent pas d'erreurs
- [ ] Frontend Vercel peut appeler le backend

**Une fois tout coché, votre application est prête ! 🚀**
