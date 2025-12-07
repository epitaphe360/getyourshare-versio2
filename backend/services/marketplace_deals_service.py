"""
Service Marketplace Deals (Groupon-style)
- Flash Sales avec countdown timer
- Deals du jour (rotation 24h)
- Seuil minimum participants
- Réduction massive (50-90%)
- Remboursement automatique si seuil non atteint
- Stock limité (premiers arrivés)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from supabase import Client
import random

import logging
logger = logging.getLogger(__name__)


class MarketplaceDealsService:
    """Service de gestion des deals marketplace (Groupon-style)"""

    def __init__(self, supabase: Client):
        self.supabase = supabase

        # Types de deals
        self.DEAL_TYPES = {
            'flash_sale': 'Flash Sale (1-6h)',
            'deal_of_day': 'Deal du Jour (24h)',
            'group_buy': 'Achat groupé (seuil participants)',
            'limited_stock': 'Stock limité',
            'early_bird': 'Early Bird (premiers X acheteurs)'
        }


    def create_deal(
        self,
        product_id: str,
        merchant_id: str,
        deal_type: str,
        discount_percentage: Decimal,
        duration_hours: int,
        min_participants: Optional[int] = None,
        max_participants: Optional[int] = None,
        stock_limit: Optional[int] = None,
        start_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Créer un nouveau deal

        Args:
            product_id: ID du produit
            merchant_id: ID du merchant
            deal_type: Type de deal (flash_sale, deal_of_day, group_buy, etc.)
            discount_percentage: Réduction (ex: 70 pour -70%)
            duration_hours: Durée en heures
            min_participants: Nombre minimum participants (pour group_buy)
            max_participants: Nombre maximum participants
            stock_limit: Stock disponible
            start_at: Date de début (None = immédiat)

        Returns:
            Deal créé
        """
        try:
            # Validation
            if discount_percentage < 10 or discount_percentage > 90:
                raise ValueError("Discount must be between 10% and 90%")

            if deal_type not in self.DEAL_TYPES:
                raise ValueError(f"Invalid deal type. Must be one of: {list(self.DEAL_TYPES.keys())}")

            # Récupérer le produit
            product = self.supabase.table('products').select('*').eq('id', product_id).single().execute()

            if not product.data:
                raise ValueError("Product not found")

            product_data = product.data
            original_price = Decimal(str(product_data['price']))

            # Calculer le prix deal
            discount_amount = original_price * (discount_percentage / 100)
            deal_price = original_price - discount_amount

            # Dates
            start_time = start_at or datetime.now()
            end_time = start_time + timedelta(hours=duration_hours)

            # Créer le deal
            deal_data = {
                'product_id': product_id,
                'merchant_id': merchant_id,
                'deal_type': deal_type,
                'original_price': float(original_price),
                'discount_percentage': float(discount_percentage),
                'deal_price': float(deal_price),
                'savings': float(discount_amount),
                'start_at': start_time.isoformat(),
                'end_at': end_time.isoformat(),
                'duration_hours': duration_hours,
                'min_participants': min_participants,
                'max_participants': max_participants,
                'stock_limit': stock_limit,
                'current_participants': 0,
                'units_sold': 0,
                'status': 'pending' if start_at and start_at > datetime.now() else 'active',
                'auto_refund_enabled': True if min_participants else False
            }

            result = self.supabase.table('marketplace_deals').insert(deal_data).execute()

            if not result.data:
                raise Exception("Error creating deal")

            deal = result.data[0]

            # Si c'est le deal du jour, désactiver les autres
            if deal_type == 'deal_of_day':
                self._deactivate_other_daily_deals(deal['id'], merchant_id)

            return deal

        except Exception as e:
            logger.error(f"Error creating deal: {e}")
            raise


    def purchase_deal(
        self,
        deal_id: str,
        user_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Acheter un deal

        Args:
            deal_id: ID du deal
            user_id: ID de l'acheteur
            quantity: Quantité

        Returns:
            Purchase record
        """
        try:
            # Récupérer le deal
            deal = self.supabase.table('marketplace_deals').select('*').eq('id', deal_id).single().execute()

            if not deal.data:
                raise ValueError("Deal not found")

            deal_data = deal.data

            # Vérifier que le deal est actif
            if deal_data['status'] != 'active':
                raise ValueError(f"Deal is not active. Status: {deal_data['status']}")

            # Vérifier que le deal n'est pas expiré
            end_at = datetime.fromisoformat(deal_data['end_at'].replace('Z', '+00:00'))
            if datetime.now() > end_at.replace(tzinfo=None):
                # Auto-expirer le deal
                self._expire_deal(deal_id)
                raise ValueError("Deal has expired")

            # Vérifier le stock
            if deal_data['stock_limit']:
                units_sold = deal_data['units_sold'] or 0
                if units_sold + quantity > deal_data['stock_limit']:
                    raise ValueError("Insufficient stock")

            # Vérifier max participants
            if deal_data['max_participants']:
                current = deal_data['current_participants'] or 0
                if current + 1 > deal_data['max_participants']:
                    raise ValueError("Maximum participants reached")

            # Vérifier que l'user n'a pas déjà acheté (limite 1 par personne pour certains deals)
            if deal_data['deal_type'] in ['flash_sale', 'early_bird']:
                existing = self.supabase.table('deal_purchases').select('*').eq('deal_id', deal_id).eq('user_id', user_id).execute()
                if existing.data:
                    raise ValueError("You have already purchased this deal")

            # Créer la purchase
            purchase_data = {
                'deal_id': deal_id,
                'user_id': user_id,
                'product_id': deal_data['product_id'],
                'merchant_id': deal_data['merchant_id'],
                'quantity': quantity,
                'unit_price': deal_data['deal_price'],
                'total_amount': float(Decimal(str(deal_data['deal_price'])) * quantity),
                'original_total': float(Decimal(str(deal_data['original_price'])) * quantity),
                'savings': float(Decimal(str(deal_data['savings'])) * quantity),
                'status': 'pending',  # pending, confirmed, refunded
                'payment_status': 'pending'
            }

            result = self.supabase.table('deal_purchases').insert(purchase_data).execute()

            if not result.data:
                raise Exception("Error creating purchase")

            purchase = result.data[0]

            # Mettre à jour le deal (participants + units sold)
            new_participants = (deal_data['current_participants'] or 0) + 1
            new_units_sold = (deal_data['units_sold'] or 0) + quantity

            self.supabase.table('marketplace_deals').update({
                'current_participants': new_participants,
                'units_sold': new_units_sold
            }).eq('id', deal_id).execute()

            # Vérifier si le seuil minimum est atteint
            if deal_data['min_participants']:
                if new_participants >= deal_data['min_participants']:
                    self._activate_deal_threshold_reached(deal_id)

            return purchase

        except Exception as e:
            logger.error(f"Error purchasing deal: {e}")
            raise


    def get_active_deals(
        self,
        deal_type: Optional[str] = None,
        merchant_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Récupérer les deals actifs

        Args:
            deal_type: Filtrer par type
            merchant_id: Filtrer par merchant
            limit: Nombre maximum de résultats

        Returns:
            Liste des deals actifs
        """
        try:
            query = self.supabase.table('marketplace_deals').select('*, products(name, description, image_url)').eq('status', 'active')

            if deal_type:
                query = query.eq('deal_type', deal_type)

            if merchant_id:
                query = query.eq('merchant_id', merchant_id)

            result = query.order('created_at', desc=True).limit(limit).execute()

            deals = result.data or []

            # Ajouter les infos dynamiques (temps restant, etc.)
            for deal in deals:
                deal['time_remaining'] = self._calculate_time_remaining(deal['end_at'])
                deal['progress_percentage'] = self._calculate_progress(deal)
                deal['is_trending'] = self._is_trending(deal)
                deal['urgency_level'] = self._calculate_urgency(deal)

            return deals

        except Exception as e:
            logger.error(f"Error getting active deals: {e}")
            return []


    def get_deal_of_the_day(self) -> Optional[Dict]:
        """
        Récupérer le deal du jour

        Returns:
            Deal du jour ou None
        """
        try:
            result = self.supabase.table('marketplace_deals').select('*, products(*)').eq('deal_type', 'deal_of_day').eq('status', 'active').order('created_at', desc=True).limit(1).execute()

            if result.data and len(result.data) > 0:
                deal = result.data[0]
                deal['time_remaining'] = self._calculate_time_remaining(deal['end_at'])
                deal['progress_percentage'] = self._calculate_progress(deal)
                return deal

            return None

        except Exception as e:
            logger.error(f"Error getting deal of the day: {e}")
            return None


    def get_deal_progress(self, deal_id: str) -> Dict:
        """
        Récupérer la progression d'un deal (pour group buy)

        Returns:
            Progression + infos
        """
        try:
            deal = self.supabase.table('marketplace_deals').select('*').eq('id', deal_id).single().execute()

            if not deal.data:
                raise ValueError("Deal not found")

            deal_data = deal.data

            current = deal_data['current_participants'] or 0
            min_required = deal_data['min_participants'] or 0
            max_allowed = deal_data['max_participants'] or 999999

            progress_percentage = 0
            if min_required > 0:
                progress_percentage = round((current / min_required) * 100, 2)

            threshold_reached = current >= min_required if min_required > 0 else True

            return {
                'deal_id': deal_id,
                'current_participants': current,
                'min_participants': min_required,
                'max_participants': max_allowed,
                'progress_percentage': min(progress_percentage, 100),
                'threshold_reached': threshold_reached,
                'spots_remaining': max_allowed - current if max_allowed < 999999 else None,
                'time_remaining': self._calculate_time_remaining(deal_data['end_at']),
                'status': deal_data['status']
            }

        except Exception as e:
            logger.error(f"Error getting deal progress: {e}")
            return {}


    def refund_failed_deal(self, deal_id: str) -> Dict:
        """
        Rembourser automatiquement si le seuil n'est pas atteint

        Args:
            deal_id: ID du deal

        Returns:
            Résultat du remboursement
        """
        try:
            # Récupérer le deal
            deal = self.supabase.table('marketplace_deals').select('*').eq('id', deal_id).single().execute()

            if not deal.data:
                raise ValueError("Deal not found")

            deal_data = deal.data

            # Vérifier que le deal est expiré
            end_at = datetime.fromisoformat(deal_data['end_at'].replace('Z', '+00:00'))
            if datetime.now() <= end_at.replace(tzinfo=None):
                raise ValueError("Deal is not expired yet")

            # Vérifier que le seuil n'est pas atteint
            current = deal_data['current_participants'] or 0
            min_required = deal_data['min_participants'] or 0

            if current >= min_required:
                raise ValueError("Deal threshold was reached, no refund needed")

            # Récupérer tous les achats
            purchases = self.supabase.table('deal_purchases').select('*').eq('deal_id', deal_id).eq('status', 'pending').execute()

            refunded_count = 0

            if purchases.data:
                for purchase in purchases.data:
                    # Marquer comme remboursé
                    self.supabase.table('deal_purchases').update({
                        'status': 'refunded',
                        'refunded_at': datetime.now().isoformat(),
                        'refund_reason': 'Deal minimum threshold not reached'
                    }).eq('id', purchase['id']).execute()

                    # TODO: Déclencher le remboursement réel (Stripe, etc.)

                    refunded_count += 1

            # Marquer le deal comme failed
            self.supabase.table('marketplace_deals').update({
                'status': 'failed',
                'failed_at': datetime.now().isoformat(),
                'failure_reason': 'Minimum participants not reached'
            }).eq('id', deal_id).execute()

            return {
                'success': True,
                'deal_id': deal_id,
                'refunded_purchases': refunded_count,
                'message': f'{refunded_count} purchases refunded'
            }

        except Exception as e:
            logger.error(f"Error refunding failed deal: {e}")
            raise


    def auto_rotate_deal_of_day(self) -> Optional[Dict]:
        """
        Rotation automatique du deal du jour (cronjob quotidien)

        Sélectionne un nouveau produit pour le deal du jour
        """
        try:
            # Désactiver l'ancien deal du jour
            self.supabase.table('marketplace_deals').update({
                'status': 'expired'
            }).eq('deal_type', 'deal_of_day').eq('status', 'active').execute()

            # Sélectionner un produit aléatoire avec bon stock
            products = self.supabase.table('products').select('*').eq('status', 'active').gte('stock', 10).execute()

            if not products.data or len(products.data) == 0:
                logger.warning("No products available for deal of the day")
                return None

            # Choisir aléatoirement
            selected_product = random.choice(products.data)

            # Créer le nouveau deal du jour
            discount = random.randint(50, 80)  # 50-80% de réduction

            new_deal = self.create_deal(
                product_id=selected_product['id'],
                merchant_id=selected_product['merchant_id'],
                deal_type='deal_of_day',
                discount_percentage=Decimal(str(discount)),
                duration_hours=24
            )

            return new_deal

        except Exception as e:
            logger.error(f"Error rotating deal of the day: {e}")
            return None


    def check_expired_deals(self) -> int:
        """
        Vérifier et expirer les deals terminés (cronjob)

        Returns:
            Nombre de deals expirés
        """
        try:
            now = datetime.now()

            # Récupérer les deals actifs dont end_at est passé
            result = self.supabase.table('marketplace_deals').select('*').eq('status', 'active').lte('end_at', now.isoformat()).execute()

            expired_count = 0

            if result.data:
                for deal in result.data:
                    self._expire_deal(deal['id'])
                    expired_count += 1

            return expired_count

        except Exception as e:
            logger.error(f"Error checking expired deals: {e}")
            return 0


    def _expire_deal(self, deal_id: str):
        """Expirer un deal"""
        try:
            deal = self.supabase.table('marketplace_deals').select('*').eq('id', deal_id).single().execute()

            if not deal.data:
                return

            deal_data = deal.data

            # Vérifier le seuil minimum pour group buy
            if deal_data['min_participants']:
                current = deal_data['current_participants'] or 0
                if current < deal_data['min_participants']:
                    # Déclencher les remboursements
                    self.refund_failed_deal(deal_id)
                    return

            # Marquer comme expiré (succès)
            self.supabase.table('marketplace_deals').update({
                'status': 'expired',
                'expired_at': datetime.now().isoformat()
            }).eq('id', deal_id).execute()

            # Confirmer tous les achats
            self.supabase.table('deal_purchases').update({
                'status': 'confirmed'
            }).eq('deal_id', deal_id).eq('status', 'pending').execute()

        except Exception as e:
            logger.error(f"Error expiring deal: {e}")


    def _deactivate_other_daily_deals(self, current_deal_id: str, merchant_id: str):
        """Désactiver les autres deals du jour"""
        try:
            self.supabase.table('marketplace_deals').update({
                'status': 'superseded'
            }).eq('deal_type', 'deal_of_day').eq('merchant_id', merchant_id).neq('id', current_deal_id).execute()

        except Exception as e:
            logger.error(f"Error deactivating other daily deals: {e}")


    def _activate_deal_threshold_reached(self, deal_id: str):
        """Activer le deal quand le seuil est atteint"""
        try:
            self.supabase.table('marketplace_deals').update({
                'threshold_reached_at': datetime.now().isoformat()
            }).eq('id', deal_id).execute()

            # TODO: Envoyer notifications à tous les participants

        except Exception as e:
            logger.error(f"Error activating deal threshold: {e}")


    def _calculate_time_remaining(self, end_at: str) -> Dict:
        """Calculer le temps restant"""
        try:
            end_time = datetime.fromisoformat(end_at.replace('Z', '+00:00'))
            now = datetime.now()

            if now >= end_time.replace(tzinfo=None):
                return {
                    'expired': True,
                    'seconds': 0,
                    'display': 'Expired'
                }

            diff = end_time.replace(tzinfo=None) - now

            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            seconds = diff.seconds % 60

            return {
                'expired': False,
                'total_seconds': diff.total_seconds(),
                'days': diff.days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'display': f"{diff.days}d {hours}h {minutes}m" if diff.days > 0 else f"{hours}h {minutes}m {seconds}s"
            }

        except Exception:
            return {'expired': True, 'seconds': 0, 'display': 'Expired'}


    def _calculate_progress(self, deal: Dict) -> float:
        """Calculer la progression (participants ou stock)"""
        try:
            if deal.get('min_participants'):
                current = deal['current_participants'] or 0
                minimum = deal['min_participants']
                return round((current / minimum) * 100, 2) if minimum > 0 else 0

            if deal.get('stock_limit'):
                sold = deal['units_sold'] or 0
                total = deal['stock_limit']
                return round((sold / total) * 100, 2) if total > 0 else 0

            return 0

        except Exception:
            return 0


    def _is_trending(self, deal: Dict) -> bool:
        """Déterminer si un deal est trending"""
        try:
            # Trending si beaucoup de ventes récentes
            units_sold = deal.get('units_sold', 0)
            return units_sold >= 20  # Plus de 20 ventes = trending

        except Exception:
            return False


    def _calculate_urgency(self, deal: Dict) -> str:
        """Calculer le niveau d'urgence"""
        try:
            time_remaining = self._calculate_time_remaining(deal['end_at'])

            if time_remaining['expired']:
                return 'expired'

            total_seconds = time_remaining.get('total_seconds', 0)

            if total_seconds < 3600:  # Moins d'1h
                return 'critical'
            elif total_seconds < 21600:  # Moins de 6h
                return 'high'
            elif total_seconds < 86400:  # Moins de 24h
                return 'medium'
            else:
                return 'low'

        except Exception:
            return 'low'
