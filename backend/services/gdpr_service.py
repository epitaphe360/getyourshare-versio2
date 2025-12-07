"""
Service GDPR/RGPD Compliance
- Export données utilisateur (Art. 20 GDPR)
- Suppression compte & données (Right to be forgotten)
- Gestion consentements cookies
- Registre traitements
- Anonymisation données
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import hashlib
from supabase import Client

import logging
logger = logging.getLogger(__name__)


class GDPRService:
    """Service de conformité GDPR/RGPD"""

    def __init__(self, supabase: Client):
        self.supabase = supabase


    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export complet des données utilisateur (GDPR Art. 20)

        Retourne TOUTES les données personnelles dans un format structuré

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Dict avec toutes les données exportées
        """
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "user_id": user_id,
                "format_version": "1.0",
                "data": {}
            }

            # 1. Informations utilisateur
            user = self.supabase.table('users').select('*').eq('id', user_id).single().execute()
            if user.data:
                export_data["data"]["user_account"] = {
                    "email": user.data.get('email'),
                    "role": user.data.get('role'),
                    "subscription_plan": user.data.get('subscription_plan'),
                    "created_at": user.data.get('created_at'),
                    "email_verified": user.data.get('email_verified'),
                    "two_factor_enabled": user.data.get('two_factor_enabled'),
                }

            # 2. Profil utilisateur
            profile = self.supabase.table('profiles').select('*').eq('user_id', user_id).single().execute()
            if profile.data:
                export_data["data"]["profile"] = profile.data

            # 3. Liens d'affiliation
            links = self.supabase.table('affiliate_links').select('*').eq('user_id', user_id).execute()
            if links.data:
                export_data["data"]["affiliate_links"] = links.data

            # 4. Produits (si merchant)
            products = self.supabase.table('products').select('*').eq('merchant_id', user_id).execute()
            if products.data:
                export_data["data"]["products"] = products.data

            # 5. Commandes (comme acheteur)
            orders = self.supabase.table('orders').select('*').eq('user_id', user_id).execute()
            if orders.data:
                export_data["data"]["orders"] = orders.data

            # 6. Conversions (si influenceur)
            conversions = self.supabase.table('conversions').select('*').eq('influencer_id', user_id).execute()
            if conversions.data:
                export_data["data"]["conversions"] = conversions.data

            # 7. Paiements reçus
            payouts = self.supabase.table('payouts').select('*').eq('influencer_id', user_id).execute()
            if payouts.data:
                export_data["data"]["payouts"] = payouts.data

            # 8. Leads (si commercial ou influenceur)
            leads = self.supabase.table('leads').select('*').or_(f'influencer_id.eq.{user_id},commercial_id.eq.{user_id}').execute()
            if leads.data:
                export_data["data"]["leads"] = leads.data

            # 9. Campagnes
            campaigns = self.supabase.table('campaigns').select('*').eq('merchant_id', user_id).execute()
            if campaigns.data:
                export_data["data"]["campaigns"] = campaigns.data

            # 10. Notifications
            notifications = self.supabase.table('notifications').select('*').eq('user_id', user_id).execute()
            if notifications.data:
                export_data["data"]["notifications"] = notifications.data

            # 11. Documents KYC
            kyc_docs = self.supabase.table('kyc_documents').select('*').eq('user_id', user_id).execute()
            if kyc_docs.data:
                # Anonymiser les URLs des documents sensibles
                export_data["data"]["kyc_documents"] = [
                    {**doc, "document_url": "[REDACTED - Contact support for full access]"}
                    for doc in kyc_docs.data
                ]

            # 12. Historique connexions
            login_history = self.supabase.table('login_history').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(100).execute()
            if login_history.data:
                export_data["data"]["login_history"] = login_history.data

            # 13. Consentements cookies/GDPR
            consents = self.supabase.table('user_consents').select('*').eq('user_id', user_id).execute()
            if consents.data:
                export_data["data"]["consents"] = consents.data

            # 14. Audit logs
            audit_logs = self.supabase.table('audit_logs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(200).execute()
            if audit_logs.data:
                export_data["data"]["audit_logs"] = audit_logs.data

            # 15. Factures
            invoices_sent = self.supabase.table('invoices').select('*').eq('merchant_id', user_id).execute()
            invoices_received = self.supabase.table('invoices').select('*').eq('client_id', user_id).execute()

            export_data["data"]["invoices"] = {
                "sent": invoices_sent.data if invoices_sent.data else [],
                "received": invoices_received.data if invoices_received.data else []
            }

            # 16. Statistiques calculées
            export_data["data"]["statistics"] = {
                "total_affiliate_links": len(export_data["data"].get("affiliate_links", [])),
                "total_conversions": len(export_data["data"].get("conversions", [])),
                "total_orders": len(export_data["data"].get("orders", [])),
                "total_leads": len(export_data["data"].get("leads", [])),
                "total_notifications": len(export_data["data"].get("notifications", [])),
            }

            # Enregistrer l'export dans les logs
            self._log_data_export(user_id)

            return export_data

        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            raise


    def delete_user_account(
        self,
        user_id: str,
        deletion_type: str = 'full',  # 'full' ou 'anonymize'
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suppression compte utilisateur (Right to be forgotten - GDPR Art. 17)

        Args:
            user_id: ID utilisateur
            deletion_type:
                - 'full': Suppression complète (défaut)
                - 'anonymize': Anonymisation (garde les données mais anonymisées)
            reason: Raison de la suppression

        Returns:
            Résultat de l'opération
        """
        try:
            # Vérifier que l'utilisateur existe
            user = self.supabase.table('users').select('*').eq('id', user_id).single().execute()
            if not user.data:
                raise ValueError("User not found")

            if deletion_type == 'anonymize':
                return self._anonymize_user(user_id, reason)
            else:
                return self._delete_user_full(user_id, reason)

        except Exception as e:
            logger.error(f"Error deleting user account: {e}")
            raise


    def _delete_user_full(self, user_id: str, reason: Optional[str]) -> Dict[str, Any]:
        """
        Suppression COMPLÈTE du compte

        ATTENTION: Cette action est IRRÉVERSIBLE
        """
        deleted_tables = []

        try:
            # 1. Enregistrer la demande de suppression (pour conformité GDPR)
            deletion_request = {
                "user_id": user_id,
                "deletion_type": "full",
                "reason": reason,
                "requested_at": datetime.now().isoformat(),
                "status": "processing"
            }

            self.supabase.table('gdpr_deletion_requests').insert(deletion_request).execute()

            # 2. Supprimer dans l'ordre (respect des contraintes FK)

            # Notifications
            self.supabase.table('notifications').delete().eq('user_id', user_id).execute()
            deleted_tables.append('notifications')

            # Audit logs
            self.supabase.table('audit_logs').delete().eq('user_id', user_id).execute()
            deleted_tables.append('audit_logs')

            # Login history
            self.supabase.table('login_history').delete().eq('user_id', user_id).execute()
            deleted_tables.append('login_history')

            # User consents
            self.supabase.table('user_consents').delete().eq('user_id', user_id).execute()
            deleted_tables.append('user_consents')

            # Affiliate links
            self.supabase.table('affiliate_links').delete().eq('user_id', user_id).execute()
            deleted_tables.append('affiliate_links')

            # Conversions (mettre influencer_id à NULL plutôt que supprimer - besoin comptable)
            self.supabase.table('conversions').update({'influencer_id': None}).eq('influencer_id', user_id).execute()

            # Leads
            self.supabase.table('leads').delete().or_(f'influencer_id.eq.{user_id},commercial_id.eq.{user_id}').execute()
            deleted_tables.append('leads')

            # Payouts (garder pour comptabilité mais anonymiser)
            self.supabase.table('payouts').update({
                'user_email': '[DELETED]',
                'user_name': '[DELETED]'
            }).eq('influencer_id', user_id).execute()

            # KYC documents
            self.supabase.table('kyc_documents').delete().eq('user_id', user_id).execute()
            deleted_tables.append('kyc_documents')

            # Produits (si merchant) - OPTION: garder les produits mais supprimer le merchant_id
            # Pour cet exemple, on supprime
            self.supabase.table('products').delete().eq('merchant_id', user_id).execute()
            deleted_tables.append('products')

            # Campaigns
            self.supabase.table('campaigns').delete().eq('merchant_id', user_id).execute()
            deleted_tables.append('campaigns')

            # Invoices (garder pour légal mais anonymiser)
            self.supabase.table('invoices').update({
                'metadata': {'anonymized': True, 'deleted_at': datetime.now().isoformat()}
            }).or_(f'merchant_id.eq.{user_id},client_id.eq.{user_id}').execute()

            # Profile
            self.supabase.table('profiles').delete().eq('user_id', user_id).execute()
            deleted_tables.append('profiles')

            # User (EN DERNIER)
            self.supabase.table('users').delete().eq('id', user_id).execute()
            deleted_tables.append('users')

            # Marquer la requête comme complétée
            self.supabase.table('gdpr_deletion_requests').update({
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'deleted_tables': deleted_tables
            }).eq('user_id', user_id).eq('status', 'processing').execute()

            return {
                "success": True,
                "deletion_type": "full",
                "deleted_tables": deleted_tables,
                "message": "Compte utilisateur supprimé définitivement"
            }

        except Exception as e:
            # Marquer comme failed
            self.supabase.table('gdpr_deletion_requests').update({
                'status': 'failed',
                'error': str(e)
            }).eq('user_id', user_id).eq('status', 'processing').execute()

            logger.error(f"Error in full deletion: {e}")
            raise


    def _anonymize_user(self, user_id: str, reason: Optional[str]) -> Dict[str, Any]:
        """
        Anonymisation du compte (alternative à la suppression)

        Garde les données mais remplace toutes les infos personnelles
        par des valeurs anonymisées
        """
        try:
            anonymized_id = f"ANON-{hashlib.sha256(user_id.encode()).hexdigest()[:12]}"
            anonymized_email = f"{anonymized_id}@anonymized.local"

            # Enregistrer la demande
            deletion_request = {
                "user_id": user_id,
                "deletion_type": "anonymize",
                "reason": reason,
                "requested_at": datetime.now().isoformat(),
                "status": "processing"
            }

            self.supabase.table('gdpr_deletion_requests').insert(deletion_request).execute()

            # Anonymiser user
            self.supabase.table('users').update({
                'email': anonymized_email,
                'email_verified': False,
                'password_hash': None,
                'metadata': {'anonymized': True, 'anonymized_at': datetime.now().isoformat()}
            }).eq('id', user_id).execute()

            # Anonymiser profile
            self.supabase.table('profiles').update({
                'first_name': 'Anonymous',
                'last_name': 'User',
                'phone': None,
                'address': None,
                'city': None,
                'postal_code': None,
                'company_name': None
            }).eq('user_id', user_id).execute()

            # Supprimer KYC documents
            self.supabase.table('kyc_documents').delete().eq('user_id', user_id).execute()

            # Marquer comme complété
            self.supabase.table('gdpr_deletion_requests').update({
                'status': 'completed',
                'completed_at': datetime.now().isoformat()
            }).eq('user_id', user_id).eq('status', 'processing').execute()

            return {
                "success": True,
                "deletion_type": "anonymize",
                "message": "Compte utilisateur anonymisé"
            }

        except Exception as e:
            logger.error(f"Error in anonymization: {e}")
            raise


    def update_cookie_consent(
        self,
        user_id: str,
        consent_data: Dict[str, bool]
    ) -> Dict:
        """
        Mettre à jour les consentements cookies (granulaire)

        Args:
            user_id: ID utilisateur
            consent_data: {
                'necessary': True,  # Toujours true
                'analytics': bool,
                'marketing': bool,
                'personalization': bool
            }
        """
        try:
            consent_record = {
                'user_id': user_id,
                'necessary_cookies': True,  # Toujours accepté
                'analytics_cookies': consent_data.get('analytics', False),
                'marketing_cookies': consent_data.get('marketing', False),
                'personalization_cookies': consent_data.get('personalization', False),
                'consent_date': datetime.now().isoformat(),
                'ip_address': consent_data.get('ip_address'),
                'user_agent': consent_data.get('user_agent')
            }

            # Vérifier si un consentement existe déjà
            existing = self.supabase.table('user_consents').select('*').eq('user_id', user_id).eq('consent_type', 'cookies').single().execute()

            if existing.data:
                # Mettre à jour
                result = self.supabase.table('user_consents').update(consent_record).eq('user_id', user_id).eq('consent_type', 'cookies').execute()
            else:
                # Créer
                consent_record['consent_type'] = 'cookies'
                result = self.supabase.table('user_consents').insert(consent_record).execute()

            return {
                "success": True,
                "consent": result.data[0] if result.data else {}
            }

        except Exception as e:
            logger.error(f"Error updating cookie consent: {e}")
            raise


    def get_cookie_consent(self, user_id: str) -> Dict:
        """Récupérer les consentements cookies d'un utilisateur"""
        try:
            result = self.supabase.table('user_consents').select('*').eq('user_id', user_id).eq('consent_type', 'cookies').single().execute()

            if result.data:
                return {
                    "success": True,
                    "consent": {
                        "necessary": result.data.get('necessary_cookies', True),
                        "analytics": result.data.get('analytics_cookies', False),
                        "marketing": result.data.get('marketing_cookies', False),
                        "personalization": result.data.get('personalization_cookies', False),
                        "consent_date": result.data.get('consent_date')
                    }
                }
            else:
                # Aucun consentement = refus (sauf necessary)
                return {
                    "success": True,
                    "consent": {
                        "necessary": True,
                        "analytics": False,
                        "marketing": False,
                        "personalization": False
                    }
                }

        except Exception as e:
            logger.error(f"Error getting cookie consent: {e}")
            return {
                "success": False,
                "consent": {
                    "necessary": True,
                    "analytics": False,
                    "marketing": False,
                    "personalization": False
                }
            }


    def get_data_processing_register(self) -> List[Dict]:
        """
        Registre des traitements de données (GDPR Art. 30)

        Retourne la liste des traitements de données personnelles
        """
        register = [
            {
                "id": "1",
                "name": "Gestion comptes utilisateurs",
                "purpose": "Création et gestion des comptes utilisateurs",
                "legal_basis": "Contrat",
                "data_categories": ["Identité", "Contact", "Connexion"],
                "data_retention": "Durée du contrat + 3 ans",
                "recipients": ["Équipe technique", "Support client"],
                "security_measures": ["Chiffrement", "Accès restreint", "2FA"]
            },
            {
                "id": "2",
                "name": "Traitement paiements",
                "purpose": "Gestion des paiements et commissions",
                "legal_basis": "Contrat",
                "data_categories": ["Identité", "Bancaires", "Transactions"],
                "data_retention": "10 ans (légal comptabilité)",
                "recipients": ["Service comptabilité", "Stripe", "Banque"],
                "security_measures": ["PCI-DSS", "Chiffrement", "Tokenization"]
            },
            {
                "id": "3",
                "name": "Analytics & Statistiques",
                "purpose": "Amélioration des services, statistiques d'usage",
                "legal_basis": "Intérêt légitime / Consentement",
                "data_categories": ["Connexion", "Comportement", "Technique"],
                "data_retention": "25 mois max",
                "recipients": ["Équipe produit", "Google Analytics"],
                "security_measures": ["Anonymisation IP", "Pseudonymisation"]
            },
            {
                "id": "4",
                "name": "Marketing & Communication",
                "purpose": "Envoi de newsletters et offres commerciales",
                "legal_basis": "Consentement",
                "data_categories": ["Identité", "Contact", "Préférences"],
                "data_retention": "3 ans après dernier contact",
                "recipients": ["Service marketing", "Mailchimp"],
                "security_measures": ["Opt-out facile", "Chiffrement"]
            },
            {
                "id": "5",
                "name": "KYC & Vérification identité",
                "purpose": "Vérification identité pour conformité réglementaire",
                "legal_basis": "Obligation légale",
                "data_categories": ["Identité", "Documents officiels"],
                "data_retention": "5 ans après fin de relation",
                "recipients": ["Service conformité"],
                "security_measures": ["Chiffrement fort", "Accès ultra-restreint"]
            }
        ]

        return register


    def _log_data_export(self, user_id: str):
        """Enregistrer l'export de données dans les logs (audit trail)"""
        try:
            log_entry = {
                "user_id": user_id,
                "action": "gdpr_data_export",
                "details": {
                    "export_date": datetime.now().isoformat(),
                    "requester": "user"
                }
            }

            self.supabase.table('audit_logs').insert(log_entry).execute()

        except Exception as e:
            logger.error(f"Error logging data export: {e}")
