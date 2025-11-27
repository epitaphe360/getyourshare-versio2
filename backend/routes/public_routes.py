"""
Routes publiques - Endpoints sans authentification
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from db_helpers import get_all_products, get_all_services
from supabase_client import supabase
from datetime import datetime

router = APIRouter(prefix="/api/public", tags=["Public"])


@router.get("/stats")
async def get_public_stats() -> Dict:
    """Statistiques publiques de la plateforme"""
    try:
        # Count users by role
        users_response = supabase.table("users").select("role", count="exact").execute()
        
        # Count influencers
        influencers_response = supabase.table("influencers").select("*", count="exact").execute()
        
        # Count merchants
        merchants_response = supabase.table("merchants").select("*", count="exact").execute()
        
        # Count products
        products_response = supabase.table("products").select("*", count="exact").execute()
        
        # Count campaigns
        campaigns_response = supabase.table("campaigns").select("*", count="exact").execute()
        
        return {
            "total_users": users_response.count if users_response.count else 0,
            "total_influencers": influencers_response.count if influencers_response.count else 0,
            "total_merchants": merchants_response.count if merchants_response.count else 0,
            "total_products": products_response.count if products_response.count else 0,
            "total_campaigns": campaigns_response.count if campaigns_response.count else 0,
            "platform_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "total_users": 0,
            "total_influencers": 0,
            "total_merchants": 0,
            "total_products": 0,
            "total_campaigns": 0,
            "platform_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }


@router.get("/subscription-plans")
async def get_subscription_plans() -> List[Dict]:
    """Liste des plans d'abonnement disponibles"""
    plans = [
        {
            "id": "free",
            "name": "Free",
            "price": 0,
            "currency": "MAD",
            "features": [
                "1 produit",
                "10 liens d'affiliation",
                "Commission 15%",
                "Support email"
            ],
            "limits": {
                "products": 1,
                "links": 10,
                "campaigns": 1
            }
        },
        {
            "id": "starter",
            "name": "Starter",
            "price": 299,
            "currency": "MAD",
            "period": "month",
            "features": [
                "10 produits",
                "100 liens d'affiliation",
                "Commission 12%",
                "Support prioritaire",
                "Analytics basiques"
            ],
            "limits": {
                "products": 10,
                "links": 100,
                "campaigns": 5
            }
        },
        {
            "id": "pro",
            "name": "Pro",
            "price": 799,
            "currency": "MAD",
            "period": "month",
            "popular": True,
            "features": [
                "50 produits",
                "500 liens d'affiliation",
                "Commission 10%",
                "Support 24/7",
                "Analytics avancées",
                "Intégration IA",
                "API access"
            ],
            "limits": {
                "products": 50,
                "links": 500,
                "campaigns": 20
            }
        },
        {
            "id": "enterprise",
            "name": "Enterprise",
            "price": 1999,
            "currency": "MAD",
            "period": "month",
            "features": [
                "Produits illimités",
                "Liens illimités",
                "Commission 8%",
                "Support dédié",
                "Analytics complètes",
                "IA premium",
                "Intégrations personnalisées",
                "White-label"
            ],
            "limits": {
                "products": -1,  # -1 = unlimited
                "links": -1,
                "campaigns": -1
            }
        }
    ]
    return plans


@router.get("/products")
async def get_public_products(
    limit: int = 20,
    offset: int = 0,
    category: str = None
) -> Dict:
    """Liste publique des produits"""
    try:
        query = supabase.table("products").select("*")
        
        if category:
            query = query.eq("category", category)
        
        query = query.eq("is_active", True)
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "products": response.data if response.data else [],
            "total": len(response.data) if response.data else 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {
            "products": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }


@router.get("/campaigns")
async def get_public_campaigns(
    limit: int = 20,
    offset: int = 0,
    category: str = None
) -> Dict:
    """Liste publique des campagnes actives"""
    try:
        query = supabase.table("campaigns").select("*")
        
        if category:
            query = query.eq("category", category)
        
        query = query.eq("status", "active")
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "campaigns": response.data if response.data else [],
            "total": len(response.data) if response.data else 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {
            "campaigns": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }


@router.get("/merchants")
async def get_public_merchants(
    limit: int = 20,
    offset: int = 0
) -> Dict:
    """Liste publique des marchands"""
    try:
        query = supabase.table("merchants").select("*")
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        # Filter sensitive data
        merchants = []
        if response.data:
            for merchant in response.data:
                merchants.append({
                    "id": merchant.get("id"),
                    "company_name": merchant.get("company_name"),
                    "industry": merchant.get("industry"),
                    "category": merchant.get("category"),
                    "description": merchant.get("description"),
                    "logo_url": merchant.get("logo_url"),
                    "subscription_plan": merchant.get("subscription_plan")
                })
        
        return {
            "merchants": merchants,
            "total": len(merchants),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {
            "merchants": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }


@router.get("/influencers")
async def get_public_influencers(
    limit: int = 20,
    offset: int = 0,
    category: str = None
) -> Dict:
    """Liste publique des influenceurs"""
    try:
        query = supabase.table("influencers").select("*")
        
        if category:
            query = query.eq("category", category)
        
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        # Filter sensitive data
        influencers = []
        if response.data:
            for inf in response.data:
                influencers.append({
                    "id": inf.get("id"),
                    "username": inf.get("username"),
                    "full_name": inf.get("full_name"),
                    "bio": inf.get("bio"),
                    "profile_picture_url": inf.get("profile_picture_url"),
                    "category": inf.get("category"),
                    "influencer_type": inf.get("influencer_type"),
                    "audience_size": inf.get("audience_size"),
                    "engagement_rate": inf.get("engagement_rate"),
                    "social_links": inf.get("social_links")
                })
        
        return {
            "influencers": influencers,
            "total": len(influencers),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {
            "influencers": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }
