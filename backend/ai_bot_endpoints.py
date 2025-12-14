"""
API Endpoints pour le Bot IA Conversationnel

Endpoints:
- POST /api/bot/chat - Envoyer un message au bot
- GET /api/bot/conversations - Historique des conversations
- DELETE /api/bot/conversations/{id} - Supprimer une conversation
- POST /api/bot/feedback - Feedback sur une réponse
- GET /api/bot/suggestions - Suggestions contextuelles
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import structlog

from services.ai_bot_service import (
    AIBotService,
    ConversationContext,
    BotLanguage,
    Message,
    MessageRole,
    create_conversation_context
)
from auth import get_current_user
from supabase_client import supabase

router = APIRouter(prefix="/api/bot", tags=["AI Bot"])
logger = structlog.get_logger()

# ============================================
# MODÈLES PYDANTIC
# ============================================

class ChatRequest(BaseModel):
    """Requête pour envoyer un message au bot"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message utilisateur")
    language: Optional[str] = Field("fr", description="Langue (fr, en, ar)")
    session_id: Optional[str] = Field(None, description="ID de session pour continuer conversation")


class ChatResponse(BaseModel):
    """Réponse du bot"""
    bot_response: str
    session_id: str
    timestamp: datetime
    intent_detected: Optional[str] = None
    action_executed: Optional[dict] = None
    suggestions: Optional[List[str]] = None


class ConversationHistoryResponse(BaseModel):
    """Historique d'une conversation"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    messages: List[dict]


class FeedbackRequest(BaseModel):
    """Feedback sur une réponse du bot"""
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    comment: Optional[str] = Field(None, max_length=500)


class SuggestionResponse(BaseModel):
    """Suggestions contextuelles"""
    suggestions: List[str]
    category: str


# ============================================
# FONCTIONS DE STOCKAGE SUPABASE
# ============================================

async def get_conversation_from_db(session_id: str) -> Optional[dict]:
    """Récupère une conversation depuis Supabase"""
    try:
        result = supabase.table("bot_conversations")\
            .select("*")\
            .eq("session_id", session_id)\
            .single()\
            .execute()
        return result.data
    except Exception:
        return None

async def save_conversation_to_db(session_id: str, user_id: str, messages: List[dict], language: str = "fr"):
    """Sauvegarde une conversation dans Supabase"""
    try:
        existing = await get_conversation_from_db(session_id)

        data = {
            "session_id": session_id,
            "user_id": user_id,
            "messages": messages,
            "language": language,
            "updated_at": datetime.utcnow().isoformat()
        }

        if existing:
            supabase.table("bot_conversations")\
                .update(data)\
                .eq("session_id", session_id)\
                .execute()
        else:
            data["created_at"] = datetime.utcnow().isoformat()
            supabase.table("bot_conversations").insert(data).execute()
    except Exception as e:
        logger.error("save_conversation_error", error=str(e), session_id=session_id)

async def delete_conversation_from_db(session_id: str):
    """Supprime une conversation de Supabase"""
    try:
        supabase.table("bot_conversations")\
            .delete()\
            .eq("session_id", session_id)\
            .execute()
    except Exception as e:
        logger.error("delete_conversation_error", error=str(e), session_id=session_id)

# Cache en mémoire pour les sessions actives (optimisation)
conversations_cache = {}


# ============================================
# ENDPOINTS
# ============================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Converser avec le bot IA

    Le bot peut:
    - Répondre aux questions
    - Exécuter des actions (créer affiliation, stats, etc.)
    - Guider l'utilisateur
    - Proposer des suggestions
    """
    try:
        user_id = current_user["id"]
        user_role = current_user.get("role", "influencer")

        # Récupérer ou créer contexte
        session_id = request.session_id or f"{user_id}_{datetime.utcnow().timestamp()}"

        # Essayer de récupérer du cache, sinon de la DB
        context = None
        if session_id in conversations_cache:
            context = conversations_cache[session_id]
        else:
            # Chercher dans Supabase
            db_conv = await get_conversation_from_db(session_id)
            if db_conv:
                context = create_conversation_context(
                    user_id=user_id,
                    user_role=user_role,
                    language=db_conv.get("language", request.language)
                )
                context.session_id = session_id
                # Restaurer les messages
                for msg in db_conv.get("messages", []):
                    context.messages.append(Message(
                        role=MessageRole(msg["role"]),
                        content=msg["content"],
                        timestamp=datetime.fromisoformat(msg["timestamp"]) if msg.get("timestamp") else datetime.utcnow()
                    ))

        if not context:
            context = create_conversation_context(
                user_id=user_id,
                user_role=user_role,
                language=request.language
            )
            context.session_id = session_id

        conversations_cache[session_id] = context

        # Créer le service bot
        bot = AIBotService()

        # Envoyer le message
        bot_response, action = await bot.chat(request.message, context)

        # Sauvegarder dans Supabase
        messages_to_save = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in context.messages
        ]
        await save_conversation_to_db(session_id, user_id, messages_to_save, request.language)

        # Générer suggestions contextuelles
        suggestions = _generate_suggestions(context, current_user)

        logger.info(
            "bot_chat",
            user_id=user_id,
            session_id=session_id,
            message_length=len(request.message)
        )

        return ChatResponse(
            bot_response=bot_response,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            intent_detected=context.messages[-2].metadata.get("intent") if len(context.messages) >= 2 else None,
            action_executed=action.__dict__ if action else None,
            suggestions=suggestions
        )

    except Exception as e:
        logger.error("bot_chat_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la communication avec le bot"
        )


@router.get("/conversations", response_model=List[ConversationHistoryResponse])
async def get_conversations(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer l'historique des conversations de l'utilisateur
    """
    try:
        user_id = current_user["id"]

        # Récupérer depuis Supabase
        result = supabase.table("bot_conversations")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("updated_at", desc=True)\
            .limit(limit)\
            .execute()

        conversations = result.data or []

        # Formater réponse
        response = []
        for conv in conversations:
            messages = conv.get("messages", [])
            if not messages:
                continue

            response.append(ConversationHistoryResponse(
                session_id=conv.get("session_id"),
                created_at=datetime.fromisoformat(conv.get("created_at", datetime.utcnow().isoformat())),
                updated_at=datetime.fromisoformat(conv.get("updated_at", datetime.utcnow().isoformat())),
                message_count=len(messages),
                messages=messages
            ))

        return response

    except Exception as e:
        logger.error("get_conversations_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des conversations"
        )


@router.get("/conversations/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer une conversation spécifique
    """
    try:
        # Récupérer depuis Supabase
        conv = await get_conversation_from_db(session_id)

        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation non trouvée"
            )

        # Vérifier que la conversation appartient à l'utilisateur
        if conv.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à cette conversation"
            )

        messages = conv.get("messages", [])

        return ConversationHistoryResponse(
            session_id=conv.get("session_id"),
            created_at=datetime.fromisoformat(conv.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(conv.get("updated_at", datetime.utcnow().isoformat())),
            message_count=len(messages),
            messages=messages
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_conversation_error", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de la conversation"
        )


@router.delete("/conversations/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer une conversation
    """
    try:
        # Vérifier que la conversation existe et appartient à l'utilisateur
        conv = await get_conversation_from_db(session_id)

        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation non trouvée"
            )

        # Vérifier propriété
        if conv.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )

        # Supprimer de Supabase
        await delete_conversation_from_db(session_id)

        # Supprimer du cache si présent
        if session_id in conversations_cache:
            del conversations_cache[session_id]

        logger.info("conversation_deleted", session_id=session_id, user_id=current_user["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_conversation_error", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        )


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Soumettre un feedback sur une réponse du bot

    Utilisé pour améliorer le bot via fine-tuning
    """
    try:
        # Sauvegarder feedback dans Supabase
        feedback_data = {
            "user_id": current_user["id"],
            "session_id": feedback.session_id,
            "message_id": feedback.message_id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "created_at": datetime.utcnow().isoformat()
        }

        supabase.table("bot_feedback").insert(feedback_data).execute()

        logger.info(
            "bot_feedback_received",
            user_id=current_user["id"],
            session_id=feedback.session_id,
            rating=feedback.rating
        )

        return {
            "status": "success",
            "message": "Merci pour votre feedback!"
        }

    except Exception as e:
        logger.error("feedback_error", error=str(e), user_id=current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la soumission du feedback"
        )


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir des suggestions contextuelles

    Suggestions basées sur:
    - Rôle utilisateur
    - État du compte
    - Actions récentes
    """
    try:
        suggestions = _generate_suggestions(None, current_user)

        return SuggestionResponse(
            suggestions=suggestions,
            category="general"
        )

    except Exception as e:
        logger.error("suggestions_error", error=str(e), user_id=current_user["id"])
        return SuggestionResponse(suggestions=[], category="general")


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def _generate_suggestions(
    context: Optional[ConversationContext],
    current_user: dict
) -> List[str]:
    """
    Génère des suggestions contextuelles pour l'utilisateur
    """
    role = current_user.get("role", "influencer")

    if role == "influencer":
        return [
            "📊 Voir mes statistiques",
            "🔗 Créer un lien d'affiliation",
            "📱 Connecter mes réseaux sociaux",
            "💰 Vérifier mon solde",
            "📈 Conseils pour augmenter mes ventes"
        ]
    elif role == "merchant":
        return [
            "📦 Ajouter un produit",
            "👥 Voir les demandes d'affiliation",
            "📊 Analyser mes performances",
            "🔍 Rechercher des influenceurs",
            "💳 Gérer mon abonnement"
        ]
    else:
        return [
            "❓ Comment ça marche?",
            "💰 Quels sont les tarifs?",
            "📱 Connecter mes réseaux sociaux",
            "📝 Créer mon compte"
        ]


# ============================================
# WEBHOOK POUR PLATEFORMES EXTERNES
# ============================================

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: dict):
    """
    Webhook pour intégration WhatsApp Business

    Permet de répondre aux messages WhatsApp via le bot
    """
    # TODO: Implémenter intégration WhatsApp Business API
    return {"status": "not_implemented"}


@router.post("/webhook/messenger")
async def messenger_webhook(request: dict):
    """
    Webhook pour intégration Facebook Messenger

    Permet de répondre aux messages Messenger via le bot
    """
    # TODO: Implémenter intégration Messenger
    return {"status": "not_implemented"}


@router.post("/webhook/telegram")
async def telegram_webhook(request: dict):
    """
    Webhook pour intégration Telegram

    Permet de répondre aux messages Telegram via le bot
    """
    # TODO: Implémenter intégration Telegram Bot API
    return {"status": "not_implemented"}
