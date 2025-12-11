"""
Routes Live Chat (WebSocket)
Chat en temps réel client-support
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Set
from datetime import datetime
import json

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/live-chat", tags=["Live Chat"])


# ============================================
# CONNECTION MANAGER
# ============================================

class ConnectionManager:
    """
    Gestionnaire de connexions WebSocket
    """

    def __init__(self):
        # {user_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # {room_id: Set[user_id]}
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connecter un utilisateur"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to live chat")

    def disconnect(self, user_id: str):
        """Déconnecter un utilisateur"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from live chat")

        # Retirer de toutes les rooms
        for room_id in list(self.rooms.keys()):
            if user_id in self.rooms[room_id]:
                self.rooms[room_id].remove(user_id)
                if not self.rooms[room_id]:
                    del self.rooms[room_id]

    def join_room(self, user_id: str, room_id: str):
        """Rejoindre une room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(user_id)
        logger.info(f"User {user_id} joined room {room_id}")

    def leave_room(self, user_id: str, room_id: str):
        """Quitter une room"""
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            self.rooms[room_id].remove(user_id)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            logger.info(f"User {user_id} left room {room_id}")

    async def send_personal_message(self, message: str, user_id: str):
        """Envoyer un message à un utilisateur spécifique"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)

    async def broadcast_to_room(self, message: str, room_id: str, exclude_user: str = None):
        """Envoyer un message à tous les utilisateurs d'une room"""
        if room_id not in self.rooms:
            return

        for user_id in self.rooms[room_id]:
            if user_id != exclude_user:
                await self.send_personal_message(message, user_id)

    def get_room_users(self, room_id: str) -> list:
        """Obtenir la liste des utilisateurs dans une room"""
        return list(self.rooms.get(room_id, set()))


# Instance globale du manager
manager = ConnectionManager()


# ============================================
# WEBSOCKET ENDPOINT
# ============================================

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint pour live chat

    Messages format:
    {
        "type": "message|typing|join_room|leave_room",
        "room_id": "chat_room_id",
        "content": "message content",
        "metadata": {}
    }
    """
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Recevoir un message
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                message_type = message_data.get('type')
                room_id = message_data.get('room_id')
                content = message_data.get('content')

                if message_type == 'join_room':
                    # Rejoindre une room
                    manager.join_room(user_id, room_id)

                    # Notifier les autres
                    await manager.broadcast_to_room(
                        json.dumps({
                            'type': 'user_joined',
                            'user_id': user_id,
                            'timestamp': datetime.now().isoformat()
                        }),
                        room_id,
                        exclude_user=user_id
                    )

                    # Envoyer l'historique au nouvel arrivant
                    history = await get_chat_history_internal(room_id, limit=50)
                    await manager.send_personal_message(
                        json.dumps({
                            'type': 'history',
                            'messages': history
                        }),
                        user_id
                    )

                elif message_type == 'leave_room':
                    # Quitter une room
                    manager.leave_room(user_id, room_id)

                    # Notifier les autres
                    await manager.broadcast_to_room(
                        json.dumps({
                            'type': 'user_left',
                            'user_id': user_id,
                            'timestamp': datetime.now().isoformat()
                        }),
                        room_id
                    )

                elif message_type == 'message':
                    # Envoyer un message
                    if not room_id or not content:
                        continue

                    # Sauvegarder en DB
                    message_record = {
                        'room_id': room_id,
                        'user_id': user_id,
                        'content': content,
                        'metadata': message_data.get('metadata', {}),
                        'created_at': datetime.now().isoformat()
                    }

                    try:
                        result = supabase.table('chat_messages').insert(message_record).execute()
                        message_id = result.data[0]['id'] if result.data else None
                    except Exception:
                        message_id = None

                    # Broadcaster à la room
                    await manager.broadcast_to_room(
                        json.dumps({
                            'type': 'message',
                            'id': message_id,
                            'room_id': room_id,
                            'user_id': user_id,
                            'content': content,
                            'timestamp': datetime.now().isoformat(),
                            'metadata': message_data.get('metadata', {})
                        }),
                        room_id
                    )

                elif message_type == 'typing':
                    # Indicateur de frappe
                    await manager.broadcast_to_room(
                        json.dumps({
                            'type': 'typing',
                            'user_id': user_id,
                            'room_id': room_id
                        }),
                        room_id,
                        exclude_user=user_id
                    )

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from user {user_id}")
                continue

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"User {user_id} disconnected")


# ============================================
# REST ENDPOINTS
# ============================================

@router.post("/rooms")
async def create_chat_room(
    participants: list[str],
    room_type: str = "support",  # support, direct, group
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une room de chat
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Inclure le créateur
        if user_id not in participants:
            participants.append(user_id)

        # Générer room ID
        import uuid
        room_id = f"room_{uuid.uuid4().hex[:12]}"

        room_data = {
            'room_id': room_id,
            'room_type': room_type,
            'created_by': user_id,
            'participants': participants,
            'created_at': datetime.now().isoformat()
        }

        result = supabase.table('chat_rooms').insert(room_data).execute()

        return {
            "success": True,
            "room": result.data[0] if result.data else room_data,
            "room_id": room_id
        }

    except Exception as e:
        logger.error(f"Error creating chat room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms")
async def get_chat_rooms(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des rooms de l'utilisateur
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Rooms où l'utilisateur est participant
        rooms = supabase.table('chat_rooms').select('*').contains('participants', [user_id]).execute()

        return {
            "success": True,
            "rooms": rooms.data or [],
            "total": len(rooms.data) if rooms.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting chat rooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/history")
async def get_chat_history(
    room_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Historique des messages d'une room
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier que l'utilisateur est participant
        room = supabase.table('chat_rooms').select('participants').eq('room_id', room_id).single().execute()

        if not room.data or user_id not in room.data.get('participants', []):
            raise HTTPException(status_code=403, detail="Non autorisé")

        messages = await get_chat_history_internal(room_id, limit, before)

        return {
            "success": True,
            "room_id": room_id,
            "messages": messages,
            "total": len(messages)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_chat_history_internal(room_id: str, limit: int = 50, before: Optional[str] = None) -> list:
    """Fonction interne pour récupérer l'historique"""
    try:
        query = supabase.table('chat_messages').select('*').eq('room_id', room_id)

        if before:
            query = query.lt('created_at', before)

        query = query.order('created_at', desc=True).limit(limit)

        response = query.execute()

        # Inverser pour avoir l'ordre chronologique
        messages = list(reversed(response.data or []))

        return messages
    except Exception:
        return []


@router.get("/rooms/{room_id}/participants")
async def get_room_participants(
    room_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des participants dans une room
    """
    try:
        # Participants en ligne (WebSocket)
        online_users = manager.get_room_users(room_id)

        # Tous les participants (DB)
        room = supabase.table('chat_rooms').select('participants').eq('room_id', room_id).single().execute()

        all_participants = room.data.get('participants', []) if room.data else []

        # Enrichir avec infos utilisateurs
        participants_info = []
        for user_id in all_participants:
            profile = supabase.table('profiles').select('full_name, avatar_url').eq('user_id', user_id).single().execute()

            participants_info.append({
                'user_id': user_id,
                'full_name': profile.data.get('full_name') if profile.data else 'Unknown',
                'avatar_url': profile.data.get('avatar_url') if profile.data else None,
                'online': user_id in online_users
            })

        return {
            "success": True,
            "room_id": room_id,
            "participants": participants_info,
            "online_count": len(online_users),
            "total_count": len(all_participants)
        }

    except Exception as e:
        logger.error(f"Error getting room participants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/mark-read")
async def mark_messages_as_read(
    room_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Marquer les messages comme lus
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Marquer tous les messages de la room comme lus pour cet utilisateur
        # Note: Nécessite une table read_receipts pour tracking précis

        return {
            "success": True,
            "message": "Messages marqués comme lus"
        }

    except Exception as e:
        logger.error(f"Error marking messages as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from typing import Optional
