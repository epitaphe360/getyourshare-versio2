"""
User Repository
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from utils.cache import cache


class UserRepository(BaseRepository):
    """Repository pour la gestion des utilisateurs"""

    table_name = "users"

    @cache(ttl_seconds=300)
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email avec cache (5 min)"""
        result = self._execute_query(
            self.supabase.table(self.table_name).select("*").eq("email", email).maybe_single(),
            operation="find_by_email"
        )
        return result["data"] if result["success"] else None

    @cache(ttl_seconds=60)
    async def find_by_role(self, role: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users with specific role avec cache (1 min)"""
        return await self.find_by({"role": role}, limit=limit)

    async def find_by_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by verification token (no cache for security)"""
        result = self._execute_query(
            self.supabase.table(self.table_name).select("*").eq("verification_token", token).maybe_single(),
            operation="find_by_verification_token"
        )
        return result["data"] if result["success"] else None

    async def update_last_login(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Update user's last login timestamp"""
        return await self.update(user_id, {
            "last_login": datetime.utcnow().isoformat()
        })

    async def verify_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Mark user as verified"""
        return await self.update(user_id, {
            "verified": True,
            "verification_token": None
        })

    async def update_password(self, user_id: str, hashed_password: str) -> Optional[Dict[str, Any]]:
        """Update user password (hashed)"""
        return await self.update(user_id, {
            "password": hashed_password
        })

    async def find_active_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all active users"""
        return await self.find_by({"status": "active"}, limit=limit)

    async def count_by_role(self, role: str) -> int:
        """Count users by role"""
        return await self.count({"role": role})
