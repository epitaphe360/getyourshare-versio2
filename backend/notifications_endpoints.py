"""
============================================
NOTIFICATIONS ENDPOINTS
GetYourShare - Système de Notifications
============================================

Endpoints pour notifications temps réel:
- WebSocket pour notifications live
- CRUD notifications
- Paramètres utilisateur
- Marquage lu/non lu
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from auth import get_current_user_from_cookie
from supabase_client import supabase
from utils.logger import logger
import json

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

# ============================================
# WEBSOCKET CONNECTION MANAGER
# ============================================

class ConnectionManager:
    """Gestionnaire de connexions WebSocket"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
    
    async def broadcast(self, message: dict):
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_id}: {e}")

manager = ConnectionManager()

# ============================================
# PYDANTIC MODELS
# ============================================

class NotificationSettingsUpdate(BaseModel):
    """Mise à jour des paramètres de notifications"""
    settings: Dict[str, bool]

class NotificationCreate(BaseModel):
    """Création de notification"""
    user_id: str
    title: str
    message: str
    type: str  # sale, payment, message, user, achievement, warning, info
    link: Optional[str] = None

# ============================================
# WEBSOCKET ENDPOINT
# ============================================

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: str):
    """
    WebSocket endpoint pour notifications temps réel
    """
    user = None
    user_id = None
    
    try:
        # Authentifier l'utilisateur via token (WebSocket auth simplified)
        # For now, use token as user_id directly (should be improved with proper JWT validation)
        import jwt
        from server import JWT_SECRET, JWT_ALGORITHM
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get('sub') or payload.get('id')
            user = {'id': user_id}
        except Exception:
            await websocket.close(code=1008)
            return
        
        # Connecter le WebSocket
        await manager.connect(websocket, user_id)
        
        # Envoyer un message de confirmation
        await websocket.send_json({
            'type': 'connection_established',
            'message': 'Connected to notifications',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Boucle pour maintenir la connexion
        while True:
            # Recevoir les messages du client (heartbeat, etc.)
            data = await websocket.receive_text()
            
            if data == 'ping':
                await websocket.send_json({'type': 'pong'})
    
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user_id:
            manager.disconnect(websocket, user_id)
        try:
            await websocket.close()
        except:
            pass

# ============================================
# HELPER FUNCTIONS
# ============================================

async def send_notification(user_id: str, title: str, message: str, notification_type: str, link: str = None):
    """
    Envoie une notification à un utilisateur (WebSocket + DB)
    """
    try:
        # Sauvegarder en DB
        notification_data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'link': link,
            'read': False,
            'created_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('notifications').insert(notification_data).execute()
        
        if response.data:
            notification = response.data[0]
            
            # Envoyer via WebSocket si connecté
            await manager.send_personal_message(notification, user_id)
            
            return notification
        
        return None
    
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return None

# ============================================
# REST ENDPOINTS
# ============================================

@router.get("")
async def get_notifications(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère les notifications de l'utilisateur
    """
    try:
        response = supabase.table('notifications')\
            .select('*')\
            .eq('user_id', current_user['id'])\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        notifications = response.data if response.data else []
        unread_count = len([n for n in notifications if not n.get('read')])
        
        return {
            'notifications': notifications,
            'unread_count': unread_count
        }
    
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Marque une notification comme lue
    """
    try:
        response = supabase.table('notifications')\
            .update({'read': True, 'read_at': datetime.utcnow().isoformat()})\
            .eq('id', notification_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {
            'success': True,
            'message': 'Notification marked as read'
        }
    
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Marque toutes les notifications comme lues
    """
    try:
        response = supabase.table('notifications')\
            .update({'read': True, 'read_at': datetime.utcnow().isoformat()})\
            .eq('user_id', current_user['id'])\
            .eq('read', False)\
            .execute()
        
        return {
            'success': True,
            'message': 'All notifications marked as read'
        }
    
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Supprime une notification
    """
    try:
        response = supabase.table('notifications')\
            .delete()\
            .eq('id', notification_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {
            'success': True,
            'message': 'Notification deleted'
        }
    
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )


@router.get("/settings")
async def get_notification_settings(
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère les paramètres de notifications de l'utilisateur
    """
    try:
        response = supabase.table('notification_settings')\
            .select('*')\
            .eq('user_id', current_user['id'])\
            .single()\
            .execute()
        
        if response.data:
            return {'settings': response.data.get('settings', {})}
        
        # Paramètres par défaut
        return {
            'settings': {
                'email': True,
                'push': True,
                'sms': False,
                'sales': True,
                'payments': True,
                'messages': True,
                'system': True
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching notification settings: {e}")
        # Retourner les paramètres par défaut en cas d'erreur
        return {
            'settings': {
                'email': True,
                'push': True,
                'sms': False,
                'sales': True,
                'payments': True,
                'messages': True,
                'system': True
            }
        }


@router.put("/settings")
async def update_notification_settings(
    request: NotificationSettingsUpdate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Met à jour les paramètres de notifications
    """
    try:
        # Vérifier si les paramètres existent
        existing = supabase.table('notification_settings')\
            .select('id')\
            .eq('user_id', current_user['id'])\
            .execute()
        
        settings_data = {
            'user_id': current_user['id'],
            'settings': request.settings,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if existing.data:
            # Update
            response = supabase.table('notification_settings')\
                .update(settings_data)\
                .eq('user_id', current_user['id'])\
                .execute()
        else:
            # Insert
            settings_data['created_at'] = datetime.utcnow().isoformat()
            response = supabase.table('notification_settings')\
                .insert(settings_data)\
                .execute()
        
        return {
            'success': True,
            'message': 'Settings updated successfully',
            'settings': request.settings
        }
    
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """
    Crée et envoie une notification (admin only)
    """
    try:
        # Vérifier que l'utilisateur est admin
        if current_user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can send notifications"
            )
        
        result = await send_notification(
            notification.user_id,
            notification.title,
            notification.message,
            notification.type,
            notification.link
        )
        
        if result:
            return {
                'success': True,
                'message': 'Notification sent successfully',
                'notification': result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send notification"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )
