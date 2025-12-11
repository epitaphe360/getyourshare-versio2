"""
ENDPOINTS BACKEND POUR DASHBOARD COMMERCIAL
============================================
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
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

class ActivityCreate(BaseModel):
    type: str  # call, email, meeting, note, update
    subject: str
    description: Optional[str] = None

class ActivityResponse(BaseModel):
    id: str
    lead_id: str
    type: str
    subject: str
    description: Optional[str]
    created_at: str
    user_id: str
    user_name: Optional[str]

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
            try:
            user_data = supabase.table('users').select('email, first_name, last_name, phone').eq('id', user_id).single().execute()
            except Exception:
                pass  # .single() might return no results
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
        
        # Compter les leads (Table 'services_leads')
        leads_result = supabase.table('services_leads') \
            .select('id, status, estimated_value, created_at', count='exact') \
            .eq('commercial_id', user_id) \
            .execute()
        
        total_leads = leads_result.count or 0
        leads_data = leads_result.data or []
        
        # Leads du mois en cours
        first_day_month = datetime.now().replace(day=1).date()
        leads_month = len([l for l in leads_data if l.get('created_at') and datetime.fromisoformat(l['created_at'].replace('Z', '+00:00')).date() >= first_day_month])
        
        qualified_leads = len([l for l in leads_data if l.get('status') in ['qualifié', 'proposition', 'négociation']])
        converted_leads = len([l for l in leads_data if l.get('status') == 'conclu'])
        
        # Valeur du pipeline (leads en négociation)
        pipeline_value = sum([float(l.get('estimated_value', 0) or 0) for l in leads_data if l.get('status') in ['proposition', 'négociation']])
        
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
        leads_value_concluded = sum([float(l.get('estimated_value', 0) or 0) for l in leads_data if l.get('status') == 'conclu'])
        
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
        
        query = supabase.table('services_leads') \
            .select('*') \
            .eq('commercial_id', user_id) \
            .order('created_at', desc=True)
        
        if status:
            query = query.eq('status', status)
        
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
            
            temp = item.get('temperature', 'froid')

            leads.append({
                'id': item['id'],
                'first_name': first_name,
                'last_name': last_name,
                'email': item.get('contact_email'),
                'phone': item.get('contact_phone'),
                'company': item.get('company_name'),
                'status': item.get('status'),
                'temperature': temp,
                'source': item.get('source', 'manual'),
                'estimated_value': float(item.get('estimated_value', 0) or 0),
                'notes': item.get('notes'),
                'next_action': item.get('next_action'),
                'next_action_date': item.get('next_action_date'),
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
             # Auto-create if missing
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
                else:
                    raise HTTPException(status_code=500, detail="Failed to create sales profile")
             else:
                 raise HTTPException(status_code=404, detail="User not found")
        else:
            sales_rep_id = sales_rep_result.data[0]['id']

        # Vérifier la limite pour STARTER
        if subscription_tier == 'starter':
            # Compter les leads du mois
            first_day_month = datetime.now().replace(day=1).date()
            count_result = supabase.table('services_leads') \
                .select('id', count='exact') \
                .eq('commercial_id', user_id) \
                .gte('created_at', first_day_month.isoformat()) \
                .execute()
            
            leads_count = count_result.count or 0
            
            if leads_count >= 10:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Limite de 10 leads/mois atteinte pour l'abonnement STARTER. Passez à PRO pour leads illimités."
                )
        
        # Créer le lead dans services_leads
        lead_insert_data = {
            'commercial_id': user_id,
            'contact_name': f"{lead_data.first_name} {lead_data.last_name}".strip(),
            'contact_email': lead_data.email,
            'contact_phone': lead_data.phone,
            'company_name': lead_data.company,
            'status': lead_data.status,
            'temperature': lead_data.temperature,
            'source': lead_data.source,
            'estimated_value': lead_data.estimated_value,
            'notes': lead_data.notes,
            'next_action': lead_data.next_action,
            'next_action_date': lead_data.next_action_date
        }
        
        result = supabase.table('services_leads') \
            .insert(lead_insert_data) \
            .execute()
        
        if not result.data:
             raise HTTPException(status_code=500, detail="Failed to create lead")

        item = result.data[0]
        
        # Map back for response
        name_parts = (item.get('contact_name') or '').split(' ', 1)
        return {
            'id': item['id'],
            'first_name': name_parts[0],
            'last_name': name_parts[1] if len(name_parts) > 1 else '',
            'email': item.get('contact_email'),
            'phone': item.get('contact_phone'),
            'company': item.get('company_name'),
            'status': item.get('status'),
            'temperature': item.get('temperature'),
            'source': item.get('source'),
            'estimated_value': float(item.get('estimated_value', 0) or 0),
            'notes': item.get('notes'),
            'next_action': item.get('next_action'),
            'next_action_date': item.get('next_action_date'),
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
             # Auto-create if missing
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
                else:
                    raise HTTPException(status_code=500, detail="Failed to create sales profile")
             else:
                 raise HTTPException(status_code=404, detail="User not found")
        else:
            sales_rep_id = sales_rep_result.data[0]['id']

        # Vérifier que le lead appartient bien à l'utilisateur
        check_result = supabase.table('services_leads') \
            .select('id') \
            .eq('id', lead_id) \
            .eq('commercial_id', user_id) \
            try:
            .single() \
            except Exception:
                pass  # .single() might return no results
            .execute()
        
        if not check_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead non trouvé"
            )
        
        # Map updates directement (services_leads utilise les bons noms de colonnes)
        db_updates = {}
        if 'status' in update_data: db_updates['status'] = update_data['status']
        if 'company' in update_data: db_updates['company_name'] = update_data['company']
        if 'estimated_value' in update_data: db_updates['estimated_value'] = update_data['estimated_value']
        if 'temperature' in update_data: db_updates['temperature'] = update_data['temperature']
        if 'notes' in update_data: db_updates['notes'] = update_data['notes']
        if 'next_action' in update_data: db_updates['next_action'] = update_data['next_action']
        if 'next_action_date' in update_data: db_updates['next_action_date'] = update_data['next_action_date']
        
        if not db_updates:
             return {"message": "No valid fields to update"}

        # Mettre à jour
        result = supabase.table('services_leads') \
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
        try:
        product = supabase.table('products').select('url').eq('id', link_data.product_id).single().execute()
        except Exception:
            pass  # .single() might return no results
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
            try:
            .single() \
            except Exception:
                pass  # .single() might return no results
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
        leads_result = supabase.table('services_leads') \
            .select('created_at, status, estimated_value') \
            .eq('commercial_id', user_id) \
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
                    if lead.get('status') == 'conclu':
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

        # Compter les leads par statut depuis services_leads
        result = supabase.table('services_leads') \
            .select('status, estimated_value') \
            .eq('commercial_id', user_id) \
            .execute()
        
        leads_data = result.data or []
        
        funnel = {
            'nouveau': {'count': 0, 'value': 0},
            'contacté': {'count': 0, 'value': 0},
            'qualifié': {'count': 0, 'value': 0},
            'proposition': {'count': 0, 'value': 0},
            'négociation': {'count': 0, 'value': 0},
            'conclu': {'count': 0, 'value': 0}
        }

        for lead in leads_data:
            db_status = lead.get('status')
            
            if db_status and db_status in funnel:
                funnel[db_status]['count'] += 1
                funnel[db_status]['value'] += float(lead.get('estimated_value', 0) or 0)
        
        return funnel
        
    except Exception as e:
        logger.error(f"Erreur get_funnel_data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# NOUVEAUX ENDPOINTS CRITIQUES
# =====================================================

@router.get("/pipeline")
async def get_pipeline(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Pipeline de vente avec statistiques par étape
    """
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer tous les leads avec leur statut
        response = supabase.table("services_leads")\
            .select("*")\
            .eq("commercial_id", user_id)\
            .execute()
        
        leads = response.data if response.data else []
        
        # Calculer le pipeline par étape
        pipeline = {
            "new": 0,
            "new_amount": 0,
            "contacted": 0,
            "contacted_amount": 0,
            "qualified": 0,
            "qualified_amount": 0,
            "proposal": 0,
            "proposal_amount": 0,
            "negotiation": 0,
            "negotiation_amount": 0,
            "won": 0,
            "won_amount": 0,
            "conversion_rate": 0
        }
        
        total_leads = len(leads)
        won_leads = 0
        
        for lead in leads:
            lead_status = lead.get("status", "nouveau").lower()
            value = float(lead.get("estimated_value", 0) or 0)

            if lead_status in ["nouveau", "new"]:
                pipeline["new"] += 1
                pipeline["new_amount"] += value
            elif lead_status in ["contacté", "contacted"]:
                pipeline["contacted"] += 1
                pipeline["contacted_amount"] += value
            elif lead_status in ["qualifié", "qualified"]:
                pipeline["qualified"] += 1
                pipeline["qualified_amount"] += value
            elif lead_status in ["proposition", "proposal"]:
                pipeline["proposal"] += 1
                pipeline["proposal_amount"] += value
            elif lead_status in ["négociation", "negotiation"]:
                pipeline["negotiation"] += 1
                pipeline["negotiation_amount"] += value
            elif lead_status in ["gagné", "won", "conclu"]:
                pipeline["won"] += 1
                pipeline["won_amount"] += value
                won_leads += 1
        
        # Calculer le taux de conversion
        if total_leads > 0:
            pipeline["conversion_rate"] = round((won_leads / total_leads) * 100, 1)
        
        return pipeline
        
    except Exception as e:
        logger.error(f"Erreur get_pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/quota")
async def get_quota(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Suivi de l'objectif mensuel du commercial
    """
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer l'objectif personnalisé depuis sales_representatives
        sales_rep_result = supabase.table("sales_representatives")\
            .select("target_monthly_revenue, target_monthly_deals")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        # Objectif personnalisé ou par défaut
        if sales_rep_result.data and sales_rep_result.data.get('target_monthly_revenue'):
            target = float(sales_rep_result.data.get('target_monthly_revenue', 10000))
            target_deals = sales_rep_result.data.get('target_monthly_deals', 15)
        else:
            # Fallback basé sur subscription si pas de profil sales_rep
            try:
            user_response = supabase.table("users").select("subscription_tier").eq("id", user_id).single().execute()
            except Exception:
                pass  # .single() might return no results
            subscription_tier = user_response.data.get("subscription_tier", "starter") if user_response.data else "starter"
            target_mapping = {"starter": 5000, "pro": 10000, "enterprise": 25000}
            target = target_mapping.get(subscription_tier, 10000)
            target_deals = 15
        
        # Calculer les revenus du mois en cours
        today = datetime.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        response = supabase.table("services_leads")\
            .select("*")\
            .eq("commercial_id", user_id)\
            .eq("status", "conclu")\
            .gte("created_at", first_day.isoformat())\
            .execute()
        
        leads = response.data if response.data else []
        
        current_revenue = sum(float(lead.get("estimated_value", 0) or 0) for lead in leads)
        current_deals = len(leads)
        progress = (current_revenue / target * 100) if target > 0 else 0
        deals_progress = (current_deals / target_deals * 100) if target_deals > 0 else 0
        remaining = max(0, target - current_revenue)
        
        # Calculer les jours restants
        last_day = datetime(today.year, today.month + 1 if today.month < 12 else 1, 1) - timedelta(days=1)
        days_remaining = (last_day - today).days + 1
        
        # Vérifier si on est sur la bonne voie
        days_in_month = last_day.day
        expected_progress = (today.day / days_in_month) * 100
        on_track = progress >= expected_progress
        
        # Rythme nécessaire
        daily_rate_needed = remaining / days_remaining if days_remaining > 0 else 0
        
        return {
            "current": round(current_revenue, 2),
            "target": target,
            "progress": round(progress, 1),
            "remaining": round(remaining, 2),
            "days_remaining": days_remaining,
            "on_track": on_track,
            "current_deals": current_deals,
            "target_deals": target_deals,
            "deals_progress": round(deals_progress, 1),
            "daily_rate_needed": round(daily_rate_needed, 2)
        }
        
    except Exception as e:
        logger.error(f"Erreur get_quota: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/tasks")
async def get_tasks(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupérer les tâches et rappels du commercial
    """
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer les leads avec actions en attente
        response = supabase.table("services_leads")\
            .select("*")\
            .eq("commercial_id", user_id)\
            .in_("status", ["nouveau", "contacté", "qualifié"])\
            .order("created_at", desc=False)\
            .limit(10)\
            .execute()
        
        leads = response.data if response.data else []
        
        tasks = []
        today = datetime.now()
        
        for lead in leads:
            created_at = datetime.fromisoformat(lead.get("created_at", "").replace("Z", "+00:00"))
            days_ago = (today - created_at).days
            
            # Générer des tâches basées sur le statut et l'ancienneté
            if lead.get("status") == "nouveau" and days_ago == 0:
                tasks.append({
                    "id": f"task_{lead['id']}_1",
                    "title": f"Appeler {lead.get('company_name', 'prospect')}",
                    "description": f"Premier contact pour {lead.get('service_type', 'service')}",
                    "type": "call",
                    "priority": "high",
                    "due_date": "Aujourd'hui",
                    "lead_id": lead["id"]
                })
            elif lead.get("status") == "contacté" and days_ago >= 3:
                tasks.append({
                    "id": f"task_{lead['id']}_2",
                    "title": f"Relancer {lead.get('company_name', 'prospect')}",
                    "description": "Suivi après premier contact",
                    "type": "email",
                    "priority": "medium",
                    "due_date": "Cette semaine",
                    "lead_id": lead["id"]
                })
            elif lead.get("status") == "qualifié" and days_ago >= 7:
                tasks.append({
                    "id": f"task_{lead['id']}_3",
                    "title": f"Envoyer proposition à {lead.get('company_name', 'prospect')}",
                    "description": "Lead qualifié prêt pour proposition",
                    "type": "meeting",
                    "priority": "high",
                    "due_date": "Urgent",
                    "lead_id": lead["id"]
                })
        
        return {"tasks": tasks}
        
    except Exception as e:
        logger.error(f"Erreur get_tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Marquer une tâche comme complétée
    """
    try:
        # Pour l'instant, on retourne juste un succès
        # Dans une vraie implémentation, on sauvegarderait dans une table tasks
        return {"status": "completed", "task_id": task_id}
        
    except Exception as e:
        logger.error(f"Erreur complete_task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/hot-lead")
async def get_hot_lead(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupérer le lead le plus prometteur de la semaine
    """
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer les leads récents avec forte valeur
        response = supabase.table("services_leads")\
            .select("*")\
            .eq("commercial_id", user_id)\
            .in_("status", ["qualifié", "proposition", "négociation"])\
            .order("estimated_value", desc=True)\
            .limit(1)\
            .execute()
        
        leads = response.data if response.data else []
        
        if not leads:
            return {"lead": None}
        
        lead = leads[0]
        created_at = datetime.fromisoformat(lead.get("created_at", "").replace("Z", "+00:00"))
        days_ago = (datetime.now() - created_at).days
        
        return {
            "lead": {
                "id": lead["id"],
                "company": lead.get("company_name", "Prospect"),
                "contact_name": lead.get("contact_name", "Non renseigné"),
                "contact_email": lead.get("contact_email", ""),
                "estimated_value": lead.get("estimated_value", 0),
                "last_contact": f"Il y a {days_ago} jour{'s' if days_ago > 1 else ''}"
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur get_hot_lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/leaderboard")
async def get_leaderboard(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Classement des meilleurs commerciaux du mois
    """
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer tous les commerciaux
        users_response = supabase.table("users")\
            .select("id, first_name, last_name")\
            .eq("role", "commercial")\
            .execute()
        
        users = users_response.data if users_response.data else []
        
        # Calculer les revenus de chaque commercial ce mois
        today = datetime.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        rankings = []
        for user in users:
            commercial_id = user["id"]
            
            # Récupérer les leads conclus du mois
            leads_response = supabase.table("services_leads")\
                .select("*")\
                .eq("commercial_id", commercial_id)\
                .eq("status", "conclu")\
                .gte("created_at", first_day.isoformat())\
                .execute()
            
            leads = leads_response.data if leads_response.data else []
            revenue = sum(float(lead.get("estimated_value", 0) or 0) for lead in leads)
            
            # Récupérer toutes les activités du mois pour ce commercial
            activities_response = supabase.table("lead_activities")\
                .select("type")\
                .eq("user_id", commercial_id)\
                .gte("created_at", first_day.isoformat())\
                .execute()
            
            activities = activities_response.data if activities_response.data else []
            nb_calls = len([a for a in activities if a.get("type") == "call"])
            nb_meetings = len([a for a in activities if a.get("type") == "meeting"])
            nb_emails = len([a for a in activities if a.get("type") == "email"])
            
            # Calculer taux de conversion
            total_leads_response = supabase.table("services_leads")\
                .select("id", count="exact")\
                .eq("commercial_id", commercial_id)\
                .gte("created_at", first_day.isoformat())\
                .execute()
            total_leads = total_leads_response.count or 0
            conversion_rate = (len(leads) / total_leads * 100) if total_leads > 0 else 0
            
            rankings.append({
                "id": commercial_id,
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')[:1]}.",
                "revenue": revenue,
                "leads_count": len(leads),
                "nb_calls": nb_calls,
                "nb_meetings": nb_meetings,
                "nb_emails": nb_emails,
                "conversion_rate": round(conversion_rate, 1),
                "is_current_user": commercial_id == user_id,
                "position_change": 0
            })
        
        # Trier par revenu
        rankings.sort(key=lambda x: x["revenue"], reverse=True)
        
        return {"rankings": rankings}
        
    except Exception as e:
        logger.error(f"Erreur get_leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# ENDPOINTS - GESTION COMPLÈTE DES ACTIVITÉS
# =====================================================

@router.get("/leads/{lead_id}/activities")
async def get_lead_activities(
    lead_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupérer toutes les activités d'un lead
    """
    try:
        # Vérifier que le lead appartient bien au commercial
        lead_response = supabase.table("services_leads")\
            .select("*")\
            .eq("id", lead_id)\
            .eq("commercial_id", current_user.get("user_id"))\
            .execute()
        
        if not lead_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead introuvable"
            )
        
        # Récupérer les activités
        activities_response = supabase.table("lead_activities")\
            .select("*, users(first_name, last_name)")\
            .eq("lead_id", lead_id)\
            .order("created_at", desc=True)\
            .execute()
        
        activities = activities_response.data if activities_response.data else []
        
        # Formatter les activités
        formatted_activities = []
        for activity in activities:
            user_data = activity.get("users", {})
            formatted_activities.append({
                "id": activity["id"],
                "lead_id": activity["lead_id"],
                "type": activity["type"],
                "subject": activity["subject"],
                "description": activity.get("description"),
                "created_at": activity["created_at"],
                "user_id": activity["user_id"],
                "user_name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}" if user_data else "Utilisateur"
            })
        
        return {"activities": formatted_activities}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_lead_activities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/leads/{lead_id}/activities")
async def create_lead_activity(
    lead_id: str,
    activity: ActivityCreate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une nouvelle activité pour un lead
    """
    try:
        # Vérifier que le lead appartient bien au commercial
        lead_response = supabase.table("services_leads")\
            .select("*")\
            .eq("id", lead_id)\
            .eq("commercial_id", current_user.get("user_id"))\
            .execute()
        
        if not lead_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead introuvable"
            )
        
        # Créer l'activité
        activity_data = {
            "lead_id": lead_id,
            "user_id": current_user.get("user_id"),
            "type": activity.type,
            "subject": activity.subject,
            "description": activity.description,
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("lead_activities")\
            .insert(activity_data)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la création de l'activité"
            )
        
        return {
            "message": "Activité créée avec succès",
            "activity": response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur create_lead_activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/leads/{lead_id}")
async def get_lead_detail(
    lead_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupérer les détails complets d'un lead
    """
    try:
        response = supabase.table("services_leads")\
            .select("*")\
            .eq("id", lead_id)\
            .eq("commercial_id", current_user.get("user_id"))\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead introuvable"
            )
        
        lead = response.data[0]
        
        return {
            "id": lead["id"],
            "company_name": lead["company_name"],
            "contact_name": lead["contact_name"],
            "contact_email": lead["contact_email"],
            "contact_phone": lead.get("contact_phone"),
            "service_type": lead.get("service_type"),
            "estimated_value": float(lead.get("estimated_value", 0) or 0),
            "status": lead["status"],
            "temperature": lead.get("temperature", "froid"),
            "source": lead.get("source", "website"),
            "notes": lead.get("notes"),
            "created_at": lead["created_at"],
            "updated_at": lead.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_lead_detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# NOUVEAUX ENDPOINTS TRACKING (SYSTEME COMPLET)
# =====================================================

@router.post("/tracking/generate-link")
async def generate_tracking_link(
    request: Request,
    lead_id: Optional[str] = None,
    campaign: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Génère un lien affilié pour le commercial connecté"""
    user = current_user
    
    if user.get('role') != 'commercial' and user.get('role') != 'admin':
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

@router.get("/tracking/links")
async def get_tracking_links_v2(
    request: Request,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Liste les liens affiliés du commercial (Version Tracking System)"""
    user = current_user
    
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
            "total": len(result.data) if result.data else 0,
            "stats": stats_result.data[0] if stats_result.data else {}
        }
    }

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
    try:
        supabase.rpc(
            'track_commercial_click',
            {
                'p_tracking_code': tracking_code,
                'p_ip_address': ip_address,
                'p_user_agent': user_agent
            }
        ).execute()
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        # Continue execution to redirect even if tracking fails
    
    # Récupérer URL de redirection
    link = supabase.table('commercial_tracking_links')\
        .select('tracking_url')\
        .eq('unique_code', tracking_code)\
        .execute()
    
    if not link.data:
        return RedirectResponse(url="https://getyourshare.ma/pricing")
    
    return RedirectResponse(url=link.data[0]['tracking_url'])

@router.get("/tracking/stats")
async def get_tracking_stats(
    request: Request,
    period: str = '30d',
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Statistiques globales de tracking"""
    user = current_user
    
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
    
    return {
        "success": True,
        "data": {
            **(stats.data[0] if stats.data else {}),
            "top_performing_links": top_links.data if top_links.data else []
        }
    }

@router.post("/promo-codes")
async def create_promo_code(
    request: Request,
    code: str,
    discount_type: str,
    discount_value: float,
    valid_until: Optional[str] = None,
    max_usage: int = 100,
    applicable_plans: List[str] = ["starter", "pro", "enterprise"],
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Créer un code promo personnalisé"""
    user = current_user
    
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
async def list_promo_codes(
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Liste les codes promo du commercial"""
    user = current_user
    
    result = supabase.table('promo_codes')\
        .select('*')\
        .eq('commercial_id', user['id'])\
        .order('created_at', desc=True)\
        .execute()
    
    return {
        "success": True,
        "data": result.data
    }

@router.get("/commissions")
async def get_commissions(
    request: Request,
    status: str = 'all',
    period: str = '30d',
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Liste des commissions du commercial"""
    user = current_user
    
    query = supabase.table('subscription_attributions')\
        .select('*, users!user_id(email, first_name, last_name)')\
        .eq('commercial_id', user['id'])
    
    if status != 'all':
        query = query.eq('status', status)
    
    result = query.order('created_at', desc=True).execute()
    
    data = result.data if result.data else []
    
    # Calculer summary
    summary = {
        'total_pending': sum(float(c.get('commission_amount', 0) or 0) for c in data if c.get('status') == 'pending'),
        'total_approved': sum(float(c.get('commission_amount', 0) or 0) for c in data if c.get('status') == 'approved'),
        'total_paid': sum(float(c.get('commission_amount', 0) or 0) for c in data if c.get('status') == 'paid'),
        'count_pending': len([c for c in data if c.get('status') == 'pending']),
        'count_approved': len([c for c in data if c.get('status') == 'approved']),
        'count_paid': len([c for c in data if c.get('status') == 'paid'])
    }
    
    return {
        "success": True,
        "data": {
            "commissions": data,
            "summary": summary
        }
    }
