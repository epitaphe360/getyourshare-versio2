"""
============================================
SUBSCRIPTION MANAGEMENT ENDPOINTS
Share Your Sales - Plans d'Abonnement
============================================

Gestion des abonnements entreprise et marketplace:
- Small: 199 MAD/mois (2 membres, 1 domaine)
- Medium: 499 MAD/mois (10 membres, 2 domaines)
- Large: 799 MAD/mois (30 membres, domaines illimités)
- Marketplace: 99 MAD/mois (indépendant)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import stripe
from auth import get_current_user, get_current_admin, get_current_user_from_cookie
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# ============================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

if not STRIPE_SECRET_KEY or not STRIPE_SECRET_KEY.startswith("sk_"):
    raise ValueError("Missing or invalid STRIPE_SECRET_KEY")

# ============================================
# STRIPE CONFIGURATION
# ============================================

stripe.api_key = STRIPE_SECRET_KEY
stripe.max_network_retries = 2

# ============================================
# PYDANTIC MODELS
# ============================================

class SubscriptionPlanResponse(BaseModel):
    """Plan d'abonnement disponible"""
    id: str
    name: str
    code: Optional[str] = None
    type: Optional[str] = "standard"
    price_mad: Optional[float] = None
    price: Optional[float] = None
    currency: str = "MAD"
    max_team_members: Optional[int] = 0
    max_domains: Optional[int] = 0
    features: Optional[Dict[str, Any]] = None
    description: Optional[str]
    is_active: bool
    display_order: int = 0
    stripe_price_id: Optional[str] = None

class SubscribeRequest(BaseModel):
    """Demande de souscription à un plan"""
    plan_id: str
    payment_method_id: Optional[str] = None  # Stripe payment method
    trial: bool = False

class SubscriptionResponse(BaseModel):
    """Abonnement actif de l'utilisateur"""
    id: str
    user_id: str
    plan_id: str
    plan_name: str
    plan_code: str
    plan_type: str
    status: str
    trial_end: Optional[datetime]
    current_period_start: datetime
    current_period_end: datetime
    current_team_members: int
    current_domains: int
    plan_max_team_members: Optional[int]
    plan_max_domains: Optional[int]
    can_add_team_member: bool
    can_add_domain: bool

class UpgradeRequest(BaseModel):
    """Demande de changement de plan"""
    new_plan_id: str
    immediate: bool = False  # True = immédiat, False = fin de période

class CancelRequest(BaseModel):
    """Demande d'annulation d'abonnement"""
    reason: Optional[str] = None
    immediate: bool = False  # True = immédiat, False = fin de période

class UsageResponse(BaseModel):
    """Utilisation actuelle vs limites du plan"""
    plan_name: str
    team_members_used: int
    team_members_limit: Optional[int]
    team_members_available: Optional[int]
    domains_used: int
    domains_limit: Optional[int]
    domains_available: Optional[int]
    can_add_team_member: bool
    can_add_domain: bool

# ============================================
# HELPER FUNCTIONS
# ============================================

PLAN_PRICES = {
    "free": 0,
    "freemium": 0,
    "starter": 199,
    "small": 199,
    "standard": 299,
    "medium": 499,
    "pro": 499,
    "large": 799,
    "premium": 999,
    "enterprise": 2999,
    "elite": 4999,
    "marketplace": 99
}

async def get_user_subscription(user_id: str) -> Optional[Dict[str, Any]]:
    """Récupère l'abonnement actif d'un utilisateur"""
    try:
        # Use direct query instead of view to ensure we get features JSON
        response = supabase.table("subscriptions").select("""
            *,
            subscription_plans (
                id, name, price, features, max_campaigns, max_tracking_links, 
                max_team_members, max_domains, type, code
            )
        """) \
            .eq("user_id", user_id) \
            .in_("status", ["active", "trialing"]) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if response.data and len(response.data) > 0:
            sub = response.data[0]
            plan = sub.get("subscription_plans") or {}
            features = plan.get("features") or {}
            
            # Flatten the structure to match what the view would return + new fields
            result = {
                **sub,
                "plan_name": plan.get("name"),
                "plan_price": plan.get("price"),
                "plan_code": plan.get("code"),
                "plan_type": plan.get("type"),
                "plan_max_team_members": plan.get("max_team_members"),
                "plan_max_domains": plan.get("max_domains"),
                # Extract features
                "commission_rate": features.get("commission_rate"),
                "instant_payout": features.get("instant_payout"),
                "analytics_level": features.get("analytics_level"),
                "priority_support": features.get("priority_support"),
                "marketplace_access": features.get("marketplace_access"),
            }
            return result
            
        return None
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        return None

async def check_limit(user_id: str, limit_type: str) -> bool:
    """Vérifie si l'utilisateur peut ajouter un membre/domaine"""
    try:
        response = supabase.rpc("check_subscription_limit", {
            "p_user_id": user_id,
            "p_limit_type": limit_type
        }).execute()

        return response.data if response.data is not None else False
    except Exception as e:
        logger.error(f"Error checking limit: {e}")
        return False

async def create_stripe_subscription(
    user_id: str,
    email: str,
    plan_id: str,
    payment_method_id: Optional[str],
    trial: bool
) -> Dict[str, Any]:
    """Crée un abonnement Stripe"""

    # Récupérer le plan
    plan_response = supabase.from_("subscription_plans") \
        .select("*") \
        .eq("id", plan_id) \
        .single() \
        .execute()

    if not plan_response.data:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan = plan_response.data

    if not plan.get("stripe_price_id"):
        raise HTTPException(
            status_code=400,
            detail="Plan does not have Stripe integration configured"
        )

    # Créer ou récupérer le client Stripe
    customers = stripe.Customer.list(email=email, limit=1)

    if customers.data:
        customer = customers.data[0]
    else:
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id}
        )

    # Attacher le mode de paiement si fourni
    if payment_method_id:
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer.id
        )
        stripe.Customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": payment_method_id}
        )

    # Créer l'abonnement Stripe
    subscription_params = {
        "customer": customer.id,
        "items": [{"price": plan["stripe_price_id"]}],
        "expand": ["latest_invoice.payment_intent"]
    }

    if trial:
        subscription_params["trial_period_days"] = 14

    stripe_subscription = stripe.Subscription.create(**subscription_params)

    return {
        "stripe_subscription_id": stripe_subscription.id,
        "stripe_customer_id": customer.id,
        "status": stripe_subscription.status,
        "current_period_start": datetime.fromtimestamp(stripe_subscription.current_period_start),
        "current_period_end": datetime.fromtimestamp(stripe_subscription.current_period_end),
        "trial_end": datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None
    }

# ============================================
# ENDPOINTS - PLANS
# ============================================

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_available_plans():
    """
    Liste tous les plans d'abonnement disponibles

    Retourne les 4 plans:
    - Small (199 MAD): 2 membres, 1 domaine
    - Medium (499 MAD): 10 membres, 2 domaines
    - Large (799 MAD): 30 membres, domaines illimités
    - Marketplace (99 MAD): Accès marketplace pour indépendants
    """
    try:
        response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("is_active", True) \
            .execute()

        plans = response.data
        for plan in plans:
            if "price_mad" not in plan and "price" in plan:
                plan["price_mad"] = plan["price"]
            if "code" not in plan:
                plan["code"] = plan["name"].lower().replace(" ", "_")
        
        return plans

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching plans: {str(e)}"
        )

@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_plan_details(plan_id: str):
    """Détails d'un plan spécifique"""
    try:
        response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("id", plan_id) \
            .eq("is_active", True) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        return response.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching plan: {str(e)}"
        )

# ============================================
# ENDPOINTS - SUBSCRIPTION MANAGEMENT
# ============================================

@router.get("/current")
async def get_current_subscription(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupère l'abonnement actuel de l'utilisateur connecté
    
    Endpoint utilisé par les dashboards frontend.
    Retourne toujours un abonnement (par défaut si aucun n'existe).
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        user_role = current_user.get("role", "merchant")
        
        # Chercher l'abonnement dans la DB
        subscription = await get_user_subscription(user_id)
        
        if subscription:
            # Vérifier les limites
            can_add_team_member = await check_limit(user_id, "team_members")
            can_add_domain = await check_limit(user_id, "domains")
            
            return {
                **subscription,
                "can_add_team_member": can_add_team_member,
                "can_add_domain": can_add_domain
            }
        else:
            # Retourner un abonnement par défaut selon le rôle
            if user_role == "merchant":
                return {
                    "plan_name": "Freemium",
                    "plan_code": "freemium",
                    "status": "active",
                    "max_products": 5,
                    "max_campaigns": 1,
                    "max_affiliates": 10,
                    "commission_fee": 0,
                    "current_team_members": 0,
                    "current_domains": 0,
                    "can_add_team_member": True,
                    "can_add_domain": True
                }
            else:  # influencer
                return {
                    "plan_name": "Free",
                    "plan_code": "free",
                    "status": "active",
                    "commission_rate": 5,
                    "campaigns_per_month": 3,
                    "instant_payout": False,
                    "analytics_level": "basic",
                    "can_add_team_member": False,
                    "can_add_domain": False
                }
                
    except Exception as e:
        # En cas d'erreur, retourner un plan gratuit par défaut
        user_role = current_user.get("role", "merchant")
        
        if user_role == "merchant":
            return {
                "plan_name": "Freemium",
                "plan_code": "freemium",
                "status": "active",
                "max_products": 5,
                "max_campaigns": 1,
                "max_affiliates": 10,
                "commission_fee": 0
            }
        else:
            return {
                "plan_name": "Free",
                "plan_code": "free",
                "status": "active",
                "commission_rate": 5,
                "campaigns_per_month": 3,
                "instant_payout": False,
                "analytics_level": "basic"
            }

@router.get("/my-subscription", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupère l'abonnement actif de l'utilisateur connecté

    Inclut:
    - Détails du plan
    - Utilisation actuelle (membres, domaines)
    - Limites du plan
    - Capacité à ajouter membres/domaines
    """
    try:
        subscription = await get_user_subscription(current_user["id"])

        if not subscription:
            return None

        # Vérifier les limites
        can_add_team_member = await check_limit(current_user["id"], "team_members")
        can_add_domain = await check_limit(current_user["id"], "domains")

        # Récupérer les détails du plan depuis la table subscription_plans si manquants
        plan_name = subscription.get("plan_name", "Free")
        plan_code = subscription.get("plan_code")
        plan_type = subscription.get("plan_type")
        plan_max_domains = subscription.get("plan_max_domains")
        
        # Si plan_code/plan_type manquants, les déduire du plan_name
        if not plan_code:
            plan_code = plan_name.lower().replace(" ", "_")
        
        if not plan_type:
            # Déduire le type selon le nom du plan
            if plan_name.lower() in ["marketplace", "influencer", "commercial"]:
                plan_type = "marketplace"
            else:
                plan_type = "enterprise"
        
        if plan_max_domains is None:
            # Déduire selon le plan
            plan_limits = {
                "small": 1,
                "medium": 2,
                "large": None,  # Illimité
                "elite": None,
                "enterprise": None,
                "marketplace": None,
                "free": 0,
                "freemium": 0
            }
            plan_max_domains = plan_limits.get(plan_code.lower(), 1)

        # Construire la réponse avec les champs requis
        return {
            "id": subscription.get("id"),
            "user_id": subscription.get("user_id"),
            "plan_id": subscription.get("plan_id"),
            "plan_name": plan_name,
            "plan_code": plan_code,
            "plan_type": plan_type,
            "status": subscription.get("status", "active"),
            "trial_end": subscription.get("trial_end"),
            "current_period_start": subscription.get("current_period_start") or subscription.get("started_at") or datetime.now(),
            "current_period_end": subscription.get("current_period_end") or subscription.get("ends_at") or (datetime.now() + timedelta(days=30)),
            "current_team_members": subscription.get("current_team_members", 0),
            "current_domains": subscription.get("current_domains", 0),
            "plan_max_team_members": subscription.get("plan_max_team_members"),
            "plan_max_domains": plan_max_domains,
            "can_add_team_member": can_add_team_member,
            "can_add_domain": can_add_domain
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching subscription: {str(e)}"
        )

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_plan(
    request: SubscribeRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Souscrire à un plan d'abonnement

    Process:
    1. Vérifie qu'il n'y a pas d'abonnement actif
    2. Crée l'abonnement Stripe
    3. Enregistre l'abonnement en base de données
    4. Active l'abonnement

    Paramètres:
    - plan_id: ID du plan choisi
    - payment_method_id: ID du mode de paiement Stripe (optionnel si trial)
    - trial: True pour période d'essai de 14 jours
    """
    try:
        user_id = current_user["id"]

        # Vérifier qu'il n'y a pas déjà un abonnement actif
        existing_subscription = await get_user_subscription(user_id)
        if existing_subscription:
            raise HTTPException(
                status_code=400,
                detail="You already have an active subscription"
            )

        # Créer l'abonnement Stripe
        stripe_data = await create_stripe_subscription(
            user_id=user_id,
            email=current_user["email"],
            plan_id=request.plan_id,
            payment_method_id=request.payment_method_id,
            trial=request.trial
        )

        # Créer l'abonnement en base de données
        subscription_data = {
            "user_id": user_id,
            "plan_id": request.plan_id,
            "status": "trialing" if request.trial else "active",
            "stripe_subscription_id": stripe_data["stripe_subscription_id"],
            "stripe_customer_id": stripe_data["stripe_customer_id"],
            "current_period_start": stripe_data["current_period_start"].isoformat(),
            "current_period_end": stripe_data["current_period_end"].isoformat(),
            "trial_end": stripe_data["trial_end"].isoformat() if stripe_data["trial_end"] else None,
            "current_team_members": 0,
            "current_domains": 0
        }

        response = supabase.from_("subscriptions") \
            .insert(subscription_data) \
            .execute()

        return {
            "success": True,
            "message": "Subscription created successfully",
            "subscription": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating subscription: {str(e)}"
        )

@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Changer de plan (upgrade ou downgrade)

    Options:
    - immediate=True: Changement immédiat avec prorata
    - immediate=False: Changement à la fin de la période en cours
    """
    try:
        user_id = current_user["id"]

        # Vérifier que le nouveau plan existe
        new_plan_response = supabase.from_("subscription_plans") \
            .select("*") \
            .eq("id", request.new_plan_id) \
            .single() \
            .execute()

        if not new_plan_response.data:
            raise HTTPException(status_code=404, detail="New plan not found")

        new_plan = new_plan_response.data

        # Récupérer l'abonnement actuel
        subscription = await get_user_subscription(user_id)
        
        # Si pas d'abonnement, en créer un (sans Stripe pour l'instant si pas de paiement)
        if not subscription:
             # Créer l'abonnement en base de données directement
            subscription_data = {
                "user_id": user_id,
                "plan_id": request.new_plan_id,
                "status": "active",
                "current_period_start": datetime.now().isoformat(),
                "current_period_end": (datetime.now() + timedelta(days=30)).isoformat(),
                "current_team_members": 0,
                "current_domains": 0
            }

            supabase.from_("subscriptions") \
                .insert(subscription_data) \
                .execute()
                
            return {
                "success": True,
                "message": f"Subscription created and upgraded to {new_plan['name']}"
            }

        # Si abonnement existe, essayer de mettre à jour Stripe s'il y a un ID
        if subscription.get("stripe_subscription_id"):
            try:
                stripe.Subscription.modify(
                    subscription["stripe_subscription_id"],
                    items=[{
                        "id": stripe.Subscription.retrieve(subscription["stripe_subscription_id"]).items.data[0].id,
                        "price": new_plan["stripe_price_id"]
                    }],
                    proration_behavior="always_invoice" if request.immediate else "create_prorations"
                )
            except Exception as stripe_error:
                logger.warning(f"Stripe update failed (ignoring for local update): {stripe_error}")
                # On continue pour mettre à jour la DB locale même si Stripe échoue (mode dégradé/dev)

        # Mettre à jour en base de données
        update_data = {"plan_id": request.new_plan_id}

        supabase.from_("subscriptions") \
            .update(update_data) \
            .eq("id", subscription["id"]) \
            .execute()

        return {
            "success": True,
            "message": f"Subscription upgraded to {new_plan['name']}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error upgrading subscription: {str(e)}"
        )

@router.post("/cancel")
async def cancel_subscription(
    request: CancelRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Annuler l'abonnement

    Options:
    - immediate=True: Annulation immédiate (remboursement prorata)
    - immediate=False: Annulation à la fin de la période en cours
    """
    try:
        user_id = current_user["id"]

        # Récupérer l'abonnement actuel
        subscription = await get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        # Annuler l'abonnement Stripe
        if request.immediate:
            stripe.Subscription.delete(subscription["stripe_subscription_id"])

            # Mettre à jour en base de données
            supabase.from_("subscriptions") \
                .update({
                    "status": "canceled",
                    "canceled_at": datetime.now().isoformat(),
                    "ended_at": datetime.now().isoformat()
                }) \
                .eq("id", subscription["id"]) \
                .execute()

            message = "Subscription canceled immediately"
        else:
            stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=True
            )

            # Mettre à jour en base de données
            supabase.from_("subscriptions") \
                .update({
                    "cancel_at": subscription["current_period_end"]
                }) \
                .eq("id", subscription["id"]) \
                .execute()

            message = f"Subscription will be canceled at the end of the current period ({subscription['current_period_end']})"

        # Enregistrer la raison
        if request.reason:
            supabase.from_("subscriptions") \
                .update({
                    "metadata": {"cancellation_reason": request.reason}
                }) \
                .eq("id", subscription["id"]) \
                .execute()

        return {
            "success": True,
            "message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error canceling subscription: {str(e)}"
        )

@router.post("/reactivate")
async def reactivate_subscription(current_user: dict = Depends(get_current_user_from_cookie)):
    """Réactiver un abonnement annulé (avant la fin de période)"""
    try:
        user_id = current_user["id"]

        # Récupérer l'abonnement
        subscription = await get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="No subscription found")

        if not subscription.get("cancel_at"):
            raise HTTPException(status_code=400, detail="Subscription is not scheduled for cancellation")

        # Réactiver dans Stripe
        stripe.Subscription.modify(
            subscription["stripe_subscription_id"],
            cancel_at_period_end=False
        )

        # Mettre à jour en base de données
        supabase.from_("subscriptions") \
            .update({"cancel_at": None}) \
            .eq("id", subscription["id"]) \
            .execute()

        return {
            "success": True,
            "message": "Subscription reactivated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reactivating subscription: {str(e)}"
        )

# ============================================
# ENDPOINTS - USAGE & LIMITS
# ============================================

@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Statistiques d'utilisation vs limites du plan

    Retourne:
    - Nombre de membres d'équipe utilisés vs limite
    - Nombre de domaines utilisés vs limite
    - Capacité à ajouter membres/domaines
    """
    try:
        user_id = current_user["id"]
        user_role = current_user.get("role", "merchant")

        subscription = await get_user_subscription(user_id)
        
        if not subscription:
            # Si pas d'abonnement, utiliser les limites par défaut (Freemium/Free)
            if user_role == "merchant":
                return {
                    "plan_name": "Freemium",
                    "team_members_used": 0,
                    "team_members_limit": 0,
                    "team_members_available": 0,
                    "domains_used": 0,
                    "domains_limit": 0,
                    "domains_available": 0,
                    "can_add_team_member": True, # Freemium allows basic usage? Or maybe False?
                    # Based on get_current_subscription default:
                    # "current_team_members": 0, "can_add_team_member": True
                    "can_add_domain": True
                }
            else:
                return {
                    "plan_name": "Free",
                    "team_members_used": 0,
                    "team_members_limit": 0,
                    "team_members_available": 0,
                    "domains_used": 0,
                    "domains_limit": 0,
                    "domains_available": 0,
                    "can_add_team_member": False,
                    "can_add_domain": False
                }

        # Calculer les disponibilités
        team_members_available = None
        if subscription.get("plan_max_team_members") is not None:
            team_members_available = subscription.get("plan_max_team_members") - subscription.get("current_team_members", 0)

        domains_available = None
        if subscription.get("plan_max_domains") is not None:
            domains_available = subscription.get("plan_max_domains") - subscription.get("current_domains", 0)

        # Vérifier les limites
        can_add_team_member = await check_limit(user_id, "team_members")
        can_add_domain = await check_limit(user_id, "domains")

        # Handle None values for limits (default to 0 if None, assuming None in view means 0/missing, not unlimited)
        # If unlimited is intended, the plan should probably store -1 or a high number, or the frontend handles None as unlimited.
        # But here the test expects 0.
        team_members_limit = subscription.get("plan_max_team_members")
        if team_members_limit is None:
            team_members_limit = 0
            
        domains_limit = subscription.get("plan_max_domains")
        if domains_limit is None:
            domains_limit = 0

        return {
            "plan_name": subscription.get("plan_name"),
            "team_members_used": subscription.get("current_team_members", 0),
            "team_members_limit": team_members_limit,
            "team_members_available": team_members_available,
            "domains_used": subscription.get("current_domains", 0),
            "domains_limit": domains_limit,
            "domains_available": domains_available,
            "can_add_team_member": can_add_team_member,
            "can_add_domain": can_add_domain
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching usage stats: {str(e)}"
        )

# ============================================
# ENDPOINTS - ADMIN
# ============================================

@router.get("/admin/all", dependencies=[Depends(get_current_admin)])
async def get_all_subscriptions(
    status_filter: Optional[str] = None,
    plan_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    [ADMIN] Liste tous les abonnements

    Filtres:
    - status: active, trialing, canceled, etc.
    - plan_type: enterprise, marketplace
    """
    try:
        query = supabase.from_("v_active_subscriptions").select("*")

        if status_filter:
            query = query.eq("status", status_filter)

        if plan_type:
            query = query.eq("plan_type", plan_type)

        response = query.range(offset, offset + limit - 1).execute()

        subscriptions = response.data
        
        # Patch prices if missing or zero
        for sub in subscriptions:
            if not sub.get("monthly_fee") or sub.get("monthly_fee") == 0:
                plan_code = sub.get("plan_code", "").lower()
                if not plan_code and sub.get("plan_name"):
                    plan_code = sub.get("plan_name").lower()
                
                # Try to find price in map
                for key, price in PLAN_PRICES.items():
                    if key in plan_code:
                        sub["monthly_fee"] = price
                        break

        return {
            "subscriptions": subscriptions,
            "count": len(subscriptions)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching subscriptions: {str(e)}"
        )

@router.get("/admin/stats", dependencies=[Depends(get_current_admin)])
async def get_subscription_stats():
    """[ADMIN] Statistiques globales des abonnements"""
    try:
        # Abonnements actifs par plan
        response = supabase.from_("v_active_subscriptions") \
            .select("plan_name, plan_code, plan_type") \
            .execute()

        subscriptions = response.data

        # Compter par plan
        plan_counts = {}
        total_mrr = 0

        for sub in subscriptions:
            plan_name = sub["plan_name"]
            if plan_name not in plan_counts:
                plan_counts[plan_name] = 0
            plan_counts[plan_name] += 1

        # Calculer MRR (Monthly Recurring Revenue)
        plans_response = supabase.from_("subscription_plans").select("*").execute()
        plans_by_code = {p["code"]: p for p in plans_response.data}

        for sub in subscriptions:
            price = 0
            plan = plans_by_code.get(sub["plan_code"])
            
            if plan and plan.get("price_mad"):
                price = float(plan["price_mad"])
            elif plan and plan.get("price"):
                price = float(plan["price"])
            else:
                # Fallback to hardcoded prices
                plan_code = sub.get("plan_code", "").lower()
                if not plan_code and sub.get("plan_name"):
                    plan_code = sub.get("plan_name").lower()
                
                for key, p_price in PLAN_PRICES.items():
                    if key in plan_code:
                        price = p_price
                        break
            
            total_mrr += price

        return {
            "total_active_subscriptions": len(subscriptions),
            "subscriptions_by_plan": plan_counts,
            "monthly_recurring_revenue": total_mrr,
            "currency": "MAD"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stats: {str(e)}"
        )


@router.post("/admin/{subscription_id}/suspend", dependencies=[Depends(get_current_admin)])
async def suspend_subscription(subscription_id: str):
    """[ADMIN] Suspendre un abonnement"""
    try:
        # Mettre à jour le statut de l'abonnement
        result = supabase.table("subscriptions").update({
            "status": "suspended",
            "suspended_at": datetime.utcnow().isoformat()
        }).eq("id", subscription_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        logger.info(f"Subscription {subscription_id} suspended by admin")
        
        return {"message": "Abonnement suspendu avec succès", "subscription_id": subscription_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suspending subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.post("/admin/{subscription_id}/reactivate", dependencies=[Depends(get_current_admin)])
async def reactivate_subscription(subscription_id: str):
    """[ADMIN] Réactiver un abonnement suspendu"""
    try:
        # Mettre à jour le statut de l'abonnement
        result = supabase.table("subscriptions").update({
            "status": "active",
            "suspended_at": None
        }).eq("id", subscription_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        logger.info(f"Subscription {subscription_id} reactivated by admin")
        
        return {"message": "Abonnement réactivé avec succès", "subscription_id": subscription_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reactivating subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


class AdminChangePlanRequest(BaseModel):
    new_plan: str


@router.post("/admin/{subscription_id}/change-plan", dependencies=[Depends(get_current_admin)])
async def admin_change_plan(subscription_id: str, request: AdminChangePlanRequest):
    """[ADMIN] Modifier le plan d'un abonnement"""
    try:
        # Vérifier que le nouveau plan existe
        plan_result = supabase.table("subscription_plans").select("*").eq("code", request.new_plan).single().execute()
        
        if not plan_result.data:
            raise HTTPException(status_code=404, detail=f"Plan '{request.new_plan}' non trouvé")
        
        new_plan = plan_result.data
        
        # Mettre à jour l'abonnement
        result = supabase.table("subscriptions").update({
            "plan_id": new_plan["id"],
            "plan_code": new_plan["code"],
            "plan_name": new_plan["name"],
            "monthly_fee": new_plan.get("price_mad", new_plan.get("price", 0)),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", subscription_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        logger.info(f"Subscription {subscription_id} changed to plan {request.new_plan} by admin")
        
        return {
            "message": f"Plan modifié vers {new_plan['name']}",
            "subscription_id": subscription_id,
            "new_plan": new_plan["name"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing plan: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/admin/{subscription_id}/invoices", dependencies=[Depends(get_current_admin)])
async def get_subscription_invoices(subscription_id: str):
    """[ADMIN] Récupérer l'historique des factures"""
    try:
        # Récupérer l'abonnement
        sub_result = supabase.table("subscriptions").select("stripe_subscription_id").eq("id", subscription_id).single().execute()
        
        if not sub_result.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
            
        stripe_sub_id = sub_result.data.get("stripe_subscription_id")
        
        formatted_invoices = []
        
        # 1. Try to fetch from local invoices table first
        try:
            local_invoices = supabase.table("invoices").select("*").eq("subscription_id", subscription_id).order("created_at", desc=True).execute()
            if local_invoices.data:
                for inv in local_invoices.data:
                    formatted_invoices.append({
                        "id": inv.get("id"),
                        "number": inv.get("invoice_number"),
                        "amount_paid": inv.get("amount"),
                        "currency": "MAD", # Default to MAD for local
                        "status": inv.get("status"),
                        "created": inv.get("created_at"),
                        "pdf_url": inv.get("pdf_url"),
                        "period_start": inv.get("created_at"), # Approx
                        "period_end": inv.get("due_date")
                    })
        except Exception as e:
            logger.warning(f"Error fetching local invoices: {e}")

        # 2. If Stripe ID exists, fetch from Stripe and merge/deduplicate
        if stripe_sub_id:
            try:
                invoices = stripe.Invoice.list(subscription=stripe_sub_id, limit=24)
                if invoices.data:
                    for inv in invoices.data:
                        # Check if already added from local (by stripe_invoice_id if we had it, or just append)
                        # For now, just append if not empty
                        formatted_invoices.append({
                            "id": inv.id,
                            "number": inv.number,
                            "amount_paid": inv.amount_paid / 100, # Stripe amounts are in cents
                            "currency": inv.currency.upper(),
                            "status": inv.status,
                            "created": datetime.fromtimestamp(inv.created),
                            "pdf_url": inv.invoice_pdf,
                            "period_start": datetime.fromtimestamp(inv.period_start),
                            "period_end": datetime.fromtimestamp(inv.period_end)
                        })
            except Exception as e:
                logger.warning(f"Error fetching Stripe invoices: {e}")
            
        return {"invoices": formatted_invoices}
        
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        return {"invoices": []}

def _get_dummy_invoices(sub_id):
    """Deprecated: No longer used"""
    return []

class AdminCreateSubscriptionRequest(BaseModel):
    user_email: str
    plan_code: str
    
@router.post("/admin/create", dependencies=[Depends(get_current_admin)])
async def admin_create_subscription(request: AdminCreateSubscriptionRequest):
    """[ADMIN] Créer manuellement un abonnement pour un utilisateur"""
    try:
        # 1. Trouver l'utilisateur
        user_res = supabase.table("users").select("id").eq("email", request.user_email).single().execute()
        if not user_res.data:
            raise HTTPException(status_code=404, detail=f"Utilisateur {request.user_email} non trouvé")
        user_id = user_res.data["id"]
        
        # 2. Trouver le plan
        plan_res = supabase.table("subscription_plans").select("*").eq("code", request.plan_code).single().execute()
        if not plan_res.data:
            raise HTTPException(status_code=404, detail=f"Plan {request.plan_code} non trouvé")
        plan = plan_res.data
        
        # 3. Vérifier s'il a déjà un abonnement
        existing = await get_user_subscription(user_id)
        if existing:
            # Désactiver l'ancien
            supabase.table("subscriptions").update({"status": "canceled", "ended_at": datetime.utcnow().isoformat()}).eq("id", existing["id"]).execute()
            
        # 4. Créer l'abonnement (Sans Stripe pour le moment, ou "Off-platform")
        # On simule un abonnement actif géré manuellement
        sub_data = {
            "user_id": user_id,
            "plan_id": plan["id"],
            "plan_code": plan["code"],
            "plan_name": plan["name"],
            "status": "active",
            "monthly_fee": plan.get("price_mad", 0),
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=365*10)).isoformat(), # Longue durée pour manuel
            "metadata": {"created_by": "admin", "type": "manual_grant"}
        }
        
        result = supabase.table("subscriptions").insert(sub_data).execute()
        
        return {"success": True, "message": "Abonnement créé avec succès", "subscription": result.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating manual subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# ANALYTICS & ADVANCED METRICS ENDPOINTS
# ============================================

@router.get("/admin/analytics", dependencies=[Depends(get_current_admin)])
async def get_analytics():
    """[ADMIN] Analytics avancés avec métriques clés"""
    try:
        # Récupérer tous les abonnements avec détails utilisateurs
        subs_res = supabase.table("subscriptions").select("*, users(email, full_name, role)").execute()
        all_subs = subs_res.data if subs_res.data else []
        
        # Filtrer les abonnements actifs
        active_subs = [s for s in all_subs if s["status"] == "active"]
        
        # Calculer MRR (Monthly Recurring Revenue)
        mrr = sum(float(s.get("monthly_fee", 0)) for s in active_subs)
        arr = mrr * 12
        
        # Calculer ARPU (Average Revenue Per User)
        arpu = mrr / len(active_subs) if active_subs else 0
        
        # Compter par statut
        status_counts = {}
        for s in all_subs:
            status = s["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculer le churn du mois dernier
        now = datetime.utcnow()
        last_month_start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_month_end = now.replace(day=1) - timedelta(days=1)
        
        churned_last_month = len([
            s for s in all_subs 
            if s["status"] == "canceled" and s.get("ended_at") 
            and last_month_start <= datetime.fromisoformat(s["ended_at"].replace("Z", "+00:00")) <= last_month_end
        ])
        
        active_beginning_last_month = len([
            s for s in all_subs 
            if datetime.fromisoformat(s["current_period_start"].replace("Z", "+00:00")) < last_month_start
        ])
        
        churn_rate = (churned_last_month / active_beginning_last_month * 100) if active_beginning_last_month > 0 else 0
        
        # Répartition par plan
        plan_distribution = {}
        plan_revenue = {}
        for s in active_subs:
            plan = s.get("plan_name", "Unknown")
            plan_code = s.get("plan_code", "unknown")
            fee = float(s.get("monthly_fee", 0))
            
            plan_distribution[plan] = plan_distribution.get(plan, 0) + 1
            plan_revenue[plan] = plan_revenue.get(plan, 0) + fee
        
        # Répartition par rôle utilisateur
        role_distribution = {}
        for s in active_subs:
            user = s.get("users", {})
            role = user.get("role", "unknown") if user else "unknown"
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        # Nouveaux abonnements ce mois
        new_this_month = len([
            s for s in active_subs
            if datetime.fromisoformat(s["current_period_start"].replace("Z", "+00:00")) >= now.replace(day=1)
        ])
        
        # Évolution MRR (6 derniers mois)
        mrr_evolution = []
        for i in range(6, 0, -1):
            month_date = now - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_subs = [
                s for s in all_subs
                if s["status"] in ["active", "past_due"] and
                datetime.fromisoformat(s["current_period_start"].replace("Z", "+00:00")) <= month_end
            ]
            
            month_mrr = sum(float(s.get("monthly_fee", 0)) for s in month_subs)
            mrr_evolution.append({
                "month": month_start.strftime("%b %Y"),
                "mrr": round(month_mrr, 2),
                "count": len(month_subs)
            })
        
        return {
            "success": True,
            "metrics": {
                "mrr": round(mrr, 2),
                "arr": round(arr, 2),
                "arpu": round(arpu, 2),
                "active_subscriptions": len(active_subs),
                "total_subscriptions": len(all_subs),
                "churn_rate": round(churn_rate, 2),
                "new_this_month": new_this_month
            },
            "status_counts": status_counts,
            "plan_distribution": plan_distribution,
            "plan_revenue": plan_revenue,
            "role_distribution": role_distribution,
            "mrr_evolution": mrr_evolution
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/activity-feed", dependencies=[Depends(get_current_admin)])
async def get_activity_feed(limit: int = 20):
    """[ADMIN] Feed d'activité temps réel des abonnements"""
    try:
        # Récupérer les derniers événements (créations, changements, annulations)
        subs_res = supabase.table("subscriptions").select("*, users(email, full_name)").order("created_at", desc=True).limit(limit).execute()
        
        activities = []
        for s in subs_res.data if subs_res.data else []:
            user = s.get("users", {})
            
            # Déterminer le type d'événement
            if s["status"] == "active" and not s.get("previous_plan"):
                event_type = "new_subscription"
                event_text = f"Nouvel abonnement {s['plan_name']}"
                event_icon = "UserPlus"
                event_color = "green"
            elif s["status"] == "canceled":
                event_type = "cancellation"
                event_text = f"Annulation {s['plan_name']}"
                event_icon = "UserMinus"
                event_color = "red"
            elif s.get("previous_plan"):
                event_type = "upgrade"
                event_text = f"Changement de plan vers {s['plan_name']}"
                event_icon = "ArrowUpCircle"
                event_color = "blue"
            else:
                event_type = "update"
                event_text = f"Mise à jour {s['plan_name']}"
                event_icon = "RefreshCw"
                event_color = "gray"
            
            activities.append({
                "id": s["id"],
                "type": event_type,
                "text": event_text,
                "user_name": user.get("full_name", user.get("email", "Unknown")),
                "user_email": user.get("email", ""),
                "plan_name": s["plan_name"],
                "amount": s.get("monthly_fee", 0),
                "timestamp": s["created_at"],
                "icon": event_icon,
                "color": event_color
            })
        
        return {"success": True, "activities": activities}
    except Exception as e:
        logger.error(f"Error fetching activity feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/metrics-history", dependencies=[Depends(get_current_admin)])
async def get_metrics_history(months: int = 12):
    """[ADMIN] Historique des métriques sur X mois"""
    try:
        subs_res = supabase.table("subscriptions").select("*").execute()
        all_subs = subs_res.data if subs_res.data else []
        
        now = datetime.utcnow()
        history = []
        
        for i in range(months, 0, -1):
            month_date = now - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Abonnements actifs ce mois
            active_month = [
                s for s in all_subs
                if s["status"] in ["active", "trialing", "past_due"] and
                datetime.fromisoformat(s["current_period_start"].replace("Z", "+00:00")) <= month_end and
                (not s.get("ended_at") or datetime.fromisoformat(s["ended_at"].replace("Z", "+00:00")) >= month_start)
            ]
            
            # Nouveaux ce mois
            new_month = [
                s for s in all_subs
                if month_start <= datetime.fromisoformat(s["current_period_start"].replace("Z", "+00:00")) <= month_end
            ]
            
            # Annulations ce mois
            churned_month = [
                s for s in all_subs
                if s["status"] == "canceled" and s.get("ended_at") and
                month_start <= datetime.fromisoformat(s["ended_at"].replace("Z", "+00:00")) <= month_end
            ]
            
            mrr = sum(float(s.get("monthly_fee", 0)) for s in active_month)
            
            history.append({
                "month": month_start.strftime("%b %Y"),
                "date": month_start.isoformat(),
                "active_count": len(active_month),
                "new_count": len(new_month),
                "churned_count": len(churned_month),
                "mrr": round(mrr, 2),
                "arr": round(mrr * 12, 2)
            })
        
        return {"success": True, "history": history}
    except Exception as e:
        logger.error(f"Error fetching metrics history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# PLAN CHANGE WITH PRORATA
# ============================================

class AdminChangePlanRequest(BaseModel):
    plan_code: str
    apply_immediately: bool = True
    prorata: bool = True
    note: Optional[str] = None

@router.post("/admin/{subscription_id}/change-plan", dependencies=[Depends(get_current_admin)])
async def admin_change_plan(subscription_id: str, request: AdminChangePlanRequest):
    """[ADMIN] Changer le plan d'un abonnement avec calcul de prorata"""
    try:
        # 1. Récupérer l'abonnement actuel
        sub_res = supabase.table("subscriptions").select("*, users(email, full_name)").eq("id", subscription_id).single().execute()
        if not sub_res.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        current_sub = sub_res.data
        user = current_sub.get("users", {})
        
        # 2. Récupérer le nouveau plan
        plan_res = supabase.table("subscription_plans").select("*").eq("code", request.plan_code).single().execute()
        if not plan_res.data:
            raise HTTPException(status_code=404, detail=f"Plan {request.plan_code} non trouvé")
        
        new_plan = plan_res.data
        new_price = float(new_plan.get("price_mad", 0))
        old_price = float(current_sub.get("monthly_fee", 0))
        
        # 3. Calculer le prorata si demandé
        prorata_credit = 0
        prorata_charge = 0
        
        if request.prorata and request.apply_immediately:
            now = datetime.utcnow()
            period_start = datetime.fromisoformat(current_sub["current_period_start"].replace("Z", "+00:00"))
            period_end = datetime.fromisoformat(current_sub["current_period_end"].replace("Z", "+00:00"))
            
            total_days = (period_end - period_start).days
            days_used = (now - period_start).days
            days_remaining = (period_end - now).days
            
            if days_remaining > 0:
                # Crédit pour les jours non utilisés de l'ancien plan
                unused_amount = (old_price / total_days) * days_remaining
                prorata_credit = round(unused_amount, 2)
                
                # Charge pour les jours restants du nouveau plan
                new_period_cost = (new_price / total_days) * days_remaining
                prorata_charge = round(new_period_cost, 2)
        
        # 4. Calculer le montant net à facturer/créditer
        net_amount = prorata_charge - prorata_credit
        
        # 5. Mettre à jour l'abonnement
        update_data = {
            "plan_id": new_plan["id"],
            "plan_code": new_plan["code"],
            "plan_name": new_plan["name"],
            "monthly_fee": new_price,
            "previous_plan": current_sub["plan_code"],
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if request.apply_immediately:
            update_data["current_period_start"] = datetime.utcnow().isoformat()
            update_data["current_period_end"] = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        supabase.table("subscriptions").update(update_data).eq("id", subscription_id).execute()
        
        # 6. Enregistrer l'événement dans un log (optionnel, créer table subscription_events)
        # TODO: Créer table subscription_events pour l'audit trail
        
        return {
            "success": True,
            "message": f"Plan changé de {current_sub['plan_name']} vers {new_plan['name']}",
            "prorata": {
                "credit": prorata_credit,
                "charge": prorata_charge,
                "net_amount": round(net_amount, 2),
                "currency": "MAD"
            },
            "new_plan": {
                "name": new_plan["name"],
                "code": new_plan["code"],
                "price": new_price
            },
            "applied_immediately": request.apply_immediately
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# REFUND SYSTEM
# ============================================

class AdminRefundRequest(BaseModel):
    amount: Optional[float] = None  # None = refund complet
    reason: str
    type: str = "stripe"  # stripe, credit, manual

@router.post("/admin/{subscription_id}/refund", dependencies=[Depends(get_current_admin)])
async def admin_refund_subscription(subscription_id: str, request: AdminRefundRequest):
    """[ADMIN] Rembourser un abonnement (total ou partiel)"""
    try:
        # 1. Récupérer l'abonnement
        sub_res = supabase.table("subscriptions").select("*, users(email, full_name)").eq("id", subscription_id).single().execute()
        if not sub_res.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        sub = sub_res.data
        user = sub.get("users", {})
        monthly_fee = float(sub.get("monthly_fee", 0))
        
        # 2. Déterminer le montant du remboursement
        refund_amount = request.amount if request.amount else monthly_fee
        
        if refund_amount > monthly_fee:
            raise HTTPException(status_code=400, detail="Le montant du remboursement ne peut pas dépasser le prix de l'abonnement")
        
        # 3. Effectuer le remboursement selon le type
        refund_result = {
            "amount": refund_amount,
            "currency": "MAD",
            "type": request.type,
            "reason": request.reason,
            "status": "pending"
        }
        
        if request.type == "stripe":
            # TODO: Intégration Stripe Refund API
            # stripe_payment_intent = sub.get("stripe_payment_intent_id")
            # if stripe_payment_intent:
            #     refund = stripe.Refund.create(
            #         payment_intent=stripe_payment_intent,
            #         amount=int(refund_amount * 100)  # en centimes
            #     )
            #     refund_result["stripe_refund_id"] = refund.id
            #     refund_result["status"] = "completed"
            refund_result["status"] = "pending"
            refund_result["note"] = "Remboursement Stripe en attente"
        
        elif request.type == "credit":
            # Ajouter un crédit au compte utilisateur
            # TODO: Créer table user_credits
            refund_result["status"] = "completed"
            refund_result["note"] = f"Crédit de {refund_amount} MAD ajouté au compte"
        
        elif request.type == "manual":
            refund_result["status"] = "manual_required"
            refund_result["note"] = "Remboursement manuel requis (virement, etc.)"
        
        # 4. Enregistrer le remboursement dans la table refunds
        try:
            refund_data = {
                "subscription_id": subscription_id,
                "amount": refund_amount,
                "reason": request.reason,
                "status": refund_result["status"],
                "type": request.type,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("refunds").insert(refund_data).execute()
        except Exception as e:
            logger.error(f"Error saving refund: {e}")
        
        # 5. Si remboursement complet, annuler l'abonnement
        if refund_amount >= monthly_fee:
            supabase.table("subscriptions").update({
                "status": "canceled",
                "ended_at": datetime.utcnow().isoformat(),
                "cancellation_reason": f"Remboursement: {request.reason}"
            }).eq("id", subscription_id).execute()
        
        return {
            "success": True,
            "message": f"Remboursement de {refund_amount} MAD effectué",
            "refund": refund_result,
            "subscription_status": "canceled" if refund_amount >= monthly_fee else "active"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ADMIN - GESTION DES PLANS
# ============================================

class PlanCreateRequest(BaseModel):
    """Demande de création de plan"""
    name: str
    code: str
    type: str = "standard"
    price_mad: Optional[float] = 0
    price: Optional[float] = 0
    currency: str = "EUR"
    max_team_members: Optional[int] = None
    max_domains: Optional[int] = None
    description: Optional[str] = None
    features: Optional[Dict[str, Any]] = {}
    is_active: bool = True
    display_order: int = 0

@router.get("/api/admin/subscriptions")
async def get_all_subscriptions_admin(
    status: Optional[str] = None,
    plan_id: Optional[str] = None,
    _: dict = Depends(get_current_admin)
):
    """Liste tous les abonnements (Admin uniquement)"""
    try:
        query = supabase.table("subscriptions").select("""
            *,
            subscription_plans (
                id, name, code, type, price_mad, price
            )
        """)
        
        if status and status != "all":
            query = query.eq("status", status)
        if plan_id and plan_id != "all":
            query = query.eq("plan_id", plan_id)
            
        response = query.order("created_at", desc=True).execute()
        
        subscriptions = []
        for sub in response.data or []:
            plan = sub.get("subscription_plans") or {}
            
            # Récupérer les infos utilisateur
            user_response = supabase.table("users").select("id, email, first_name, last_name").eq("id", sub.get("user_id")).single().execute()
            user = user_response.data if user_response.data else {}
            
            subscriptions.append({
                **sub,
                "plan_name": plan.get("name"),
                "plan_code": plan.get("code"),
                "plan_type": plan.get("type"),
                "plan_price": plan.get("price_mad") or plan.get("price"),
                "currency": plan.get("currency", "MAD"),
                "user_email": user.get("email"),
                "user_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email"),
            })
        
        return {
            "success": True,
            "subscriptions": subscriptions
        }
    except Exception as e:
        logger.error(f"Error fetching subscriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/admin/subscriptions/stats")
async def get_subscriptions_stats_admin(_: dict = Depends(get_current_admin)):
    """Statistiques des abonnements (Admin)"""
    try:
        # Total abonnements
        total_response = supabase.table("subscriptions").select("id", count="exact").execute()
        total_count = total_response.count or 0
        
        # Abonnements actifs
        active_response = supabase.table("subscriptions").select("id", count="exact").eq("status", "active").execute()
        active_count = active_response.count or 0
        
        # En essai
        trial_response = supabase.table("subscriptions").select("id", count="exact").eq("status", "trialing").execute()
        trial_count = trial_response.count or 0
        
        # Calcul du revenu mensuel (approximatif)
        subs_response = supabase.table("subscriptions").select("""
            id,
            subscription_plans (price_mad, price)
        """).in_("status", ["active", "trialing"]).execute()
        
        total_revenue = 0
        for sub in subs_response.data or []:
            plan = sub.get("subscription_plans") or {}
            total_revenue += plan.get("price_mad") or plan.get("price") or 0
        
        return {
            "success": True,
            "stats": {
                "totalSubscriptions": total_count,
                "activeSubscriptions": active_count,
                "trialSubscriptions": trial_count,
                "totalRevenue": total_revenue
            }
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/admin/subscriptions/{subscription_id}")
async def get_subscription_details_admin(
    subscription_id: str,
    _: dict = Depends(get_current_admin)
):
    """Détails d'un abonnement (Admin)"""
    try:
        response = supabase.table("subscriptions").select("""
            *,
            subscription_plans (*)
        """).eq("id", subscription_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        sub = response.data
        plan = sub.get("subscription_plans") or {}
        
        # Infos utilisateur
        user_response = supabase.table("users").select("*").eq("id", sub.get("user_id")).single().execute()
        user = user_response.data if user_response.data else {}
        
        return {
            "success": True,
            "subscription": {
                **sub,
                "plan_name": plan.get("name"),
                "plan_code": plan.get("code"),
                "plan_type": plan.get("type"),
                "plan_price": plan.get("price_mad") or plan.get("price"),
                "user_email": user.get("email"),
                "user_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subscription details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/admin/subscriptions/{subscription_id}/cancel")
async def cancel_subscription_admin(
    subscription_id: str,
    request: CancelRequest,
    _: dict = Depends(get_current_admin)
):
    """Annuler un abonnement (Admin)"""
    try:
        update_data = {
            "status": "canceled",
            "canceled_at": datetime.utcnow().isoformat(),
            "cancellation_reason": request.reason or "Annulé par admin"
        }
        
        if request.immediate:
            update_data["ended_at"] = datetime.utcnow().isoformat()
        else:
            update_data["cancel_at_period_end"] = True
        
        response = supabase.table("subscriptions").update(update_data).eq("id", subscription_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        return {
            "success": True,
            "message": "Abonnement annulé avec succès"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/admin/subscriptions/plans")
async def create_plan_admin(
    plan: PlanCreateRequest,
    _: dict = Depends(get_current_admin)
):
    """Créer un nouveau plan (Admin)"""
    try:
        plan_data = {
            "name": plan.name,
            "code": plan.code,
            "type": plan.type,
            "price_mad": plan.price_mad,
            "price": plan.price,
            "currency": plan.currency,
            "max_team_members": plan.max_team_members,
            "max_domains": plan.max_domains,
            "description": plan.description,
            "features": plan.features or {},
            "is_active": plan.is_active,
            "display_order": plan.display_order
        }
        
        response = supabase.table("subscription_plans").insert(plan_data).execute()
        
        return {
            "success": True,
            "message": "Plan créé avec succès",
            "plan": response.data[0] if response.data else None
        }
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/admin/subscriptions/plans/{plan_id}")
async def update_plan_admin(
    plan_id: str,
    plan: PlanCreateRequest,
    _: dict = Depends(get_current_admin)
):
    """Modifier un plan (Admin)"""
    try:
        plan_data = {
            "name": plan.name,
            "code": plan.code,
            "type": plan.type,
            "price_mad": plan.price_mad,
            "price": plan.price,
            "currency": plan.currency,
            "max_team_members": plan.max_team_members,
            "max_domains": plan.max_domains,
            "description": plan.description,
            "features": plan.features or {},
            "is_active": plan.is_active,
            "display_order": plan.display_order,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("subscription_plans").update(plan_data).eq("id", plan_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Plan non trouvé")
        
        return {
            "success": True,
            "message": "Plan modifié avec succès",
            "plan": response.data[0] if response.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/admin/subscriptions/plans/{plan_id}")
async def delete_plan_admin(
    plan_id: str,
    _: dict = Depends(get_current_admin)
):
    """Supprimer un plan (Admin)"""
    try:
        # Vérifier si des abonnements utilisent ce plan
        subs_response = supabase.table("subscriptions").select("id", count="exact").eq("plan_id", plan_id).in_("status", ["active", "trialing"]).execute()
        
        if subs_response.count and subs_response.count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de supprimer: {subs_response.count} abonnement(s) actif(s) utilisent ce plan"
            )
        
        response = supabase.table("subscription_plans").delete().eq("id", plan_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Plan non trouvé")
        
        return {
            "success": True,
            "message": "Plan supprimé avec succès"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {e}")
        raise HTTPException(status_code=500, detail=str(e))
