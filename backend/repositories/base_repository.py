from typing import Optional, List, Dict, Any
from datetime import datetime
import time
from utils.logger import logger
from utils.cache import cache


class BaseRepository:
    """
    Base Repository avec CRUD générique, caching, logging et monitoring
    """

    def __init__(self, supabase_client, table_name: str = None):
        self.supabase = supabase_client
        self.table_name = table_name or getattr(self, 'table_name', None)

        if not self.table_name:
            raise ValueError(f"{self.__class__.__name__} must define table_name")

    def _execute_query(self, query, operation: str = "query"):
        """Execute query avec logging et monitoring"""
        start_time = time.time()
        try:
            result = query.execute()
            duration_ms = (time.time() - start_time) * 1000

            # Log slow queries
            if duration_ms > 100:
                logger.warning(f"Slow {operation}", extra={
                    "table": self.table_name,
                    "duration_ms": round(duration_ms, 2),
                    "operation": operation
                })
            else:
                logger.debug(f"{operation} executed", extra={
                    "table": self.table_name,
                    "duration_ms": round(duration_ms, 2)
                })

            return {"success": True, "data": result.data, "count": getattr(result, 'count', None)}
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"{operation} failed", extra={
                "table": self.table_name,
                "error": str(e),
                "duration_ms": round(duration_ms, 2)
            })
            return {"success": False, "error": str(e), "data": None}

    @cache(ttl_seconds=300)
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID avec cache (5 min)"""
        result = self._execute_query(
            self.supabase.table(self.table_name).select("*").eq("id", id).maybe_single(),
            operation="find_by_id"
        )
        return result["data"] if result["success"] else None

    @cache(ttl_seconds=60)
    async def find_all(self, limit: int = 100, offset: int = 0, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all records avec cache (1 min) et filtres optionnels"""
        query = self.supabase.table(self.table_name).select("*")

        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        query = query.range(offset, offset + limit - 1)

        result = self._execute_query(query, operation="find_all")
        return result["data"] if result["success"] else []

    async def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create record avec auto-timestamps"""
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow().isoformat()

        result = self._execute_query(
            self.supabase.table(self.table_name).insert(data),
            operation="create"
        )

        if result["success"] and result["data"]:
            logger.info(f"Record created", extra={
                "table": self.table_name,
                "id": result["data"][0].get("id")
            })
            return result["data"][0]

        return None

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update record avec auto-timestamp updated_at"""
        data["updated_at"] = datetime.utcnow().isoformat()

        result = self._execute_query(
            self.supabase.table(self.table_name).update(data).eq("id", id),
            operation="update"
        )

        if result["success"] and result["data"]:
            logger.info(f"Record updated", extra={
                "table": self.table_name,
                "id": id
            })
            return result["data"][0]

        return None

    async def delete(self, id: str) -> bool:
        """Delete record"""
        result = self._execute_query(
            self.supabase.table(self.table_name).delete().eq("id", id),
            operation="delete"
        )

        if result["success"]:
            logger.info(f"Record deleted", extra={
                "table": self.table_name,
                "id": id
            })

        return result["success"]

    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records avec filtres optionnels"""
        query = self.supabase.table(self.table_name).select("id", count="exact", head=True)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        result = self._execute_query(query, operation="count")
        return result.get("count", 0) if result["success"] else 0

    async def bulk_create(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple records"""
        for record in records:
            if "created_at" not in record:
                record["created_at"] = datetime.utcnow().isoformat()

        result = self._execute_query(
            self.supabase.table(self.table_name).insert(records),
            operation="bulk_create"
        )

        if result["success"]:
            logger.info(f"Bulk create completed", extra={
                "table": self.table_name,
                "count": len(records)
            })

        return result["data"] if result["success"] else []

    async def find_by(self, filters: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Find records by filters"""
        query = self.supabase.table(self.table_name).select("*")

        for key, value in filters.items():
            query = query.eq(key, value)

        query = query.limit(limit)

        result = self._execute_query(query, operation="find_by")
        return result["data"] if result["success"] else []

