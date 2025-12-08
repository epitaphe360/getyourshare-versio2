"""
Routes API GDPR/RGPD Compliance
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import json

from auth import get_current_user_from_cookie
from db_helpers import supabase
from services.gdpr_service import GDPRService

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gdpr", tags=["GDPR/RGPD"])

# Initialize service
gdpr_service = GDPRService(supabase)


# ============================================
# MODELS
# ============================================

class CookieConsentRequest(BaseModel):
    analytics: bool = False
    marketing: bool = False
    personalization: bool = False
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class DeleteAccountRequest(BaseModel):
    deletion_type: str = 'full'  # 'full' ou 'anonymize'
    reason: Optional[str] = None
    confirmation_email: EmailStr
    confirmation_password: str


# ============================================
# ENDPOINTS
# ============================================

@router.get("/export")
async def export_user_data(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Export COMPLET des données utilisateur (GDPR Art. 20)

    Retourne toutes les données personnelles dans un format JSON structuré.
    L'utilisateur peut télécharger ce fichier.
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        export_data = gdpr_service.export_user_data(user_id)

        # Retourner comme téléchargement JSON
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)

        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=my_data_export_{user_id}.json"
            }
        )

    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete-account")
async def delete_account(
    request: DeleteAccountRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Suppression du compte utilisateur (Right to be forgotten - GDPR Art. 17)

    ATTENTION: Cette action est IRRÉVERSIBLE si deletion_type='full'

    Options:
    - 'full': Suppression complète et définitive
    - 'anonymize': Anonymisation (garde les données comptables mais anonymisées)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        user_email = payload.get("email")

        # Vérifier l'email de confirmation
        if request.confirmation_email != user_email:
            raise HTTPException(
                status_code=400,
                detail="L'email de confirmation ne correspond pas"
            )

        # TODO: Vérifier le mot de passe (bcrypt check)
        # Pour l'instant, on accepte

        # Supprimer le compte
        result = gdpr_service.delete_user_account(
            user_id=user_id,
            deletion_type=request.deletion_type,
            reason=request.reason
        )

        return {
            "success": True,
            **result,
            "message": "Votre compte a été supprimé. Vous allez être déconnecté."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consent/cookies")
async def update_cookie_consent(
    request: CookieConsentRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre à jour les consentements cookies (granulaire)

    Types de cookies:
    - necessary: Cookies essentiels (toujours actifs)
    - analytics: Google Analytics, statistiques
    - marketing: Publicité ciblée, remarketing
    - personalization: Préférences utilisateur, UX
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        consent_data = request.dict()

        result = gdpr_service.update_cookie_consent(user_id, consent_data)

        return {
            "success": True,
            **result,
            "message": "Préférences cookies mises à jour"
        }

    except Exception as e:
        logger.error(f"Error updating cookie consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consent/cookies")
async def get_cookie_consent(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupérer les consentements cookies actuels
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        result = gdpr_service.get_cookie_consent(user_id)

        return result

    except Exception as e:
        logger.error(f"Error getting cookie consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-processing-register")
async def get_data_processing_register():
    """
    Registre des traitements de données (GDPR Art. 30)

    Liste TOUS les traitements de données personnelles effectués.
    Accessible publiquement (transparence GDPR).
    """
    try:
        register = gdpr_service.get_data_processing_register()

        return {
            "success": True,
            "register": register,
            "total": len(register)
        }

    except Exception as e:
        logger.error(f"Error getting data processing register: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/privacy-policy")
async def get_privacy_policy():
    """
    Politique de confidentialité

    Retourne la politique complète de confidentialité
    """
    privacy_policy = {
        "version": "2.0",
        "last_updated": "2025-12-07",
        "language": "fr",
        "sections": [
            {
                "title": "1. Responsable du traitement",
                "content": "GetYourShare, société [à compléter], est responsable du traitement de vos données personnelles."
            },
            {
                "title": "2. Données collectées",
                "content": "Nous collectons les données suivantes: identité, contact, données de connexion, données bancaires (pour paiements), cookies (avec consentement)."
            },
            {
                "title": "3. Finalités du traitement",
                "content": "Vos données sont traitées pour: gestion de votre compte, traitement des paiements, amélioration de nos services, marketing (avec consentement), conformité légale."
            },
            {
                "title": "4. Base légale",
                "content": "Contrat (gestion compte, paiements), Consentement (cookies, marketing), Obligation légale (KYC, comptabilité), Intérêt légitime (sécurité, amélioration)."
            },
            {
                "title": "5. Destinataires des données",
                "content": "Vos données peuvent être partagées avec: notre équipe interne, prestataires techniques (Supabase, Stripe), autorités (si obligation légale)."
            },
            {
                "title": "6. Durée de conservation",
                "content": "Compte actif: durée du contrat. Après fermeture: 3 ans (données commerciales), 10 ans (données comptables/fiscales). Cookies: 25 mois max."
            },
            {
                "title": "7. Vos droits GDPR",
                "content": "Vous disposez des droits suivants: Accès (Art. 15), Rectification (Art. 16), Effacement (Art. 17), Portabilité (Art. 20), Opposition (Art. 21), Limitation (Art. 18). Contact: dpo@getyourshare.com"
            },
            {
                "title": "8. Sécurité",
                "content": "Nous mettons en œuvre des mesures de sécurité: chiffrement, authentification 2FA, accès restreints, audits réguliers, conformité PCI-DSS (paiements)."
            },
            {
                "title": "9. Cookies",
                "content": "Nous utilisons des cookies avec votre consentement (sauf cookies essentiels). Vous pouvez gérer vos préférences à tout moment."
            },
            {
                "title": "10. Contact DPO",
                "content": "Pour toute question relative à vos données: dpo@getyourshare.com ou via notre formulaire de contact."
            }
        ]
    }

    return privacy_policy


@router.get("/terms-of-service")
async def get_terms_of_service():
    """
    Conditions Générales d'Utilisation (CGU)
    """
    terms = {
        "version": "2.0",
        "last_updated": "2025-12-07",
        "language": "fr",
        "sections": [
            {
                "title": "1. Acceptation des CGU",
                "content": "En utilisant GetYourShare, vous acceptez ces conditions générales d'utilisation."
            },
            {
                "title": "2. Services fournis",
                "content": "GetYourShare est une plateforme d'affiliation connectant influenceurs et marchands."
            },
            {
                "title": "3. Inscription",
                "content": "L'inscription nécessite des informations exactes. Vous êtes responsable de votre compte."
            },
            {
                "title": "4. Commissions",
                "content": "Les taux de commission sont définis par chaque marchand. GetYourShare prélève une commission de plateforme."
            },
            {
                "title": "5. Paiements",
                "content": "Les paiements sont effectués mensuellement sous réserve d'un seuil minimum de 50 MAD."
            },
            {
                "title": "6. Responsabilités",
                "content": "GetYourShare agit comme intermédiaire. Les transactions sont entre marchands et clients finaux."
            },
            {
                "title": "7. Propriété intellectuelle",
                "content": "Le contenu de GetYourShare est protégé par le droit d'auteur."
            },
            {
                "title": "8. Résiliation",
                "content": "Vous pouvez fermer votre compte à tout moment. GetYourShare peut suspendre un compte en cas de violation."
            },
            {
                "title": "9. Droit applicable",
                "content": "Ces CGU sont régies par le droit [marocain/français/applicable]."
            },
            {
                "title": "10. Contact",
                "content": "Pour toute question: support@getyourshare.com"
            }
        ]
    }

    return terms


@router.get("/dpo-contact")
async def get_dpo_contact():
    """
    Informations de contact du DPO (Data Protection Officer)
    """
    return {
        "dpo": {
            "name": "À définir",
            "email": "dpo@getyourshare.com",
            "phone": "+212 [à compléter]",
            "address": "GetYourShare, [adresse à compléter]",
            "response_time": "30 jours maximum (GDPR)"
        },
        "rights_requests": {
            "access": "Demander une copie de vos données",
            "rectification": "Corriger des données inexactes",
            "erasure": "Demander la suppression de vos données",
            "portability": "Récupérer vos données dans un format structuré",
            "objection": "S'opposer à un traitement",
            "restriction": "Limiter le traitement de vos données"
        },
        "complaint": {
            "authority": "CNDP (Commission Nationale de Contrôle de la Protection des Données Personnelles) - Maroc",
            "email": "contact@cndp.ma",
            "website": "https://www.cndp.ma"
        }
    }
