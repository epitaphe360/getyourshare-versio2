"""
Twitter API v2 Service for ShareYourSales
Complete integration with Twitter/X for affiliate marketing

Dependencies:
    pip install requests requests-oauthlib

Environment Variables:
    TWITTER_API_KEY: Twitter API Key (Consumer Key)
    TWITTER_API_SECRET: Twitter API Secret (Consumer Secret)
    TWITTER_ACCESS_TOKEN: User Access Token
    TWITTER_ACCESS_TOKEN_SECRET: User Access Token Secret
    TWITTER_BEARER_TOKEN: App-only Bearer Token (optional)

API Documentation:
    https://developer.twitter.com/en/docs/twitter-api

Features:
    - OAuth 1.0a and OAuth 2.0 authentication
    - Tweet creation (text, images, videos)
    - Thread creation
    - Tweet analytics
    - User timeline
    - Search tweets
    - Manage followers
"""

import os
import requests
import logging
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from requests_oauthlib import OAuth1
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    logging.warning("requests-oauthlib not installed. Run: pip install requests-oauthlib")


logger = logging.getLogger(__name__)


class TweetReplySettings(str, Enum):
    """Who can reply to a tweet"""
    EVERYONE = "everyone"
    MENTIONED_USERS = "mentionedUsers"
    FOLLOWING = "following"


@dataclass
class Tweet:
    """Tweet data structure"""
    text: str
    media_ids: Optional[List[str]] = None
    reply_settings: TweetReplySettings = TweetReplySettings.EVERYONE
    quote_tweet_id: Optional[str] = None
    poll_options: Optional[List[str]] = None
    poll_duration_minutes: int = 1440  # 24 hours


class TwitterAPIv2:
    """
    Twitter API v2 client

    Supports:
    - Creating tweets
    - Uploading media
    - Tweet analytics
    - User management
    - Search and timeline

    Example:
        api = TwitterAPIv2(
            api_key="your_key",
            api_secret="your_secret",
            access_token="your_token",
            access_token_secret="your_token_secret"
        )

        # Create tweet
        result = api.create_tweet(
            text="Check out this amazing product! #affiliate",
            media_urls=["https://example.com/image.jpg"]
        )

        # Get tweet analytics
        analytics = api.get_tweet_metrics(tweet_id="123456")
    """

    BASE_URL = "https://api.twitter.com/2"
    UPLOAD_URL = "https://upload.twitter.com/1.1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None
    ):
        """
        Initialize Twitter API client

        Args:
            api_key: Twitter API Key (Consumer Key)
            api_secret: Twitter API Secret (Consumer Secret)
            access_token: User Access Token
            access_token_secret: User Access Token Secret
            bearer_token: App-only Bearer Token
        """
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")

        # Initialize OAuth1 for user context
        if self.api_key and self.api_secret and self.access_token and self.access_token_secret:
            if not OAUTH_AVAILABLE:
                raise ImportError("requests-oauthlib required. Run: pip install requests-oauthlib")
            self.oauth = OAuth1(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )
        else:
            self.oauth = None
            logger.warning("OAuth credentials not complete. User-context endpoints will not work.")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        auth_type: str = "oauth1",  # "oauth1" or "bearer"
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Twitter API"""
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = f"{self.BASE_URL}/{endpoint}"

        headers = {}

        # Choose authentication method
        if auth_type == "bearer" and self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
            auth = None
        elif auth_type == "oauth1" and self.oauth:
            auth = self.oauth
        else:
            raise ValueError("No valid authentication credentials")

        if json_data:
            headers["Content-Type"] = "application/json"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, auth=auth, params=params, timeout=30)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=headers, auth=auth, params=params, data=data, files=files, timeout=120)
                else:
                    response = requests.post(url, headers=headers, auth=auth, params=params, json=json_data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, auth=auth, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            logger.error(f"Twitter API error: {error_data}")
            return {
                "success": False,
                "error": error_data.get("detail") or error_data.get("title") or str(e),
                "errors": error_data.get("errors", [])
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== User Info =====

    def get_user_info(self, user_id: Optional[str] = None, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user information

        Args:
            user_id: Twitter user ID
            username: Twitter username (without @)

        Returns:
            User data
        """
        if user_id:
            endpoint = f"users/{user_id}"
        elif username:
            endpoint = f"users/by/username/{username}"
        else:
            # Get authenticated user
            endpoint = "users/me"

        params = {
            "user.fields": "id,name,username,created_at,description,location,profile_image_url,public_metrics,verified,verified_type"
        }

        result = self._make_request(
            "GET",
            endpoint,
            auth_type="oauth1",
            params=params
        )

        if "data" in result:
            result["success"] = True
            result["user"] = result["data"]

        return result

    def get_my_user_id(self) -> Optional[str]:
        """Get the authenticated user's ID"""
        result = self.get_user_info()
        if result.get("success"):
            return result["user"]["id"]
        return None

    # ===== Tweet Creation =====

    def create_tweet(
        self,
        text: str,
        media_ids: Optional[List[str]] = None,
        media_urls: Optional[List[str]] = None,
        reply_to_tweet_id: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        reply_settings: TweetReplySettings = TweetReplySettings.EVERYONE,
        poll_options: Optional[List[str]] = None,
        poll_duration_minutes: int = 1440
    ) -> Dict[str, Any]:
        """
        Create a tweet

        Args:
            text: Tweet text (max 280 chars, or 4000 for premium)
            media_ids: List of uploaded media IDs
            media_urls: List of media URLs to upload
            reply_to_tweet_id: Tweet ID to reply to
            quote_tweet_id: Tweet ID to quote
            reply_settings: Who can reply
            poll_options: Poll options (2-4 options)
            poll_duration_minutes: Poll duration in minutes

        Returns:
            Tweet result with tweet_id
        """
        # Upload media if URLs provided
        if media_urls and not media_ids:
            media_ids = []
            for media_url in media_urls:
                media_result = self.upload_media_from_url(media_url)
                if media_result.get("success"):
                    media_ids.append(media_result["media_id"])

        # Build tweet payload
        payload = {"text": text}

        if media_ids:
            payload["media"] = {"media_ids": media_ids}

        if reply_to_tweet_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}

        if quote_tweet_id:
            payload["quote_tweet_id"] = quote_tweet_id

        if reply_settings != TweetReplySettings.EVERYONE:
            payload["reply_settings"] = reply_settings.value

        if poll_options:
            payload["poll"] = {
                "options": poll_options,
                "duration_minutes": poll_duration_minutes
            }

        result = self._make_request(
            "POST",
            "tweets",
            auth_type="oauth1",
            json_data=payload
        )

        if "data" in result:
            result["success"] = True
            result["tweet_id"] = result["data"]["id"]
            result["tweet_text"] = result["data"]["text"]

        return result

    def create_thread(
        self,
        tweets: List[str],
        media_per_tweet: Optional[List[List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a tweet thread

        Args:
            tweets: List of tweet texts
            media_per_tweet: Optional list of media lists for each tweet

        Returns:
            Thread result with all tweet IDs
        """
        tweet_ids = []
        previous_tweet_id = None

        for i, tweet_text in enumerate(tweets):
            media_urls = media_per_tweet[i] if media_per_tweet and i < len(media_per_tweet) else None

            result = self.create_tweet(
                text=tweet_text,
                media_urls=media_urls,
                reply_to_tweet_id=previous_tweet_id
            )

            if not result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to create tweet {i + 1}",
                    "partial_thread": tweet_ids
                }

            tweet_ids.append(result["tweet_id"])
            previous_tweet_id = result["tweet_id"]

        return {
            "success": True,
            "thread_ids": tweet_ids,
            "first_tweet_id": tweet_ids[0],
            "last_tweet_id": tweet_ids[-1]
        }

    def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Delete a tweet"""
        result = self._make_request(
            "DELETE",
            f"tweets/{tweet_id}",
            auth_type="oauth1"
        )

        if "data" in result:
            return {"success": True, "deleted": result["data"].get("deleted", False)}
        else:
            return {"success": False, "error": result.get("error")}

    # ===== Media Upload =====

    def upload_media_from_url(self, media_url: str) -> Dict[str, Any]:
        """
        Upload media from URL

        Args:
            media_url: Public URL to media file

        Returns:
            Upload result with media_id
        """
        try:
            # Download media
            media_response = requests.get(media_url, timeout=60)
            media_response.raise_for_status()
            media_bytes = media_response.content

            # Determine media type
            content_type = media_response.headers.get("Content-Type", "")
            if "image" in content_type:
                media_category = "tweet_image"
            elif "video" in content_type:
                media_category = "tweet_video"
            else:
                media_category = "tweet_image"  # Default

            return self.upload_media_bytes(media_bytes, media_category)

        except Exception as e:
            logger.error(f"Failed to download media: {e}")
            return {"success": False, "error": str(e)}

    def upload_media_bytes(
        self,
        media_bytes: bytes,
        media_category: str = "tweet_image"
    ) -> Dict[str, Any]:
        """
        Upload media bytes to Twitter

        Args:
            media_bytes: Media file bytes
            media_category: Media category (tweet_image, tweet_video, tweet_gif)

        Returns:
            Upload result with media_id
        """
        # INIT
        init_url = f"{self.UPLOAD_URL}/media/upload.json"
        init_params = {
            "command": "INIT",
            "total_bytes": len(media_bytes),
            "media_type": "image/jpeg" if media_category == "tweet_image" else "video/mp4",
            "media_category": media_category
        }

        try:
            init_response = requests.post(
                init_url,
                auth=self.oauth,
                params=init_params,
                timeout=30
            )
            init_response.raise_for_status()
            media_id = init_response.json()["media_id_string"]

            # APPEND
            append_url = f"{self.UPLOAD_URL}/media/upload.json"
            append_params = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": 0
            }
            append_files = {"media": media_bytes}

            append_response = requests.post(
                append_url,
                auth=self.oauth,
                params=append_params,
                files=append_files,
                timeout=120
            )
            append_response.raise_for_status()

            # FINALIZE
            finalize_params = {
                "command": "FINALIZE",
                "media_id": media_id
            }

            finalize_response = requests.post(
                init_url,
                auth=self.oauth,
                params=finalize_params,
                timeout=30
            )
            finalize_response.raise_for_status()

            return {
                "success": True,
                "media_id": media_id
            }

        except Exception as e:
            logger.error(f"Media upload failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== Tweet Retrieval =====

    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Get a single tweet"""
        params = {
            "tweet.fields": "created_at,public_metrics,entities,attachments,author_id",
            "expansions": "author_id,attachments.media_keys",
            "media.fields": "url,preview_image_url,type,duration_ms,public_metrics"
        }

        result = self._make_request(
            "GET",
            f"tweets/{tweet_id}",
            auth_type="bearer" if self.bearer_token else "oauth1",
            params=params
        )

        if "data" in result:
            result["success"] = True
            result["tweet"] = result["data"]

        return result

    def get_user_tweets(
        self,
        user_id: Optional[str] = None,
        max_results: int = 10,
        exclude_replies: bool = False,
        exclude_retweets: bool = False
    ) -> Dict[str, Any]:
        """Get user's tweets"""
        if not user_id:
            user_id = self.get_my_user_id()

        if not user_id:
            return {"success": False, "error": "User ID required"}

        params = {
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics,entities",
            "exclude": []
        }

        if exclude_replies:
            params["exclude"].append("replies")
        if exclude_retweets:
            params["exclude"].append("retweets")

        if params["exclude"]:
            params["exclude"] = ",".join(params["exclude"])
        else:
            del params["exclude"]

        result = self._make_request(
            "GET",
            f"users/{user_id}/tweets",
            auth_type="bearer" if self.bearer_token else "oauth1",
            params=params
        )

        if "data" in result:
            result["success"] = True
            result["tweets"] = result["data"]

        return result

    # ===== Analytics =====

    def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get metrics for a tweet (requires ownership)

        Args:
            tweet_id: Tweet ID

        Returns:
            Tweet metrics
        """
        params = {
            "tweet.fields": "public_metrics,non_public_metrics,organic_metrics,promoted_metrics"
        }

        result = self._make_request(
            "GET",
            f"tweets/{tweet_id}",
            auth_type="oauth1",
            params=params
        )

        if "data" in result:
            result["success"] = True
            result["metrics"] = {
                "public": result["data"].get("public_metrics", {}),
                "non_public": result["data"].get("non_public_metrics", {}),
                "organic": result["data"].get("organic_metrics", {})
            }

        return result

    # ===== Search =====

    def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Search recent tweets

        Args:
            query: Search query
            max_results: Number of results (max 100)
            start_time: Start time for search
            end_time: End time for search

        Returns:
            Search results
        """
        params = {
            "query": query,
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics,author_id"
        }

        if start_time:
            params["start_time"] = start_time.isoformat() + "Z"
        if end_time:
            params["end_time"] = end_time.isoformat() + "Z"

        result = self._make_request(
            "GET",
            "tweets/search/recent",
            auth_type="bearer" if self.bearer_token else "oauth1",
            params=params
        )

        if "data" in result:
            result["success"] = True
            result["tweets"] = result["data"]

        return result

    # ===== Likes & Retweets =====

    def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Like a tweet"""
        user_id = self.get_my_user_id()
        if not user_id:
            return {"success": False, "error": "Could not get user ID"}

        result = self._make_request(
            "POST",
            f"users/{user_id}/likes",
            auth_type="oauth1",
            json_data={"tweet_id": tweet_id}
        )

        if "data" in result:
            result["success"] = True

        return result

    def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """Retweet a tweet"""
        user_id = self.get_my_user_id()
        if not user_id:
            return {"success": False, "error": "Could not get user ID"}

        result = self._make_request(
            "POST",
            f"users/{user_id}/retweets",
            auth_type="oauth1",
            json_data={"tweet_id": tweet_id}
        )

        if "data" in result:
            result["success"] = True

        return result


# ===== Usage Example =====
if __name__ == "__main__":
    # Example usage
    api = TwitterAPIv2()

    # Get user info
    user_info = api.get_user_info()
    print("User info:", user_info)

    # Create tweet
    result = api.create_tweet(
        text="Excited to share this amazing product! Check it out 👇 #affiliate",
        media_urls=["https://example.com/product.jpg"]
    )
    print("Tweet created:", result)

    if result.get("success"):
        # Get tweet metrics
        metrics = api.get_tweet_metrics(result["tweet_id"])
        print("Metrics:", metrics)

    # Create thread
    thread = api.create_thread([
        "🧵 Thread about this amazing product (1/3)",
        "Here are the key features... (2/3)",
        "Get it now with my affiliate link! (3/3)"
    ])
    print("Thread created:", thread)
