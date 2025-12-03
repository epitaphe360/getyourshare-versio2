from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from auth import get_current_user_from_cookie
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/finance", tags=["Finance"])

@router.get("/earnings")
async def get_earnings(current_user: Dict = Depends(get_current_user_from_cookie)):
    """
    Récupère les gains de l'utilisateur (Influenceur ou Commercial)
    """
    try:
        user_id = current_user["id"]
        role = current_user.get("role")

        if role == "influencer":
            # 1. Total des commissions gagnées
            commissions_result = supabase.table("commissions").select("amount").eq("influencer_id", user_id).execute()
            commissions = commissions_result.data if commissions_result.data else []
            total_earned = sum([float(c.get("amount", 0)) for c in commissions])

            # 2. Total des payouts
            payouts_result = supabase.table("payouts").select("amount, status").eq("influencer_id", user_id).execute()
            payouts = payouts_result.data if payouts_result.data else []
            
            total_withdrawn = sum([float(p.get("amount", 0)) for p in payouts if p.get("status") in ["paid", "processing"]])
            pending_payouts = sum([float(p.get("amount", 0)) for p in payouts if p.get("status") == "pending"])

            available_balance = total_earned - total_withdrawn

            return {
                "total_earned": round(total_earned, 2),
                "total_withdrawn": round(total_withdrawn, 2),
                "available_balance": round(available_balance, 2),
                "pending_payouts": round(pending_payouts, 2),
                "currency": "MAD" # Ou EUR selon la config
            }

        elif role == "commercial":
            # Logique pour les commerciaux (similaire ou différente selon le modèle de données)
            # Pour l'instant, on suppose une structure similaire ou on retourne des données mockées si la table n'existe pas
            try:
                # Si une table commissions_commercial existe
                commissions_result = supabase.table("commercial_commissions").select("amount").eq("commercial_id", user_id).execute()
                commissions = commissions_result.data if commissions_result.data else []
                total_earned = sum([float(c.get("amount", 0)) for c in commissions])
                
                # Payouts
                payouts_result = supabase.table("commercial_payouts").select("amount, status").eq("commercial_id", user_id).execute()
                payouts = payouts_result.data if payouts_result.data else []
                total_withdrawn = sum([float(p.get("amount", 0)) for p in payouts if p.get("status") in ["paid", "processing"]])
                pending_payouts = sum([float(p.get("amount", 0)) for p in payouts if p.get("status") == "pending"])
                
                available_balance = total_earned - total_withdrawn
                
                return {
                    "total_earned": round(total_earned, 2),
                    "total_withdrawn": round(total_withdrawn, 2),
                    "available_balance": round(available_balance, 2),
                    "pending_payouts": round(pending_payouts, 2),
                    "currency": "MAD"
                }
            except Exception:
                # Fallback si les tables n'existent pas encore
                return {
                    "total_earned": 0.0,
                    "total_withdrawn": 0.0,
                    "available_balance": 0.0,
                    "pending_payouts": 0.0,
                    "currency": "MAD"
                }

        else:
            # Pour les autres rôles (Merchant, Admin), peut-être retourner 0 ou une erreur
            return {
                "total_earned": 0.0,
                "total_withdrawn": 0.0,
                "available_balance": 0.0,
                "pending_payouts": 0.0,
                "currency": "MAD"
            }

    except Exception as e:
        logger.error(f"Error fetching earnings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
