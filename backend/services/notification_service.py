"""
Service de notifications pour le système LEADS
Alertes solde bas, dépôt épuisé, arrêt campagne, leads en attente
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from decimal import Decimal
from supabase import Client
from utils.logger import logger


class NotificationService:
    """Service pour gérer les notifications du système LEADS"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    
    def send_low_balance_alert(
        self,
        merchant_id: str,
        deposit: Dict,
        is_critical: bool = False
    ):
        """
        Envoyer alerte solde bas
        
        Args:
            merchant_id: ID du merchant
            deposit: Données du dépôt
            is_critical: Solde critique (< 200 dhs)
        """
        try:
            # Récupérer user_id du merchant
            merchant = self.supabase.table('merchants').select('user_id, company_name').eq('id', merchant_id).single().execute()
            
            if not merchant.data:
                return
            
            user_id = merchant.data['user_id']
            company_name = merchant.data['company_name']
            
            current_balance = deposit['current_balance']
            alert_threshold = deposit['alert_threshold']
            
            # Déterminer le niveau d'urgence
            if is_critical:
                level = 'critical'
                title = '🚨 URGENT: Solde critique!'
                message = f"Votre solde est critique: {current_balance} dhs restants. Rechargez immédiatement pour ne pas interrompre vos campagnes."
            else:
                level = 'warning'
                title = '⚠️ Solde bas'
                message = f"Votre solde est bas: {current_balance} dhs restants (seuil: {alert_threshold} dhs). Pensez à recharger bientôt."
            
            # Créer la notification
            notification_data = {
                'user_id': user_id,
                'type': 'deposit_low_balance',
                'level': level,
                'title': title,
                'message': message,
                'metadata': {
                    'deposit_id': deposit['id'],
                    'current_balance': current_balance,
                    'alert_threshold': alert_threshold,
                    'is_critical': is_critical,
                    'campaign_id': deposit.get('campaign_id')
                },
                'action_url': '/deposits/recharge',
                'is_read': False
            }
            
            self.supabase.table('notifications').insert(notification_data).execute()
            
            # Envoyer email si critique
            if is_critical:
                self._send_email_alert(
                    user_id,
                    title,
                    message,
                    company_name
                )
            
            logger.info(f"✅ Alerte solde envoyée à {company_name}: {current_balance} dhs")
            
        except Exception as e:
            logger.info(f"Erreur send_low_balance_alert: {e}")
    
    
    def send_deposit_depleted_alert(
        self,
        merchant_id: str,
        deposit: Dict,
        campaign_stopped: bool = False
    ):
        """
        Envoyer alerte dépôt épuisé
        
        Args:
            merchant_id: ID du merchant
            deposit: Données du dépôt
            campaign_stopped: Campagne arrêtée automatiquement
        """
        try:
            merchant = self.supabase.table('merchants').select('user_id, company_name').eq('id', merchant_id).single().execute()
            
            if not merchant.data:
                return
            
            user_id = merchant.data['user_id']
            company_name = merchant.data['company_name']
            
            title = '🚫 Dépôt épuisé'
            message = f"Votre dépôt est épuisé. "
            
            if campaign_stopped:
                message += "Vos campagnes ont été automatiquement mises en pause. Rechargez pour les réactiver."
            else:
                message += "Rechargez pour continuer à générer des leads."
            
            notification_data = {
                'user_id': user_id,
                'type': 'deposit_depleted',
                'level': 'critical',
                'title': title,
                'message': message,
                'metadata': {
                    'deposit_id': deposit['id'],
                    'campaign_id': deposit.get('campaign_id'),
                    'campaign_stopped': campaign_stopped
                },
                'action_url': '/deposits/recharge',
                'is_read': False
            }
            
            self.supabase.table('notifications').insert(notification_data).execute()
            
            # Envoyer email
            self._send_email_alert(
                user_id,
                title,
                message,
                company_name
            )
            
            # Notifier influenceurs si campagne arrêtée
            if campaign_stopped and deposit.get('campaign_id'):
                self._notify_influencers_campaign_stopped(
                    deposit['campaign_id'],
                    company_name
                )
            
            logger.info(f"✅ Alerte dépôt épuisé envoyée à {company_name}")
            
        except Exception as e:
            logger.info(f"Erreur send_deposit_depleted_alert: {e}")
    
    
    def send_new_lead_notification(
        self,
        merchant_id: str,
        lead: Dict
    ):
        """
        Notifier merchant d'un nouveau lead
        
        Args:
            merchant_id: ID du merchant
            lead: Données du lead
        """
        try:
            merchant = self.supabase.table('merchants').select('user_id, company_name').eq('id', merchant_id).single().execute()
            
            if not merchant.data:
                return
            
            user_id = merchant.data['user_id']
            
            customer_name = lead.get('customer_name', 'N/A')
            estimated_value = lead.get('estimated_value', 0)
            source = lead.get('source', 'direct')
            
            title = '🎯 Nouveau lead!'
            message = f"Nouveau lead généré: {customer_name} - Valeur estimée: {estimated_value} dhs (source: {source})"
            
            notification_data = {
                'user_id': user_id,
                'type': 'new_lead',
                'level': 'info',
                'title': title,
                'message': message,
                'metadata': {
                    'lead_id': lead['id'],
                    'campaign_id': lead.get('campaign_id'),
                    'estimated_value': estimated_value,
                    'source': source
                },
                'action_url': f"/leads/{lead['id']}",
                'is_read': False
            }
            
            self.supabase.table('notifications').insert(notification_data).execute()
            
            logger.info(f"✅ Notification nouveau lead envoyée")
            
        except Exception as e:
            logger.info(f"Erreur send_new_lead_notification: {e}")
    
    
    def send_lead_validated_notification(
        self,
        influencer_id: str,
        lead: Dict,
        status: str,
        commission: Decimal
    ):
        """
        Notifier influenceur de la validation d'un lead
        
        Args:
            influencer_id: ID de l'influenceur
            lead: Données du lead
            status: validated, rejected, converted
            commission: Montant de la commission
        """
        try:
            influencer = self.supabase.table('influencers').select('user_id').eq('id', influencer_id).single().execute()
            
            if not influencer.data:
                return
            
            user_id = influencer.data['user_id']
            
            if status == 'validated' or status == 'converted':
                title = '✅ Lead validé!'
                message = f"Votre lead a été validé. Commission: {commission} dhs"
                level = 'success'
            elif status == 'rejected':
                title = '❌ Lead rejeté'
                message = f"Votre lead a été rejeté. Raison: {lead.get('rejection_reason', 'Non spécifiée')}"
                level = 'warning'
            else:
                return
            
            notification_data = {
                'user_id': user_id,
                'type': 'lead_validation',
                'level': level,
                'title': title,
                'message': message,
                'metadata': {
                    'lead_id': lead['id'],
                    'status': status,
                    'commission': float(commission),
                    'estimated_value': lead.get('estimated_value')
                },
                'action_url': f"/leads/{lead['id']}",
                'is_read': False
            }
            
            self.supabase.table('notifications').insert(notification_data).execute()
            
            logger.info(f"✅ Notification validation lead envoyée à influenceur")
            
        except Exception as e:
            logger.info(f"Erreur send_lead_validated_notification: {e}")
    
    
    def send_campaign_stopped_notification(
        self,
        merchant_id: str,
        campaign_id: str,
        reason: str = 'deposit_depleted'
    ):
        """
        Notifier arrêt de campagne
        
        Args:
            merchant_id: ID du merchant
            campaign_id: ID de la campagne
            reason: Raison de l'arrêt
        """
        try:
            merchant = self.supabase.table('merchants').select('user_id, company_name').eq('id', merchant_id).single().execute()
            campaign = self.supabase.table('campaigns').select('name').eq('id', campaign_id).single().execute()
            
            if not merchant.data or not campaign.data:
                return
            
            user_id = merchant.data['user_id']
            campaign_name = campaign.data['name']
            
            if reason == 'deposit_depleted':
                title = '⏸️ Campagne mise en pause'
                message = f"La campagne '{campaign_name}' a été automatiquement mise en pause (dépôt épuisé). Rechargez pour la réactiver."
            elif reason == 'poor_quality':
                title = '⏸️ Campagne suspendue'
                message = f"La campagne '{campaign_name}' a été suspendue en raison de la qualité des leads."
            else:
                title = '⏸️ Campagne arrêtée'
                message = f"La campagne '{campaign_name}' a été arrêtée."
            
            notification_data = {
                'user_id': user_id,
                'type': 'campaign_stopped',
                'level': 'critical',
                'title': title,
                'message': message,
                'metadata': {
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_name,
                    'reason': reason
                },
                'action_url': f"/campaigns/{campaign_id}",
                'is_read': False
            }
            
            self.supabase.table('notifications').insert(notification_data).execute()
            
            logger.info(f"✅ Notification arrêt campagne envoyée")
            
        except Exception as e:
            logger.info(f"Erreur send_campaign_stopped_notification: {e}")
    
    
    def send_agreement_notification(
        self,
        influencer_id: str,
        merchant_id: str,
        agreement: Dict,
        notification_type: str = 'new_agreement'
    ):
        """
        Notifier nouveau accord ou modification
        
        Args:
            influencer_id: ID de l'influenceur
            merchant_id: ID du merchant
            agreement: Données de l'accord
            notification_type: new_agreement, agreement_terminated
        """
        try:
            influencer = self.supabase.table('influencers').select('user_id').eq('id', influencer_id).single().execute()
            merchant = self.supabase.table('merchants').select('company_name').eq('id', merchant_id).single().execute()
            
            if not influencer.data or not merchant.data:
                return
            
            user_id = influencer.data['user_id']
            company_name = merchant.data['company_name']
            commission_percentage = agreement.get('commission_percentage', 0)
            
            if notification_type == 'new_agreement':
                title = '🤝 Nouveau partenariat'
                message = f"{company_name} vous propose un partenariat: {commission_percentage}% de commission. Acceptez pour commencer."
                level = 'info'
                action_url = f"/agreements/{agreement['id']}"
            elif notification_type == 'agreement_terminated':
                title = '⚠️ Partenariat terminé'
                message = f"Votre partenariat avec {company_name} a été terminé."
                level = 'warning'
                action_url = '/agreements'
            else:
                return
            
            notification_data = {
                'user_id': user_id,
                'type': notification_type,
                'level': level,
                'title': title,
                'message': message,
                'metadata': {
                    'agreement_id': agreement['id'],
                    'merchant_id': merchant_id,
                    'company_name': company_name,
                    'commission_percentage': commission_percentage
                },
                'action_url': action_url,
                'is_read': False
            }
            
            self.supabase.table('notifications').insert(notification_data).execute()
            
            logger.info(f"✅ Notification accord envoyée à influenceur")
            
        except Exception as e:
            logger.info(f"Erreur send_agreement_notification: {e}")
    
    
    def get_user_notifications(
        self,
        user_id: str,
        is_read: Optional[bool] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Récupérer les notifications d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            is_read: Filtrer par lu/non lu
            limit: Nombre maximum
            
        Returns:
            Liste des notifications
        """
        try:
            query = self.supabase.table('notifications').select('*').eq('user_id', user_id)
            
            if is_read is not None:
                query = query.eq('is_read', is_read)
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.info(f"Erreur get_user_notifications: {e}")
            return []
    
    
    def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ):
        """Marquer une notification comme lue"""
        try:
            self.supabase.table('notifications').update({
                'is_read': True,
                'read_at': datetime.now().isoformat()
            }).eq('id', notification_id).eq('user_id', user_id).execute()
            
        except Exception as e:
            logger.info(f"Erreur mark_as_read: {e}")
    
    
    def mark_all_as_read(self, user_id: str):
        """Marquer toutes les notifications comme lues"""
        try:
            self.supabase.table('notifications').update({
                'is_read': True,
                'read_at': datetime.now().isoformat()
            }).eq('user_id', user_id).eq('is_read', False).execute()
            
        except Exception as e:
            logger.info(f"Erreur mark_all_as_read: {e}")
    
    
    # ============================================
    # MÉTHODES PRIVÉES
    # ============================================
    
    def _notify_influencers_campaign_stopped(
        self,
        campaign_id: str,
        company_name: str
    ):
        """Notifier tous les influenceurs d'une campagne de son arrêt"""
        try:
            # Récupérer tous les influenceurs avec leads sur cette campagne
            leads = self.supabase.table('leads').select('influencer_id').eq('campaign_id', campaign_id).execute()
            
            if not leads.data:
                return
            
            influencer_ids = list(set([l['influencer_id'] for l in leads.data if l.get('influencer_id')]))
            
            for influencer_id in influencer_ids:
                influencer = self.supabase.table('influencers').select('user_id').eq('id', influencer_id).single().execute()
                
                if not influencer.data:
                    continue
                
                user_id = influencer.data['user_id']
                
                notification_data = {
                    'user_id': user_id,
                    'type': 'campaign_stopped_influencer',
                    'level': 'warning',
                    'title': '⏸️ Campagne mise en pause',
                    'message': f"La campagne de {company_name} a été mise en pause (dépôt épuisé). Vous ne pouvez plus générer de leads.",
                    'metadata': {
                        'campaign_id': campaign_id,
                        'company_name': company_name
                    },
                    'is_read': False
                }
                
                self.supabase.table('notifications').insert(notification_data).execute()
            
            logger.info(f"✅ {len(influencer_ids)} influenceurs notifiés de l'arrêt de campagne")
            
        except Exception as e:
            logger.info(f"Erreur _notify_influencers_campaign_stopped: {e}")
    
    
    def _send_email_alert(
        self,
        user_id: str,
        subject: str,
        message: str,
        company_name: str
    ):
        """Envoyer email d'alerte (à implémenter avec service email)"""
        # TODO: Intégrer avec service d'envoi d'emails (SendGrid, Mailgun, etc.)
        logger.info(f"📧 Email envoyé à {company_name}: {subject}")
