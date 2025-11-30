# 🔒 CORRECTIONS BACKEND - Protection des Endpoints par Abonnement

**Date:** 28 novembre 2025  
**Priorité:** HAUTE

---

## PROBLÈME IDENTIFIÉ

Les endpoints de création de ressources dans `server.py` ne vérifient **PAS** les limites d'abonnement !

Un utilisateur peut contourner les restrictions UI en appelant directement l'API.

---

## ENDPOINTS À PROTÉGER

### 1. Création Produits (Merchant)

**Fichier:** `backend/server.py`  
**Ligne:** À trouver `@app.post` pour produits

**Correction:**
```python
from subscription_limits_middleware import SubscriptionLimits

# Ajouter dans les imports en haut du fichier
SUBSCRIPTION_LIMITS_ENABLED = True  # Mettre False pour désactiver temporairement

# Pour chaque endpoint de création de produit:
@app.post("/api/products")
async def create_product(
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie),
    _: bool = Depends(SubscriptionLimits.check_product_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    ...
```

---

### 2. Création Campagnes (Tous)

**Ligne:** ~2947

**Avant:**
```python
@app.post("/api/campaigns")
async def create_campaign(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
```

**Après:**
```python
@app.post("/api/campaigns")
async def create_campaign(
    request: Request, 
    current_user: dict = Depends(get_current_user_from_cookie),
    _: bool = Depends(SubscriptionLimits.check_campaign_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
```

---

### 3. Création Liens d'Affiliation (Influencer)

**Lignes:** ~1404, ~2732

**Correction:**
```python
@app.post("/api/affiliate-links")
async def create_affiliate_link(
    request: Request,
    payload: dict = Depends(get_current_user_from_cookie),
    _: bool = Depends(SubscriptionLimits.check_link_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
```

---

### 4. Commercial - Leads

**Ligne:** ~8753

**Correction:**
```python
@app.post("/api/commercial/leads")
async def create_commercial_lead(
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    # Vérifier limite leads pour Starter (10/mois)
    if current_user.get('subscription_tier', 'starter') == 'starter':
        # Compter les leads du mois
        result = supabase.table("leads").select("id", count="exact").eq(
            "created_by", current_user["id"]
        ).gte("created_at", datetime.now().replace(day=1).isoformat()).execute()
        
        if result.count >= 10:
            raise HTTPException(
                status_code=403,
                detail="Limite de 10 leads/mois atteinte. Passez à Pro pour illimité."
            )
    ...
```

---

### 5. Commercial - Tracking Links

**Ligne:** ~8824

**Correction:**
```python
@app.post("/api/commercial/tracking-links")
async def create_tracking_link(
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    # Vérifier limite liens pour Starter (3 max)
    if current_user.get('subscription_tier', 'starter') == 'starter':
        result = supabase.table("commercial_tracking_links").select("id", count="exact").eq(
            "created_by", current_user["id"]
        ).execute()
        
        if result.count >= 3:
            raise HTTPException(
                status_code=403,
                detail="Limite de 3 liens trackés atteinte. Passez à Pro pour illimité."
            )
    ...
```

---

## IMPORT À AJOUTER

En haut de `server.py`:

```python
# Après les imports existants
try:
    from subscription_limits_middleware import SubscriptionLimits
    SUBSCRIPTION_LIMITS_ENABLED = True
except ImportError:
    SUBSCRIPTION_LIMITS_ENABLED = False
    print("⚠️ subscription_limits_middleware not available - limits disabled")
```

---

## VÉRIFICATION POST-CORRECTION

Après avoir appliqué les corrections, tester avec curl:

```bash
# Test création produit au-delà de la limite (Freemium = 5 max)
curl -X POST http://localhost:5000/api/products \
  -H "Authorization: Bearer <token_freemium_user>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product 6"}'

# Devrait retourner:
# 403 Forbidden - "Product limit reached (5/5). Please upgrade your plan."
```

---

## PRIORITÉ DE CORRECTION

| Endpoint | Priorité | Risque si non protégé |
|----------|----------|----------------------|
| `/api/commercial/leads` | 🔴 HAUTE | Abus du système de leads |
| `/api/commercial/tracking-links` | 🔴 HAUTE | Liens illimités |
| `/api/affiliate-links` | 🟡 MOYENNE | Liens d'affiliation illimités |
| `/api/campaigns` | 🟡 MOYENNE | Campagnes illimitées |
| `/api/products` | 🟢 BASSE | Produits illimités (moins critique) |
