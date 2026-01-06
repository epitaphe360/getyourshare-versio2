"""
Tracking Repository
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from utils.cache import cache


class TrackingRepository(BaseRepository):
    """Repository pour la gestion des événements de tracking"""

    table_name = "tracking_events"

    @cache(ttl_seconds=60)
    async def find_by_link(self, link_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all tracking events for a link avec cache (1 min)"""
        result = self._execute_query(
            self.supabase.table(self.table_name)
            .select("*")
            .eq("link_id", link_id)
            .order("created_at", desc=True)
            .limit(limit),
            operation="find_by_link"
        )
        return result["data"] if result["success"] else []

    async def find_by_influencer(self, influencer_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all tracking events for an influencer"""
        return await self.find_by({"influencer_id": influencer_id}, limit=limit)

    async def find_by_event_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tracking events by type (click, view, conversion, etc.)"""
        return await self.find_by({"event_type": event_type}, limit=limit)

    async def find_by_date_range(self, start_date: str, end_date: str, link_id: str = None) -> List[Dict[str, Any]]:
        """Get tracking events within a date range"""
        query = self.supabase.table(self.table_name).select("*")

        query = query.gte("created_at", start_date).lte("created_at", end_date)

        if link_id:
            query = query.eq("link_id", link_id)

        query = query.order("created_at", desc=True)

        result = self._execute_query(query, operation="find_by_date_range")
        return result["data"] if result["success"] else []

    async def count_by_link(self, link_id: str) -> int:
        """Count tracking events for a specific link"""
        return await self.count({"link_id": link_id})

    async def count_by_event_type(self, link_id: str, event_type: str) -> int:
        """Count specific event types for a link (e.g., clicks, conversions)"""
        return await self.count({"link_id": link_id, "event_type": event_type})

    async def get_conversion_rate(self, link_id: str) -> Dict[str, Any]:
        """Calculate conversion rate for a link"""
        clicks = await self.count_by_event_type(link_id, "click")
        conversions = await self.count_by_event_type(link_id, "conversion")

        rate = (conversions / clicks * 100) if clicks > 0 else 0

        return {
            "link_id": link_id,
            "clicks": clicks,
            "conversions": conversions,
            "conversion_rate": round(rate, 2)
        }
