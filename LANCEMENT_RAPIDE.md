# 🚀 LANCEMENT RAPIDE DES SERVEURS

## 3 Méthodes Ultra-Rapides

### ⚡ Méthode 1 : Double-clic (RECOMMANDÉ)
**Fichier** : `DEMARRER.bat`
- Double-cliquez dessus
- C'est tout !

### ⚡ Méthode 2 : PowerShell Simple
```powershell
.\launch.ps1
```

### ⚡ Méthode 3 : PowerShell Détaillé
```powershell
.\start-servers.ps1
```

---

## 🌐 URLs après démarrage

- Frontend : http://localhost:3000
- Backend : http://localhost:5000
- API Docs : http://localhost:5000/docs

---

## 👤 Comptes de Test

Utilisez ces identifiants pour vous connecter :

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| 👑 Admin | `admin@test.com` | `admin123` |
| 🏪 Marchant | `merchant@test.com` | `merchant123` |
| ⭐ Influenceur | `influencer@test.com` | `influencer123` |
| 💼 Commercial | `commercial@test.com` | `commercial123` |

---

## 🛑 Arrêter les serveurs

Fermez les fenêtres PowerShell ouvertes

Ou :
```powershell
Get-Process python,node | Stop-Process -Force
```

---

## 🔧 Dépannage

### Libérer les ports
```powershell
Get-NetTCPConnection -LocalPort 5000,3000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Vérifier l'état
```powershell
Get-NetTCPConnection -LocalPort 5000,3000 -State Listen
```

---

✨ **Les serveurs démarrent en ~5 secondes !**
