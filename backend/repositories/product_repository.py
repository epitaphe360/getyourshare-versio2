"""
Product Repository
"""

from typing import Optional, List, Dict, Any
from .base_repository import BaseRepository
from utils.cache import cache


class ProductRepository(BaseRepository):
    """Repository pour la gestion des produits"""

    table_name = "products"

    @cache(ttl_seconds=300)
    async def find_by_merchant(self, merchant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all products for a merchant avec cache (5 min)"""
        return await self.find_by({"merchant_id": merchant_id}, limit=limit)

    @cache(ttl_seconds=300)
    async def find_by_category(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products by category avec cache (5 min)"""
        return await self.find_by({"category": category}, limit=limit)

    @cache(ttl_seconds=60)
    async def find_active_products(self, merchant_id: str = None) -> List[Dict[str, Any]]:
        """Get active products avec cache (1 min)"""
        filters = {"status": "active"}
        if merchant_id:
            filters["merchant_id"] = merchant_id

        return await self.find_by(filters, limit=1000)

    async def find_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products by status"""
        return await self.find_by({"status": status}, limit=limit)

    async def update_status(self, product_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        """Update product status"""
        return await self.update(product_id, {"status": new_status})

    async def update_stock(self, product_id: str, stock_quantity: int) -> Optional[Dict[str, Any]]:
        """Update product stock quantity"""
        return await self.update(product_id, {"stock_quantity": stock_quantity})

    async def update_price(self, product_id: str, price: float) -> Optional[Dict[str, Any]]:
        """Update product price"""
        return await self.update(product_id, {"price": price})

    async def get_product_stats(self, product_id: str) -> Dict[str, Any]:
        """Get product statistics"""
        product = await self.find_by_id(product_id)

        if not product:
            return {"error": "Product not found"}

        return {
            "id": product.get("id"),
            "name": product.get("name"),
            "status": product.get("status"),
            "price": product.get("price"),
            "stock_quantity": product.get("stock_quantity"),
            "category": product.get("category"),
            "merchant_id": product.get("merchant_id"),
        }

    async def search_by_name(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search products by name (basic implementation)"""
        # Note: This is a basic implementation
        # For production, consider using full-text search or elasticsearch
        result = self._execute_query(
            self.supabase.table(self.table_name)
            .select("*")
            .ilike("name", f"%{search_term}%")
            .limit(limit),
            operation="search_by_name"
        )
        return result["data"] if result["success"] else []
