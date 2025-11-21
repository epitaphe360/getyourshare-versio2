"""
Influencer Matching Service - Tinder for Business
Match automatique Marchand ↔ Influenceur avec IA
- Algorithme de scoring compatibilité
- Recommandations personnalisées
- Swipe interface backend
- Analytics matching
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import random

from utils.logger import logger


class InfluencerMatchingService:
    """Service de matching intelligent marchand-influenceur"""

    def __init__(self):
        self.db = None  # supabase client

    # ========================================
    # SCORING & MATCHING ALGORITHM
    # ========================================

    async def find_matches(
        self,
        merchant_id: str,
        campaign_details: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Trouver les meilleurs influenceurs pour une campagne marchand

        Args:
            merchant_id: ID du marchand
            campaign_details: {
                'product_category': str,
                'target_audience': {...},
                'budget': float,
                'campaign_goals': ['awareness', 'sales', 'engagement'],
                'duration_days': int
            }
            limit: Nombre de résultats

        Returns:
            Liste d'influenceurs avec score de match (0-100)
        """
        # Récupérer profil marchand
        merchant = await self._get_merchant_profile(merchant_id)

        # Récupérer tous les influenceurs actifs
        influencers = await self._get_active_influencers()

        # Calculer score de match pour chaque influenceur
        scored_matches = []

        for influencer in influencers:
            match_score = await self._calculate_match_score(
                merchant,
                influencer,
                campaign_details
            )

            if match_score['total'] >= 50:  # Seuil minimum
                scored_matches.append({
                    'influencer': influencer,
                    'match_score': match_score['total'],
                    'score_breakdown': match_score['breakdown'],
                    'estimated_reach': self._estimate_reach(influencer, campaign_details),
                    'estimated_engagement': self._estimate_engagement(influencer),
                    'estimated_conversions': self._estimate_conversions(influencer, campaign_details),
                    'pricing': self._calculate_pricing(influencer, campaign_details),
                    'match_reasons': self._generate_match_reasons(match_score['breakdown'])
                })

        # Trier par score décroissant
        scored_matches.sort(key=lambda x: x['match_score'], reverse=True)

        logger.info(f"✅ Trouvé {len(scored_matches)} matches pour marchand {merchant_id}")

        return scored_matches[:limit]

    async def _calculate_match_score(
        self,
        merchant: Dict[str, Any],
        influencer: Dict[str, Any],
        campaign: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculer score de compatibilité (0-100)

        Facteurs:
        - Audience alignment (30%)
        - Niche/Category match (25%)
        - Budget fit (15%)
        - Performance history (20%)
        - Engagement rate (10%)
        """
        breakdown = {}
        total_score = 0

        # 1. AUDIENCE ALIGNMENT (30 points max)
        audience_score = self._score_audience_alignment(
            campaign.get('target_audience', {}),
            influencer.get('audience_demographics', {})
        )
        breakdown['audience_alignment'] = audience_score
        total_score += audience_score * 0.30

        # 2. NICHE/CATEGORY MATCH (25 points max)
        niche_score = self._score_niche_match(
            campaign.get('product_category'),
            influencer.get('niches', []),
            influencer.get('content_categories', [])
        )
        breakdown['niche_match'] = niche_score
        total_score += niche_score * 0.25

        # 3. BUDGET FIT (15 points max)
        budget_score = self._score_budget_fit(
            campaign.get('budget', 0),
            influencer.get('average_campaign_price', 0),
            influencer.get('price_range', {})
        )
        breakdown['budget_fit'] = budget_score
        total_score += budget_score * 0.15

        # 4. PERFORMANCE HISTORY (20 points max)
        performance_score = self._score_performance_history(
            influencer.get('past_campaigns', []),
            campaign.get('campaign_goals', [])
        )
        breakdown['performance_history'] = performance_score
        total_score += performance_score * 0.20

        # 5. ENGAGEMENT RATE (10 points max)
        engagement_score = self._score_engagement_rate(
            influencer.get('engagement_rate', 0)
        )
        breakdown['engagement_rate'] = engagement_score
        total_score += engagement_score * 0.10

        return {
            'total': int(total_score),
            'breakdown': breakdown
        }

    def _score_audience_alignment(
        self,
        target_audience: Dict[str, Any],
        influencer_audience: Dict[str, Any]
    ) -> int:
        """
        Score l'alignement d'audience (0-100)

        Compare:
        - Age range
        - Gender
        - Location
        - Interests
        """
        score = 0

        # Age range overlap
        if target_audience.get('age_range') and influencer_audience.get('age_distribution'):
            target_ages = set(target_audience['age_range'])
            influencer_ages = set(influencer_audience['age_distribution'].keys())
            overlap = len(target_ages & influencer_ages) / len(target_ages) if target_ages else 0
            score += overlap * 30

        # Gender match
        if target_audience.get('gender') and influencer_audience.get('gender_split'):
            target_gender = target_audience['gender']
            influencer_gender_pct = influencer_audience['gender_split'].get(target_gender, 0)
            score += (influencer_gender_pct / 100) * 25

        # Location match
        if target_audience.get('locations') and influencer_audience.get('top_locations'):
            target_locs = set(target_audience['locations'])
            influencer_locs = set(influencer_audience['top_locations'])
            overlap = len(target_locs & influencer_locs) / len(target_locs) if target_locs else 0
            score += overlap * 25

        # Interests overlap
        if target_audience.get('interests') and influencer_audience.get('interests'):
            target_interests = set(target_audience['interests'])
            influencer_interests = set(influencer_audience['interests'])
            overlap = len(target_interests & influencer_interests) / len(target_interests) if target_interests else 0
            score += overlap * 20

        return int(min(score, 100))

    def _score_niche_match(
        self,
        product_category: str,
        influencer_niches: List[str],
        content_categories: List[str]
    ) -> int:
        """Score la correspondance de niche (0-100)"""
        if not product_category:
            return 50  # Neutre

        # Exact match
        if product_category.lower() in [n.lower() for n in influencer_niches]:
            return 100

        # Partial match in content categories
        if product_category.lower() in [c.lower() for c in content_categories]:
            return 80

        # Related categories (à définir avec une matrice de similarité)
        # Pour simplifier, retourner score moyen
        return 60

    def _score_budget_fit(
        self,
        campaign_budget: float,
        influencer_avg_price: float,
        price_range: Dict[str, float]
    ) -> int:
        """Score l'adéquation budget (0-100)"""
        if not campaign_budget or not influencer_avg_price:
            return 50

        # Budget dans la fourchette de prix
        min_price = price_range.get('min', influencer_avg_price * 0.7)
        max_price = price_range.get('max', influencer_avg_price * 1.3)

        if min_price <= campaign_budget <= max_price:
            return 100
        elif campaign_budget < min_price:
            # Budget insuffisant
            ratio = campaign_budget / min_price
            return int(ratio * 50)  # Max 50 si budget trop bas
        else:
            # Budget supérieur (bon pour l'influenceur)
            return 90

    def _score_performance_history(
        self,
        past_campaigns: List[Dict[str, Any]],
        campaign_goals: List[str]
    ) -> int:
        """Score l'historique de performance (0-100)"""
        if not past_campaigns:
            return 60  # Nouveau = score neutre

        # Analyser les campagnes passées
        total_roi = 0
        relevant_campaigns = 0

        for campaign in past_campaigns:
            # Vérifier si type de campagne correspond aux goals
            if any(goal in campaign.get('type', '') for goal in campaign_goals):
                relevant_campaigns += 1
                total_roi += campaign.get('roi_percentage', 100)

        if relevant_campaigns == 0:
            return 60

        avg_roi = total_roi / relevant_campaigns

        # Convertir ROI en score
        # ROI 300%+ = 100 points
        # ROI 200% = 80 points
        # ROI 100% = 60 points
        # ROI 0% = 40 points
        if avg_roi >= 300:
            return 100
        elif avg_roi >= 200:
            return 80
        elif avg_roi >= 100:
            return 60
        else:
            return max(40, int(avg_roi / 3))

    def _score_engagement_rate(self, engagement_rate: float) -> int:
        """Score le taux d'engagement (0-100)"""
        # Taux d'engagement excellent: >8%
        # Bon: 5-8%
        # Moyen: 2-5%
        # Faible: <2%

        if engagement_rate >= 8:
            return 100
        elif engagement_rate >= 5:
            return 80
        elif engagement_rate >= 2:
            return 60
        elif engagement_rate >= 1:
            return 40
        else:
            return 20

    # ========================================
    # ESTIMATIONS
    # ========================================

    def _estimate_reach(
        self,
        influencer: Dict[str, Any],
        campaign: Dict[str, Any]
    ) -> Dict[str, int]:
        """Estimer la portée de la campagne"""
        followers = influencer.get('total_followers', 0)
        avg_reach_rate = influencer.get('average_reach_rate', 0.15)  # 15% par défaut

        estimated_reach = int(followers * avg_reach_rate)

        return {
            'min': int(estimated_reach * 0.8),
            'max': int(estimated_reach * 1.2),
            'expected': estimated_reach
        }

    def _estimate_engagement(self, influencer: Dict[str, Any]) -> Dict[str, int]:
        """Estimer l'engagement"""
        followers = influencer.get('total_followers', 0)
        engagement_rate = influencer.get('engagement_rate', 3.0) / 100

        estimated_engagement = int(followers * engagement_rate)

        return {
            'likes': int(estimated_engagement * 0.7),
            'comments': int(estimated_engagement * 0.2),
            'shares': int(estimated_engagement * 0.1),
            'total': estimated_engagement
        }

    def _estimate_conversions(
        self,
        influencer: Dict[str, Any],
        campaign: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimer les conversions (ventes)"""
        reach = self._estimate_reach(influencer, campaign)['expected']

        # Taux de conversion typique: 1-3% du reach
        avg_conversion_rate = influencer.get('average_conversion_rate', 2.0) / 100

        estimated_conversions = int(reach * avg_conversion_rate)

        # Estimer le revenu
        product_price = campaign.get('product_price', 0)
        estimated_revenue = estimated_conversions * product_price

        return {
            'conversions': estimated_conversions,
            'conversion_rate': avg_conversion_rate * 100,
            'estimated_revenue': estimated_revenue,
            'estimated_roi': (estimated_revenue / influencer.get('average_campaign_price', 1)) * 100 if influencer.get('average_campaign_price') else 0
        }

    def _calculate_pricing(
        self,
        influencer: Dict[str, Any],
        campaign: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculer pricing recommandé"""
        base_price = influencer.get('average_campaign_price', 0)

        # Ajustements selon durée
        duration_days = campaign.get('duration_days', 7)
        if duration_days > 14:
            price = base_price * 1.5
        elif duration_days > 7:
            price = base_price * 1.2
        else:
            price = base_price

        return {
            'base_price': base_price,
            'recommended_price': price,
            'price_per_post': price / max(duration_days // 2, 1),  # Environ 1 post tous les 2 jours
            'negotiable': influencer.get('price_negotiable', True)
        }

    def _generate_match_reasons(self, breakdown: Dict[str, int]) -> List[str]:
        """Générer raisons du match"""
        reasons = []

        if breakdown.get('audience_alignment', 0) >= 80:
            reasons.append("Audience parfaitement alignée avec votre cible")

        if breakdown.get('niche_match', 0) >= 90:
            reasons.append("Expert dans votre catégorie de produit")

        if breakdown.get('budget_fit', 0) >= 85:
            reasons.append("Prix dans votre budget")

        if breakdown.get('performance_history', 0) >= 80:
            reasons.append("Excellent historique de performance")

        if breakdown.get('engagement_rate', 0) >= 80:
            reasons.append("Taux d'engagement très élevé")

        if not reasons:
            reasons.append("Bon potentiel de collaboration")

        return reasons

    # ========================================
    # SWIPE ACTIONS
    # ========================================

    async def swipe_right(
        self,
        merchant_id: str,
        influencer_id: str,
        campaign_id: str,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Swipe Right = Intéressé par cet influenceur

        Envoie invitation de collaboration
        """
        # Vérifier si déjà swipé
        existing = await self._check_existing_swipe(merchant_id, influencer_id, campaign_id)
        if existing:
            return {'error': 'Déjà swipé'}

        # Créer invitation
        invitation = {
            'merchant_id': merchant_id,
            'influencer_id': influencer_id,
            'campaign_id': campaign_id,
            'status': 'pending',
            'merchant_message': message,
            'created_at': datetime.now()
        }

        # En production: Insert dans collaboration_invitations
        # result = supabase.table('collaboration_invitations').insert(invitation).execute()

        # Vérifier si c'est un MATCH (influenceur a aussi swipé right)
        is_match = await self._check_mutual_interest(merchant_id, influencer_id)

        if is_match:
            # MATCH! Créer collaboration
            await self._create_collaboration(merchant_id, influencer_id, campaign_id)

            logger.info(f"💝 MATCH! Marchand {merchant_id} ↔ Influenceur {influencer_id}")

            return {
                'action': 'swipe_right',
                'match': True,
                'message': "C'est un MATCH! 💝 L'influenceur est aussi intéressé!"
            }
        else:
            # Invitation envoyée, en attente
            # Notification à l'influenceur
            await self._notify_influencer(influencer_id, merchant_id, campaign_id)

            logger.info(f"✅ Invitation envoyée à influenceur {influencer_id}")

            return {
                'action': 'swipe_right',
                'match': False,
                'message': "Invitation envoyée! En attente de réponse."
            }

    async def swipe_left(
        self,
        merchant_id: str,
        influencer_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        Swipe Left = Pas intéressé

        Ne pas montrer à nouveau cet influenceur pour cette campagne
        """
        # Enregistrer le swipe négatif
        swipe_record = {
            'merchant_id': merchant_id,
            'influencer_id': influencer_id,
            'campaign_id': campaign_id,
            'action': 'left',
            'created_at': datetime.now()
        }

        # En production: Insert dans swipe_history
        # supabase.table('swipe_history').insert(swipe_record).execute()

        logger.info(f"⬅️ Swipe left: Marchand {merchant_id} → Influenceur {influencer_id}")

        return {
            'action': 'swipe_left',
            'message': "Influenceur ignoré"
        }

    async def super_like(
        self,
        merchant_id: str,
        influencer_id: str,
        campaign_id: str,
        premium_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Super Like = Offre premium avec bonus

        Augmente les chances de réponse positive
        """
        # Créer invitation premium
        invitation = {
            'merchant_id': merchant_id,
            'influencer_id': influencer_id,
            'campaign_id': campaign_id,
            'status': 'pending',
            'type': 'super_like',
            'premium_offer': premium_offer,  # Bonus, prix majoré, etc.
            'priority': 'high',
            'created_at': datetime.now()
        }

        # En production: Insert avec priority flag
        # supabase.table('collaboration_invitations').insert(invitation).execute()

        # Notification push prioritaire à l'influenceur
        await self._notify_influencer_priority(influencer_id, merchant_id, campaign_id, premium_offer)

        logger.info(f"⭐ SUPER LIKE! Marchand {merchant_id} → Influenceur {influencer_id}")

        return {
            'action': 'super_like',
            'message': "Super Like envoyé! L'influenceur sera notifié en priorité."
        }

    async def get_recommendations(
        self,
        merchant_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Wrapper pour find_matches pour l'API simple
        Utilise des critères par défaut basés sur le profil marchand
        """
        # Récupérer profil marchand pour déduire les critères
        merchant = await self._get_merchant_profile(merchant_id)
        
        # Construire des détails de campagne par défaut
        default_campaign = {
            'product_category': merchant.get('industry', 'General'),
            'target_audience': {
                'locations': [merchant.get('country', 'MA')],
                'age_range': ['18-24', '25-34'],
                'gender': 'all'
            },
            'budget': 1000,  # Valeur par défaut
            'campaign_goals': ['awareness'],
            'duration_days': 30
        }
        
        return await self.find_matches(merchant_id, default_campaign, limit)

    async def record_swipe(
        self,
        merchant_id: str,
        influencer_id: str,
        action: str
    ) -> Dict[str, Any]:
        """Enregistrer un swipe (like/pass)"""
        if action == 'like':
            return await self.swipe_right(merchant_id, influencer_id, 'default_campaign')
        elif action == 'pass':
            return await self.swipe_left(merchant_id, influencer_id, 'default_campaign')
        elif action == 'super_like':
            return await self.super_like(merchant_id, influencer_id, 'default_campaign', {})
        else:
            return {'error': 'Invalid action'}

    # ========================================
    # HELPER FUNCTIONS
    # ========================================

    async def _get_merchant_profile(self, merchant_id: str) -> Dict[str, Any]:
        """Récupérer profil marchand"""
        # En production: Query Supabase
        return {}

    async def _get_active_influencers(self) -> List[Dict[str, Any]]:
        """Récupérer influenceurs actifs"""
        # En production: Query influenceurs avec status=active
        return []

    async def _check_existing_swipe(
        self,
        merchant_id: str,
        influencer_id: str,
        campaign_id: str
    ) -> bool:
        """Vérifier si déjà swipé"""
        # En production: Query swipe_history
        return False

    async def _check_mutual_interest(
        self,
        merchant_id: str,
        influencer_id: str
    ) -> bool:
        """Vérifier intérêt mutuel (match)"""
        # En production: Query invitations dans les 2 sens
        return False

    async def _create_collaboration(
        self,
        merchant_id: str,
        influencer_id: str,
        campaign_id: str
    ):
        """Créer collaboration après match"""
        # En production: Insert dans collaborations table
        pass

    async def _notify_influencer(
        self,
        influencer_id: str,
        merchant_id: str,
        campaign_id: str
    ):
        """Notifier influenceur d'une invitation"""
        # En production: Email/push notification
        pass

    async def _notify_influencer_priority(
        self,
        influencer_id: str,
        merchant_id: str,
        campaign_id: str,
        premium_offer: Dict[str, Any]
    ):
        """Notification prioritaire pour super like"""
        # En production: SMS + Email + Push
        pass

    # ========================================
    # ANALYTICS
    # ========================================

    async def get_match_analytics(self, merchant_id: str) -> Dict[str, Any]:
        """Analytics des matches pour un marchand"""
        analytics = {
            'total_swipes': 0,
            'swipes_right': 0,
            'swipes_left': 0,
            'super_likes': 0,
            'matches': 0,
            'match_rate': 0,
            'pending_invitations': 0,
            'active_collaborations': 0
        }

        return analytics


# Global instance
matching_service = InfluencerMatchingService()
