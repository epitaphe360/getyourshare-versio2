"""
Service de Publication Multi-Plateformes
Publie du contenu sur Instagram, Twitter, LinkedIn, Facebook, TikTok
"""

import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime

from models.media_models import (
    PlatformType,
    ScheduledPost,
    PublishResult,
    PlatformConnection
)


class MediaPublishingService:
    """
    Service de publication sur les réseaux sociaux
    Gère l'upload de médias et la publication de contenu
    """

    # ============================================
    # RATE LIMITS PAR PLATEFORME
    # ============================================

    RATE_LIMITS = {
        PlatformType.INSTAGRAM: {"posts_per_hour": 25, "posts_per_day": 200},
        PlatformType.TWITTER: {"posts_per_hour": 50, "posts_per_day": 2400},
        PlatformType.LINKEDIN: {"posts_per_hour": 20, "posts_per_day": 100},
        PlatformType.FACEBOOK: {"posts_per_hour": 50, "posts_per_day": 200},
        PlatformType.TIKTOK: {"posts_per_hour": 10, "posts_per_day": 50}
    }

    # ============================================
    # MÉTHODE PRINCIPALE DE PUBLICATION
    # ============================================

    async def publish_post(
        self,
        scheduled_post: ScheduledPost,
        platform_connection: PlatformConnection
    ) -> PublishResult:
        """
        Publie un post sur la plateforme appropriée

        Args:
            scheduled_post: Post à publier
            platform_connection: Connexion à la plateforme

        Returns:
            Résultat de la publication
        """
        platform = platform_connection.platform

        try:
            # Router vers la bonne méthode de publication
            if platform == PlatformType.INSTAGRAM:
                result = await self._publish_to_instagram(scheduled_post, platform_connection)
            elif platform == PlatformType.TWITTER:
                result = await self._publish_to_twitter(scheduled_post, platform_connection)
            elif platform == PlatformType.LINKEDIN:
                result = await self._publish_to_linkedin(scheduled_post, platform_connection)
            elif platform == PlatformType.FACEBOOK:
                result = await self._publish_to_facebook(scheduled_post, platform_connection)
            elif platform == PlatformType.TIKTOK:
                result = await self._publish_to_tiktok(scheduled_post, platform_connection)
            else:
                raise ValueError(f"Unsupported platform: {platform}")

            return result

        except Exception as e:
            return PublishResult(
                success=False,
                platform=platform,
                error_message=str(e)
            )

    # ============================================
    # INSTAGRAM
    # ============================================

    async def _publish_to_instagram(
        self,
        post: ScheduledPost,
        connection: PlatformConnection
    ) -> PublishResult:
        """Publie sur Instagram"""
        try:
            # Instagram Graph API requiert:
            # 1. Upload de média
            # 2. Création du container
            # 3. Publication du container

            account_id = connection.account_id
            access_token = connection.access_token

            # Si média présent, uploader d'abord
            media_id = None
            if post.media_urls:
                media_id = await self._upload_instagram_media(
                    post.media_urls[0],
                    access_token
                )

            # Créer le container
            container_id = await self._create_instagram_container(
                account_id=account_id,
                caption=self._format_instagram_caption(post.post_text, post.hashtags),
                media_id=media_id,
                access_token=access_token
            )

            # Publier le container
            post_id = await self._publish_instagram_container(
                account_id=account_id,
                container_id=container_id,
                access_token=access_token
            )

            return PublishResult(
                success=True,
                platform=PlatformType.INSTAGRAM,
                platform_post_id=post_id,
                platform_post_url=f"https://www.instagram.com/p/{post_id}/",
                published_at=datetime.utcnow()
            )

        except Exception as e:
            return PublishResult(
                success=False,
                platform=PlatformType.INSTAGRAM,
                error_message=f"Instagram error: {str(e)}"
            )

    async def _upload_instagram_media(
        self,
        media_url: str,
        access_token: str
    ) -> str:
        """Upload un média sur Instagram"""
        # Simplified mock - dans la vraie implémentation:
        # POST https://graph.facebook.com/v18.0/{ig-user-id}/media
        return "mock_media_id"

    async def _create_instagram_container(
        self,
        account_id: str,
        caption: str,
        media_id: Optional[str],
        access_token: str
    ) -> str:
        """Crée un container Instagram"""
        # Mock - vraie implémentation utiliserait Graph API
        return "mock_container_id"

    async def _publish_instagram_container(
        self,
        account_id: str,
        container_id: str,
        access_token: str
    ) -> str:
        """Publie un container Instagram"""
        # Mock - vraie implémentation publierait le container
        return "mock_post_id"

    def _format_instagram_caption(self, text: str, hashtags: list) -> str:
        """Formate la caption Instagram"""
        caption = text
        if hashtags:
            caption += "\n\n" + " ".join(hashtags)
        return caption[:2200]  # Max length

    # ============================================
    # TWITTER/X
    # ============================================

    async def _publish_to_twitter(
        self,
        post: ScheduledPost,
        connection: PlatformConnection
    ) -> PublishResult:
        """Publie sur Twitter/X"""
        try:
            access_token = connection.access_token

            # Formater le tweet
            tweet_text = self._format_twitter_text(post.post_text, post.hashtags)

            # API v2 endpoint
            url = "https://api.twitter.com/2/tweets"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {"text": tweet_text}

            # Si média, uploader d'abord
            if post.media_urls:
                media_ids = await self._upload_twitter_media(post.media_urls, access_token)
                if media_ids:
                    payload["media"] = {"media_ids": media_ids}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 201:
                        data = await response.json()
                        tweet_id = data["data"]["id"]

                        return PublishResult(
                            success=True,
                            platform=PlatformType.TWITTER,
                            platform_post_id=tweet_id,
                            platform_post_url=f"https://twitter.com/i/web/status/{tweet_id}",
                            published_at=datetime.utcnow()
                        )
                    else:
                        error = await response.text()
                        raise Exception(f"Twitter API error: {error}")

        except Exception as e:
            return PublishResult(
                success=False,
                platform=PlatformType.TWITTER,
                error_message=f"Twitter error: {str(e)}"
            )

    async def _upload_twitter_media(
        self,
        media_urls: list,
        access_token: str
    ) -> list:
        """Upload des médias sur Twitter"""
        # Mock - vraie implémentation utiliserait media upload API
        return ["mock_media_id"]

    def _format_twitter_text(self, text: str, hashtags: list) -> str:
        """Formate le texte du tweet"""
        tweet = text
        if hashtags:
            # Ajouter hashtags si ça rentre dans 280 caractères
            hashtags_text = " ".join(hashtags[:2])
            if len(tweet) + len(hashtags_text) + 2 <= 280:
                tweet += " " + hashtags_text

        return tweet[:280]

    # ============================================
    # LINKEDIN
    # ============================================

    async def _publish_to_linkedin(
        self,
        post: ScheduledPost,
        connection: PlatformConnection
    ) -> PublishResult:
        """Publie sur LinkedIn"""
        try:
            access_token = connection.access_token
            account_id = connection.account_id

            # LinkedIn API endpoint
            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Formater le post
            post_text = self._format_linkedin_text(post.post_text, post.hashtags)

            payload = {
                "author": f"urn:li:person:{account_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post_text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 201:
                        data = await response.json()
                        post_id = data.get("id", "").split(":")[-1]

                        return PublishResult(
                            success=True,
                            platform=PlatformType.LINKEDIN,
                            platform_post_id=post_id,
                            platform_post_url=f"https://www.linkedin.com/feed/update/{post_id}/",
                            published_at=datetime.utcnow()
                        )
                    else:
                        error = await response.text()
                        raise Exception(f"LinkedIn API error: {error}")

        except Exception as e:
            return PublishResult(
                success=False,
                platform=PlatformType.LINKEDIN,
                error_message=f"LinkedIn error: {str(e)}"
            )

    def _format_linkedin_text(self, text: str, hashtags: list) -> str:
        """Formate le texte LinkedIn"""
        post_text = text
        if hashtags:
            post_text += "\n\n" + " ".join(hashtags[:3])
        return post_text[:3000]

    # ============================================
    # FACEBOOK
    # ============================================

    async def _publish_to_facebook(
        self,
        post: ScheduledPost,
        connection: PlatformConnection
    ) -> PublishResult:
        """Publie sur Facebook"""
        try:
            access_token = connection.access_token
            page_id = connection.metadata.get("page_id")

            # Facebook Graph API
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"

            # Formater le post
            message = self._format_facebook_text(post.post_text, post.hashtags)

            params = {
                "message": message,
                "access_token": access_token
            }

            # Si média
            if post.media_urls:
                params["link"] = post.media_urls[0]

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        post_id = data.get("id")

                        return PublishResult(
                            success=True,
                            platform=PlatformType.FACEBOOK,
                            platform_post_id=post_id,
                            platform_post_url=f"https://www.facebook.com/{post_id}",
                            published_at=datetime.utcnow()
                        )
                    else:
                        error = await response.text()
                        raise Exception(f"Facebook API error: {error}")

        except Exception as e:
            return PublishResult(
                success=False,
                platform=PlatformType.FACEBOOK,
                error_message=f"Facebook error: {str(e)}"
            )

    def _format_facebook_text(self, text: str, hashtags: list) -> str:
        """Formate le texte Facebook"""
        message = text
        if hashtags:
            message += "\n\n" + " ".join(hashtags)
        return message

    # ============================================
    # TIKTOK
    # ============================================

    async def _publish_to_tiktok(
        self,
        post: ScheduledPost,
        connection: PlatformConnection
    ) -> PublishResult:
        """Publie sur TikTok"""
        try:
            # TikTok nécessite un upload de vidéo complexe
            # Cette implémentation est simplifiée

            access_token = connection.access_token

            # TikTok Content Posting API
            url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "post_info": {
                    "title": post.post_text[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE"
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_url": post.media_urls[0] if post.media_urls else ""
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        publish_id = data.get("data", {}).get("publish_id")

                        return PublishResult(
                            success=True,
                            platform=PlatformType.TIKTOK,
                            platform_post_id=publish_id,
                            platform_post_url=f"https://www.tiktok.com/@{connection.account_name}",
                            published_at=datetime.utcnow()
                        )
                    else:
                        error = await response.text()
                        raise Exception(f"TikTok API error: {error}")

        except Exception as e:
            return PublishResult(
                success=False,
                platform=PlatformType.TIKTOK,
                error_message=f"TikTok error: {str(e)}"
            )

    # ============================================
    # HELPERS
    # ============================================

    async def check_rate_limit(
        self,
        user_id: int,
        platform: PlatformType
    ) -> bool:
        """Vérifie si l'utilisateur n'a pas dépassé les rate limits"""
        # Dans la vraie app:
        # - Compter les publications de l'utilisateur dans la dernière heure/jour
        # - Comparer avec les limites
        # - Retourner False si limite atteinte

        return True

    async def validate_content(
        self,
        post: ScheduledPost,
        platform: PlatformType
    ) -> Dict[str, Any]:
        """Valide que le contenu respecte les contraintes de la plateforme"""
        errors = []

        # Vérifier la longueur du texte
        max_length = {
            PlatformType.INSTAGRAM: 2200,
            PlatformType.TWITTER: 280,
            PlatformType.LINKEDIN: 3000,
            PlatformType.FACEBOOK: 63206,
            PlatformType.TIKTOK: 2200
        }

        if len(post.post_text) > max_length[platform]:
            errors.append(f"Text too long (max {max_length[platform]} characters)")

        # Vérifier les médias
        if platform == PlatformType.TIKTOK and not post.media_urls:
            errors.append("TikTok requires video content")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
