"""
GAMIFICATION ENDPOINTS - Système complet de gamification
Tables utilisées: user_gamification, badges, missions, user_missions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from supabase_config import get_supabase_client

import logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# MODELS
# ============================================

class UserGamification(BaseModel):
    user_id: str
    total_points: int
    level: int
    experience: int
    achievements: List[str]
    last_updated: Optional[datetime] = None

class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon_url: Optional[str] = None
    points_reward: int
    category: str
    requirements: dict
    rarity: str

class Mission(BaseModel):
    id: str
    title: str
    description: str
    mission_type: str
    criteria: dict
    points_reward: int
    badge_id: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool

class UserMission(BaseModel):
    id: str
    user_id: str
    mission_id: str
    status: str
    progress: int
    completed_at: Optional[datetime] = None
    points_earned: int

# ============================================
# GET /api/gamification/profile
# Profil gamification de l'utilisateur
# ============================================
@router.get("/profile")
async def get_gamification_profile(
    user_id: str = Query(..., description="ID de l'utilisateur")
):
    """Récupère le profil gamification complet d'un utilisateur"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer gamification (colonnes existantes uniquement)
        # Schema actuel: user_id, total_points, level, experience, achievements, last_updated, created_at
        gamification = supabase.table('user_gamification')\
            .select('user_id, total_points, level, experience, achievements, last_updated, created_at')\
            .eq('user_id', user_id)\
            .limit(1)\
            .execute()
        
        if not gamification.data:
            # Créer profil si inexistant
            new_profile = {
                'user_id': user_id,
                'total_points': 0,
                'level': 1,
                'experience': 0,
                'achievements': [],
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            try:
                gamification = supabase.table('user_gamification').insert(new_profile).execute()
                profile_data = gamification.data[0]
            except Exception as e:
                # Fallback: Si l'insertion échoue (ex: contrainte FK si user pas dans auth.users),
                # on retourne le profil en mémoire pour ne pas bloquer l'UI.
                print(f"Warning: Could not create gamification profile in DB: {e}")
                profile_data = new_profile
        else:
            profile_data = gamification.data[0]
        
        # Récupérer badges gagnés (via user_missions ou achievements)
        # Note: user_missions might rely on badges table which might not exist or be linked differently
        # For now, we'll try to fetch from user_missions if possible, but wrap in try/except or check schema
        earned_badges_data = []
        try:
            earned_badges = supabase.table('user_missions')\
                .select('mission_id, missions(badge_id, badges(*))')\
                .eq('user_id', user_id)\
                .eq('status', 'completed')\
                .not_.is_('missions.badge_id', 'null')\
                .execute()
            earned_badges_data = [b['missions']['badges'] for b in earned_badges.data if b.get('missions', {}).get('badges')]
        except Exception as e:
            # Fallback if user_missions/badges tables have issues
            logger.debug(f"Failed to get earned badges: {e}")
            pass
        
        # Récupérer missions actives
        active_missions_data = []
        try:
            active_missions = supabase.table('user_missions')\
                .select('*, missions(*)')\
                .eq('user_id', user_id)\
                .eq('status', 'in_progress')\
                .execute()
            active_missions_data = active_missions.data
        except Exception as e:
            logger.debug(f"Failed to get active missions: {e}")
            pass
        
        # Calculer progression vers prochain niveau
        current_points = profile_data.get('total_points', 0)
        current_level_num = profile_data.get('level', 1)
        
        # Mapping niveau numérique -> nom
        level_names = {1: 'bronze', 2: 'silver', 3: 'gold', 4: 'platinum', 5: 'diamond'}
        level_name = level_names.get(current_level_num, 'bronze')
        if current_level_num > 5: level_name = 'legend'

        # Logique simple de niveaux: 1000 pts par niveau
        next_level_points = current_level_num * 1000
        prev_level_points = (current_level_num - 1) * 1000
        
        points_in_level = current_points - prev_level_points
        points_needed = next_level_points - prev_level_points
        
        progress_percentage = (points_in_level / points_needed) * 100 if points_needed > 0 else 100
        
        # Adapter la réponse au format attendu par le frontend
        response_profile = {
            **profile_data,
            "current_level": level_name, # Champ attendu par le frontend
            "level_points": points_in_level, # Champ attendu
            "badges_earned": len(profile_data.get('achievements', [])) + len(earned_badges_data), # Champ attendu
            "missions_completed": 0, # Pas de colonne pour ça, on met 0 ou on compte
            "streak_days": 0, # Pas de colonne
            "next_level_points": next_level_points,
            "progress_percentage": round(progress_percentage, 1)
        }
        
        return {
            "success": True,
            "profile": response_profile,
            "earned_badges": earned_badges_data,
            "active_missions": active_missions_data,
            "stats": {
                "total_badges": len(earned_badges_data),
                "active_missions_count": len(active_missions_data),
                "achievements_count": len(profile_data.get('achievements', []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/gamification/leaderboard
# Classement des utilisateurs par points
# ============================================
@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(50, description="Nombre d'utilisateurs"),
    role: Optional[str] = Query(None, description="Filtrer par rôle (merchant, influencer, commercial)")
):
    """Récupère le classement des utilisateurs"""
    try:
        supabase = get_supabase_client()
        
        # 1. Récupérer le leaderboard (colonnes existantes)
        query = supabase.table('user_gamification')\
            .select('user_id, total_points, level, achievements')\
            .order('total_points', desc=True)\
            .limit(limit)
        
        response = query.execute()
        leaderboard_data = response.data
        
        if not leaderboard_data:
            return {"success": True, "leaderboard": [], "total": 0}
            
        # 2. Récupérer les infos utilisateurs
        user_ids = [entry['user_id'] for entry in leaderboard_data]
        
        users_response = supabase.table('users')\
            .select('id, first_name, last_name, email, role, avatar_url')\
            .in_('id', user_ids)\
            .execute()
            
        users_map = {u['id']: u for u in users_response.data}
        
        # 3. Combiner les données
        final_leaderboard = []
        for entry in leaderboard_data:
            user = users_map.get(entry['user_id'], {})
            
            # Filtrer par rôle si demandé
            if role and user.get('role') != role:
                continue
                
            entry['users'] = user
            final_leaderboard.append(entry)
        
        # Ajouter rang
        for i, entry in enumerate(final_leaderboard):
            entry['rank'] = i + 1
        
        return {
            "success": True,
            "leaderboard": final_leaderboard,
            "total": len(final_leaderboard)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/gamification/badges
# Liste tous les badges disponibles
# ============================================
@router.get("/badges")
async def get_all_badges(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    rarity: Optional[str] = Query(None, description="Filtrer par rareté")
):
    """Récupère tous les badges disponibles"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('badges').select('*')
        
        if category:
            query = query.eq('category', category)
        if rarity:
            query = query.eq('rarity', rarity)
        
        response = query.order('points_reward', desc=True).execute()
        
        # Grouper par catégorie
        badges_by_category = {}
        for badge in response.data:
            cat = badge['category']
            if cat not in badges_by_category:
                badges_by_category[cat] = []
            badges_by_category[cat].append(badge)
        
        return {
            "success": True,
            "badges": response.data,
            "total": len(response.data),
            "by_category": badges_by_category,
            "categories": list(badges_by_category.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/gamification/badges/earned
# Badges gagnés par l'utilisateur
# ============================================
@router.get("/badges/earned")
async def get_earned_badges(
    user_id: str = Query(..., description="ID de l'utilisateur")
):
    """Récupère tous les badges gagnés par l'utilisateur"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer missions complétées avec badges
        completed_missions = supabase.table('user_missions')\
            .select('*, missions(*, badges(*))')\
            .eq('user_id', user_id)\
            .eq('status', 'completed')\
            .execute()
        
        earned_badges = []
        total_points = 0
        
        for mission in completed_missions.data:
            if mission.get('missions', {}).get('badge_id'):
                badge = mission['missions']['badges']
                if badge:
                    earned_badges.append({
                        **badge,
                        'earned_at': mission['completed_at'],
                        'mission_title': mission['missions']['title']
                    })
                    total_points += badge['points_reward']
        
        # Grouper par rareté
        by_rarity = {}
        for badge in earned_badges:
            rarity = badge['rarity']
            if rarity not in by_rarity:
                by_rarity[rarity] = []
            by_rarity[rarity].append(badge)
        
        return {
            "success": True,
            "earned_badges": earned_badges,
            "total_earned": len(earned_badges),
            "total_points_from_badges": total_points,
            "by_rarity": by_rarity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/gamification/missions
# Liste toutes les missions disponibles
# ============================================
@router.get("/missions")
async def get_all_missions(
    is_active: bool = Query(True, description="Filtrer par missions actives"),
    mission_type: Optional[str] = Query(None, description="Filtrer par type")
):
    """Récupère toutes les missions disponibles"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('missions').select('*, badges(*)')
        
        if is_active:
            query = query.eq('is_active', True)
        if mission_type:
            query = query.eq('mission_type', mission_type)
        
        response = query.order('points_reward', desc=True).execute()
        
        # Grouper par type
        missions_by_type = {}
        for mission in response.data:
            mtype = mission['mission_type']
            if mtype not in missions_by_type:
                missions_by_type[mtype] = []
            missions_by_type[mtype].append(mission)
        
        return {
            "success": True,
            "missions": response.data,
            "total": len(response.data),
            "by_type": missions_by_type,
            "types": list(missions_by_type.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# GET /api/gamification/missions/active
# Missions actives de l'utilisateur
# ============================================
@router.get("/missions/active")
async def get_user_active_missions(
    user_id: str = Query(..., description="ID de l'utilisateur")
):
    """Récupère les missions actives de l'utilisateur"""
    try:
        supabase = get_supabase_client()
        
        # Missions en cours
        active = supabase.table('user_missions')\
            .select('*, missions(*, badges(*))')\
            .eq('user_id', user_id)\
            .eq('status', 'in_progress')\
            .execute()
        
        # Missions complétées
        completed = supabase.table('user_missions')\
            .select('*, missions(*, badges(*))')\
            .eq('user_id', user_id)\
            .eq('status', 'completed')\
            .execute()
        
        # Missions disponibles (non commencées)
        started_mission_ids = [m['mission_id'] for m in active.data + completed.data]
        
        available_query = supabase.table('missions')\
            .select('*, badges(*)')\
            .eq('is_active', True)
        
        if started_mission_ids:
            available_query = available_query.not_.in_('id', started_mission_ids)
        
        available = available_query.execute()
        
        return {
            "success": True,
            "active_missions": active.data,
            "completed_missions": completed.data,
            "available_missions": available.data,
            "stats": {
                "active_count": len(active.data),
                "completed_count": len(completed.data),
                "available_count": len(available.data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# POST /api/gamification/missions/{mission_id}/start
# Commencer une mission
# ============================================
@router.post("/missions/{mission_id}/start")
async def start_mission(
    mission_id: str,
    user_id: str = Query(..., description="ID de l'utilisateur")
):
    """Démarre une nouvelle mission pour l'utilisateur"""
    try:
        supabase = get_supabase_client()
        
        # Vérifier que la mission existe et est active
        mission = supabase.table('missions')\
            .select('*')\
            .eq('id', mission_id)\
            .eq('is_active', True)\
            .single()\
            .execute()
        
        if not mission.data:
            raise HTTPException(status_code=404, detail="Mission non trouvée ou inactive")
        
        # Vérifier que l'utilisateur n'a pas déjà cette mission
        existing = supabase.table('user_missions')\
            .select('id')\
            .eq('user_id', user_id)\
            .eq('mission_id', mission_id)\
            .execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Mission déjà commencée")
        
        # Créer user_mission
        new_user_mission = {
            'user_id': user_id,
            'mission_id': mission_id,
            'status': 'in_progress',
            'progress': 0,
            'points_earned': 0,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('user_missions').insert(new_user_mission).execute()
        
        return {
            "success": True,
            "message": "Mission commencée",
            "user_mission": result.data[0] if result.data else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# POST /api/gamification/missions/{user_mission_id}/complete
# Compléter une mission
# ============================================
@router.post("/missions/{user_mission_id}/complete")
async def complete_mission(
    user_mission_id: str,
    user_id: str = Query(..., description="ID de l'utilisateur")
):
    """Marque une mission comme complétée et attribue les récompenses"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer user_mission
        user_mission = supabase.table('user_missions')\
            .select('*, missions(*)')\
            .eq('id', user_mission_id)\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        if not user_mission.data:
            raise HTTPException(status_code=404, detail="Mission non trouvée")
        
        if user_mission.data['status'] == 'completed':
            raise HTTPException(status_code=400, detail="Mission déjà complétée")
        
        mission = user_mission.data['missions']
        points_reward = mission['points_reward']
        
        # Mettre à jour user_mission
        supabase.table('user_missions')\
            .update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat(),
                'points_earned': points_reward
            })\
            .eq('id', user_mission_id)\
            .execute()
        
        # Mettre à jour user_gamification
        gamification = supabase.table('user_gamification')\
            .select('*')\
            .eq('user_id', user_id)\
            try:
            .single()\
            except Exception:
                pass  # .single() might return no results
            .execute()
        
        if gamification.data:
            current_points = gamification.data['total_points']
            new_points = current_points + points_reward
            new_level = (new_points // 1000) + 1
            
            achievements = gamification.data.get('achievements', [])
            if mission['title'] not in achievements:
                achievements.append(mission['title'])
            
            supabase.table('user_gamification')\
                .update({
                    'total_points': new_points,
                    'level': new_level,
                    'achievements': achievements,
                    'last_updated': datetime.now().isoformat()
                })\
                .eq('user_id', user_id)\
                .execute()
        
        return {
            "success": True,
            "message": f"Mission complétée ! +{points_reward} points",
            "points_earned": points_reward,
            "new_total_points": new_points if gamification.data else points_reward,
            "level_up": new_level > gamification.data['level'] if gamification.data else False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ============================================
# POST /api/gamification/points/add
# Ajouter des points (admin/système)
# ============================================
@router.post("/points/add")
async def add_points(
    user_id: str = Query(..., description="ID de l'utilisateur"),
    points: int = Query(..., description="Nombre de points à ajouter"),
    reason: str = Query(..., description="Raison de l'ajout")
):
    """Ajoute des points au profil gamification (admin/système)"""
    try:
        supabase = get_supabase_client()
        
        # Récupérer gamification actuelle
        gamification = supabase.table('user_gamification')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        if not gamification.data:
            raise HTTPException(status_code=404, detail="Profil gamification non trouvé")
        
        current_points = gamification.data['total_points']
        new_points = current_points + points
        new_level = (new_points // 1000) + 1
        
        achievements = gamification.data.get('achievements', [])
        if reason not in achievements:
            achievements.append(reason)
        
        supabase.table('user_gamification')\
            .update({
                'total_points': new_points,
                'level': new_level,
                'achievements': achievements,
                'last_updated': datetime.now().isoformat()
            })\
            .eq('user_id', user_id)\
            .execute()
        
        return {
            "success": True,
            "message": f"+{points} points ajoutés",
            "reason": reason,
            "new_total": new_points,
            "level": new_level,
            "level_up": new_level > gamification.data['level']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
