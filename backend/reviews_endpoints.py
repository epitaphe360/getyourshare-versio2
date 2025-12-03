"""
Review Management Endpoints - Python/FastAPI
Gestion avancée des avis avec modération IA
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from db_helpers import get_db_connection, get_current_user
import logging
import re

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ReviewCreate(BaseModel):
    product_id: str
    customer_name: str
    customer_email: Optional[str] = None
    rating: int  # 1-5
    title: Optional[str] = None
    comment: Optional[str] = None
    verified_purchase: bool = False
    order_id: Optional[str] = None
    images: List[str] = []

class ReviewResponse(BaseModel):
    response_text: str

class ReviewModeration(BaseModel):
    status: str  # approved, rejected, flagged
    reason: Optional[str] = None

# ============================================================================
# AI MODERATION HELPERS
# ============================================================================

def analyze_sentiment(text: str) -> str:
    """Analyse de sentiment simple"""
    if not text:
        return "neutral"

    text_lower = text.lower()

    # Mots positifs
    positive_words = ['excellent', 'parfait', 'super', 'génial', 'incroyable', 'top',
                     'merveilleux', 'fantastique', 'recommande', 'satisfait', 'content',
                     'great', 'amazing', 'awesome', 'love', 'best', 'perfect']

    # Mots négatifs
    negative_words = ['mauvais', 'terrible', 'nul', 'horrible', 'décevant', 'arnaque',
                     'pire', 'médiocre', 'insatisfait', 'déçu', 'problème',
                     'bad', 'terrible', 'awful', 'worst', 'disappointed', 'poor']

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    return "neutral"

def detect_spam_score(text: str, email: Optional[str] = None) -> float:
    """Détection de spam (0-1, 1 = spam certain)"""
    if not text:
        return 0.0

    score = 0.0
    text_lower = text.lower()

    # Patterns de spam
    spam_patterns = [
        r'http[s]?://',  # URLs
        r'www\.',
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
        r'click here',
        r'buy now',
        r'limited offer',
        r'act now',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone numbers
    ]

    for pattern in spam_patterns:
        if re.search(pattern, text_lower):
            score += 0.2

    # Répétitions excessives
    words = text_lower.split()
    if len(words) > 0:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.5:  # Beaucoup de répétitions
            score += 0.3

    # Majuscules excessives
    if len(text) > 0:
        upper_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if upper_ratio > 0.5:
            score += 0.2

    return min(score, 1.0)

def detect_profanity(text: str) -> bool:
    """Détection de langage inapproprié"""
    if not text:
        return False

    profanity_words = [
        'fuck', 'shit', 'damn', 'ass', 'bitch',
        'merde', 'putain', 'con', 'connard', 'salaud'
    ]

    text_lower = text.lower()
    return any(word in text_lower for word in profanity_words)

def detect_issues(review_data: dict) -> List[str]:
    """Détection d'anomalies"""
    issues = []

    comment = review_data.get('comment', '')
    rating = review_data.get('rating', 3)
    sentiment = review_data.get('sentiment', 'neutral')

    # Incohérence rating/sentiment
    if rating >= 4 and sentiment == 'negative':
        issues.append('rating_sentiment_mismatch')
    elif rating <= 2 and sentiment == 'positive':
        issues.append('rating_sentiment_mismatch')

    # Commentaire trop court
    if comment and len(comment) < 20:
        issues.append('short_comment')

    # Langage inapproprié
    if detect_profanity(comment):
        issues.append('profanity_detected')

    # Email suspect
    email = review_data.get('customer_email', '')
    if email and any(domain in email.lower() for domain in ['tempmail', 'throwaway', '10minutemail']):
        issues.append('suspicious_email')

    return issues

def moderate_review(review_data: dict) -> dict:
    """Modération automatique avec IA"""
    comment = review_data.get('comment', '')

    # Analyse sentiment
    sentiment = analyze_sentiment(comment)

    # Détection spam
    spam_score = detect_spam_score(comment, review_data.get('customer_email'))

    # Détection d'anomalies
    temp_data = {**review_data, 'sentiment': sentiment}
    detected_issues = detect_issues(temp_data)

    # Score de confiance (1 = haute confiance)
    moderation_score = 1.0 - spam_score
    if len(detected_issues) > 0:
        moderation_score -= len(detected_issues) * 0.15
    moderation_score = max(0.0, min(1.0, moderation_score))

    # Recommandation
    if spam_score > 0.7 or 'profanity_detected' in detected_issues:
        recommended_action = 'reject'
    elif moderation_score > 0.7 and len(detected_issues) == 0:
        recommended_action = 'approve'
    else:
        recommended_action = 'review'

    return {
        'sentiment': sentiment,
        'spam_score': round(spam_score, 2),
        'detected_issues': detected_issues,
        'moderation_score': round(moderation_score, 2),
        'recommended_action': recommended_action
    }

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/reviews")
async def create_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouvel avis (avec modération IA automatique)"""
    try:
        supabase = get_db_connection()

        # Préparer les données
        review_data = review.dict()
        review_data['customer_id'] = current_user.get('id')

        # Modération IA
        moderation = moderate_review({
            'comment': review.comment,
            'rating': review.rating,
            'customer_email': review.customer_email
        })

        # Ajouter les résultats de modération
        review_data.update({
            'sentiment': moderation['sentiment'],
            'spam_score': moderation['spam_score'],
            'detected_issues': moderation['detected_issues'],
            'moderation_score': moderation['moderation_score'],
            'recommended_action': moderation['recommended_action'],
            'auto_moderated': True,
            'status': 'approved' if moderation['recommended_action'] == 'approve' else 'pending'
        })

        result = supabase.table('reviews').insert(review_data).execute()

        return {
            "success": True,
            "review": result.data[0] if result.data else None,
            "moderation": moderation,
            "message": "Merci pour votre avis! Il sera publié après modération." if moderation['recommended_action'] != 'approve' else "Merci pour votre avis!"
        }

    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews")
async def get_reviews(
    merchant_id: Optional[str] = None,
    product_id: Optional[str] = None,
    status: Optional[str] = None,
    rating: Optional[int] = None,
    sentiment: Optional[str] = None,
    requires_attention: bool = False,
    no_response: bool = False,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les avis d'un marchand"""
    try:
        supabase = get_db_connection()

        # Base query - merchant sees their own reviews
        query = supabase.table('reviews').select('*')

        # Si merchant_id n'est pas fourni, utiliser l'ID de l'utilisateur connecté
        if not merchant_id:
            merchant_id = current_user['id']

        query = query.eq('merchant_id', merchant_id)

        # Filtres
        if product_id:
            query = query.eq('product_id', product_id)
        if status:
            query = query.eq('status', status)
        if rating:
            query = query.eq('rating', rating)
        if sentiment:
            query = query.eq('sentiment', sentiment)
        if requires_attention:
            query = query.or_('status.eq.flagged,spam_score.gt.0.5')
        if no_response:
            query = query.is_('merchant_response', 'null')

        result = query.order('created_at', desc=True).limit(limit).execute()

        return {
            "success": True,
            "reviews": result.data or [],
            "count": len(result.data) if result.data else 0
        }

    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews/statistics")
async def get_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les statistiques des avis"""
    try:
        supabase = get_db_connection()

        # Récupérer tous les avis du marchand
        result = supabase.table('reviews').select('*').eq(
            'merchant_id', current_user['id']
        ).execute()

        reviews = result.data or []

        # Calculer les statistiques
        total = len(reviews)

        if total == 0:
            return {
                "success": True,
                "statistics": {
                    "total": 0,
                    "average_rating": 0,
                    "pending": 0,
                    "approved": 0,
                    "rejected": 0,
                    "flagged": 0,
                    "requires_attention": 0,
                    "no_response": 0,
                    "by_rating": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    "by_sentiment": {"positive": 0, "neutral": 0, "negative": 0},
                    "verified_purchases": 0,
                    "spam_detected": 0
                }
            }

        # Statistiques
        stats = {
            "total": total,
            "average_rating": sum(r.get('rating', 0) for r in reviews) / total,
            "pending": len([r for r in reviews if r.get('status') == 'pending']),
            "approved": len([r for r in reviews if r.get('status') == 'approved']),
            "rejected": len([r for r in reviews if r.get('status') == 'rejected']),
            "flagged": len([r for r in reviews if r.get('status') == 'flagged']),
            "requires_attention": len([r for r in reviews if r.get('status') in ['flagged', 'pending'] or r.get('spam_score', 0) > 0.5]),
            "no_response": len([r for r in reviews if not r.get('merchant_response')]),
            "by_rating": {},
            "by_sentiment": {"positive": 0, "neutral": 0, "negative": 0},
            "verified_purchases": len([r for r in reviews if r.get('verified_purchase')]),
            "spam_detected": len([r for r in reviews if r.get('spam_score', 0) > 0.7])
        }

        # Distribution par rating
        for rating in range(1, 6):
            stats["by_rating"][rating] = len([r for r in reviews if r.get('rating') == rating])

        # Distribution par sentiment
        for sentiment in ['positive', 'neutral', 'negative']:
            stats["by_sentiment"][sentiment] = len([r for r in reviews if r.get('sentiment') == sentiment])

        return {
            "success": True,
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews/product/{product_id}")
async def get_product_reviews(
    product_id: str,
    limit: int = 20
):
    """Obtenir les avis d'un produit (public)"""
    try:
        supabase = get_db_connection()

        result = supabase.table('reviews').select('*').eq(
            'product_id', product_id
        ).eq('status', 'approved').eq('is_visible', True).order(
            'is_featured', desc=True
        ).order('created_at', desc=True).limit(limit).execute()

        return {
            "success": True,
            "reviews": result.data or [],
            "count": len(result.data) if result.data else 0
        }

    except Exception as e:
        logger.error(f"Error fetching product reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/{review_id}/respond")
async def respond_to_review(
    review_id: str,
    response: ReviewResponse,
    current_user: dict = Depends(get_current_user)
):
    """Répondre à un avis"""
    try:
        supabase = get_db_connection()

        # Vérifier que le review appartient au marchand
        check = supabase.table('reviews').select('id, merchant_id').eq(
            'id', review_id
        ).execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Review not found")

        if check.data[0]['merchant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Mettre à jour avec la réponse
        result = supabase.table('reviews').update({
            'merchant_response': response.response_text,
            'merchant_response_date': datetime.now().isoformat(),
            'responded_by': current_user['id']
        }).eq('id', review_id).execute()

        return {
            "success": True,
            "review": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error responding to review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Approuver un avis"""
    try:
        supabase = get_db_connection()

        # Vérifier que le review appartient au marchand
        check = supabase.table('reviews').select('id, merchant_id').eq(
            'id', review_id
        ).execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Review not found")

        if check.data[0]['merchant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Approuver
        result = supabase.table('reviews').update({
            'status': 'approved',
            'moderated_by': current_user['id'],
            'moderated_at': datetime.now().isoformat(),
            'is_visible': True
        }).eq('id', review_id).execute()

        return {
            "success": True,
            "review": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    moderation: ReviewModeration,
    current_user: dict = Depends(get_current_user)
):
    """Rejeter un avis"""
    try:
        supabase = get_db_connection()

        # Vérifier que le review appartient au marchand
        check = supabase.table('reviews').select('id, merchant_id').eq(
            'id', review_id
        ).execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Review not found")

        if check.data[0]['merchant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Rejeter
        result = supabase.table('reviews').update({
            'status': 'rejected',
            'rejection_reason': moderation.reason,
            'moderated_by': current_user['id'],
            'moderated_at': datetime.now().isoformat(),
            'is_visible': False
        }).eq('id', review_id).execute()

        return {
            "success": True,
            "review": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/{review_id}/remoderate")
async def remoderate_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Re-modérer un avis avec l'IA"""
    try:
        supabase = get_db_connection()

        # Récupérer l'avis
        result = supabase.table('reviews').select('*').eq('id', review_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = result.data[0]

        # Re-modération
        moderation = moderate_review({
            'comment': review.get('comment'),
            'rating': review.get('rating'),
            'customer_email': review.get('customer_email')
        })

        # Mettre à jour
        update_result = supabase.table('reviews').update({
            'sentiment': moderation['sentiment'],
            'spam_score': moderation['spam_score'],
            'detected_issues': moderation['detected_issues'],
            'moderation_score': moderation['moderation_score'],
            'recommended_action': moderation['recommended_action'],
            'auto_moderated': True
        }).eq('id', review_id).execute()

        return {
            "success": True,
            "review": update_result.data[0] if update_result.data else None,
            "moderation": moderation
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-moderating review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/{review_id}/helpful")
async def mark_helpful(review_id: str):
    """Marquer un avis comme utile (public)"""
    try:
        supabase = get_db_connection()

        # Récupérer l'avis
        result = supabase.table('reviews').select('helpful_count').eq('id', review_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        current_count = result.data[0].get('helpful_count', 0)

        # Incrémenter
        update_result = supabase.table('reviews').update({
            'helpful_count': current_count + 1
        }).eq('id', review_id).execute()

        return {
            "success": True,
            "helpful_count": current_count + 1
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking helpful: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/{review_id}/report")
async def report_review(review_id: str):
    """Signaler un avis (public)"""
    try:
        supabase = get_db_connection()

        # Récupérer l'avis
        result = supabase.table('reviews').select('report_count, status, merchant_id').eq('id', review_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = result.data[0]
        current_count = review.get('report_count', 0)
        new_count = current_count + 1

        # Si trop de signalements, marquer comme flagged
        update_data = {'report_count': new_count}
        if new_count >= 3 and review.get('status') == 'approved':
            update_data['status'] = 'flagged'

        # Incrémenter
        update_result = supabase.table('reviews').update(update_data).eq('id', review_id).execute()

        return {
            "success": True,
            "message": "Review reported successfully",
            "report_count": new_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting review: {e}")
        raise HTTPException(status_code=500, detail=str(e))
