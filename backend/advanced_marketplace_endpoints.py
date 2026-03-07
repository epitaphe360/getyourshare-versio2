"""
============================================
ADVANCED MARKETPLACE ENDPOINTS
GetYourShare - Marketplace Enrichie
============================================

Endpoints pour marketplace avancée:
- Produits avec filtres multiples
- Catégories
- Notes et avis
- Système de panier (frontend)
- Recherche intelligente
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from auth import get_current_user
from supabase_client import supabase
from utils.logger import logger

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])

# ============================================
# PYDANTIC MODELS
# ============================================

class ReviewCreate(BaseModel):
    """Création d'un avis"""
    product_id: str
    rating: int
    comment: Optional[str]

class ReviewResponse(BaseModel):
    """Avis produit"""
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    comment: Optional[str]
    created_at: datetime

# ============================================
# ENDPOINTS
# ============================================

@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    search: Optional[str] = None,
    category: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    minRating: Optional[float] = None,
    inStock: Optional[bool] = None,
    sortBy: Optional[str] = "newest"
):
    """
    Récupère les produits avec filtres avancés
    """
    try:
        # Base query
        query = supabase.table('products').select('*', count='exact')

        # Filtres
        if search:
            query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
        
        if category:
            query = query.eq('category_id', category)
        
        if minPrice is not None:
            query = query.gte('price', minPrice)
        
        if maxPrice is not None:
            query = query.lte('price', maxPrice)
        
        if minRating is not None:
            query = query.gte('rating', minRating)
        
        if inStock:
            query = query.eq('in_stock', True)

        # Tri
        if sortBy == "newest":
            query = query.order('created_at', desc=True)
        elif sortBy == "price_asc":
            query = query.order('price', desc=False)
        elif sortBy == "price_desc":
            query = query.order('price', desc=True)
        elif sortBy == "rating":
            query = query.order('rating', desc=True)
        elif sortBy == "popular":
            query = query.order('reviews_count', desc=True)

        # Pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        # Execute
        response = query.execute()
        
        products = response.data if response.data else []
        total = response.count if hasattr(response, 'count') else len(products)

        # Enrichir avec infos marchands (simulation)
        for product in products:
            product['merchant_name'] = product.get('merchant_name', 'Marchand')
            product['category'] = product.get('category', 'Général')
            product['rating'] = product.get('rating', 4.0)
            product['reviews_count'] = product.get('reviews_count', 0)
            product['in_stock'] = product.get('in_stock', True)

        return {
            'products': products,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'pages': (total + page_size - 1) // page_size
            }
        }

    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch products: {str(e)}"
        )


@router.get("/categories")
async def get_categories():
    """
    Récupère toutes les catégories
    """
    try:
        response = supabase.table('categories').select('*').order('name').execute()
        
        categories = response.data if response.data else []
        
        # Ajouter des catégories de démonstration si vide
        if not categories:
            categories = [
                {"id": "1", "name": "Électronique", "slug": "electronique"},
                {"id": "2", "name": "Mode", "slug": "mode"},
                {"id": "3", "name": "Maison", "slug": "maison"},
                {"id": "4", "name": "Sports", "slug": "sports"},
                {"id": "5", "name": "Beauté", "slug": "beaute"},
                {"id": "6", "name": "Livres", "slug": "livres"},
                {"id": "7", "name": "Jouets", "slug": "jouets"},
                {"id": "8", "name": "Services", "slug": "services"}
            ]

        return {
            'categories': categories
        }

    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}"
        )


@router.get("/products/{product_id}")
async def get_product_details(product_id: str):
    """
    Récupère les détails d'un produit
    """
    try:
        response = supabase.table('products').select('*').eq('id', product_id).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        product = response.data
        
        # Enrichir avec infos supplémentaires
        product['merchant_name'] = product.get('merchant_name', 'Marchand')
        product['category'] = product.get('category', 'Général')
        product['rating'] = product.get('rating', 4.0)
        product['reviews_count'] = product.get('reviews_count', 0)
        product['in_stock'] = product.get('in_stock', True)

        return {
            'product': product
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product: {str(e)}"
        )


@router.get("/products/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50)
):
    """
    Récupère les avis d'un produit
    """
    try:
        # Base query
        query = supabase.table('product_reviews')\
            .select('*, users(first_name, last_name)')\
            .eq('product_id', product_id)\
            .order('created_at', desc=True)

        # Pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        response = query.execute()
        
        reviews = response.data if response.data else []
        
        # Formater les avis
        for review in reviews:
            user = review.get('users', {})
            review['user_name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or 'Utilisateur'

        return {
            'reviews': reviews,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': len(reviews)
            }
        }

    except Exception as e:
        logger.error(f"Error fetching reviews for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reviews: {str(e)}"
        )


@router.post("/products/{product_id}/reviews", status_code=status.HTTP_201_CREATED)
async def create_review(
    product_id: str,
    review: ReviewCreate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Créer un avis sur un produit
    """
    try:
        # Vérifier que le produit existe
        product = supabase.table('products').select('id').eq('id', product_id).single().execute()
        if not product.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Créer l'avis
        review_data = {
            'product_id': product_id,
            'user_id': current_user['id'],
            'rating': review.rating,
            'comment': review.comment,
            'created_at': datetime.utcnow().isoformat()
        }

        response = supabase.table('product_reviews').insert(review_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create review"
            )

        # Mettre à jour la note moyenne du produit
        try:
            all_reviews_res = supabase.table('product_reviews').select('rating').eq('product_id', product_id).execute()
            all_reviews = all_reviews_res.data or []
            if all_reviews:
                avg_rating = round(sum(float(r['rating']) for r in all_reviews) / len(all_reviews), 2)
                supabase.table('products').update({
                    'rating': avg_rating,
                    'review_count': len(all_reviews)
                }).eq('id', product_id).execute()
        except Exception as rating_err:
            logger.error(f"Error updating product rating: {rating_err}")

        return {
            'success': True,
            'review': response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )


@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2)
):
    """
    Suggestions de recherche intelligente
    """
    try:
        # Rechercher dans les produits
        products_response = supabase.table('products')\
            .select('name')\
            .ilike('name', f'%{query}%')\
            .limit(5)\
            .execute()

        # Rechercher dans les catégories
        categories_response = supabase.table('categories')\
            .select('name')\
            .ilike('name', f'%{query}%')\
            .limit(3)\
            .execute()

        suggestions = []
        
        # Ajouter produits
        for product in (products_response.data or []):
            suggestions.append({
                'type': 'product',
                'text': product['name']
            })
        
        # Ajouter catégories
        for category in (categories_response.data or []):
            suggestions.append({
                'type': 'category',
                'text': category['name']
            })

        return {
            'suggestions': suggestions
        }

    except Exception as e:
        logger.error(f"Error fetching suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch suggestions: {str(e)}"
        )


@router.get("/trending")
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50)
):
    """
    Récupère les produits tendance
    """
    try:
        response = supabase.table('products')\
            .select('*')\
            .order('reviews_count', desc=True)\
            .order('rating', desc=True)\
            .limit(limit)\
            .execute()

        products = response.data if response.data else []

        return {
            'products': products
        }

    except Exception as e:
        logger.error(f"Error fetching trending products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending products: {str(e)}"
        )


@router.get("/featured")
async def get_featured_products(
    limit: int = Query(6, ge=1, le=20)
):
    """
    Récupère les produits mis en avant
    """
    try:
        response = supabase.table('products')\
            .select('*')\
            .eq('featured', True)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        products = response.data if response.data else []

        return {
            'products': products
        }

    except Exception as e:
        logger.error(f"Error fetching featured products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch featured products: {str(e)}"
        )
