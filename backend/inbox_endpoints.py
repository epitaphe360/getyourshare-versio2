"""
Unified Inbox Endpoints - Python/FastAPI
Boîte de réception unifiée multi-canal pour commerciaux
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from db_helpers import get_db_connection, get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class MessageCreate(BaseModel):
    thread_id: Optional[str] = None
    contact_id: Optional[str] = None
    contact_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    channel: str
    subject: Optional[str] = None
    body: str
    priority: str = "normal"

@router.get("/messages")
async def get_messages(
    channel: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_starred: Optional[bool] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir la boîte de réception"""
    try:
        supabase = get_db_connection()
        query = supabase.table('unified_messages').select('*').eq('commercial_id', current_user['id']).eq('direction', 'inbound')
        
        if channel:
            query = query.eq('channel', channel)
        if is_read is not None:
            query = query.eq('is_read', is_read)
        if is_starred:
            query = query.eq('is_starred', True)
        if priority:
            query = query.eq('priority', priority)
            
        result = query.order('created_at', desc=True).limit(limit).execute()
        return {"success": True, "messages": result.data or [], "count": len(result.data) if result.data else 0}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """Obtenir les statistiques"""
    try:
        supabase = get_db_connection()
        result = supabase.table('unified_messages').select('*').eq('commercial_id', current_user['id']).eq('direction', 'inbound').execute()
        messages = result.data or []
        
        stats = {
            "total": len(messages),
            "unread": len([m for m in messages if not m.get('is_read')]),
            "starred": len([m for m in messages if m.get('is_starred')]),
            "urgent": len([m for m in messages if m.get('priority') == 'urgent']),
            "by_channel": {},
            "by_sentiment": {"positive": 0, "neutral": 0, "negative": 0},
            "avg_response_time_hours": "2.5"
        }
        
        for channel in ['email', 'sms', 'whatsapp', 'messenger', 'linkedin']:
            stats["by_channel"][channel] = len([m for m in messages if m.get('channel') == channel])
        
        for sentiment in ['positive', 'neutral', 'negative']:
            stats["by_sentiment"][sentiment] = len([m for m in messages if m.get('sentiment') == sentiment])
            
        return {"success": True, "statistics": stats}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages")
async def send_message(message: MessageCreate, current_user: dict = Depends(get_current_user)):
    """Envoyer un message"""
    try:
        import uuid
        supabase = get_db_connection()
        msg_data = {
            "thread_id": message.thread_id or str(uuid.uuid4()),
            "commercial_id": current_user['id'],
            "direction": "outbound",
            **message.dict(exclude_none=True)
        }
        result = supabase.table('unified_messages').insert(msg_data).execute()
        return {"success": True, "message": result.data[0] if result.data else None}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/messages/{message_id}/read")
async def mark_as_read(message_id: str, current_user: dict = Depends(get_current_user)):
    """Marquer comme lu"""
    try:
        supabase = get_db_connection()
        result = supabase.table('unified_messages').update({
            "is_read": True,
            "read_at": datetime.now().isoformat()
        }).eq('id', message_id).eq('commercial_id', current_user['id']).execute()
        return {"success": True, "message": result.data[0] if result.data else None}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str, current_user: dict = Depends(get_current_user)):
    """Obtenir un thread de conversation"""
    try:
        supabase = get_db_connection()
        result = supabase.table('unified_messages').select('*').eq('thread_id', thread_id).eq('commercial_id', current_user['id']).order('created_at').execute()
        return {"success": True, "messages": result.data or [], "count": len(result.data) if result.data else 0}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
