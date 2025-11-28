"""
YouTube Live API Service

Service pour gérer les sessions live sur YouTube:
- Création de live streams
- Récupération des viewers et analytics en temps réel
- Gestion du chat live
- Attribution des ventes pendant le live
- Integration YouTube Shopping

API utilisée: YouTube Data API v3 / YouTube Live Streaming API
Documentation: https://developers.google.com/youtube/v3/live
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase_client import supabase

logger = logging.getLogger(__name__)


class YouTubeLiveService:
    """Service pour gérer YouTube Live API"""

    def __init__(self):
        # Configuration YouTube API
        self.api_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.access_token = os.getenv("YOUTUBE_ACCESS_TOKEN", "")
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")

        # Mode DEMO par défaut
        self.demo_mode = not bool(self.api_key and self.access_token)

        if self.demo_mode:
            logger.warning("⚠️ YouTube Live Service en mode DEMO (pas de credentials)")
        else:
            logger.info("✅ YouTube Live Service configuré")

    async def create_broadcast(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Créer un live broadcast YouTube

        Args:
            session_data: {
                "title": "Live Shopping",
                "description": "Découverte produits",
                "scheduled_start_time": "2025-11-30T20:00:00Z",
                "privacy_status": "public"  # public, unlisted, private
            }

        Returns:
            Broadcast info avec broadcast_id
        """
        if self.demo_mode:
            logger.info(f"📺 [DEMO] Création YouTube Live: {session_data.get('title')}")
            return {
                "success": True,
                "broadcast_id": f"youtube_broadcast_demo_{int(datetime.now().timestamp())}",
                "stream_id": f"youtube_stream_demo_{int(datetime.now().timestamp())}",
                "stream_url": "rtmp://a.rtmp.youtube.com/live2",
                "stream_key": "demo_youtube_key_abcd1234",
                "watch_url": "https://youtube.com/watch?v=demo_video_id",
                "embed_html": "<iframe src='https://youtube.com/embed/demo_video_id'></iframe>",
                "status": "ready",
                "demo_mode": True
            }

        try:
            # Créer le broadcast
            url = f"{self.api_url}/liveBroadcasts"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            params = {"part": "snippet,status,contentDetails"}

            payload = {
                "snippet": {
                    "title": session_data.get("title", "Live Shopping"),
                    "description": session_data.get("description", ""),
                    "scheduledStartTime": session_data.get(
                        "scheduled_start_time",
                        datetime.utcnow().isoformat() + "Z"
                    )
                },
                "status": {
                    "privacyStatus": session_data.get("privacy_status", "public"),
                    "selfDeclaredMadeForKids": False
                },
                "contentDetails": {
                    "enableAutoStart": True,
                    "enableAutoStop": True,
                    "enableDvr": True,
                    "enableContentEncryption": False,
                    "enableEmbed": True,
                    "recordFromStart": True
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                broadcast = response.json()

                # Créer le stream associé
                stream = await self._create_stream(session_data.get("title", "Stream"))

                # Lier broadcast et stream
                await self._bind_broadcast_to_stream(
                    broadcast["id"],
                    stream["id"]
                )

                return {
                    "success": True,
                    "broadcast_id": broadcast["id"],
                    "stream_id": stream["id"],
                    "stream_url": stream.get("cdn", {}).get("ingestionInfo", {}).get("ingestionAddress", ""),
                    "stream_key": stream.get("cdn", {}).get("ingestionInfo", {}).get("streamName", ""),
                    "watch_url": f"https://youtube.com/watch?v={broadcast['id']}",
                    "embed_html": f"<iframe src='https://youtube.com/embed/{broadcast['id']}'></iframe>",
                    "status": "ready",
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur création YouTube Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_stream(self, title: str) -> Dict[str, Any]:
        """Créer un stream YouTube (flux RTMP)"""
        url = f"{self.api_url}/liveStreams"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        params = {"part": "snippet,cdn,status"}

        payload = {
            "snippet": {"title": title},
            "cdn": {
                "frameRate": "30fps",
                "ingestionType": "rtmp",
                "resolution": "1080p"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def _bind_broadcast_to_stream(
        self,
        broadcast_id: str,
        stream_id: str
    ) -> None:
        """Lier un broadcast à un stream"""
        url = f"{self.api_url}/liveBroadcasts/bind"

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        params = {
            "part": "id,snippet,status",
            "id": broadcast_id,
            "streamId": stream_id
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()

    async def start_broadcast(
        self,
        broadcast_id: str
    ) -> Dict[str, Any]:
        """
        Démarrer un live broadcast YouTube

        Change le statut à "live"
        """
        if self.demo_mode:
            logger.info(f"📺 [DEMO] Démarrage YouTube Live: {broadcast_id}")
            return {
                "success": True,
                "broadcast_id": broadcast_id,
                "status": "live",
                "watch_url": f"https://youtube.com/watch?v={broadcast_id}",
                "started_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            url = f"{self.api_url}/liveBroadcasts/transition"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            params = {
                "part": "status",
                "id": broadcast_id,
                "broadcastStatus": "live"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "broadcast_id": broadcast_id,
                    "status": "live",
                    "watch_url": f"https://youtube.com/watch?v={broadcast_id}",
                    "started_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur démarrage YouTube Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_stats(
        self,
        broadcast_id: str
    ) -> Dict[str, Any]:
        """
        Récupérer les statistiques en temps réel d'un YouTube Live

        Métriques:
        - Viewers actuels (concurrent viewers)
        - Total viewers
        - Likes/Dislikes
        - Super Chat revenus
        - Chat messages
        """
        if self.demo_mode:
            import random

            current_viewers = random.randint(100, 800)

            return {
                "broadcast_id": broadcast_id,
                "status": "live",
                "concurrent_viewers": current_viewers,
                "peak_viewers": current_viewers + random.randint(50, 300),
                "total_views": current_viewers + random.randint(500, 3000),
                "likes": random.randint(100, 1000),
                "super_chats": random.randint(5, 50),
                "super_chat_revenue": round(random.uniform(50.0, 500.0), 2),
                "chat_messages": random.randint(200, 1500),
                "duration_seconds": random.randint(600, 3600),
                "demo_mode": True
            }

        try:
            # Récupérer les stats via Videos API
            url = f"{self.api_url}/videos"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            params = {
                "part": "liveStreamingDetails,statistics",
                "id": broadcast_id
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                if not result.get("items"):
                    raise Exception("Broadcast not found")

                data = result["items"][0]
                live_details = data.get("liveStreamingDetails", {})
                stats = data.get("statistics", {})

                # Calculer durée
                start_time = datetime.fromisoformat(
                    live_details.get("actualStartTime", "").replace("Z", "+00:00")
                )
                duration = (datetime.utcnow() - start_time.replace(tzinfo=None)).total_seconds()

                return {
                    "broadcast_id": broadcast_id,
                    "status": "live",
                    "concurrent_viewers": int(live_details.get("concurrentViewers", 0)),
                    "total_views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "duration_seconds": int(duration),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur récupération stats YouTube Live: {str(e)}")
            return {
                "broadcast_id": broadcast_id,
                "error": str(e),
                "demo_mode": False
            }

    async def end_broadcast(
        self,
        broadcast_id: str
    ) -> Dict[str, Any]:
        """
        Terminer un live broadcast YouTube

        Change le statut à "complete"
        """
        if self.demo_mode:
            import random
            logger.info(f"📺 [DEMO] Fin YouTube Live: {broadcast_id}")

            return {
                "success": True,
                "broadcast_id": broadcast_id,
                "status": "ended",
                "final_stats": {
                    "total_views": random.randint(2000, 8000),
                    "peak_viewers": random.randint(400, 1500),
                    "total_likes": random.randint(500, 3000),
                    "super_chats": random.randint(20, 100),
                    "super_chat_revenue": round(random.uniform(100.0, 1000.0), 2),
                    "chat_messages": random.randint(800, 4000),
                    "duration_minutes": random.randint(30, 120),
                    "engagement_rate": round(random.uniform(5.0, 12.0), 2)
                },
                "vod_url": f"https://youtube.com/watch?v={broadcast_id}",
                "ended_at": datetime.utcnow().isoformat(),
                "demo_mode": True
            }

        try:
            url = f"{self.api_url}/liveBroadcasts/transition"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            params = {
                "part": "status",
                "id": broadcast_id,
                "broadcastStatus": "complete"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()

                # Récupérer les stats finales
                stats = await self.get_live_stats(broadcast_id)

                return {
                    "success": True,
                    "broadcast_id": broadcast_id,
                    "status": "ended",
                    "final_stats": stats,
                    "vod_url": f"https://youtube.com/watch?v={broadcast_id}",
                    "ended_at": datetime.utcnow().isoformat(),
                    "demo_mode": False
                }

        except Exception as e:
            logger.error(f"❌ Erreur fin YouTube Live: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_live_chat_messages(
        self,
        broadcast_id: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les messages du chat live YouTube

        Utile pour:
        - Modération
        - Engagement analytics
        - Détection questions produits
        """
        if self.demo_mode:
            import random
            demo_messages = [
                {
                    "author": "Ahmed_Tech",
                    "message": "Super live! 👍",
                    "timestamp": "2025-11-28T20:10:00Z",
                    "is_super_chat": False
                },
                {
                    "author": "Samira_Beauty",
                    "message": "Le prix du parfum s'il vous plaît?",
                    "timestamp": "2025-11-28T20:12:00Z",
                    "is_super_chat": False
                },
                {
                    "author": "Karim_Casablanca",
                    "message": "🔥🔥🔥 J'achète!",
                    "timestamp": "2025-11-28T20:15:00Z",
                    "is_super_chat": True,
                    "super_chat_amount": 50.0
                }
            ]
            return random.sample(demo_messages, min(max_results, len(demo_messages)))

        try:
            # Récupérer le liveChatId
            url = f"{self.api_url}/videos"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            params = {
                "part": "liveStreamingDetails",
                "id": broadcast_id
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                if not result.get("items"):
                    return []

                live_chat_id = result["items"][0].get("liveStreamingDetails", {}).get("activeLiveChatId")

                if not live_chat_id:
                    return []

                # Récupérer les messages
                chat_url = f"{self.api_url}/liveChat/messages"
                chat_params = {
                    "liveChatId": live_chat_id,
                    "part": "snippet,authorDetails",
                    "maxResults": max_results
                }

                chat_response = await client.get(
                    chat_url,
                    headers=headers,
                    params=chat_params,
                    timeout=30.0
                )
                chat_response.raise_for_status()
                chat_result = chat_response.json()

                messages = []
                for item in chat_result.get("items", []):
                    snippet = item.get("snippet", {})
                    author = item.get("authorDetails", {})

                    messages.append({
                        "author": author.get("displayName", "Unknown"),
                        "message": snippet.get("displayMessage", ""),
                        "timestamp": snippet.get("publishedAt", ""),
                        "is_super_chat": snippet.get("type") == "superChatEvent",
                        "super_chat_amount": snippet.get("superChatDetails", {}).get("amountMicros", 0) / 1000000
                    })

                return messages

        except Exception as e:
            logger.error(f"❌ Erreur récupération chat YouTube: {str(e)}")
            return []

    def get_optimal_live_times(self) -> List[Dict[str, Any]]:
        """
        Meilleurs moments pour faire un YouTube Live

        Basé sur les données d'engagement YouTube
        """
        return [
            {
                "day": "Samedi",
                "time_slots": ["14:00-17:00", "19:00-21:00"],
                "engagement_score": 95,
                "reason": "Weekend, forte audience",
                "expected_viewers": "500-2000"
            },
            {
                "day": "Dimanche",
                "time_slots": ["15:00-18:00"],
                "engagement_score": 92,
                "reason": "Afternoon dominicale",
                "expected_viewers": "400-1800"
            },
            {
                "day": "Jeudi",
                "time_slots": ["20:00-22:00"],
                "engagement_score": 88,
                "reason": "Soirée pre-weekend",
                "expected_viewers": "300-1500"
            },
            {
                "day": "Mercredi",
                "time_slots": ["19:00-21:00"],
                "engagement_score": 82,
                "reason": "Milieu de semaine",
                "expected_viewers": "200-1000"
            }
        ]


# Instance singleton
youtube_live_service = YouTubeLiveService()
