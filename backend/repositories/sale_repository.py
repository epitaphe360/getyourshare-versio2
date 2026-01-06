"""
Sale Repository
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from utils.cache import cache


class SaleRepository(BaseRepository):
    """Repository pour la gestion des ventes"""

    table_name = "sales"

    @cache(ttl_seconds=60)
    async def find_by_merchant(self, merchant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all sales for a merchant avec cache (1 min)"""
        result = self._execute_query(
            self.supabase.table(self.table_name)
            .select("*")
            .eq("merchant_id", merchant_id)
            .order("created_at", desc=True)
            .limit(limit),
            operation="find_by_merchant"
        )
        return result["data"] if result["success"] else []

    @cache(ttl_seconds=60)
    async def find_by_influencer(self, influencer_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all sales for an influencer avec cache (1 min)"""
        result = self._execute_query(
            self.supabase.table(self.table_name)
            .select("*")
            .eq("influencer_id", influencer_id)
            .order("created_at", desc=True)
            .limit(limit),
            operation="find_by_influencer"
        )
        return result["data"] if result["success"] else []

    async def find_by_campaign(self, campaign_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all sales for a campaign"""
        return await self.find_by({"campaign_id": campaign_id}, limit=limit)

    async def find_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sales by status"""
        return await self.find_by({"status": status}, limit=limit)

    async def find_by_date_range(self, start_date: str, end_date: str, merchant_id: str = None) -> List[Dict[str, Any]]:
        """Get sales within a date range"""
        query = self.supabase.table(self.table_name).select("*")

        query = query.gte("created_at", start_date).lte("created_at", end_date)

        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        query = query.order("created_at", desc=True)

        result = self._execute_query(query, operation="find_by_date_range")
        return result["data"] if result["success"] else []

    async def get_total_revenue(self, merchant_id: str = None) -> float:
        """Calculate total revenue"""
        filters = {}
        if merchant_id:
            filters["merchant_id"] = merchant_id

        sales = await self.find_by(filters, limit=10000)
        return sum(sale.get("amount", 0) for sale in sales)

    async def update_status(self, sale_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        """Update sale status"""
        return await self.update(sale_id, {"status": new_status})
