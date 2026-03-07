# 🔧 Configuration Supabase sur Railway - URGENT

## ❌ Problème Actuel

**Erreur de connexion lors du login** - Le backend Railway ne peut pas se connecter à Supabase car les variables d'environnement sont manquantes.

## 🎯 Solution: Ajouter les Variables d'Environnement Railway

### **Étape 1: Ouvrir Railway Dashboard**

1. Allez sur https://railway.app
2. Sélectionnez votre projet **getyourshare-versio2**
3. Cliquez sur le service **Backend** (où votre API Python tourne)

### **Étape 2: Ajouter les Variables Supabase**

1. Cliquez sur l'onglet **"Variables"** (dans la navigation de gauche)
2. Cliquez sur **"+ New Variable"** (ou "Raw Editor" pour tout copier-coller en une fois)

### **Étape 3: Copier-Coller ces Variables**

```bash
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g
```

**Important**:
- ✅ Pas de guillemets autour des valeurs
- ✅ Pas d'espace avant/après le `=`
- ✅ Copier EXACTEMENT comme montré ci-dessus

### **Étape 4: Sauvegarder et Redéployer**

1. Cliquez sur **"Add"** ou **"Save"**
2. **Railway va automatiquement redéployer** (attendez 2-3 minutes)
3. Surveillez les **logs de déploiement**

---

## ✅ Vérification: Logs à Vérifier

Après le redéploiement, dans Railway **Logs**, vous DEVEZ voir au démarrage:

```
✅ Supabase client créé: True
🔐 CORS allowed origins: [...]
🔐 CORS Vercel regex pattern: https://.*\.vercel\.app
✅ CORS middleware configured with Vercel regex support
```

### Si vous voyez:
```
⚠️ Supabase non disponible: [error]
✅ Supabase client créé: False
```

→ **Les variables sont mal configurées**, revérifiez l'Étape 3.

---

## 🧪 Test Final

Après le redéploiement:

1. **Allez sur votre frontend Vercel**
2. **Essayez de vous connecter** avec n'importe quel compte MOCK_USERS:
   - Email: `admin@shareyoursales.ma`
   - Password: `Admin123`

3. **Dans Railway Logs**, vous devriez voir:
   ```
   🔍 Login attempt for admin@shareyoursales.ma - User found in Supabase: False
   ⚠️ Falling back to MOCK_USERS for admin@shareyoursales.ma
   ✅ Login successful for admin@shareyoursales.ma (role: admin)
   ```

4. **Si vous avez des comptes dans Supabase** (comme `julie.beauty@tiktok.com`):
   ```
   🔍 Login attempt for julie.beauty@tiktok.com - User found in Supabase: True
   ✅ Login successful for julie.beauty@tiktok.com (role: influencer)
   ```

---

## 📝 Variables Railway Complètes (Pour Référence)

Voici TOUTES les variables que Railway devrait avoir:

```bash
# === SUPABASE ===
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g

# === JWT/AUTH ===
SECRET_KEY=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
JWT_SECRET=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==

# === ENVIRONMENT ===
ENVIRONMENT=production
NODE_ENV=production
DEBUG=False

# === CORS (Optionnel, ajoutez vos URLs Vercel) ===
CORS_ORIGINS=https://votre-app.vercel.app,http://localhost:3000
FRONTEND_URL=https://votre-app.vercel.app
```

---

## ❓ FAQ

### Q: Où trouver SUPABASE_SERVICE_ROLE_KEY?
**R**: C'est déjà dans le fichier `.env.railway` à la racine du projet. Copier exactement.

### Q: Railway redéploie automatiquement quand je change une variable?
**R**: **Oui!** Dès que vous sauvegardez une variable, Railway redémarre le service.

### Q: Comment savoir si ça a marché?
**R**: Regardez les logs Railway - cherchez "✅ Supabase client créé: True"

### Q: Le login fonctionne toujours pas?
**R**: Vérifiez:
1. Les variables sont bien EXACTEMENT comme montré (pas d'espace, pas de guillemets)
2. Railway a bien redéployé (regardez l'heure du dernier déploiement)
3. Les logs montrent "✅ Supabase client créé: True"

---

## 🚨 Actions Immédiates

1. ✅ **MAINTENANT**: Allez sur Railway → Variables
2. ✅ Ajoutez `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY`
3. ✅ Attendez le redéploiement automatique (2-3 min)
4. ✅ Vérifiez les logs
5. ✅ Testez le login

**Temps estimé: 5 minutes** ⏱️
