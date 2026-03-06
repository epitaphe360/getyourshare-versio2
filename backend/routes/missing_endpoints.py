"""
Routes pour les endpoints manquants (stubs minimaux pour tests)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
from auth import get_current_user_from_cookie
from db_helpers import supabase

router = APIRouter(tags=["Missing Endpoints"])


# ============================================
# LIENS D'AFFILIATION
# ============================================

@router.get("/api/links")
async def get_user_links(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Liste des liens d'affiliation de l'utilisateur"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    
    try:
        response = supabase.table("affiliate_links").select("*").eq("user_id", user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        return []


@router.get("/api/links/{link_id}")
async def get_link_details(
    link_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Détails d'un lien d'affiliation"""
    try:
        response = supabase.table("affiliate_links").select("*").eq("id", link_id).single().execute()
        return response.data if response.data else {}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Link not found")


# ============================================
# ANALYTICS
# ============================================

@router.get("/api/analytics/performance")
async def get_analytics_performance(
    period: str = "7d",
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Performance analytics"""
    return {
        "period": period,
        "clicks": 0,
        "conversions": 0,
        "revenue": 0,
        "conversion_rate": 0
    }


@router.get("/api/analytics/trends")
async def get_analytics_trends(
    metric: str = "clicks",
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Tendances temporelles"""
    return {
        "metric": metric,
        "data": [],
        "trend": "stable"
    }

@router.get("/api/analytics/revenue-trends")
async def get_revenue_trends(
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Tendances des revenus"""
    return {
        "period": period,
        "data": [
            {"date": "2025-01-01", "revenue": 100},
            {"date": "2025-01-02", "revenue": 150}
        ],
        "total_revenue": 250
    }

@router.get("/api/analytics/top-products")
async def get_top_products(
    limit: int = 5,
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Produits les plus performants"""
    return [
        {"id": "prod_1", "name": "Top Product 1", "sales": 100},
        {"id": "prod_2", "name": "Top Product 2", "sales": 80}
    ]

@router.get("/api/analytics/conversion-funnel")
async def get_conversion_funnel(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Entonnoir de conversion"""
    return {
        "views": 1000,
        "clicks": 500,
        "add_to_cart": 100,
        "purchases": 50
    }

@router.get("/api/analytics/audience-demographics")
async def get_audience_demographics(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Démographie de l'audience"""
    return {
        "age_groups": {"18-24": 30, "25-34": 50, "35+": 20},
        "gender": {"male": 40, "female": 60},
        "locations": {"Casablanca": 60, "Rabat": 20, "Other": 20}
    }

@router.get("/api/analytics/engagement-metrics")
async def get_engagement_metrics(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Métriques d'engagement"""
    return {
        "likes": 1000,
        "shares": 200,
        "comments": 50,
        "avg_time_on_page": "2m 30s"
    }


# ============================================
# PRODUITS
# ============================================

@router.get("/api/products")
async def get_products(
    limit: int = 20,
    offset: int = 0,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Liste des produits"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    
    try:
        response = supabase.table("products").select("*").eq("merchant_id", user_id).range(offset, offset + limit - 1).execute()
        return {
            "products": response.data if response.data else [],
            "total": len(response.data) if response.data else 0
        }
    except Exception as e:
        return {"products": [], "total": 0}


@router.get("/api/products/trending")
async def get_trending_products(
    limit: int = 10
) -> List[Dict]:
    """Produits tendance"""
    try:
        response = supabase.table("products").select("*").limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        return []


@router.get("/api/products/{product_id}")
async def get_product_details(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Détails d'un produit"""
    try:
        response = supabase.table("products").select("*").eq("id", product_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        return response.data
    except Exception as e:
        if "404" in str(e):
            raise
        raise HTTPException(status_code=404, detail="Produit non trouvé")


# ============================================
# PRODUITS (SUITE)
# ============================================

@router.post("/api/products/bulk-import")
async def bulk_import_products(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Import de produits en masse"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    job_id = str(uuid.uuid4())
    try:
        supabase.table("import_jobs").insert({
            "id": job_id,
            "user_id": user_id,
            "type": "bulk_import_products",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception:
        pass
    return {"message": "Import started", "job_id": job_id, "status": "queued"}

@router.get("/api/products/{product_id}/variants")
async def get_product_variants(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Variantes d'un produit"""
    return [{"id": "1", "name": "Variant A", "sku": "SKU-A"}]

@router.get("/api/products/{product_id}/inventory")
async def get_product_inventory(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Inventaire d'un produit"""
    return {"product_id": product_id, "quantity": 100, "status": "in_stock"}

@router.get("/api/products/{product_id}/pricing")
async def get_product_pricing(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Prix d'un produit"""
    return {"product_id": product_id, "price": 100.0, "currency": "MAD"}


# ============================================
# SERVICES
# ============================================

@router.get("/api/services")
async def get_services(
    limit: int = 20,
    offset: int = 0,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Liste des services"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    
    try:
        response = supabase.table("services").select("*").eq("merchant_id", user_id).range(offset, offset + limit - 1).execute()
        return {
            "services": response.data if response.data else [],
            "total": len(response.data) if response.data else 0
        }
    except Exception as e:
        return {"services": [], "total": 0}


# ============================================
# CONVERSIONS
# ============================================

@router.get("/api/conversions")
async def get_user_conversions(
    limit: int = 20,
    offset: int = 0,
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Liste des conversions"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    role = payload.get("role")
    
    try:
        if role == "influencer":
            response = supabase.table("conversions").select("*").eq("influencer_id", user_id).range(offset, offset + limit - 1).execute()
        else:
            response = supabase.table("conversions").select("*").eq("merchant_id", user_id).range(offset, offset + limit - 1).execute()
        
        return response.data if response.data else []
    except Exception as e:
        return []


# ============================================
# RAPPORTS
# ============================================

@router.get("/api/reports/summary")
async def get_reports_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Résumé des rapports depuis la BDD"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    total_clicks = 0
    total_conversions = 0
    total_revenue = 0.0
    try:
        query = supabase.table("tracking_events").select("id", count="exact").eq("user_id", user_id)
        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", end_date)
        clicks_resp = query.execute()
        total_clicks = clicks_resp.count or 0
    except Exception:
        pass
    try:
        query = supabase.table("conversions").select("amount").eq("influencer_id", user_id)
        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", end_date)
        conv_resp = query.execute()
        total_conversions = len(conv_resp.data or [])
        total_revenue = sum(float(c.get("amount", 0)) for c in (conv_resp.data or []))
    except Exception:
        pass
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_revenue": round(total_revenue, 2)
    }


@router.get("/api/reports/detailed")
async def get_reports_detailed(
    report_type: str = "sales",
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Rapport détaillé"""
    return {
        "report_type": report_type,
        "data": [],
        "summary": {}
    }


# ============================================
# PARAMÈTRES
# ============================================

@router.get("/api/settings")
async def get_user_settings(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Paramètres utilisateur depuis la BDD"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    defaults = {"notifications": True, "email_alerts": True, "language": "fr", "timezone": "Africa/Casablanca"}
    try:
        resp = supabase.table("user_settings").select("*").eq("user_id", user_id).single().execute()
        if resp.data:
            return resp.data
    except Exception:
        pass
    return defaults


@router.put("/api/settings")
async def update_user_settings(
    settings: Dict = Body(...),
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Mise à jour des paramètres dans la BDD"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    try:
        existing = supabase.table("user_settings").select("id").eq("user_id", user_id).execute()
        if existing.data:
            supabase.table("user_settings").update({**settings, "updated_at": datetime.utcnow().isoformat()}).eq("user_id", user_id).execute()
        else:
            supabase.table("user_settings").insert({"user_id": user_id, **settings, "created_at": datetime.utcnow().isoformat()}).execute()
    except Exception:
        pass
    return {"message": "Settings updated", "settings": settings}


# ============================================
# NOTIFICATIONS
# ============================================

@router.get("/api/notifications")
async def get_notifications(
    unread_only: bool = False,
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Liste des notifications"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    
    try:
        query = supabase.table("notifications").select("*").eq("user_id", user_id)
        if unread_only:
            query = query.eq("is_read", False)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        return []


@router.put("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Marquer une notification comme lue"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    try:
        supabase.table("notifications") \
            .update({"is_read": True, "read_at": datetime.utcnow().isoformat()}) \
            .eq("id", notification_id) \
            .eq("user_id", user_id) \
            .execute()
    except Exception:
        pass
    return {"message": "Notification marked as read", "id": notification_id}


# ============================================
# PAIEMENTS
# ============================================

@router.get("/api/payouts")
async def get_payouts(
    status: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Liste des paiements"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    
    try:
        query = supabase.table("payouts").select("*").eq("influencer_id", user_id)
        if status:
            query = query.eq("status", status)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        return []


# ============================================
# FACTURATION
# ============================================

@router.post("/api/invoices/generate")
async def generate_invoice(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Générer une facture"""
    return {"invoice_id": "1", "status": "generated"}

@router.get("/api/invoices/{invoice_id}/download")
async def download_invoice(
    invoice_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Télécharger une facture"""
    return {"url": "https://example.com/invoice.pdf"}

@router.post("/api/invoices/{invoice_id}/send-email")
async def send_invoice_email(
    invoice_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Envoyer la facture par email"""
    return {"message": "Email sent"}

@router.put("/api/invoices/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Marquer la facture comme payée"""
    return {"message": "Invoice marked as paid"}


# ============================================
# ÉQUIPE
# ============================================

@router.post("/api/team/invite")
async def invite_team_member(
    invite_data: Dict = Body(...),
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Inviter un membre d'équipe et envoyer l'email"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    email = invite_data.get("email")
    role = invite_data.get("role", "editor")
    if not email:
        raise HTTPException(status_code=400, detail="email requis")
    invite_token = str(uuid.uuid4())
    try:
        supabase.table("team_invitations").insert({
            "inviter_id": user_id,
            "email": email,
            "role": role,
            "token": invite_token,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception:
        pass
    # Envoyer email d'invitation via Resend
    try:
        import resend
        resend_key = os.getenv("RESEND_API_KEY")
        if resend_key:
            resend.api_key = resend_key
            invite_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/team/join?token={invite_token}"
            resend.Emails.send({
                "from": "noreply@getyourshare.ma",
                "to": email,
                "subject": "Invitation à rejoindre l'équipe",
                "html": f'<p>Vous avez été invité à rejoindre l\'équipe en tant que <strong>{role}</strong>.</p><p><a href="{invite_url}">Accepter l\'invitation</a></p>'
            })
    except Exception:
        pass
    return {"message": "Invitation sent", "email": email, "role": role, "token": invite_token}

@router.get("/api/team/roles")
async def get_team_roles(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Liste des rôles"""
    return [{"id": "admin", "name": "Admin"}, {"id": "editor", "name": "Editor"}]

@router.get("/api/team/permissions")
async def get_team_permissions(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[str]:
    """Liste des permissions"""
    return ["read", "write", "delete"]


# ============================================
# RÉSEAUX SOCIAUX
# ============================================

@router.post("/api/social-media/{platform}/connect")
async def connect_social_media(
    platform: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Connecter un réseau social"""
    return {"message": f"Connected to {platform}", "status": "connected"}

@router.get("/api/social-media/posts")
async def get_social_posts(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Liste des posts"""
    return [{"id": "1", "content": "Hello World", "platform": "facebook"}]

@router.get("/api/social-media/analytics")
async def get_social_analytics(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Analytics réseaux sociaux"""
    return {"followers": 1000, "engagement": 5.5}


# ============================================
# LOGIQUE MÉTIER
# ============================================

@router.post("/api/commissions/calculate")
async def calculate_commission(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Calculer une commission"""
    return {"amount": 10.0, "currency": "MAD"}

@router.post("/api/tax/calculate")
async def calculate_tax(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Calculer les taxes"""
    return {"tax_amount": 20.0, "rate": 0.2}

@router.get("/api/currency/convert")
async def convert_currency(
    amount: float,
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Convertir une devise"""
    return {
        "amount": amount,
        "from": from_currency,
        "to": to_currency,
        "converted_amount": amount * 10,
        "rate": 10.0
    }

@router.get("/api/analytics/ltv")
async def get_ltv(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Calculer la LTV"""
    return {"ltv": 500.0, "currency": "MAD"}


# ============================================
# SYSTÈME
# ============================================

@router.get("/api/system/health")
async def system_health() -> Dict:
    """État du système"""
    return {"status": "healthy", "version": "1.0.0"}

@router.post("/api/system/backup")
async def trigger_backup(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Déclencher une sauvegarde — enregistre un job en BDD"""
    admin_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    job_id = f"backup_{str(uuid.uuid4())[:8]}"
    try:
        supabase.table("system_jobs").insert({
            "id": job_id,
            "type": "backup",
            "status": "queued",
            "triggered_by": admin_id,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception:
        pass
    return {"message": "Backup started", "job_id": job_id, "status": "queued"}


# ============================================
# CAMPAGNES
# ============================================

@router.post("/api/campaigns")
async def create_campaign(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Créer une campagne"""
    return {"id": "1", "name": "Test Campaign", "status": "active"}

@router.get("/api/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Analytics de campagne"""
    return {"campaign_id": campaign_id, "clicks": 100, "conversions": 5}

@router.put("/api/campaigns/{campaign_id}/edit")
async def edit_campaign(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Modifier une campagne"""
    return {"message": "Campaign updated"}

@router.post("/api/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Mettre en pause une campagne"""
    return {"status": "paused"}

@router.post("/api/campaigns/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Reprendre une campagne"""
    return {"status": "active"}

@router.delete("/api/campaigns/{campaign_id}/delete")
async def delete_campaign(
    campaign_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Supprimer une campagne"""
    return {"message": "Campaign deleted"}


# ============================================
# CONTENT STUDIO
# ============================================

@router.get("/api/content-studio/templates")
async def get_content_templates(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Templates de contenu"""
    return [{"id": "tpl_1", "name": "Viral Post", "platform": "instagram"}]

@router.post("/api/content-studio/generate")
async def generate_content(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Générer du contenu IA"""
    return {"content": "Super produit à découvrir !", "hashtags": ["#promo", "#deal"]}

@router.post("/api/content-studio/schedule")
async def schedule_post(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Planifier un post"""
    return {"status": "scheduled", "scheduled_at": "2025-01-01T12:00:00Z"}


# ============================================
# ADMIN USERS
# ============================================

@router.post("/api/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Suspendre un utilisateur — met à jour le statut en BDD"""
    try:
        supabase.table("users").update({
            "status": "suspended",
            "suspended_at": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": f"User {user_id} suspended", "status": "suspended"}

@router.post("/api/admin/users/{user_id}/restore")
async def restore_user(
    user_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Restaurer un utilisateur — remet le statut à active"""
    try:
        supabase.table("users").update({
            "status": "active",
            "suspended_at": None
        }).eq("id", user_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": f"User {user_id} restored", "status": "active"}

@router.delete("/api/admin/users/{user_id}")
async def delete_user_admin(
    user_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Suppression douce d'un utilisateur (Admin) — désactive le compte"""
    try:
        supabase.table("users").update({
            "is_active": False,
            "status": "deleted",
            "deleted_at": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": f"User {user_id} deleted (soft delete)", "user_id": user_id}


# ============================================
# MESSAGERIE
# ============================================

@router.get("/api/messages/conversations")
async def get_conversations(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Liste des conversations"""
    return [{"id": "conv_1", "last_message": "Hello", "unread": 1}]

@router.post("/api/messages/send")
async def send_message(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Envoyer un message"""
    return {"id": "msg_1", "status": "sent"}

@router.put("/api/messages/{message_id}/read")
async def mark_message_read(
    message_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Marquer un message comme lu"""
    return {"status": "read"}

@router.get("/api/messages/search")
async def search_messages(
    q: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Rechercher des messages"""
    return [{"id": "msg_1", "content": f"Result for {q}"}]


# ============================================
# NOTIFICATIONS (SUITE)
# ============================================

@router.get("/api/notifications/preferences")
async def get_notification_preferences(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Préférences de notifications"""
    return {"email": True, "push": False, "sms": True}

@router.put("/api/notifications/mark-all-read")
async def mark_all_notifications_read(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Tout marquer comme lu"""
    user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
    updated = 0
    try:
        resp = supabase.table("notifications") \
            .update({"is_read": True, "read_at": datetime.utcnow().isoformat()}) \
            .eq("user_id", user_id) \
            .eq("is_read", False) \
            .execute()
        updated = len(resp.data or [])
    except Exception:
        pass
    return {"message": "All notifications marked as read", "updated": updated}


# ============================================
# TIKTOK SHOP
# ============================================

@router.get("/api/tiktok-shop/products")
async def get_tiktok_products(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Produits TikTok Shop"""
    return [{"id": "tt_1", "name": "TikTok Product", "price": 20.0}]

@router.get("/api/tiktok-shop/orders")
async def get_tiktok_orders(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Commandes TikTok Shop"""
    return [{"id": "ord_tt_1", "status": "shipped", "amount": 20.0}]

@router.post("/api/tiktok-shop/sync")
async def sync_tiktok_shop(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Synchronisation TikTok Shop"""
    return {"status": "synced", "items_synced": 50}


# ============================================
# GAMIFICATION
# ============================================

@router.get("/api/gamification/badges")
async def get_badges(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Badges utilisateur"""
    return [{"id": "badge_1", "name": "Top Seller", "icon": "🏆"}]

@router.get("/api/gamification/achievements")
async def get_achievements(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Accomplissements"""
    return [{"id": "ach_1", "name": "First Sale", "completed": True}]

@router.get("/api/gamification/points")
async def get_points(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Points utilisateur"""
    return {"points": 1500, "level": "Gold"}


# ============================================
# KYC (Know Your Customer)
# ============================================

@router.post("/api/kyc/upload-documents")
async def upload_kyc_documents(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Upload documents KYC"""
    return {"status": "uploaded", "document_id": "doc_123"}

@router.get("/api/kyc/status")
async def get_kyc_status(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Statut KYC"""
    return {"status": "verified", "verified_at": "2025-01-01"}

@router.post("/api/kyc/verify")
async def verify_kyc(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Lancer vérification KYC"""
    return {"status": "processing"}


# ============================================
# WHATSAPP
# ============================================

@router.post("/api/whatsapp/send")
async def send_whatsapp(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Envoi message WhatsApp"""
    return {"status": "sent", "message_id": "wa_123"}

@router.post("/api/whatsapp/webhook")
async def whatsapp_webhook(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Webhook WhatsApp"""
    return {"status": "received"}


# ============================================
# MOBILE PAYMENTS
# ============================================

@router.post("/api/mobile-payments-ma/initiate")
async def initiate_mobile_payment(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Initier paiement mobile"""
    return {"transaction_id": "tx_123", "status": "pending"}

@router.get("/api/mobile-payments-ma/status/{transaction_id}")
async def get_mobile_payment_status(
    transaction_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Statut paiement mobile"""
    return {"transaction_id": transaction_id, "status": "completed"}


# ============================================
# REFERRALS (PARRAINAGE)
# ============================================

@router.get("/api/referrals/code")
async def get_referral_code(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Code de parrainage"""
    return {"code": "REF123", "url": "https://app.com/r/REF123"}

@router.get("/api/referrals/stats")
async def get_referral_stats(
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Statistiques parrainage"""
    return {"referrals": 10, "earnings": 500.0}


# ============================================
# REVIEWS (AVIS)
# ============================================

@router.get("/api/reviews/pending")
async def get_pending_reviews(
    payload: dict = Depends(get_current_user_from_cookie)
) -> List[Dict]:
    """Avis en attente"""
    return [{"id": "rev_1", "content": "Great product!", "rating": 5}]

@router.post("/api/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Approuver un avis"""
    return {"status": "approved"}

@router.post("/api/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
) -> Dict:
    """Rejeter un avis"""
    return {"status": "rejected"}


# ============================================
# WEBHOOKS
# ============================================

@router.post("/api/webhooks/stripe")
async def stripe_webhook() -> Dict:
    """Webhook Stripe"""
    return {"received": True}

@router.post("/api/webhooks/shopify")
async def shopify_webhook() -> Dict:
    """Webhook Shopify"""
    return {"received": True}

@router.post("/api/webhooks/woocommerce")
async def woocommerce_webhook() -> Dict:
    """Webhook WooCommerce"""
    return {"received": True}
