"""
Routes E-commerce Integrations
Shopify, WooCommerce, PrestaShop, Magento
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from auth import get_current_user_from_cookie
from db_helpers import supabase
from services.ecommerce_integrations_service import EcommerceIntegrationsService

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ecommerce", tags=["E-commerce Integrations"])

# Initialize service
ecommerce_service = EcommerceIntegrationsService(supabase)


# ============================================
# MODELS
# ============================================

class ShopifyConnect(BaseModel):
    shop_url: str
    access_token: str


class WooCommerceConnect(BaseModel):
    site_url: str
    consumer_key: str
    consumer_secret: str


class PrestaShopConnect(BaseModel):
    shop_url: str
    api_key: str


# ============================================
# SHOPIFY
# ============================================

@router.post("/shopify/connect")
async def connect_shopify(
    data: ShopifyConnect,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Connecter un store Shopify
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        if role != "merchant" and role != "admin":
            raise HTTPException(status_code=403, detail="Merchant uniquement")

        result = ecommerce_service.connect_shopify(
            user_id=user_id,
            shop_url=data.shop_url,
            access_token=data.access_token
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting Shopify: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shopify/sync-products")
async def sync_shopify_products(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Synchroniser les produits Shopify → GetYourShare
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        result = ecommerce_service.sync_shopify_products(user_id)

        return result

    except Exception as e:
        logger.error(f"Error syncing Shopify products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# WOOCOMMERCE
# ============================================

@router.post("/woocommerce/connect")
async def connect_woocommerce(
    data: WooCommerceConnect,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Connecter un store WooCommerce
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        if role != "merchant" and role != "admin":
            raise HTTPException(status_code=403, detail="Merchant uniquement")

        result = ecommerce_service.connect_woocommerce(
            user_id=user_id,
            site_url=data.site_url,
            consumer_key=data.consumer_key,
            consumer_secret=data.consumer_secret
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting WooCommerce: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/woocommerce/sync-products")
async def sync_woocommerce_products(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Synchroniser les produits WooCommerce → GetYourShare
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        result = ecommerce_service.sync_woocommerce_products(user_id)

        return result

    except Exception as e:
        logger.error(f"Error syncing WooCommerce products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PRESTASHOP
# ============================================

@router.post("/prestashop/connect")
async def connect_prestashop(
    data: PrestaShopConnect,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Connecter un store PrestaShop
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")

        if role != "merchant" and role != "admin":
            raise HTTPException(status_code=403, detail="Merchant uniquement")

        result = ecommerce_service.connect_prestashop(
            user_id=user_id,
            shop_url=data.shop_url,
            api_key=data.api_key
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting PrestaShop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GENERIC
# ============================================

@router.get("/connected")
async def get_connected_platforms(
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Liste des plateformes e-commerce connectées
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        platforms = ecommerce_service.get_connected_platforms(user_id)

        return {
            "success": True,
            "platforms": platforms,
            "total": len(platforms)
        }

    except Exception as e:
        logger.error(f"Error getting connected platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{platform}/disconnect")
async def disconnect_platform(
    platform: str,
    payload: dict = Depends(get_current_user_from_cookie)
):
    """
    Déconnecter une plateforme
    """
    try:
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")

        result = ecommerce_service.disconnect_platform(user_id, platform)

        return result

    except Exception as e:
        logger.error(f"Error disconnecting platform: {e}")
        raise HTTPException(status_code=500, detail=str(e))
