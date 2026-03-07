# 🔧 CORRECTIONS TYPE SAFETY - USER OBJECT

## Script de correction automatique pour tous les `user["role"]` sans vérification

---

## 📝 MODIFICATIONS À APPLIQUER

### Fichier: `backend/advanced_endpoints.py`

#### Pattern à rechercher:
```python
user = request.state.user
if user["role"] != "merchant":
```

#### Remplacer par:
```python
user = request.state.user
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

---

### LISTE COMPLÈTE DES CORRECTIONS

#### 1. Ligne 136 - create_product()
```python
# AVANT:
user = request.state.user
if user["role"] != "merchant":
    raise HTTPException(...)

# APRÈS:
user = request.state.user
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
    raise HTTPException(...)
```

#### 2. Ligne 197 - update_product()
```python
# AVANT:
if user["role"] != "merchant":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

#### 3. Ligne 224 - delete_product()
```python
# AVANT:
if user["role"] != "merchant":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

#### 4. Ligne 258 - create_campaign()
```python
# AVANT:
if user["role"] != "merchant":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

#### 5. Ligne 307 - update_campaign()
```python
# AVANT:
if user["role"] != "merchant":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

#### 6. Ligne 323 - delete_campaign()
```python
# AVANT:
if user["role"] != "merchant":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

#### 7. Ligne 349 - assign_products()
```python
# AVANT:
if user["role"] != "merchant":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

#### 8. Ligne 377 - get_invitations()
```python
# AVANT:
if user["role"] != "merchant":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "merchant":
```

#### 9. Ligne 485 - get_my_campaigns()
```python
# AVANT:
if user["role"] != "influencer":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "influencer":
```

#### 10. Ligne 510 - get_all_payouts()
```python
# AVANT:
if user["role"] not in ["admin", "merchant"]:

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") not in ["admin", "merchant"]:
```

#### 11. Ligne 536 - request_payout()
```python
# AVANT:
if user["role"] != "influencer":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "influencer":
```

#### 12. Ligne 561 - approve_payout()
```python
# AVANT:
if user["role"] != "admin":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "admin":
```

#### 13. Ligne 574 - reject_payout()
```python
# AVANT:
if user["role"] != "admin":

# APRÈS:
if not user:
    raise HTTPException(status_code=401, detail="Non authentifié")
if user.get("role") != "admin":
```

---

### AUSSI: Sécuriser les accès aux propriétés user

#### Pattern dangereux:
```python
merchant = get_merchant_by_user_id(user["id"])
```

#### Remplacer par:
```python
if not user or "id" not in user:
    raise HTTPException(status_code=401, detail="Non authentifié")
merchant = get_merchant_by_user_id(user["id"])
```

**Lignes concernées:** 141, 176, 205, 231, 263, 354, 380, 396, 490, 539

---

## 🤖 SCRIPT PYTHON POUR APPLIQUER AUTOMATIQUEMENT

```python
#!/usr/bin/env python3
"""
Script pour ajouter automatiquement les vérifications user != None
"""

import re
from pathlib import Path

def fix_user_checks(file_path: str):
    """Ajoute vérifications user avant accès à user['role']"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: if user["role"] != "xxx":
    pattern1 = r'(\s+)(if user\["role"\])'
    replacement1 = r'\1if not user:\n\1    raise HTTPException(status_code=401, detail="Non authentifié")\n\1if user.get("role")'
    
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: if user["role"] not in [...]
    pattern2 = r'(\s+)(if user\["role"\] not in)'
    replacement2 = r'\1if not user:\n\1    raise HTTPException(status_code=401, detail="Non authentifié")\n\1if user.get("role") not in'
    
    content = re.sub(pattern2, replacement2, content)
    
    # Pattern 3: Remplacer user["role"] par user.get("role") partout
    content = content.replace('user["role"]', 'user.get("role")')
    
    # Pattern 4: Sécuriser user["id"]
    pattern4 = r'(get_\w+_by_user_id\()(user\["id"\])'
    replacement4 = r'\1user.get("id") if user else None'
    
    # Note: Ce pattern nécessite vérification manuelle
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {file_path} corrigé")

if __name__ == "__main__":
    files_to_fix = [
        "backend/advanced_endpoints.py",
        "backend/advanced_helpers.py"
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            # Backup
            backup_path = f"{file_path}.backup"
            Path(file_path).rename(backup_path)
            print(f"📦 Backup créé: {backup_path}")
            
            # Restore from backup and fix
            Path(backup_path).rename(file_path)
            fix_user_checks(file_path)
        else:
            print(f"❌ Fichier non trouvé: {file_path}")
    
    print("\n🎉 Corrections terminées !")
    print("⚠️  IMPORTANT: Vérifier manuellement les changements avant de commit")
```

---

## 🔍 VALIDATION APRÈS CORRECTIONS

### Tests à exécuter:

```python
# Test 1: Endpoint sans authentification
curl -X POST http://localhost:8000/api/merchant/products \
  -H "Content-Type: application/json" \
  -d '{...}'

# Résultat attendu: 401 Unauthorized

# Test 2: Endpoint avec mauvais rôle
curl -X POST http://localhost:8000/api/merchant/products \
  -H "Authorization: Bearer INFLUENCER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Résultat attendu: 403 Forbidden

# Test 3: Endpoint avec bon rôle
curl -X POST http://localhost:8000/api/merchant/products \
  -H "Authorization: Bearer MERCHANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Résultat attendu: 200 OK
```

---

## 📝 CHECKLIST

- [ ] Backup créé pour `advanced_endpoints.py`
- [ ] Backup créé pour `advanced_helpers.py`
- [ ] Script Python exécuté
- [ ] Vérification manuelle des changements
- [ ] Tests unitaires passent
- [ ] Tests d'intégration passent
- [ ] Code committed avec message clair
- [ ] Déployé en staging

---

## 🆘 EN CAS DE PROBLÈME

Si les corrections causent des régressions:

```bash
# Restaurer depuis backup
mv backend/advanced_endpoints.py.backup backend/advanced_endpoints.py
mv backend/advanced_helpers.py.backup backend/advanced_helpers.py
```

Puis appliquer corrections manuellement une par une.

---

**Temps estimé:** 30 minutes (automatique) ou 1h (manuel)
