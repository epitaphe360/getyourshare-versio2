"""
Routes Team Management
Invitations, Roles, Permissions, Collaboration
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import secrets

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/team", tags=["Team Management"])


# ============================================
# MODELS
# ============================================

class TeamInvite(BaseModel):
    email: EmailStr
    role: str = "editor"  # admin, editor, viewer
    permissions: Optional[List[str]] = []


class RoleUpdate(BaseModel):
    role: str
    permissions: Optional[List[str]] = None


# ============================================
# ROLES & PERMISSIONS
# ============================================

AVAILABLE_ROLES = {
    "admin": {
        "name": "Administrator",
        "description": "Full access to all features",
        "permissions": ["read", "write", "delete", "manage_team", "manage_settings", "view_analytics"]
    },
    "editor": {
        "name": "Editor",
        "description": "Can create and edit content",
        "permissions": ["read", "write", "view_analytics"]
    },
    "viewer": {
        "name": "Viewer",
        "description": "Read-only access",
        "permissions": ["read"]
    },
    "marketing": {
        "name": "Marketing",
        "description": "Marketing and campaigns",
        "permissions": ["read", "write", "manage_campaigns", "view_analytics"]
    }
}


@router.get("/roles")
async def get_team_roles(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des rôles disponibles
    """
    return {
        "success": True,
        "roles": [
            {"id": key, **value}
            for key, value in AVAILABLE_ROLES.items()
        ]
    }


@router.get("/permissions")
async def get_team_permissions(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des permissions disponibles
    """
    return {
        "success": True,
        "permissions": [
            "read",
            "write",
            "delete",
            "manage_team",
            "manage_settings",
            "manage_campaigns",
            "view_analytics",
            "manage_products",
            "manage_orders"
        ]
    }


# ============================================
# TEAM MEMBERS
# ============================================

@router.get("/members")
async def get_team_members(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des membres de l'équipe
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer les membres
        members = supabase.table('team_members').select('*').eq('team_owner_id', user_id).execute()

        # Enrichir avec infos utilisateur
        result = []
        for member in (members.data or []):
            member_user_id = member.get('user_id')

            # Récupérer profile
            try:
                profile = supabase.table('profiles').select('full_name, avatar_url').eq('user_id', member_user_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            try:
                user_info = supabase.table('users').select('email').eq('id', member_user_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            result.append({
                **member,
                'full_name': profile.data.get('full_name') if profile.data else None,
                'avatar_url': profile.data.get('avatar_url') if profile.data else None,
                'email': user_info.data.get('email') if user_info.data else None
            })

        return {
            "success": True,
            "members": result,
            "total": len(result)
        }

    except Exception as e:
        logger.error(f"Error getting team members: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# INVITATIONS
# ============================================

@router.post("/invite")
async def invite_team_member(
    invite: TeamInvite,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Inviter un membre à l'équipe
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier permissions (seul admin ou owner peut inviter)
        if role != "admin" and role != "merchant":
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Vérifier que le rôle existe
        if invite.role not in AVAILABLE_ROLES:
            raise HTTPException(status_code=400, detail="Rôle invalide")

        # Générer un token d'invitation
        invitation_token = secrets.token_urlsafe(32)

        # Créer l'invitation
        invitation_data = {
            'team_owner_id': user_id,
            'email': invite.email,
            'role': invite.role,
            'permissions': invite.permissions or AVAILABLE_ROLES[invite.role]['permissions'],
            'token': invitation_token,
            'status': 'pending',
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
            'created_at': datetime.now().isoformat()
        }

        result = supabase.table('team_invitations').insert(invitation_data).execute()

        # TODO: Envoyer email d'invitation
        invitation_url = f"https://app.getyourshare.com/team/accept?token={invitation_token}"

        return {
            "success": True,
            "message": "Invitation envoyée",
            "invitation": result.data[0] if result.data else invitation_data,
            "invitation_url": invitation_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting team member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invitations")
async def get_team_invitations(
    status: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des invitations envoyées
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        query = supabase.table('team_invitations').select('*').eq('team_owner_id', user_id)

        if status:
            query = query.eq('status', status)

        query = query.order('created_at', desc=True)

        response = query.execute()

        return {
            "success": True,
            "invitations": response.data or [],
            "total": len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting invitations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invitations/{invitation_id}/cancel")
async def cancel_invitation(
    invitation_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Annuler une invitation
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier que l'invitation appartient au user
        invitation = supabase.table('team_invitations').select('team_owner_id').eq('id', invitation_id).single().execute()

        if not invitation.data or invitation.data.get('team_owner_id') != user_id:
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Annuler
        supabase.table('team_invitations').update({'status': 'cancelled'}).eq('id', invitation_id).execute()

        return {
            "success": True,
            "message": "Invitation annulée"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling invitation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invitations/accept")
async def accept_invitation(
    token: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Accepter une invitation
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        email = payload.get("email")

        # Récupérer l'invitation
        invitation = supabase.table('team_invitations').select('*').eq('token', token).single().execute()

        if not invitation.data:
            raise HTTPException(status_code=404, detail="Invitation non trouvée")

        inv_data = invitation.data

        # Vérifier email
        if inv_data.get('email') != email:
            raise HTTPException(status_code=403, detail="Email ne correspond pas")

        # Vérifier expiration
        expires_at = datetime.fromisoformat(inv_data.get('expires_at'))
        if datetime.now() > expires_at:
            raise HTTPException(status_code=400, detail="Invitation expirée")

        # Vérifier statut
        if inv_data.get('status') != 'pending':
            raise HTTPException(status_code=400, detail="Invitation déjà utilisée ou annulée")

        # Ajouter le membre à l'équipe
        member_data = {
            'team_owner_id': inv_data.get('team_owner_id'),
            'user_id': user_id,
            'role': inv_data.get('role'),
            'permissions': inv_data.get('permissions'),
            'joined_at': datetime.now().isoformat()
        }

        supabase.table('team_members').insert(member_data).execute()

        # Marquer l'invitation comme acceptée
        supabase.table('team_invitations').update({'status': 'accepted', 'accepted_at': datetime.now().isoformat()}).eq('id', inv_data.get('id')).execute()

        return {
            "success": True,
            "message": "Invitation acceptée",
            "team_owner_id": inv_data.get('team_owner_id'),
            "role": inv_data.get('role')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MEMBER MANAGEMENT
# ============================================

@router.put("/members/{member_id}/role")
async def update_member_role(
    member_id: str,
    update: RoleUpdate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre à jour le rôle d'un membre
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier que le membre appartient à cette équipe
        member = supabase.table('team_members').select('team_owner_id').eq('id', member_id).single().execute()

        if not member.data or member.data.get('team_owner_id') != user_id:
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Vérifier que le rôle existe
        if update.role not in AVAILABLE_ROLES:
            raise HTTPException(status_code=400, detail="Rôle invalide")

        # Mettre à jour
        update_data = {
            'role': update.role,
            'permissions': update.permissions or AVAILABLE_ROLES[update.role]['permissions'],
            'updated_at': datetime.now().isoformat()
        }

        supabase.table('team_members').update(update_data).eq('id', member_id).execute()

        return {
            "success": True,
            "message": "Rôle mis à jour"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating member role: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/members/{member_id}")
async def remove_team_member(
    member_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Retirer un membre de l'équipe
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Vérifier que le membre appartient à cette équipe
        member = supabase.table('team_members').select('team_owner_id').eq('id', member_id).single().execute()

        if not member.data or member.data.get('team_owner_id') != user_id:
            raise HTTPException(status_code=403, detail="Non autorisé")

        # Supprimer
        supabase.table('team_members').delete().eq('id', member_id).execute()

        return {
            "success": True,
            "message": "Membre retiré de l'équipe"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing team member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ACTIVITY LOG
# ============================================

@router.get("/activity")
async def get_team_activity(
    limit: int = 50,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Journal d'activité de l'équipe
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        # Récupérer les activités des membres de l'équipe
        members = supabase.table('team_members').select('user_id').eq('team_owner_id', user_id).execute()

        member_ids = [m['user_id'] for m in (members.data or [])]
        member_ids.append(user_id)  # Inclure le owner

        # Récupérer les logs
        activity = supabase.table('audit_logs').select('*').in_('user_id', member_ids).order('created_at', desc=True).limit(limit).execute()

        return {
            "success": True,
            "activity": activity.data or [],
            "total": len(activity.data) if activity.data else 0
        }

    except Exception as e:
        logger.error(f"Error getting team activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))
