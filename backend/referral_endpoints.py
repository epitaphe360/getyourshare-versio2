"""
Endpoints du Système de Parrainage Viral
Programme multi-niveaux avec tracking des gains
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from utils.logger import logger
from supabase_client import supabase, get_supabase_client
from auth import get_current_user_from_cookie

router = APIRouter(prefix="/api/referrals", tags=["Referrals"])

# ============================================
# MODELS
# ============================================

class ReferralCode(BaseModel):
    code: str
    user_id: str
    is_active: bool = True

class ReferralNetwork(BaseModel):
    id: str
    referrer_id: str
    referred_id: str
    referred_username: str
    referred_email: str
    referred_role: Optional[str] = None
    level: int
    status: str
    total_sales: float
    referrer_earnings: float
    referred_at: datetime

class ReferralEarnings(BaseModel):
    total_earnings: float
    pending_earnings: float
    paid_earnings: float
    this_month_earnings: float
    total_referrals: int
    active_referrals: int

class ReferralStats(BaseModel):
    code: Optional[str]
    total_referrals: int
    active_referrals: int
    total_earnings: float
    badge_level: str
    tier: int
    network: List[ReferralNetwork]


# ============================================
# ENDPOINTS
# ============================================

@router.post("/generate-code")
async def generate_referral_code(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Générer un code de parrainage unique pour l'utilisateur connecté
    """
    try:
        user_id = current_user["id"]
        supabase = get_supabase_client()

        # Vérifier si l'utilisateur a déjà un code
        existing = supabase.table('referral_codes').select('*').eq('user_id', user_id).execute()

        if existing.data and len(existing.data) > 0:
            logger.info(f"Code existant trouvé pour user {user_id}")
            return {
                "code": existing.data[0]['code'],
                "message": "Code de parrainage existant",
                "already_exists": True
            }

        # Générer nouveau code via fonction SQL
        # Fallback si la fonction RPC n'existe pas ou échoue
        try:
            result = supabase.rpc('generate_referral_code', {'p_user_id': user_id}).execute()
            new_code = result.data
        except Exception as rpc_error:
            logger.warning(f"RPC generate_referral_code failed: {rpc_error}. Using fallback generation.")
            import random
            import string
            chars = string.ascii_uppercase + string.digits
            new_code = ''.join(random.choice(chars) for _ in range(8))

        if not new_code:
             import random
             import string
             chars = string.ascii_uppercase + string.digits
             new_code = ''.join(random.choice(chars) for _ in range(8))

        # Insérer dans la table
        insert_result = supabase.table('referral_codes').insert({
            'user_id': user_id,
            'code': new_code,
            'is_active': True
        }).execute()

        logger.info(f"✅ Code parrainage créé: {new_code} pour user {user_id}")

        return {
            "code": new_code,
            "message": "Code de parrainage créé avec succès",
            "share_link": f"https://getyourshare.com/register?ref={new_code}"
        }

    except Exception as e:
        logger.error(f"Erreur génération code parrainage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=ReferralStats)
async def get_referral_stats(current_user: dict = Depends(get_current_user_from_cookie)):
    """
    Récupérer les statistiques complètes de parrainage pour l'utilisateur connecté
    """
    try:
        user_id = current_user["id"]
        
        # 1. Récupérer le code
        code_info = await get_my_referral_code(user_id)
        code = code_info.get("code") if code_info.get("has_code") else None
        
        # 2. Récupérer le réseau
        network_data = await get_referral_network(user_id)
        network_list = network_data.get("network", [])
        
        # 3. Récupérer les gains
        earnings_data = await get_referral_earnings(user_id)
        
        # Convertir en modèle ReferralStats
        stats = ReferralStats(
            code=code,
            total_referrals=earnings_data.get("total_referrals", 0),
            active_referrals=earnings_data.get("active_referrals", 0),
            total_earnings=earnings_data.get("total_earnings", 0.0),
            badge_level=earnings_data.get("badge_level", "bronze"),
            tier=earnings_data.get("tier", 1),
            network=[ReferralNetwork(**n) for n in network_list]
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération stats parrainage: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/my-code/{user_id}")
async def get_my_referral_code(user_id: str):
    """
    Récupérer le code de parrainage d'un utilisateur
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table('referral_codes').select('*').eq('user_id', user_id).execute()

        if not result.data or len(result.data) == 0:
            return {
                "has_code": False,
                "message": "Aucun code de parrainage trouvé"
            }

        code_data = result.data[0]

        return {
            "has_code": True,
            "code": code_data['code'],
            "is_active": code_data['is_active'],
            "created_at": code_data['created_at'],
            "share_link": f"https://getyourshare.com/register?ref={code_data['code']}",
            "share_message": f"🎁 Rejoins GetYourShare avec mon code: {code_data['code']} et gagne des bonus!"
        }

    except Exception as e:
        logger.error(f"Erreur récupération code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-code")
async def validate_referral_code(code: str, new_user_id: str):
    """
    Valider un code de parrainage lors de l'inscription
    """
    try:
        supabase = get_supabase_client()

        # Vérifier que le code existe
        code_result = supabase.table('referral_codes').select('*').eq('code', code).eq('is_active', True).execute()

        if not code_result.data or len(code_result.data) == 0:
            raise HTTPException(status_code=404, detail="Code de parrainage invalide")

        referrer_id = code_result.data[0]['user_id']

        # Vérifier pas d'auto-parrainage
        if referrer_id == new_user_id:
            raise HTTPException(status_code=400, detail="Auto-parrainage impossible")

        # Créer la relation de parrainage
        referral_data = {
            'referrer_id': referrer_id,
            'referred_id': new_user_id,
            'referral_code': code,
            'level': 1,
            'status': 'pending',  # Devient 'active' après première vente
            'referred_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('referrals').insert(referral_data).execute()

        logger.info(f"✅ Parrainage créé: {referrer_id} → {new_user_id} avec code {code}")

        # Initialiser rewards si besoin
        supabase.table('referral_rewards').upsert({
            'user_id': referrer_id,
            'total_referrals': 1,
            'active_referrals': 0
        }, on_conflict='user_id').execute()

        return {
            "success": True,
            "message": "Code de parrainage validé!",
            "referrer_id": referrer_id,
            "bonus_unlocked": True,
            "bonus_message": "🎉 Vous avez débloqué des bonus de bienvenue!"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validation code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-network/{user_id}")
async def get_referral_network(user_id: str):
    """
    Récupérer le réseau de parrainage (niveau 1 et 2)
    """
    try:
        supabase = get_supabase_client()

        # Niveau 1: Parrainages directs
        level1 = supabase.table('referrals').select('''
            id,
            referred_id,
            referral_code,
            level,
            status,
            total_sales,
            referrer_earnings,
            referred_at,
            users:referred_id(full_name, email, role)
        ''').eq('referrer_id', user_id).execute()

        network = []

        for referral in level1.data:
            user_info = referral.get('users', {})
            # Use full_name or email part as display name
            display_name = user_info.get('full_name')
            if not display_name and user_info.get('email'):
                display_name = user_info.get('email').split('@')[0]
            
            network.append({
                "id": referral['id'],
                "referrer_id": user_id,
                "referred_id": referral['referred_id'],
                "referred_username": display_name or 'N/A',
                "referred_email": user_info.get('email', 'N/A'),
                "referred_role": user_info.get('role', 'N/A'),
                "level": 1,
                "status": referral['status'],
                "total_sales": float(referral['total_sales'] or 0),
                "referrer_earnings": float(referral['referrer_earnings'] or 0),
                "referred_at": referral['referred_at']
            })

        # Niveau 2: Parrainages de mes filleuls
        if level1.data:
            referred_ids = [r['referred_id'] for r in level1.data]

            level2 = supabase.table('referrals').select('''
                id,
                referrer_id,
                referred_id,
                level,
                status,
                total_sales,
                referrer_earnings,
                referred_at,
                users:referred_id(full_name, email, role)
            ''').in_('referrer_id', referred_ids).execute()

            for referral in level2.data:
                user_info = referral.get('users', {})
                # Use full_name or email part as display name
                display_name = user_info.get('full_name')
                if not display_name and user_info.get('email'):
                    display_name = user_info.get('email').split('@')[0]

                network.append({
                    "id": referral['id'],
                    "referrer_id": referral['referrer_id'],
                    "referred_id": referral['referred_id'],
                    "referred_username": display_name or 'N/A',
                    "referred_email": user_info.get('email', 'N/A'),
                    "referred_role": user_info.get('role', 'N/A'),
                    "level": 2,
                    "status": referral['status'],
                    "total_sales": float(referral['total_sales'] or 0),
                    "referrer_earnings": float(referral['referrer_earnings'] or 0),
                    "referred_at": referral['referred_at']
                })

        return {
            "network": network,
            "level1_count": len([n for n in network if n['level'] == 1]),
            "level2_count": len([n for n in network if n['level'] == 2]),
            "total_network": len(network)
        }

    except Exception as e:
        logger.error(f"Erreur récupération réseau: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/earnings/{user_id}")
async def get_referral_earnings(user_id: str):
    """
    Récupérer les gains de parrainage détaillés
    """
    try:
        supabase = get_supabase_client()

        # Stats globales depuis rewards
        rewards = supabase.table('referral_rewards').select('*').eq('user_id', user_id).execute()

        if not rewards.data or len(rewards.data) == 0:
            return {
                "total_earnings": 0,
                "pending_earnings": 0,
                "paid_earnings": 0,
                "this_month_earnings": 0,
                "total_referrals": 0,
                "active_referrals": 0,
                "badge_level": "bronze",
                "tier": 1
            }

        reward_data = rewards.data[0]

        # Gains détaillés
        earnings = supabase.table('referral_earnings').select('*').eq('referrer_id', user_id).execute()

        pending = sum(float(e['earning_amount']) for e in earnings.data if e['status'] == 'pending')
        paid = sum(float(e['earning_amount']) for e in earnings.data if e['status'] == 'paid')

        # Gains du mois en cours
        from datetime import datetime
        current_month = datetime.now().month
        this_month = sum(
            float(e['earning_amount']) for e in earnings.data
            if datetime.fromisoformat(e['created_at'].replace('Z', '+00:00')).month == current_month
        )

        return {
            "total_earnings": float(reward_data.get('total_earnings', 0)),
            "pending_earnings": pending,
            "paid_earnings": paid,
            "this_month_earnings": this_month,
            "total_referrals": reward_data.get('total_referrals', 0),
            "active_referrals": reward_data.get('active_referrals', 0),
            "badge_level": reward_data.get('badge_level', 'bronze'),
            "tier": reward_data.get('tier', 1),
            "bonus_commission_rate": float(reward_data.get('bonus_commission_rate', 0)),
            "details": [
                {
                    "amount": float(e['earning_amount']),
                    "status": e['status'],
                    "level": e['level'],
                    "date": e['created_at']
                }
                for e in earnings.data[:10]  # 10 dernières
            ]
        }

    except Exception as e:
        logger.error(f"Erreur récupération gains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_referral_leaderboard(limit: int = 20):
    """
    Classement des meilleurs parrains
    """
    try:
        supabase = get_supabase_client()

        # Top parrains par earnings
        leaderboard = supabase.table('referral_rewards').select('''
            user_id,
            total_earnings,
            total_referrals,
            active_referrals,
            badge_level,
            tier,
            users:user_id(full_name, email, role)
        ''').order('total_earnings', desc=True).limit(limit).execute()

        results = []
        for idx, entry in enumerate(leaderboard.data, 1):
            user_info = entry.get('users', {})
            # Use full_name or email part as display name
            display_name = user_info.get('full_name')
            if not display_name and user_info.get('email'):
                display_name = user_info.get('email').split('@')[0]
                
            results.append({
                "rank": idx,
                "user_id": entry['user_id'],
                "username": display_name or 'Anonymous',
                "role": user_info.get('role', 'N/A'),
                "total_earnings": float(entry['total_earnings'] or 0),
                "total_referrals": entry['total_referrals'],
                "active_referrals": entry['active_referrals'],
                "badge_level": entry['badge_level'],
                "tier": entry['tier'],
                "badge_emoji": {
                    'bronze': '🥉',
                    'silver': '🥈',
                    'gold': '🥇',
                    'platinum': '💎',
                    'diamond': '👑'
                }.get(entry['badge_level'], '🏅')
            })

        return {
            "leaderboard": results,
            "total_ambassadors": len(results),
            "updated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Erreur leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{user_id}")
async def get_referral_dashboard(user_id: str):
    """
    Dashboard complet de parrainage
    """
    try:
        # Combiner toutes les infos
        code_info = await get_my_referral_code(user_id)
        network = await get_referral_network(user_id)
        earnings = await get_referral_earnings(user_id)

        return {
            "referral_code": code_info,
            "network": network,
            "earnings": earnings,
            "quick_stats": {
                "total_network": network['total_network'],
                "pending_earnings": earnings['pending_earnings'],
                "this_month_earnings": earnings['this_month_earnings'],
                "badge": earnings['badge_level']
            }
        }

    except Exception as e:
        logger.error(f"Erreur dashboard parrainage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
