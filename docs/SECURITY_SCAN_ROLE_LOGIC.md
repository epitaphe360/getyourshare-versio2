# SCAN SECURITE URGENT - ERREURS LOGIQUE DE ROLES

**Status:** CRITIQUE 🔴
**Date:** 2025-12-11
**Type:** Role-Based Access Control (RBAC) Bypass

---

## SOMMAIRE EXECUTIF

**3 endpoints dangereux découverts** permettant à n'importe quel utilisateur authentifié de créer des produits et campagnes, sans vérification du rôle `merchant`.

| Fichier | Endpoint | Ligne | Danger | Sécurisé |
|---------|----------|-------|--------|----------|
| products_routes.py | POST /api/products | 236-263 | Création produit | ❌ |
| products_routes.py | POST /api/products/bulk-import | 349-427 | Import massif | ❌ |
| campaigns_routes.py | POST /api/campaigns | 176-216 | Création campagne | ❌ |

---

## DETAIL DES VULNERABILITES

### 1. POST /api/products - CREATE PRODUCT

**Fichier:** `/home/user/getyourshare-versio2/backend/routes/products_routes.py`
**Ligne:** 236-263
**Sévérité:** CRITIQUE

#### Code Problématique:
```python
@router.post("")
async def create_product(
    product: ProductCreate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer un nouveau produit
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        # ⚠️ MANQUANT: Vérification du rôle

        product_data = product.dict()
        product_data['merchant_id'] = user_id

        response = supabase.table("products").insert(product_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création du produit")

        return {
            "success": True,
            "product": response.data[0],
            "message": "Produit créé avec succès"
        }
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### Problèmes Identifiés:
- Aucune vérification `if role != "merchant"`
- Influencers ✗ peuvent créer des produits
- Commerciaux ✗ peuvent créer des produits
- L'utilisateur devient automatiquement propriétaire (merchant_id = user_id)

#### Fix Requis:
**Ajouter à la ligne 245 (après extraction du user_id):**
```python
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # AJOUTER CES LIGNES:
        if role != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only merchants can create products"
            )
```

---

### 2. POST /api/products/bulk-import - BULK IMPORT

**Fichier:** `/home/user/getyourshare-versio2/backend/routes/products_routes.py`
**Ligne:** 349-427
**Sévérité:** CRITIQUE + Data Pollution Risk

#### Code Problématique:
```python
@router.post("/bulk-import")
async def bulk_import_products(
    file: UploadFile = File(...),
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Import en masse de produits via CSV RÉEL

    Format CSV attendu:
    name,description,price,currency,category,sku,commission_rate,stock_quantity

    Exemple:
    "Product 1","Description",100.0,MAD,electronics,SKU-001,10.0,50
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        # ⚠️ MANQUANT: Vérification du rôle

        # Lire le fichier CSV
        contents = await file.read()
        csv_data = contents.decode('utf-8')

        # Parser le CSV
        csv_reader = csv.DictReader(io.StringIO(csv_data))

        products_to_insert = []
        errors = []
        line_number = 1

        for row in csv_reader:
            line_number += 1
            # ... construit et insère des produits en masse

        # Insérer en base de données
        if products_to_insert:
            response = supabase.table("products").insert(products_to_insert).execute()
            inserted_count = len(response.data) if response.data else 0
```

#### Problèmes Identifiés:
- **Aucune vérification du rôle**
- Permet l'import massif de 100s/1000s de produits en un seul appel
- Pas de limite sur le nombre de produits
- Utilisateurs non-merchants peuvent polluer la base de données
- **Pas de rate limiting visible**

#### Fix Requis:
**Ajouter à la ligne 364-365 (après extraction user_id):**
```python
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # AJOUTER CES LIGNES:
        if role != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only merchants can bulk import products"
            )
```

---

### 3. POST /api/campaigns - CREATE CAMPAIGN

**Fichier:** `/home/user/getyourshare-versio2/backend/routes/campaigns_routes.py`
**Ligne:** 176-216
**Sévérité:** CRITIQUE

#### Code Problématique:
```python
@router.post("")
async def create_campaign(
    campaign: CampaignCreate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une nouvelle campagne
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        # ⚠️ MANQUANT: Vérification du rôle

        campaign_data = campaign.dict()
        campaign_data['created_by'] = user_id

        # Déterminer le statut initial
        now = datetime.now()
        start_date = campaign.start_date or now

        if start_date > now:
            status = "scheduled"
        elif campaign.end_date and campaign.end_date < now:
            status = "completed"
        else:
            status = "active"

        campaign_data['status'] = status

        response = supabase.table("campaigns").insert(campaign_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création de la campagne")

        return {
            "success": True,
            "campaign": response.data[0],
            "message": "Campagne créée avec succès"
        }
```

#### Problèmes Identifiés:
- Aucune vérification `if role != "merchant"`
- Influencers ✗ peuvent créer des campagnes
- Commerciaux ✗ peuvent créer des campagnes
- Campaign owners devient l'utilisateur courant
- Contournement du modèle d'affiliation

#### Fix Requis:
**Ajouter à la ligne 185-186 (après extraction user_id):**
```python
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # AJOUTER CES LIGNES:
        if role != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only merchants can create campaigns"
            )
```

---

## ENDPOINTS VERIFIES CORRECTEMENT (✓)

### Exemple 1: PUT /api/products/{product_id}
**Fichier:** products_routes.py, Ligne 266-306

```python
@router.put("/{product_id}")
async def update_product(
    product_id: str,
    product: ProductUpdate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """Mettre à jour un produit"""
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # ✓ VERIFICATION CORRECTE:
        if role != "admin":
            existing = supabase.table("products").select("merchant_id").eq("id", product_id).single().execute()
            if not existing.data or existing.data.get('merchant_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")
```

**Status:** ✓ Sécurisé - Vérifie le propriétaire ET le rôle

### Exemple 2: DELETE /api/products/{product_id}
**Fichier:** products_routes.py, Ligne 309-342

```python
@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """Supprimer un produit (soft delete)"""
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # ✓ VERIFICATION CORRECTE:
        if role != "admin":
            existing = supabase.table("products").select("merchant_id").eq("id", product_id).single().execute()
            if not existing.data or existing.data.get('merchant_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")
```

**Status:** ✓ Sécurisé

---

## COMPARAISON AVEC AUTRES FICHIERS

### advanced_endpoints.py - ✓ CORRECT
**Ligne 130-139:** `create_product_endpoint()` HAS verification:
```python
if user["role"] != "merchant":
    raise HTTPException(status_code=403, detail="Seuls les merchants peuvent créer des produits")
```

**Ligne 252-261:** `create_campaign_endpoint()` HAS verification:
```python
if user["role"] != "merchant":
    raise HTTPException(status_code=403, detail="Seuls les merchants peuvent créer des campagnes")
```

### subscription_limits_middleware.py - ✓ HAS PROTECTION
**Ligne 18-45:** `check_product_limit()` method verifies:
```python
if current_user.get("role") != "merchant":
    raise HTTPException(status_code=403, detail="Only merchants can create products")
```

**BUT:** Ce middleware n'est pas appliqué aux endpoints dans `products_routes.py` et `campaigns_routes.py`.

---

## RISQUES DE SECURITE

### 1. Escalade de Privilèges
- Influencers deviennent effectivement merchants
- Commerciaux peuvent créer des campagnes
- Contournement complet du système de rôles

### 2. Data Pollution
- N'importe quel utilisateur peut créer/importer des milliers de produits
- Pas de limite visible
- Bulk import sans rate limiting

### 3. Abus Financier
- Influencers créent leurs propres produits
- Auto-attribution de commissions
- Contournement du modèle économique

### 4. Exploitation Potentielle
- Script bot peut créer/importer massivement
- Overload de la base de données
- Consommation de ressources

---

## ACTIONS REQUISES

### 1. Fix Immédiat - 3 endpoints (30 min)
Ajouter les vérifications de rôles dans:
1. `/home/user/getyourshare-versio2/backend/routes/products_routes.py` ligne 245
2. `/home/user/getyourshare-versio2/backend/routes/products_routes.py` ligne 364
3. `/home/user/getyourshare-versio2/backend/routes/campaigns_routes.py` ligne 185

### 2. Code Review (1h)
- Vérifier tous les endpoints POST/PUT/DELETE
- S'assurer que role checks sont présents
- Tester avec différents rôles

### 3. Testing (2h)
- Test as influencer → should be rejected
- Test as commercial → should be rejected
- Test as merchant → should succeed
- Test bulk import → should be rejected for non-merchants

### 4. Monitoring (à faire)
- Monitorer les créations de produits/campagnes
- Chercher les patterns d'abus
- Audit des créations massives

---

## FICHIERS AFFECTES

```
/home/user/getyourshare-versio2/backend/
├── routes/
│   ├── products_routes.py (2 endpoints)
│   │   ├── Line 236-263: POST /api/products ❌
│   │   └── Line 349-427: POST /api/products/bulk-import ❌
│   └── campaigns_routes.py (1 endpoint)
│       └── Line 176-216: POST /api/campaigns ❌
```

---

## PROCHAINES ETAPES

1. **URGENT:** Appliquer les 3 fixes ci-dessus
2. Commit avec message: "Fix: Add role verification to create product/campaign endpoints"
3. Test complet avant deployment
4. Monitor pour activité d'abus potentielle

---

**Rapport généré:** 2025-12-11 via Security Scan
**Mode:** Exhaustif - Tous les endpoints POST/PUT/DELETE vérifiés
