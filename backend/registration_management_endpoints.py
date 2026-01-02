"""
Endpoints pour la gestion complète des demandes d'inscription annonceurs
Fonctionnalités: Approbation, Rejet, Actions en masse, Notes, Filtres avancés
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import os
from supabase import create_client, Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

router = APIRouter()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@getyourshare.com")

# Models Pydantic
class RegistrationNote(BaseModel):
    note: str
    
class BulkActionRequest(BaseModel):
    registration_ids: List[int]
    action: str  # 'approve' or 'reject'
    
class SendMessageRequest(BaseModel):
    subject: str
    message: str

class RegistrationDetailResponse(BaseModel):
    id: int
    company_name: str
    email: str
    country: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    notes: Optional[str]
    contact_person: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    business_type: Optional[str]
    estimated_budget: Optional[float]
    
# Fonction utilitaire pour envoyer des emails
async def send_email(to_email: str, subject: str, content: str):
    """Envoie un email via SendGrid"""
    if not SENDGRID_API_KEY:
        print("⚠️ SendGrid API Key non configurée")
        return
    
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✉️ Email envoyé à {to_email}: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email: {str(e)}")

# ========== ENDPOINTS DE GESTION ==========

@router.get("/admin/registration-requests")
async def get_registration_requests(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    search: Optional[str] = Query(None, description="Search in company name, email, country"),
    country: Optional[str] = Query(None, description="Filter by country"),
    limit: int = Query(100, le=500),
    offset: int = Query(0)
):
    """
    Récupère les demandes d'inscription avec filtres avancés
    Admin only
    """
    try:
        query = supabase.table('advertiser_registrations').select('*')
        
        # Filtre par statut
        if status:
            query = query.eq('status', status)
        
        # Filtre par pays
        if country:
            query = query.eq('country', country)
        
        # Recherche textuelle
        if search:
            # Note: Supabase ne supporte pas le LIKE directement, on filtre côté serveur
            query = query.limit(limit).offset(offset)
            response = query.execute()
            registrations = response.data
            
            # Filtrage côté serveur
            search_lower = search.lower()
            registrations = [
                r for r in registrations
                if (r.get('company_name', '').lower().find(search_lower) >= 0 or
                    r.get('email', '').lower().find(search_lower) >= 0 or
                    r.get('country', '').lower().find(search_lower) >= 0)
            ]
        else:
            query = query.limit(limit).offset(offset)
            response = query.execute()
            registrations = response.data
        
        # Statistiques
        all_registrations = supabase.table('advertiser_registrations').select('status').execute().data
        stats = {
            'total': len(all_registrations),
            'pending': len([r for r in all_registrations if r.get('status') == 'pending']),
            'approved': len([r for r in all_registrations if r.get('status') == 'approved']),
            'rejected': len([r for r in all_registrations if r.get('status') == 'rejected'])
        }
        
        return {
            'registrations': registrations,
            'stats': stats,
            'count': len(registrations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

import bcrypt
import secrets
import string

# Fonction utilitaire pour hasher le mot de passe
def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def generate_random_password(length=12):
    """Génère un mot de passe aléatoire sécurisé"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(length))

@router.get("/admin/registration-requests/{registration_id}")
async def get_registration_detail(registration_id: str):
    """
    Récupère les détails complets d'une demande d'inscription
    Admin only
    """
    try:
        response = supabase.table('advertiser_registrations').select('*').eq('id', registration_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/admin/registration-requests/{registration_id}/approve")
async def approve_registration(registration_id: str):
    """
    Approuve une demande d'inscription et envoie un email de confirmation
    Admin only
    """
    try:
        # Récupérer la demande
        response = supabase.table('advertiser_registrations').select('*').eq('id', registration_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        registration = response.data[0]
        
        # Mettre à jour le statut
        update_response = supabase.table('advertiser_registrations').update({
            'status': 'approved',
            'updated_at': datetime.now().isoformat()
        }).eq('id', registration_id).execute()
        
        # Créer le compte utilisateur dans la table users
        generated_password = generate_random_password()
        hashed_password = hash_password(generated_password)
        
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = supabase.table('users').select('id').eq('email', registration['email']).execute()
            
            if not existing_user.data:
                user_data = {
                    'email': registration['email'],
                    'password_hash': hashed_password,
                    'role': 'merchant',
                    'company': registration.get('company_name'),
                    'country': registration.get('country'),
                    'phone': registration.get('phone'),
                    'status': 'active',
                    'is_active': True,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                supabase.table('users').insert(user_data).execute()
                print(f"✅ Utilisateur créé pour {registration['email']}")
            else:
                print(f"⚠️ L'utilisateur {registration['email']} existe déjà")
                # On ne met pas à jour le mot de passe si l'utilisateur existe déjà
                generated_password = "Utilisez votre mot de passe existant"
                
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {str(e)}")
            # On continue quand même pour envoyer l'email
        
        # Envoyer email de confirmation
        email_content = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 30px; border-radius: 10px;">
        <h1 style="color: #10b981;">🎉 Votre demande a été approuvée !</h1>
        <p>Bonjour {registration.get('company_name', '')} !</p>
        <p>Nous avons le plaisir de vous informer que votre demande d'inscription en tant qu'annonceur sur <strong>GetYourShare</strong> a été approuvée.</p>
        <p>Votre compte a été créé avec succès. Voici vos identifiants de connexion :</p>
        <div style="background: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #e5e7eb; margin: 20px 0;">
            <p><strong>Email :</strong> {registration['email']}</p>
            <p><strong>Mot de passe :</strong> {generated_password}</p>
        </div>
        <p>Nous vous recommandons de changer votre mot de passe dès votre première connexion.</p>
        <div style="margin: 30px 0;">
            <a href="https://getyourshare.com/login" style="background: #4f46e5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">
                Accéder à mon espace
            </a>
        </div>
        <p>Si vous avez des questions, n'hésitez pas à nous contacter.</p>
        <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
            Cordialement,<br>
            L'équipe GetYourShare
        </p>
    </div>
</body>
</html>
"""
        
        await send_email(
            registration['email'],
            "✅ Votre demande GetYourShare a été approuvée",
            email_content
        )
        
        return {
            'message': 'Demande approuvée avec succès',
            'registration': update_response.data[0] if update_response.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/admin/registration-requests/{registration_id}/reject")
async def reject_registration(registration_id: str):
    """
    Rejette une demande d'inscription et envoie un email d'information
    Admin only
    """
    try:
        # Récupérer la demande
        response = supabase.table('advertiser_registrations').select('*').eq('id', registration_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        registration = response.data[0]
        
        # Mettre à jour le statut
        update_response = supabase.table('advertiser_registrations').update({
            'status': 'rejected',
            'updated_at': datetime.now().isoformat()
        }).eq('id', registration_id).execute()
        
        # Envoyer email d'information
        email_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #ef4444;">Mise à jour de votre demande</h1>
                <p>Bonjour {registration.get('company_name', '')} !</p>
                <p>Nous vous remercions de l'intérêt que vous portez à <strong>GetYourShare</strong>.</p>
                <p>Après examen de votre demande d'inscription, nous ne pouvons malheureusement pas y donner suite pour le moment.</p>
                <p>Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez plus d'informations, n'hésitez pas à nous contacter.</p>
                <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                    Cordialement,<br>
                    L'équipe GetYourShare
                </p>
            </div>
        </body>
        </html>
        """
        
        await send_email(
            registration['email'],
            "Mise à jour de votre demande GetYourShare",
            email_content
        )
        
        return {
            'message': 'Demande rejetée',
            'registration': update_response.data[0] if update_response.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/admin/registration-requests/bulk-actions")
async def bulk_actions(request: BulkActionRequest):
    """
    Effectue des actions en masse sur plusieurs demandes
    Admin only
    """
    try:
        if not request.registration_ids:
            raise HTTPException(status_code=400, detail="Aucun ID fourni")
        
        if request.action not in ['approve', 'reject']:
            raise HTTPException(status_code=400, detail="Action invalide")
        
        results = {
            'success': [],
            'failed': []
        }
        
        for registration_id in request.registration_ids:
            try:
                if request.action == 'approve':
                    await approve_registration(registration_id)
                    results['success'].append(registration_id)
                elif request.action == 'reject':
                    await reject_registration(registration_id)
                    results['success'].append(registration_id)
            except Exception as e:
                results['failed'].append({
                    'id': registration_id,
                    'error': str(e)
                })
        
        return {
            'message': f'{len(results["success"])} demandes traitées',
            'results': results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/admin/registration-requests/{registration_id}/notes")
async def add_note(registration_id: int, note_data: RegistrationNote):
    """
    Ajoute une note interne à une demande d'inscription
    Admin only
    """
    try:
        # Récupérer la demande actuelle
        response = supabase.table('advertiser_registrations').select('notes').eq('id', registration_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        current_notes = response.data[0].get('notes', '')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_note = f"[{timestamp}] {note_data.note}"
        
        # Ajouter la nouvelle note
        updated_notes = f"{current_notes}\n{new_note}" if current_notes else new_note
        
        # Mettre à jour
        update_response = supabase.table('advertiser_registrations').update({
            'notes': updated_notes,
            'updated_at': datetime.now().isoformat()
        }).eq('id', registration_id).execute()
        
        return {
            'message': 'Note ajoutée',
            'notes': updated_notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/admin/registration-requests/{registration_id}/send-message")
async def send_custom_message(registration_id: int, message_data: SendMessageRequest):
    """
    Envoie un message personnalisé à un demandeur
    Admin only
    """
    try:
        # Récupérer la demande
        response = supabase.table('advertiser_registrations').select('*').eq('id', registration_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        registration = response.data[0]

        # Préparer le message formaté (éviter backslash dans f-string)
        safe_message = message_data.message.replace('\n', '<br>')
        email_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #4f46e5;">{message_data.subject}</h1>
                <p>Bonjour {registration.get('company_name', '')} !</p>
                <div style="margin: 20px 0; padding: 20px; background: white; border-radius: 8px;">
                    {safe_message}
                </div>
                <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                    Cordialement,<br>
                    L'équipe GetYourShare
                </p>
            </div>
        </body>
        </html>
        """
        
        await send_email(
            registration['email'],
            message_data.subject,
            email_content
        )
        
        return {'message': 'Message envoyé avec succès'}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/admin/registration-stats")
async def get_registration_stats():
    """
    Récupère les statistiques détaillées des demandes d'inscription
    Admin only
    """
    try:
        all_registrations = supabase.table('advertiser_registrations').select('*').execute().data
        
        # Statistiques par statut
        by_status = {
            'pending': len([r for r in all_registrations if r.get('status') == 'pending']),
            'approved': len([r for r in all_registrations if r.get('status') == 'approved']),
            'rejected': len([r for r in all_registrations if r.get('status') == 'rejected'])
        }
        
        # Statistiques par pays
        countries = {}
        for reg in all_registrations:
            country = reg.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        # Statistiques temporelles (derniers 30 jours)
        from datetime import timedelta
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        
        recent_registrations = [
            r for r in all_registrations
            if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) > thirty_days_ago
        ]
        
        return {
            'total': len(all_registrations),
            'by_status': by_status,
            'by_country': countries,
            'last_30_days': len(recent_registrations),
            'approval_rate': round((by_status['approved'] / len(all_registrations) * 100) if all_registrations else 0, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/admin/registration-countries")
async def get_registration_countries():
    """
    Récupère la liste des pays avec des demandes
    Pour le filtre pays
    """
    try:
        response = supabase.table('advertiser_registrations').select('country').execute()
        countries = list(set([r.get('country') for r in response.data if r.get('country')]))
        countries.sort()
        return {'countries': countries}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
