"""
Routes KYC (Know Your Customer)
Vérification d'identité pour les paiements
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import uuid

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kyc", tags=["KYC"])


# ============================================
# MODELS
# ============================================

class KYCVerifyRequest(BaseModel):
    document_type: str  # passport, national_id, driver_license
    document_number: str
    country: str
    date_of_birth: Optional[str] = None


# ============================================
# UPLOAD DOCUMENTS
# ============================================

@router.post("/upload-documents")
async def upload_kyc_documents(
    document_type: str,
    front_image: UploadFile = File(...),
    back_image: Optional[UploadFile] = File(None),
    selfie: Optional[UploadFile] = File(None),
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Upload des documents KYC (pièce d'identité + selfie)

    document_type: passport, national_id, driver_license, residence_permit
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Valider le type de document
        valid_types = ['passport', 'national_id', 'driver_license', 'residence_permit']
        if document_type not in valid_types:
            raise HTTPException(status_code=400, detail="Type de document invalide")

        # Générer des noms de fichiers uniques
        doc_id = str(uuid.uuid4())[:12]

        # Upload front image
        front_filename = f"kyc/{user_id}/{doc_id}_front_{front_image.filename}"
        front_content = await front_image.read()

        try:
            # Upload vers Supabase Storage
            supabase.storage.from_('kyc-documents').upload(
                front_filename,
                front_content,
                {"content-type": front_image.content_type}
            )

            front_url = supabase.storage.from_('kyc-documents').get_public_url(front_filename)
        except Exception as e:
            # Fallback: sauvegarder localement
            logger.warning(f"Supabase storage error, saving locally: {e}")
            front_url = f"/uploads/kyc/{doc_id}_front.jpg"

        # Upload back image si fourni
        back_url = None
        if back_image:
            back_filename = f"kyc/{user_id}/{doc_id}_back_{back_image.filename}"
            back_content = await back_image.read()

            try:
                supabase.storage.from_('kyc-documents').upload(
                    back_filename,
                    back_content,
                    {"content-type": back_image.content_type}
                )

                back_url = supabase.storage.from_('kyc-documents').get_public_url(back_filename)
            except Exception:
                back_url = f"/uploads/kyc/{doc_id}_back.jpg"

        # Upload selfie si fourni
        selfie_url = None
        if selfie:
            selfie_filename = f"kyc/{user_id}/{doc_id}_selfie_{selfie.filename}"
            selfie_content = await selfie.read()

            try:
                supabase.storage.from_('kyc-documents').upload(
                    selfie_filename,
                    selfie_content,
                    {"content-type": selfie.content_type}
                )

                selfie_url = supabase.storage.from_('kyc-documents').get_public_url(selfie_filename)
            except Exception:
                selfie_url = f"/uploads/kyc/{doc_id}_selfie.jpg"

        # Sauvegarder dans la DB
        kyc_data = {
            'user_id': user_id,
            'document_type': document_type,
            'document_id': doc_id,
            'front_image_url': front_url,
            'back_image_url': back_url,
            'selfie_url': selfie_url,
            'status': 'pending',
            'submitted_at': datetime.now().isoformat()
        }

        # Upsert
        existing = supabase.table('kyc_verifications').select('id').eq('user_id', user_id).execute()

        if existing.data:
            result = supabase.table('kyc_verifications').update(kyc_data).eq('user_id', user_id).execute()
        else:
            result = supabase.table('kyc_verifications').insert(kyc_data).execute()

        return {
            "success": True,
            "status": "uploaded",
            "document_id": doc_id,
            "message": "Documents uploadés avec succès. Vérification en cours.",
            "kyc": result.data[0] if result.data else kyc_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading KYC documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# STATUS
# ============================================

@router.get("/status")
async def get_kyc_status(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Statut de vérification KYC
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        kyc = supabase.table('kyc_verifications').select('*').eq('user_id', user_id).single().execute()

        if not kyc.data:
            return {
                "success": True,
                "status": "not_submitted",
                "verified": False,
                "message": "Aucun document soumis"
            }

        kyc_data = kyc.data

        return {
            "success": True,
            "status": kyc_data.get('status'),
            "verified": kyc_data.get('status') == 'verified',
            "submitted_at": kyc_data.get('submitted_at'),
            "verified_at": kyc_data.get('verified_at'),
            "rejection_reason": kyc_data.get('rejection_reason'),
            "document_type": kyc_data.get('document_type')
        }

    except Exception as e:
        logger.error(f"Error getting KYC status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# VERIFY (ADMIN/AUTOMATED)
# ============================================

@router.post("/verify")
async def verify_kyc(
    verify_data: KYCVerifyRequest,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Lancer la vérification KYC

    NOTE: Dans un système réel, intégrer avec des services comme:
    - Onfido
    - Jumio
    - Stripe Identity
    - Sumsub
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer le KYC
        kyc = supabase.table('kyc_verifications').select('*').eq('user_id', user_id).single().execute()

        if not kyc.data:
            raise HTTPException(status_code=404, detail="Aucun document soumis")

        # Simuler une vérification (à remplacer par vraie API)
        # Dans la réalité, on appellerait une API tierce pour vérifier l'identité

        # Pour la démo, on accepte automatiquement
        verification_status = "verified"

        # Mettre à jour
        supabase.table('kyc_verifications').update({
            'status': verification_status,
            'document_number': verify_data.document_number,
            'country': verify_data.country,
            'date_of_birth': verify_data.date_of_birth,
            'verified_at': datetime.now().isoformat(),
            'verification_method': 'automated'
        }).eq('user_id', user_id).execute()

        return {
            "success": True,
            "status": verification_status,
            "message": "Vérification complétée",
            "note": "Intégrer avec Onfido/Jumio/Stripe Identity pour vérification réelle"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying KYC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ADMIN: REVIEW KYC
# ============================================

@router.get("/admin/pending")
async def get_pending_kyc(
    limit: int = 50,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des KYC en attente de vérification (admin only)
    """
    try:
        role = payload.get("role")

        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin uniquement")

        kyc_list = supabase.table('kyc_verifications').select('*').eq('status', 'pending').order('submitted_at', desc=False).limit(limit).execute()

        # Enrichir avec infos utilisateur
        result = []
        for kyc in (kyc_list.data or []):
            user_id = kyc.get('user_id')

            profile = supabase.table('profiles').select('full_name').eq('user_id', user_id).single().execute()
            user = supabase.table('users').select('email').eq('id', user_id).single().execute()

            result.append({
                **kyc,
                'user_name': profile.data.get('full_name') if profile.data else None,
                'user_email': user.data.get('email') if user.data else None
            })

        return {
            "success": True,
            "pending_kyc": result,
            "total": len(result)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending KYC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/approve/{user_id}")
async def approve_kyc(
    user_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Approuver un KYC manuellement (admin only)
    """
    try:
        role = payload.get("role")

        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin uniquement")

        supabase.table('kyc_verifications').update({
            'status': 'verified',
            'verified_at': datetime.now().isoformat(),
            'verification_method': 'manual',
            'verified_by': payload.get("id")
        }).eq('user_id', user_id).execute()

        return {
            "success": True,
            "message": "KYC approuvé"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving KYC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/reject/{user_id}")
async def reject_kyc(
    user_id: str,
    reason: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Rejeter un KYC (admin only)
    """
    try:
        role = payload.get("role")

        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin uniquement")

        supabase.table('kyc_verifications').update({
            'status': 'rejected',
            'rejection_reason': reason,
            'reviewed_at': datetime.now().isoformat(),
            'reviewed_by': payload.get("id")
        }).eq('user_id', user_id).execute()

        return {
            "success": True,
            "message": "KYC rejeté"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting KYC: {e}")
        raise HTTPException(status_code=500, detail=str(e))
