"""
Smart Match Endpoints
Endpoints pour le matching intelligent influenceurs-marques
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from smart_match_service import (
    SmartMatchService,
    BatchMatchingService,
    InfluencerProfile,
    BrandProfile,
    MatchResult,
    Niche,
    AudienceAge,
    AudienceGender
)
from auth import get_current_user
# from db_helpers import log_user_activity  # TODO: Implémenter log_user_activity dans db_helpers

router = APIRouter(prefix="/api/smart-match", tags=["Smart Match"])

# Initialiser les services
matcher = SmartMatchService()
batch_matcher = BatchMatchingService()

# ============================================
# ENDPOINTS
# ============================================

@router.post("/find-influencers", response_model=List[MatchResult])
async def find_matching_influencers(
    brand_profile: BrandProfile,
    top_n: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Trouve les meilleurs influenceurs pour une marque

    Retourne une liste de matches triée par score de compatibilité
    avec prédictions de ROI, reach, et conversions.
    """

    try:
        # Récupérer les vrais influenceurs depuis Supabase
        real_influencers = await get_real_influencers()

        matches = await matcher.find_matches_for_brand(
            brand=brand_profile,
            influencers=real_influencers,
            top_n=top_n
        )

        return matches

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching: {str(e)}"
        )


@router.post("/find-brands", response_model=List[MatchResult])
async def find_matching_brands(
    influencer_profile: InfluencerProfile,
    top_n: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Trouve les meilleures marques pour un influenceur

    Retourne les opportunités les plus compatibles avec l'influenceur.
    """

    try:
        # Récupérer les vraies marques depuis Supabase
        real_brands = await get_mock_brands()  # contient déjà la logique Supabase-first

        matches = await matcher.find_matches_for_influencer(
            influencer=influencer_profile,
            brands=real_brands,
            top_n=top_n
        )

        return matches

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching: {str(e)}"
        )


@router.post("/batch-match-campaign")
async def batch_match_campaign(
    campaign_id: str,
    brand_profile: BrandProfile,
    target_influencer_count: int = 10,
    min_score: float = 65.0,
    current_user: dict = Depends(get_current_user)
):
    """
    Matche une campagne complète avec les meilleurs influenceurs
    """
    try:
        all_influencers = await get_real_influencers()

        campaign_report = await batch_matcher.match_campaign_to_influencers(
            campaign_id=campaign_id,
            brand=brand_profile,
            all_influencers=all_influencers,
            target_influencer_count=target_influencer_count,
            min_score=min_score
        )
        return campaign_report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du batch matching: {str(e)}"
        )


@router.get("/my-compatibility/{brand_id}")
async def check_my_compatibility(
    brand_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifie la compatibilité de l'influenceur connecté avec une marque spécifique.
    """
    try:
        from supabase_client import supabase

        # Récupérer le profil influenceur réel
        influencer_profile = await get_real_influencer_profile(current_user["id"])
        if not influencer_profile:
            raise HTTPException(status_code=404, detail="Profil influenceur introuvable")

        # Récupérer le profil marque réel
        brand_profile = await get_real_brand_profile(brand_id)
        if not brand_profile:
            raise HTTPException(status_code=404, detail="Marque introuvable")

        match_result = await matcher._calculate_match_score(
            influencer=influencer_profile,
            brand=brand_profile
        )
        return match_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


# ============================================
# DATA HELPERS — Données réelles Supabase (fallback mock si tables vides)
# ============================================

async def get_real_influencers() -> List[InfluencerProfile]:
    """Alias vers get_mock_influencers (déjà Supabase-first)"""
    return await get_mock_influencers()


async def get_real_influencer_profile(user_id: str):
    """Récupère le profil influenceur depuis la table users + influencers_profiles."""
    try:
        from supabase_client import supabase
        # Essayer smart_match_influencers en priorité
        r = supabase.table("smart_match_influencers").select("*").eq("user_id", user_id).limit(1).execute()
        if r.data:
            inf = r.data[0]
            return InfluencerProfile(
                user_id=inf["user_id"], name=inf["name"],
                niches=inf.get("niches", []), followers_count=inf.get("followers_count", 0),
                engagement_rate=inf.get("engagement_rate", 0.0),
                audience_age=inf.get("audience_age", []), audience_gender=inf.get("audience_gender", AudienceGender.MIXED),
                audience_location=inf.get("audience_location", []), platforms=inf.get("platforms", []),
                average_views=inf.get("average_views", 0), content_quality_score=inf.get("content_quality_score", 70.0),
                reliability_score=inf.get("reliability_score", 70.0), preferred_commission=inf.get("preferred_commission", 10.0),
                language=inf.get("language", ["fr"])
            )
        # Fallback sur users + influencers
        u = supabase.table("users").select("id, email").eq("id", user_id).limit(1).execute()
        ip = supabase.table("influencers").select("*").eq("user_id", user_id).limit(1).execute()
        if u.data:
            user = u.data[0]
            profile = ip.data[0] if ip.data else {}
            return InfluencerProfile(
                user_id=user["id"], name=profile.get("name") or user.get("email", ""),
                niches=[Niche.FASHION], followers_count=profile.get("followers_count", 0),
                engagement_rate=profile.get("engagement_rate", 0.0),
                audience_age=[AudienceAge.YOUNG_ADULT], audience_gender=AudienceGender.MIXED,
                audience_location=["MA"], platforms=["instagram"],
                average_views=0, content_quality_score=70.0, reliability_score=70.0,
                preferred_commission=10.0, language=["fr"]
            )
    except Exception as e:
        print(f"get_real_influencer_profile error: {e}")
    return None


async def get_real_brand_profile(brand_id: str):
    """Récupère le profil marque depuis merchants ou smart_match_brands."""
    try:
        from supabase_client import supabase
        # Essayer smart_match_brands en priorité
        r = supabase.table("smart_match_brands").select("*").eq("company_id", brand_id).limit(1).execute()
        if r.data:
            brand = r.data[0]
            return BrandProfile(
                company_id=brand["company_id"], company_name=brand["company_name"],
                product_category=brand.get("product_category", Niche.FASHION),
                target_audience_age=brand.get("target_audience_age", [AudienceAge.ADULT]),
                target_audience_gender=brand.get("target_audience_gender", AudienceGender.MIXED),
                target_locations=brand.get("target_locations", ["MA"]),
                budget_per_influencer=brand.get("budget_per_influencer", 1000.0),
                commission_percentage=brand.get("commission_percentage", 10.0),
                campaign_description=brand.get("campaign_description", ""),
                required_followers_min=brand.get("required_followers_min", 1000),
                required_engagement_min=brand.get("required_engagement_min", 1.0),
                preferred_platforms=brand.get("preferred_platforms", ["instagram"]),
                language=brand.get("language", ["fr"])
            )
        # Fallback sur merchants
        m = supabase.table("merchants").select("*").eq("id", brand_id).limit(1).execute()
        if m.data:
            merchant = m.data[0]
            return BrandProfile(
                company_id=merchant["id"], company_name=merchant.get("company_name", merchant["id"]),
                product_category=Niche.FASHION, target_audience_age=[AudienceAge.ADULT],
                target_audience_gender=AudienceGender.MIXED, target_locations=["MA"],
                budget_per_influencer=1000.0, commission_percentage=10.0,
                campaign_description=merchant.get("description", ""),
                required_followers_min=1000, required_engagement_min=1.0,
                preferred_platforms=["instagram"], language=["fr"]
            )
    except Exception as e:
        print(f"get_real_brand_profile error: {e}")
    return None


async def get_mock_influencers() -> List[InfluencerProfile]:
    """Get influencers from DB (fallback to mock)"""
    try:
        from supabase_client import supabase
        result = supabase.table("smart_match_influencers").select("*").execute()
        if result.data:
            influencers = []
            for inf in result.data:
                # Convert DB fields to Pydantic model
                # Note: Enums need to be handled if they are strict
                influencers.append(InfluencerProfile(
                    user_id=inf["user_id"],
                    name=inf["name"],
                    niches=inf["niches"],
                    followers_count=inf["followers_count"],
                    engagement_rate=inf["engagement_rate"],
                    audience_age=inf["audience_age"],
                    audience_gender=inf["audience_gender"],
                    audience_location=inf["audience_location"],
                    platforms=inf["platforms"],
                    average_views=inf["average_views"],
                    content_quality_score=inf["content_quality_score"],
                    reliability_score=inf["reliability_score"],
                    preferred_commission=inf["preferred_commission"],
                    language=inf["language"]
                ))
            return influencers
    except Exception as e:
        print(f"Error fetching influencers from DB: {e}")
    
    # Fallback
    return [
        InfluencerProfile(
            user_id="inf_1",
            name="Sarah Fashion",
            niches=[Niche.FASHION, Niche.BEAUTY],
            followers_count=50000,
            engagement_rate=4.5,
            audience_age=[AudienceAge.YOUNG_ADULT, AudienceAge.ADULT],
            audience_gender=AudienceGender.FEMALE,
            audience_location=["MA", "FR"],
            platforms=["instagram", "tiktok"],
            average_views=15000,
            content_quality_score=85.0,
            reliability_score=92.0,
            preferred_commission=10.0,
            language=["fr", "ar"]
        ),
        InfluencerProfile(
            user_id="inf_2",
            name="Tech Morocco",
            niches=[Niche.TECH, Niche.BUSINESS],
            followers_count=120000,
            engagement_rate=3.2,
            audience_age=[AudienceAge.ADULT],
            audience_gender=AudienceGender.MIXED,
            audience_location=["MA"],
            platforms=["youtube", "instagram"],
            average_views=45000,
            content_quality_score=90.0,
            reliability_score=95.0,
            preferred_commission=15.0,
            language=["fr", "ar", "en"]
        )
    ]


async def get_mock_brands() -> List[BrandProfile]:
    """Get brands from DB (fallback to mock)"""
    try:
        from supabase_client import supabase
        result = supabase.table("smart_match_brands").select("*").execute()
        if result.data:
            brands = []
            for brand in result.data:
                brands.append(BrandProfile(
                    company_id=brand["company_id"],
                    company_name=brand["company_name"],
                    product_category=brand["product_category"],
                    target_audience_age=brand["target_audience_age"],
                    target_audience_gender=brand["target_audience_gender"],
                    target_locations=brand["target_locations"],
                    budget_per_influencer=brand["budget_per_influencer"],
                    commission_percentage=brand["commission_percentage"],
                    campaign_description=brand["campaign_description"],
                    required_followers_min=brand["required_followers_min"],
                    required_engagement_min=brand["required_engagement_min"],
                    preferred_platforms=brand["preferred_platforms"],
                    language=brand["language"]
                ))
            return brands
    except Exception as e:
        print(f"Error fetching brands from DB: {e}")

    # Fallback
    return [
        BrandProfile(
            company_id="brand_1",
            company_name="Moroccan Beauty Co",
            product_category=Niche.BEAUTY,
            target_audience_age=[AudienceAge.YOUNG_ADULT, AudienceAge.ADULT],
            target_audience_gender=AudienceGender.FEMALE,
            target_locations=["MA"],
            budget_per_influencer=3000.0,
            commission_percentage=12.0,
            campaign_description="Produits de beauté naturels marocains",
            required_followers_min=10000,
            required_engagement_min=3.0,
            preferred_platforms=["instagram", "tiktok"],
            language=["fr", "ar"]
        )
    ]


async def get_mock_influencer_profile(user_id: str) -> InfluencerProfile:
    """Get mock influencer profile"""
    influencers = await get_mock_influencers()
    return influencers[0] if influencers else None


async def get_mock_brand_profile(brand_id: str) -> BrandProfile:
    """Get mock brand profile"""
    brands = await get_mock_brands()
    return brands[0] if brands else None
