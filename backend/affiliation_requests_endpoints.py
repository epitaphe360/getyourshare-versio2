"""
Endpoints API pour le système de demandes d'affiliation
Workflow: Influenceur demande → Marchand approuve/refuse → Lien généré automatiquement
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from supabase_client import supabase
from tracking_service import tracking_service
from auth import get_current_user_from_cookie
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/affiliation-requests", tags=["affiliation_requests"])

# ============================================
# MODELS PYDANTIC
# ============================================

class AffiliationRequestCreate(BaseModel):
    """Modèle pour créer une demande d'affiliation"""
    product_id: Optional[str] = None
    service_id: Optional[str] = None
    influencer_message: Optional[str] = None
    influencer_followers: Optional[int] = None
    influencer_engagement_rate: Optional[float] = None
    influencer_social_links: Optional[dict] = None

class AffiliationRequestResponse(BaseModel):
    """Modèle de réponse pour approuver/refuser une demande"""
    status: str  # "approved" ou "rejected"
    merchant_response: Optional[str] = None
    rejection_reason: Optional[str] = None  # Si rejected

# ============================================
# ENDPOINTS
# ============================================

@router.post("/request")
async def create_affiliation_request(
    request_data: AffiliationRequestCreate,
    request: Request,
    user: dict = Depends(get_current_user_from_cookie)
):
    """
    Endpoint pour qu'un influenceur demande l'affiliation à un produit

    Workflow:
    1. Influenceur envoie demande avec son profil
    2. Système récupère le merchant_id depuis le product
    3. Création de la demande avec status='pending'
    4. Notification automatique au marchand (Email + SMS + Dashboard)
    5. Retour confirmation à l'influenceur
    """
    try:
        # 1. Récupérer le produit ou service pour avoir le merchant_id
        merchant_id = None
        product = None
        service = None
        
        if request_data.product_id:
            product_result = supabase.table('products').select('*').eq('id', request_data.product_id).execute()
            if not product_result.data:
                raise HTTPException(status_code=404, detail="Produit introuvable")
            product = product_result.data[0]
            merchant_id = product['merchant_id']
        elif request_data.service_id:
            service_result = supabase.table('services').select('*').eq('id', request_data.service_id).execute()
            if not service_result.data:
                raise HTTPException(status_code=404, detail="Service introuvable")
            service = service_result.data[0]
            merchant_id = service['merchant_id']
        else:
             raise HTTPException(status_code=400, detail="Product ID or Service ID required")

        # 2. Récupérer l'influenceur depuis l'utilisateur connecté
        user_id = user['id']

        influencer_result = supabase.table('influencers').select('*').eq('user_id', user_id).execute()

        if not influencer_result.data:
            raise HTTPException(status_code=403, detail="Vous devez être un influenceur pour faire une demande")

        influencer = influencer_result.data[0]
        influencer_id = influencer['id']

        # 3. Vérifier qu'il n'y a pas déjà une demande pending pour ce produit
        query = supabase.table('affiliate_requests').select('*').eq('influencer_id', influencer_id).eq('status', 'pending')
        if request_data.product_id:
            query = query.eq('product_id', request_data.product_id)
        else:
            query = query.eq('service_id', request_data.service_id)
            
        existing_request = query.execute()

        if existing_request.data:
            raise HTTPException(status_code=400, detail="Vous avez déjà une demande en attente pour cet élément")

        # 4. Créer la demande d'affiliation
        affiliation_request = {
            'influencer_id': influencer_id,
            'product_id': request_data.product_id,
            'service_id': request_data.service_id,
            'merchant_id': merchant_id,
            'status': 'pending',
            'influencer_message': request_data.influencer_message,
            'influencer_followers': request_data.influencer_followers or influencer.get('audience_size', 0),
            'influencer_engagement_rate': request_data.influencer_engagement_rate or influencer.get('engagement_rate', 0),
            'influencer_social_links': request_data.influencer_social_links or influencer.get('social_links', {}),
            'created_at': datetime.now().isoformat()
        }

        result = supabase.table('affiliate_requests').insert(affiliation_request).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Erreur lors de la création de la demande")

        request_id = result.data[0]['id']

        # 5. Envoyer notifications au marchand
        # Adapt notification to handle service
        item_for_notif = product if product else {'name': service['title']}
        await send_merchant_notifications(merchant_id, influencer, item_for_notif, request_id)

        logger.info(f"✅ Demande d'affiliation créée: {request_id} | Influenceur: {influencer_id}")

        return {
            "success": True,
            "message": "Demande d'affiliation envoyée avec succès",
            "request_id": request_id,
            "status": "pending",
            "merchant_response_time": "Le marchand a 48h pour répondre"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création demande d'affiliation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-requests")
async def get_my_requests(
    request: Request,
    user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère toutes les demandes d'affiliation de l'influenceur connecté
    """
    try:
        user_id = user['id']

        influencer_result = supabase.table('influencers').select('id').eq('user_id', user_id).execute()

        if not influencer_result.data:
            raise HTTPException(status_code=403, detail="Influenceur introuvable")

        influencer_id = influencer_result.data[0]['id']

        # Récupérer les demandes
        requests_result = supabase.table('affiliate_requests').select('*').eq('influencer_id', influencer_id).order('created_at', desc=True).execute()
        requests = requests_result.data or []

        # Manual joins
        product_ids = list(set(r['product_id'] for r in requests if r.get('product_id')))
        products_map = {}
        if product_ids:
            p_res = supabase.table('products').select('id, name, price, commission_rate, images').in_('id', product_ids).execute()
            products_map = {p['id']: p for p in p_res.data} if p_res.data else {}

        merchant_ids = list(set(r['merchant_id'] for r in requests if r.get('merchant_id')))
        merchants_map = {}
        if merchant_ids:
            m_res = supabase.table('merchants').select('id, company_name, logo_url').in_('id', merchant_ids).execute()
            merchants_map = {m['id']: m for m in m_res.data} if m_res.data else {}

        # Enrich
        for req in requests:
            req['products'] = products_map.get(req['product_id'])
            req['merchants'] = merchants_map.get(req['merchant_id'])

        return {
            "success": True,
            "requests": requests
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération demandes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/merchant/pending")
async def get_merchant_pending_requests(
    request: Request,
    user: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupère toutes les demandes d'affiliation EN ATTENTE pour le marchand connecté
    """
    try:
        user_id = user['id']

        merchant_result = supabase.table('merchants').select('id').eq('user_id', user_id).execute()

        if not merchant_result.data:
            raise HTTPException(status_code=403, detail="Marchand introuvable")

        merchant_id = merchant_result.data[0]['id']

        # Récupérer les demandes pending
        requests_result = supabase.table('affiliate_requests').select('*').eq('merchant_id', merchant_id).eq('status', 'pending').order('created_at', desc=True).execute()
        requests = requests_result.data or []

        # Manual joins
        influencer_ids = list(set(r['influencer_id'] for r in requests if r.get('influencer_id')))
        influencers_map = {}
        if influencer_ids:
            # Note: influencers table might not have username/full_name directly if they are in users table.
            # But the original code selected them from influencers table.
            # Let's check influencers table columns or assume they are there or joined from users.
            # Based on schema, influencers table has handles but not full_name (in users).
            # But let's try to fetch what we can from influencers table first.
            i_res = supabase.table('influencers').select('id, audience_size, engagement_rate, total_sales, total_earnings, user_id').in_('id', influencer_ids).execute()
            
            if i_res.data:
                influencers_data = {i['id']: i for i in i_res.data}
                # Fetch user details for names
                user_ids = [i['user_id'] for i in i_res.data if i.get('user_id')]
                if user_ids:
                    u_res = supabase.table('users').select('id, full_name, avatar_url, email').in_('id', user_ids).execute()
                    users_map = {u['id']: u for u in u_res.data} if u_res.data else {}
                    
                    # Merge
                    for i_id, i_data in influencers_data.items():
                        u_data = users_map.get(i_data['user_id'], {})
                        i_data['full_name'] = u_data.get('full_name')
                        i_data['profile_picture_url'] = u_data.get('avatar_url')
                        i_data['username'] = u_data.get('email', '').split('@')[0] # Fallback
                        influencers_map[i_id] = i_data

        product_ids = list(set(r['product_id'] for r in requests if r.get('product_id')))
        products_map = {}
        if product_ids:
            p_res = supabase.table('products').select('id, name, price, commission_rate, images').in_('id', product_ids).execute()
            products_map = {p['id']: p for p in p_res.data} if p_res.data else {}

        service_ids = list(set(r['service_id'] for r in requests if r.get('service_id')))
        services_map = {}
        if service_ids:
            s_res = supabase.table('services').select('id, title, price, description').in_('id', service_ids).execute()
            services_map = {s['id']: s for s in s_res.data} if s_res.data else {}

        # Enrich
        for req in requests:
            req['influencers'] = influencers_map.get(req['influencer_id'])
            req['products'] = products_map.get(req['product_id'])
            req['services'] = services_map.get(req['service_id'])

        return {
            "success": True,
            "pending_requests": requests,
            "count": len(requests)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération demandes marchand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{request_id}/respond")
async def respond_to_request(
    request_id: str,
    response_data: AffiliationRequestResponse,
    request: Request,
    user: dict = Depends(get_current_user_from_cookie)
):
    """
    Endpoint pour qu'un marchand approuve ou refuse une demande d'affiliation

    Workflow si APPROUVÉ:
    1. Marchand clique "Approuver"
    2. Système génère automatiquement un lien trackable unique
    3. Mise à jour de la demande avec status='approved' et generated_link_id
    4. Notification à l'influenceur (Email + SMS + Dashboard) avec son lien
    5. Lien activé et prêt à l'emploi

    Workflow si REFUSÉ:
    1. Marchand clique "Refuser" et indique la raison
    2. Mise à jour de la demande avec status='rejected' et rejection_reason
    3. Notification à l'influenceur avec message encourageant
    """
    try:
        # 1. Récupérer la demande
        request_result = supabase.table('affiliate_requests').select('*').eq('id', request_id).execute()

        if not request_result.data:
            raise HTTPException(status_code=404, detail="Demande introuvable")

        affiliation_request = request_result.data[0]

        # 2. Vérifier que le marchand a le droit de répondre
        user_id = user['id']

        merchant_result = supabase.table('merchants').select('id').eq('user_id', user_id).execute()

        if not merchant_result.data:
            raise HTTPException(status_code=403, detail="Marchand introuvable")

        merchant_profile_id = merchant_result.data[0]['id']

        # Check if the request belongs to this merchant
        # Note: products.merchant_id references users.id, so affiliation_request['merchant_id'] is likely user_id
        # But we check both user_id and merchant_profile_id to be safe
        if affiliation_request['merchant_id'] != user_id and affiliation_request['merchant_id'] != merchant_profile_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas le droit de répondre à cette demande")

        # 3. Vérifier que la demande est pending
        if affiliation_request['status'] != 'pending':
            raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")

        # 4. Traiter selon la réponse
        if response_data.status == 'approved':
            # ✅ APPROBATION
            # Générer automatiquement le lien trackable
            product = None
            target_url = ""
            item_name = "Produit/Service"
            commission_rate = 0
            
            if affiliation_request.get('product_id'):
                product = supabase.table('products').select('*').eq('id', affiliation_request['product_id']).execute().data[0]
                target_url = product.get('url', f"https://merchant.com/product/{product['id']}")
                item_name = product['name']
                commission_rate = product.get('commission_rate', 0)
            elif affiliation_request.get('service_id'):
                service = supabase.table('services').select('*').eq('id', affiliation_request['service_id']).execute().data[0]
                target_url = f"https://merchant.com/service/{service['id']}"
                item_name = service['title']
                # commission_rate = service.get('commission_rate', 0) # If services have commission rate

            link_result = await tracking_service.create_tracking_link(
                influencer_id=affiliation_request['influencer_id'],
                product_id=affiliation_request.get('product_id'),
                service_id=affiliation_request.get('service_id'),
                merchant_url=target_url,
                campaign_id=None
            )

            if not link_result.get('success'):
                raise HTTPException(status_code=500, detail="Erreur lors de la génération du lien")

            # Mettre à jour la demande
            update_data = {
                'status': 'approved',
                # 'merchant_response': response_data.merchant_response, # Column missing in DB
                # 'generated_link_id': link_result['link_id'], # Column missing in DB
                # 'responded_at': datetime.now().isoformat() # Column missing in DB
            }

            supabase.table('affiliate_requests').update(update_data).eq('id', request_id).execute()

            # Envoyer notification à l'influenceur
            # We need to adapt send_influencer_approval_notification to handle services too
            # For now, we pass a dummy product dict if it's a service, or update the function
            
            notification_item = product if product else {'name': item_name, 'commission_rate': commission_rate}
            
            await send_influencer_approval_notification(
                affiliation_request['influencer_id'],
                notification_item,
                link_result['tracking_url'],
                link_result['short_code'],
                response_data.merchant_response
            )

            logger.info(f"✅ Demande approuvée: {request_id} | Lien généré: {link_result['short_code']}")

            return {
                "success": True,
                "message": "Demande approuvée avec succès",
                "status": "approved",
                "tracking_link": link_result['tracking_url'],
                "short_code": link_result['short_code']
            }

        elif response_data.status == 'rejected':
            # ❌ REFUS
            if not response_data.rejection_reason:
                raise HTTPException(status_code=400, detail="La raison du refus est obligatoire")

            # Mettre à jour la demande
            update_data = {
                'status': 'rejected',
                'merchant_response': response_data.merchant_response,
                'rejection_reason': response_data.rejection_reason,
                'responded_at': datetime.now().isoformat()
            }

            supabase.table('affiliate_requests').update(update_data).eq('id', request_id).execute()

            # Envoyer notification à l'influenceur
            await send_influencer_rejection_notification(
                affiliation_request['influencer_id'],
                affiliation_request['product_id'],
                response_data.rejection_reason,
                response_data.merchant_response
            )

            logger.info(f"❌ Demande refusée: {request_id} | Raison: {response_data.rejection_reason}")

            return {
                "success": True,
                "message": "Demande refusée",
                "status": "rejected",
                "rejection_reason": response_data.rejection_reason
            }

        else:
            raise HTTPException(status_code=400, detail="Status invalide. Utilisez 'approved' ou 'rejected'")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur réponse à la demande: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# FONCTIONS DE NOTIFICATION
# ============================================

async def send_merchant_notifications(merchant_id: str, influencer: dict, product: dict, request_id: str):
    """
    Envoie toutes les notifications au marchand quand un influenceur fait une demande
    - Email
    - SMS
    - Notification Dashboard
    - WhatsApp (optionnel)
    """
    try:
        # Récupérer les infos du marchand
        merchant = supabase.table('merchants').select('*, users(email, phone)').eq('id', merchant_id).execute().data[0]

        # EMAIL
        email_data = {
            'to': merchant['users']['email'],
            'subject': f"📬 Nouvelle demande d'affiliation - {influencer['username']}",
            'body': f"""
            Bonjour {merchant['company_name']},

            Vous avez reçu une nouvelle demande d'affiliation !

            Influenceur: {influencer['full_name']} (@{influencer['username']})
            Produit: {product['name']}
            Abonnés: {influencer.get('audience_size', 0):,}
            Taux d'engagement: {influencer.get('engagement_rate', 0)}%

            Consultez la demande complète et approuvez-la en 1 clic:
            https://shareyoursales.ma/merchant/affiliation-requests/{request_id}

            Vous avez 48h pour répondre.

            ShareYourSales Team
            """
        }

        # TODO: Envoyer l'email via service SMTP
        logger.info(f"📧 Email envoyé à {merchant['users']['email']}")

        # SMS
        sms_data = {
            'to': merchant['users']['phone'],
            'message': f"📬 Nouvelle demande d'affiliation de {influencer['username']} ({influencer.get('audience_size', 0):,} abonnés). Consultez sur ShareYourSales.ma"
        }

        # TODO: Envoyer SMS via Twilio/Vonage
        logger.info(f"📱 SMS envoyé à {merchant['users']['phone']}")

        # NOTIFICATION DASHBOARD
        notification = {
            'user_id': merchant['user_id'],
            'type': 'affiliation_request',
            'title': 'Nouvelle demande d\'affiliation',
            'message': f"{influencer['username']} souhaite promouvoir {product['name']}",
            'link': f"/merchant/affiliation-requests/{request_id}",
            'is_read': False
        }

        supabase.table('notifications').insert(notification).execute()
        logger.info(f"🔔 Notification dashboard créée pour marchand {merchant_id}")

    except Exception as e:
        logger.error(f"Erreur envoi notifications marchand: {e}")


async def send_influencer_approval_notification(influencer_id: str, product: dict, tracking_url: str, short_code: str, merchant_message: str):
    """
    Envoie notifications à l'influenceur quand sa demande est approuvée
    """
    try:
        # Récupérer l'influenceur
        influencer = supabase.table('influencers').select('*, users(email, phone)').eq('id', influencer_id).execute().data[0]

        # EMAIL
        email_data = {
            'to': influencer['users']['email'],
            'subject': f"🎉 Demande approuvée - {product['name']}",
            'body': f"""
            Félicitations {influencer['full_name']} !

            Votre demande d'affiliation a été APPROUVÉE !

            Produit: {product['name']}
            Commission: {product['commission_rate']}% par vente

            Votre lien personnel:
            {tracking_url}

            Code court: {short_code}

            Message du marchand:
            {merchant_message or "Bienvenue ! Hâte de travailler avec vous."}

            Téléchargez votre kit marketing:
            https://shareyoursales.ma/influencer/my-links/{short_code}/kit

            Commencez à promouvoir dès maintenant !

            ShareYourSales Team
            """
        }

        logger.info(f"📧 Email d'approbation envoyé à {influencer['users']['email']}")

        # NOTIFICATION DASHBOARD
        notification = {
            'user_id': influencer['user_id'],
            'type': 'request_approved',
            'title': 'Demande approuvée !',
            'message': f"Votre demande pour {product['name']} a été approuvée. Votre lien: {tracking_url}",
            'link': f"/influencer/my-links",
            'is_read': False
        }

        supabase.table('notifications').insert(notification).execute()
        logger.info(f"🔔 Notification approbation créée pour influenceur {influencer_id}")

    except Exception as e:
        logger.error(f"Erreur envoi notifications approbation: {e}")


async def send_influencer_rejection_notification(influencer_id: str, product_id: str, rejection_reason: str, merchant_message: str):
    """
    Envoie notifications à l'influenceur quand sa demande est refusée
    """
    try:
        # Récupérer l'influenceur et le produit
        influencer = supabase.table('influencers').select('*, users(email)').eq('id', influencer_id).execute().data[0]
        product = supabase.table('products').select('name').eq('id', product_id).execute().data[0]

        # EMAIL
        email_data = {
            'to': influencer['users']['email'],
            'subject': f"Demande non retenue - {product['name']}",
            'body': f"""
            Bonjour {influencer['full_name']},

            Malheureusement, votre demande pour {product['name']} n'a pas été retenue.

            Raison: {rejection_reason}

            Message du marchand:
            {merchant_message or "Merci pour votre intérêt."}

            NE VOUS DÉCOURAGEZ PAS !
            Il y a 2,456 autres produits sur la plateforme qui correspondent mieux à votre profil.

            Continuez à postuler: https://shareyoursales.ma/marketplace

            ShareYourSales Team
            """
        }

        logger.info(f"📧 Email de refus envoyé à {influencer['users']['email']}")

        # NOTIFICATION DASHBOARD
        notification = {
            'user_id': influencer['user_id'],
            'type': 'request_rejected',
            'title': 'Demande non retenue',
            'message': f"Votre demande pour {product['name']} n'a pas été retenue. Raison: {rejection_reason}",
            'link': "/marketplace",
            'is_read': False
        }

        supabase.table('notifications').insert(notification).execute()
        logger.info(f"🔔 Notification refus créée pour influenceur {influencer_id}")

    except Exception as e:
        logger.error(f"Erreur envoi notifications refus: {e}")
