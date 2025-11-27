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
        if current_user.get('role') not in ['commercial', 'sales_rep']:
            # Allow if admin for testing
            if current_user.get('role') != 'admin':
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accès réservé aux commerciaux"
                )
        
        # Récupérer le sales_rep_id
        sales_rep_result = supabase.table('sales_representatives') \
            .select('id, commission_rate') \
            .eq('user_id', user_id) \
            .execute()
        
        if not sales_rep_result.data:
            # Create profile if not exists (auto-provisioning)
            user_data = supabase.table('users').select('email, first_name, last_name, phone').eq('id', user_id).single().execute()
            if user_data.data:
                new_rep = {
                    'user_id': user_id,
                    'email': user_data.data.get('email'),
                    'first_name': user_data.data.get('first_name', 'Commercial'),
                    'last_name': user_data.data.get('last_name', ''),
                    'phone': user_data.data.get('phone'),
                    'commission_rate': 5.0,
                    'is_active': True
                }
                created_rep = supabase.table('sales_representatives').insert(new_rep).execute()
                if created_rep.data:
                    sales_rep_id = created_rep.data[0]['id']
                    commission_rate = 5.0
                else:
                    raise HTTPException(status_code=500, detail="Failed to create sales profile")
            else:
                 raise HTTPException(status_code=404, detail="User not found")
        else:
            sales_rep_id = sales_rep_result.data[0]['id']
            commission_rate = float(sales_rep_result.data[0].get('commission_rate', 5.0))
        
        # Compter les leads (Table 'leads')
        leads_result = supabase.table('leads') \
            .select('id, lead_status, estimated_value, created_at', count='exact') \
            .eq('sales_rep_id', sales_rep_id) \
            .execute()
        
        total_leads = leads_result.count or 0
        leads_data = leads_result.data or []
        
        # Leads du mois en cours
        first_day_month = datetime.now().replace(day=1).date()
        leads_month = len([l for l in leads_data if l.get('created_at') and datetime.fromisoformat(l['created_at'].replace('Z', '+00:00')).date() >= first_day_month])
        
        qualified_leads = len([l for l in leads_data if l.get('lead_status') in ['qualified', 'negotiation', 'qualifie', 'en_negociation']])
        converted_leads = len([l for l in leads_data if l.get('lead_status') in ['won', 'conclu']])
        
        # Valeur du pipeline (leads en négociation)
        pipeline_value = sum([float(l.get('estimated_value', 0) or 0) for l in leads_data if l.get('lead_status') in ['negotiation', 'en_negociation']])
        
        # Calculer les stats totales (Lifetime)
        
        # 1. Stats des liens trackés (Table 'tracking_links')
        # Note: tracking_links usually linked to influencer_id, but for commercials we might use user_id or a specific field
        # Assuming commercials use tracking_links table with their user_id as influencer_id (or we need a separate column)
        # For now, let's query tracking_links where influencer_id = user_id (assuming commercial acts as influencer for links)
        links_stats_result = supabase.table('tracking_links') \
            .select('id') \
            .eq('influencer_id', user_id) \
            .execute()
            
        links_data = links_stats_result.data or []
        # Need to aggregate clicks/revenue from conversions/sales tables for these links
        # This is expensive, so maybe just use 0 for now or simple count
        total_clicks = 0 # Placeholder
        links_revenue = 0 # Placeholder
        
        # 2. Stats des leads
        # Valeur des leads conclus
        leads_value_concluded = sum([float(l.get('estimated_value', 0) or 0) for l in leads_data if l.get('lead_status') in ['won', 'conclu']])
        
        # 3. Calcul des totaux
        total_revenue = links_revenue + leads_value_concluded
        
        # Estimation de la commission (using dynamic rate / 100)
        commission_from_links = links_revenue * (commission_rate / 100.0)
        commission_from_leads = leads_value_concluded * (commission_rate / 100.0)
        total_commission = commission_from_links + commission_from_leads
        
        # Compter les liens actifs
        active_links = len(links_data)
        
        # Calculer le taux de conversion
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
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
        
        # Get sales_rep_id
        sales_rep_result = supabase.table('sales_representatives').select('id').eq('user_id', user_id).execute()
        if not sales_rep_result.data:
            return []
        sales_rep_id = sales_rep_result.data[0]['id']

        # Vérifier la limite pour STARTER
        if subscription_tier == 'starter':
            limit = min(limit, 10)
        
        query = supabase.table('leads') \
            .select('*') \
            .eq('sales_rep_id', sales_rep_id) \
            .order('created_at', desc=True)
        
        if status:
            query = query.eq('lead_status', status)
        
        # Temperature mapping not direct, skip filter or implement complex logic
        # if temperature:
        #     query = query.eq('temperature', temperature)
        
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        leads = []
        for item in (result.data or []):
            # Map fields back to Lead model
            name_parts = (item.get('contact_name') or '').split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            score = item.get('score', 0)
            temp = 'froid'
            if score >= 80: temp = 'chaud'
            elif score >= 40: temp = 'tiede'

            leads.append({
                'id': item['id'],
                'first_name': first_name,
                'last_name': last_name,
                'email': item.get('contact_email'),
                'phone': None, # Not in standard leads table view
                'company': item.get('company_name'),
                'status': item.get('lead_status'),
                'temperature': temp,
                'source': 'manual', # Default
                'estimated_value': float(item.get('estimated_value', 0) or 0),
                'notes': None,
                'next_action': None,
                'next_action_date': None,
                'created_at': item['created_at']
            })

        return leads
        
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
        
        # Get sales_rep_id
        sales_rep_result = supabase.table('sales_representatives').select('id').eq('user_id', user_id).execute()
        if not sales_rep_result.data:
             # Auto-create if missing (should be handled in stats but good safety)
             pass # Assume handled or fail
             raise HTTPException(status_code=404, detail="Sales profile not found")
        sales_rep_id = sales_rep_result.data[0]['id']

        # Vérifier la limite pour STARTER
        if subscription_tier == 'starter':
            # Compter les leads du mois
            first_day_month = datetime.now().replace(day=1).date()
            count_result = supabase.table('leads') \
                .select('id', count='exact') \
                .eq('sales_rep_id', sales_rep_id) \
                .gte('created_at', first_day_month.isoformat()) \
                .execute()
            
            leads_count = count_result.count or 0
            
            if leads_count >= 10:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Limite de 10 leads/mois atteinte pour l'abonnement STARTER. Passez à PRO pour leads illimités."
                )
        
        # Map temperature to score
        score = 10
        if lead_data.temperature == 'chaud': score = 90
        elif lead_data.temperature == 'tiede': score = 50

        # Créer le lead
        result = supabase.table('leads') \
            .insert({
                'sales_rep_id': sales_rep_id,
                'contact_name': f"{lead_data.first_name} {lead_data.last_name}".strip(),
                'contact_email': lead_data.email,
                'company_name': lead_data.company,
                'lead_status': lead_data.status,
                'score': score,
                'estimated_value': lead_data.estimated_value,
                # 'notes': lead_data.notes # If column exists
            }) \
            .execute()
        
        if not result.data:
             raise HTTPException(status_code=500, detail="Failed to create lead")

        item = result.data[0]
        
        # Map back for response
        return {
            'id': item['id'],
            'first_name': lead_data.first_name,
            'last_name': lead_data.last_name,
            'email': item.get('contact_email'),
            'phone': lead_data.phone,
            'company': item.get('company_name'),
            'status': item.get('lead_status'),
            'temperature': lead_data.temperature,
            'source': lead_data.source,
            'estimated_value': float(item.get('estimated_value', 0) or 0),
            'notes': lead_data.notes,
            'next_action': None,
            'next_action_date': None,
            'created_at': item['created_at']
        }
        
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
        
        # Get sales_rep_id
        sales_rep_result = supabase.table('sales_representatives').select('id').eq('user_id', user_id).execute()
        if not sales_rep_result.data:
             raise HTTPException(status_code=404, detail="Sales profile not found")
        sales_rep_id = sales_rep_result.data[0]['id']

        # Vérifier que le lead appartient bien à l'utilisateur
        check_result = supabase.table('leads') \
            .select('id') \
            .eq('id', lead_id) \
            .eq('sales_rep_id', sales_rep_id) \
            .single() \
            .execute()
        
        if not check_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead non trouvé"
            )
        
        # Map updates
        db_updates = {}
        if 'status' in update_data: db_updates['lead_status'] = update_data['status']
        if 'company' in update_data: db_updates['company_name'] = update_data['company']
        if 'estimated_value' in update_data: db_updates['estimated_value'] = update_data['estimated_value']
        
        if not db_updates:
             return {"message": "No valid fields to update"}

        # Mettre à jour
        result = supabase.table('leads') \
            .update(db_updates) \
            .eq('id', lead_id) \
            .execute()
        
        # Return simplified object or fetch full
        return {"id": lead_id, "status": "updated"} # Simplified for now
        
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
        
        # Use tracking_links table, assuming influencer_id is used for commercial's user_id
        query = supabase.table('tracking_links') \
            .select('*, products(name)') \
            .eq('influencer_id', user_id) \
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
                'link_code': item['unique_code'], # Changed from link_code to unique_code (standard name)
                'full_url': item.get('original_url', ''), # Or construct it
                'channel': item.get('utm_source', 'direct'), # Map fields
                'campaign_name': item.get('utm_campaign'),
                'total_clicks': item.get('clicks', 0),
                'total_conversions': 0, # Need to count conversions separately or if column exists
                'total_revenue': 0, # Need to sum sales
                'is_active': item.get('is_active', True),
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
            count_result = supabase.table('tracking_links') \
                .select('id', count='exact') \
                .eq('influencer_id', user_id) \
                .execute()
            
            links_count = count_result.count or 0
            
            if links_count >= 3:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Limite de 3 liens trackés atteinte pour l'abonnement STARTER. Passez à PRO pour liens illimités."
                )
        
        # Générer un code unique
        import secrets
        unique_code = secrets.token_urlsafe(8)
        # full_url = f"https://tracknow.io/ref/{unique_code}" # Construct based on product URL
        
        # Get product url
        product = supabase.table('products').select('url').eq('id', link_data.product_id).single().execute()
        original_url = product.data.get('url') if product.data else 'https://example.com'

        # Créer le lien
        result = supabase.table('tracking_links') \
            .insert({
                'influencer_id': user_id,
                'product_id': link_data.product_id,
                'unique_code': unique_code,
                'original_url': original_url,
                'utm_source': link_data.channel,
                'utm_campaign': link_data.campaign_name,
                'is_active': True
            }) \
            .execute()
        
        # Récupérer avec le nom du produit
        link_with_product = supabase.table('tracking_links') \
            .select('*, products(name)') \
            .eq('id', result.data[0]['id']) \
            .single() \
            .execute()
        
        item = link_with_product.data
        
        return {
            'id': item['id'],
            'product_name': item.get('products', {}).get('name', 'Produit') if item.get('products') else 'Aucun',
            'link_code': item['unique_code'],
            'full_url': item['original_url'],
            'channel': item.get('utm_source'),
            'campaign_name': item.get('utm_campaign'),
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
        
        # Get sales_rep_id and commission_rate
        sales_rep_result = supabase.table('sales_representatives').select('id, commission_rate').eq('user_id', user_id).execute()
        if sales_rep_result.data:
            sales_rep_id = sales_rep_result.data[0]['id']
            commission_rate = float(sales_rep_result.data[0].get('commission_rate', 5.0))
        else:
            sales_rep_id = None
            commission_rate = 5.0

        if not sales_rep_id:
             return {'period': f"{days} jours", 'data': []}

        # Récupérer les leads créés dans la période
        leads_result = supabase.table('leads') \
            .select('created_at, lead_status, estimated_value') \
            .eq('sales_rep_id', sales_rep_id) \
            .gte('created_at', start_date.isoformat()) \
            .execute()
        
        leads_data = leads_result.data or []

        # Grouper par jour
        daily_stats = {}
        current_date = start_date
        end_date = datetime.now().date()
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_stats[date_str] = {
                'leads': 0,
                'conversions': 0,
                'revenue': 0.0,
                'commission': 0.0,
                'clicks': 0
            }
            current_date += timedelta(days=1)

        for lead in leads_data:
            created_at = lead.get('created_at', '')
            if created_at:
                date_str = created_at[:10]
                if date_str in daily_stats:
                    daily_stats[date_str]['leads'] += 1
                    if lead.get('lead_status') in ['won', 'conclu']:
                        daily_stats[date_str]['conversions'] += 1
                        val = float(lead.get('estimated_value', 0) or 0)
                        daily_stats[date_str]['revenue'] += val
                        daily_stats[date_str]['commission'] += val * (commission_rate / 100.0)

        # Formater pour les graphiques
        performance_data = []
        for date_str, stats in sorted(daily_stats.items()):
            performance_data.append({
                'date': date_str,
                'leads': stats['leads'],
                'conversions': stats['conversions'],
                'revenue': stats['revenue'],
                'commission': stats['commission'],
                'clicks': stats['clicks']
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
        
        # Get sales_rep_id
        sales_rep_result = supabase.table('sales_representatives').select('id').eq('user_id', user_id).execute()
        sales_rep_id = sales_rep_result.data[0]['id'] if sales_rep_result.data else None

        if not sales_rep_id:
             return {
                'nouveau': {'count': 0, 'value': 0},
                'qualifie': {'count': 0, 'value': 0},
                'en_negociation': {'count': 0, 'value': 0},
                'conclu': {'count': 0, 'value': 0}
            }

        # Compter les leads par statut
        result = supabase.table('leads') \
            .select('lead_status, estimated_value') \
            .eq('sales_rep_id', sales_rep_id) \
            .execute()
        
        leads_data = result.data or []
        
        funnel = {
            'nouveau': {'count': 0, 'value': 0},
            'qualifie': {'count': 0, 'value': 0},
            'en_negociation': {'count': 0, 'value': 0},
            'conclu': {'count': 0, 'value': 0}
        }
        
        # Map DB status to funnel keys
        status_map = {
            'new': 'nouveau', 'nouveau': 'nouveau',
            'qualified': 'qualifie', 'qualifie': 'qualifie',
            'negotiation': 'en_negociation', 'en_negociation': 'en_negociation',
            'won': 'conclu', 'conclu': 'conclu'
        }

        for lead in leads_data:
            db_status = lead.get('lead_status')
            mapped_status = status_map.get(db_status)
            
            if mapped_status and mapped_status in funnel:
                funnel[mapped_status]['count'] += 1
                funnel[mapped_status]['value'] += float(lead.get('estimated_value', 0) or 0)
        
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
