"""
Instagram Graph API Service for ShareYourSales
Complete integration with Instagram for Business/Creator accounts

Dependencies:
    pip install requests

Environment Variables:
    INSTAGRAM_APP_ID: Facebook App ID
    INSTAGRAM_APP_SECRET: Facebook App Secret
    INSTAGRAM_ACCESS_TOKEN: Long-lived user access token (optional, can be obtained via OAuth)

API Documentation:
    https://developers.facebook.com/docs/instagram-api

Features:
    - OAuth 2.0 authentication
    - Publishing posts (single image, carousel, video, reels)
    - Getting insights and analytics
    - Managing comments and replies
    - Getting media details
    - Getting follower/engagement metrics
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time


logger = logging.getLogger(__name__)


class MediaType(str, Enum):
    """Instagram media types"""
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"
    REELS = "REELS"


class InsightMetric(str, Enum):
    """Available insight metrics"""
    IMPRESSIONS = "impressions"
    REACH = "reach"
    ENGAGEMENT = "engagement"
    SAVED = "saved"
    VIDEO_VIEWS = "video_views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    FOLLOWS = "follows"
    PROFILE_VIEWS = "profile_views"


@dataclass
class InstagramPost:
    """Instagram post data"""
    caption: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    media_type: MediaType = MediaType.IMAGE
    carousel_items: Optional[List[str]] = None  # URLs for carousel
    location_id: Optional[str] = None
    user_tags: Optional[List[Dict[str, Any]]] = None
    share_to_feed: bool = True  # For reels


class InstagramGraphAPI:
    """
    Instagram Graph API client

    Supports:
    - Instagram Business accounts
    - Instagram Creator accounts
    - Publishing content (posts, reels, stories)
    - Analytics and insights
    - Comment management
    - Hashtag research

    Example:
        api = InstagramGraphAPI(access_token="your_token")

        # Publish a post
        result = api.publish_photo(
            image_url="https://example.com/image.jpg",
            caption="Check out this amazing product! #affiliate"
        )

        # Get insights
        insights = api.get_media_insights(media_id="123456789")
    """

    BASE_URL = "https://graph.instagram.com"
    GRAPH_API_VERSION = "v18.0"

    def __init__(
        self,
        access_token: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None
    ):
        """
        Initialize Instagram Graph API client

        Args:
            access_token: Instagram User Access Token (long-lived)
            app_id: Facebook App ID
            app_secret: Facebook App Secret
        """
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.app_id = app_id or os.getenv("INSTAGRAM_APP_ID")
        self.app_secret = app_secret or os.getenv("INSTAGRAM_APP_SECRET")

        if not self.access_token:
            logger.warning(
                "Instagram access token not provided. "
                "Some features will require authentication."
            )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Instagram API"""
        url = f"{self.BASE_URL}/{endpoint}"

        # Add access token to params
        if params is None:
            params = {}
        if self.access_token:
            params["access_token"] = self.access_token

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            logger.error(f"Instagram API error: {error_data}")
            return {
                "success": False,
                "error": error_data.get("error", {}).get("message", str(e)),
                "error_code": error_data.get("error", {}).get("code"),
                "error_type": error_data.get("error", {}).get("type")
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== OAuth & Authentication =====

    def get_authorization_url(self, redirect_uri: str, scope: List[str] = None) -> str:
        """
        Generate Instagram OAuth authorization URL

        Args:
            redirect_uri: Callback URL for OAuth flow
            scope: List of permissions (default: basic permissions)

        Returns:
            Authorization URL to redirect user to
        """
        if not self.app_id:
            raise ValueError("app_id required for OAuth")

        if scope is None:
            scope = [
                "instagram_basic",
                "instagram_content_publish",
                "instagram_manage_comments",
                "instagram_manage_insights",
                "pages_read_engagement",
                "pages_show_list"
            ]

        auth_url = (
            f"https://www.instagram.com/oauth/authorize"
            f"?client_id={self.app_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={','.join(scope)}"
            f"&response_type=code"
        )

        return auth_url

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization

        Returns:
            Dictionary with access_token and user info
        """
        if not self.app_id or not self.app_secret:
            raise ValueError("app_id and app_secret required")

        url = "https://api.instagram.com/oauth/access_token"
        data = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code
        }

        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()

            # Exchange short-lived token for long-lived token
            long_lived = self.get_long_lived_token(token_data["access_token"])

            return {
                "success": True,
                "access_token": long_lived["access_token"],
                "token_type": long_lived.get("token_type", "bearer"),
                "expires_in": long_lived.get("expires_in"),
                "user_id": token_data.get("user_id")
            }

        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return {"success": False, "error": str(e)}

    def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """
        Exchange short-lived token (1 hour) for long-lived token (60 days)

        Args:
            short_lived_token: Short-lived access token

        Returns:
            Long-lived token data
        """
        url = f"https://graph.instagram.com/access_token"
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": self.app_secret,
            "access_token": short_lived_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Long-lived token exchange failed: {e}")
            return {"error": str(e)}

    def refresh_long_lived_token(self) -> Dict[str, Any]:
        """
        Refresh long-lived token (extends by 60 days)

        Must be called before token expires
        """
        url = f"https://graph.instagram.com/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": self.access_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            new_token_data = response.json()

            # Update current token
            self.access_token = new_token_data["access_token"]

            return {
                "success": True,
                "access_token": new_token_data["access_token"],
                "token_type": new_token_data.get("token_type"),
                "expires_in": new_token_data.get("expires_in")
            }

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== Account Info =====

    def get_user_profile(self, user_id: str = "me") -> Dict[str, Any]:
        """
        Get Instagram user profile information

        Args:
            user_id: Instagram user ID or "me" for authenticated user

        Returns:
            User profile data
        """
        fields = [
            "id", "username", "account_type", "media_count",
            "followers_count", "follows_count", "profile_picture_url",
            "biography", "website", "name"
        ]

        result = self._make_request(
            "GET",
            f"{user_id}",
            params={"fields": ",".join(fields)}
        )

        if "error" not in result:
            result["success"] = True

        return result

    # ===== Publishing Content =====

    def publish_photo(
        self,
        image_url: str,
        caption: str = "",
        location_id: Optional[str] = None,
        user_tags: Optional[List[Dict]] = None,
        ig_user_id: str = "me"
    ) -> Dict[str, Any]:
        """
        Publish a single photo to Instagram

        Args:
            image_url: Publicly accessible URL of image (JPEG, max 8MB)
            caption: Post caption (max 2200 chars)
            location_id: Facebook location ID
            user_tags: List of user tags [{"username": "user", "x": 0.5, "y": 0.5}]
            ig_user_id: Instagram business account ID

        Returns:
            Result with media_id
        """
        # Step 1: Create media container
        container_params = {
            "image_url": image_url,
            "caption": caption[:2200],  # Max length
        }

        if location_id:
            container_params["location_id"] = location_id

        if user_tags:
            container_params["user_tags"] = user_tags

        container_result = self._make_request(
            "POST",
            f"{ig_user_id}/media",
            params=container_params
        )

        if "id" not in container_result:
            return {"success": False, "error": "Failed to create container", "details": container_result}

        container_id = container_result["id"]

        # Step 2: Publish container
        time.sleep(2)  # Wait for media to be processed

        publish_result = self._make_request(
            "POST",
            f"{ig_user_id}/media_publish",
            params={"creation_id": container_id}
        )

        if "id" in publish_result:
            return {
                "success": True,
                "media_id": publish_result["id"],
                "container_id": container_id
            }
        else:
            return {"success": False, "error": "Failed to publish", "details": publish_result}

    def publish_video(
        self,
        video_url: str,
        caption: str = "",
        thumbnail_url: Optional[str] = None,
        location_id: Optional[str] = None,
        ig_user_id: str = "me"
    ) -> Dict[str, Any]:
        """
        Publish a video to Instagram

        Args:
            video_url: Publicly accessible video URL (MP4, max 100MB, 3-60s)
            caption: Post caption
            thumbnail_url: Optional thumbnail image URL
            location_id: Facebook location ID
            ig_user_id: Instagram business account ID

        Returns:
            Result with media_id
        """
        container_params = {
            "media_type": "VIDEO",
            "video_url": video_url,
            "caption": caption[:2200]
        }

        if thumbnail_url:
            container_params["thumb_offset"] = 0  # Can also use thumbnail_url

        if location_id:
            container_params["location_id"] = location_id

        container_result = self._make_request(
            "POST",
            f"{ig_user_id}/media",
            params=container_params
        )

        if "id" not in container_result:
            return {"success": False, "error": "Failed to create container", "details": container_result}

        container_id = container_result["id"]

        # Check status until video is ready
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(5)  # Wait 5 seconds between checks

            status = self._make_request("GET", container_id, params={"fields": "status_code"})

            if status.get("status_code") == "FINISHED":
                break
            elif status.get("status_code") == "ERROR":
                return {"success": False, "error": "Video processing failed", "details": status}

        # Publish container
        publish_result = self._make_request(
            "POST",
            f"{ig_user_id}/media_publish",
            params={"creation_id": container_id}
        )

        if "id" in publish_result:
            return {
                "success": True,
                "media_id": publish_result["id"],
                "container_id": container_id
            }
        else:
            return {"success": False, "error": "Failed to publish", "details": publish_result}

    def publish_carousel(
        self,
        media_urls: List[str],
        caption: str = "",
        location_id: Optional[str] = None,
        ig_user_id: str = "me"
    ) -> Dict[str, Any]:
        """
        Publish a carousel album (2-10 images/videos)

        Args:
            media_urls: List of media URLs (images/videos)
            caption: Post caption
            location_id: Facebook location ID
            ig_user_id: Instagram business account ID

        Returns:
            Result with media_id
        """
        if len(media_urls) < 2 or len(media_urls) > 10:
            return {"success": False, "error": "Carousel must have 2-10 items"}

        # Create containers for each media item
        item_ids = []
        for media_url in media_urls:
            # Determine if image or video
            is_video = media_url.lower().endswith(('.mp4', '.mov'))

            item_params = {
                "is_carousel_item": True
            }

            if is_video:
                item_params["media_type"] = "VIDEO"
                item_params["video_url"] = media_url
            else:
                item_params["image_url"] = media_url

            item_result = self._make_request(
                "POST",
                f"{ig_user_id}/media",
                params=item_params
            )

            if "id" not in item_result:
                return {"success": False, "error": f"Failed to create item: {media_url}", "details": item_result}

            item_ids.append(item_result["id"])

        # Create carousel container
        carousel_params = {
            "media_type": "CAROUSEL",
            "children": ",".join(item_ids),
            "caption": caption[:2200]
        }

        if location_id:
            carousel_params["location_id"] = location_id

        carousel_result = self._make_request(
            "POST",
            f"{ig_user_id}/media",
            params=carousel_params
        )

        if "id" not in carousel_result:
            return {"success": False, "error": "Failed to create carousel", "details": carousel_result}

        container_id = carousel_result["id"]

        # Publish carousel
        time.sleep(2)

        publish_result = self._make_request(
            "POST",
            f"{ig_user_id}/media_publish",
            params={"creation_id": container_id}
        )

        if "id" in publish_result:
            return {
                "success": True,
                "media_id": publish_result["id"],
                "container_id": container_id,
                "item_ids": item_ids
            }
        else:
            return {"success": False, "error": "Failed to publish carousel", "details": publish_result}

    # ===== Media & Insights =====

    def get_media(self, media_id: str) -> Dict[str, Any]:
        """Get media details"""
        fields = [
            "id", "media_type", "media_url", "thumbnail_url",
            "permalink", "caption", "timestamp", "username",
            "like_count", "comments_count", "is_comment_enabled"
        ]

        result = self._make_request(
            "GET",
            media_id,
            params={"fields": ",".join(fields)}
        )

        if "error" not in result:
            result["success"] = True

        return result

    def get_user_media(
        self,
        user_id: str = "me",
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Get user's media (posts)

        Args:
            user_id: Instagram user ID
            limit: Number of media to return (default 25, max 100)

        Returns:
            List of media objects
        """
        fields = [
            "id", "media_type", "media_url", "thumbnail_url",
            "permalink", "caption", "timestamp", "like_count",
            "comments_count"
        ]

        result = self._make_request(
            "GET",
            f"{user_id}/media",
            params={"fields": ",".join(fields), "limit": limit}
        )

        if "error" not in result:
            result["success"] = True

        return result

    def get_media_insights(
        self,
        media_id: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get insights for a media post

        Args:
            media_id: Media ID
            metrics: List of metrics to retrieve

        Returns:
            Insights data
        """
        if metrics is None:
            # Default metrics for posts
            metrics = ["impressions", "reach", "engagement", "saved", "likes", "comments", "shares"]

        result = self._make_request(
            "GET",
            f"{media_id}/insights",
            params={"metric": ",".join(metrics)}
        )

        if "error" not in result:
            result["success"] = True
            # Format insights into easier structure
            if "data" in result:
                formatted = {}
                for item in result["data"]:
                    formatted[item["name"]] = item["values"][0]["value"] if item.get("values") else 0
                result["insights"] = formatted

        return result

    def get_account_insights(
        self,
        user_id: str = "me",
        period: str = "day",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get account-level insights

        Args:
            user_id: Instagram user ID
            period: Time period (day, week, days_28)
            since: Start date
            until: End date

        Returns:
            Account insights
        """
        metrics = [
            "impressions", "reach", "follower_count",
            "profile_views", "website_clicks", "email_contacts"
        ]

        params = {
            "metric": ",".join(metrics),
            "period": period
        }

        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())

        result = self._make_request(
            "GET",
            f"{user_id}/insights",
            params=params
        )

        if "error" not in result:
            result["success"] = True

        return result

    # ===== Comments Management =====

    def get_comments(self, media_id: str) -> Dict[str, Any]:
        """Get comments on a media post"""
        result = self._make_request(
            "GET",
            f"{media_id}/comments",
            params={"fields": "id,username,text,timestamp,like_count"}
        )

        if "error" not in result:
            result["success"] = True

        return result

    def reply_to_comment(
        self,
        comment_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Reply to a comment"""
        result = self._make_request(
            "POST",
            f"{comment_id}/replies",
            params={"message": message}
        )

        if "id" in result:
            result["success"] = True

        return result

    def delete_comment(self, comment_id: str) -> Dict[str, Any]:
        """Delete a comment"""
        result = self._make_request("DELETE", comment_id)

        if "success" in result or "error" not in result:
            return {"success": True}
        else:
            return {"success": False, "error": result.get("error")}


# ===== Usage Example =====
if __name__ == "__main__":
    # Example usage
    api = InstagramGraphAPI()

    # Get user profile
    profile = api.get_user_profile()
    print("Profile:", profile)

    # Publish a photo
    result = api.publish_photo(
        image_url="https://example.com/product.jpg",
        caption="Check out this amazing product! 🔥 #affiliate #shareyoursales"
    )
    print("Published:", result)

    if result.get("success"):
        # Get media insights
        media_id = result["media_id"]
        time.sleep(60)  # Wait for insights to be available
        insights = api.get_media_insights(media_id)
        print("Insights:", insights)
