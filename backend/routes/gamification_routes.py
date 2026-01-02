"""
Routes Gamification
Badges, Achievements, Points, Levels, Leaderboard
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gamification", tags=["Gamification"])


# ============================================
# BADGES SYSTEM
# ============================================

AVAILABLE_BADGES = {
    "first_sale": {
        "id": "first_sale",
        "name": "First Sale",
        "name_fr": "Première Vente",
        "description": "Made your first sale",
        "icon": "🎯",
        "points": 100,
        "criteria": {"sales_count": 1}
    },
    "top_seller": {
        "id": "top_seller",
        "name": "Top Seller",
        "name_fr": "Vendeur Expert",
        "description": "Achieved 100 sales",
        "icon": "🏆",
        "points": 1000,
        "criteria": {"sales_count": 100}
    },
    "revenue_milestone_1k": {
        "id": "revenue_milestone_1k",
        "name": "1K Revenue",
        "name_fr": "1000 MAD de Revenu",
        "description": "Earned 1000 MAD in revenue",
        "icon": "💰",
        "points": 500,
        "criteria": {"total_revenue": 1000}
    },
    "social_butterfly": {
        "id": "social_butterfly",
        "name": "Social Butterfly",
        "name_fr": "Papillon Social",
        "description": "Connected 3+ social media accounts",
        "icon": "🦋",
        "points": 200,
        "criteria": {"social_connections": 3}
    },
    "team_builder": {
        "id": "team_builder",
        "name": "Team Builder",
        "name_fr": "Bâtisseur d'Équipe",
        "description": "Invited 5+ team members",
        "icon": "👥",
        "points": 300,
        "criteria": {"team_members": 5}
    },
    "content_creator": {
        "id": "content_creator",
        "name": "Content Creator",
        "name_fr": "Créateur de Contenu",
        "description": "Published 50+ social media posts",
        "icon": "✍️",
        "points": 400,
        "criteria": {"posts_count": 50}
    },
    "early_adopter": {
        "id": "early_adopter",
        "name": "Early Adopter",
        "name_fr": "Adopteur Précoce",
        "description": "Joined in the first month",
        "icon": "🚀",
        "points": 150,
        "criteria": {"joined_before": "2025-02-01"}
    },
    "referral_champion": {
        "id": "referral_champion",
        "name": "Referral Champion",
        "name_fr": "Champion du Parrainage",
        "description": "Referred 10+ users",
        "icon": "🎁",
        "points": 600,
        "criteria": {"referrals": 10}
    }
}


@router.get("/badges")
async def get_badges(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste de tous les badges disponibles
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer les badges de l'utilisateur
        user_badges = supabase.table('user_badges').select('badge_id, earned_at').eq('user_id', user_id).execute()

        earned_badge_ids = {b['badge_id'] for b in (user_badges.data or [])}

        # Enrichir la liste
        result = []
        for badge_id, badge in AVAILABLE_BADGES.items():
            is_earned = badge_id in earned_badge_ids

            earned_at = None
            if is_earned:
                for ub in (user_badges.data or []):
                    if ub['badge_id'] == badge_id:
                        earned_at = ub.get('earned_at')
                        break

            result.append({
                **badge,
                'earned': is_earned,
                'earned_at': earned_at
            })

        return {
            "success": True,
            "badges": result,
            "total": len(result),
            "earned": len(earned_badge_ids)
        }

    except Exception as e:
        logger.error(f"Error getting badges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/badges/earned")
async def get_earned_badges(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Badges gagnés par l'utilisateur
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        user_badges = supabase.table('user_badges').select('*').eq('user_id', user_id).order('earned_at', desc=True).execute()

        # Enrichir avec les infos du badge
        result = []
        for ub in (user_badges.data or []):
            badge_id = ub.get('badge_id')
            if badge_id in AVAILABLE_BADGES:
                result.append({
                    **AVAILABLE_BADGES[badge_id],
                    'earned_at': ub.get('earned_at')
                })

        return {
            "success": True,
            "badges": result,
            "total": len(result)
        }

    except Exception as e:
        logger.error(f"Error getting earned badges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ACHIEVEMENTS SYSTEM
# ============================================

@router.get("/achievements")
async def get_achievements(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des accomplissements (achievements)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Calculer les accomplissements basés sur les données réelles
        achievements = []

        # Ventes
        conversions = supabase.table('conversions').select('*', count='exact').eq('influencer_id', user_id).execute()
        sales_count = conversions.count if hasattr(conversions, 'count') else len(conversions.data or [])

        achievements.append({
            "id": "sales_milestone",
            "name": "Sales Milestone",
            "description": f"{sales_count} sales completed",
            "icon": "📈",
            "progress": sales_count,
            "target": 100,
            "completed": sales_count >= 100
        })

        # Revenue
        conversions_data = conversions.data or []
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in conversions_data)

        achievements.append({
            "id": "revenue_milestone",
            "name": "Revenue Milestone",
            "description": f"{float(total_revenue)} MAD earned",
            "icon": "💵",
            "progress": float(total_revenue),
            "target": 10000,
            "completed": total_revenue >= 10000
        })

        # Produits
        products = supabase.table('products').select('*', count='exact').eq('merchant_id', user_id).execute()
        products_count = products.count if hasattr(products, 'count') else len(products.data or [])

        achievements.append({
            "id": "product_catalog",
            "name": "Product Catalog",
            "description": f"{products_count} products added",
            "icon": "🛍️",
            "progress": products_count,
            "target": 50,
            "completed": products_count >= 50
        })

        # Connexions sociales
        social_connections = supabase.table('social_media_connections').select('*', count='exact').eq('user_id', user_id).eq('status', 'connected').execute()
        social_count = social_connections.count if hasattr(social_connections, 'count') else len(social_connections.data or [])

        achievements.append({
            "id": "social_presence",
            "name": "Social Presence",
            "description": f"{social_count} social accounts connected",
            "icon": "📱",
            "progress": social_count,
            "target": 4,
            "completed": social_count >= 4
        })

        return {
            "success": True,
            "achievements": achievements,
            "total": len(achievements),
            "completed": sum(1 for a in achievements if a['completed'])
        }

    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POINTS & LEVELS
# ============================================

@router.get("/points")
async def get_points(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Points et niveau de l'utilisateur
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer les points depuis la table gamification
        try:
            gamif_data = supabase.table('gamification').select('points, level').eq('user_id', user_id).single().execute()

            if gamif_data.data:
                current_points = gamif_data.data.get('points', 0)
                current_level = gamif_data.data.get('level', 1)
            else:
                current_points = 0
                current_level = 1
        except Exception:
            current_points = 0
            current_level = 1

        # Calculer le niveau basé sur les points
        # Formule: level = floor(sqrt(points / 100))
        import math
        calculated_level = max(1, int(math.sqrt(current_points / 100)))

        # Points pour le prochain niveau
        next_level = calculated_level + 1
        points_for_next = (next_level ** 2) * 100
        points_progress = current_points - ((calculated_level ** 2) * 100)
        points_needed = points_for_next - current_points

        # Badges points
        badges = supabase.table('user_badges').select('badge_id').eq('user_id', user_id).execute()
        badge_points = sum(AVAILABLE_BADGES.get(b['badge_id'], {}).get('points', 0) for b in (badges.data or []))

        return {
            "success": True,
            "points": current_points,
            "badge_points": badge_points,
            "level": calculated_level,
            "next_level": next_level,
            "points_for_next_level": points_for_next,
            "points_progress": points_progress,
            "points_needed": points_needed,
            "level_name": get_level_name(calculated_level)
        }

    except Exception as e:
        logger.error(f"Error getting points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_level_name(level: int) -> str:
    """Obtenir le nom du niveau"""
    if level < 5:
        return "Novice"
    elif level < 10:
        return "Bronze"
    elif level < 20:
        return "Silver"
    elif level < 35:
        return "Gold"
    elif level < 50:
        return "Platinum"
    else:
        return "Diamond"


# ============================================
# LEADERBOARD
# ============================================

@router.get("/leaderboard")
async def get_leaderboard(
    period: str = "all",  # all, month, week
    metric: str = "points",  # points, sales, revenue
    limit: int = 100
):
    """
    Classement des utilisateurs
    """
    try:
        if metric == "points":
            # Leaderboard par points
            leaderboard = supabase.table('gamification').select('user_id, points, level').order('points', desc=True).limit(limit).execute()

            result = []
            rank = 1
            for entry in (leaderboard.data or []):
                user_id = entry.get('user_id')

                # Enrichir avec infos utilisateur
                try:
                    profile = supabase.table('profiles').select('full_name, avatar_url').eq('user_id', user_id).single().execute()
                except Exception:
                    pass  # .single() might return no results

                result.append({
                    'rank': rank,
                    'user_id': user_id,
                    'full_name': profile.data.get('full_name') if profile.data else 'Anonymous',
                    'avatar_url': profile.data.get('avatar_url') if profile.data else None,
                    'points': entry.get('points', 0),
                    'level': entry.get('level', 1)
                })

                rank += 1

        elif metric == "sales":
            # Leaderboard par nombre de ventes
            from datetime import timedelta

            if period == "month":
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            elif period == "week":
                start_date = (datetime.now() - timedelta(days=7)).isoformat()
            else:
                start_date = None

            # Compter les conversions par influenceur
            # TODO: Utiliser une query plus efficace avec COUNT GROUP BY
            all_conversions = supabase.table('conversions').select('influencer_id').execute()

            sales_by_user = {}
            for conv in (all_conversions.data or []):
                influencer_id = conv.get('influencer_id')
                if influencer_id:
                    sales_by_user[influencer_id] = sales_by_user.get(influencer_id, 0) + 1

            # Trier
            sorted_users = sorted(sales_by_user.items(), key=lambda x: x[1], reverse=True)[:limit]

            result = []
            rank = 1
            for user_id, sales_count in sorted_users:
                try:
                    profile = supabase.table('profiles').select('full_name, avatar_url').eq('user_id', user_id).single().execute()
                except Exception:
                    pass  # .single() might return no results

                result.append({
                    'rank': rank,
                    'user_id': user_id,
                    'full_name': profile.data.get('full_name') if profile.data else 'Anonymous',
                    'avatar_url': profile.data.get('avatar_url') if profile.data else None,
                    'sales': sales_count
                })

                rank += 1

        elif metric == "revenue":
            # Leaderboard par revenue
            # TODO: Implémenter
            result = []

        else:
            raise HTTPException(status_code=400, detail="Metric invalide")

        return {
            "success": True,
            "period": period,
            "metric": metric,
            "leaderboard": result,
            "total": len(result)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AWARD POINTS (INTERNAL)
# ============================================

async def award_points(user_id: str, points: int, reason: str):
    """
    Attribuer des points à un utilisateur (fonction interne)
    """
    try:
        # Récupérer les points actuels
        current = supabase.table('gamification').select('points, level').eq('user_id', user_id).execute()

        if current.data:
            new_points = current.data[0].get('points', 0) + points

            # Calculer nouveau niveau
            import math
            new_level = max(1, int(math.sqrt(new_points / 100)))

            # Update
            supabase.table('gamification').update({
                'points': new_points,
                'level': new_level,
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).execute()
        else:
            # Créer
            supabase.table('gamification').insert({
                'user_id': user_id,
                'points': points,
                'level': 1
            }).execute()

        # Log l'attribution
        supabase.table('points_history').insert({
            'user_id': user_id,
            'points': points,
            'reason': reason,
            'created_at': datetime.now().isoformat()
        }).execute()

        logger.info(f"Awarded {points} points to user {user_id}: {reason}")

    except Exception as e:
        logger.error(f"Error awarding points: {e}")
