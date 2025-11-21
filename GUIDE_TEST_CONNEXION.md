# 🎯 GUIDE DE TEST - CONNEXION AU TABLEAU DE BORD

## ✅ CORRECTIONS APPLIQUÉES

Tous les fichiers frontend ont été corrigés pour utiliser le **bon port 5000** au lieu du port 8000:

### Fichiers corrigés:
- ✅ `frontend/src/utils/api.js` - API principale (REACT_APP_API_URL)
- ✅ `frontend/src/services/api.js` - API services (REACT_APP_API_URL + withCredentials)
- ✅ `frontend/src/pages/Login.js` - Page de connexion (ligne 101)
- ✅ `frontend/src/pages/Register.js` - Page d'inscription
- ✅ `frontend/src/pages/Pricing.js` - Page tarifs
- ✅ `frontend/src/pages/AIMarketing.js` - Page AI Marketing
- ✅ `frontend/src/components/GamificationWidget.jsx` - Widget gamification
- ✅ `frontend/src/context/WebSocketContext.js` - WebSocket

### Configuration:
- ✅ `withCredentials: true` activé dans les deux fichiers api.js
- ✅ Cookies httpOnly supportés
- ✅ CORS configuré pour localhost:3000

---

## 🚀 TESTER LA CONNEXION

### 1. Vérifier que les serveurs sont actifs

**Backend:**
```powershell
netstat -ano | findstr :5000
# Doit afficher: TCP 0.0.0.0:5000 ... LISTENING
```

**Frontend:**
```powershell
Invoke-WebRequest -Uri "http://localhost:3000" | Select-Object StatusCode
# Doit afficher: StatusCode 200
```

### 2. Ouvrir l'application dans le navigateur

1. Allez sur **http://localhost:3000**
2. Vous devriez voir la page d'accueil
3. Cliquez sur **"Connexion"** ou allez sur **http://localhost:3000/login**

### 3. Se connecter

**Identifiants Admin:**
- Email: `admin@getyourshare.com`
- Mot de passe: `Admin123!`

**Autres comptes de test:**
- Merchant: `merchant1@fashionstore.com` / `Test123!`
- Influencer: `influencer1@fashion.com` / `Test123!`

### 4. Vérifier dans la Console du navigateur (F12)

**Ce que vous DEVEZ voir:**
- ✅ Aucune erreur de connexion
- ✅ Aucune erreur `ERR_CONNECTION_REFUSED`
- ✅ Requêtes vers `http://localhost:5000` (PAS 8000!)
- ✅ Réponses 200 OK

**Ce que vous NE DEVEZ PAS voir:**
- ❌ Erreurs vers `http://localhost:8000`
- ❌ "Connexion échouée"
- ❌ Erreurs CORS
- ❌ 401 Unauthorized (sauf si non connecté)

### 5. Vérifier l'onglet Network (Réseau)

Dans F12 → Network:

1. Rafraîchissez la page (F5)
2. Connectez-vous
3. Vous devriez voir:
   - `POST http://localhost:5000/api/auth/login` → **200 OK**
   - `GET http://localhost:5000/api/auth/me` → **200 OK**
   - `GET http://localhost:5000/api/dashboard/stats` → **200 OK**

### 6. Vérifier les Cookies

Dans F12 → Application → Cookies → http://localhost:3000:

Vous devriez voir:
- ✅ `access_token` (httpOnly)
- ✅ `refresh_token` (httpOnly)

---

## 🧪 TESTS AUTOMATIQUES

### Test complet du backend:
```powershell
cd backend
python test_dashboard_complet.py
```

**Résultat attendu:**
```
✓ Login réussi!
✓ Session valide!
✓ Dashboard accessible!
✓ Produits récupérés
```

### Test rapide:
```powershell
cd backend
python simple_test.py
```

---

## ❌ RÉSOLUTION DES PROBLÈMES

### Si vous voyez encore "Connexion échouée":

1. **Vérifier l'URL dans la console:**
   - Ouvrez F12 → Console
   - Cherchez les requêtes HTTP
   - Si vous voyez `localhost:8000` → Le cache navigateur n'est pas vidé

2. **Vider le cache du navigateur:**
   - Chrome/Edge: Ctrl + Shift + Delete → Vider le cache
   - Ou: Mode navigation privée (Ctrl + Shift + N)

3. **Redémarrer le frontend:**
   ```powershell
   cd frontend
   Get-Process -Name node | Stop-Process -Force
   $env:REACT_APP_API_URL='http://localhost:5000'
   npm start
   ```

4. **Vérifier les variables d'environnement:**
   ```powershell
   cd frontend
   Get-Content .env
   # Doit contenir: REACT_APP_API_URL=http://localhost:5000
   ```

### Si le backend ne répond pas:

```powershell
cd backend
python start_server_bg.py
Start-Sleep -Seconds 5
python simple_test.py
```

---

## 📊 STATISTIQUES DU TABLEAU DE BORD

Après connexion réussie, vous devriez voir:

- **Utilisateurs:** 17
- **Marchands:** 5
- **Influenceurs:** 5
- **Produits:** 25
- **Services:** 5
- **Revenu total:** 13,545.76 €

---

## ✨ TOUT FONCTIONNE SI:

1. ✅ Connexion réussie sans erreur
2. ✅ Redirection vers `/dashboard` après login
3. ✅ Statistiques affichées
4. ✅ Aucune erreur dans la console
5. ✅ Toutes les requêtes vers `localhost:5000`
6. ✅ Cookies `access_token` et `refresh_token` présents

---

## 🔧 COMMANDES UTILES

### Vérifier les processus:
```powershell
# Backend
Get-Process python | Where-Object {$_.MainWindowTitle -like "*server*"}

# Frontend
Get-Process node
```

### Vérifier les ports:
```powershell
netstat -ano | findstr ":5000"
netstat -ano | findstr ":3000"
```

### Logs en temps réel:
```powershell
cd backend
python watch_logs.py
# Puis connectez-vous sur le frontend
```

---

## 📝 NOTES IMPORTANTES

1. **Port Backend:** 5000 (PAS 8000!)
2. **Port Frontend:** 3000
3. **Cookies:** httpOnly (invisibles au JavaScript)
4. **CORS:** Configuré pour localhost:3000
5. **JWT:** Expiration 4 heures

---

**Date de correction:** ${new Date().toLocaleString('fr-FR')}
**Statut:** ✅ TOUTES LES CORRECTIONS APPLIQUÉES
