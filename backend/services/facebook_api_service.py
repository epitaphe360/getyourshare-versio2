"""
Facebook Graph API Service for ShareYourSales
Complete integration with Facebook Pages and user profiles

Dependencies:
    pip install requests

Environment Variables:
    FACEBOOK_APP_ID: Facebook App ID
    FACEBOOK_APP_SECRET: Facebook App Secret
    FACEBOOK_ACCESS_TOKEN: User/Page access token

API Documentation:
    https://developers.facebook.com/docs/graph-api

Features:
    - OAuth authentication
    - Publish posts (text, images, videos, links)
    - Page management
    - Post insights and analytics
    - Comment management
    - Audience insights
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class PostType(str, Enum):
    """Facebook post types"""
    STATUS = "status"
    PHOTO = "photo"
    VIDEO = "video"
    LINK = "link"


class InsightPeriod(str, Enum):
    """Insight time periods"""
    DAY = "day"
    WEEK = "week"
    DAYS_28 = "days_28"
    LIFETIME = "lifetime"


@dataclass
class FacebookPost:
    """Facebook post data"""
    message: str
    link: Optional[str] = None
    photo_url: Optional[str] = None
    video_url: Optional[str] = None
    scheduled_publish_time: Optional[datetime] = None
    published: bool = True


class FacebookGraphAPI:
    """
    Facebook Graph API client

    Supports:
    - Facebook Pages
    - User profiles (limited)
    - Publishing content
    - Analytics and insights
    - Comment management

    Example:
        api = FacebookGraphAPI(access_token="your_token")

        # Publish to page
        result = api.publish_post(
            page_id="123456789",
            message="Check out this product!",
            link="https://example.com/product"
        )

        # Get page insights
        insights = api.get_page_insights(page_id="123456789")
    """

    BASE_URL = "https://graph.facebook.com"
    API_VERSION = "v18.0"

    def __init__(
        self,
        access_token: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None
    ):
        """
        Initialize Facebook Graph API client

        Args:
            access_token: Facebook user/page access token
            app_id: Facebook App ID
            app_secret: Facebook App Secret
        """
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET")

        if not self.access_token:
            logger.warning("Facebook access token not provided")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Facebook Graph API"""
        url = f"{self.BASE_URL}/{self.API_VERSION}/{endpoint}"

        # Add access token
        if params is None:
            params = {}
        if self.access_token:
            params["access_token"] = self.access_token

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, params=params, data=data, files=files, timeout=120)
                else:
                    response = requests.post(url, params=params, data=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            logger.error(f"Facebook API error: {error_data}")
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

    def get_authorization_url(
        self,
        redirect_uri: str,
        scope: Optional[List[str]] = None,
        state: Optional[str] = None
    ) -> str:
        """
        Generate Facebook OAuth authorization URL

        Args:
            redirect_uri: Callback URL
            scope: List of permissions
            state: CSRF protection state

        Returns:
            Authorization URL
        """
        if not self.app_id:
            raise ValueError("app_id required for OAuth")

        if scope is None:
            scope = [
                "public_profile",
                "email",
                "pages_show_list",
                "pages_read_engagement",
                "pages_manage_posts",
                "pages_manage_engagement",
                "pages_read_user_content",
                "read_insights",
                "publish_to_groups"
            ]

        auth_url = (
            f"https://www.facebook.com/{self.API_VERSION}/dialog/oauth"
            f"?client_id={self.app_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={','.join(scope)}"
            f"&response_type=code"
        )

        if state:
            auth_url += f"&state={state}"

        return auth_url

    def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code
            redirect_uri: Same redirect URI from authorization

        Returns:
            Token data
        """
        if not self.app_id or not self.app_secret:
            raise ValueError("app_id and app_secret required")

        url = f"{self.BASE_URL}/{self.API_VERSION}/oauth/access_token"
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            token_data = response.json()

            # Exchange for long-lived token
            if "access_token" in token_data:
                long_lived = self.get_long_lived_token(token_data["access_token"])
                return {
                    "success": True,
                    "access_token": long_lived.get("access_token", token_data["access_token"]),
                    "token_type": "bearer",
                    "expires_in": long_lived.get("expires_in")
                }
            else:
                return {"success": False, "error": "No access token in response"}

        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return {"success": False, "error": str(e)}

    def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """
        Exchange short-lived token (1-2 hours) for long-lived token (60 days)

        Args:
            short_lived_token: Short-lived access token

        Returns:
            Long-lived token data
        """
        url = f"{self.BASE_URL}/{self.API_VERSION}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": short_lived_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Long-lived token exchange failed: {e}")
            return {"error": str(e)}

    # ===== User & Page Info =====

    def get_user_info(self, user_id: str = "me") -> Dict[str, Any]:
        """Get user profile information"""
        fields = ["id", "name", "email", "picture"]

        result = self._make_request(
            "GET",
            user_id,
            params={"fields": ",".join(fields)}
        )

        if "error" not in result:
            result["success"] = True

        return result

    def get_user_pages(self, user_id: str = "me") -> Dict[str, Any]:
        """Get list of pages managed by user"""
        result = self._make_request(
            "GET",
            f"{user_id}/accounts",
            params={"fields": "id,name,access_token,category,fan_count,picture"}
        )

        if "data" in result:
            result["success"] = True
            result["pages"] = result["data"]

        return result

    def get_page_info(self, page_id: str) -> Dict[str, Any]:
        """Get page information"""
        fields = [
            "id", "name", "username", "category", "fan_count",
            "picture", "cover", "about", "website", "phone",
            "engagement", "link"
        ]

        result = self._make_request(
            "GET",
            page_id,
            params={"fields": ",".join(fields)}
        )

        if "error" not in result:
            result["success"] = True

        return result

    # ===== Publishing =====

    def publish_post(
        self,
        page_id: str,
        message: str,
        link: Optional[str] = None,
        published: bool = True,
        scheduled_publish_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Publish a text/link post to a page

        Args:
            page_id: Facebook Page ID
            message: Post message/caption
            link: Optional URL to share
            published: Publish immediately (True) or save as draft (False)
            scheduled_publish_time: Schedule for future

        Returns:
            Post result with post_id
        """
        data = {"message": message}

        if link:
            data["link"] = link

        if not published:
            data["published"] = "false"
        elif scheduled_publish_time:
            data["published"] = "false"
            data["scheduled_publish_time"] = int(scheduled_publish_time.timestamp())

        result = self._make_request(
            "POST",
            f"{page_id}/feed",
            data=data
        )

        if "id" in result:
            result["success"] = True
            result["post_id"] = result["id"]

        return result

    def publish_photo(
        self,
        page_id: str,
        image_url: str,
        caption: str = "",
        published: bool = True
    ) -> Dict[str, Any]:
        """
        Publish a photo to a page

        Args:
            page_id: Facebook Page ID
            image_url: Public URL to image
            caption: Photo caption
            published: Publish immediately

        Returns:
            Post result
        """
        data = {
            "url": image_url,
            "caption": caption,
            "published": "true" if published else "false"
        }

        result = self._make_request(
            "POST",
            f"{page_id}/photos",
            data=data
        )

        if "id" in result:
            result["success"] = True
            result["photo_id"] = result["id"]
            result["post_id"] = result.get("post_id")

        return result

    def publish_video(
        self,
        page_id: str,
        video_url: str,
        description: str = "",
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a video to a page

        Args:
            page_id: Facebook Page ID
            video_url: Public URL to video file
            description: Video description
            title: Video title

        Returns:
            Post result
        """
        data = {
            "file_url": video_url,
            "description": description
        }

        if title:
            data["title"] = title

        result = self._make_request(
            "POST",
            f"{page_id}/videos",
            data=data
        )

        if "id" in result:
            result["success"] = True
            result["video_id"] = result["id"]

        return result

    # ===== Post Management =====

    def get_page_posts(
        self,
        page_id: str,
        limit: int = 25,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get posts from a page"""
        fields = [
            "id", "message", "created_time", "permalink_url",
            "shares", "story", "type", "status_type",
            "is_published"
        ]

        params = {
            "fields": ",".join(fields),
            "limit": limit
        }

        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())

        result = self._make_request(
            "GET",
            f"{page_id}/posts",
            params=params
        )

        if "data" in result:
            result["success"] = True
            result["posts"] = result["data"]

        return result

    def get_post_details(self, post_id: str) -> Dict[str, Any]:
        """Get details for a specific post"""
        fields = [
            "id", "message", "created_time", "updated_time",
            "permalink_url", "shares", "reactions", "comments"
        ]

        result = self._make_request(
            "GET",
            post_id,
            params={"fields": ",".join(fields)}
        )

        if "error" not in result:
            result["success"] = True

        return result

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a post"""
        result = self._make_request("DELETE", post_id)

        if "success" in result or "error" not in result:
            return {"success": True}
        else:
            return {"success": False, "error": result.get("error")}

    # ===== Insights & Analytics =====

    def get_post_insights(
        self,
        post_id: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get insights for a post

        Args:
            post_id: Post ID
            metrics: List of metrics to retrieve

        Returns:
            Post insights
        """
        if metrics is None:
            metrics = [
                "post_impressions",
                "post_impressions_unique",
                "post_impressions_paid",
                "post_impressions_organic",
                "post_engaged_users",
                "post_clicks",
                "post_reactions_like_total",
                "post_reactions_love_total",
                "post_reactions_wow_total"
            ]

        result = self._make_request(
            "GET",
            f"{post_id}/insights",
            params={"metric": ",".join(metrics)}
        )

        if "data" in result:
            result["success"] = True
            # Format insights
            formatted = {}
            for item in result["data"]:
                formatted[item["name"]] = item["values"][0]["value"] if item.get("values") else 0
            result["insights"] = formatted

        return result

    def get_page_insights(
        self,
        page_id: str,
        metrics: Optional[List[str]] = None,
        period: InsightPeriod = InsightPeriod.DAY,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get page-level insights

        Args:
            page_id: Page ID
            metrics: List of metrics
            period: Time period
            since: Start date
            until: End date

        Returns:
            Page insights
        """
        if metrics is None:
            metrics = [
                "page_impressions",
                "page_impressions_unique",
                "page_engaged_users",
                "page_post_engagements",
                "page_fans",
                "page_fan_adds",
                "page_views_total",
                "page_video_views"
            ]

        params = {
            "metric": ",".join(metrics),
            "period": period.value
        }

        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())

        result = self._make_request(
            "GET",
            f"{page_id}/insights",
            params=params
        )

        if "data" in result:
            result["success"] = True

        return result

    # ===== Comments Management =====

    def get_post_comments(
        self,
        post_id: str,
        limit: int = 25
    ) -> Dict[str, Any]:
        """Get comments on a post"""
        result = self._make_request(
            "GET",
            f"{post_id}/comments",
            params={
                "fields": "id,from,message,created_time,like_count,comment_count",
                "limit": limit
            }
        )

        if "data" in result:
            result["success"] = True
            result["comments"] = result["data"]

        return result

    def reply_to_comment(
        self,
        comment_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Reply to a comment"""
        result = self._make_request(
            "POST",
            f"{comment_id}/comments",
            data={"message": message}
        )

        if "id" in result:
            result["success"] = True
            result["comment_id"] = result["id"]

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
    api = FacebookGraphAPI()

    # Get user pages
    pages = api.get_user_pages()
    print("Pages:", pages)

    if pages.get("success") and len(pages.get("pages", [])) > 0:
        page_id = pages["pages"][0]["id"]

        # Publish post
        result = api.publish_post(
            page_id=page_id,
            message="Check out this amazing product! 🔥",
            link="https://example.com/product"
        )
        print("Published:", result)

        # Get page insights
        insights = api.get_page_insights(page_id)
        print("Insights:", insights)
