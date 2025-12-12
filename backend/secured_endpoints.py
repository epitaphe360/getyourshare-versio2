"""
SECURED ENDPOINTS - Contrôle d'accès par rôle
Garantit que chaque utilisateur n'accède qu'à ses propres données
"""
from fastapi import APIRouter, Depends, HTTPException
from supabase_config import get_supabase_client
from auth import get_current_user_from_cookie
from db_helpers import get_user_by_id

router = APIRouter()

# ============================================
# MERCHANT ENDPOINTS - Données du marchand connecté uniquement
# ============================================

@router.get("/merchant/me")
async def get_my_merchant_data(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupère UNIQUEMENT les données du marchand connecté
    ✅ Sécurisé : Un marchand ne voit QUE ses propres données
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") != "merchant":
        raise HTTPException(status_code=403, detail="Accès réservé aux marchands")
    
    try:
        supabase = get_supabase_client()
        merchant_id = user["id"]
        
        # Récupérer les campagnes DU marchand
        campaigns = supabase.table('campaigns')\
            .select('*')\
            .eq('merchant_id', merchant_id)\
            .execute()
        
        # Récupérer les produits DU marchand
        products = supabase.table('products')\
            .select('*')\
            .eq('merchant_id', merchant_id)\
            .execute()
        
        # Récupérer les influenceurs qui promeuvent SES produits
        partnerships = supabase.table('affiliate_links')\
            .select('*, influencer:profiles!influencer_id(*)')\
            .eq('merchant_id', merchant_id)\
            .execute()
        
        # Récupérer SES transactions
        transactions = supabase.table('transactions')\
            .select('*')\
            .eq('merchant_id', merchant_id)\
            .order('created_at', desc=True)\
            .limit(50)\
            .execute()
        
        # Statistiques du marchand
        sales = supabase.table('sales')\
            .select('amount')\
            .eq('merchant_id', merchant_id)\
            .execute()
        
        total_revenue = sum([float(s.get('amount', 0)) for s in (sales.data or [])])
        
        return {
            "success": True,
            "profile": user,
            "campaigns": campaigns.data or [],
            "products": products.data or [],
            "influencers": partnerships.data or [],
            "transactions": transactions.data or [],
            "stats": {
                "total_revenue": round(total_revenue, 2),
                "total_campaigns": len(campaigns.data or []),
                "total_products": len(products.data or []),
                "total_influencers": len(partnerships.data or [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/merchant/influencers")
async def get_my_influencers(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Liste des influenceurs qui promeuvent les produits DU marchand connecté
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") != "merchant":
        raise HTTPException(status_code=403, detail="Accès réservé aux marchands")
    
    try:
        supabase = get_supabase_client()
        
        partnerships = supabase.table('affiliate_links')\
            .select('*, influencer:profiles!influencer_id(id, full_name, username, email, avatar_url)')\
            .eq('merchant_id', user["id"])\
            .execute()
        
        return {
            "success": True,
            "influencers": partnerships.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============================================
# INFLUENCER ENDPOINTS - Données de l'influenceur connecté uniquement
# ============================================

@router.get("/influencer/me")
async def get_my_influencer_data(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupère UNIQUEMENT les données de l'influenceur connecté
    ✅ Sécurisé : Un influenceur ne voit QUE ses propres données
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") != "influencer":
        raise HTTPException(status_code=403, detail="Accès réservé aux influenceurs")
    
    try:
        supabase = get_supabase_client()
        influencer_id = user["id"]
        
        # Récupérer SES liens d'affiliation
        links = supabase.table('affiliate_links')\
            .select('*')\
            .eq('influencer_id', influencer_id)\
            .execute()
        
        # Récupérer SES commissions
        commissions = supabase.table('commissions')\
            .select('*')\
            .eq('influencer_id', influencer_id)\
            .execute()
        
        # Récupérer SES conversions
        conversions = supabase.table('conversions')\
            .select('*')\
            .eq('influencer_id', influencer_id)\
            .execute()
        
        # Statistiques de l'influenceur
        total_earnings = sum([float(c.get('amount', 0)) for c in (commissions.data or [])])
        total_clicks = sum([int(l.get('clicks', 0)) for l in (links.data or [])])
        total_conversions = len(conversions.data or [])
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        return {
            "success": True,
            "profile": user,
            "links": links.data or [],
            "commissions": commissions.data or [],
            "conversions": conversions.data or [],
            "stats": {
                "total_earnings": round(total_earnings, 2),
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "conversion_rate": round(conversion_rate, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/influencer/available-merchants")
async def get_available_merchants(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Liste des annonceurs dont l'influenceur PEUT promouvoir les produits
    ✅ Affiche tous les marchands actifs (marketplace)
    ❌ NE montre PAS les données financières des autres marchands
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") != "influencer":
        raise HTTPException(status_code=403, detail="Accès réservé aux influenceurs")
    
    try:
        supabase = get_supabase_client()
        
        # Récupérer UNIQUEMENT les informations publiques des marchands
        merchants = supabase.table('profiles')\
            .select('id, company_name, email, avatar_url, created_at')\
            .eq('role', 'merchant')\
            .eq('is_active', True)\
            .execute()
        
        # Pour chaque marchand, compter ses produits et services actifs (info publique)
        for merchant in (merchants.data or []):
            products = supabase.table('products')\
                .select('id', count='exact', head=True)\
                .eq('merchant_id', merchant['id'])\
                .eq('is_active', True)\
                .execute()
            services = supabase.table('services')\
                .select('id', count='exact', head=True)\
                .eq('merchant_id', merchant['id'])\
                .eq('statut', 'actif')\
                .execute()
            merchant['products_count'] = (products.count or 0) + (services.count or 0)
        
        return {
            "success": True,
            "merchants": merchants.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============================================
# COMMERCIAL ENDPOINTS - Données des clients assignés au commercial
# ============================================

@router.get("/commercial/me")
async def get_my_commercial_data(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupère les données du commercial connecté
    ✅ Sécurisé : Un commercial ne voit QUE ses clients assignés
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") not in ["commercial", "sales_rep"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux commerciaux")
    
    try:
        supabase = get_supabase_client()
        commercial_id = user["id"]
        
        # Récupérer SES leads assignés
        leads = supabase.table('leads')\
            .select('*')\
            .eq('assigned_commercial_id', commercial_id)\
            .execute()
        
        # Récupérer SES clients (marchands assignés)
        clients = supabase.table('profiles')\
            .select('*')\
            .eq('role', 'merchant')\
            .eq('assigned_commercial_id', commercial_id)\
            .execute()
        
        # Statistiques du commercial
        total_leads = len(leads.data or [])
        converted_leads = len([l for l in (leads.data or []) if l.get('status') == 'converted'])
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        return {
            "success": True,
            "profile": user,
            "leads": leads.data or [],
            "clients": clients.data or [],
            "stats": {
                "total_leads": total_leads,
                "converted_leads": converted_leads,
                "conversion_rate": round(conversion_rate, 2),
                "total_clients": len(clients.data or [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/commercial/clients")
async def get_my_clients(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Liste des clients (marchands) assignés au commercial connecté
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") not in ["commercial", "sales_rep"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux commerciaux")
    
    try:
        supabase = get_supabase_client()
        
        clients = supabase.table('profiles')\
            .select('*')\
            .eq('role', 'merchant')\
            .eq('assigned_commercial_id', user["id"])\
            .execute()
        
        return {
            "success": True,
            "clients": clients.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============================================
# ADMIN ENDPOINTS - Accès complet (déjà sécurisé dans analytics_endpoints.py)
# ============================================

@router.get("/admin/all-merchants")
async def get_all_merchants_admin(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Liste COMPLÈTE de tous les marchands (ADMIN UNIQUEMENT)
    ✅ Sécurisé : Réservé aux admins
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    try:
        supabase = get_supabase_client()
        
        merchants = supabase.table('profiles')\
            .select('*')\
            .eq('role', 'merchant')\
            .order('created_at', desc=True)\
            .execute()
        
        return {
            "success": True,
            "merchants": merchants.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/admin/all-influencers")
async def get_all_influencers_admin(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Liste COMPLÈTE de tous les influenceurs (ADMIN UNIQUEMENT)
    ✅ Sécurisé : Réservé aux admins
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    try:
        supabase = get_supabase_client()
        
        influencers = supabase.table('profiles')\
            .select('*')\
            .eq('role', 'influencer')\
            .order('created_at', desc=True)\
            .execute()
        
        return {
            "success": True,
            "influencers": influencers.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/admin/all-commercials")
async def get_all_commercials_admin(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Liste COMPLÈTE de tous les commerciaux (ADMIN UNIQUEMENT)
    ✅ Sécurisé : Réservé aux admins
    """
    user = get_user_by_id(current_user["id"])
    if not user or user.get("role") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    try:
        supabase = get_supabase_client()
        
        commercials = supabase.table('profiles')\
            .select('*')\
            .eq('role', 'commercial')\
            .order('created_at', desc=True)\
            .execute()
        
        return {
            "success": True,
            "commercials": commercials.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
