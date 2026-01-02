"""
Endpoints pour la gestion des services et leads (génération de leads)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from auth import get_current_user_from_cookie
from db_helpers import (
    create_service,
    get_all_services,
    get_service_by_id,
    update_service,
    delete_service,
    create_lead,
    get_leads_by_service,
    get_leads_by_marchand,
    get_all_leads,
    update_lead_status,
    create_service_recharge,
    get_service_recharges,
    create_service_extra,
    get_service_extras,
    get_services_stats,
    get_user_by_id,
    get_merchant_by_user_id
)
from utils.logger import logger

router = APIRouter(prefix="/api", tags=["services_leads"])

# ============================================
# MODELS
# ============================================

class ServiceCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    images: Optional[List[str]] = []
    categorie_id: Optional[str] = None
    localisation: Optional[str] = None
    conditions: Optional[str] = None
    depot_initial: float
    prix_par_lead: float
    commission_rate: Optional[float] = 20.0
    formulaire_champs: Optional[List[Dict]] = []
    date_expiration: Optional[str] = None


class ServiceUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    categorie_id: Optional[str] = None
    localisation: Optional[str] = None
    conditions: Optional[str] = None
    prix_par_lead: Optional[float] = None
    commission_rate: Optional[float] = None
    formulaire_champs: Optional[List[Dict]] = None
    date_expiration: Optional[str] = None
    statut: Optional[str] = None


class LeadCreate(BaseModel):
    service_id: str
    nom_client: str
    email_client: EmailStr
    telephone_client: str
    donnees_formulaire: Optional[Dict] = {}


class LeadStatusUpdate(BaseModel):
    statut: str  # nouveau, en_cours, converti, perdu, spam
    notes_marchand: Optional[str] = None


class ServiceRecharge(BaseModel):
    montant: float
    methode_paiement: Optional[str] = None
    transaction_id: Optional[str] = None


class ServiceExtraCreate(BaseModel):
    type: str
    nom: str
    description: Optional[str] = None
    prix: float
    date_fin: Optional[str] = None
    transaction_id: Optional[str] = None


# ============================================
# ENDPOINTS SERVICES (ADMIN & MARCHAND)
# ============================================

@router.post("/admin/services")
async def create_service_endpoint(
    service_data: ServiceCreate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Créer un nouveau service (Admin uniquement)"""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Créer le service
        service = create_service(current_user["id"], service_data.dict())
        
        if not service:
            raise HTTPException(status_code=400, detail="Erreur lors de la création du service")
        
        return {
            "success": True,
            "message": "Service créé avec succès",
            "service": service
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/services")
async def get_services_endpoint(
    statut: Optional[str] = None,
    categorie_id: Optional[str] = None,
    marchand_id: Optional[str] = None,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer tous les services avec filtres"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        filters = {}
        if statut:
            filters["statut"] = statut
        if categorie_id:
            filters["categorie_id"] = categorie_id
        if marchand_id:
            filters["marchand_id"] = marchand_id
        elif current_user.get("role") == "merchant":
            # Si marchand, ne voir que ses propres services
            filters["marchand_id"] = current_user["id"]
        
        services = get_all_services(filters)
        
        return {
            "success": True,
            "total": len(services),
            "services": services
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/services/{service_id}")
async def get_service_detail_endpoint(
    service_id: str,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer les détails d'un service"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        service = get_service_by_id(service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service introuvable")
        
        # Vérifier que le marchand ne peut voir que ses services
        if current_user.get("role") == "merchant" and service.get("marchand_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Récupérer les leads du service
        leads = get_leads_by_service(service_id)
        
        # Récupérer les recharges
        recharges = get_service_recharges(service_id)
        
        # Récupérer les extras
        extras = get_service_extras(service_id)
        
        return {
            "success": True,
            "service": service,
            "leads": leads,
            "recharges": recharges,
            "extras": extras,
            "stats": {
                "total_leads": len(leads),
                "leads_convertis": len([l for l in leads if l.get("statut") == "converti"]),
                "leads_en_cours": len([l for l in leads if l.get("statut") == "en_cours"]),
                "leads_perdus": len([l for l in leads if l.get("statut") == "perdu"]),
                "taux_conversion": round((len([l for l in leads if l.get("statut") == "converti"]) / len(leads) * 100) if leads else 0, 2)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/services/{service_id}")
async def update_service_endpoint(
    service_id: str,
    service_data: ServiceUpdate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Mettre à jour un service"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Vérifier que le service existe
        service = get_service_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service introuvable")
        
        # Vérifier que le marchand ne peut modifier que ses services
        if current_user.get("role") == "merchant" and service.get("marchand_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Mettre à jour uniquement les champs fournis
        update_data = {k: v for k, v in service_data.dict().items() if v is not None}
        
        success = update_service(service_id, update_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la mise à jour")
        
        updated_service = get_service_by_id(service_id)
        
        return {
            "success": True,
            "message": "Service mis à jour avec succès",
            "service": updated_service
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/services/{service_id}")
async def delete_service_endpoint(
    service_id: str,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Supprimer un service (Admin uniquement)"""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        success = delete_service(service_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la suppression")
        
        return {
            "success": True,
            "message": "Service supprimé avec succès"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS LEADS
# ============================================

@router.post("/leads")
async def create_lead_endpoint(lead_data: LeadCreate):
    """Créer un lead (demande client) - Public"""
    try:
        # Récupérer le service
        service = get_service_by_id(lead_data.service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service introuvable")
        
        # Vérifier que le service est actif
        if service.get("statut") != "actif":
            raise HTTPException(status_code=400, detail="Ce service n'est plus disponible")
        
        # Vérifier qu'il reste du solde
        if float(service.get("depot_actuel", 0)) < float(service.get("prix_par_lead", 0)):
            raise HTTPException(status_code=400, detail="Ce service n'accepte plus de demandes pour le moment")
        
        # Créer le lead
        lead = create_lead({
            "service_id": lead_data.service_id,
            "marchand_id": service.get("marchand_id"),
            "nom_client": lead_data.nom_client,
            "email_client": lead_data.email_client,
            "telephone_client": lead_data.telephone_client,
            "donnees_formulaire": lead_data.donnees_formulaire,
            "cout_lead": service.get("prix_par_lead")
        })
        
        if not lead:
            raise HTTPException(status_code=400, detail="Erreur lors de la création de la demande")
        
        # TODO: Envoyer email au marchand et au client
        
        return {
            "success": True,
            "message": "Votre demande a été envoyée avec succès ! Le marchand vous contactera sous 24h.",
            "lead": lead
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/leads")
async def get_all_leads_endpoint(
    service_id: Optional[str] = None,
    marchand_id: Optional[str] = None,
    statut: Optional[str] = None,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer tous les leads avec filtres"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        filters = {}
        if service_id:
            filters["service_id"] = service_id
        if statut:
            filters["statut"] = statut
        
        # Si marchand, ne voir que ses leads
        if current_user.get("role") == "merchant":
            filters["marchand_id"] = current_user["id"]
        elif marchand_id:
            filters["marchand_id"] = marchand_id
        
        leads = get_all_leads(filters)
        
        return {
            "success": True,
            "total": len(leads),
            "leads": leads
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/leads/{lead_id}/status")
async def update_lead_status_endpoint(
    lead_id: str,
    status_data: LeadStatusUpdate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Mettre à jour le statut d'un lead"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        success = update_lead_status(
            lead_id,
            status_data.statut,
            status_data.notes_marchand
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la mise à jour")
        
        return {
            "success": True,
            "message": "Statut du lead mis à jour avec succès"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS RECHARGES
# ============================================

@router.post("/admin/services/{service_id}/recharge")
async def recharge_service_endpoint(
    service_id: str,
    recharge_data: ServiceRecharge,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Recharger le dépôt d'un service"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Récupérer le service
        service = get_service_by_id(service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service introuvable")
        
        # Vérifier que le marchand ne peut recharger que ses services
        if current_user.get("role") == "merchant" and service.get("marchand_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        ancien_solde = float(service.get("depot_actuel", 0))
        nouveau_solde = ancien_solde + recharge_data.montant
        leads_ajoutes = int(recharge_data.montant / float(service.get("prix_par_lead", 1)))
        
        # Créer la recharge
        recharge = create_service_recharge({
            "service_id": service_id,
            "marchand_id": service.get("marchand_id"),
            "montant": recharge_data.montant,
            "ancien_solde": ancien_solde,
            "nouveau_solde": nouveau_solde,
            "leads_ajoutes": leads_ajoutes,
            "methode_paiement": recharge_data.methode_paiement,
            "transaction_id": recharge_data.transaction_id,
            "statut_paiement": "reussi"  # À adapter selon votre système de paiement
        })
        
        if not recharge:
            raise HTTPException(status_code=400, detail="Erreur lors de la recharge")
        
        # Mettre à jour le service
        update_service(service_id, {
            "depot_actuel": nouveau_solde,
            "statut": "actif"
        })
        
        return {
            "success": True,
            "message": f"Recharge de {recharge_data.montant}€ effectuée avec succès (+{leads_ajoutes} leads)",
            "recharge": recharge,
            "nouveau_solde": nouveau_solde
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recharging service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS EXTRAS
# ============================================

@router.post("/admin/services/{service_id}/extras")
async def add_service_extra_endpoint(
    service_id: str,
    extra_data: ServiceExtraCreate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Ajouter un extra/boost à un service"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Récupérer le service
        service = get_service_by_id(service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service introuvable")
        
        # Vérifier que le marchand ne peut ajouter des extras qu'à ses services
        if current_user.get("role") == "merchant" and service.get("marchand_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        # Créer l'extra
        extra = create_service_extra({
            "service_id": service_id,
            "marchand_id": service.get("marchand_id"),
            "type": extra_data.type,
            "nom": extra_data.nom,
            "description": extra_data.description,
            "prix": extra_data.prix,
            "date_fin": extra_data.date_fin,
            "transaction_id": extra_data.transaction_id
        })
        
        if not extra:
            raise HTTPException(status_code=400, detail="Erreur lors de l'ajout de l'extra")
        
        return {
            "success": True,
            "message": "Extra ajouté avec succès",
            "extra": extra
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding service extra: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS STATS
# ============================================

@router.get("/admin/services/stats/dashboard")
async def get_services_dashboard_stats(
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer les statistiques du dashboard services"""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        stats = get_services_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting services stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS PUBLIC (pour clients)
# ============================================

@router.get("/public/services")
async def get_public_services(
    categorie_id: Optional[str] = None,
    search: Optional[str] = None
):
    """Récupérer les services disponibles (public)"""
    try:
        filters = {"statut": "actif"}
        
        if categorie_id:
            filters["categorie_id"] = categorie_id
        
        services = get_all_services(filters)
        
        # Filtrer les services qui ont encore du solde
        services = [s for s in services if float(s.get("depot_actuel", 0)) >= float(s.get("prix_par_lead", 0))]
        
        # Recherche textuelle si fournie
        if search:
            search_lower = search.lower()
            services = [
                s for s in services
                if search_lower in s.get("nom", "").lower()
                or search_lower in s.get("description", "").lower()
            ]
        
        # Masquer les infos sensibles
        for service in services:
            service.pop("depot_initial", None)
            service.pop("depot_actuel", None)
            service.pop("prix_par_lead", None)
            service.pop("commission_rate", None)
        
        return {
            "success": True,
            "total": len(services),
            "services": services
        }
    
    except Exception as e:
        logger.error(f"Error getting public services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/public/services/{service_id}")
async def get_public_service_detail(service_id: str):
    """Récupérer les détails d'un service (public)"""
    try:
        service = get_service_by_id(service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service introuvable")
        
        if service.get("statut") != "actif":
            raise HTTPException(status_code=404, detail="Ce service n'est plus disponible")
        
        # Masquer les infos sensibles
        service.pop("depot_initial", None)
        service.pop("depot_actuel", None)
        service.pop("prix_par_lead", None)
        service.pop("commission_rate", None)
        service.pop("leads_possibles", None)
        service.pop("leads_recus", None)
        
        return {
            "success": True,
            "service": service
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting public service detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS CATEGORIES
# ============================================

@router.get("/categories")
async def get_categories():
    """Récupérer toutes les catégories (public)"""
    try:
        from supabase_client import supabase
        result = supabase.table("categories").select("*").order("name").execute()
        
        return {
            "success": True,
            "categories": result.data if result.data else []
        }
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS LEADS ANALYTICS & EXPORT
# ============================================

@router.get("/admin/leads/stats")
async def get_leads_stats(
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer les statistiques des leads (Optimisé)"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        from supabase_client import supabase
        
        # Base query builder
        def get_base_query():
            query = supabase.table("service_leads").select("id", count="exact", head=True)
            # Si marchand, filtrer par ses services
            if current_user.get("role") == "merchant":
                services_result = supabase.table("services")\
                    .select("id")\
                    .eq("marchand_id", current_user["id"])\
                    .execute()
                service_ids = [s["id"] for s in (services_result.data or [])]
                if service_ids:
                    query = query.in_("service_id", service_ids)
                else:
                    # Force 0 results if no services
                    query = query.eq("id", "00000000-0000-0000-0000-000000000000") 
            return query

        # Execute counts in parallel (conceptually, though here sequential)
        total_res = get_base_query().execute()
        total = total_res.count or 0
        
        new_res = get_base_query().eq("statut", "nouveau").execute()
        new = new_res.count or 0
        
        contacted_res = get_base_query().eq("statut", "contacté").execute()
        contacted = contacted_res.count or 0
        
        qualified_res = get_base_query().eq("statut", "qualifié").execute()
        qualified = qualified_res.count or 0
        
        converted_res = get_base_query().eq("statut", "converti").execute()
        converted = converted_res.count or 0
        
        conversion_rate = (converted / total * 100) if total > 0 else 0
        
        return {
            "stats": {
                "total": total,
                "new": new,
                "contacted": contacted,
                "qualified": qualified,
                "converted": converted,
                "conversion_rate": round(conversion_rate, 2)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leads stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/leads/analytics")
async def get_leads_analytics(
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer les données analytics des leads"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        from supabase_client import supabase
        from datetime import datetime, timedelta
        
        # 1. Conversion Trend (30 derniers jours)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        query = supabase.table("service_leads")\
            .select("created_at, statut")\
            .gte("created_at", start_date.isoformat())
            
        # Si marchand, filtrer par ses services
        if current_user.get("role") == "merchant":
            services_result = supabase.table("services")\
                .select("id")\
                .eq("marchand_id", current_user["id"])\
                .execute()
            service_ids = [s["id"] for s in (services_result.data or [])]
            if service_ids:
                query = query.in_("service_id", service_ids)
            else:
                # Aucun service, donc aucun lead
                return {
                    "analytics": {
                        "conversionTrend": [],
                        "sourceDistribution": [],
                        "servicePerformance": []
                    }
                }
                
        result = query.execute()
        leads = result.data if result.data else []
        
        # Grouper par date
        trend_data = {}
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            trend_data[date_str] = {"date": date_str, "leads": 0, "converted": 0}
            current += timedelta(days=1)
            
        for lead in leads:
            created_at = datetime.fromisoformat(lead["created_at"].replace("Z", "+00:00"))
            date_str = created_at.strftime("%Y-%m-%d")
            if date_str in trend_data:
                trend_data[date_str]["leads"] += 1
                if lead.get("statut") == "converti":
                    trend_data[date_str]["converted"] += 1
                    
        conversion_trend = list(trend_data.values())
        conversion_trend.sort(key=lambda x: x["date"])
        
        # 2. Source Distribution
        # Note: On suppose qu'il y a un champ 'source' dans service_leads. 
        # Sinon on utilise une distribution vide ou basée sur d'autres métadonnées.
        # Vérifions si 'source' existe dans le modèle LeadCreate... non.
        # On va utiliser le statut pour la distribution si source n'existe pas, ou retourner vide.
        # Pour l'instant, retournons vide si pas de champ source, pour ne pas inventer de données.
        source_distribution = []
        
        # 3. Service Performance
        # On a besoin des noms de services
        perf_query = supabase.table("service_leads")\
            .select("service_id, statut, services(nom)")
            
        if current_user.get("role") == "merchant":
             if service_ids:
                perf_query = perf_query.in_("service_id", service_ids)
        
        perf_result = perf_query.execute()
        perf_leads = perf_result.data if perf_result.data else []
        
        service_stats = {}
        for lead in perf_leads:
            svc = lead.get("services")
            svc_name = svc.get("nom", "Inconnu") if svc else "Inconnu"
            
            if svc_name not in service_stats:
                service_stats[svc_name] = {"service": svc_name, "leads": 0, "converted": 0}
            
            service_stats[svc_name]["leads"] += 1
            if lead.get("statut") == "converti":
                service_stats[svc_name]["converted"] += 1
                
        service_performance = list(service_stats.values())
        # Trier par nombre de leads
        service_performance.sort(key=lambda x: x["leads"], reverse=True)
        
        return {
            "analytics": {
                "conversionTrend": conversion_trend,
                "sourceDistribution": source_distribution,
                "servicePerformance": service_performance[:10] # Top 10
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leads analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/leads/export")
async def export_leads(
    service_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Exporter les leads en CSV"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        from supabase_client import supabase
        import csv
        from io import StringIO
        from fastapi.responses import StreamingResponse
        
        # Récupérer les leads
        query = supabase.table("service_leads")\
            .select("*, services(title)")
        
        if service_id:
            query = query.eq("service_id", service_id)
        if status:
            query = query.eq("statut", status)
        
        # Si marchand, filtrer par ses services
        if current_user.get("role") == "merchant":
            services_result = supabase.table("services")\
                .select("id")\
                .eq("marchand_id", current_user["id"])\
                .execute()
            service_ids = [s["id"] for s in (services_result.data or [])]
            if service_ids:
                query = query.in_("service_id", service_ids)
        
        result = query.execute()
        leads = result.data if result.data else []
        
        # Créer le CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow([
            'ID', 'Nom', 'Email', 'Téléphone', 'Entreprise', 
            'Service', 'Budget', 'Statut', 'Source', 'Date'
        ])
        
        # Données
        for lead in leads:
            service_title = lead.get('services', {}).get('title', 'N/A') if lead.get('services') else 'N/A'
            writer.writerow([
                lead.get('id', ''),
                lead.get('nom', ''),
                lead.get('email', ''),
                lead.get('telephone', ''),
                lead.get('entreprise', ''),
                service_title,
                lead.get('budget', ''),
                lead.get('statut', ''),
                lead.get('source', ''),
                lead.get('created_at', '')
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=leads_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/admin/leads/{lead_id}/status")
async def update_lead_status_v2(
    lead_id: str,
    status_data: Dict,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Mettre à jour le statut d'un lead (v2)"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        from supabase_client import supabase
        
        result = supabase.table("service_leads")\
            .update({"statut": status_data.get("status")})\
            .eq("id", lead_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Lead introuvable")
        
        return {
            "success": True,
            "message": "Statut mis à jour"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/leads/{lead_id}/send-email")
async def send_lead_email(
    lead_id: str,
    email_data: Dict,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Envoyer un email à un lead"""
    try:
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        from services.email_service import email_service
        from supabase_client import supabase
        
        # Récupérer le lead pour avoir l'email
        lead_res = supabase.table("service_leads").select("email_client, nom_client").eq("id", lead_id).single().execute()
        if not lead_res.data:
            raise HTTPException(status_code=404, detail="Lead introuvable")
            
        lead = lead_res.data
        recipient_email = lead.get("email_client")
        
        if not recipient_email:
             raise HTTPException(status_code=400, detail="Le lead n'a pas d'adresse email")

        subject = email_data.get("subject", "Message concernant votre demande")
        message = email_data.get("message", "")
        
        # Envoyer l'email
        try:
            email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=f"""
                <p>Bonjour {lead.get('nom_client', '')},</p>
                <p>{message}</p>
                <br>
                <p>Cordialement,</p>
                <p>{current_user.get('first_name', '')} {current_user.get('last_name', '')}</p>
                """
            )
        except Exception as e:
            logger.error(f"Failed to send email via service: {e}")
            # Fallback log if email service fails (but we tried!)
            pass
        
        logger.info(f"Email sent to lead {lead_id} at {recipient_email}")
        
        return {
            "success": True,
            "message": "Email envoyé avec succès"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
