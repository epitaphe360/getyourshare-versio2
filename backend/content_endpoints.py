"""
Content Calendar Endpoints - Python/FastAPI
Calendrier éditorial multi-plateformes pour influenceurs
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from db_helpers import get_db_connection, get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ContentPostCreate(BaseModel):
    campaign_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    platform: str  # instagram, tiktok, youtube, facebook, linkedin, twitter
    content_type: str = "post"  # post, story, reel, video, carousel, live
    status: str = "draft"  # draft, scheduled, published, failed
    scheduled_date: Optional[datetime] = None
    media_urls: List[str] = []
    thumbnail_url: Optional[str] = None
    hashtags: List[str] = []
    mentions: List[str] = []
    cta_type: str = "none"  # link, shop, swipe_up, none
    cta_url: Optional[str] = None
    tracking_link: Optional[str] = None
    is_sponsored: bool = False
    brand_name: Optional[str] = None
    commission_rate: Optional[float] = None
    auto_publish: bool = False
    notes: Optional[str] = None
    reminder_date: Optional[datetime] = None

class ContentPostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    notes: Optional[str] = None

class MetricsUpdate(BaseModel):
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    clicks: Optional[int] = None
    revenue_generated: Optional[float] = None

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/posts")
async def create_post(
    post: ContentPostCreate,
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouveau post"""
    try:
        supabase = get_db_connection()

        # Vérifier que l'utilisateur est un influenceur
        if current_user.get('role') not in ['influencer', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only influencers can create content posts"
            )

        post_data = {
            "influencer_id": current_user['id'],
            **post.dict(exclude_none=True)
        }

        result = supabase.table('content_posts').insert(post_data).execute()

        return {
            "success": True,
            "post": result.data[0] if result.data else None
        }

    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar")
async def get_calendar(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir le calendrier des posts"""
    try:
        supabase = get_db_connection()

        query = supabase.table('content_posts').select('*').eq(
            'influencer_id', current_user['id']
        )

        # Filtres
        if platform:
            query = query.eq('platform', platform)
        if status:
            query = query.eq('status', status)
        if start_date and end_date:
            query = query.gte('scheduled_date', start_date).lte('scheduled_date', end_date)

        result = query.order('scheduled_date', desc=False).limit(limit).execute()

        return {
            "success": True,
            "posts": result.data or [],
            "count": len(result.data) if result.data else 0
        }

    except Exception as e:
        logger.error(f"Error fetching calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(
    period: str = "month",
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les statistiques du calendrier"""
    try:
        supabase = get_db_connection()

        # Calculer la date de début selon la période
        from datetime import datetime, timedelta
        now = datetime.now()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)

        # Récupérer tous les posts de la période
        result = supabase.table('content_posts').select('*').eq(
            'influencer_id', current_user['id']
        ).gte('created_at', start_date.isoformat()).execute()

        posts = result.data or []

        # Calculer les statistiques
        stats = {
            "total_posts": len(posts),
            "published": len([p for p in posts if p.get('status') == 'published']),
            "scheduled": len([p for p in posts if p.get('status') == 'scheduled']),
            "drafts": len([p for p in posts if p.get('status') == 'draft']),
            "failed": len([p for p in posts if p.get('status') == 'failed']),
            "total_views": sum(p.get('views', 0) for p in posts),
            "total_likes": sum(p.get('likes', 0) for p in posts),
            "total_comments": sum(p.get('comments', 0) for p in posts),
            "total_shares": sum(p.get('shares', 0) for p in posts),
            "total_clicks": sum(p.get('clicks', 0) for p in posts),
            "total_revenue": sum(float(p.get('revenue_generated', 0)) for p in posts),
            "by_platform": {},
            "top_posts": []
        }

        # Stats par plateforme
        platforms = set(p.get('platform') for p in posts if p.get('platform'))
        for platform in platforms:
            platform_posts = [p for p in posts if p.get('platform') == platform]
            stats["by_platform"][platform] = {
                "count": len(platform_posts),
                "published": len([p for p in platform_posts if p.get('status') == 'published']),
                "views": sum(p.get('views', 0) for p in platform_posts)
            }

        # Calculer engagement rate moyen
        published_posts = [p for p in posts if p.get('status') == 'published' and p.get('engagement_rate')]
        if published_posts:
            stats["avg_engagement_rate"] = sum(float(p.get('engagement_rate', 0)) for p in published_posts) / len(published_posts)
        else:
            stats["avg_engagement_rate"] = 0

        # Top 5 posts par engagement
        sorted_posts = sorted(
            [p for p in posts if p.get('status') == 'published'],
            key=lambda x: float(x.get('engagement_rate', 0)),
            reverse=True
        )[:5]

        stats["top_posts"] = [{
            "id": p.get('id'),
            "title": p.get('title'),
            "platform": p.get('platform'),
            "engagement_rate": float(p.get('engagement_rate', 0)),
            "views": p.get('views', 0),
            "revenue": float(p.get('revenue_generated', 0))
        } for p in sorted_posts]

        return {
            "success": True,
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/{post_id}")
async def get_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir un post spécifique"""
    try:
        supabase = get_db_connection()

        result = supabase.table('content_posts').select('*').eq(
            'id', post_id
        ).eq('influencer_id', current_user['id']).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Post not found")

        return {
            "success": True,
            "post": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/posts/{post_id}")
async def update_post(
    post_id: str,
    updates: ContentPostUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour un post"""
    try:
        supabase = get_db_connection()

        # Vérifier que le post appartient à l'utilisateur
        check = supabase.table('content_posts').select('id').eq(
            'id', post_id
        ).eq('influencer_id', current_user['id']).execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Post not found")

        update_data = updates.dict(exclude_none=True)
        result = supabase.table('content_posts').update(update_data).eq('id', post_id).execute()

        return {
            "success": True,
            "post": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un post"""
    try:
        supabase = get_db_connection()

        # Vérifier que le post appartient à l'utilisateur
        check = supabase.table('content_posts').select('id').eq(
            'id', post_id
        ).eq('influencer_id', current_user['id']).execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Post not found")

        supabase.table('content_posts').delete().eq('id', post_id).execute()

        return {
            "success": True,
            "message": "Post deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/posts/{post_id}/metrics")
async def update_metrics(
    post_id: str,
    metrics: MetricsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour les métriques d'un post"""
    try:
        supabase = get_db_connection()

        # Vérifier que le post appartient à l'utilisateur
        check = supabase.table('content_posts').select('id, views').eq(
            'id', post_id
        ).eq('influencer_id', current_user['id']).execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Post not found")

        update_data = metrics.dict(exclude_none=True)

        # Calculer l'engagement rate si les métriques sont fournies
        if any(k in update_data for k in ['views', 'likes', 'comments', 'shares']):
            post_data = check.data[0]
            views = update_data.get('views', post_data.get('views', 0))
            likes = update_data.get('likes', 0)
            comments = update_data.get('comments', 0)
            shares = update_data.get('shares', 0)

            if views > 0:
                engagement_rate = ((likes + comments + shares) / views) * 100
                update_data['engagement_rate'] = round(engagement_rate, 2)

        result = supabase.table('content_posts').update(update_data).eq('id', post_id).execute()

        return {
            "success": True,
            "post": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/{post_id}/duplicate")
async def duplicate_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Dupliquer un post"""
    try:
        supabase = get_db_connection()

        # Récupérer le post original
        result = supabase.table('content_posts').select('*').eq(
            'id', post_id
        ).eq('influencer_id', current_user['id']).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Post not found")

        original = result.data[0]

        # Créer la copie
        duplicate_data = {k: v for k, v in original.items() if k not in [
            'id', 'created_at', 'updated_at', 'published_date', 'post_url', 'external_id'
        ]}
        duplicate_data['title'] = f"{original['title']} (Copie)"
        duplicate_data['status'] = 'draft'
        duplicate_data['scheduled_date'] = None
        duplicate_data['views'] = 0
        duplicate_data['likes'] = 0
        duplicate_data['comments'] = 0
        duplicate_data['shares'] = 0
        duplicate_data['clicks'] = 0
        duplicate_data['engagement_rate'] = 0
        duplicate_data['revenue_generated'] = 0

        dup_result = supabase.table('content_posts').insert(duplicate_data).execute()

        return {
            "success": True,
            "post": dup_result.data[0] if dup_result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hashtags/suggestions")
async def get_hashtag_suggestions(
    platform: str,
    category: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir des suggestions de hashtags"""
    # Base de données simple de hashtags populaires
    hashtag_database = {
        "instagram": {
            "fashion": ["#fashion", "#style", "#ootd", "#fashionblogger", "#instafashion"],
            "beauty": ["#beauty", "#makeup", "#skincare", "#beautyblogger", "#cosmetics"],
            "fitness": ["#fitness", "#workout", "#gym", "#fitnessmotivation", "#healthylifestyle"],
            "food": ["#food", "#foodie", "#foodporn", "#instafood", "#delicious"],
            "travel": ["#travel", "#wanderlust", "#travelgram", "#instatravel", "#adventure"]
        },
        "tiktok": {
            "fashion": ["#fashiontiktok", "#ootd", "#styleinspo", "#fashiontrends"],
            "beauty": ["#beautytiktok", "#makeuptutorial", "#skincareroutine", "#beautyhacks"],
            "fitness": ["#fitnesstiktok", "#workouttips", "#gymtok", "#fitnessmotivation"]
        }
    }

    hashtags = hashtag_database.get(platform, {}).get(category, [])

    return {
        "success": True,
        "hashtags": hashtags
    }
