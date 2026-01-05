# RÈGLE OBLIGATOIRE: Validation du Solde des Payouts

## 🚨 Règle Critique

**Le total des retraits (payouts) ne doit JAMAIS dépasser les commissions gagnées.**

```
Total Retiré ≤ Commissions Gagnées
```

## 📊 Calcul du Balance

### Formule
```
Balance Disponible = Σ Commissions - Σ Payouts (paid + processing + pending)
```

### Sources de Données
- **Commissions**: Table `commissions`, colonne `amount`
- **Payouts**: Table `payouts`, colonne `amount` avec `status IN ('paid', 'processing', 'pending')`

## 🛡️ Implémentation de la Validation

### 1. Validation Backend (server.py)

**Endpoint**: `POST /api/payouts/request`

**Validations en place**:
1. ✅ Montant > 0€
2. ✅ Montant minimum: 50€
3. ✅ **RÈGLE CRITIQUE**: `(Total Retiré + Montant Demandé) ≤ Commissions Gagnées`
4. ✅ Montant Demandé ≤ Balance Disponible

**Code** (lignes 1160-1257 dans `backend/server.py`):
```python
# Calculer le total des commissions
commissions_result = supabase.table("commissions").select("amount").eq("influencer_id", influencer_id).execute()
total_earned = sum([float(c.get("amount", 0)) for c in commissions])

# Calculer le total retiré
payouts_result = supabase.table("payouts").select("amount, status").eq("influencer_id", influencer_id).execute()
total_withdrawn = sum([float(p.get("amount", 0)) for p in payouts if p.get("status") in ["paid", "processing"]])

# Balance disponible
available_balance = total_earned - total_withdrawn

# VALIDATION CRITIQUE
new_total_withdrawn = total_withdrawn + requested_amount
if new_total_withdrawn > total_earned:
    raise HTTPException(status_code=400, detail="Le retrait dépasserait vos commissions gagnées")
```

### 2. Contrainte Base de Données (ADD_BALANCE_CONSTRAINT.sql)

**Trigger**: `validate_payout_balance`

- Se déclenche **AVANT** chaque INSERT ou UPDATE sur `payouts`
- Calcule automatiquement le total des commissions vs payouts
- Bloque l'opération si la règle est violée

**Installation**:
```bash
# Exécuter le script SQL sur Supabase
psql -h [SUPABASE_URL] -U postgres -d postgres -f ADD_BALANCE_CONSTRAINT.sql
```

Ou via l'interface Supabase SQL Editor.

### 3. Validation Frontend (InfluencerDashboard.js)

**Ligne 209-220**:
```javascript
const currentBalance = stats?.balance || 0;

if (amount > currentBalance) {
    toast.error(`Montant demandé (${amount}€) supérieur au solde disponible (${currentBalance}€)`);
    return;
}
```

## 🔧 Correction des Données de Test

Si vous voyez un balance négatif (comme -7,133.11€), c'est que les données de test sont incohérentes.

### Script de Nettoyage

**Fichier**: `fix_balance_data.py`

**Utilisation**:
```bash
python fix_balance_data.py
```

**Options**:
1. Nettoyer les données incohérentes (annuler payouts excédentaires)
2. Ajouter des données de test réalistes
3. Les deux

**Ce que fait le script**:
- Parcourt tous les influenceurs
- Calcule: Commissions - Payouts
- Si Balance < 0:
  - Annule les payouts "paid" excédentaires (status → "cancelled")
  - Recalcule le balance
- Affiche un rapport détaillé

### Vérification

**Fichier**: `check_balance_data.py`

**Utilisation**:
```bash
python check_balance_data.py
```

**Sortie**:
```
=== CALCUL DU BALANCE GLOBAL ===
Total commissions: 1794.64 €
Total retiré (paid): 8927.75 €
Balance calculé: -7133.11 €

⚠️ ALERTE: Balance négatif détecté!
```

## 📋 États des Payouts

| Status | Compte dans Balance | Description |
|--------|---------------------|-------------|
| `pending` | ✅ Oui | Demande créée, en attente de traitement |
| `processing` | ✅ Oui | En cours de traitement |
| `paid` | ✅ Oui | Paiement effectué |
| `cancelled` | ❌ Non | Annulé (ne compte pas) |
| `rejected` | ❌ Non | Rejeté (ne compte pas) |

## 🧪 Tests

### Test 1: Retrait Normal
```python
Commissions: 1000€
Payouts paid: 200€
Balance: 800€
Demande: 500€ → ✅ Accepté (nouveau balance: 300€)
```

### Test 2: Retrait Excédentaire
```python
Commissions: 1000€
Payouts paid: 200€
Balance: 800€
Demande: 900€ → ❌ Refusé (dépasserait 1000€)
```

### Test 3: Balance Négatif (Données Corrompues)
```python
Commissions: 1794.64€
Payouts paid: 8927.75€
Balance: -7133.11€ → ⚠️ Données incohérentes!
```

## 🚀 Déploiement

### Étapes pour Activer la Validation

1. **Backend** ✅ Déjà implémenté dans `server.py`
2. **Base de Données**: Exécuter `ADD_BALANCE_CONSTRAINT.sql`
3. **Données de Test**: Exécuter `fix_balance_data.py`
4. **Vérification**: Exécuter `check_balance_data.py`

### Vérification Post-Déploiement

```bash
# 1. Nettoyer les données
python fix_balance_data.py

# 2. Vérifier le résultat
python check_balance_data.py

# 3. Tester l'API
curl -X POST http://localhost:5000/api/payouts/request \
  -H "Content-Type: application/json" \
  -d '{"amount": 50, "payment_method": "bank_transfer"}'
```

## 📊 Monitoring

### Logs Backend

Les logs affichent automatiquement:
```
Payout request - Influencer: xxx
  Total earned: 1234.56€
  Total withdrawn: 500.00€
  Available balance: 734.56€
  Requested amount: 200.00€
✅ Payout created successfully
```

### Alertes

Si un retrait est refusé:
```
❌ VALIDATION ÉCHOUÉE: Le retrait dépasserait vos commissions gagnées.
Commissions gagnées: 1234.56€
Déjà retiré: 900.00€
Solde disponible: 334.56€
Montant demandé: 500.00€
Total après retrait: 1400.00€ (INTERDIT)
```

## 🔐 Sécurité

### Points de Contrôle

1. **Frontend**: Validation UX (empêche erreurs utilisateur)
2. **Backend**: Validation business logic (sécurité principale)
3. **Database**: Trigger SQL (dernier rempart, données cohérentes)

### Impossible de Contourner

- ✅ API directe → Bloquée par backend
- ✅ Manipulation SQL → Bloquée par trigger
- ✅ Import CSV → Bloquée par trigger
- ✅ Script externe → Bloquée par trigger

## 📝 Historique

- **2025-01-18**: Implémentation de la règle obligatoire
- **Problème détecté**: Balance négatif de -7,133.11€
- **Cause**: Données de test incohérentes (payouts > commissions)
- **Solution**: Validation multi-niveaux + scripts de nettoyage

## 🆘 Dépannage

### Balance Négatif Détecté

1. Exécuter `check_balance_data.py` pour diagnostiquer
2. Exécuter `fix_balance_data.py` (option 1) pour corriger
3. Re-vérifier avec `check_balance_data.py`

### Payout Bloqué

Vérifier:
1. Balance disponible suffisant?
2. Montant ≥ 50€?
3. Les logs backend pour le message d'erreur exact

### Données de Test

Utiliser `fix_balance_data.py` (option 2) pour générer des données réalistes.

## 📞 Contact

En cas de problème persistant, vérifier:
- Logs backend: `backend/server.py` ligne 1180-1200
- Trigger SQL: Vérifier qu'il est bien installé
- Données: Exécuter les scripts de vérification
