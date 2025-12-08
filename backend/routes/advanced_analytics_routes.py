"""
Routes Advanced Analytics
Cohort Analysis, RFM Segmentation, Customer Segments, A/B Testing
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advanced-analytics", tags=["Advanced Analytics"])


# ============================================
# MODELS
# ============================================

class ABTestCreate(BaseModel):
    name: str
    description: Optional[str] = None
    variants: List[Dict[str, Any]]  # [{"id": "A", "name": "Control", "config": {...}}, ...]
    traffic_split: List[float]  # [0.5, 0.5] for 50/50 split
    metric: str  # conversion_rate, revenue, engagement
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ABTestAssignment(BaseModel):
    test_id: str
    user_id: str
    variant_id: str


# ============================================
# COHORT ANALYSIS
# ============================================

@router.get("/cohorts")
async def get_cohort_analysis(
    period: str = "month",  # week, month
    metric: str = "retention",  # retention, revenue, engagement
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Analyse par cohortes

    Analyse l'évolution des utilisateurs groupés par période d'inscription
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Admin ou merchant uniquement
        if role not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès réservé aux admins/merchants")

        # Dates par défaut: 6 derniers mois
        if not end_date:
            end_date = datetime.now().isoformat()

        if not start_date:
            start_date = (datetime.now() - timedelta(days=180)).isoformat()

        # Récupérer tous les utilisateurs dans la période
        users = supabase.table('users').select('id, created_at').gte('created_at', start_date).lte('created_at', end_date).execute()

        # Grouper par cohorte
        cohorts = {}

        for user in (users.data or []):
            user_created = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))

            # Déterminer la cohorte
            if period == "week":
                # Semaine de l'année (ex: 2025-W01)
                cohort_key = user_created.strftime("%Y-W%U")
            else:  # month
                cohort_key = user_created.strftime("%Y-%m")

            if cohort_key not in cohorts:
                cohorts[cohort_key] = {
                    'cohort': cohort_key,
                    'cohort_date': cohort_key,
                    'users_count': 0,
                    'user_ids': []
                }

            cohorts[cohort_key]['users_count'] += 1
            cohorts[cohort_key]['user_ids'].append(user['id'])

        # Calculer les métriques pour chaque cohorte
        result = []

        for cohort_key, cohort_data in cohorts.items():
            user_ids = cohort_data['user_ids']

            # Métrique selon le type
            if metric == "retention":
                # Calculer la rétention (utilisateurs actifs dans les 30 derniers jours)
                recent_activity = supabase.table('conversions').select('influencer_id', count='exact').in_('influencer_id', user_ids).gte('created_at', (datetime.now() - timedelta(days=30)).isoformat()).execute()

                active_users = set()
                if recent_activity.data:
                    active_users = {c['influencer_id'] for c in recent_activity.data}

                retention_rate = len(active_users) / cohort_data['users_count'] if cohort_data['users_count'] > 0 else 0

                cohort_metric = {
                    'retention_rate': round(retention_rate * 100, 2),
                    'active_users': len(active_users),
                    'total_users': cohort_data['users_count']
                }

            elif metric == "revenue":
                # Revenu total de la cohorte
                conversions = supabase.table('conversions').select('sale_amount').in_('influencer_id', user_ids).execute()

                total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in (conversions.data or []))
                avg_revenue_per_user = total_revenue / cohort_data['users_count'] if cohort_data['users_count'] > 0 else 0

                cohort_metric = {
                    'total_revenue': float(total_revenue),
                    'avg_revenue_per_user': float(avg_revenue_per_user),
                    'total_users': cohort_data['users_count']
                }

            elif metric == "engagement":
                # Nombre moyen de conversions par utilisateur
                conversions = supabase.table('conversions').select('*', count='exact').in_('influencer_id', user_ids).execute()

                total_conversions = conversions.count if hasattr(conversions, 'count') else len(conversions.data or [])
                avg_conversions = total_conversions / cohort_data['users_count'] if cohort_data['users_count'] > 0 else 0

                cohort_metric = {
                    'total_conversions': total_conversions,
                    'avg_conversions_per_user': round(avg_conversions, 2),
                    'total_users': cohort_data['users_count']
                }

            result.append({
                'cohort': cohort_key,
                'users_count': cohort_data['users_count'],
                'metrics': cohort_metric
            })

        # Trier par date de cohorte
        result = sorted(result, key=lambda x: x['cohort'])

        return {
            "success": True,
            "period": period,
            "metric": metric,
            "start_date": start_date,
            "end_date": end_date,
            "cohorts": result,
            "total_cohorts": len(result)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cohort analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RFM ANALYSIS (Recency, Frequency, Monetary)
# ============================================

@router.get("/rfm-analysis")
async def get_rfm_analysis(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Analyse RFM (Recency, Frequency, Monetary)

    Segmente les clients selon:
    - Recency: Quand ont-ils acheté pour la dernière fois ?
    - Frequency: À quelle fréquence achètent-ils ?
    - Monetary: Combien dépensent-ils ?
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        if role not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès réservé aux admins/merchants")

        # Récupérer toutes les conversions
        conversions = supabase.table('conversions').select('influencer_id, sale_amount, created_at').execute()

        if not conversions.data:
            return {
                "success": True,
                "message": "Aucune donnée de conversion disponible",
                "segments": []
            }

        # Calculer RFM pour chaque utilisateur
        user_rfm = {}
        now = datetime.now()

        for conv in conversions.data:
            influencer_id = conv.get('influencer_id')
            sale_amount = Decimal(str(conv.get('sale_amount', 0)))
            created_at = datetime.fromisoformat(conv.get('created_at').replace('Z', '+00:00'))

            if influencer_id not in user_rfm:
                user_rfm[influencer_id] = {
                    'last_purchase': created_at,
                    'purchase_count': 0,
                    'total_spent': Decimal('0')
                }

            # Update metrics
            if created_at > user_rfm[influencer_id]['last_purchase']:
                user_rfm[influencer_id]['last_purchase'] = created_at

            user_rfm[influencer_id]['purchase_count'] += 1
            user_rfm[influencer_id]['total_spent'] += sale_amount

        # Calculer les scores RFM (1-5, 5 étant le meilleur)
        rfm_scores = []

        for influencer_id, data in user_rfm.items():
            # Recency: jours depuis dernier achat
            recency_days = (now - data['last_purchase']).days

            # Scoring (inversé car moins de jours = meilleur)
            if recency_days <= 7:
                recency_score = 5
            elif recency_days <= 30:
                recency_score = 4
            elif recency_days <= 90:
                recency_score = 3
            elif recency_days <= 180:
                recency_score = 2
            else:
                recency_score = 1

            # Frequency score
            freq_count = data['purchase_count']
            if freq_count >= 20:
                frequency_score = 5
            elif freq_count >= 10:
                frequency_score = 4
            elif freq_count >= 5:
                frequency_score = 3
            elif freq_count >= 2:
                frequency_score = 2
            else:
                frequency_score = 1

            # Monetary score
            total_spent = float(data['total_spent'])
            if total_spent >= 10000:
                monetary_score = 5
            elif total_spent >= 5000:
                monetary_score = 4
            elif total_spent >= 1000:
                monetary_score = 3
            elif total_spent >= 500:
                monetary_score = 2
            else:
                monetary_score = 1

            # Score total
            rfm_total = recency_score + frequency_score + monetary_score

            # Déterminer le segment
            if recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4:
                segment = "Champions"
            elif recency_score >= 3 and frequency_score >= 3:
                segment = "Loyal Customers"
            elif recency_score >= 4:
                segment = "Recent Customers"
            elif frequency_score >= 4:
                segment = "Frequent Buyers"
            elif monetary_score >= 4:
                segment = "Big Spenders"
            elif recency_score <= 2 and frequency_score >= 3:
                segment = "At Risk"
            elif recency_score <= 2:
                segment = "Lost Customers"
            else:
                segment = "Potential Loyalists"

            rfm_scores.append({
                'user_id': influencer_id,
                'recency_score': recency_score,
                'frequency_score': frequency_score,
                'monetary_score': monetary_score,
                'rfm_score': rfm_total,
                'segment': segment,
                'recency_days': recency_days,
                'purchase_count': freq_count,
                'total_spent': total_spent
            })

        # Grouper par segment
        segments = {}
        for user_rfm_data in rfm_scores:
            segment = user_rfm_data['segment']
            if segment not in segments:
                segments[segment] = {
                    'segment_name': segment,
                    'users_count': 0,
                    'avg_recency_score': 0,
                    'avg_frequency_score': 0,
                    'avg_monetary_score': 0,
                    'total_revenue': 0,
                    'users': []
                }

            segments[segment]['users_count'] += 1
            segments[segment]['avg_recency_score'] += user_rfm_data['recency_score']
            segments[segment]['avg_frequency_score'] += user_rfm_data['frequency_score']
            segments[segment]['avg_monetary_score'] += user_rfm_data['monetary_score']
            segments[segment]['total_revenue'] += user_rfm_data['total_spent']
            segments[segment]['users'].append(user_rfm_data)

        # Calculer les moyennes
        for segment in segments.values():
            count = segment['users_count']
            segment['avg_recency_score'] = round(segment['avg_recency_score'] / count, 2)
            segment['avg_frequency_score'] = round(segment['avg_frequency_score'] / count, 2)
            segment['avg_monetary_score'] = round(segment['avg_monetary_score'] / count, 2)

        return {
            "success": True,
            "segments": list(segments.values()),
            "total_users_analyzed": len(rfm_scores),
            "total_segments": len(segments)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in RFM analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CUSTOMER SEGMENTS
# ============================================

@router.get("/segments")
async def get_customer_segments(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Segments de clients personnalisés
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        if role not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès réservé aux admins/merchants")

        # Définir les segments
        segments = []

        # 1. VIP Customers (plus de 5000 MAD de revenue)
        vip_conversions = supabase.table('conversions').select('influencer_id, sale_amount').execute()

        vip_users = {}
        for conv in (vip_conversions.data or []):
            inf_id = conv.get('influencer_id')
            amount = Decimal(str(conv.get('sale_amount', 0)))

            if inf_id not in vip_users:
                vip_users[inf_id] = Decimal('0')
            vip_users[inf_id] += amount

        vip_count = sum(1 for total in vip_users.values() if total >= 5000)

        segments.append({
            'segment_id': 'vip',
            'name': 'VIP Customers',
            'description': 'Customers with >5000 MAD total revenue',
            'users_count': vip_count,
            'criteria': {'min_revenue': 5000}
        })

        # 2. Active Last 30 Days
        recent = (datetime.now() - timedelta(days=30)).isoformat()
        active_recent = supabase.table('conversions').select('influencer_id', count='exact').gte('created_at', recent).execute()

        active_users = set()
        if active_recent.data:
            active_users = {c['influencer_id'] for c in active_recent.data}

        segments.append({
            'segment_id': 'active_30d',
            'name': 'Active (Last 30 Days)',
            'description': 'Users with at least one conversion in the last 30 days',
            'users_count': len(active_users),
            'criteria': {'activity_period': '30_days'}
        })

        # 3. Dormant (No activity in 90 days)
        old_date = (datetime.now() - timedelta(days=90)).isoformat()

        # Tous les utilisateurs avec activité
        all_active = supabase.table('conversions').select('influencer_id').execute()
        all_user_ids = {c['influencer_id'] for c in (all_active.data or [])}

        # Activité récente (90j)
        recent_active = supabase.table('conversions').select('influencer_id').gte('created_at', old_date).execute()
        recent_user_ids = {c['influencer_id'] for c in (recent_active.data or [])}

        dormant_users = all_user_ids - recent_user_ids

        segments.append({
            'segment_id': 'dormant_90d',
            'name': 'Dormant (90+ days)',
            'description': 'Users with no activity in the last 90 days',
            'users_count': len(dormant_users),
            'criteria': {'inactivity_period': '90_days'}
        })

        # 4. New Users (registered in last 7 days)
        new_date = (datetime.now() - timedelta(days=7)).isoformat()
        new_users = supabase.table('users').select('*', count='exact').gte('created_at', new_date).execute()
        new_count = new_users.count if hasattr(new_users, 'count') else len(new_users.data or [])

        segments.append({
            'segment_id': 'new_7d',
            'name': 'New Users (Last 7 Days)',
            'description': 'Users registered in the last 7 days',
            'users_count': new_count,
            'criteria': {'registration_period': '7_days'}
        })

        return {
            "success": True,
            "segments": segments,
            "total_segments": len(segments)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# A/B TESTING
# ============================================

@router.post("/ab-tests")
async def create_ab_test(
    test: ABTestCreate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer un test A/B
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        if role not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès réservé aux admins/merchants")

        # Valider traffic split
        if abs(sum(test.traffic_split) - 1.0) > 0.01:
            raise HTTPException(status_code=400, detail="Traffic split must sum to 1.0")

        if len(test.traffic_split) != len(test.variants):
            raise HTTPException(status_code=400, detail="Traffic split length must match variants length")

        # Créer le test
        test_data = {
            'name': test.name,
            'description': test.description,
            'created_by': user_id,
            'variants': test.variants,
            'traffic_split': test.traffic_split,
            'metric': test.metric,
            'status': 'active',
            'start_date': test.start_date or datetime.now().isoformat(),
            'end_date': test.end_date,
            'created_at': datetime.now().isoformat()
        }

        result = supabase.table('ab_tests').insert(test_data).execute()

        return {
            "success": True,
            "test": result.data[0] if result.data else test_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating A/B test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-tests")
async def get_ab_tests(
    status: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des tests A/B
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        query = supabase.table('ab_tests').select('*')

        if status:
            query = query.eq('status', status)

        query = query.order('created_at', desc=True)

        response = query.execute()

        return {
            "success": True,
            "tests": response.data or [],
            "total": len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting A/B tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-tests/{test_id}/results")
async def get_ab_test_results(
    test_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Résultats d'un test A/B
    """
    try:
        # Récupérer le test
        test = supabase.table('ab_tests').select('*').eq('id', test_id).single().execute()

        if not test.data:
            raise HTTPException(status_code=404, detail="Test non trouvé")

        # Récupérer les assignments
        assignments = supabase.table('ab_test_assignments').select('*').eq('test_id', test_id).execute()

        # Calculer les résultats par variante
        variants_results = {}

        for variant in test.data.get('variants', []):
            variant_id = variant['id']

            # Utilisateurs assignés à cette variante
            variant_users = [a['user_id'] for a in (assignments.data or []) if a.get('variant_id') == variant_id]

            if not variant_users:
                variants_results[variant_id] = {
                    'variant_id': variant_id,
                    'variant_name': variant.get('name'),
                    'users_count': 0,
                    'conversions': 0,
                    'conversion_rate': 0,
                    'revenue': 0
                }
                continue

            # Métriques selon le type
            metric = test.data.get('metric')

            if metric == 'conversion_rate':
                conversions = supabase.table('conversions').select('*', count='exact').in_('influencer_id', variant_users).execute()

                conv_count = conversions.count if hasattr(conversions, 'count') else len(conversions.data or [])
                conv_rate = (conv_count / len(variant_users) * 100) if len(variant_users) > 0 else 0

                variants_results[variant_id] = {
                    'variant_id': variant_id,
                    'variant_name': variant.get('name'),
                    'users_count': len(variant_users),
                    'conversions': conv_count,
                    'conversion_rate': round(conv_rate, 2)
                }

            elif metric == 'revenue':
                conversions = supabase.table('conversions').select('sale_amount').in_('influencer_id', variant_users).execute()

                total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in (conversions.data or []))
                avg_revenue = total_revenue / len(variant_users) if len(variant_users) > 0 else 0

                variants_results[variant_id] = {
                    'variant_id': variant_id,
                    'variant_name': variant.get('name'),
                    'users_count': len(variant_users),
                    'total_revenue': float(total_revenue),
                    'avg_revenue_per_user': float(avg_revenue)
                }

        return {
            "success": True,
            "test_id": test_id,
            "test_name": test.data.get('name'),
            "status": test.data.get('status'),
            "metric": test.data.get('metric'),
            "results": list(variants_results.values()),
            "total_users": len(assignments.data) if assignments.data else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting A/B test results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-tests/{test_id}/assign")
async def assign_user_to_variant(
    test_id: str,
    assignment: ABTestAssignment,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Assigner un utilisateur à une variante
    """
    try:
        # Vérifier si déjà assigné
        existing = supabase.table('ab_test_assignments').select('*').eq('test_id', test_id).eq('user_id', assignment.user_id).execute()

        if existing.data:
            return {
                "success": True,
                "message": "User already assigned",
                "assignment": existing.data[0]
            }

        # Créer l'assignment
        assignment_data = {
            'test_id': test_id,
            'user_id': assignment.user_id,
            'variant_id': assignment.variant_id,
            'assigned_at': datetime.now().isoformat()
        }

        result = supabase.table('ab_test_assignments').insert(assignment_data).execute()

        return {
            "success": True,
            "assignment": result.data[0] if result.data else assignment_data
        }

    except Exception as e:
        logger.error(f"Error assigning user to variant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-tests/{test_id}/stop")
async def stop_ab_test(
    test_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Arrêter un test A/B
    """
    try:
        role = payload.get("role")

        if role not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès réservé aux admins/merchants")

        supabase.table('ab_tests').update({
            'status': 'stopped',
            'end_date': datetime.now().isoformat()
        }).eq('id', test_id).execute()

        return {
            "success": True,
            "message": "Test A/B arrêté"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping A/B test: {e}")
        raise HTTPException(status_code=500, detail=str(e))
