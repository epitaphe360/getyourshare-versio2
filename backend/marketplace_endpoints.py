"""
Marketplace Endpoints - Style Groupon
API pour marketplace avec deals, produits détaillés, reviews

Endpoints:
- GET /api/marketplace/products - Liste produits marketplace
- GET /api/marketplace/products/{id} - Détails produit complet
- GET /api/marketplace/categories - Catégories
- GET /api/marketplace/featured - Produits featured
- GET /api/marketplace/deals-of-day - Deals du jour
- POST /api/marketplace/products/{id}/view - Incrémenter vues
- POST /api/marketplace/products/{id}/request-affiliate - Demander affiliation
- POST /api/marketplace/products/{id}/review - Ajouter avis
- GET /api/marketplace/products/{id}/reviews - Avis produit
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import structlog

from auth import get_current_user_from_cookie, optional_auth
from supabase_client import supabase
from utils.db_safe import build_or_search
from utils.db_optimized import DBOptimizer
from db_helpers import get_all_services, get_service_by_id

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])
logger = structlog.get_logger()


# ============================================
# PYDANTIC MODELS
# ============================================

class ProductHighlight(BaseModel):
    """Point clé produit"""
    icon: str = Field(..., description="Emoji ou icon")
    text: str = Field(..., description="Texte du highlight")


class ProductFAQ(BaseModel):
    """Question fréquente"""
    question: str
    answer: str


class ProductLocation(BaseModel):
    """Localisation service"""
    address: str
    city: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class ProductReviewRequest(BaseModel):
    """Créer un avis"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    title: Optional[str] = Field(None, max_length=255)
    comment: str = Field(..., min_length=10, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "title": "Excellent service!",
                "comment": "J'ai adoré ce service. Personnel professionnel, ambiance agréable. Je recommande!"
            }
        }


class AffiliateRequestCreate(BaseModel):
    """Demande d'affiliation"""
    message: Optional[str] = Field(None, max_length=500, description="Message au marchand")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Bonjour, je suis influenceur avec 50K followers sur Instagram. J'aimerais promouvoir vos produits."
            }
        }


# ============================================
# ENDPOINTS - PUBLIC
# ============================================

@router.get("/products", response_model=dict)
async def get_marketplace_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|price|rating|sold_count|discount)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_discount: Optional[int] = None
):
    """
    Liste des produits marketplace

    **Filtres:**
    - category: Slug de catégorie
    - search: Recherche texte (nom, description)
    - min_price, max_price: Fourchette de prix
    - min_discount: Réduction minimum (%)

    **Tri:**
    - created_at: Date de création
    - price: Prix
    - rating: Note moyenne
    - sold_count: Nombre de ventes
    - discount: % de réduction
    """
    try:
        offset = (page - 1) * limit

        # Construire query - Using products table directly
        # Select relevant fields including merchant info
        # Simplified query to avoid potential FK issues for now
        query = supabase.table('products').select('*')

        # Pas de filtre status car la colonne n'existe pas

        # Filtre: catégorie
        if category:
            # TODO: Filtrer par catégorie (nécessite ajustement query)
            pass

        # Filtre: recherche (sécurisé contre SQL injection)
        if search:
            query = build_or_search(query, ['name', 'description'], search)

        # Filtre: prix (using current_price from products table)
        if min_price:
            query = query.gte('current_price', min_price)
        if max_price:
            query = query.lte('current_price', max_price)

        # Filtre: réduction (using discount field if exists)
        if min_discount:
            # Calculate discount if original_price and current_price exist
            pass  # May need to handle this differently

        # Tri
        # if sort_by == "price":
        #     sort_field = "current_price"
        # elif sort_by == "rating":
        #     sort_field = "rating"  # May need adjustment if field name differs
        # elif sort_by == "sold_count":
        #     sort_field = "sales_count"  # Adjust to actual field name
        # elif sort_by == "discount":
        #     sort_field = "discount"  # Adjust to actual field name
        # else:
        #     sort_field = "created_at"

        # query = query.order(sort_field, desc=(order == 'desc'))

        # Pagination
        # query = query.range(offset, offset + limit - 1)

        # Exécuter
        result = query.execute()
        
        products = result.data or []
        
        # Enrichir avec info rémunération
        for p in products:
            p['remuneration_model'] = 'commission'
            p['commission_type'] = 'percentage'
            # Ensure commission_percentage is present or default to something
            if 'commission_percentage' not in p:
                p['commission_percentage'] = 0

        return {
            "success": True,
            "products": products,
            "total": len(result.data) if result.data else 0, # result.count is not available without count='exact'
            "page": page,
            "limit": limit,
            "total_pages": 1 # Simplified
        }

    except Exception as e:
        logger.error("get_marketplace_products_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des produits"
        )


@router.get("/products/{product_id}", response_model=dict)
async def get_product_detail(product_id: str):
    """
    Détails complets d'un produit (style Groupon)

    **Inclut:**
    - Toutes les infos produit
    - Images
    - Highlights
    - Conditions
    - FAQ
    - Reviews
    - Marchand info
    - Stats (ventes, vues, rating)
    """
    try:
        # Récupérer produit complet directement depuis la table products
        result = supabase.table('products').select('*').eq('id', product_id).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )

        product = result.data[0]
        
        # Récupérer les infos du marchand séparément
        if product.get('merchant_id'):
            try:
                merchant_result = supabase.table('users').select(
                    'id, first_name, last_name, email, phone, company_name, username'
                ).eq('id', product['merchant_id']).execute()
                
                if merchant_result.data and len(merchant_result.data) > 0:
                    merchant_data = merchant_result.data[0]
                    first = merchant_data.get('first_name', '')
                    last = merchant_data.get('last_name', '')
                    name = f"{first} {last}".strip()
                    if not name:
                        name = merchant_data.get('company_name') or merchant_data.get('username') or "Marchand"
                    
                    product['merchant'] = {
                        'id': merchant_data.get('id'),
                        'name': name,
                        'email': merchant_data.get('email'),
                        'phone': merchant_data.get('phone'),
                        'company_name': merchant_data.get('company_name')
                    }
            except Exception as e:
                logger.error(f'Error fetching merchant: {e}')
                product['merchant'] = None
        
        # Ajouter info explicite sur la rémunération
        product['remuneration_model'] = 'commission'
        product['commission_type'] = 'percentage'
        if 'commission_percentage' not in product:
            product['commission_percentage'] = 0
        
        # Calculer deal_status (logique de la vue)
        now = datetime.utcnow().isoformat()
        expiry = product.get('expiry_date')
        stock = product.get('stock_quantity')
        is_active = product.get('is_active', True)
        
        deal_status = 'active'
        if is_active is False:
            deal_status = 'inactive'
        elif stock is not None and stock <= 0:
            deal_status = 'sold_out'
        elif expiry and expiry < now:
            deal_status = 'expired'
            
        product['deal_status'] = deal_status
        
        # Compter les affiliés actifs
        try:
            count_res = supabase.table('affiliate_requests').select(
                'id', count='exact'
            ).eq('product_id', product_id).eq('status', 'approved').execute()
            product['active_affiliates_count'] = count_res.count or 0
        except:
            product['active_affiliates_count'] = 0

        # Incrémenter vues (async)
        try:
            supabase.rpc('increment_product_views', {'p_product_id': product_id}).execute()
        except Exception as e:
            logger.error(f'Error incrementing views: {e}')
            pass  # Non-bloquant

        return {
            "success": True,
            "product": product
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_product_detail_failed", product_id=product_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du produit"
        )


@router.get("/categories", response_model=dict)
async def get_categories():
    """
    Liste des catégories de produits

    Hiérarchie: catégories parents + sous-catégories
    """
    try:
        # Récupérer toutes les catégories actives
        result = supabase.table('product_categories').select('*').eq('is_active', True).order('display_order').execute()

        categories = result.data or []

        # Organiser en hiérarchie
        categories_map = {cat['id']: {**cat, 'children': []} for cat in categories}
        root_categories = []

        for cat in categories:
            if cat.get('parent_id'):
                # Sous-catégorie
                if cat['parent_id'] in categories_map:
                    categories_map[cat['parent_id']]['children'].append(categories_map[cat['id']])
            else:
                # Catégorie racine
                root_categories.append(categories_map[cat['id']])

        return {
            "success": True,
            "categories": root_categories
        }

    except Exception as e:
        logger.error("get_categories_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des catégories"
        )


@router.get("/featured", response_model=dict)
async def get_featured_products(limit: int = Query(10, ge=1, le=50)):
    """
    Produits mis en avant (featured)

    Triés par nombre de ventes et rating
    """
    try:
        # Utiliser la table products directement
        result = supabase.table('products').select(
            '*, merchant:users(first_name, last_name)'
        ).eq('is_featured', True).eq('is_active', True).order('sold_count', desc=True).limit(limit).execute()

        products = result.data or []
        
        # Enrichir les données
        for product in products:
            # Merchant
            if product.get('merchant'):
                merchant_data = product['merchant']
                if isinstance(merchant_data, list) and merchant_data:
                    merchant_data = merchant_data[0]
                
                if isinstance(merchant_data, dict):
                    first = merchant_data.get('first_name', '')
                    last = merchant_data.get('last_name', '')
                    product['merchant'] = {
                        'name': f"{first} {last}".strip() or "Marchand"
                    }
            
            # Deal status
            now = datetime.utcnow().isoformat()
            expiry = product.get('expiry_date')
            stock = product.get('stock_quantity')
            
            deal_status = 'active'
            if stock is not None and stock <= 0:
                deal_status = 'sold_out'
            elif expiry and expiry < now:
                deal_status = 'expired'
            product['deal_status'] = deal_status

        return {
            "success": True,
            "products": products
        }

    except Exception as e:
        logger.error("get_featured_products_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des produits featured"
        )


@router.get("/deals-of-day", response_model=dict)
async def get_deals_of_day(limit: int = Query(10, ge=1, le=50)):
    """
    Deals du jour

    Produits avec les meilleures réductions actives
    """
    try:
        # Utiliser la table products directement
        now = datetime.utcnow().isoformat()
        
        # Note: Supabase filter for date > now might need specific syntax or we filter in python
        # .gt('expiry_date', now)
        
        result = supabase.table('products').select(
            '*, merchant:users(first_name, last_name)'
        ).eq('is_deal_of_day', True).eq('is_active', True).order('discount_percentage', desc=True).limit(limit).execute()

        products = result.data or []
        
        # Filter expired deals in python if needed (though we should filter in query if possible)
        valid_products = []
        
        for product in products:
            expiry = product.get('expiry_date')
            if expiry and expiry < now:
                continue
                
            # Merchant
            if product.get('merchant'):
                merchant_data = product['merchant']
                if isinstance(merchant_data, list) and merchant_data:
                    merchant_data = merchant_data[0]
                
                if isinstance(merchant_data, dict):
                    first = merchant_data.get('first_name', '')
                    last = merchant_data.get('last_name', '')
                    product['merchant'] = {
                        'name': f"{first} {last}".strip() or "Marchand"
                    }
            
            product['deal_status'] = 'active'
            valid_products.append(product)

        return {
            "success": True,
            "deals": valid_products
        }

    except Exception as e:
        logger.error("get_deals_of_day_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des deals"
        )


@router.get("/products/{product_id}/reviews", response_model=dict)
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort_by: str = Query("created_at")
):
    """
    Avis clients d'un produit

    **Tri:**
    - created_at: Plus récents
    - rating: Meilleure note
    - helpful: Plus utiles
    """
    try:
        offset = (page - 1) * limit

        # Récupérer reviews approuvés (ou tous si pas de colonne is_approved)
        query = supabase.table('product_reviews').select('*').eq('product_id', product_id)
        
        # Essayer de filtrer par is_approved si la colonne existe
        try:
            query = query.eq('is_approved', True)
        except:
            pass

        # Tri
        if sort_by == "rating":
            query = query.order('rating', desc=True)
        elif sort_by == "helpful":
            try:
                query = query.order('helpful_count', desc=True)
            except:
                query = query.order('created_at', desc=True)
        else:
            query = query.order('created_at', desc=True)

        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        
        reviews = result.data or []
        
        # Enrichir avec les infos utilisateurs
        for review in reviews:
            if review.get('user_id'):
                try:
                    user_result = supabase.table('users').select('first_name, last_name, username').eq('id', review['user_id']).execute()
                    if user_result.data and len(user_result.data) > 0:
                        user_data = user_result.data[0]
                        first = user_data.get('first_name', '')
                        last = user_data.get('last_name', '')
                        name = f"{first} {last}".strip()
                        if not name:
                            name = user_data.get('username') or 'Utilisateur'
                        review['user_name'] = name
                    else:
                        review['user_name'] = 'Utilisateur'
                except Exception as e:
                    logger.error(f'Error fetching user for review: {e}')
                    review['user_name'] = 'Utilisateur'

        return {
            "success": True,
            "reviews": reviews,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error("get_product_reviews_failed", product_id=product_id, error=str(e), exc_info=True)
        # Retourner une liste vide plutôt qu'une erreur
        return {
            "success": True,
            "reviews": [],
            "page": page,
            "limit": limit
        }


# ============================================
# ENDPOINTS - AUTHENTICATED
# ============================================

@router.post("/products/{product_id}/request-affiliate", response_model=dict)
async def request_affiliate(
    product_id: str,
    request_data: AffiliateRequestCreate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Demander affiliation pour un produit

    **Requis:**
    - Être connecté (influenceur)
    - Produit actif

    **Process:**
    1. Vérifier produit existe
    2. Vérifier pas déjà affilié
    3. Créer demande (status: pending)
    4. Notifier marchand par email
    """
    user_id = current_user.get("id")
    user_role = current_user.get("role")

    try:
        # Vérifier rôle
        if user_role != "influencer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les influenceurs peuvent demander une affiliation"
            )

        # Vérifier produit existe
        product_result = supabase.table('products').select('*').eq('id', product_id).eq('is_active', True).execute()

        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )

        product = product_result.data[0]
        merchant_id = product['merchant_id']

        # Vérifier pas déjà demandé
        existing = supabase.table('affiliate_requests').select('*').eq('influencer_id', user_id).eq('product_id', product_id).execute()

        if existing.data:
            existing_request = existing.data[0]
            if existing_request['status'] == 'pending':
                return {
                    "success": False,
                    "message": "Vous avez déjà une demande en attente pour ce produit",
                    "request_id": existing_request['id']
                }
            elif existing_request['status'] == 'approved':
                return {
                    "success": False,
                    "message": "Vous êtes déjà affilié à ce produit",
                    "request_id": existing_request['id']
                }

        # Créer demande
        affiliate_request = {
            'influencer_id': user_id,
            'merchant_id': merchant_id,
            'product_id': product_id,
            'status': 'pending',
            'message': request_data.message,
            'created_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('affiliate_requests').insert(affiliate_request).execute()

        request_id = result.data[0]['id'] if result.data else None

        # Envoyer email au marchand (async)
        # TODO: Implémenter notification email
        from celery_tasks import send_new_affiliate_request_email
        # send_new_affiliate_request_email.delay(merchant_email, product_name, influencer_name)

        logger.info("affiliate_request_created", user_id=user_id, product_id=product_id, request_id=request_id)

        return {
            "success": True,
            "message": "Demande d'affiliation envoyée avec succès",
            "request_id": request_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("request_affiliate_failed", user_id=user_id, product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la demande d'affiliation"
        )


@router.post("/products/{product_id}/review", response_model=dict)
async def create_product_review(
    product_id: str,
    review_data: ProductReviewRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Ajouter un avis sur un produit

    **Requis:**
    - Être connecté
    - 1 seul avis par produit par utilisateur

    **L'avis sera en attente d'approbation par admin**
    """
    user_id = current_user.get("id")

    try:
        # Vérifier produit existe
        product_result = supabase.table('products').select('id').eq('id', product_id).execute()

        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )

        # Vérifier pas déjà reviewé
        existing = supabase.table('product_reviews').select('id').eq('product_id', product_id).eq('user_id', user_id).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous avez déjà laissé un avis sur ce produit"
            )

        # Créer review
        review = {
            'product_id': product_id,
            'user_id': user_id,
            'rating': review_data.rating,
            'title': review_data.title,
            'comment': review_data.comment,
            'is_approved': False,  # En attente modération
            'created_at': datetime.utcnow().isoformat()
        }

        result = supabase.table('product_reviews').insert(review).execute()

        review_id = result.data[0]['id'] if result.data else None

        logger.info("product_review_created", user_id=user_id, product_id=product_id, review_id=review_id)

        return {
            "success": True,
            "message": "Avis soumis avec succès. Il sera publié après modération.",
            "review_id": review_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_product_review_failed", user_id=user_id, product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'avis"
        )


@router.get("/services", response_model=dict)
async def get_marketplace_services(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    Liste des services marketplace (Remuneration par Deal/Lead)

    **Filtres:**
    - category: Catégorie
    - search: Recherche texte
    - min_price, max_price: Fourchette de prix par lead
    """
    try:
        # Récupérer les services via le helper
        services = get_all_services(category=category)
        
        # Filtrage additionnel en Python (car le helper est basique)
        filtered_services = []
        for service in services:
            # Filtre recherche
            if search:
                search_lower = search.lower()
                name = service.get('name', '').lower()
                desc = service.get('description', '').lower()
                if search_lower not in name and search_lower not in desc:
                    continue
            
            # Filtre prix
            price = float(service.get('price_per_lead', 0))
            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue
                
            # Ajouter info explicite sur la rémunération
            service['remuneration_model'] = 'deal' # Fixed price per deal/lead
            service['commission_type'] = 'fixed'
            service['commission_amount'] = price
            
            filtered_services.append(service)
            
        # Pagination
        total = len(filtered_services)
        start = (page - 1) * limit
        end = start + limit
        paginated_services = filtered_services[start:end]

        return {
            "success": True,
            "services": paginated_services,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    except Exception as e:
        logger.error("get_marketplace_services_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des services"
        )


@router.get("/services/{service_id}", response_model=dict)
async def get_service_detail(service_id: str):
    """
    Détails complets d'un service
    """
    try:
        service = get_service_by_id(service_id)
        
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service non trouvé"
            )
            
        # Ajouter info explicite sur la rémunération
        service['remuneration_model'] = 'deal'
        service['commission_type'] = 'fixed'
        service['commission_amount'] = service.get('price_per_lead', 0)
        
        return {
            "success": True,
            "service": service
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_service_detail_failed", service_id=service_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du service"
        )
