"""
Fonctions corrigées pour db_helpers.py
Remplace les calculs hardcodés par des requêtes DB réelles

Ces fonctions doivent être intégrées dans db_helpers.py pour corriger les TODOs
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_service_total_leads(supabase, service_id: str) -> int:
    """
    Calcule le nombre RÉEL de leads pour un service depuis la DB

    Args:
        supabase: Client Supabase
        service_id: ID du service

    Returns:
        Nombre total de leads
    """
    try:
        result = supabase.table("leads")\
            .select("id", count="exact")\
            .eq("service_id", service_id)\
            .execute()

        return result.count or 0
    except Exception as e:
        logger.error(f"Erreur calcul total_leads pour service {service_id}: {e}")
        return 0

def calculate_monthly_growth(supabase, metric: str, entity_id: str) -> float:
    """
    Calcule la croissance mensuelle RÉELLE pour une métrique

    Args:
        supabase: Client Supabase
        metric: Type de métrique ('revenue', 'sales', 'leads', etc.)
        entity_id: ID de l'entité (user_id, merchant_id, etc.)

    Returns:
        Pourcentage de croissance (ex: 15.5 pour +15.5%)
    """
    try:
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Mois dernier
        if current_month_start.month == 1:
            last_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            last_month_start = current_month_start.replace(month=current_month_start.month - 1)

        # Sélectionner la table selon la métrique
        table_map = {
            "revenue": "sales",
            "sales": "sales",
            "leads": "leads",
            "conversions": "conversions"
        }

        table = table_map.get(metric, "sales")

        # Mois en cours
        current_result = supabase.table(table)\
            .select("total", count="exact")\
            .eq("merchant_id" if metric in ["revenue", "sales"] else "created_by", entity_id)\
            .gte("created_at", current_month_start.isoformat())\
            .execute()

        current_value = current_result.count or 0

        # Mois dernier
        last_result = supabase.table(table)\
            .select("total", count="exact")\
            .eq("merchant_id" if metric in ["revenue", "sales"] else "created_by", entity_id)\
            .gte("created_at", last_month_start.isoformat())\
            .lt("created_at", current_month_start.isoformat())\
            .execute()

        last_value = last_result.count or 0

        # Calcul croissance
        if last_value == 0:
            return 100.0 if current_value > 0 else 0.0

        growth = ((current_value - last_value) / last_value) * 100
        return round(growth, 2)

    except Exception as e:
        logger.error(f"Erreur calcul monthly_growth pour {metric}: {e}")
        return 0.0

def get_service_with_real_data(supabase, service_id: str) -> Optional[Dict]:
    """
    Récupère un service avec TOUTES les données calculées depuis la DB

    Args:
        supabase: Client Supabase
        service_id: ID du service

    Returns:
        Service enrichi avec données réelles ou None
    """
    try:
        # Service de base
        service_result = supabase.table("services")\
            .select("*, merchants(company_name, email)")\
            .eq("id", service_id)\
            .single()\
            .execute()

        if not service_result.data:
            return None

        service = service_result.data

        # Calculs réels
        # 1. Total leads
        leads_result = supabase.table("leads")\
            .select("id", count="exact")\
            .eq("service_id", service_id)\
            .execute()
        service["total_leads"] = leads_result.count or 0

        # 2. Leads actifs (pending/in_progress)
        active_leads_result = supabase.table("leads")\
            .select("id", count="exact")\
            .eq("service_id", service_id)\
            .in_("status", ["pending", "in_progress"])\
            .execute()
        service["active_leads"] = active_leads_result.count or 0

        # 3. Taux de conversion
        converted_leads_result = supabase.table("leads")\
            .select("id", count="exact")\
            .eq("service_id", service_id)\
            .eq("status", "converted")\
            .execute()
        converted_count = converted_leads_result.count or 0
        total_leads = service["total_leads"]
        service["conversion_rate"] = round((converted_count / total_leads * 100), 2) if total_leads > 0 else 0.0

        # 4. Solde restant (si système de dépôt)
        deposit_result = supabase.table("merchant_deposits")\
            .select("remaining_balance")\
            .eq("service_id", service_id)\
            .eq("status", "active")\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        service["remaining_balance"] = deposit_result.data[0]["remaining_balance"] if deposit_result.data else 0

        # 5. Capacité réelle calculée depuis config ou stats
        # Vérifier s'il y a une colonne capacity_per_month en DB
        service["capacity_per_month"] = service.get("capacity_per_month") or service.get("capacity", 100)

        # 6. Prix par lead
        service["price_per_lead"] = service.get("price_per_lead") or service.get("price", 0)

        # 7. Disponibilité
        service["is_available"] = service.get("is_active", True) and service["remaining_balance"] > 0

        return service

    except Exception as e:
        logger.error(f"Erreur get_service_with_real_data pour {service_id}: {e}")
        return None

def get_all_services_with_real_stats(
    supabase,
    category: Optional[str] = None,
    merchant_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """
    Récupère tous les services avec statistiques RÉELLES calculées

    Args:
        supabase: Client Supabase
        category: Filtrer par catégorie (optionnel)
        merchant_id: Filtrer par merchant (optionnel)
        limit: Nombre max de résultats

    Returns:
        Liste de services enrichis avec stats réelles
    """
    try:
        # Query de base
        query = supabase.table("services").select("*, merchants(company_name, email)")

        # Filtres
        if category:
            query = query.eq("category", category)
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        # Seulement services actifs par défaut
        query = query.eq("is_active", True)

        # Ordre et limite
        result = query.order("created_at", desc=True).limit(limit).execute()

        services = result.data or []

        # Enrichir chaque service avec stats réelles
        enriched_services = []
        for service in services:
            # Total leads
            leads_count = supabase.table("leads")\
                .select("id", count="exact")\
                .eq("service_id", service["id"])\
                .execute()
            service["total_leads"] = leads_count.count or 0

            # Leads convertis
            converted_count = supabase.table("leads")\
                .select("id", count="exact")\
                .eq("service_id", service["id"])\
                .eq("status", "converted")\
                .execute()
            converted = converted_count.count or 0

            # Taux conversion
            service["conversion_rate"] = round((converted / service["total_leads"] * 100), 2) if service["total_leads"] > 0 else 0.0

            # Solde restant
            deposit = supabase.table("merchant_deposits")\
                .select("remaining_balance")\
                .eq("service_id", service["id"])\
                .eq("status", "active")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()

            service["remaining_balance"] = deposit.data[0]["remaining_balance"] if deposit.data else 0

            # Mapping champs pour compatibilité frontend
            service["price_per_lead"] = service.get("price_per_lead") or service.get("price", 0)
            service["capacity_per_month"] = service.get("capacity_per_month") or service.get("capacity", 100)
            service["is_available"] = service.get("is_active", True) and service["remaining_balance"] > 0
            service["images"] = [service["image_url"]] if service.get("image_url") else []

            enriched_services.append(service)

        return enriched_services

    except Exception as e:
        logger.error(f"Erreur get_all_services_with_real_stats: {e}")
        return []

def get_merchant_stats_real(supabase, merchant_id: str) -> Dict:
    """
    Calcule les statistiques RÉELLES d'un merchant

    Args:
        supabase: Client Supabase
        merchant_id: ID du merchant

    Returns:
        Dict avec toutes les stats calculées depuis la DB
    """
    try:
        stats = {}

        # 1. Revenus total
        revenue_result = supabase.rpc("get_merchant_total_revenue", {"p_merchant_id": merchant_id}).execute()
        stats["total_revenue"] = revenue_result.data if revenue_result.data else 0

        # 2. Revenus mois en cours
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = supabase.table("sales")\
            .select("total")\
            .eq("merchant_id", merchant_id)\
            .gte("created_at", month_start.isoformat())\
            .execute()

        stats["monthly_revenue"] = sum([s.get("total", 0) for s in (monthly_revenue.data or [])])

        # 3. Croissance mensuelle
        stats["monthly_growth"] = calculate_monthly_growth(supabase, "revenue", merchant_id)

        # 4. Nombre produits
        products_count = supabase.table("products")\
            .select("id", count="exact")\
            .eq("merchant_id", merchant_id)\
            .execute()
        stats["products_count"] = products_count.count or 0

        # 5. Nombre services
        services_count = supabase.table("services")\
            .select("id", count="exact")\
            .eq("merchant_id", merchant_id)\
            .execute()
        stats["services_count"] = services_count.count or 0

        # 6. Nombre campagnes
        campaigns_count = supabase.table("campaigns")\
            .select("id", count="exact")\
            .eq("merchant_id", merchant_id)\
            .execute()
        stats["campaigns_count"] = campaigns_count.count or 0

        # 7. Nombre affiliés actifs
        affiliates_count = supabase.table("affiliate_links")\
            .select("user_id")\
            .eq("merchant_id", merchant_id)\
            .execute()

        # Compter les affiliés uniques
        unique_affiliates = set([a["user_id"] for a in (affiliates_count.data or [])])
        stats["affiliates_count"] = len(unique_affiliates)

        # 8. Nombre de ventes
        sales_count = supabase.table("sales")\
            .select("id", count="exact")\
            .eq("merchant_id", merchant_id)\
            .execute()
        stats["sales_count"] = sales_count.count or 0

        # 9. Panier moyen
        if stats["sales_count"] > 0:
            stats["average_order_value"] = round(stats["total_revenue"] / stats["sales_count"], 2)
        else:
            stats["average_order_value"] = 0

        # 10. Taux de conversion global
        clicks_count = supabase.table("click_tracking")\
            .select("id", count="exact")\
            .eq("merchant_id", merchant_id)\
            .execute()
        total_clicks = clicks_count.count or 0

        if total_clicks > 0:
            stats["conversion_rate"] = round((stats["sales_count"] / total_clicks * 100), 2)
        else:
            stats["conversion_rate"] = 0.0

        return stats

    except Exception as e:
        logger.error(f"Erreur get_merchant_stats_real pour {merchant_id}: {e}")
        return {}

# Fonction SQL à créer dans Supabase pour calcul revenue optimisé
GET_MERCHANT_TOTAL_REVENUE_SQL = """
CREATE OR REPLACE FUNCTION get_merchant_total_revenue(p_merchant_id UUID)
RETURNS NUMERIC AS $$
BEGIN
    RETURN COALESCE(
        (SELECT SUM(total) FROM sales WHERE merchant_id = p_merchant_id),
        0
    );
END;
$$ LANGUAGE plpgsql;
"""
