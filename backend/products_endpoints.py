from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from auth import get_current_user_from_cookie
from db_helpers import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product,
    get_merchant_by_user_id
)
from utils.logger import logger

router = APIRouter(prefix="/api", tags=["products"])

# ============================================
# MODELS
# ============================================

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "EUR"
    stock: int = 0
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    commission_rate: float = 0.0
    merchant_id: Optional[str] = None  # Admin can specify merchant

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    commission_rate: Optional[float] = None

# ============================================
# ENDPOINTS
# ============================================

@router.get("/products")
async def get_products_endpoint(
    category: Optional[str] = None,
    merchant_id: Optional[str] = None,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer tous les produits avec filtres"""
    try:
        # Si c'est un marchand, on force le filtre sur son ID
        if current_user and current_user.get("role") == "merchant":
            merchant = get_merchant_by_user_id(current_user["id"])
            if merchant:
                merchant_id = merchant["id"]
            else:
                # Si le marchand n'a pas de profil marchand, il ne voit rien
                return []

        products = get_all_products(category, merchant_id)
        return products
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}")
async def get_product_detail_endpoint(
    product_id: str,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Récupérer les détails d'un produit"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produit introuvable")
        
        # Vérification des droits d'accès pour les marchands
        if current_user and current_user.get("role") == "merchant":
            merchant = get_merchant_by_user_id(current_user["id"])
            if merchant and product.get("merchant_id") != merchant["id"]:
                raise HTTPException(status_code=403, detail="Accès refusé")
                
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products")
async def create_product_endpoint(
    product_data: ProductCreate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Créer un nouveau produit"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Non authentifié")
            
        if current_user.get("role") not in ["admin", "merchant"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        
        data = product_data.dict()
        
        # Déterminer le merchant_id
        if current_user.get("role") == "merchant":
            merchant = get_merchant_by_user_id(current_user["id"])
            if not merchant:
                raise HTTPException(status_code=400, detail="Profil marchand introuvable")
            data["merchant_id"] = merchant["id"]
        elif current_user.get("role") == "admin":
            if not data.get("merchant_id"):
                # Admin doit spécifier un merchant_id ou on l'attribue à un compte par défaut?
                # Pour l'instant, on exige un merchant_id si admin
                # Ou on laisse passer si c'est un produit "système" (peu probable ici)
                pass
        
        if not data.get("merchant_id"):
             raise HTTPException(status_code=400, detail="Merchant ID requis")

        new_product = create_product(data)
        
        if not new_product:
            raise HTTPException(status_code=400, detail="Erreur lors de la création du produit")
            
        return new_product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}")
async def update_product_endpoint(
    product_id: str,
    product_data: ProductUpdate,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Mettre à jour un produit"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Non authentifié")
            
        # Vérifier l'existence et les droits
        existing_product = get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Produit introuvable")
            
        if current_user.get("role") == "merchant":
            merchant = get_merchant_by_user_id(current_user["id"])
            if not merchant or existing_product.get("merchant_id") != merchant["id"]:
                raise HTTPException(status_code=403, detail="Accès refusé")
        elif current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
            
        # Filtrer les données None
        update_data = {k: v for k, v in product_data.dict().items() if v is not None}
        
        success = update_product(product_id, update_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la mise à jour")
            
        return get_product_by_id(product_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product_endpoint(
    product_id: str,
    current_user: Dict = Depends(get_current_user_from_cookie)
):
    """Supprimer un produit"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Non authentifié")
            
        # Vérifier l'existence et les droits
        existing_product = get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Produit introuvable")
            
        if current_user.get("role") == "merchant":
            merchant = get_merchant_by_user_id(current_user["id"])
            if not merchant or existing_product.get("merchant_id") != merchant["id"]:
                raise HTTPException(status_code=403, detail="Accès refusé")
        elif current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
            
        success = delete_product(product_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erreur lors de la suppression")
            
        return {"success": True, "message": "Produit supprimé"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))
