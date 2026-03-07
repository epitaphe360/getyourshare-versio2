# ✅ SERVEUR CORRIGÉ - Démarrage Immédiat

## 🎯 Le problème est résolu définitivement

**Symptôme:** Serveur démarrait puis s'arrêtait immédiatement  
**Cause:** Scheduler LEADS s'initialisait au moment de l'import  
**Solution:** Scheduler refactorisé - initialization différée

---

## 🚀 DÉMARRER LE SERVEUR (choisir une méthode)

### ⭐ Méthode 1: Double-clic (RECOMMANDÉ)
```
Double-cliquez sur START_SERVER.bat
```

### Méthode 2: PowerShell
```powershell
cd backend
python server.py
```

### Méthode 3: Uvicorn
```powershell
cd backend
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

---

## ✅ Vérifier que ça fonctionne

Serveur sur: **http://localhost:8000**

```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health

# API Docs (dans navigateur)
http://localhost:8000/docs
```

---

## 📊 Ce qui démarre automatiquement

- ✅ FastAPI + Uvicorn
- ✅ Scheduler LEADS (alertes dépôts)
- ✅ JWT + 2FA auth
- ✅ Supabase PostgreSQL
- ✅ Tous les endpoints API

**Jobs planifiés:**
- 🔄 Alertes dépôts: Toutes les heures
- 🧹 Nettoyage leads: 23h00 quotidien
- 📊 Rapports: 09h00 quotidien

---

## 🔧 Modifications techniques

**Fichiers changés:**

1. `backend/scheduler/leads_scheduler.py`
   - Services initialisés uniquement dans `start_scheduler()`
   - Import-safe (pas d'effets de bord)
   - Idempotent (ne redémarre pas si déjà actif)

2. `backend/server.py`
   - Appel protégé dans `@app.on_event("startup")`
   - Arrêt propre dans `@app.on_event("shutdown")`

---

## ⚠️ Warnings visibles (non bloquants)

Vous verrez des DeprecationWarnings au démarrage - **ignorez-les**, ils n'affectent pas le fonctionnement:
- `@app.on_event` → migration future vers `lifespan`
- `regex` → `pattern` dans Query params

---

## 🎉 C'est tout !

Le serveur est stable. Pour l'arrêter: **CTRL+C** dans le terminal.

Documentation complète: `DEMARRAGE_RAPIDE.md`
