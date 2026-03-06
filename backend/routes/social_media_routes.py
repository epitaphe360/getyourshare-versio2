"""
Routes Social Media Integrations
Instagram, TikTok, Facebook, Twitter
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import requests
import os

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/social-media", tags=["Social Media"])


# ============================================
# MODELS
# ============================================

class SocialConnect(BaseModel):
    platform: str
    access_token: str
    user_id: Optional[str] = None  # ID sur la plateforme sociale


class PostCreate(BaseModel):
    content: str
    platform: str
    media_urls: Optional[List[str]] = []
    scheduled_at: Optional[datetime] = None


# ============================================
# CONNECT PLATFORMS
# ============================================

@router.post("/{platform}/connect")
async def connect_social_media(
    platform: str,
    data: SocialConnect,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Connecter un compte de réseau social (Instagram, Facebook, TikTok, Twitter)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier le token selon la plateforme
        if platform == "instagram":
            # Vérifier le token Instagram (via Facebook Graph API)
            try:
                url = f"https://graph.facebook.com/v18.0/me?fields=id,username&access_token={data.access_token}"
                response = requests.get(url, timeout=10)

                if response.status_code != 200:
                    raise Exception("Token Instagram invalide")

                ig_data = response.json()

                connection_data = {
                    'user_id': user_id,
                    'platform': 'instagram',
                    'access_token': data.access_token,
                    'social_user_id': ig_data.get('id'),
                    'username': ig_data.get('username'),
                    'status': 'connected',
                    'connected_at': datetime.now().isoformat(),
                    'metadata': ig_data
                }

            except requests.exceptions.RequestException as e:
                raise HTTPException(status_code=400, detail=f"Erreur de connexion Instagram: {str(e)}")

        elif platform == "facebook":
            # Vérifier token Facebook
            try:
                url = f"https://graph.facebook.com/v18.0/me?fields=id,name&access_token={data.access_token}"
                response = requests.get(url, timeout=10)

                if response.status_code != 200:
                    raise Exception("Token Facebook invalide")

                fb_data = response.json()

                connection_data = {
                    'user_id': user_id,
                    'platform': 'facebook',
                    'access_token': data.access_token,
                    'social_user_id': fb_data.get('id'),
                    'username': fb_data.get('name'),
                    'status': 'connected',
                    'connected_at': datetime.now().isoformat(),
                    'metadata': fb_data
                }

            except requests.exceptions.RequestException as e:
                raise HTTPException(status_code=400, detail=f"Erreur de connexion Facebook: {str(e)}")

        elif platform == "tiktok":
            # TikTok OAuth (simulation - nécessite TikTok API access)
            connection_data = {
                'user_id': user_id,
                'platform': 'tiktok',
                'access_token': data.access_token,
                'social_user_id': data.user_id,
                'status': 'connected',
                'connected_at': datetime.now().isoformat(),
                'metadata': {'note': 'TikTok API nécessite approval'}
            }

        elif platform == "twitter":
            # Twitter OAuth 2.0 (simulation)
            connection_data = {
                'user_id': user_id,
                'platform': 'twitter',
                'access_token': data.access_token,
                'social_user_id': data.user_id,
                'status': 'connected',
                'connected_at': datetime.now().isoformat(),
                'metadata': {'note': 'Twitter API v2'}
            }

        else:
            raise HTTPException(status_code=400, detail="Plateforme non supportée")

        # Sauvegarder la connexion
        existing = supabase.table('social_media_connections').select('id').eq('user_id', user_id).eq('platform', platform).execute()

        if existing.data:
            result = supabase.table('social_media_connections').update(connection_data).eq('user_id', user_id).eq('platform', platform).execute()
        else:
            result = supabase.table('social_media_connections').insert(connection_data).execute()

        return {
            'success': True,
            'platform': platform,
            'status': 'connected',
            'message': f'{platform.capitalize()} connecté avec succès',
            'connection': result.data[0] if result.data else connection_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Social media connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connected")
async def get_connected_accounts(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des comptes sociaux connectés
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        connections = supabase.table('social_media_connections').select('platform, username, status, connected_at').eq('user_id', user_id).eq('status', 'connected').execute()

        return {
            'success': True,
            'accounts': connections.data or [],
            'total': len(connections.data) if connections.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting connected accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{platform}/disconnect")
async def disconnect_social_media(
    platform: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Déconnecter un réseau social
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        supabase.table('social_media_connections').update({'status': 'disconnected'}).eq('user_id', user_id).eq('platform', platform).execute()

        return {
            'success': True,
            'platform': platform,
            'status': 'disconnected'
        }

    except Exception as e:
        logger.error(f"Error disconnecting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POSTS
# ============================================

@router.get("/posts")
async def get_social_posts(
    platform: Optional[str] = None,
    limit: int = 20,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupérer les posts publiés sur les réseaux sociaux
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        query = supabase.table('social_media_posts').select('*').eq('user_id', user_id)

        if platform:
            query = query.eq('platform', platform)

        query = query.order('created_at', desc=True).limit(limit)

        response = query.execute()

        return {
            'success': True,
            'posts': response.data or [],
            'total': len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/create")
async def create_social_post(
    post: PostCreate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Publier sur un réseau social

    NOTE: Nécessite les APIs des plateformes configurées
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer le token de connexion
        connection = supabase.table('social_media_connections').select('access_token, social_user_id').eq('user_id', user_id).eq('platform', post.platform).single().execute()

        if not connection.data:
            raise HTTPException(status_code=404, detail=f"{post.platform.capitalize()} non connecté")

        access_token = connection.data['access_token']

        # Publier selon la plateforme
        if post.platform == "facebook":
            # Facebook Graph API
            try:
                url = f"https://graph.facebook.com/v18.0/me/feed"
                data = {
                    'message': post.content,
                    'access_token': access_token
                }

                response = requests.post(url, data=data, timeout=10)

                if response.status_code != 200:
                    raise Exception(f"Facebook API error: {response.text}")

                fb_response = response.json()

                post_id = fb_response.get('id')

            except requests.exceptions.RequestException as e:
                raise HTTPException(status_code=500, detail=f"Erreur publication Facebook: {str(e)}")

        elif post.platform == "instagram":
            # Instagram Graph API (nécessite Business account)
            post_id = "simulated_ig_post_" + str(datetime.now().timestamp())
            # TODO: Implémenter vraie API Instagram

        elif post.platform == "tiktok":
            post_id = "simulated_tt_post_" + str(datetime.now().timestamp())
            # TODO: Implémenter TikTok API

        elif post.platform == "twitter":
            post_id = "simulated_tw_post_" + str(datetime.now().timestamp())
            # TODO: Implémenter Twitter API v2

        else:
            raise HTTPException(status_code=400, detail="Plateforme non supportée")

        # Sauvegarder le post
        post_data = {
            'user_id': user_id,
            'platform': post.platform,
            'content': post.content,
            'post_id': post_id,
            'media_urls': post.media_urls,
            'status': 'published',
            'published_at': datetime.now().isoformat()
        }

        result = supabase.table('social_media_posts').insert(post_data).execute()

        return {
            'success': True,
            'platform': post.platform,
            'post_id': post_id,
            'post': result.data[0] if result.data else post_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ANALYTICS
# ============================================

@router.get("/analytics")
async def get_social_analytics(
    platform: Optional[str] = None,
    period: str = "30d",
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Analytics des réseaux sociaux (followers, engagement, reach)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer les connexions
        if platform:
            connections = supabase.table('social_media_connections').select('*').eq('user_id', user_id).eq('platform', platform).execute()
        else:
            connections = supabase.table('social_media_connections').select('*').eq('user_id', user_id).execute()

        analytics_data = []

        for conn in (connections.data or []):
            platform_name = conn.get('platform')
            access_token = conn.get('access_token')

            # Récupérer les analytics selon la plateforme
            if platform_name == "facebook":
                try:
                    # Facebook Insights API
                    url = f"https://graph.facebook.com/v18.0/me?fields=followers_count&access_token={access_token}"
                    response = requests.get(url, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        followers = data.get('followers_count', 0)
                    else:
                        followers = 0
                except Exception:
                    followers = 0

                analytics_data.append({
                    'platform': 'facebook',
                    'followers': followers,
                    'engagement': conn.get('engagement_rate') or 0.0,
                    'reach': conn.get('reach') or 0
                })

            elif platform_name == "instagram":
                # Instagram Basic Display API / Graph API Insights
                ig_followers = 0
                ig_engagement = 0.0
                ig_reach = 0
                try:
                    ig_url = f"https://graph.facebook.com/v18.0/me?fields=followers_count,media_count&access_token={access_token}"
                    ig_resp = requests.get(ig_url, timeout=10)
                    if ig_resp.status_code == 200:
                        ig_data = ig_resp.json()
                        ig_followers = ig_data.get('followers_count', 0)
                except Exception:
                    pass
                # Fallback sur les données stockées en BDD
                if ig_followers == 0:
                    ig_followers = (conn.get('metadata') or {}).get('followers_count', 0) or conn.get('followers_count', 0)
                analytics_data.append({
                    'platform': 'instagram',
                    'followers': ig_followers,
                    'engagement': conn.get('engagement_rate') or ig_engagement,
                    'reach': conn.get('reach') or ig_reach
                })

            elif platform_name == "tiktok":
                # Données TikTok stockées lors de la connexion
                tt_meta = conn.get('metadata') or {}
                analytics_data.append({
                    'platform': 'tiktok',
                    'followers': tt_meta.get('follower_count', 0) or conn.get('followers_count', 0),
                    'engagement': conn.get('engagement_rate') or 0.0,
                    'reach': conn.get('reach') or 0
                })

        return {
            'success': True,
            'period': period,
            'analytics': analytics_data,
            'note': 'Intégrer vraies APIs pour données réelles'
        }

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
