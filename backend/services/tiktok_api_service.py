"""
TikTok Creator API Service for ShareYourSales
Complete integration with TikTok for Business/Creator accounts

Dependencies:
    pip install requests

Environment Variables:
    TIKTOK_CLIENT_KEY: TikTok App Client Key
    TIKTOK_CLIENT_SECRET: TikTok App Client Secret
    TIKTOK_ACCESS_TOKEN: User access token (obtained via OAuth)

API Documentation:
    https://developers.tiktok.com/doc/content-posting-api-get-started

Features:
    - OAuth 2.0 authentication
    - Upload videos
    - Get video details and analytics
    - Comment management
    - User profile data
    - Video insights and metrics
"""

import os
import requests
import logging
import time
import hashlib
import hmac
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class VideoPrivacyLevel(str, Enum):
    """TikTok video privacy settings"""
    PUBLIC = "PUBLIC_TO_EVERYONE"
    FRIENDS = "MUTUAL_FOLLOW_FRIENDS"
    PRIVATE = "SELF_ONLY"


class VideoContentCategory(str, Enum):
    """Video content categories"""
    BEAUTY = "Beauty & Style"
    EDUCATION = "Education"
    ENTERTAINMENT = "Entertainment"
    FAMILY = "Family & Parenting"
    FITNESS = "Fitness & Health"
    FOOD = "Food & Drink"
    GAMING = "Gaming"
    LIFESTYLE = "Lifestyle"
    MUSIC = "Music"
    SPORTS = "Sports"
    TECHNOLOGY = "Technology"
    TRAVEL = "Travel"


@dataclass
class TikTokVideo:
    """TikTok video upload data"""
    video_path: str  # Path to video file or URL
    title: str
    description: Optional[str] = None
    privacy_level: VideoPrivacyLevel = VideoPrivacyLevel.PUBLIC
    disable_duet: bool = False
    disable_stitch: bool = False
    disable_comment: bool = False
    brand_content: bool = False  # Brand/sponsored content
    brand_organic: bool = False  # Organic brand content


class TikTokCreatorAPI:
    """
    TikTok Creator API client

    Supports:
    - OAuth authentication
    - Video uploading
    - Video analytics
    - User profile data
    - Comment management
    - Hashtag research

    Example:
        api = TikTokCreatorAPI(access_token="your_token")

        # Upload video
        result = api.upload_video(
            video_path="/path/to/video.mp4",
            title="Check out this product!",
            description="#affiliate #product"
        )

        # Get video analytics
        analytics = api.get_video_analytics(video_id="123456")
    """

    BASE_URL = "https://open.tiktokapis.com"
    OAUTH_URL = "https://www.tiktok.com/v2/auth/authorize"
    TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

    def __init__(
        self,
        access_token: Optional[str] = None,
        client_key: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        """
        Initialize TikTok Creator API client

        Args:
            access_token: TikTok user access token
            client_key: TikTok app client key
            client_secret: TikTok app client secret
        """
        self.access_token = access_token or os.getenv("TIKTOK_ACCESS_TOKEN")
        self.client_key = client_key or os.getenv("TIKTOK_CLIENT_KEY")
        self.client_secret = client_secret or os.getenv("TIKTOK_CLIENT_SECRET")

        if not self.access_token:
            logger.warning(
                "TikTok access token not provided. "
                "Authentication required for most features."
            )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to TikTok API"""
        url = f"{self.BASE_URL}{endpoint}"

        if headers is None:
            headers = {}

        # Add authorization header
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        headers["Content-Type"] = "application/json"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == "POST":
                if files:
                    # Remove Content-Type for file upload
                    headers.pop("Content-Type", None)
                    response = requests.post(url, headers=headers, params=params, files=files, timeout=120)
                else:
                    response = requests.post(url, headers=headers, params=params, json=json_data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            logger.error(f"TikTok API error: {error_data}")
            return {
                "success": False,
                "error": error_data.get("error", {}).get("message", str(e)),
                "error_code": error_data.get("error", {}).get("code"),
                "error_description": error_data.get("error_description")
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== OAuth & Authentication =====

    def get_authorization_url(
        self,
        redirect_uri: str,
        scope: Optional[List[str]] = None,
        state: Optional[str] = None
    ) -> str:
        """
        Generate TikTok OAuth authorization URL

        Args:
            redirect_uri: Callback URL for OAuth flow
            scope: List of permissions
            state: CSRF protection state parameter

        Returns:
            Authorization URL
        """
        if not self.client_key:
            raise ValueError("client_key required for OAuth")

        if scope is None:
            scope = [
                "user.info.basic",
                "user.info.profile",
                "user.info.stats",
                "video.list",
                "video.upload",
                "video.publish"
            ]

        params = {
            "client_key": self.client_key,
            "scope": ",".join(scope),
            "response_type": "code",
            "redirect_uri": redirect_uri
        }

        if state:
            params["state"] = state

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.OAUTH_URL}?{query_string}"

    def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization

        Returns:
            Token data
        """
        if not self.client_key or not self.client_secret:
            raise ValueError("client_key and client_secret required")

        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        try:
            response = requests.post(self.TOKEN_URL, json=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()

            if "access_token" in token_data:
                self.access_token = token_data["access_token"]
                return {
                    "success": True,
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in"),
                    "token_type": token_data.get("token_type", "bearer"),
                    "scope": token_data.get("scope")
                }
            else:
                return {"success": False, "error": token_data}

        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return {"success": False, "error": str(e)}

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token from previous authentication

        Returns:
            New token data
        """
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        try:
            response = requests.post(self.TOKEN_URL, json=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()

            if "access_token" in token_data:
                self.access_token = token_data["access_token"]
                return {
                    "success": True,
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in")
                }
            else:
                return {"success": False, "error": token_data}

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== User Info =====

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user's profile information

        Returns:
            User profile data
        """
        result = self._make_request(
            "GET",
            "/v2/user/info/",
            params={"fields": "open_id,union_id,avatar_url,display_name,bio_description,profile_deep_link,is_verified,follower_count,following_count,likes_count,video_count"}
        )

        if "data" in result:
            result["success"] = True
            result["user"] = result["data"]["user"]

        return result

    # ===== Video Upload & Publishing =====

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        privacy_level: VideoPrivacyLevel = VideoPrivacyLevel.PUBLIC,
        disable_comment: bool = False,
        disable_duet: bool = False,
        disable_stitch: bool = False,
        brand_content: bool = False
    ) -> Dict[str, Any]:
        """
        Upload and publish a video to TikTok

        Args:
            video_path: Local path to video file
            title: Video title (max 150 chars)
            description: Video description/caption (max 2200 chars)
            privacy_level: Privacy setting
            disable_comment: Disable comments
            disable_duet: Disable duets
            disable_stitch: Disable stitches
            brand_content: Mark as branded content

        Returns:
            Upload result with video ID
        """
        # Step 1: Initialize upload
        init_data = {
            "post_info": {
                "title": title[:150],
                "description": description[:2200],
                "privacy_level": privacy_level.value,
                "disable_comment": disable_comment,
                "disable_duet": disable_duet,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": 1000  # Cover frame at 1 second
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": os.path.getsize(video_path),
                "chunk_size": 10 * 1024 * 1024,  # 10MB chunks
                "total_chunk_count": 1
            }
        }

        if brand_content:
            init_data["post_info"]["brand_content_toggle"] = True
            init_data["post_info"]["brand_organic_toggle"] = False

        init_result = self._make_request(
            "POST",
            "/v2/post/publish/video/init/",
            json_data=init_data
        )

        if "data" not in init_result:
            return {"success": False, "error": "Upload initialization failed", "details": init_result}

        upload_url = init_result["data"]["upload_url"]
        publish_id = init_result["data"]["publish_id"]

        # Step 2: Upload video file
        try:
            with open(video_path, "rb") as video_file:
                upload_response = requests.put(
                    upload_url,
                    data=video_file,
                    headers={"Content-Type": "video/mp4"},
                    timeout=300  # 5 minutes for upload
                )
                upload_response.raise_for_status()

        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            return {"success": False, "error": f"File upload failed: {e}"}

        # Step 3: Check publish status
        max_attempts = 60  # 5 minutes max
        for attempt in range(max_attempts):
            time.sleep(5)

            status_result = self._make_request(
                "POST",
                "/v2/post/publish/status/fetch/",
                json_data={"publish_id": publish_id}
            )

            if "data" in status_result:
                status = status_result["data"]["status"]

                if status == "PUBLISH_COMPLETE":
                    return {
                        "success": True,
                        "video_id": status_result["data"].get("video_id"),
                        "publish_id": publish_id,
                        "status": "published"
                    }
                elif status == "FAILED":
                    return {
                        "success": False,
                        "error": "Publishing failed",
                        "fail_reason": status_result["data"].get("fail_reason")
                    }

        return {"success": False, "error": "Publishing timeout"}

    def upload_video_from_url(
        self,
        video_url: str,
        title: str,
        description: str = "",
        privacy_level: VideoPrivacyLevel = VideoPrivacyLevel.PUBLIC
    ) -> Dict[str, Any]:
        """
        Upload video from public URL

        Args:
            video_url: Public URL to video file
            title: Video title
            description: Video description
            privacy_level: Privacy setting

        Returns:
            Upload result
        """
        init_data = {
            "post_info": {
                "title": title[:150],
                "description": description[:2200],
                "privacy_level": privacy_level.value
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url
            }
        }

        result = self._make_request(
            "POST",
            "/v2/post/publish/video/init/",
            json_data=init_data
        )

        if "data" in result:
            return {
                "success": True,
                "publish_id": result["data"]["publish_id"]
            }
        else:
            return {"success": False, "error": "Upload from URL failed", "details": result}

    # ===== Video Management =====

    def get_video_list(
        self,
        max_count: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of user's videos

        Args:
            max_count: Number of videos to return (max 20)
            cursor: Pagination cursor

        Returns:
            List of videos
        """
        params = {"max_count": min(max_count, 20)}

        if cursor:
            params["cursor"] = cursor

        result = self._make_request(
            "POST",
            "/v2/video/list/",
            params={"fields": "id,create_time,cover_image_url,share_url,video_description,duration,height,width,title,embed_html,embed_link,like_count,comment_count,share_count,view_count"},
            json_data=params
        )

        if "data" in result:
            result["success"] = True
            result["videos"] = result["data"].get("videos", [])
            result["has_more"] = result["data"].get("has_more", False)
            result["cursor"] = result["data"].get("cursor")

        return result

    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Get details for a specific video

        Args:
            video_id: TikTok video ID

        Returns:
            Video details
        """
        result = self._make_request(
            "POST",
            "/v2/video/query/",
            params={"fields": "id,create_time,cover_image_url,share_url,video_description,duration,height,width,title,embed_html,embed_link,like_count,comment_count,share_count,view_count"},
            json_data={"filters": {"video_ids": [video_id]}}
        )

        if "data" in result and "videos" in result["data"] and len(result["data"]["videos"]) > 0:
            result["success"] = True
            result["video"] = result["data"]["videos"][0]

        return result

    # ===== Analytics & Insights =====

    def get_video_analytics(
        self,
        video_id: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for a video

        Args:
            video_id: Video ID
            metrics: List of metrics to retrieve

        Returns:
            Video analytics data
        """
        if metrics is None:
            metrics = [
                "VIEWS",
                "LIKES",
                "COMMENTS",
                "SHARES",
                "REACH",
                "FULL_VIDEO_WATCHED_RATE",
                "AVERAGE_TIME_WATCHED"
            ]

        # Note: Analytics API may require special permissions
        result = self._make_request(
            "POST",
            "/v2/research/video/query/",
            json_data={
                "filters": {"video_ids": [video_id]},
                "fields": metrics
            }
        )

        if "data" in result:
            result["success"] = True

        return result

    # ===== Comment Management =====

    def get_comments(
        self,
        video_id: str,
        max_count: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comments on a video

        Args:
            video_id: Video ID
            max_count: Number of comments to return
            cursor: Pagination cursor

        Returns:
            List of comments
        """
        params = {
            "video_id": video_id,
            "max_count": min(max_count, 50)
        }

        if cursor:
            params["cursor"] = cursor

        result = self._make_request(
            "GET",
            "/v2/comment/list/",
            params=params
        )

        if "data" in result:
            result["success"] = True
            result["comments"] = result["data"].get("comments", [])

        return result

    def reply_to_comment(
        self,
        video_id: str,
        comment_id: str,
        reply_text: str
    ) -> Dict[str, Any]:
        """
        Reply to a comment

        Args:
            video_id: Video ID
            comment_id: Comment ID to reply to
            reply_text: Reply text

        Returns:
            Reply result
        """
        result = self._make_request(
            "POST",
            "/v2/comment/reply/",
            json_data={
                "video_id": video_id,
                "comment_id": comment_id,
                "text": reply_text
            }
        )

        if "data" in result:
            result["success"] = True

        return result


# ===== Usage Example =====
if __name__ == "__main__":
    # Example usage
    api = TikTokCreatorAPI()

    # Get user info
    user_info = api.get_user_info()
    print("User info:", user_info)

    # Upload video
    result = api.upload_video(
        video_path="/path/to/video.mp4",
        title="Amazing product review!",
        description="Check out this product I'm promoting! #affiliate #shareyoursales",
        privacy_level=VideoPrivacyLevel.PUBLIC
    )
    print("Upload result:", result)

    if result.get("success"):
        video_id = result["video_id"]

        # Get video analytics
        analytics = api.get_video_analytics(video_id)
        print("Analytics:", analytics)
