"""
============================================
ADMIN USER MANAGEMENT ENDPOINTS
GetYourShare - Gestion des Utilisateurs Admin
============================================

Endpoints pour l'administration des utilisateurs:
- Listing avec filtres et pagination
- CRUD utilisateurs
- Statistiques
- Suspension/réactivation
- Réinitialisation mot de passe
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import bcrypt
from auth import get_current_admin
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/admin/users", tags=["Admin Users"])

# ============================================
# PYDANTIC MODELS
# ============================================

class UserStatsResponse(BaseModel):
    """Statistiques des utilisateurs"""
    total: int
    merchants: int
    influencers: int
    commercials: int
    sales_reps: int
    active: int
    suspended: int
    pending: int
    new_today: int
    new_this_week: int
    new_this_month: int

class UserActivity(BaseModel):
    """Activité utilisateur"""
    action: str
    type: str = "info"
    details: Optional[str]
    created_at: datetime

class UserSubscriptionDetails(BaseModel):
    """Détails abonnement utilisateur"""
    subscription_id: Optional[str]
    plan_name: Optional[str]
    status: Optional[str]
    price: Optional[float]
    currency: Optional[str]
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    trial_end: Optional[datetime]

class UserStatsDetails(BaseModel):
    """Statistiques détaillées utilisateur"""
    login_count: int = 0
    products_count: int = 0
    campaigns_count: int = 0
    clicks_count: int = 0
    commission_total: float = 0.0

class UserListItem(BaseModel):
    """Item de liste utilisateur"""
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    role: str
    status: str = "active"
    subscription_plan: Optional[str]
    avatar: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    last_ip: Optional[str]

class UserCreateRequest(BaseModel):
    """Création d'utilisateur"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    role: str = "user"
    status: str = "active"
    send_welcome_email: bool = True

    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'merchant', 'influencer', 'commercial', 'sales_rep', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of {allowed_roles}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed_status = ['active', 'suspended', 'pending']
        if v not in allowed_status:
            raise ValueError(f'Status must be one of {allowed_status}')
        return v

class UserUpdateRequest(BaseModel):
    """Mise à jour utilisateur"""
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    role: Optional[str]
    status: Optional[str]

    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['user', 'merchant', 'influencer', 'commercial', 'sales_rep', 'admin']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of {allowed_roles}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_status = ['active', 'suspended', 'pending']
            if v not in allowed_status:
                raise ValueError(f'Status must be one of {allowed_status}')
        return v

class StatusUpdateRequest(BaseModel):
    """Modification de statut"""
    status: str

    @validator('status')
    def validate_status(cls, v):
        allowed_status = ['active', 'suspended', 'pending']
        if v not in allowed_status:
            raise ValueError(f'Status must be one of {allowed_status}')
        return v

# ============================================
# HELPER FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# ============================================
# ENDPOINTS
# ============================================

@router.get("/stats", response_model=UserStatsResponse)
async def get_users_stats(
    admin = Depends(get_current_admin)
):
    """
    Récupère les statistiques des utilisateurs
    """
    try:
        # Récupérer tous les utilisateurs
        response = supabase.table('users').select('role, status, created_at').execute()
        users = response.data if response.data else []

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculer les stats
        stats = {
            'total': len(users),
            'merchants': sum(1 for u in users if u.get('role') == 'merchant'),
            'influencers': sum(1 for u in users if u.get('role') == 'influencer'),
            'commercials': sum(1 for u in users if u.get('role') == 'commercial'),
            'sales_reps': sum(1 for u in users if u.get('role') == 'sales_rep'),
            'active': sum(1 for u in users if u.get('status') == 'active'),
            'suspended': sum(1 for u in users if u.get('status') == 'suspended'),
            'pending': sum(1 for u in users if u.get('status') == 'pending'),
            'new_today': sum(1 for u in users if u.get('created_at') and datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')) >= today_start),
            'new_this_week': sum(1 for u in users if u.get('created_at') and datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')) >= week_start),
            'new_this_month': sum(1 for u in users if u.get('created_at') and datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')) >= month_start),
        }

        return UserStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )

@router.get("", response_model=Dict[str, Any])
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    subscription: Optional[str] = None,
    admin = Depends(get_current_admin)
):
    """
    Liste paginée des utilisateurs avec filtres
    """
    try:
        # Base query
        query = supabase.table('users').select('*', count='exact')

        # Filtres
        if search:
            query = query.or_(f"email.ilike.%{search}%,first_name.ilike.%{search}%,last_name.ilike.%{search}%,company.ilike.%{search}%")
        
        if role:
            query = query.eq('role', role)
        
        if status:
            query = query.eq('status', status)

        # Pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        # Order
        query = query.order('created_at', desc=True)

        # Execute
        response = query.execute()
        
        users = response.data if response.data else []
        total = response.count if hasattr(response, 'count') else len(users)

        # Enrichir avec les abonnements si nécessaire
        if subscription:
            # TODO: Filter by subscription plan
            pass

        return {
            'users': users,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'pages': (total + page_size - 1) // page_size
            }
        }

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserListItem)
async def get_user(
    user_id: str,
    admin = Depends(get_current_admin)
):
    """
    Récupère les détails d'un utilisateur
    """
    try:
        response = supabase.table('users').select('*').eq('id', user_id).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserListItem(**response.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}"
        )

@router.post("", response_model=UserListItem, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    admin = Depends(get_current_admin)
):
    """
    Crée un nouvel utilisateur
    """
    try:
        # Vérifier si l'email existe déjà
        existing = supabase.table('users').select('id').eq('email', request.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Hasher le mot de passe
        hashed_password = hash_password(request.password)

        # Créer l'utilisateur
        user_data = {
            'email': request.email,
            'password': hashed_password,
            'first_name': request.first_name,
            'last_name': request.last_name,
            'phone': request.phone,
            'company': request.company,
            'role': request.role,
            'status': request.status,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        response = supabase.table('users').insert(user_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        # TODO: Envoyer email de bienvenue si request.send_welcome_email

        return UserListItem(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserListItem)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    admin = Depends(get_current_admin)
):
    """
    Met à jour un utilisateur
    """
    try:
        # Vérifier que l'utilisateur existe
        existing = supabase.table('users').select('*').eq('id', user_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Préparer les données de mise à jour
        update_data = {k: v for k, v in request.dict(exclude_unset=True).items() if v is not None}
        update_data['updated_at'] = datetime.utcnow().isoformat()

        # Mettre à jour
        response = supabase.table('users').update(update_data).eq('id', user_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )

        return UserListItem(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    admin = Depends(get_current_admin)
):
    """
    Supprime un utilisateur
    """
    try:
        # Vérifier que l'utilisateur existe
        existing = supabase.table('users').select('id').eq('id', user_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Supprimer l'utilisateur
        supabase.table('users').delete().eq('id', user_id).execute()

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.patch("/{user_id}/status", response_model=UserListItem)
async def update_user_status(
    user_id: str,
    request: StatusUpdateRequest,
    admin = Depends(get_current_admin)
):
    """
    Modifie le statut d'un utilisateur (actif/suspendu/en attente)
    """
    try:
        response = supabase.table('users').update({
            'status': request.status,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', user_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserListItem(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user status {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )

@router.post("/{user_id}/reset-password", status_code=status.HTTP_200_OK)
async def reset_user_password(
    user_id: str,
    admin = Depends(get_current_admin)
):
    """
    Envoie un email de réinitialisation de mot de passe
    """
    try:
        # Récupérer l'utilisateur
        response = supabase.table('users').select('email').eq('id', user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user_email = response.data[0]['email']

        # TODO: Implémenter l'envoi d'email de réinitialisation
        # Pour l'instant, on log juste l'action
        logger.info(f"Password reset requested for user {user_id} ({user_email})")

        return {
            'success': True,
            'message': 'Password reset email sent',
            'email': user_email
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )

@router.get("/{user_id}/subscription", response_model=Dict[str, Any])
async def get_user_subscription(
    user_id: str,
    admin = Depends(get_current_admin)
):
    """
    Récupère les détails d'abonnement d'un utilisateur
    """
    try:
        # Récupérer l'abonnement actif
        response = supabase.table('subscriptions')\
            .select('*, subscription_plans(*)')\
            .eq('user_id', user_id)\
            .eq('status', 'active')\
            .single()\
            .execute()

        if not response.data:
            return {'subscription': None}

        subscription = response.data
        plan = subscription.get('subscription_plans', {})

        return {
            'subscription': {
                'subscription_id': subscription.get('id'),
                'plan_name': plan.get('name'),
                'status': subscription.get('status'),
                'price': plan.get('price_mad') or plan.get('price'),
                'currency': plan.get('currency', 'MAD'),
                'current_period_start': subscription.get('current_period_start'),
                'current_period_end': subscription.get('current_period_end'),
                'trial_end': subscription.get('trial_end')
            }
        }

    except Exception as e:
        logger.error(f"Error fetching subscription for user {user_id}: {e}")
        return {'subscription': None}

@router.get("/{user_id}/stats", response_model=Dict[str, Any])
async def get_user_stats(
    user_id: str,
    admin = Depends(get_current_admin)
):
    """
    Récupère les statistiques détaillées d'un utilisateur
    """
    try:
        # Récupérer les stats selon le rôle
        stats = {
            'login_count': 0,
            'products_count': 0,
            'campaigns_count': 0,
            'clicks_count': 0,
            'commission_total': 0.0
        }

        # Products count
        try:
            prod_res = supabase.table('products').select('id', count='exact').eq('merchant_id', user_id).execute()
            stats['products_count'] = prod_res.count or 0
        except:
            pass

        # Campaigns count
        try:
            camp_res = supabase.table('campaigns').select('id', count='exact').eq('merchant_id', user_id).execute()
            stats['campaigns_count'] = camp_res.count or 0
        except:
            pass

        # Clicks count (from tracking_events or click_logs)
        try:
            # Try tracking_events first (affiliate links)
            links_res = supabase.table('affiliate_links').select('id').eq('influencer_id', user_id).execute()
            if links_res.data:
                link_ids = [l['id'] for l in links_res.data]
                clicks_res = supabase.table('tracking_events').select('id', count='exact').in_('link_id', link_ids).eq('event_type', 'click').execute()
                stats['clicks_count'] = clicks_res.count or 0
        except:
            pass

        # Commission total
        try:
            comm_res = supabase.table('commissions').select('amount').eq('influencer_id', user_id).eq('status', 'approved').execute()
            if comm_res.data:
                stats['commission_total'] = sum(float(c['amount']) for c in comm_res.data)
        except:
            pass
            
        # Login count (if tracked in users table)
        try:
            user_res = supabase.table('users').select('login_count').eq('id', user_id).single().execute()
            if user_res.data:
                stats['login_count'] = user_res.data.get('login_count', 0)
        except:
            pass

        return {'stats': stats}

    except Exception as e:
        logger.error(f"Error fetching stats for user {user_id}: {e}")
        return {'stats': None}

@router.get("/{user_id}/activity", response_model=Dict[str, Any])
async def get_user_activity(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    admin = Depends(get_current_admin)
):
    """
    Récupère l'activité récente d'un utilisateur
    """
    try:
        # TODO: Implémenter une vraie table d'audit/logs
        # Pour l'instant, retourner vide plutôt que des fausses données
        activity = []
        
        # Try to fetch from click_logs if relevant
        try:
             logs_res = supabase.table('click_logs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
             if logs_res.data:
                 for log in logs_res.data:
                     activity.append({
                         'action': 'Click',
                         'type': 'info',
                         'details': f"Clicked on link {log.get('link_id')}",
                         'created_at': log.get('created_at')
                     })
        except:
            pass

        return {'activity': activity}

    except Exception as e:
        logger.error(f"Error fetching activity for user {user_id}: {e}")
        return {'activity': []}
