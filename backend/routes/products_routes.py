"""
Routes Products COMPLÈTES avec vraie logique
Remplace les stubs de missing_endpoints.py pour les produits
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import csv
import io
from decimal import Decimal

from auth import get_current_user_from_cookie
from db_helpers import supabase

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/products", tags=["Products"])


# ============================================
# MODELS
# ============================================

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "MAD"
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    sku: Optional[str] = None
    commission_rate: Optional[float] = None
    is_active: bool = True
    metadata: Optional[Dict] = {}


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    sku: Optional[str] = None
    commission_rate: Optional[float] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict] = None


class ProductVariant(BaseModel):
    name: str
    sku: str
    price: float
    stock_quantity: int = 0
    attributes: Dict  # Ex: {"color": "red", "size": "L"}


# ============================================
# CRUD ENDPOINTS
# ============================================

@router.get("")
async def get_products(
    limit: int = 20,
    offset: int = 0,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des produits avec filtres RÉELS
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Query de base
        query = supabase.table("products").select("*", count="exact")

        # Filtre par merchant (sauf si admin)
        if role != "admin":
            query = query.eq("merchant_id", user_id)

        # Filtres optionnels
        if category:
            query = query.eq("category", category)

        if is_active is not None:
            query = query.eq("is_active", is_active)

        # Search
        if search:
            query = query.ilike("name", f"%{search}%")

        # Pagination
        query = query.range(offset, offset + limit - 1)

        # Order by created_at DESC
        query = query.order("created_at", desc=True)

        response = query.execute()

        return {
            "success": True,
            "products": response.data or [],
            "total": response.count if hasattr(response, 'count') else len(response.data or []),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_products(
    limit: int = 10,
    period: str = "7d"
):
    """
    Produits tendance RÉELS (basé sur conversions)
    """
    try:
        # Calculer la date de début
        from datetime import timedelta
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        else:
            days = 7

        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Récupérer les conversions récentes groupées par produit
        conversions = supabase.table('conversions').select('product_id, sale_amount').gte('created_at', start_date).execute()

        # Grouper par produit
        product_stats = {}
        for conv in (conversions.data or []):
            product_id = conv.get('product_id')
            if not product_id:
                continue

            if product_id not in product_stats:
                product_stats[product_id] = {
                    'sales_count': 0,
                    'total_revenue': Decimal('0')
                }

            product_stats[product_id]['sales_count'] += 1
            product_stats[product_id]['total_revenue'] += Decimal(str(conv.get('sale_amount', 0)))

        # Trier par nombre de ventes
        sorted_products = sorted(
            product_stats.items(),
            key=lambda x: x[1]['sales_count'],
            reverse=True
        )[:limit]

        # Récupérer les infos produits
        result = []
        for product_id, stats in sorted_products:
            try:
            product = supabase.table('products').select('*').eq('id', product_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            if product.data:
                result.append({
                    **product.data,
                    'trending_sales': stats['sales_count'],
                    'trending_revenue': float(stats['total_revenue'])
                })

        return {
            "success": True,
            "products": result,
            "period": period
        }

    except Exception as e:
        logger.error(f"Error getting trending products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}")
async def get_product_details(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Détails complets d'un produit
    """
    try:
        response = supabase.table("products").select("*").eq("id", product_id).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        # Récupérer aussi les stats de conversion pour ce produit
        conversions = supabase.table('conversions').select('*', count='exact').eq('product_id', product_id).execute()
        total_sales = conversions.count if hasattr(conversions, 'count') else len(conversions.data or [])

        conversions_data = conversions.data or []
        total_revenue = sum(Decimal(str(c.get('sale_amount', 0))) for c in conversions_data)

        product_data = response.data
        product_data['stats'] = {
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'currency': product_data.get('currency', 'MAD')
        }

        return {
            "success": True,
            **product_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_product(
    product: ProductCreate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer un nouveau produit
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # SECURITY: Only merchants can create products
        if role != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only merchants can create products. Influencers and commercials cannot add products."
            )

        product_data = product.dict()
        product_data['merchant_id'] = user_id

        response = supabase.table("products").insert(product_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création du produit")

        return {
            "success": True,
            "product": response.data[0],
            "message": "Produit créé avec succès"
        }

    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    product: ProductUpdate,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre à jour un produit
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier que le produit appartient au merchant (sauf admin)
        if role != "admin":
            existing = supabase.table("products").select("merchant_id").eq("id", product_id).single().execute()
            if not existing.data or existing.data.get('merchant_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

        # Mettre à jour (seulement les champs non-None)
        update_data = {k: v for k, v in product.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        response = supabase.table("products").update(update_data).eq("id", product_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        return {
            "success": True,
            "product": response.data[0],
            "message": "Produit mis à jour"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Supprimer un produit (soft delete: is_active = False)
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier que le produit appartient au merchant (sauf admin)
        if role != "admin":
            existing = supabase.table("products").select("merchant_id").eq("id", product_id).single().execute()
            if not existing.data or existing.data.get('merchant_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

        # Soft delete
        response = supabase.table("products").update({"is_active": False}).eq("id", product_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        return {
            "success": True,
            "message": "Produit désactivé"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# BULK IMPORT
# ============================================

@router.post("/bulk-import")
async def bulk_import_products(
    file: UploadFile = File(...),
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Import en masse de produits via CSV RÉEL

    Format CSV attendu:
    name,description,price,currency,category,sku,commission_rate,stock_quantity

    Exemple:
    "Product 1","Description",100.0,MAD,electronics,SKU-001,10.0,50
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # SECURITY: Only merchants can bulk import products
        if role != "merchant":
            raise HTTPException(
                status_code=403,
                detail="Only merchants can bulk import products"
            )

        # Lire le fichier CSV
        contents = await file.read()
        csv_data = contents.decode('utf-8')

        # Parser le CSV
        csv_reader = csv.DictReader(io.StringIO(csv_data))

        products_to_insert = []
        errors = []
        line_number = 1

        for row in csv_reader:
            line_number += 1

            try:
                # Valider les champs requis
                if not row.get('name') or not row.get('price'):
                    errors.append(f"Ligne {line_number}: name et price sont requis")
                    continue

                product_data = {
                    'merchant_id': user_id,
                    'name': row['name'],
                    'description': row.get('description', ''),
                    'price': float(row['price']),
                    'currency': row.get('currency', 'MAD'),
                    'category': row.get('category'),
                    'sku': row.get('sku'),
                    'commission_rate': float(row['commission_rate']) if row.get('commission_rate') else None,
                    'stock_quantity': int(row['stock_quantity']) if row.get('stock_quantity') else None,
                    'is_active': True
                }

                products_to_insert.append(product_data)

            except ValueError as e:
                errors.append(f"Ligne {line_number}: Erreur de format - {str(e)}")
                continue
            except Exception as e:
                errors.append(f"Ligne {line_number}: {str(e)}")
                continue

        # Insérer en base de données
        inserted_count = 0
        if products_to_insert:
            try:
                response = supabase.table("products").insert(products_to_insert).execute()
                inserted_count = len(response.data) if response.data else 0
            except Exception as e:
                errors.append(f"Erreur d'insertion en base: {str(e)}")

        return {
            "success": True,
            "imported": inserted_count,
            "total_lines": line_number - 1,
            "errors": errors,
            "message": f"{inserted_count} produits importés avec succès"
        }

    except Exception as e:
        logger.error(f"Error bulk importing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# VARIANTS
# ============================================

@router.get("/{product_id}/variants")
async def get_product_variants(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Récupérer les variantes d'un produit RÉEL
    """
    try:
        # Vérifier si la table product_variants existe, sinon utiliser metadata
        try:
            response = supabase.table('product_variants').select('*').eq('product_id', product_id).execute()
            variants = response.data or []
        except Exception:
            # Fallback: chercher dans metadata du produit
            try:
            product = supabase.table('products').select('metadata').eq('id', product_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            if product.data and product.data.get('metadata'):
                metadata = product.data['metadata']
                if isinstance(metadata, dict):
                    variants = metadata.get('variants', [])
                else:
                    variants = []
            else:
                variants = []

        return {
            "success": True,
            "product_id": product_id,
            "variants": variants
        }

    except Exception as e:
        logger.error(f"Error getting product variants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}/variants")
async def create_product_variant(
    product_id: str,
    variant: ProductVariant,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Créer une variante de produit
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier que le produit appartient au merchant
        if role != "admin":
            product = supabase.table("products").select("merchant_id").eq("id", product_id).single().execute()
            if not product.data or product.data.get('merchant_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

        # Essayer d'insérer dans product_variants, sinon dans metadata
        variant_data = variant.dict()
        variant_data['product_id'] = product_id

        try:
            response = supabase.table('product_variants').insert(variant_data).execute()
            created_variant = response.data[0] if response.data else variant_data
        except Exception:
            # Fallback: ajouter dans metadata
            try:
            product = supabase.table('products').select('metadata').eq('id', product_id).single().execute()
            except Exception:
                pass  # .single() might return no results

            metadata = product.data.get('metadata', {}) if product.data else {}
            if not isinstance(metadata, dict):
                metadata = {}

            if 'variants' not in metadata:
                metadata['variants'] = []

            metadata['variants'].append(variant_data)

            supabase.table('products').update({'metadata': metadata}).eq('id', product_id).execute()
            created_variant = variant_data

        return {
            "success": True,
            "variant": created_variant,
            "message": "Variante créée"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product variant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# INVENTORY
# ============================================

@router.get("/{product_id}/inventory")
async def get_product_inventory(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Inventaire d'un produit RÉEL
    """
    try:
        product = supabase.table("products").select("stock_quantity, name").eq("id", product_id).single().execute()

        if not product.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        stock_quantity = product.data.get('stock_quantity', 0) or 0

        # Déterminer le statut
        if stock_quantity == 0:
            status = "out_of_stock"
        elif stock_quantity < 10:
            status = "low_stock"
        else:
            status = "in_stock"

        return {
            "success": True,
            "product_id": product_id,
            "product_name": product.data.get('name'),
            "quantity": stock_quantity,
            "status": status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}/inventory")
async def update_product_inventory(
    product_id: str,
    quantity: int,
    operation: str = "set",  # set, add, subtract
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre à jour l'inventaire d'un produit

    Operations:
    - set: Définir la quantité exacte
    - add: Ajouter à la quantité actuelle
    - subtract: Soustraire de la quantité actuelle
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier permissions
        if role != "admin":
            product = supabase.table("products").select("merchant_id, stock_quantity").eq("id", product_id).single().execute()
            if not product.data or product.data.get('merchant_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

            current_quantity = product.data.get('stock_quantity', 0) or 0
        else:
            try:
            product = supabase.table("products").select("stock_quantity").eq("id", product_id).single().execute()
            except Exception:
                pass  # .single() might return no results
            if not product.data:
                raise HTTPException(status_code=404, detail="Produit non trouvé")
            current_quantity = product.data.get('stock_quantity', 0) or 0

        # Calculer nouvelle quantité
        if operation == "set":
            new_quantity = quantity
        elif operation == "add":
            new_quantity = current_quantity + quantity
        elif operation == "subtract":
            new_quantity = max(0, current_quantity - quantity)
        else:
            raise HTTPException(status_code=400, detail="Operation invalide (set, add, subtract)")

        # Mettre à jour
        response = supabase.table("products").update({"stock_quantity": new_quantity}).eq("id", product_id).execute()

        return {
            "success": True,
            "product_id": product_id,
            "old_quantity": current_quantity,
            "new_quantity": new_quantity,
            "operation": operation
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PRICING
# ============================================

@router.get("/{product_id}/pricing")
async def get_product_pricing(
    product_id: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Informations de prix d'un produit
    """
    try:
        product = supabase.table("products").select("price, currency, commission_rate").eq("id", product_id).single().execute()

        if not product.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        price = product.data.get('price', 0)
        currency = product.data.get('currency', 'MAD')
        commission_rate = product.data.get('commission_rate', 0) or 0

        # Calculer la commission
        commission_amount = (price * commission_rate) / 100 if commission_rate else 0

        return {
            "success": True,
            "product_id": product_id,
            "price": price,
            "currency": currency,
            "commission_rate": commission_rate,
            "commission_amount": commission_amount,
            "merchant_receives": price - commission_amount
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}/pricing")
async def update_product_pricing(
    product_id: str,
    price: Optional[float] = None,
    commission_rate: Optional[float] = None,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Mettre à jour le prix ou la commission
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        # Vérifier permissions
        if role != "admin":
            product = supabase.table("products").select("merchant_id").eq("id", product_id).single().execute()
            if not product.data or product.data.get('merchant_id') != user_id:
                raise HTTPException(status_code=403, detail="Non autorisé")

        # Préparer mise à jour
        update_data = {}
        if price is not None:
            update_data['price'] = price
        if commission_rate is not None:
            update_data['commission_rate'] = commission_rate

        if not update_data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        # Mettre à jour
        response = supabase.table("products").update(update_data).eq("id", product_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        return {
            "success": True,
            "product": response.data[0],
            "message": "Prix mis à jour"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
