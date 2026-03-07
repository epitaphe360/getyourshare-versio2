# 🚀 Guide de Démarrage Rapide - ShareYourSales

## ✅ Installation Complète

Toutes les dépendances ont été installées avec succès :

### 📦 Backend (Python)
- **135 packages** installés
- Python 3.14.0
- FastAPI + Supabase + Stripe + Redis + Celery

### 📦 Frontend (React)
- **1410 packages** installés  
- React 18.2.0 + Material-UI + React Query

### 📦 Mobile (React Native)
- **1032 packages** installés
- React Native 0.72.6 + Navigation + Firebase

---

## 🎯 Démarrage Rapide

### Option 1 : Tout démarrer en une fois
```bash
# Double-cliquez sur :
START_ALL.bat
```

Cela démarre automatiquement :
- ✅ Backend sur http://localhost:8000
- ✅ Frontend sur http://localhost:3000

### Option 2 : Démarrage séparé

#### Backend uniquement
```bash
start_backend.bat
```
Ou manuellement :
```bash
cd backend
..\.venv\Scripts\activate
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend uniquement
```bash
start_frontend.bat
```
Ou manuellement :
```bash
cd frontend
npm start
```

#### Mobile (React Native)
```bash
cd mobile
npm start
# Puis dans un autre terminal :
npm run android   # Pour Android
npm run ios       # Pour iOS
```

---

## 🔗 URLs Importantes

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface utilisateur |
| **Backend API** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Documentation interactive (Swagger) |
| **API Redoc** | http://localhost:8000/redoc | Documentation alternative |
| **Supabase** | https://iamezkmapbhlhhvvsits.supabase.co | Base de données |

---

## 📝 Configuration

### Variables d'environnement (backend/.env)

Les variables essentielles sont déjà configurées :

```bash
# Supabase
SUPABASE_URL=https://iamezkmapbhlhhvvsits.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT
JWT_SECRET=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==
SECRET_KEY=bFeUjfAZnOEKWdeOfxSRTEM/67DJMrttpW55WpBOIiK65vMNQMtBRatDy4PSoC3w9bJj7WmbArp5g/KVDaIrnw==

# Server
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

⚠️ **Pour la production**, modifiez ces clés !

---

## 🧪 Tests Rapides

### Test Backend
```bash
# Activer l'environnement Python
.venv\Scripts\activate

# Test des imports
python -c "import fastapi, supabase, stripe, redis; print('✅ Tous les modules OK')"

# Démarrer le serveur
cd backend
python -m uvicorn server:app --reload
```

### Test Frontend
```bash
cd frontend
npm start
```

### Vérifier l'API
```bash
# Une fois le backend démarré :
curl http://localhost:8000/health
# ou visitez : http://localhost:8000/docs
```

---

## 📊 Structure du Projet

```
getyourshareversion2-/
├── backend/                 # API FastAPI + Supabase
│   ├── server.py           # Point d'entrée principal
│   ├── requirements.txt    # Dépendances Python
│   ├── .env               # Variables d'environnement
│   └── ...
├── frontend/               # Application React
│   ├── src/
│   ├── public/
│   └── package.json
├── mobile/                 # Application React Native
│   ├── android/
│   ├── ios/
│   └── package.json
├── .venv/                  # Environnement virtuel Python
├── START_ALL.bat          # Démarrer tout
├── start_backend.bat      # Démarrer backend seul
└── start_frontend.bat     # Démarrer frontend seul
```

---

## ⚙️ Commandes Utiles

### Backend
```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer des migrations
python manage.py migrate

# Créer un super utilisateur
python create_user.py

# Tests
pytest tests/
```

### Frontend
```bash
# Build pour production
npm run build

# Tests
npm test

# Linter
npm run lint
```

### Mobile
```bash
# Build Android
npm run build:android

# Build iOS
npm run build:ios

# Tests
npm test
```

---

## 🐛 Résolution de Problèmes

### Backend ne démarre pas
1. Vérifier que l'environnement virtuel est activé : `.venv\Scripts\activate`
2. Vérifier les variables dans `backend/.env`
3. Vérifier le port 8000 : `netstat -ano | findstr :8000`

### Frontend ne démarre pas
1. Vérifier node_modules : `npm install`
2. Vérifier le port 3000 : `netstat -ano | findstr :3000`
3. Effacer le cache : `npm cache clean --force`

### Erreurs de dépendances Python
```bash
cd backend
..\.venv\Scripts\activate
pip install -r requirements.txt
```

### Erreurs de dépendances Node.js
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Documentation

- **API Documentation** : http://localhost:8000/docs
- **Supabase Dashboard** : https://app.supabase.com
- **FastAPI** : https://fastapi.tiangolo.com
- **React** : https://react.dev
- **React Native** : https://reactnative.dev

---

## 🎉 Félicitations !

Votre environnement ShareYourSales est maintenant prêt !

**Prochaines étapes :**
1. ✅ Lancer `START_ALL.bat`
2. ✅ Ouvrir http://localhost:3000
3. ✅ Explorer l'API : http://localhost:8000/docs
4. ✅ Commencer à développer !

---

## 📞 Support

En cas de problème :
1. Vérifier la console pour les erreurs
2. Consulter les logs : `backend/logs/`
3. Redémarrer les serveurs
4. Vérifier les issues GitHub

**Bon développement ! 🚀**
