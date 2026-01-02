"""
Endpoints pour la gestion des activités récentes de la plateforme
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from auth import get_current_user_from_cookie
from supabase_config import get_supabase_client

router = APIRouter(prefix="/api/activity", tags=["Activity"])

# ============================================
# GET /api/activity/recent
# Activités récentes de la plateforme
# ============================================
@router.get("/recent")
async def get_recent_activity(
    limit: int = Query(10, description="Nombre d'activités à récupérer", ge=1, le=100),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère les activités récentes de la plateforme
    Inclut : inscriptions, créations de produits, services, campagnes, etc.
    """
    try:
        supabase = get_supabase_client()
        activities = []

        # 1. Nouvelles inscriptions (derniers utilisateurs)
        users_result = supabase.table('users')\
            .select('id, email, role, full_name, created_at')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        for user in (users_result.data or []):
            role_labels = {
                'merchant': 'Annonceur',
                'influencer': 'Influenceur',
                'commercial': 'Commercial',
                'admin': 'Administrateur'
            }
            role_label = role_labels.get(user.get('role', ''), user.get('role', 'Utilisateur'))

            activities.append({
                'id': f"user_{user.get('id')}",
                'type': 'user_registration',
                'icon': 'UserPlus',
                'description': f"Nouvel {role_label}: {user.get('full_name') or user.get('email')}",
                'message': f"Inscription d'un nouveau {role_label.lower()}",
                'created_at': user.get('created_at'),
                'time': user.get('created_at'),
                'user_email': user.get('email'),
                'meta': {
                    'role': user.get('role'),
                    'user_id': user.get('id')
                }
            })

        # 2. Nouveaux produits
        products_result = supabase.table('products')\
            .select('id, name, merchant_id, created_at')\
            .order('created_at', desc=True)\
            .limit(int(limit / 2))\
            .execute()

        for product in (products_result.data or []):
            activities.append({
                'id': f"product_{product.get('id')}",
                'type': 'product_created',
                'icon': 'Package',
                'description': f"Nouveau produit: {product.get('name')}",
                'message': f"Un produit a été créé",
                'created_at': product.get('created_at'),
                'time': product.get('created_at'),
                'meta': {
                    'product_id': product.get('id'),
                    'merchant_id': product.get('merchant_id')
                }
            })

        # 3. Nouveaux services
        services_result = supabase.table('services')\
            .select('id, name, created_at')\
            .order('created_at', desc=True)\
            .limit(int(limit / 2))\
            .execute()

        for service in (services_result.data or []):
            activities.append({
                'id': f"service_{service.get('id')}",
                'type': 'service_created',
                'icon': 'Sparkles',
                'description': f"Nouveau service: {service.get('name')}",
                'message': f"Un service a été créé",
                'created_at': service.get('created_at'),
                'time': service.get('created_at'),
                'meta': {
                    'service_id': service.get('id')
                }
            })

        # 4. Nouvelles transactions récentes (optionnel - table peut ne pas exister)
        try:
            transactions_result = supabase.table('transactions')\
                .select('id, user_id, amount, type, status, created_at')\
                .order('created_at', desc=True)\
                .limit(int(limit / 2))\
                .execute()

            for transaction in (transactions_result.data or []):
                type_labels = {
                    'commission': 'Commission gagnée',
                    'payout': 'Paiement effectué',
                    'refund': 'Remboursement',
                    'subscription': 'Abonnement'
                }
                type_label = type_labels.get(transaction.get('type', ''), 'Transaction')

                activities.append({
                    'id': f"transaction_{transaction.get('id')}",
                    'type': 'transaction',
                    'icon': 'DollarSign',
                    'description': f"{type_label}: {transaction.get('amount')}€",
                    'message': f"Transaction de {transaction.get('amount')}€",
                    'created_at': transaction.get('created_at'),
                    'time': transaction.get('created_at'),
                    'meta': {
                        'transaction_id': transaction.get('id'),
                        'amount': transaction.get('amount'),
                        'type': transaction.get('type'),
                        'status': transaction.get('status')
                    }
                })
        except Exception as tx_error:
            # Table transactions n'existe pas encore - on ignore
            print(f"⚠️  Table transactions non disponible: {tx_error}")
            pass

        # 5. Demandes d'inscription en attente (optionnel - table peut ne pas exister)
        try:
            registrations_result = supabase.table('advertiser_registrations')\
                .select('id, company_name, status, created_at')\
                .eq('status', 'pending')\
                .order('created_at', desc=True)\
                .limit(int(limit / 3))\
                .execute()

            for reg in (registrations_result.data or []):
                activities.append({
                    'id': f"registration_{reg.get('id')}",
                    'type': 'registration_pending',
                    'icon': 'UserCheck',
                    'description': f"Demande d'inscription: {reg.get('company_name')}",
                    'message': f"Nouvelle demande d'inscription en attente",
                    'created_at': reg.get('created_at'),
                    'time': reg.get('created_at'),
                    'meta': {
                        'registration_id': reg.get('id'),
                        'company_name': reg.get('company_name')
                    }
                })
        except Exception as reg_error:
            # Table advertiser_registrations n'existe pas encore - on ignore
            print(f"⚠️  Table advertiser_registrations non disponible: {reg_error}")
            pass

        # Trier toutes les activités par date (plus récent en premier)
        activities.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Limiter au nombre demandé
        activities = activities[:limit]

        return {
            "success": True,
            "data": activities,
            "count": len(activities),
            "limit": limit
        }

    except Exception as e:
        print(f"Erreur get_recent_activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des activités: {str(e)}")


# ============================================
# GET /api/activity/stats
# Statistiques d'activité
# ============================================
@router.get("/stats")
async def get_activity_stats(
    days: int = Query(7, description="Nombre de jours", ge=1, le=90),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Statistiques d'activité sur une période"""
    try:
        supabase = get_supabase_client()
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Compter les activités par type
        users_count = supabase.table('users')\
            .select('id', count='exact')\
            .gte('created_at', start_date)\
            .execute()

        products_count = supabase.table('products')\
            .select('id', count='exact')\
            .gte('created_at', start_date)\
            .execute()

        services_count = supabase.table('services')\
            .select('id', count='exact')\
            .gte('created_at', start_date)\
            .execute()

        try:
            transactions_count = supabase.table('transactions')\
                .select('id', count='exact')\
                .gte('created_at', start_date)\
                .execute()
            tx_count = transactions_count.count or 0
        except Exception:
            tx_count = 0

        return {
            "success": True,
            "period_days": days,
            "stats": {
                "new_users": users_count.count or 0,
                "new_products": products_count.count or 0,
                "new_services": services_count.count or 0,
                "transactions": tx_count,
                "total_activities": (
                    (users_count.count or 0) +
                    (products_count.count or 0) +
                    (services_count.count or 0) +
                    tx_count
                )
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
