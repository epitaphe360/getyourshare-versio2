"""
Service IA Recommendations
Collaborative Filtering + Content-Based Recommendations
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json

import logging
logger = logging.getLogger(__name__)


class AIRecommendationsService:
    """
    Service d'intelligence artificielle pour recommandations de produits

    Méthodes:
    - Collaborative Filtering (basé sur comportement utilisateurs similaires)
    - Content-Based (basé sur attributs des produits)
    - Hybrid (combinaison des deux)
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    # ============================================
    # COLLABORATIVE FILTERING
    # ============================================

    def get_collaborative_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommandations basées sur utilisateurs similaires

        Algorithme:
        1. Trouver utilisateurs qui ont acheté les mêmes produits
        2. Identifier les produits que ces utilisateurs ont aussi aimé
        3. Recommander ces produits
        """
        try:
            # Récupérer les produits achetés par l'utilisateur
            user_purchases = self.supabase.table('conversions').select('product_id').eq('influencer_id', user_id).execute()

            user_product_ids = list(set([p['product_id'] for p in (user_purchases.data or []) if p.get('product_id')]))

            if not user_product_ids:
                # Si pas d'historique, recommander les produits populaires
                return self._get_popular_products(limit)

            # Trouver d'autres utilisateurs qui ont acheté les mêmes produits
            similar_users = self.supabase.table('conversions').select('influencer_id').in_('product_id', user_product_ids).neq('influencer_id', user_id).execute()

            similar_user_ids = list(set([u['influencer_id'] for u in (similar_users.data or []) if u.get('influencer_id')]))

            if not similar_user_ids:
                return self._get_popular_products(limit)

            # Produits achetés par ces utilisateurs similaires
            similar_purchases = self.supabase.table('conversions').select('product_id').in_('influencer_id', similar_user_ids).execute()

            # Compter la fréquence
            product_frequency = {}
            for purchase in (similar_purchases.data or []):
                product_id = purchase.get('product_id')
                if product_id and product_id not in user_product_ids:  # Exclure déjà achetés
                    product_frequency[product_id] = product_frequency.get(product_id, 0) + 1

            # Trier par fréquence
            sorted_products = sorted(product_frequency.items(), key=lambda x: x[1], reverse=True)[:limit]

            # Enrichir avec infos produits
            recommendations = []
            for product_id, frequency in sorted_products:
                product = self.supabase.table('products').select('*').eq('id', product_id).single().execute()

                if product.data:
                    recommendations.append({
                        **product.data,
                        'recommendation_score': frequency,
                        'recommendation_type': 'collaborative'
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Collaborative filtering error: {e}")
            return self._get_popular_products(limit)

    # ============================================
    # CONTENT-BASED FILTERING
    # ============================================

    def get_content_based_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommandations basées sur les attributs des produits

        Algorithme:
        1. Analyser les produits que l'utilisateur a aimé
        2. Extraire les caractéristiques (catégorie, prix, etc.)
        3. Trouver des produits similaires
        """
        try:
            # Récupérer les produits achetés par l'utilisateur
            user_purchases = self.supabase.table('conversions').select('product_id').eq('influencer_id', user_id).execute()

            user_product_ids = list(set([p['product_id'] for p in (user_purchases.data or []) if p.get('product_id')]))

            if not user_product_ids:
                return self._get_popular_products(limit)

            # Récupérer les détails de ces produits
            user_products = self.supabase.table('products').select('*').in_('id', user_product_ids).execute()

            # Analyser les caractéristiques communes
            categories = []
            price_sum = Decimal('0')
            price_count = 0

            for product in (user_products.data or []):
                if product.get('category'):
                    categories.append(product['category'])
                if product.get('price'):
                    price_sum += Decimal(str(product['price']))
                    price_count += 1

            # Catégorie la plus fréquente
            if categories:
                from collections import Counter
                most_common_category = Counter(categories).most_common(1)[0][0]
            else:
                most_common_category = None

            # Prix moyen
            avg_price = float(price_sum / price_count) if price_count > 0 else None

            # Trouver des produits similaires
            query = self.supabase.table('products').select('*').neq('id', 'in', user_product_ids)

            if most_common_category:
                query = query.eq('category', most_common_category)

            # Limiter la plage de prix (±30%)
            if avg_price:
                min_price = avg_price * 0.7
                max_price = avg_price * 1.3
                query = query.gte('price', min_price).lte('price', max_price)

            query = query.eq('is_active', True).limit(limit)

            response = query.execute()

            recommendations = []
            for product in (response.data or []):
                # Calculer score de similarité
                score = 0

                if product.get('category') == most_common_category:
                    score += 50

                if avg_price and product.get('price'):
                    price_diff = abs(product['price'] - avg_price) / avg_price
                    score += max(0, 50 - (price_diff * 100))

                recommendations.append({
                    **product,
                    'recommendation_score': score,
                    'recommendation_type': 'content_based'
                })

            # Trier par score
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)

            return recommendations

        except Exception as e:
            logger.error(f"Content-based filtering error: {e}")
            return self._get_popular_products(limit)

    # ============================================
    # HYBRID RECOMMENDATIONS
    # ============================================

    def get_hybrid_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommandations hybrides (collaborative + content-based)

        Combine les deux approches pour de meilleurs résultats
        """
        try:
            # Récupérer les deux types
            collaborative = self.get_collaborative_recommendations(user_id, limit * 2)
            content_based = self.get_content_based_recommendations(user_id, limit * 2)

            # Fusionner et pondérer
            all_recommendations = {}

            # Collaborative: poids 60%
            for rec in collaborative:
                product_id = rec['id']
                all_recommendations[product_id] = {
                    **rec,
                    'hybrid_score': rec.get('recommendation_score', 0) * 0.6
                }

            # Content-based: poids 40%
            for rec in content_based:
                product_id = rec['id']
                if product_id in all_recommendations:
                    # Déjà présent, ajouter le score
                    all_recommendations[product_id]['hybrid_score'] += rec.get('recommendation_score', 0) * 0.4
                else:
                    all_recommendations[product_id] = {
                        **rec,
                        'hybrid_score': rec.get('recommendation_score', 0) * 0.4
                    }

            # Trier par score hybride
            sorted_recommendations = sorted(
                all_recommendations.values(),
                key=lambda x: x['hybrid_score'],
                reverse=True
            )[:limit]

            # Marquer comme hybrid
            for rec in sorted_recommendations:
                rec['recommendation_type'] = 'hybrid'

            return sorted_recommendations

        except Exception as e:
            logger.error(f"Hybrid recommendations error: {e}")
            return self._get_popular_products(limit)

    # ============================================
    # TRENDING PRODUCTS
    # ============================================

    def get_trending_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Produits en tendance (basé sur ventes récentes)
        """
        try:
            # Derniers 7 jours
            start_date = (datetime.now() - timedelta(days=7)).isoformat()

            conversions = self.supabase.table('conversions').select('product_id, sale_amount').gte('created_at', start_date).execute()

            # Grouper par produit
            product_stats = {}
            for conv in (conversions.data or []):
                product_id = conv.get('product_id')
                if product_id:
                    if product_id not in product_stats:
                        product_stats[product_id] = {'sales': 0, 'revenue': Decimal('0')}

                    product_stats[product_id]['sales'] += 1
                    product_stats[product_id]['revenue'] += Decimal(str(conv.get('sale_amount', 0)))

            # Trier par ventes
            sorted_products = sorted(
                product_stats.items(),
                key=lambda x: x[1]['sales'],
                reverse=True
            )[:limit]

            # Enrichir
            recommendations = []
            for product_id, stats in sorted_products:
                product = self.supabase.table('products').select('*').eq('id', product_id).single().execute()

                if product.data:
                    recommendations.append({
                        **product.data,
                        'trending_sales': stats['sales'],
                        'trending_revenue': float(stats['revenue']),
                        'recommendation_type': 'trending'
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Trending products error: {e}")
            return []

    # ============================================
    # PERSONALIZED FOR YOU
    # ============================================

    def get_personalized_for_you(
        self,
        user_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Recommandations personnalisées complètes

        Retourne plusieurs sections:
        - Based on your purchases
        - Trending now
        - Popular in your category
        """
        try:
            return {
                'success': True,
                'user_id': user_id,
                'sections': {
                    'based_on_purchases': self.get_hybrid_recommendations(user_id, 5),
                    'trending_now': self.get_trending_products(5),
                    'you_might_like': self.get_collaborative_recommendations(user_id, 5),
                    'similar_products': self.get_content_based_recommendations(user_id, 5)
                }
            }

        except Exception as e:
            logger.error(f"Personalized recommendations error: {e}")
            return {
                'success': False,
                'error': str(e),
                'sections': {}
            }

    # ============================================
    # HELPERS
    # ============================================

    def _get_popular_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Produits les plus populaires (fallback)
        """
        try:
            # Compter les conversions par produit
            conversions = self.supabase.table('conversions').select('product_id').execute()

            product_frequency = {}
            for conv in (conversions.data or []):
                product_id = conv.get('product_id')
                if product_id:
                    product_frequency[product_id] = product_frequency.get(product_id, 0) + 1

            sorted_products = sorted(product_frequency.items(), key=lambda x: x[1], reverse=True)[:limit]

            recommendations = []
            for product_id, count in sorted_products:
                product = self.supabase.table('products').select('*').eq('id', product_id).single().execute()

                if product.data:
                    recommendations.append({
                        **product.data,
                        'recommendation_score': count,
                        'recommendation_type': 'popular'
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Popular products error: {e}")
            return []

    # ============================================
    # PRODUCT SIMILARITY
    # ============================================

    def get_similar_products(
        self,
        product_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Produits similaires à un produit donné
        """
        try:
            # Récupérer le produit source
            source = self.supabase.table('products').select('*').eq('id', product_id).single().execute()

            if not source.data:
                return []

            source_product = source.data

            # Trouver des produits similaires
            query = self.supabase.table('products').select('*').neq('id', product_id).eq('is_active', True)

            # Même catégorie
            if source_product.get('category'):
                query = query.eq('category', source_product['category'])

            # Plage de prix similaire (±40%)
            if source_product.get('price'):
                source_price = source_product['price']
                min_price = source_price * 0.6
                max_price = source_price * 1.4
                query = query.gte('price', min_price).lte('price', max_price)

            query = query.limit(limit)

            response = query.execute()

            return response.data or []

        except Exception as e:
            logger.error(f"Similar products error: {e}")
            return []
