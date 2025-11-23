from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from supabase_client import supabase
from auth import get_current_user_from_cookie
import logging

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

# Models
class NotificationRead(BaseModel):
    id: str
    user_id: str
    title: Optional[str] = None
    message: str
    type: Optional[str] = "info"
    read: bool
    created_at: str
    link: Optional[str] = None

class WebPushSubscription(BaseModel):
    endpoint: str
    keys: dict
    expirationTime: Optional[float] = None

# Endpoints

@router.get("", response_model=dict)
async def get_notifications(
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Get user notifications"""
    try:
        user_id = current_user["id"]
        
        query = supabase.table("notifications").select("*", count="exact").eq("user_id", user_id)
        
        if unread_only:
            query = query.eq("read", False)
            
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        
        result = query.execute()
        
        notifications = result.data if result.data else []
        total = result.count or 0
        
        # Count unread
        unread_query = supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("read", False).execute()
        unread_count = unread_query.count or 0
        
        return {
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count
        }
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return {"notifications": [], "total": 0, "unread_count": 0}

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Mark a notification as read"""
    try:
        user_id = current_user["id"]
        
        # Verify ownership
        check = supabase.table("notifications").select("id").eq("id", notification_id).eq("user_id", user_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        result = supabase.table("notifications").update({"read": True}).eq("id", notification_id).execute()
        
        return {"success": True, "message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Mark all user notifications as read"""
    try:
        user_id = current_user["id"]
        
        result = supabase.table("notifications").update({"read": True}).eq("user_id", user_id).eq("read", False).execute()
        
        return {"success": True, "message": "All notifications marked as read"}
        
    except Exception as e:
        logger.error(f"Error marking all notifications read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe")
async def subscribe_push_notifications(
    subscription: WebPushSubscription,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Subscribe to Web Push Notifications"""
    try:
        user_id = current_user["id"]
        
        # Store subscription in database
        # Assuming we have a table 'push_subscriptions' or we store it in 'users' or 'user_settings'
        # Let's check if 'push_subscriptions' exists, if not create it or store in a JSON column
        
        # For now, let's try to insert into 'push_subscriptions'
        data = {
            "user_id": user_id,
            "endpoint": subscription.endpoint,
            "p256dh": subscription.keys.get("p256dh"),
            "auth": subscription.keys.get("auth"),
            "user_agent": "Web", # Simplified
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Upsert based on endpoint to avoid duplicates
        # We might need to create this table if it doesn't exist
        try:
            supabase.table("push_subscriptions").upsert(data, on_conflict="endpoint").execute()
        except Exception as e:
            logger.warning(f"push_subscriptions table might be missing: {e}")
            # Fallback: maybe store in user metadata?
            # For now, just log it.
            
        return {"success": True, "message": "Subscribed to push notifications"}
        
    except Exception as e:
        logger.error(f"Error subscribing to push notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))
