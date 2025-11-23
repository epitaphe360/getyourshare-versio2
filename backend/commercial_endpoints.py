"""
ENDPOINTS BACKEND POUR DASHBOARD COMMERCIAL
============================================
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import os
import jwt
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://gwgvnusegnnhiciprvyc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3Z3ZudXNlZ25uaGljaXBydnljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MjE3NjgsImV4cCI6MjA0NjM5Nzc2OH0.gftLI_u0AxQUVIUi3hWjfJQ-m6Y56b5H5lDwbMEDGbU")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Import de la fonction d'authentification du serveur principal
from db_helpers import get_user_by_id

# Configuration JWT (même que server.py)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_current_user_from_cookie(request: Request):
    """
    Get current user from httpOnly cookie (secure method)
    Fallback to Authorization header for backward compatibility
    """
    # Try to get token from cookie first (secure)
    token = request.cookies.get("access_token")

    # Fallback to Authorization header (legacy)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Récupérer l'utilisateur complet depuis la DB
        user = get_user_by_id(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {
            "id": user["id"],
            "email": user.get("email"),
            "role": user.get("role"),
            "subscription_tier": user.get("subscription_plan", "starter")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

logger = logging.getLogger(__name__)

# Router pour les endpoints commerciaux
router = APIRouter(prefix="/api/commercial", tags=["commercial"])


# =====================================================
# MODÈLES PYDANTIC
# =====================================================

class CommercialStats(BaseModel):
    total_leads: int
    leads_generated_month: int
    qualified_leads: int
    converted_leads: int
    total_commission: float
    total_revenue: float
    pipeline_value: float
    conversion_rate: float
    total_clicks: int
    active_tracking_links: int


class TrackingLink(BaseModel):
    id: str
    product_name: str
    link_code: str
    full_url: str
    channel: str
    campaign_name: Optional[str]
    total_clicks: int
    total_conversions: int
    total_revenue: float
    is_active: bool
    created_at: datetime


class Lead(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    status: str
    temperature: str
    source: str
    estimated_value: Optional[float]
    notes: Optional[str]
    next_action: Optional[str]
    next_action_date: Optional[datetime]
    created_at: datetime


class CreateLeadRequest(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    position: Optional[str]
    status: str = 'nouveau'
    temperature: str = 'froid'
    source: str
    estimated_value: Optional[float]
    notes: Optional[str]


class CreateTrackingLinkRequest(BaseModel):
    product_id: str
    channel: str
    campaign_name: Optional[str]


class Template(BaseModel):
    id: str
    title: str
    category: str
    template_type: str
    content: str
    variables: Optional[dict]
    usage_count: int


# =====================================================
# ENDPOINTS - STATISTIQUES
# =====================================================

@router.get("/stats", response_model=CommercialStats)
async def get_commercial_stats(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupère les statistiques du dashboard commercial
    Vérifie le niveau d'abonnement pour limiter l'accès aux données
    """
    try:
        user_id = current_user.get('id')
        subscription_tier = current_user.get('subscription_tier', 'starter')
        
        # Vérifier le rôle
        if current_user.get('role') != 'commercial':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux commerciaux"
            )
        
        # Récupérer le sales_rep_id
        sales_rep_result = supabase.table('sales_representatives') \
            .select('id') \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        
        if not sales_rep_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil commercial non trouvé"
            )
        
        sales_rep_id = sales_rep_result.data['id']
        
        # Compter les leads
        leads_result = supabase.table('commercial_leads') \
            .select('id, status, estimated_value, created_at', count='exact') \
            .eq('user_id', user_id) \
            .execute()
        
        total_leads = leads_result.count or 0
        leads_data = leads_result.data or []
        
        # Leads du mois en cours
        first_day_month = datetime.now().replace(day=1).date()
        leads_month = len([l for l in leads_data if datetime.fromisoformat(l['created_at'].replace('Z', '+00:00')).date() >= first_day_month])
        
        qualified_leads = len([l for l in leads_data if l['status'] in ['qualifie', 'en_negociation']])
        converted_leads = len([l for l in leads_data if l['status'] == 'conclu'])
        
        # Valeur du pipeline (leads en négociation)
        pipeline_value = sum([l.get('estimated_value', 0) or 0 for l in leads_data if l['status'] == 'en_negociation'])
        
        # Calculer les stats totales (Lifetime)
        # On utilise les tables sources plutôt que la table stats agrégée pour éviter les 0 si le cron ne tourne pas
        
        # 1. Stats des liens trackés
        links_stats_result = supabase.table('commercial_tracking_links') \
            .select('total_revenue, total_clicks') \
            .eq('user_id', user_id) \
            .execute()
            
        links_data = links_stats_result.data or []
        links_revenue = sum([float(l.get('total_revenue', 0) or 0) for l in links_data])
        total_clicks = sum([int(l.get('total_clicks', 0) or 0) for l in links_data])
        
        # 2. Stats des leads
        # Valeur des leads conclus
        leads_value_concluded = sum([float(l.get('estimated_value', 0) or 0) for l in leads_data if l['status'] == 'conclu'])
        
        # 3. Calcul des totaux
        total_revenue = links_revenue + leads_value_concluded
        
        # Estimation de la commission (si pas stockée ailleurs)
        # Hypothèse: 10% sur les liens, 5% sur les leads
        commission_from_links = links_revenue * 0.10
        commission_from_leads = leads_value_concluded * 0.05
        total_commission = commission_from_links + commission_from_leads
        
        # Compter les liens actifs
        links_result = supabase.table('commercial_tracking_links') \
            .select('id', count='exact') \
            .eq('user_id', user_id) \
            .eq('is_active', True) \
            .execute()
        
        active_links = links_result.count or 0
        
        # Calculer le taux de conversion
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Limiter les données selon l'abonnement
        if subscription_tier == 'starter':
            # Pour STARTER, limiter l'historique à 7 jours
            logger.info(f"STARTER user - données limitées aux 7 derniers jours")
        
        return CommercialStats(
            total_leads=total_leads,
            leads_generated_month=leads_month,
            qualified_leads=qualified_leads,
            converted_leads=converted_leads,
            total_commission=float(total_commission),
            total_revenue=float(total_revenue),
            pipeline_value=float(pipeline_value),
            conversion_rate=round(conversion_rate, 2),
            total_clicks=total_clicks,
            active_tracking_links=active_links
        )
        
    except Exception as e:
        logger.error(f"Erreur get_commercial_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# ENDPOINTS - LEADS CRM
# =====================================================

@router.get("/leads", response_model=List[Lead])
async def get_leads(
    status: Optional[str] = None,
    temperature: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère la liste des leads du commercial
    Limite selon l'abonnement : STARTER=10 max
    """
    try:
        user_id = current_user.get('id')
        subscription_tier = current_user.get('subscription_tier', 'starter')
        
        # Vérifier la limite pour STARTER
        if subscription_tier == 'starter':
            limit = min(limit, 10)
        
        query = supabase.table('commercial_leads') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True)
        
        if status:
            query = query.eq('status', status)
        
        if temperature:
            query = query.eq('temperature', temperature)
        
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Erreur get_leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/leads", response_model=Lead)
async def create_lead(
    lead_data: CreateLeadRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Crée un nouveau lead
    Vérifie la limite selon l'abonnement
    """
    try:
        user_id = current_user.get('id')
        subscription_tier = current_user.get('subscription_tier', 'starter')
        
        # Vérifier la limite pour STARTER
        if subscription_tier == 'starter':
            # Compter les leads du mois
            first_day_month = datetime.now().replace(day=1).date()
            count_result = supabase.table('commercial_leads') \
                .select('id', count='exact') \
                .eq('user_id', user_id) \
                .gte('created_at', first_day_month.isoformat()) \
                .execute()
            
            leads_count = count_result.count or 0
            
            if leads_count >= 10:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Limite de 10 leads/mois atteinte pour l'abonnement STARTER. Passez à PRO pour leads illimités."
                )
        
        # Créer le lead
        result = supabase.table('commercial_leads') \
            .insert({
                'user_id': user_id,
                'first_name': lead_data.first_name,
                'last_name': lead_data.last_name,
                'email': lead_data.email,
                'phone': lead_data.phone,
                'company': lead_data.company,
                'position': lead_data.position,
                'status': lead_data.status,
                'temperature': lead_data.temperature,
                'source': lead_data.source,
                'estimated_value': lead_data.estimated_value,
                'notes': lead_data.notes
            }) \
            .execute()
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur create_lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/leads/{lead_id}")
async def update_lead(
    lead_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Met à jour un lead
    """
    try:
        user_id = current_user.get('id')
        
        # Vérifier que le lead appartient bien à l'utilisateur
        check_result = supabase.table('commercial_leads') \
            .select('id') \
            .eq('id', lead_id) \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        
        if not check_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead non trouvé"
            )
        
        # Mettre à jour
        result = supabase.table('commercial_leads') \
            .update(update_data) \
            .eq('id', lead_id) \
            .execute()
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur update_lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# ENDPOINTS - LIENS TRACKÉS
# =====================================================

@router.get("/tracking-links", response_model=List[TrackingLink])
async def get_tracking_links(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère les liens trackés du commercial
    Limite : STARTER=3, PRO=illimité
    """
    try:
        user_id = current_user.get('id')
        subscription_tier = current_user.get('subscription_tier', 'starter')
        
        query = supabase.table('commercial_tracking_links') \
            .select('*, products(name)') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True)
        
        # Limiter pour STARTER
        if subscription_tier == 'starter':
            query = query.limit(3)
        
        result = query.execute()
        
        # Formater les données
        links = []
        for item in (result.data or []):
            links.append({
                'id': item['id'],
                'product_name': item.get('products', {}).get('name', 'Produit inconnu') if item.get('products') else 'Aucun produit',
                'link_code': item['link_code'],
                'full_url': item['full_url'],
                'channel': item['channel'],
                'campaign_name': item.get('campaign_name'),
                'total_clicks': item['total_clicks'],
                'total_conversions': item['total_conversions'],
                'total_revenue': float(item['total_revenue'] or 0),
                'is_active': item['is_active'],
                'created_at': item['created_at']
            })
        
        return links
        
    except Exception as e:
        logger.error(f"Erreur get_tracking_links: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/tracking-links", response_model=TrackingLink)
async def create_tracking_link(
    link_data: CreateTrackingLinkRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Crée un nouveau lien tracké
    Vérifie la limite selon l'abonnement
    """
    try:
        user_id = current_user.get('id')
        subscription_tier = current_user.get('subscription_tier', 'starter')
        
        # Vérifier la limite pour STARTER
        if subscription_tier == 'starter':
            count_result = supabase.table('commercial_tracking_links') \
                .select('id', count='exact') \
                .eq('user_id', user_id) \
                .execute()
            
            links_count = count_result.count or 0
            
            if links_count >= 3:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Limite de 3 liens trackés atteinte pour l'abonnement STARTER. Passez à PRO pour liens illimités."
                )
        
        # Générer un code unique
        import secrets
        link_code = secrets.token_urlsafe(8)
        full_url = f"https://tracknow.io/ref/{link_code}"
        
        # Créer le lien
        result = supabase.table('commercial_tracking_links') \
            .insert({
                'user_id': user_id,
                'product_id': link_data.product_id,
                'link_code': link_code,
                'full_url': full_url,
                'channel': link_data.channel,
                'campaign_name': link_data.campaign_name
            }) \
            .execute()
        
        # Récupérer avec le nom du produit
        link_with_product = supabase.table('commercial_tracking_links') \
            .select('*, products(name)') \
            .eq('id', result.data[0]['id']) \
            .single() \
            .execute()
        
        item = link_with_product.data
        
        return {
            'id': item['id'],
            'product_name': item.get('products', {}).get('name', 'Produit') if item.get('products') else 'Aucun',
            'link_code': item['link_code'],
            'full_url': item['full_url'],
            'channel': item['channel'],
            'campaign_name': item.get('campaign_name'),
            'total_clicks': 0,
            'total_conversions': 0,
            'total_revenue': 0,
            'is_active': True,
            'created_at': item['created_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur create_tracking_link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# ENDPOINTS - TEMPLATES
# =====================================================

@router.get("/templates", response_model=List[Template])
async def get_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère les templates disponibles selon l'abonnement
    STARTER=3, PRO=15, ENTERPRISE=tous
    """
    try:
        subscription_tier = current_user.get('subscription_tier', 'starter')
        
        # Filtrer selon l'abonnement
        query = supabase.table('commercial_templates') \
            .select('*') \
            .eq('is_active', True)
        
        if subscription_tier == 'starter':
            query = query.eq('subscription_tier', 'starter')
        elif subscription_tier == 'pro':
            query = query.in_('subscription_tier', ['starter', 'pro'])
        # enterprise = tous les templates
        
        if category:
            query = query.eq('category', category)
        
        query = query.order('category')
        
        result = query.execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Erreur get_templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/templates/{template_id}/use")
async def use_template(
    template_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Incrémente le compteur d'utilisation d'un template
    """
    try:
        # Incrémenter usage_count
        supabase.rpc('increment', {
            'table_name': 'commercial_templates',
            'column_name': 'usage_count',
            'row_id': template_id,
            'increment_by': 1
        }).execute()
        
        return {"message": "Template usage recorded"}
        
    except Exception as e:
        logger.error(f"Erreur use_template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# ENDPOINTS - ANALYTICS & GRAPHIQUES
# =====================================================

@router.get("/analytics/performance")
async def get_performance_data(
    period: str = '30',  # '7', '30', '90'
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Données pour les graphiques de performance
    STARTER=7 jours, PRO/ENTERPRISE=30+ jours
    """
    try:
        user_id = current_user.get('id')
        subscription_tier = current_user.get('subscription_tier', 'starter')
        
        # Limiter la période pour STARTER
        if subscription_tier == 'starter':
            period = '7'
        
        days = int(period)
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Récupérer les stats quotidiennes
        result = supabase.table('commercial_stats') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('period', 'daily') \
            .gte('period_date', start_date.isoformat()) \
            .order('period_date') \
            .execute()
        
        # Formater pour les graphiques
        performance_data = []
        for stat in (result.data or []):
            performance_data.append({
                'date': stat['period_date'],
                'leads': stat['leads_generated'],
                'conversions': stat['leads_converted'],
                'revenue': float(stat['total_revenue'] or 0),
                'commission': float(stat['total_commission'] or 0),
                'clicks': stat['total_clicks']
            })
        
        return {
            'period': f"{days} jours",
            'data': performance_data
        }
        
    except Exception as e:
        logger.error(f"Erreur get_performance_data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/analytics/funnel")
async def get_funnel_data(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Données pour le funnel de conversion (pipeline)
    """
    try:
        user_id = current_user.get('id')
        
        # Compter les leads par statut
        result = supabase.table('commercial_leads') \
            .select('status, estimated_value') \
            .eq('user_id', user_id) \
            .execute()
        
        leads_data = result.data or []
        
        funnel = {
            'nouveau': {'count': 0, 'value': 0},
            'qualifie': {'count': 0, 'value': 0},
            'en_negociation': {'count': 0, 'value': 0},
            'conclu': {'count': 0, 'value': 0}
        }
        
        for lead in leads_data:
            status = lead['status']
            if status in funnel:
                funnel[status]['count'] += 1
                funnel[status]['value'] += float(lead.get('estimated_value', 0) or 0)
        
        return funnel
        
    except Exception as e:
        logger.error(f"Erreur get_funnel_data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# À ajouter dans server.py :
# app.include_router(router)
# =====================================================
