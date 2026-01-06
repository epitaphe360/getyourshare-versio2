"""
Campaign Repository
"""

from typing import Optional, List, Dict, Any
from .base_repository import BaseRepository
from utils.cache import cache


class CampaignRepository(BaseRepository):
    """Repository pour la gestion des campagnes"""

    table_name = "campaigns"

    async def find_by_merchant(self, merchant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all campaigns for a merchant"""
        return await self.find_by({"merchant_id": merchant_id}, limit=limit)

    @cache(ttl_seconds=300)
    async def find_active_campaigns(self, merchant_id: str = None) -> List[Dict[str, Any]]:
        """Get active campaigns avec cache (5 min)"""
        filters = {"status": "active"}
        if merchant_id:
            filters["merchant_id"] = merchant_id

        return await self.find_by(filters, limit=1000)

    async def find_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get campaigns by status"""
        return await self.find_by({"status": status}, limit=limit)

    async def update_status(self, campaign_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        """Update campaign status"""
        return await self.update(campaign_id, {"status": new_status})

    async def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics"""
        # This would typically join with other tables
        # For now, return basic info
        campaign = await self.find_by_id(campaign_id)

        if not campaign:
            return {"error": "Campaign not found"}

        return {
            "id": campaign.get("id"),
            "name": campaign.get("name"),
            "status": campaign.get("status"),
            "budget": campaign.get("budget"),
            "start_date": campaign.get("start_date"),
            "end_date": campaign.get("end_date"),
        }
