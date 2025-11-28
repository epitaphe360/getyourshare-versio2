"""
TikTok Live API Service

Service pour gérer les sessions live sur TikTok:
- Tracking des lives en temps réel
- Récupération des viewers et engagement
- Attribution des ventes pendant le live
- Stats post-live détaillées
- Intégration avec TikTok Shop

API utilisée: TikTok Creator API / Live Streaming API
Documentation: https://developers.tiktok.com/doc/live-streaming-api/
"""

import os
import json
import logging
import httpx
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase_client import supabase

logger = logging.getLogger(__name__)


class TikTokLiveService:
    """Service pour gérer TikTok Live API"""

    def __init__(self):
        # Configuration TikTok API
        self.api_url = os.getenv("TIKTOK_API_URL", "https://open.tiktokapis.com/v2")
        self.client_key = os.getenv("TIKTOK_CLIENT_KEY", "")
        self.client_secret = os.getenv("TIKTOK_CLIENT_SECRET", "")
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "")

        # Mode DEMO par défaut
        self.demo_mode = not bool(self.client_key and self.client_secret)

        if self.demo_mode:
            logger.warning("⚠️ TikTok Live Service en mode DEMO (pas de credentials)")
        else:
            logger.info("✅ TikTok Live Service configuré")

    async def create_live_room(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Créer une salle de live TikTok

        Args:
            session_data: {
                "title": "Live Shopping Produits",
                "description": "Découverte produits tendance",
                "cover_image_url": "https://...",
                "hashtags": ["#shopping", "#maroc"]
            }

        Returns:
            Room info avec room_id
        """
        if self.demo_mode:
            logger.info(f"🎵 [DEMO] Création TikTok Live: {session_data.get('title')}")
            return {
                "success": True,
                "room_id": f"tiktok_room_demo_{int(datetime.now().timestamp())}",
                "stream_url": "rtmp://push.tiktok.com/live/demo",
                "stream_key": "demo_tiktok_key_67890",
                "room_url": "https://www.tiktok.com/@username/live",
                "status": "ready",
                "demo_mode": True
            }

        try:
            # Créer une live room via TikTok API
            url = f"{self.api_url}/live/room/create"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "title": session_data.get("title", "Live Shopping")[:50],  # Max 50 chars
                "description": session_data.get("description", "")[:200],  # Max 200 chars
                "hashtags": session_data.get("hashtags", [])[:3]  # Max 3 hashtags
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                data = result.get("data", {})

                return {
                    "success": True,
                    "room_id": data.get("room_id"),
                    "stream_url": data.get("stream_url"),
                    "stream_key": data.get("stream_key"),
                    "room_url": data.get("share_url"),
                    "status": "ready",
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur création TikTok Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def start_live(
        self,
        room_id: str
    ) -> Dict[str, Any]:
        """
        Démarrer un live TikTok

        Change le statut de la room à LIVE
        """
        if self.demo_mode:
            logger.info(f"🎵 [DEMO] Démarrage TikTok Live: {room_id}")
            return {
                "success": True,
                "room_id": room_id,
                "status": "live",
                "live_url": f"https://www.tiktok.com/@username/live/{room_id}",
                "started_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            url = f"{self.api_url}/live/room/start"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {"room_id": room_id}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "room_id": room_id,
                    "status": "live",
                    "live_url": result.get("data", {}).get("share_url", ""),
                    "started_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur démarrage TikTok Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_stats(
        self,
        room_id: str
    ) -> Dict[str, Any]:
        """
        Récupérer les statistiques en temps réel d'un live TikTok

        Métriques:
        - Viewers actuels
        - Total viewers
        - Likes
        - Comments
        - Shares
        - Gifts (cadeaux virtuels)
        - Diamonds (revenus)
        """
        if self.demo_mode:
            import random

            current_viewers = random.randint(200, 1500)

            return {
                "room_id": room_id,
                "status": "live",
                "current_viewers": current_viewers,
                "peak_viewers": current_viewers + random.randint(100, 500),
                "total_viewers": current_viewers + random.randint(1000, 5000),
                "total_likes": random.randint(5000, 20000),
                "total_comments": random.randint(300, 1500),
                "total_shares": random.randint(50, 300),
                "total_gifts": random.randint(10, 100),
                "diamonds_earned": random.randint(100, 1000),
                "duration_seconds": random.randint(600, 3600),
                "engagement_rate": round(random.uniform(12.0, 25.0), 2),
                "demo_mode": True
            }

        try:
            url = f"{self.api_url}/live/room/stats"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            params = {"room_id": room_id}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                data = result.get("data", {})

                return {
                    "room_id": room_id,
                    "status": data.get("status", "unknown"),
                    "current_viewers": data.get("viewer_count", 0),
                    "peak_viewers": data.get("peak_viewers", 0),
                    "total_viewers": data.get("total_viewers", 0),
                    "total_likes": data.get("like_count", 0),
                    "total_comments": data.get("comment_count", 0),
                    "total_shares": data.get("share_count", 0),
                    "total_gifts": data.get("gift_count", 0),
                    "diamonds_earned": data.get("diamonds", 0),
                    "duration_seconds": data.get("duration", 0),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur récupération stats TikTok Live: {str(e)}")
            return {
                "room_id": room_id,
                "error": str(e),
                "demo_mode": False
            }

    async def end_live(
        self,
        room_id: str
    ) -> Dict[str, Any]:
        """
        Terminer un live TikTok

        Récupère les stats finales et ferme la room
        """
        if self.demo_mode:
            import random
            logger.info(f"🎵 [DEMO] Fin TikTok Live: {room_id}")

            return {
                "success": True,
                "room_id": room_id,
                "status": "ended",
                "final_stats": {
                    "total_viewers": random.randint(3000, 10000),
                    "peak_viewers": random.randint(800, 2500),
                    "total_likes": random.randint(10000, 50000),
                    "total_comments": random.randint(500, 2000),
                    "total_shares": random.randint(100, 500),
                    "total_gifts": random.randint(50, 300),
                    "diamonds_earned": random.randint(500, 3000),
                    "duration_minutes": random.randint(20, 90),
                    "engagement_rate": round(random.uniform(15.0, 28.0), 2),
                    "conversion_rate": round(random.uniform(3.0, 8.0), 2)
                },
                "ended_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            url = f"{self.api_url}/live/room/end"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {"room_id": room_id}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                data = result.get("data", {})

                return {
                    "success": True,
                    "room_id": room_id,
                    "status": "ended",
                    "final_stats": {
                        "total_viewers": data.get("total_viewers", 0),
                        "peak_viewers": data.get("peak_viewers", 0),
                        "total_likes": data.get("like_count", 0),
                        "total_comments": data.get("comment_count", 0),
                        "total_shares": data.get("share_count", 0),
                        "total_gifts": data.get("gift_count", 0),
                        "diamonds_earned": data.get("diamonds", 0),
                        "duration_minutes": int(data.get("duration", 0) / 60),
                        "engagement_rate": data.get("engagement_rate", 0)
                    },
                    "ended_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur fin TikTok Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_products(
        self,
        room_id: str
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les produits affichés pendant un live TikTok

        Intégration avec TikTok Shop pour tracking produits
        """
        if self.demo_mode:
            return [
                {
                    "product_id": "prod_demo_1",
                    "name": "Parfum Oriental Premium",
                    "price": 299.99,
                    "currency": "MAD",
                    "clicks": 156,
                    "adds_to_cart": 45,
                    "purchases": 12,
                    "revenue": 3599.88
                },
                {
                    "product_id": "prod_demo_2",
                    "name": "Montre Élégante",
                    "price": 599.99,
                    "currency": "MAD",
                    "clicks": 234,
                    "adds_to_cart": 67,
                    "purchases": 18,
                    "revenue": 10799.82
                }
            ]

        try:
            url = f"{self.api_url}/live/room/products"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            params = {"room_id": room_id}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                return result.get("data", {}).get("products", [])

        except Exception as e:
            logger.error(f"❌ Erreur récupération produits TikTok Live: {str(e)}")
            return []

    def get_optimal_live_times_morocco(self) -> List[Dict[str, Any]]:
        """
        Meilleurs moments pour faire un TikTok Live au Maroc

        Basé sur les données d'engagement TikTok MENA
        """
        return [
            {
                "day": "Jeudi",
                "time_slots": ["19:00-22:00", "13:00-15:00"],
                "engagement_score": 98,
                "reason": "Jeudi soir = pic TikTok au Maroc",
                "expected_viewers": "800-3000"
            },
            {
                "day": "Vendredi",
                "time_slots": ["20:00-23:00", "15:00-18:00"],
                "engagement_score": 96,
                "reason": "Weekend, forte activité",
                "expected_viewers": "1000-4000"
            },
            {
                "day": "Samedi",
                "time_slots": ["19:00-22:00", "14:00-17:00"],
                "engagement_score": 94,
                "reason": "Weekend, temps libre",
                "expected_viewers": "900-3500"
            },
            {
                "day": "Mercredi",
                "time_slots": ["20:00-22:00"],
                "engagement_score": 85,
                "reason": "Milieu de semaine",
                "expected_viewers": "600-2000"
            },
            {
                "day": "Dimanche",
                "time_slots": ["18:00-21:00"],
                "engagement_score": 82,
                "reason": "Fin de weekend",
                "expected_viewers": "500-1800"
            }
        ]

    def get_live_best_practices(self) -> Dict[str, Any]:
        """
        Guide des meilleures pratiques pour TikTok Live Shopping
        """
        return {
            "avant_live": [
                "📢 Annonce le live 24h avant (story + post)",
                "🎁 Prépare des codes promos exclusifs live",
                "📦 Vérifie stock des produits",
                "🎥 Teste ton setup (lumière, son, connexion)",
                "📝 Prépare script avec 3-5 produits max"
            ],
            "pendant_live": [
                "👋 Commence par saluer et présenter",
                "⏱️ Live optimal: 30-45 minutes",
                "🔥 Montre produit sous tous les angles",
                "💬 Réponds aux questions en direct",
                "🎯 CTA clairs: 'Clique sur le produit!'",
                "🔄 Rappelle codes promos régulièrement"
            ],
            "apres_live": [
                "📊 Analyse les stats",
                "📬 Envoie recap aux viewers",
                "📱 Poste replay en story 24h",
                "💰 Track les ventes attribuées",
                "📈 Note ce qui a marché pour next"
            ],
            "tips_conversion": [
                "🎁 Offre spéciale live (-15% minimum)",
                "⏰ Urgence: 'Promo valable 1h après live'",
                "🏆 'Premiers 10 acheteurs = cadeau'",
                "👥 Mention viewers par prénom",
                "🎯 Max 5 produits par live (focus)"
            ]
        }


# Instance singleton
tiktok_live_service = TikTokLiveService()
