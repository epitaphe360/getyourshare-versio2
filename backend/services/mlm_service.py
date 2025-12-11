"""
Service MLM (Multi-Level Marketing) Complet
- Arbre généalogique multi-niveaux (10 niveaux max)
- Commissions en cascade (niveau 1: 10%, niveau 2: 5%, etc.)
- Rangs & qualifications (Bronze → Diamond)
- Bonus sur volumes d'équipe
- Visualisation arbre MLM
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from supabase import Client

import logging
logger = logging.getLogger(__name__)


class MLMService:
    """Service de Multi-Level Marketing"""

    def __init__(self, supabase: Client):
        self.supabase = supabase

        # Configuration MLM (peut être override par DB)
        self.MAX_LEVELS = 10
        self.COMMISSION_RATES = {
            1: Decimal('10.00'),  # 10% niveau 1 (direct)
            2: Decimal('5.00'),   # 5% niveau 2
            3: Decimal('2.50'),   # 2.5% niveau 3
            4: Decimal('1.00'),   # 1% niveau 4
            5: Decimal('0.50'),   # 0.5% niveau 5
            6: Decimal('0.25'),   # 0.25% niveau 6
            7: Decimal('0.10'),   # 0.10% niveau 7
            8: Decimal('0.05'),   # 0.05% niveau 8
            9: Decimal('0.02'),   # 0.02% niveau 9
            10: Decimal('0.01'),  # 0.01% niveau 10
        }

        # Rangs MLM
        self.RANKS = {
            'bronze': {
                'name': 'Bronze',
                'min_personal_sales': 0,
                'min_team_sales': 0,
                'min_direct_recruits': 0,
                'monthly_bonus': 0,
                'benefits': []
            },
            'silver': {
                'name': 'Silver',
                'min_personal_sales': 10000,  # 10k MAD/mois
                'min_team_sales': 50000,
                'min_direct_recruits': 3,
                'monthly_bonus': 500,
                'benefits': ['Badge Silver', 'Support Priority']
            },
            'gold': {
                'name': 'Gold',
                'min_personal_sales': 25000,
                'min_team_sales': 150000,
                'min_direct_recruits': 5,
                'monthly_bonus': 1500,
                'benefits': ['Badge Gold', 'Support VIP', 'Formation exclusive']
            },
            'platinum': {
                'name': 'Platinum',
                'min_personal_sales': 50000,
                'min_team_sales': 500000,
                'min_direct_recruits': 10,
                'monthly_bonus': 5000,
                'benefits': ['Badge Platinum', 'Support VIP+', 'Événements privés', 'Bonus mensuel']
            },
            'diamond': {
                'name': 'Diamond',
                'min_personal_sales': 100000,
                'min_team_sales': 2000000,
                'min_direct_recruits': 20,
                'monthly_bonus': 20000,
                'benefits': ['Badge Diamond', 'Véhicule entreprise', 'Voyages incentive', 'Conférences internationales']
            }
        }


    def register_referral(
        self,
        referrer_id: str,
        referred_id: str,
        referral_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enregistrer un parrainage (nouveau filleul)

        Args:
            referrer_id: ID du parrain
            referred_id: ID du filleul
            referral_code: Code de parrainage utilisé

        Returns:
            Relationship créée
        """
        try:
            # Vérifier que les users existent
            referrer = self.supabase.table('users').select('id').eq('id', referrer_id).single().execute()
            referred = self.supabase.table('users').select('id').eq('id', referred_id).single().execute()

            if not referrer.data or not referred.data:
                raise ValueError("Referrer or referred user not found")

            # Vérifier qu'il n'y a pas de cycle (A parraine B qui parraine A)
            if self._would_create_cycle(referrer_id, referred_id):
                raise ValueError("Circular referral detected")

            # Déterminer le niveau
            level = self._calculate_referral_level(referrer_id, referred_id)

            # Créer la relation
            relationship = {
                'referrer_id': referrer_id,
                'referred_id': referred_id,
                'referral_code': referral_code,
                'level': level,
                'status': 'active'
            }

            result = self.supabase.table('mlm_relationships').insert(relationship).execute()

            if not result.data:
                raise Exception("Error creating MLM relationship")

            # Propager les relations pour tous les niveaux supérieurs
            self._propagate_relationships(referrer_id, referred_id, level)

            return result.data[0]

        except Exception as e:
            logger.error(f"Error registering referral: {e}")
            raise


    def calculate_mlm_commission(
        self,
        sale_id: str,
        sale_amount: Decimal,
        seller_id: str
    ) -> List[Dict[str, Any]]:
        """
        Calculer les commissions MLM pour une vente

        Remonte l'arbre MLM et calcule la commission de chaque niveau

        Args:
            sale_id: ID de la vente
            sale_amount: Montant de la vente
            seller_id: ID du vendeur

        Returns:
            Liste des commissions par niveau
        """
        try:
            commissions = []

            # Récupérer l'arbre MLM (tous les parrains du vendeur)
            upline = self._get_upline(seller_id, max_levels=self.MAX_LEVELS)

            for level_data in upline:
                level = level_data['level']
                referrer_id = level_data['referrer_id']

                # Taux de commission pour ce niveau
                commission_rate = self.COMMISSION_RATES.get(level, Decimal('0'))

                if commission_rate <= 0:
                    continue

                # Calculer la commission
                commission_amount = (sale_amount * commission_rate / 100).quantize(Decimal('0.01'))

                # Vérifier que le referrer est éligible (actif, en règle)
                if not self._is_eligible_for_commission(referrer_id):
                    continue

                # Créer l'enregistrement de commission
                commission_record = {
                    'sale_id': sale_id,
                    'referrer_id': referrer_id,
                    'referred_id': seller_id,
                    'level': level,
                    'commission_rate': float(commission_rate),
                    'commission_amount': float(commission_amount),
                    'sale_amount': float(sale_amount),
                    'status': 'pending'
                }

                result = self.supabase.table('mlm_commissions').insert(commission_record).execute()

                if result.data:
                    commissions.append(result.data[0])

            return commissions

        except Exception as e:
            logger.error(f"Error calculating MLM commission: {e}")
            raise


    def get_mlm_tree(
        self,
        user_id: str,
        max_levels: int = 3,
        include_stats: bool = True
    ) -> Dict[str, Any]:
        """
        Récupérer l'arbre MLM d'un utilisateur (sa downline)

        Args:
            user_id: ID de l'utilisateur
            max_levels: Nombre de niveaux à récupérer
            include_stats: Inclure les statistiques de performance

        Returns:
            Arbre hiérarchique avec enfants récursifs
        """
        try:
            tree = self._build_tree_recursive(user_id, 1, max_levels, include_stats)
            return tree

        except Exception as e:
            logger.error(f"Error getting MLM tree: {e}")
            raise


    def _build_tree_recursive(
        self,
        user_id: str,
        current_level: int,
        max_levels: int,
        include_stats: bool
    ) -> Dict:
        """Construire l'arbre récursivement"""
        try:
            # Informations utilisateur
            user = self.supabase.table('users').select('id, email, role, created_at').eq('id', user_id).single().execute()

            if not user.data:
                return {}

            user_data = user.data

            # Profile
            profile = self.supabase.table('profiles').select('first_name, last_name, phone').eq('user_id', user_id).single().execute()

            node = {
                'user_id': user_id,
                'email': user_data.get('email'),
                'name': f"{profile.data.get('first_name', '')} {profile.data.get('last_name', '')}".strip() if profile.data else '',
                'role': user_data.get('role'),
                'level': current_level,
                'children': []
            }

            # Stats si demandé
            if include_stats:
                stats = self._get_user_mlm_stats(user_id)
                node['stats'] = stats

            # Si on n'a pas atteint le max, récupérer les enfants
            if current_level < max_levels:
                direct_referrals = self.supabase.table('mlm_relationships').select('referred_id').eq('referrer_id', user_id).eq('level', 1).execute()

                if direct_referrals.data:
                    for referral in direct_referrals.data:
                        child_node = self._build_tree_recursive(
                            referral['referred_id'],
                            current_level + 1,
                            max_levels,
                            include_stats
                        )
                        if child_node:
                            node['children'].append(child_node)

            return node

        except Exception as e:
            logger.error(f"Error building tree recursive: {e}")
            return {}


    def _get_upline(self, user_id: str, max_levels: int = 10) -> List[Dict]:
        """
        Récupérer la upline (tous les parrains) d'un utilisateur

        Returns:
            Liste triée par niveau [{'level': 1, 'referrer_id': '...'}]
        """
        try:
            upline = []

            # Récupérer toutes les relations MLM de cet user (comme referred)
            relationships = self.supabase.table('mlm_relationships').select('*').eq('referred_id', user_id).order('level').execute()

            if relationships.data:
                for rel in relationships.data:
                    if rel['level'] <= max_levels:
                        upline.append({
                            'level': rel['level'],
                            'referrer_id': rel['referrer_id'],
                            'relationship_id': rel['id']
                        })

            return upline

        except Exception as e:
            logger.error(f"Error getting upline: {e}")
            return []


    def _calculate_referral_level(self, referrer_id: str, new_referred_id: str) -> int:
        """
        Calculer le niveau de parrainage

        Si A parraine B directement → niveau 1
        Si A parraine B qui parraine C → C est niveau 2 pour A
        """
        # Pour l'instant, on retourne 1 (direct)
        # La propagation se fera dans _propagate_relationships
        return 1


    def _propagate_relationships(self, referrer_id: str, new_referred_id: str, base_level: int):
        """
        Propager les relations MLM à tous les niveaux supérieurs

        Si A parraine B (niveau 1) et B parraine C:
        - B → C est niveau 1
        - A → C est niveau 2 (indirect)
        """
        try:
            # Récupérer la upline du referrer
            upline = self._get_upline(referrer_id, max_levels=self.MAX_LEVELS - 1)

            for ancestor in upline:
                new_level = ancestor['level'] + base_level

                if new_level > self.MAX_LEVELS:
                    continue

                # Créer la relation indirecte
                indirect_relationship = {
                    'referrer_id': ancestor['referrer_id'],
                    'referred_id': new_referred_id,
                    'level': new_level,
                    'status': 'active',
                    'is_direct': False
                }

                # Insérer (ignore si existe déjà)
                try:
                    self.supabase.table('mlm_relationships').insert(indirect_relationship).execute()
                except Exception:
                    pass  # Relation existe déjà

        except Exception as e:
            logger.error(f"Error propagating relationships: {e}")


    def _would_create_cycle(self, referrer_id: str, referred_id: str) -> bool:
        """
        Vérifier si créer cette relation créerait un cycle

        Exemple cycle: A parraine B, B parraine C, C veut parrainer A
        """
        try:
            # Récupérer la upline du referred
            upline = self._get_upline(referred_id)

            # Si le referrer est dans la upline du referred = cycle
            for ancestor in upline:
                if ancestor['referrer_id'] == referrer_id:
                    return True

            return False

        except Exception:
            return False


    def _is_eligible_for_commission(self, user_id: str) -> bool:
        """Vérifier si un user est éligible pour recevoir des commissions MLM"""
        try:
            user = self.supabase.table('users').select('*').eq('id', user_id).single().execute()

            if not user.data:
                return False

            # Vérifier que l'utilisateur est actif
            if user.data.get('status') != 'active':
                return False

            # Vérifier qu'il n'est pas suspendu
            if user.data.get('suspended'):
                return False

            # TODO: Ajouter d'autres critères (paiement à jour, etc.)

            return True

        except Exception:
            return False


    def _get_user_mlm_stats(self, user_id: str) -> Dict:
        """Statistiques MLM d'un utilisateur"""
        try:
            # Direct recruits
            direct_recruits = self.supabase.table('mlm_relationships').select('*', count='exact').eq('referrer_id', user_id).eq('level', 1).execute()

            # Total downline (tous niveaux)
            total_downline = self.supabase.table('mlm_relationships').select('*', count='exact').eq('referrer_id', user_id).execute()

            # Commissions gagnées
            commissions = self.supabase.table('mlm_commissions').select('commission_amount').eq('referrer_id', user_id).execute()

            total_commissions = sum(Decimal(str(c.get('commission_amount', 0))) for c in (commissions.data or []))

            return {
                'direct_recruits': direct_recruits.count if hasattr(direct_recruits, 'count') else len(direct_recruits.data or []),
                'total_downline': total_downline.count if hasattr(total_downline, 'count') else len(total_downline.data or []),
                'total_commissions': float(total_commissions),
                'currency': 'MAD'
            }

        except Exception as e:
            logger.error(f"Error getting user MLM stats: {e}")
            return {}


    def calculate_rank(self, user_id: str, period: str = 'current_month') -> Dict:
        """
        Calculer le rang MLM d'un utilisateur

        Args:
            user_id: ID utilisateur
            period: Période de calcul (current_month, last_month, etc.)

        Returns:
            Rang actuel + prochain rang + progression
        """
        try:
            # Récupérer les ventes personnelles
            personal_sales = self._get_personal_sales(user_id, period)

            # Récupérer les ventes d'équipe (downline)
            team_sales = self._get_team_sales(user_id, period)

            # Nombre de recrues directes
            direct_recruits = self.supabase.table('mlm_relationships').select('*', count='exact').eq('referrer_id', user_id).eq('level', 1).execute()
            direct_count = direct_recruits.count if hasattr(direct_recruits, 'count') else len(direct_recruits.data or [])

            # Déterminer le rang
            current_rank = 'bronze'

            for rank_id in ['diamond', 'platinum', 'gold', 'silver', 'bronze']:
                rank_criteria = self.RANKS[rank_id]

                if (personal_sales >= rank_criteria['min_personal_sales'] and
                    team_sales >= rank_criteria['min_team_sales'] and
                    direct_count >= rank_criteria['min_direct_recruits']):
                    current_rank = rank_id
                    break

            # Prochain rang
            rank_order = ['bronze', 'silver', 'gold', 'platinum', 'diamond']
            current_index = rank_order.index(current_rank)
            next_rank = rank_order[current_index + 1] if current_index < len(rank_order) - 1 else None

            result = {
                'user_id': user_id,
                'current_rank': current_rank,
                'current_rank_info': self.RANKS[current_rank],
                'personal_sales': float(personal_sales),
                'team_sales': float(team_sales),
                'direct_recruits': direct_count,
                'monthly_bonus': self.RANKS[current_rank]['monthly_bonus'],
                'benefits': self.RANKS[current_rank]['benefits']
            }

            if next_rank:
                next_rank_criteria = self.RANKS[next_rank]
                result['next_rank'] = next_rank
                result['next_rank_requirements'] = {
                    'personal_sales': next_rank_criteria['min_personal_sales'],
                    'team_sales': next_rank_criteria['min_team_sales'],
                    'direct_recruits': next_rank_criteria['min_direct_recruits']
                }
                result['progress'] = {
                    'personal_sales': round(personal_sales / next_rank_criteria['min_personal_sales'] * 100, 2) if next_rank_criteria['min_personal_sales'] > 0 else 100,
                    'team_sales': round(team_sales / next_rank_criteria['min_team_sales'] * 100, 2) if next_rank_criteria['min_team_sales'] > 0 else 100,
                    'direct_recruits': round(direct_count / next_rank_criteria['min_direct_recruits'] * 100, 2) if next_rank_criteria['min_direct_recruits'] > 0 else 100
                }

            return result

        except Exception as e:
            logger.error(f"Error calculating rank: {e}")
            raise


    def _get_personal_sales(self, user_id: str, period: str) -> Decimal:
        """Récupérer les ventes personnelles"""
        try:
            # Récupérer les conversions/ventes de l'utilisateur
            conversions = self.supabase.table('conversions').select('sale_amount').eq('influencer_id', user_id).execute()

            total = sum(Decimal(str(c.get('sale_amount', 0))) for c in (conversions.data or []))
            return total

        except Exception:
            return Decimal('0')


    def _get_team_sales(self, user_id: str, period: str) -> Decimal:
        """Récupérer les ventes de toute l'équipe (downline)"""
        try:
            # Récupérer tous les membres de la downline
            downline = self.supabase.table('mlm_relationships').select('referred_id').eq('referrer_id', user_id).execute()

            if not downline.data:
                return Decimal('0')

            team_member_ids = [d['referred_id'] for d in downline.data]

            # Récupérer les ventes de toute l'équipe
            conversions = self.supabase.table('conversions').select('sale_amount').in_('influencer_id', team_member_ids).execute()

            total = sum(Decimal(str(c.get('sale_amount', 0))) for c in (conversions.data or []))
            return total

        except Exception:
            return Decimal('0')


    def get_mlm_dashboard_stats(self, user_id: str) -> Dict:
        """Dashboard complet MLM pour un utilisateur"""
        try:
            # Stats de base
            base_stats = self._get_user_mlm_stats(user_id)

            # Rang
            rank_info = self.calculate_rank(user_id)

            # Top performers dans la downline
            top_performers = self._get_top_performers_downline(user_id, limit=5)

            # Commissions par niveau
            commissions_by_level = self._get_commissions_by_level(user_id)

            return {
                **base_stats,
                'rank': rank_info,
                'top_performers': top_performers,
                'commissions_by_level': commissions_by_level
            }

        except Exception as e:
            logger.error(f"Error getting MLM dashboard stats: {e}")
            return {}


    def _get_top_performers_downline(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Top performers dans la downline"""
        try:
            # Récupérer la downline
            downline = self.supabase.table('mlm_relationships').select('referred_id, level').eq('referrer_id', user_id).execute()

            if not downline.data:
                return []

            # Pour chaque membre, calculer ses ventes
            performers = []
            for member in downline.data:
                member_id = member['referred_id']
                sales = self._get_personal_sales(member_id, 'current_month')

                try:
                    user_info = self.supabase.table('users').select('email').eq('id', member_id).single().execute()
                except Exception:
                    pass  # .single() might return no results

                performers.append({
                    'user_id': member_id,
                    'email': user_info.data.get('email') if user_info.data else '',
                    'level': member['level'],
                    'sales': float(sales)
                })

            # Trier par ventes décroissantes
            performers.sort(key=lambda x: x['sales'], reverse=True)

            return performers[:limit]

        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return []


    def _get_commissions_by_level(self, user_id: str) -> List[Dict]:
        """Commissions reçues par niveau MLM"""
        try:
            commissions = self.supabase.table('mlm_commissions').select('*').eq('referrer_id', user_id).execute()

            if not commissions.data:
                return []

            # Grouper par niveau
            by_level = {}
            for comm in commissions.data:
                level = comm.get('level', 1)
                if level not in by_level:
                    by_level[level] = {
                        'level': level,
                        'count': 0,
                        'total_amount': Decimal('0')
                    }

                by_level[level]['count'] += 1
                by_level[level]['total_amount'] += Decimal(str(comm.get('commission_amount', 0)))

            # Convertir en liste
            result = []
            for level in sorted(by_level.keys()):
                result.append({
                    'level': level,
                    'count': by_level[level]['count'],
                    'total_amount': float(by_level[level]['total_amount']),
                    'commission_rate': float(self.COMMISSION_RATES.get(level, 0))
                })

            return result

        except Exception as e:
            logger.error(f"Error getting commissions by level: {e}")
            return []
