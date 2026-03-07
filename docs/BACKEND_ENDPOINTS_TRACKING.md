# 🔗 Endpoints Backend - Système de Tracking Commercial

## 📋 Vue d'ensemble

Endpoints à ajouter dans `backend/commercial_endpoints.py` pour gérer le système de tracking des ventes commerciales.

---

## 🆕 Nouveaux Endpoints

### 1. Générer un lien affilié

**Endpoint:** `POST /api/commercial/tracking/generate-link`

**Description:** Génère un lien affilié unique pour un commercial (optionnellement lié à un lead).

**Body:**
```json
{
  "lead_id": "uuid-optional",
  "campaign": "black_friday_2024"
}
```

**Réponse:**
```json
{
  "success": true,
  "data": {
    "tracking_link_id": "uuid",
    "unique_code": "COM-JOHN-A3F2D9",
    "full_url": "https://getyourshare.ma/pricing?ref=COM-JOHN-A3F2D9",
    "short_url": "https://gys.ma/john-a3f2d9"
  }
}
```

**Code Python:**
```python
@router.post("/tracking/generate-link")
async def generate_tracking_link(
    request: Request,
    lead_id: Optional[str] = None,
    campaign: Optional[str] = None
):
    """Génère un lien affilié pour le commercial connecté"""
    user = request.state.user
    
    if user['role'] != 'commercial':
        raise HTTPException(status_code=403, detail="Réservé aux commerciaux")
    
    # Appeler fonction PostgreSQL
    result = supabase.rpc(
        'generate_commercial_tracking_link',
        {
            'p_commercial_id': user['id'],
            'p_lead_id': lead_id,
            'p_campaign': campaign
        }
    ).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Erreur génération lien")
    
    return {
        "success": True,
        "data": result.data[0]
    }
```

---

### 2. Lister les liens affiliés

**Endpoint:** `GET /api/commercial/tracking/links`

**Query params:**
- `active_only`: boolean (default: true)
- `limit`: int (default: 50)
- `offset`: int (default: 0)

**Réponse:**
```json
{
  "success": true,
  "data": {
    "links": [
      {
        "id": "uuid",
        "unique_code": "COM-JOHN-A3F2D9",
        "tracking_url": "https://getyourshare.ma/pricing?ref=COM-JOHN-A3F2D9",
        "campaign": "black_friday_2024",
        "clicks": 45,
        "conversions": 3,
        "total_revenue": 2400.00,
        "commission_earned": 480.00,
        "created_at": "2024-11-30T10:00:00Z"
      }
    ],
    "total": 12,
    "stats": {
      "total_clicks": 234,
      "total_conversions": 18,
      "conversion_rate": 7.69,
      "total_commission": 3600.00
    }
  }
}
```

**Code Python:**
```python
@router.get("/tracking/links")
async def get_tracking_links(
    request: Request,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0
):
    """Liste les liens affiliés du commercial"""
    user = request.state.user
    
    query = supabase.table('commercial_tracking_links')\
        .select('*')\
        .eq('commercial_id', user['id'])
    
    if active_only:
        query = query.eq('is_active', True)
    
    result = query.order('created_at', desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    # Stats globales
    stats_result = supabase.table('commercial_tracking_stats')\
        .select('*')\
        .eq('commercial_id', user['id'])\
        .execute()
    
    return {
        "success": True,
        "data": {
            "links": result.data,
            "total": len(result.data),
            "stats": stats_result.data[0] if stats_result.data else {}
        }
    }
```

---

### 3. Tracker un clic (Public endpoint)

**Endpoint:** `GET /api/track/{tracking_code}`

**Description:** Endpoint PUBLIC pour tracker les clics (utilisé par les redirections).

**Réponse:** Redirection 302 vers la vraie URL.

**Code Python:**
```python
@router.get("/track/{tracking_code}")
async def track_click(
    tracking_code: str,
    request: Request
):
    """Track clic et redirige (endpoint public)"""
    # Récupérer infos
    ip_address = request.client.host
    user_agent = request.headers.get('user-agent', '')
    
    # Appeler fonction tracking
    result = supabase.rpc(
        'track_commercial_click',
        {
            'p_tracking_code': tracking_code,
            'p_ip_address': ip_address,
            'p_user_agent': user_agent
        }
    ).execute()
    
    # Récupérer URL de redirection
    link = supabase.table('commercial_tracking_links')\
        .select('tracking_url')\
        .eq('unique_code', tracking_code)\
        .execute()
    
    if not link.data:
        return RedirectResponse(url="https://getyourshare.ma/pricing")
    
    return RedirectResponse(url=link.data[0]['tracking_url'])
```

---

### 4. Statistiques de tracking

**Endpoint:** `GET /api/commercial/tracking/stats`

**Query params:**
- `period`: string ('7d', '30d', '90d', 'all')

**Réponse:**
```json
{
  "success": true,
  "data": {
    "total_links": 12,
    "active_links": 10,
    "total_clicks": 456,
    "total_conversions": 23,
    "conversion_rate": 5.04,
    "total_revenue": 15600.00,
    "total_commission": 3120.00,
    "top_performing_links": [
      {
        "unique_code": "COM-JOHN-A3F2D9",
        "campaign": "black_friday_2024",
        "clicks": 120,
        "conversions": 8,
        "revenue": 5400.00
      }
    ],
    "clicks_by_day": [
      {"date": "2024-11-23", "clicks": 45},
      {"date": "2024-11-24", "clicks": 67}
    ]
  }
}
```

**Code Python:**
```python
@router.get("/tracking/stats")
async def get_tracking_stats(
    request: Request,
    period: str = '30d'
):
    """Statistiques globales de tracking"""
    user = request.state.user
    
    # Stats depuis la vue
    stats = supabase.table('commercial_tracking_stats')\
        .select('*')\
        .eq('commercial_id', user['id'])\
        .execute()
    
    # Top performing links
    top_links = supabase.table('commercial_tracking_links')\
        .select('unique_code, campaign, clicks, conversions, total_revenue')\
        .eq('commercial_id', user['id'])\
        .order('conversions', desc=True)\
        .limit(5)\
        .execute()
    
    # Évolution clics (requête custom selon period)
    # TODO: Implémenter agrégation par jour
    
    return {
        "success": True,
        "data": {
            **stats.data[0] if stats.data else {},
            "top_performing_links": top_links.data
        }
    }
```

---

### 5. Gérer les codes promo

**Endpoint:** `POST /api/commercial/promo-codes`

**Body:**
```json
{
  "code": "JOHN20",
  "discount_type": "percentage",
  "discount_value": 20,
  "valid_until": "2025-12-31T23:59:59Z",
  "max_usage": 50,
  "applicable_plans": ["pro", "enterprise"]
}
```

**Code Python:**
```python
@router.post("/promo-codes")
async def create_promo_code(
    request: Request,
    code: str,
    discount_type: str,
    discount_value: float,
    valid_until: Optional[str] = None,
    max_usage: int = 100,
    applicable_plans: List[str] = ["starter", "pro", "enterprise"]
):
    """Créer un code promo personnalisé"""
    user = request.state.user
    
    result = supabase.table('promo_codes').insert({
        "code": code.upper(),
        "commercial_id": user['id'],
        "discount_type": discount_type,
        "discount_value": discount_value,
        "valid_until": valid_until,
        "max_usage": max_usage,
        "applicable_plans": applicable_plans
    }).execute()
    
    return {
        "success": True,
        "data": result.data[0]
    }

@router.get("/promo-codes")
async def list_promo_codes(request: Request):
    """Liste les codes promo du commercial"""
    user = request.state.user
    
    result = supabase.table('promo_codes')\
        .select('*')\
        .eq('commercial_id', user['id'])\
        .order('created_at', desc=True)\
        .execute()
    
    return {
        "success": True,
        "data": result.data
    }
```

---

### 6. Voir les commissions

**Endpoint:** `GET /api/commercial/commissions`

**Query params:**
- `status`: string ('pending', 'approved', 'paid', 'all')
- `period`: string ('7d', '30d', '90d', 'all')

**Réponse:**
```json
{
  "success": true,
  "data": {
    "commissions": [
      {
        "id": "uuid",
        "user_email": "client@example.com",
        "subscription_amount": 800.00,
        "commission_percentage": 20.00,
        "commission_amount": 160.00,
        "status": "approved",
        "attribution_type": "last_touch",
        "created_at": "2024-11-30T10:00:00Z",
        "paid_at": null
      }
    ],
    "summary": {
      "total_pending": 1240.00,
      "total_approved": 3600.00,
      "total_paid": 8900.00,
      "count_pending": 7,
      "count_approved": 18,
      "count_paid": 45
    }
  }
}
```

**Code Python:**
```python
@router.get("/commissions")
async def get_commissions(
    request: Request,
    status: str = 'all',
    period: str = '30d'
):
    """Liste des commissions du commercial"""
    user = request.state.user
    
    query = supabase.table('subscription_attributions')\
        .select('*, users!user_id(email, first_name, last_name)')\
        .eq('commercial_id', user['id'])
    
    if status != 'all':
        query = query.eq('status', status)
    
    # Filter par période
    # TODO: Ajouter filtre date selon period
    
    result = query.order('created_at', desc=True).execute()
    
    # Calculer summary
    summary = {
        'total_pending': sum(c['commission_amount'] for c in result.data if c['status'] == 'pending'),
        'total_approved': sum(c['commission_amount'] for c in result.data if c['status'] == 'approved'),
        'total_paid': sum(c['commission_amount'] for c in result.data if c['status'] == 'paid'),
        'count_pending': len([c for c in result.data if c['status'] == 'pending']),
        'count_approved': len([c for c in result.data if c['status'] == 'approved']),
        'count_paid': len([c for c in result.data if c['status'] == 'paid'])
    }
    
    return {
        "success": True,
        "data": {
            "commissions": result.data,
            "summary": summary
        }
    }
```

---

## 🔧 Modifications dans `backend/commercial_endpoints.py`

### Ajouter les imports

```python
from typing import Optional, List
from fastapi.responses import RedirectResponse
```

### Ajouter les nouveaux endpoints

Copier-coller tous les endpoints ci-dessus dans le fichier `commercial_endpoints.py`.

---

## 📝 Notes d'implémentation

1. **Sécurité:** 
   - L'endpoint `/track/{tracking_code}` doit être PUBLIC (pas d'auth)
   - Tous les autres endpoints nécessitent authentification commercial
   - RLS PostgreSQL protège automatiquement les données

2. **Performance:**
   - Les index créés dans le SQL garantissent des requêtes rapides
   - Utiliser les vues matérialisées pour les stats complexes

3. **Tests:**
   - Tester génération de liens
   - Vérifier tracking de clics
   - Valider calcul commissions
   - Tester expiration codes promo

4. **Monitoring:**
   - Logger tous les clics de tracking
   - Alerter si taux de conversion anormal
   - Surveiller usage codes promo

---

## ✅ Checklist d'intégration

- [ ] Ajouter imports nécessaires
- [ ] Copier endpoints dans `commercial_endpoints.py`
- [ ] Tester génération lien via Postman
- [ ] Tester redirection tracking
- [ ] Vérifier stats en temps réel
- [ ] Tester création code promo
- [ ] Valider calcul commissions
- [ ] Documenter API dans Swagger
- [ ] Ajouter logs d'audit
- [ ] Déployer en production

---

**Prochaine étape:** Voir `UI_COMPONENTS_TRACKING.md` pour l'intégration React.
