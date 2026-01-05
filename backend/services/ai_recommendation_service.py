"""
AI Product Recommendation Service for ShareYourSales
Intelligent product recommendations using collaborative filtering and content-based algorithms

Dependencies:
    pip install numpy scikit-learn pandas

Features:
    - Collaborative Filtering (User-User, Item-Item)
    - Content-Based Filtering (TF-IDF, Cosine Similarity)
    - Hybrid Recommendations
    - Trending Products
    - Personalized Recommendations
    - Similar Products
    - Cold Start Handling
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not installed. Run: pip install numpy scikit-learn pandas")


logger = logging.getLogger(__name__)


class AIRecommendationEngine:
    """
    AI-powered product recommendation engine

    Methods:
    1. Collaborative Filtering - Recommendations based on user behavior similarity
    2. Content-Based Filtering - Recommendations based on product attributes
    3. Hybrid Approach - Combining both methods
    4. Trending Products - Popular products based on recent activity

    Example:
        engine = AIRecommendationEngine()

        # Train on user interactions
        engine.train_collaborative_filtering(user_interactions)

        # Get recommendations for a user
        recommendations = engine.get_user_recommendations(user_id="user123", n=10)

        # Get similar products
        similar = engine.get_similar_products(product_id="prod456", n=5)
    """

    def __init__(self):
        """Initialize recommendation engine"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Install with: pip install scikit-learn numpy pandas")

        # User-Item interaction matrix
        self.user_item_matrix = None
        self.user_ids = []
        self.product_ids = []

        # Product content features
        self.product_features = {}
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None

        # Similarity matrices
        self.user_similarity = None
        self.item_similarity = None

        # Cache
        self.recommendation_cache = {}
        self.cache_ttl = 3600  # 1 hour

    # ===== Data Preparation =====

    def prepare_user_item_matrix(
        self,
        interactions: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Prepare user-item interaction matrix from interaction data

        Args:
            interactions: List of interactions with user_id, product_id, interaction_type, value
                Example: [
                    {"user_id": "u1", "product_id": "p1", "interaction_type": "view", "value": 1},
                    {"user_id": "u1", "product_id": "p2", "interaction_type": "purchase", "value": 5},
                ]

        Returns:
            User-item matrix (numpy array)
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        # Extract unique users and products
        users = sorted(list(set([i["user_id"] for i in interactions])))
        products = sorted(list(set([i["product_id"] for i in interactions])))

        self.user_ids = users
        self.product_ids = products

        # Create matrix
        matrix = np.zeros((len(users), len(products)))

        # Interaction weights
        weights = {
            "view": 1.0,
            "click": 1.5,
            "add_to_cart": 3.0,
            "purchase": 5.0,
            "share": 4.0,
            "like": 2.0
        }

        # Fill matrix
        for interaction in interactions:
            user_idx = users.index(interaction["user_id"])
            product_idx = products.index(interaction["product_id"])

            interaction_type = interaction.get("interaction_type", "view")
            weight = weights.get(interaction_type, 1.0)
            value = interaction.get("value", 1.0)

            matrix[user_idx][product_idx] += weight * value

        self.user_item_matrix = matrix
        logger.info(f"Created user-item matrix: {len(users)} users x {len(products)} products")

        return matrix

    def prepare_product_features(
        self,
        products: List[Dict[str, Any]]
    ):
        """
        Prepare product content features for content-based filtering

        Args:
            products: List of products with id, name, description, category, tags
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        self.product_features = {p["id"]: p for p in products}

        # Create text corpus for TF-IDF
        corpus = []
        product_ids = []

        for product in products:
            # Combine all text features
            text_features = []

            if product.get("name"):
                text_features.append(product["name"])

            if product.get("description"):
                text_features.append(product["description"])

            if product.get("category"):
                text_features.append(product["category"])

            if product.get("tags"):
                if isinstance(product["tags"], list):
                    text_features.extend(product["tags"])
                else:
                    text_features.append(product["tags"])

            corpus.append(" ".join(text_features))
            product_ids.append(product["id"])

        # Create TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
        self.product_ids = product_ids

        logger.info(f"Created TF-IDF matrix for {len(products)} products")

    # ===== Collaborative Filtering =====

    def train_collaborative_filtering(
        self,
        interactions: List[Dict[str, Any]],
        method: str = "item"  # "user" or "item"
    ):
        """
        Train collaborative filtering model

        Args:
            interactions: User-item interactions
            method: "user" for user-based, "item" for item-based CF
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        # Prepare matrix
        self.prepare_user_item_matrix(interactions)

        if method == "user":
            # User-based collaborative filtering
            # Compute user-user similarity
            self.user_similarity = cosine_similarity(self.user_item_matrix)
            logger.info("Trained user-based collaborative filtering")

        elif method == "item":
            # Item-based collaborative filtering
            # Compute item-item similarity
            self.item_similarity = cosine_similarity(self.user_item_matrix.T)
            logger.info("Trained item-based collaborative filtering")

        else:
            raise ValueError("method must be 'user' or 'item'")

    def get_user_recommendations_cf(
        self,
        user_id: str,
        n: int = 10,
        exclude_purchased: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations using collaborative filtering

        Args:
            user_id: User ID
            n: Number of recommendations
            exclude_purchased: Exclude already purchased products

        Returns:
            List of recommended products with scores
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        if self.user_item_matrix is None:
            raise ValueError("Model not trained. Call train_collaborative_filtering first.")

        if user_id not in self.user_ids:
            # Cold start - return popular items
            return self.get_trending_products(n=n)

        user_idx = self.user_ids.index(user_id)

        if self.user_similarity is not None:
            # User-based CF
            user_sim = self.user_similarity[user_idx]

            # Get weighted average of similar users' ratings
            predictions = np.dot(user_sim, self.user_item_matrix) / np.sum(np.abs(user_sim))

        elif self.item_similarity is not None:
            # Item-based CF
            user_ratings = self.user_item_matrix[user_idx]

            # Predict ratings based on item similarity
            predictions = np.dot(user_ratings, self.item_similarity) / np.sum(np.abs(self.item_similarity), axis=0)

        else:
            raise ValueError("No similarity matrix available")

        # Exclude already interacted products
        if exclude_purchased:
            predictions = predictions.copy()
            interacted_items = np.where(self.user_item_matrix[user_idx] > 0)[0]
            predictions[interacted_items] = -np.inf

        # Get top N recommendations
        top_indices = np.argsort(predictions)[::-1][:n]

        recommendations = []
        for idx in top_indices:
            if predictions[idx] > 0:  # Only include positive predictions
                recommendations.append({
                    "product_id": self.product_ids[idx],
                    "score": float(predictions[idx]),
                    "method": "collaborative_filtering"
                })

        return recommendations

    # ===== Content-Based Filtering =====

    def get_similar_products(
        self,
        product_id: str,
        n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar products using content-based filtering

        Args:
            product_id: Product ID
            n: Number of similar products

        Returns:
            List of similar products with similarity scores
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        if self.tfidf_matrix is None:
            raise ValueError("Product features not prepared. Call prepare_product_features first.")

        if product_id not in self.product_ids:
            return []

        product_idx = self.product_ids.index(product_id)

        # Compute similarity with all products
        product_vector = self.tfidf_matrix[product_idx]
        similarities = cosine_similarity(product_vector, self.tfidf_matrix).flatten()

        # Get top N similar products (excluding itself)
        top_indices = np.argsort(similarities)[::-1][1:n+1]

        similar_products = []
        for idx in top_indices:
            similar_products.append({
                "product_id": self.product_ids[idx],
                "similarity_score": float(similarities[idx]),
                "method": "content_based"
            })

        return similar_products

    def get_user_recommendations_content(
        self,
        user_id: str,
        n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on user's past product interactions (content-based)

        Args:
            user_id: User ID
            n: Number of recommendations

        Returns:
            List of recommended products
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        if user_id not in self.user_ids:
            return []

        user_idx = self.user_ids.index(user_id)

        # Get user's interacted products
        user_ratings = self.user_item_matrix[user_idx]
        interacted_indices = np.where(user_ratings > 0)[0]

        if len(interacted_indices) == 0:
            return []

        # Get products similar to user's liked products
        all_similarities = np.zeros(len(self.product_ids))

        for idx in interacted_indices:
            product_id = self.product_ids[idx]
            similar = self.get_similar_products(product_id, n=20)

            for sim_product in similar:
                sim_idx = self.product_ids.index(sim_product["product_id"])
                # Weight by user's rating of original product
                all_similarities[sim_idx] += sim_product["similarity_score"] * user_ratings[idx]

        # Exclude already interacted products
        all_similarities[interacted_indices] = -np.inf

        # Get top N
        top_indices = np.argsort(all_similarities)[::-1][:n]

        recommendations = []
        for idx in top_indices:
            if all_similarities[idx] > 0:
                recommendations.append({
                    "product_id": self.product_ids[idx],
                    "score": float(all_similarities[idx]),
                    "method": "content_based"
                })

        return recommendations

    # ===== Hybrid Recommendations =====

    def get_hybrid_recommendations(
        self,
        user_id: str,
        n: int = 10,
        cf_weight: float = 0.6,
        content_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Get hybrid recommendations combining CF and content-based

        Args:
            user_id: User ID
            n: Number of recommendations
            cf_weight: Weight for collaborative filtering
            content_weight: Weight for content-based filtering

        Returns:
            List of recommended products
        """
        # Get both types of recommendations
        cf_recs = self.get_user_recommendations_cf(user_id, n=n*2)
        content_recs = self.get_user_recommendations_content(user_id, n=n*2)

        # Combine scores
        combined_scores = defaultdict(float)

        for rec in cf_recs:
            combined_scores[rec["product_id"]] += rec["score"] * cf_weight

        for rec in content_recs:
            combined_scores[rec["product_id"]] += rec["score"] * content_weight

        # Sort by combined score
        sorted_products = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

        recommendations = []
        for product_id, score in sorted_products:
            recommendations.append({
                "product_id": product_id,
                "score": float(score),
                "method": "hybrid"
            })

        return recommendations

    # ===== Trending Products =====

    def get_trending_products(
        self,
        n: int = 10,
        time_window_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get trending products based on recent interactions

        Args:
            n: Number of trending products
            time_window_days: Time window for trending calculation

        Returns:
            List of trending products
        """
        if self.user_item_matrix is None:
            return []

        # Sum interactions across all users for each product
        product_scores = np.sum(self.user_item_matrix, axis=0)

        # Get top N
        top_indices = np.argsort(product_scores)[::-1][:n]

        trending = []
        for idx in top_indices:
            trending.append({
                "product_id": self.product_ids[idx],
                "score": float(product_scores[idx]),
                "method": "trending"
            })

        return trending

    # ===== Main Recommendation Method =====

    def get_recommendations(
        self,
        user_id: str,
        n: int = 10,
        method: str = "hybrid"  # "hybrid", "cf", "content", "trending"
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations for a user

        Args:
            user_id: User ID
            n: Number of recommendations
            method: Recommendation method

        Returns:
            List of recommended products
        """
        # Check cache
        cache_key = f"{user_id}_{n}_{method}"
        if cache_key in self.recommendation_cache:
            cached_time, cached_recs = self.recommendation_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                return cached_recs

        # Get recommendations
        if method == "hybrid":
            recommendations = self.get_hybrid_recommendations(user_id, n)
        elif method == "cf":
            recommendations = self.get_user_recommendations_cf(user_id, n)
        elif method == "content":
            recommendations = self.get_user_recommendations_content(user_id, n)
        elif method == "trending":
            recommendations = self.get_trending_products(n)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Cache results
        self.recommendation_cache[cache_key] = (datetime.now(), recommendations)

        return recommendations

    # ===== Evaluation Metrics =====

    def evaluate_recommendations(
        self,
        test_interactions: List[Dict[str, Any]],
        n: int = 10
    ) -> Dict[str, float]:
        """
        Evaluate recommendation quality using precision, recall, and NDCG

        Args:
            test_interactions: Test set interactions
            n: Number of recommendations to evaluate

        Returns:
            Evaluation metrics
        """
        precisions = []
        recalls = []

        # Group test interactions by user
        test_by_user = defaultdict(set)
        for interaction in test_interactions:
            test_by_user[interaction["user_id"]].add(interaction["product_id"])

        for user_id, true_products in test_by_user.items():
            # Get recommendations
            recs = self.get_recommendations(user_id, n=n)
            rec_products = set([r["product_id"] for r in recs])

            # Calculate precision and recall
            hits = len(rec_products & true_products)

            precision = hits / len(rec_products) if rec_products else 0
            recall = hits / len(true_products) if true_products else 0

            precisions.append(precision)
            recalls.append(recall)

        return {
            "precision@{n}": np.mean(precisions),
            "recall@{n}": np.mean(recalls),
            "f1_score": 2 * np.mean(precisions) * np.mean(recalls) / (np.mean(precisions) + np.mean(recalls)) if (np.mean(precisions) + np.mean(recalls)) > 0 else 0
        }


# ===== Usage Example =====
if __name__ == "__main__":
    # Example usage
    engine = AIRecommendationEngine()

    # Sample interactions
    interactions = [
        {"user_id": "u1", "product_id": "p1", "interaction_type": "view", "value": 1},
        {"user_id": "u1", "product_id": "p2", "interaction_type": "purchase", "value": 1},
        {"user_id": "u2", "product_id": "p1", "interaction_type": "purchase", "value": 1},
        {"user_id": "u2", "product_id": "p3", "interaction_type": "view", "value": 1},
    ]

    # Sample products
    products = [
        {"id": "p1", "name": "iPhone 15", "description": "Latest smartphone", "category": "Electronics", "tags": ["phone", "apple"]},
        {"id": "p2", "name": "Samsung Galaxy", "description": "Android smartphone", "category": "Electronics", "tags": ["phone", "samsung"]},
        {"id": "p3", "name": "MacBook Pro", "description": "Laptop computer", "category": "Electronics", "tags": ["laptop", "apple"]},
    ]

    # Train
    engine.train_collaborative_filtering(interactions, method="item")
    engine.prepare_product_features(products)

    # Get recommendations
    recommendations = engine.get_recommendations("u1", n=5)
    print("Recommendations:", recommendations)

    # Get similar products
    similar = engine.get_similar_products("p1", n=2)
    print("Similar products:", similar)
