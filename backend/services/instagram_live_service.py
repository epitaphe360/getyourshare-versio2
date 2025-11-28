"""
Instagram Live API Service

Service pour gérer les sessions live sur Instagram:
- Création de live streams
- Récupération des viewers en temps réel
- Tracking des commentaires et engagement
- Attribution des ventes pendant le live
- Stats post-live

API utilisée: Facebook Graph API / Instagram API
Documentation: https://developers.facebook.com/docs/instagram-api/
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase_client import supabase

logger = logging.getLogger(__name__)


class InstagramLiveService:
    """Service pour gérer Instagram Live API"""

    def __init__(self):
        # Configuration Instagram/Facebook API
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        self.instagram_user_id = os.getenv("INSTAGRAM_USER_ID", "")
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.app_id = os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET", "")

        # Mode DEMO par défaut si pas de credentials
        self.demo_mode = not bool(self.access_token and self.instagram_user_id)

        if self.demo_mode:
            logger.warning("⚠️ Instagram Live Service en mode DEMO (pas de credentials)")
        else:
            logger.info("✅ Instagram Live Service configuré")

    async def create_live_stream(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Créer un live stream Instagram

        Args:
            session_data: {
                "title": "Mon Live Shopping",
                "description": "Découverte de produits",
                "start_time": "2025-11-30T20:00:00"
            }

        Returns:
            Live stream info avec broadcast_id
        """
        if self.demo_mode:
            logger.info(f"📱 [DEMO] Création Instagram Live: {session_data.get('title')}")
            return {
                "success": True,
                "broadcast_id": f"ig_live_demo_{int(datetime.now().timestamp())}",
                "stream_url": "rtmps://live-upload.instagram.com/rtmp/demo",
                "stream_key": "demo_stream_key_12345",
                "status": "ready",
                "demo_mode": True
            }

        try:
            # Créer une session live via Graph API
            url = f"{self.graph_api_url}/{self.instagram_user_id}/live_videos"

            params = {
                "access_token": self.access_token,
                "title": session_data.get("title", "Live Shopping"),
                "description": session_data.get("description", ""),
                "status": "UNPUBLISHED"  # Sera publié au start
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, timeout=30.0)
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "broadcast_id": result["id"],
                    "stream_url": result.get("stream_url", ""),
                    "stream_key": result.get("stream_key", ""),
                    "status": "ready",
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur création Instagram Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def start_live_stream(
        self,
        broadcast_id: str
    ) -> Dict[str, Any]:
        """
        Démarrer un live stream Instagram

        Publie le live et commence le streaming
        """
        if self.demo_mode:
            logger.info(f"📱 [DEMO] Démarrage Instagram Live: {broadcast_id}")
            return {
                "success": True,
                "broadcast_id": broadcast_id,
                "status": "live",
                "live_url": f"https://www.instagram.com/demo_username/live/",
                "started_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            # Publier le live stream
            url = f"{self.graph_api_url}/{broadcast_id}"

            params = {
                "access_token": self.access_token,
                "status": "LIVE_NOW"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, timeout=30.0)
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "broadcast_id": broadcast_id,
                    "status": "live",
                    "live_url": result.get("permalink_url", ""),
                    "started_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur démarrage Instagram Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_stats(
        self,
        broadcast_id: str
    ) -> Dict[str, Any]:
        """
        Récupérer les statistiques en temps réel d'un live Instagram

        Métriques:
        - Viewers actuels
        - Total viewers
        - Likes
        - Commentaires
        - Durée
        """
        if self.demo_mode:
            # Données demo réalistes
            import random
            current_viewers = random.randint(150, 800)

            return {
                "broadcast_id": broadcast_id,
                "status": "live",
                "current_viewers": current_viewers,
                "peak_viewers": current_viewers + random.randint(50, 200),
                "total_viewers": current_viewers + random.randint(500, 2000),
                "likes": random.randint(500, 3000),
                "comments_count": random.randint(50, 300),
                "duration_seconds": random.randint(300, 1800),
                "demo_mode": True
            }

        try:
            # Récupérer les stats via Graph API
            url = f"{self.graph_api_url}/{broadcast_id}"

            params = {
                "access_token": self.access_token,
                "fields": "live_views,status,creation_time,permalink_url"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                result = response.json()

                # Calculer la durée
                start_time = datetime.fromisoformat(result["creation_time"].replace("Z", "+00:00"))
                duration = (datetime.utcnow() - start_time.replace(tzinfo=None)).total_seconds()

                return {
                    "broadcast_id": broadcast_id,
                    "status": result.get("status", "unknown"),
                    "current_viewers": result.get("live_views", 0),
                    "duration_seconds": int(duration),
                    "live_url": result.get("permalink_url", ""),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur récupération stats Instagram Live: {str(e)}")
            return {
                "broadcast_id": broadcast_id,
                "error": str(e),
                "demo_mode": False
            }

    async def end_live_stream(
        self,
        broadcast_id: str
    ) -> Dict[str, Any]:
        """
        Terminer un live stream Instagram

        Récupère les stats finales et arrête le streaming
        """
        if self.demo_mode:
            import random
            logger.info(f"📱 [DEMO] Fin Instagram Live: {broadcast_id}")

            return {
                "success": True,
                "broadcast_id": broadcast_id,
                "status": "ended",
                "final_stats": {
                    "total_viewers": random.randint(1500, 5000),
                    "peak_viewers": random.randint(500, 1500),
                    "total_likes": random.randint(2000, 8000),
                    "total_comments": random.randint(200, 800),
                    "duration_minutes": random.randint(15, 60),
                    "engagement_rate": round(random.uniform(8.0, 15.0), 2)
                },
                "ended_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            # Terminer le live
            url = f"{self.graph_api_url}/{broadcast_id}"

            params = {
                "access_token": self.access_token,
                "status": "VOD"  # Video On Demand (archivé)
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, timeout=30.0)
                response.raise_for_status()

                # Récupérer les stats finales
                stats_response = await client.get(
                    url,
                    params={
                        "access_token": self.access_token,
                        "fields": "live_views,reactions,comments_count,creation_time"
                    },
                    timeout=30.0
                )
                stats = stats_response.json()

                # Calculer durée
                start_time = datetime.fromisoformat(stats["creation_time"].replace("Z", "+00:00"))
                duration = (datetime.utcnow() - start_time.replace(tzinfo=None)).total_seconds()

                return {
                    "success": True,
                    "broadcast_id": broadcast_id,
                    "status": "ended",
                    "final_stats": {
                        "total_viewers": stats.get("live_views", 0),
                        "total_likes": stats.get("reactions", {}).get("like", 0),
                        "total_comments": stats.get("comments_count", 0),
                        "duration_minutes": int(duration / 60),
                        "engagement_rate": 0  # À calculer
                    },
                    "ended_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur fin Instagram Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_comments(
        self,
        broadcast_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les commentaires d'un live Instagram

        Utile pour:
        - Modération en temps réel
        - Engagement analytics
        - Détection questions produits
        """
        if self.demo_mode:
            import random
            demo_comments = [
                {"username": "sarah_92", "text": "Trop cool ce live! 😍", "timestamp": "2025-11-28T20:05:00"},
                {"username": "mohamed_casa", "text": "C'est combien le prix?", "timestamp": "2025-11-28T20:06:00"},
                {"username": "amina_style", "text": "J'adore! Je commande 🛍️", "timestamp": "2025-11-28T20:07:00"},
                {"username": "karim_tech", "text": "Livraison à Rabat possible?", "timestamp": "2025-11-28T20:08:00"},
                {"username": "fatima_beauty", "text": "💕💕💕", "timestamp": "2025-11-28T20:09:00"}
            ]
            return random.sample(demo_comments, min(limit, len(demo_comments)))

        try:
            url = f"{self.graph_api_url}/{broadcast_id}/comments"

            params = {
                "access_token": self.access_token,
                "limit": limit,
                "fields": "username,text,timestamp,like_count"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                result = response.json()

                return result.get("data", [])

        except Exception as e:
            logger.error(f"❌ Erreur récupération commentaires: {str(e)}")
            return []

    def get_optimal_live_times(self) -> List[Dict[str, Any]]:
        """
        Obtenir les meilleurs moments pour faire un live Instagram au Maroc

        Basé sur les données d'engagement Instagram
        """
        return [
            {
                "day": "Jeudi",
                "time_slots": ["20:00-22:00", "12:00-14:00"],
                "engagement_score": 95,
                "reason": "Pic d'activité avant weekend"
            },
            {
                "day": "Vendredi",
                "time_slots": ["19:00-21:00", "15:00-17:00"],
                "engagement_score": 92,
                "reason": "Soirée weekend, forte activité"
            },
            {
                "day": "Samedi",
                "time_slots": ["20:00-23:00", "14:00-16:00"],
                "engagement_score": 88,
                "reason": "Weekend, temps libre"
            },
            {
                "day": "Dimanche",
                "time_slots": ["19:00-21:00"],
                "engagement_score": 85,
                "reason": "Fin de weekend"
            },
            {
                "day": "Mercredi",
                "time_slots": ["20:00-22:00"],
                "engagement_score": 78,
                "reason": "Milieu de semaine"
            }
        ]


# Instance singleton
instagram_live_service = InstagramLiveService()
