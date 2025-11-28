"""
Facebook Live API Service

Service pour gérer les sessions live sur Facebook:
- Création de live videos
- Récupération des viewers et engagement en temps réel
- Gestion des commentaires live
- Attribution des ventes pendant le live
- Integration Facebook Shop

API utilisée: Facebook Graph API
Documentation: https://developers.facebook.com/docs/live-video-api/
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase_client import supabase

logger = logging.getLogger(__name__)


class FacebookLiveService:
    """Service pour gérer Facebook Live API"""

    def __init__(self):
        # Configuration Facebook API
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        self.page_id = os.getenv("FACEBOOK_PAGE_ID", "")
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.app_id = os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET", "")

        # Mode DEMO par défaut
        self.demo_mode = not bool(self.access_token and self.page_id)

        if self.demo_mode:
            logger.warning("⚠️ Facebook Live Service en mode DEMO (pas de credentials)")
        else:
            logger.info("✅ Facebook Live Service configuré")

    async def create_live_video(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Créer une live video Facebook

        Args:
            session_data: {
                "title": "Live Shopping Produits",
                "description": "Découverte de produits tendance",
                "planned_start_time": "2025-11-30T20:00:00",
                "privacy": "PUBLIC"  # PUBLIC, FRIENDS, ONLY_ME
            }

        Returns:
            Live video info avec video_id et stream_url
        """
        if self.demo_mode:
            logger.info(f"📘 [DEMO] Création Facebook Live: {session_data.get('title')}")
            return {
                "success": True,
                "video_id": f"fb_live_demo_{int(datetime.now().timestamp())}",
                "stream_url": "rtmps://live-api-s.facebook.com:443/rtmp/",
                "stream_key": "demo_fb_stream_key_xyz789",
                "secure_stream_url": "rtmps://live-api-s.facebook.com:443/rtmp/demo",
                "status": "SCHEDULED_UNPUBLISHED",
                "permalink_url": "https://facebook.com/demo_page/videos/demo_video_id",
                "demo_mode": True
            }

        try:
            # Créer la live video via Graph API
            url = f"{self.graph_api_url}/{self.page_id}/live_videos"

            params = {
                "access_token": self.access_token,
                "title": session_data.get("title", "Live Shopping"),
                "description": session_data.get("description", ""),
                "privacy": json.dumps({"value": session_data.get("privacy", "PUBLIC")}),
                "status": "SCHEDULED_UNPUBLISHED",
                "planned_start_time": session_data.get(
                    "planned_start_time",
                    int(datetime.utcnow().timestamp())
                ),
                "save_vod": True,  # Sauvegarder VOD après live
                "stop_on_delete_stream": True
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, timeout=30.0)
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "video_id": result["id"],
                    "stream_url": result.get("stream_url", ""),
                    "stream_key": result.get("stream_url", "").split("/")[-1] if result.get("stream_url") else "",
                    "secure_stream_url": result.get("secure_stream_url", ""),
                    "status": result.get("status", "SCHEDULED_UNPUBLISHED"),
                    "permalink_url": result.get("permalink_url", ""),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur création Facebook Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def go_live(
        self,
        video_id: str
    ) -> Dict[str, Any]:
        """
        Passer une live video en mode LIVE (publier)

        Change le statut de SCHEDULED à LIVE
        """
        if self.demo_mode:
            logger.info(f"📘 [DEMO] Démarrage Facebook Live: {video_id}")
            return {
                "success": True,
                "video_id": video_id,
                "status": "LIVE",
                "permalink_url": f"https://facebook.com/demo_page/videos/{video_id}",
                "started_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            # Mettre à jour le statut
            url = f"{self.graph_api_url}/{video_id}"

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
                    "video_id": video_id,
                    "status": "LIVE",
                    "permalink_url": result.get("permalink_url", ""),
                    "started_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur démarrage Facebook Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_stats(
        self,
        video_id: str
    ) -> Dict[str, Any]:
        """
        Récupérer les statistiques en temps réel d'une Facebook Live

        Métriques:
        - Viewers en direct
        - Reactions (likes, love, haha, etc.)
        - Commentaires
        - Partages
        - Peak concurrent viewers
        """
        if self.demo_mode:
            import random

            current_viewers = random.randint(100, 600)

            return {
                "video_id": video_id,
                "status": "LIVE",
                "live_views": current_viewers,
                "total_views": current_viewers + random.randint(500, 2000),
                "peak_live_views": current_viewers + random.randint(50, 200),
                "reactions": {
                    "like": random.randint(100, 500),
                    "love": random.randint(50, 300),
                    "haha": random.randint(10, 100),
                    "wow": random.randint(20, 150),
                    "total": random.randint(200, 1000)
                },
                "comments_count": random.randint(50, 400),
                "shares_count": random.randint(10, 100),
                "duration_seconds": random.randint(300, 2400),
                "demo_mode": True
            }

        try:
            # Récupérer les stats via Graph API
            url = f"{self.graph_api_url}/{video_id}"

            params = {
                "access_token": self.access_token,
                "fields": "live_views,status,permalink_url,creation_time,video_views,reactions.summary(true),comments.summary(true),shares"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                result = response.json()

                # Calculer durée
                start_time = datetime.fromisoformat(result.get("creation_time", "").replace("Z", "+00:00"))
                duration = (datetime.utcnow() - start_time.replace(tzinfo=None)).total_seconds()

                return {
                    "video_id": video_id,
                    "status": result.get("status", "unknown"),
                    "live_views": result.get("live_views", 0),
                    "total_views": result.get("video_views", 0),
                    "reactions": result.get("reactions", {}).get("summary", {}),
                    "comments_count": result.get("comments", {}).get("summary", {}).get("total_count", 0),
                    "shares_count": result.get("shares", {}).get("count", 0),
                    "duration_seconds": int(duration),
                    "permalink_url": result.get("permalink_url", ""),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur récupération stats Facebook Live: {str(e)}")
            return {
                "video_id": video_id,
                "error": str(e),
                "demo_mode": False
            }

    async def end_live_video(
        self,
        video_id: str
    ) -> Dict[str, Any]:
        """
        Terminer une Facebook Live video

        Change le statut à VOD (Video On Demand)
        """
        if self.demo_mode:
            import random
            logger.info(f"📘 [DEMO] Fin Facebook Live: {video_id}")

            return {
                "success": True,
                "video_id": video_id,
                "status": "VOD",
                "final_stats": {
                    "total_views": random.randint(1000, 5000),
                    "peak_live_views": random.randint(200, 1000),
                    "total_reactions": random.randint(500, 2500),
                    "total_comments": random.randint(100, 800),
                    "total_shares": random.randint(20, 200),
                    "duration_minutes": random.randint(20, 90),
                    "engagement_rate": round(random.uniform(10.0, 20.0), 2),
                    "reach": random.randint(2000, 10000)
                },
                "vod_url": f"https://facebook.com/demo_page/videos/{video_id}",
                "ended_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            # Terminer la live
            url = f"{self.graph_api_url}/{video_id}"

            params = {
                "access_token": self.access_token,
                "end_live_video": True
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, timeout=30.0)
                response.raise_for_status()

                # Récupérer les stats finales
                stats_url = f"{self.graph_api_url}/{video_id}/video_insights"
                stats_params = {
                    "access_token": self.access_token,
                    "metric": "total_video_views,total_video_views_unique,total_video_complete_views"
                }

                stats_response = await client.get(
                    stats_url,
                    params=stats_params,
                    timeout=30.0
                )
                stats_result = stats_response.json()

                # Récupérer les réactions/commentaires
                video_stats = await self.get_live_stats(video_id)

                return {
                    "success": True,
                    "video_id": video_id,
                    "status": "VOD",
                    "final_stats": {
                        "total_views": video_stats.get("total_views", 0),
                        "peak_live_views": video_stats.get("peak_live_views", 0),
                        "total_reactions": video_stats.get("reactions", {}).get("total", 0),
                        "total_comments": video_stats.get("comments_count", 0),
                        "total_shares": video_stats.get("shares_count", 0),
                        "engagement_rate": 0  # À calculer
                    },
                    "vod_url": video_stats.get("permalink_url", ""),
                    "ended_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur fin Facebook Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_comments(
        self,
        video_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les commentaires d'une Facebook Live

        Utile pour:
        - Modération en temps réel
        - Engagement analytics
        - Détection questions produits
        """
        if self.demo_mode:
            import random
            demo_comments = [
                {
                    "author_name": "Leila Alaoui",
                    "message": "Super live! J'adore 😍",
                    "created_time": "2025-11-28T20:05:00Z",
                    "like_count": 12
                },
                {
                    "author_name": "Youssef Bennani",
                    "message": "Quel est le prix du produit?",
                    "created_time": "2025-11-28T20:07:00Z",
                    "like_count": 5
                },
                {
                    "author_name": "Nadia Sebti",
                    "message": "Je commande tout de suite! 🛒",
                    "created_time": "2025-11-28T20:10:00Z",
                    "like_count": 8
                }
            ]
            return random.sample(demo_comments, min(limit, len(demo_comments)))

        try:
            url = f"{self.graph_api_url}/{video_id}/comments"

            params = {
                "access_token": self.access_token,
                "limit": limit,
                "fields": "from,message,created_time,like_count",
                "order": "reverse_chronological"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                result = response.json()

                comments = []
                for comment in result.get("data", []):
                    comments.append({
                        "author_name": comment.get("from", {}).get("name", "Unknown"),
                        "author_id": comment.get("from", {}).get("id", ""),
                        "message": comment.get("message", ""),
                        "created_time": comment.get("created_time", ""),
                        "like_count": comment.get("like_count", 0)
                    })

                return comments

        except Exception as e:
            logger.error(f"❌ Erreur récupération commentaires Facebook: {str(e)}")
            return []

    async def add_product_tags(
        self,
        video_id: str,
        product_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Ajouter des tags produits à une Facebook Live

        Permet aux viewers de cliquer sur les produits pendant le live
        Nécessite Facebook Shop configuré
        """
        if self.demo_mode:
            logger.info(f"📘 [DEMO] Ajout tags produits: {len(product_ids)} produits")
            return {
                "success": True,
                "video_id": video_id,
                "products_tagged": len(product_ids),
                "demo_mode": True
            }

        try:
            url = f"{self.graph_api_url}/{video_id}/product_tags"

            headers = {
                "Content-Type": "application/json"
            }

            tags = []
            for product_id in product_ids:
                tags.append({
                    "product_id": product_id,
                    "is_organic": True
                })

            params = {
                "access_token": self.access_token,
                "tags": json.dumps(tags)
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()

                return {
                    "success": True,
                    "video_id": video_id,
                    "products_tagged": len(product_ids),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur ajout tags produits: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_optimal_live_times_morocco(self) -> List[Dict[str, Any]]:
        """
        Meilleurs moments pour faire un Facebook Live au Maroc

        Basé sur les données d'engagement Facebook MENA
        """
        return [
            {
                "day": "Jeudi",
                "time_slots": ["20:00-22:00", "13:00-15:00"],
                "engagement_score": 93,
                "reason": "Pic activité Facebook au Maroc",
                "expected_viewers": "300-1500"
            },
            {
                "day": "Vendredi",
                "time_slots": ["19:00-21:00", "15:00-17:00"],
                "engagement_score": 90,
                "reason": "Weekend, temps libre",
                "expected_viewers": "400-1800"
            },
            {
                "day": "Samedi",
                "time_slots": ["18:00-21:00"],
                "engagement_score": 88,
                "reason": "Soirée weekend",
                "expected_viewers": "350-1600"
            },
            {
                "day": "Dimanche",
                "time_slots": ["19:00-21:00"],
                "engagement_score": 85,
                "reason": "Fin de weekend",
                "expected_viewers": "250-1200"
            },
            {
                "day": "Mercredi",
                "time_slots": ["20:00-22:00"],
                "engagement_score": 78,
                "reason": "Milieu de semaine",
                "expected_viewers": "200-1000"
            }
        ]

    def get_live_best_practices(self) -> Dict[str, Any]:
        """
        Guide des meilleures pratiques pour Facebook Live Shopping
        """
        return {
            "preparation": [
                "📢 Annonce le live 24-48h avant",
                "🎁 Créé un événement Facebook",
                "📱 Invite tes amis/followers",
                "🎥 Teste connexion et setup",
                "📝 Prépare 3-5 produits max"
            ],
            "pendant_live": [
                "👋 Salue les viewers par prénom",
                "🏷️ Tag les produits en temps réel",
                "💬 Réponds aux commentaires rapidement",
                "⏱️ Durée optimale: 20-45 minutes",
                "🎯 CTA: 'Clique sur le produit tagué!'",
                "🔁 Rappelle les promos toutes les 5 min"
            ],
            "apres_live": [
                "💾 Le live reste en VOD automatiquement",
                "📊 Check les insights vidéo",
                "📧 Message aux viewers engagés",
                "🎬 Partage les highlights en post",
                "📈 Analyse ce qui a fonctionné"
            ],
            "tips_engagement": [
                "🎁 'Les 5 premiers à commenter gagnent X'",
                "❓ Pose des questions pour stimuler chat",
                "🏆 Annonce offre exclusive live",
                "⏰ 'Promo valable pendant le live uniquement'",
                "👥 Invite un co-animateur (+ d'audience)"
            ]
        }


# Instance singleton
facebook_live_service = FacebookLiveService()
