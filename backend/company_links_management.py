"""
============================================
COMPANY LINKS MANAGEMENT
Share Your Sales - Génération de Liens par Entreprises
============================================

WORKFLOW CONFORME AUX SPÉCIFICATIONS:
1. SEULES les entreprises peuvent générer des liens d'affiliation
2. Les entreprises attribuent ensuite ces liens à leurs membres d'équipe
3. Les commerciaux/influenceurs REÇOIVENT des liens (ne les génèrent PAS)

Cette approche garantit:
- Contrôle total des entreprises sur leurs liens
- Attribution claire des liens aux membres
- Suivi précis des performances par membre
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
import os
import secrets
from auth import get_current_user
import asyncio
from fastapi.concurrency import run_in_threadpool

router = APIRouter(prefix="/api/company/links", tags=["Company Links Management"])

# ============================================
# ENVIRONMENT VARIABLES VALIDATION
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing required Supabase environment variables")

# ============================================
# SUPABASE CLIENT
# ============================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# PYDANTIC MODELS
# ============================================

class GenerateCompanyLinkRequest(BaseModel):
    """Génération d'un lien par l'entreprise"""
    product_id: str
    custom_slug: Optional[str] = Field(None, max_length=50)
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None

class AssignLinkToMemberRequest(BaseModel):
    """Attribution d'un lien à un membre d'équipe"""
    link_id: str
    member_id: str  # ID du membre d'équipe
    custom_commission_rate: Optional[float] = Field(None, ge=0, le=100)

class BulkGenerateLinksRequest(BaseModel):
    """Génération en masse de liens pour plusieurs produits"""
    product_ids: List[str] = Field(..., min_items=1, max_items=50)
    commission_rate: Optional[float] = Field(None, ge=0, le=100)

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_unique_short_code() -> str:
    """Générer un code court unique"""
    while True:
        short_code = secrets.token_urlsafe(6)[:8]
        existing = supabase.from_("tracking_links") \
            .select("id") \
            .eq("unique_code", short_code) \
            .execute()

        if not existing.data:
            return short_code

async def verify_company_owns_product(company_id: str, product_id: str) -> bool:
    """Vérifier que le produit appartient à l'entreprise"""
    try:
        # Vérifier via la table products
        product = supabase.from_("products") \
            .select("merchant_id") \
            .eq("id", product_id) \
            .single() \
            .execute()

        if not product.data:
            return False

        return product.data["merchant_id"] == company_id
    except Exception:
        return False

async def verify_member_in_team(company_id: str, member_id: str) -> bool:
    """Vérifier que le membre fait partie de l'équipe de l'entreprise"""
    try:
        member = supabase.from_("team_members") \
            .select("id") \
            .eq("company_id", company_id) \
            .eq("member_id", member_id) \
            .eq("status", "active") \
            .execute()

        return len(member.data) > 0 if member.data else False
    except Exception:
        return False

# ============================================
# ENDPOINTS - LINK GENERATION (Company Only)
# ============================================

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_company_affiliate_link(
    request: GenerateCompanyLinkRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    [ENTREPRISE UNIQUEMENT] Générer un lien d'affiliation pour un produit
    """
    try:
        # Vérifier que c'est une entreprise
        if current_user.get("role") != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only companies can generate affiliate links"
            )

        company_id = current_user["id"]

        # Vérifier que le produit appartient à l'entreprise
        owns_product = await verify_company_owns_product(company_id, request.product_id)
        if not owns_product:
            raise HTTPException(
                status_code=403,
                detail="You can only generate links for your own products"
            )

        # Vérifier si un lien existe déjà pour ce produit
        existing = supabase.from_("tracking_links") \
            .select("*") \
            .eq("merchant_id", company_id) \
            .eq("product_id", request.product_id) \
            .eq("is_active", True) \
            .is_("influencer_id", "null") \
            .execute()

        if existing.data and len(existing.data) > 0:
            # Lien de base existe déjà
            link = existing.data[0]
            return {
                "success": True,
                "message": "Company link already exists for this product",
                "link": {
                    **link,
                    "short_code": link['unique_code'],
                    "full_url": link['full_url'],
                    "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={link['full_url']}"
                }
            }

        # Générer le code court
        if request.custom_slug:
            # Vérifier disponibilité
            slug_check = supabase.from_("tracking_links") \
                .select("id") \
                .eq("unique_code", request.custom_slug) \
                .execute()

            if slug_check.data:
                raise HTTPException(
                    status_code=400,
                    detail="Custom slug already in use"
                )

            short_code = request.custom_slug
        else:
            short_code = generate_unique_short_code()

        # Obtenir le taux de commission du produit
        product = supabase.from_("products") \
            .select("commission_rate") \
            .eq("id", request.product_id) \
                .single() \
            .execute()

        commission_rate = request.commission_rate or product.data.get("commission_rate", 15.0)

        # Créer le lien de base (pas encore attribué à un membre)
        full_url = f"https://shareyoursales.ma/r/{short_code}"
        link_data = {
            "merchant_id": company_id,
            "product_id": request.product_id,
            "unique_code": short_code,
            "full_url": full_url,
            "short_url": full_url,
            "is_active": True,
            "metadata": {
                "notes": request.notes,
                "commission_rate": commission_rate
            }
        }

        result = supabase.from_("tracking_links") \
            .insert(link_data) \
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create affiliate link"
            )

        link = result.data[0]

        return {
            "success": True,
            "message": "Affiliate link generated successfully",
            "link": {
                **link,
                "short_code": short_code,
                "full_url": full_url,
                "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={full_url}"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating link: {str(e)}"
        )

@router.post("/bulk-generate", status_code=status.HTTP_201_CREATED)
async def bulk_generate_links(
    request: BulkGenerateLinksRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    [ENTREPRISE] Générer des liens pour plusieurs produits en masse
    """
    try:
        if current_user.get("role") != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only companies can generate affiliate links"
            )

        company_id = current_user["id"]
        generated_links = []
        errors = []

        for product_id in request.product_ids:
            try:
                # Vérifier la propriété
                owns = await verify_company_owns_product(company_id, product_id)
                if not owns:
                    errors.append({"product_id": product_id, "error": "Not your product"})
                    continue

                # Vérifier si existe déjà
                existing = supabase.from_("tracking_links") \
                    .select("*") \
                    .eq("merchant_id", company_id) \
                    .eq("product_id", product_id) \
                    .eq("is_active", True) \
                    .is_("influencer_id", "null") \
                    .execute()

                if existing.data:
                    generated_links.append(existing.data[0])
                    continue

                # Créer nouveau lien
                short_code = generate_unique_short_code()
                full_url = f"https://shareyoursales.ma/r/{short_code}"

                link_data = {
                    "merchant_id": company_id,
                    "product_id": product_id,
                    "unique_code": short_code,
                    "full_url": full_url,
                    "short_url": full_url,
                    "is_active": True,
                    "metadata": {
                        "commission_rate": request.commission_rate or 15.0
                    }
                }

                result = supabase.from_("tracking_links") \
                    .insert(link_data) \
                    .execute()

                if result.data:
                    generated_links.append(result.data[0])

            except Exception as e:
                errors.append({"product_id": product_id, "error": str(e)})

        return {
            "success": True,
            "generated": len(generated_links),
            "links": generated_links,
            "errors": errors if errors else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error bulk generating links: {str(e)}"
        )

# ============================================
# ENDPOINTS - LINK ASSIGNMENT
# ============================================

@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_link_to_team_member(
    request: AssignLinkToMemberRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    [ENTREPRISE] Attribuer un lien d'affiliation à un membre d'équipe
    """
    try:
        if current_user.get("role") != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only companies can assign links"
            )

        company_id = current_user["id"]

        # Vérifier que le lien appartient à l'entreprise
        link = supabase.from_("tracking_links") \
            .select("*") \
            .eq("id", request.link_id) \
            .eq("merchant_id", company_id) \
                .single() \
            .execute()

        if not link.data:
            raise HTTPException(
                status_code=404,
                detail="Link not found or not yours"
            )

        # Vérifier que le membre fait partie de l'équipe
        is_member = await verify_member_in_team(company_id, request.member_id)
        if not is_member:
            raise HTTPException(
                status_code=403,
                detail="Member is not part of your team"
            )

        # Créer un nouveau lien pour ce membre (clone du lien de base)
        short_code = generate_unique_short_code()
        full_url = f"https://shareyoursales.ma/r/{short_code}"
        
        # Get commission rate from metadata or default
        base_commission = link.data.get("metadata", {}).get("commission_rate", 15.0)

        member_link_data = {
            "merchant_id": company_id,
            "influencer_id": request.member_id,
            "product_id": link.data["product_id"],
            "unique_code": short_code,
            "full_url": full_url,
            "short_url": full_url,
            "is_active": True,
            "metadata": {
                "assigned_by": company_id,
                "parent_link_id": request.link_id,
                "assigned_at": datetime.now().isoformat(),
                "commission_rate": request.custom_commission_rate or base_commission
            }
        }

        result = supabase.from_("tracking_links") \
            .insert(member_link_data) \
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to assign link"
            )

        assigned_link = result.data[0]

        return {
            "success": True,
            "message": f"Link assigned to team member successfully",
            "assigned_link": {
                **assigned_link,
                "short_code": short_code,
                "full_url": full_url,
                "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={full_url}"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error assigning link: {str(e)}"
        )

@router.post("/assign-bulk", status_code=status.HTTP_201_CREATED)
async def bulk_assign_links(
    link_id: str,
    member_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """[ENTREPRISE] Attribuer un lien à plusieurs membres en masse"""
    try:
        if current_user.get("role") != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only companies can assign links"
            )

        company_id = current_user["id"]

        # Vérifier que le lien existe
        link = supabase.from_("tracking_links") \
            .select("*") \
            .eq("id", link_id) \
            .eq("merchant_id", company_id) \
                .single() \
            .execute()

        if not link.data:
            raise HTTPException(status_code=404, detail="Link not found")

        assigned = []
        errors = []
        
        base_commission = link.data.get("metadata", {}).get("commission_rate", 15.0)

        for member_id in member_ids:
            try:
                is_member = await verify_member_in_team(company_id, member_id)
                if not is_member:
                    errors.append({"member_id": member_id, "error": "Not in team"})
                    continue

                short_code = generate_unique_short_code()
                full_url = f"https://shareyoursales.ma/r/{short_code}"

                member_link_data = {
                    "merchant_id": company_id,
                    "influencer_id": member_id,
                    "product_id": link.data["product_id"],
                    "unique_code": short_code,
                    "full_url": full_url,
                    "short_url": full_url,
                    "is_active": True,
                    "metadata": {
                        "assigned_by": company_id,
                        "parent_link_id": link_id,
                        "assigned_at": datetime.now().isoformat(),
                        "commission_rate": base_commission
                    }
                }

                result = supabase.from_("tracking_links") \
                    .insert(member_link_data) \
                    .execute()

                if result.data:
                    assigned.append(result.data[0])

            except Exception as e:
                errors.append({"member_id": member_id, "error": str(e)})

        return {
            "success": True,
            "assigned": len(assigned),
            "links": assigned,
            "errors": errors if errors else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error bulk assigning: {str(e)}"
        )

# ============================================
# ENDPOINTS - COMPANY LINK MANAGEMENT
# ============================================

@router.get("/my-company-links")
async def get_company_links(
    product_id: Optional[str] = None,
    assigned_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """[ENTREPRISE] Liste tous les liens générés par l'entreprise"""
    try:
        company_id = current_user["id"]

        query = supabase.from_("tracking_links") \
            .select("*") \
            .eq("merchant_id", company_id)

        if product_id:
            query = query.eq("product_id", product_id)

        if assigned_only:
            query = query.not_.is_("influencer_id", "null")

        response = await run_in_threadpool(lambda: query.order("created_at", desc=True).execute())
        links = response.data or []

        # Manually fetch related data to avoid PGRST200 errors
        product_ids = list(set(l['product_id'] for l in links if l.get('product_id')))
        member_ids = list(set(l['influencer_id'] for l in links if l.get('influencer_id')))

        async def fetch_products():
            if not product_ids: return {}
            p_res = await run_in_threadpool(lambda: supabase.from_("products").select("id, name, price").in_("id", product_ids).execute())
            return {p['id']: p for p in p_res.data} if p_res.data else {}

        async def fetch_members():
            if not member_ids: return {}
            m_res = await run_in_threadpool(lambda: supabase.from_("users").select("id, first_name, last_name, email").in_("id", member_ids).execute())
            return {m['id']: m for m in m_res.data} if m_res.data else {}

        products_map, members_map = await asyncio.gather(fetch_products(), fetch_members())

        # Enrich links
        enriched_links = []
        for link in links:
            link_data = link.copy()
            link_data['product'] = products_map.get(link['product_id'])
            link_data['member'] = members_map.get(link['influencer_id'])
            link_data['short_code'] = link['unique_code'] # Map for frontend
            
            # Ensure URLs are present
            if not link_data.get("full_url"):
                link_data["full_url"] = f"https://shareyoursales.ma/r/{link['unique_code']}"
            
            link_data["qr_code_url"] = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={link_data['full_url']}"
            
            enriched_links.append(link_data)

        return {
            "success": True,
            "links": enriched_links,
            "total": len(enriched_links)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching links: {str(e)}"
        )

@router.delete("/{link_id}")
async def deactivate_link(
    link_id: str,
    current_user: dict = Depends(get_current_user)
):
    """[ENTREPRISE] Désactiver un lien d'affiliation"""
    try:
        company_id = current_user["id"]

        # Désactiver le lien
        result = supabase.from_("tracking_links") \
            .update({"is_active": False}) \
            .eq("id", link_id) \
            .eq("merchant_id", company_id) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Link not found")

        return {
            "success": True,
            "message": "Link deactivated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deactivating link: {str(e)}"
        )

# ============================================
# ENDPOINTS - TEAM MEMBER VIEW (Read Only)
# ============================================

@router.get("/assigned-to-me")
async def get_my_assigned_links(current_user: dict = Depends(get_current_user)):
    """
    [MEMBRE D'ÉQUIPE] Voir les liens qui m'ont été attribués
    """
    try:
        member_id = current_user["id"]

        response = await run_in_threadpool(
            lambda: supabase.from_("tracking_links") \
            .select("*") \
            .eq("influencer_id", member_id) \
            .eq("is_active", True) \
            .order("created_at", desc=True) \
            .execute()
        )
            
        links = response.data or []

        # Manually fetch related data
        product_ids = list(set(l['product_id'] for l in links if l.get('product_id')))
        merchant_ids = list(set(l['merchant_id'] for l in links if l.get('merchant_id')))

        async def fetch_products():
            if not product_ids: return {}
            p_res = await run_in_threadpool(lambda: supabase.from_("products").select("id, name, description, price, images").in_("id", product_ids).execute())
            return {p['id']: p for p in p_res.data} if p_res.data else {}

        async def fetch_companies():
            if not merchant_ids: return {}
            c_res = await run_in_threadpool(lambda: supabase.from_("users").select("id, first_name, last_name, company_name").in_("id", merchant_ids).execute())
            return {c['id']: c for c in c_res.data} if c_res.data else {}

        products_map, companies_map = await asyncio.gather(fetch_products(), fetch_companies())

        # Enrichir avec URLs et stats
        enriched_links = []
        for link in links:
            link_data = link.copy()
            link_data['product'] = products_map.get(link['product_id'])
            link_data['company'] = companies_map.get(link['merchant_id'])
            link_data['short_code'] = link['unique_code']
            
            if not link_data.get("full_url"):
                link_data["full_url"] = f"https://shareyoursales.ma/r/{link['unique_code']}"
            
            link_data["qr_code_url"] = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={link_data['full_url']}"
            
            enriched_links.append(link_data)

        return {
            "success": True,
            "message": "These are the links assigned to you by your companies",
            "links": enriched_links,
            "total": len(enriched_links)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching assigned links: {str(e)}"
        )
