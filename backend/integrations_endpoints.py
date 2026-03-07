"""
============================================
INTEGRATIONS ENDPOINTS
GetYourShare - Hub d'Intégrations Tierces
============================================

Endpoints pour intégrations Shopify/WooCommerce/API:
- OAuth flows
- Synchronisation produits
- Webhooks
- Configuration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from auth import get_current_user
from supabase_client import supabase
from utils.logger import logger
import hashlib
import hmac

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])

# ============================================
# PYDANTIC MODELS
# ============================================

class IntegrationConnect(BaseModel):
    """Configuration d'intégration"""
    type: str
    config: Dict[str, Any]

class OAuthInit(BaseModel):
    """Initialisation OAuth"""
    type: str

class WebhookPayload(BaseModel):
    """Webhook payload"""
    event: str
    data: Dict[str, Any]

# ============================================
# SHOPIFY INTEGRATION
# ============================================

class ShopifyIntegration:
    """Gestion intégration Shopify"""
    
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url.rstrip('/')
        self.access_token = access_token
        self.api_version = '2024-01'
    
    async def test_connection(self) -> bool:
        """Test la connexion Shopify"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.shop_url}/admin/api/{self.api_version}/shop.json",
                    headers={"X-Shopify-Access-Token": self.access_token}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Shopify test connection error: {e}")
            return False
    
    async def get_products(self, limit: int = 250) -> List[Dict]:
        """Récupère les produits Shopify"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.shop_url}/admin/api/{self.api_version}/products.json",
                    headers={"X-Shopify-Access-Token": self.access_token},
                    params={"limit": limit}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('products', [])
                return []
        except Exception as e:
            logger.error(f"Shopify get products error: {e}")
            return []
    
    async def create_webhook(self, topic: str, address: str) -> bool:
        """Crée un webhook Shopify"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.shop_url}/admin/api/{self.api_version}/webhooks.json",
                    headers={"X-Shopify-Access-Token": self.access_token},
                    json={
                        "webhook": {
                            "topic": topic,
                            "address": address,
                            "format": "json"
                        }
                    }
                )
                return response.status_code == 201
        except Exception as e:
            logger.error(f"Shopify create webhook error: {e}")
            return False

# ============================================
# WOOCOMMERCE INTEGRATION
# ============================================

class WooCommerceIntegration:
    """Gestion intégration WooCommerce"""
    
    def __init__(self, store_url: str, consumer_key: str, consumer_secret: str):
        self.store_url = store_url.rstrip('/')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
    
    async def test_connection(self) -> bool:
        """Test la connexion WooCommerce"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.store_url}/wp-json/wc/v3/system_status",
                    auth=(self.consumer_key, self.consumer_secret)
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"WooCommerce test connection error: {e}")
            return False
    
    async def get_products(self, per_page: int = 100) -> List[Dict]:
        """Récupère les produits WooCommerce"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.store_url}/wp-json/wc/v3/products",
                    auth=(self.consumer_key, self.consumer_secret),
                    params={"per_page": per_page}
                )
                
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception as e:
            logger.error(f"WooCommerce get products error: {e}")
            return []
    
    async def create_webhook(self, topic: str, delivery_url: str) -> bool:
        """Crée un webhook WooCommerce"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.store_url}/wp-json/wc/v3/webhooks",
                    auth=(self.consumer_key, self.consumer_secret),
                    json={
                        "topic": topic,
                        "delivery_url": delivery_url,
                        "secret": hashlib.sha256(self.consumer_secret.encode()).hexdigest()
                    }
                )
                return response.status_code == 201
        except Exception as e:
            logger.error(f"WooCommerce create webhook error: {e}")
            return False

# ============================================
# ENDPOINTS
# ============================================

@router.get("")
async def get_integrations(
    current_user: Dict = Depends(get_current_user)
):
    """
    Récupère les intégrations de l'utilisateur
    """
    try:
        response = supabase.table('integrations')\
            .select('*')\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {
            'integrations': response.data if response.data else []
        }
    
    except Exception as e:
        logger.error(f"Error fetching integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch integrations: {str(e)}"
        )


@router.post("/oauth/init")
async def init_oauth(
    request: OAuthInit,
    current_user: Dict = Depends(get_current_user)
):
    """
    Initialise le flow OAuth (Shopify)
    """
    try:
        if request.type == 'shopify':
            # TODO: Implémenter OAuth Shopify complet
            # Pour l'instant, retourner URL de test
            auth_url = f"https://example.myshopify.com/admin/oauth/authorize?client_id=YOUR_CLIENT_ID&scope=read_products,write_products&redirect_uri=YOUR_REDIRECT_URI"
            
            return {
                'success': True,
                'auth_url': auth_url
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"OAuth not supported for {request.type}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize OAuth: {str(e)}"
        )


@router.post("/connect", status_code=status.HTTP_201_CREATED)
async def connect_integration(
    request: IntegrationConnect,
    current_user: Dict = Depends(get_current_user)
):
    """
    Connecte une nouvelle intégration
    """
    try:
        # Tester la connexion selon le type
        if request.type == 'woocommerce':
            woo = WooCommerceIntegration(
                request.config.get('store_url'),
                request.config.get('consumer_key'),
                request.config.get('consumer_secret')
            )
            if not await woo.test_connection():
                raise HTTPException(
                    status_code=400,
                    detail="Failed to connect to WooCommerce. Check your credentials."
                )
        
        # Sauvegarder l'intégration
        integration_data = {
            'user_id': current_user['id'],
            'type': request.type,
            'config': request.config,
            'status': 'connected',
            'auto_sync': False,
            'products_count': 0,
            'created_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('integrations').insert(integration_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save integration"
            )
        
        return {
            'success': True,
            'message': 'Integration connected successfully',
            'integration': response.data[0]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect integration: {str(e)}"
        )


@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Test la connexion d'une intégration
    """
    try:
        # Récupérer l'intégration
        response = supabase.table('integrations')\
            .select('*')\
            .eq('id', integration_id)\
            .eq('user_id', current_user['id'])\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration = response.data
        success = False
        
        # Tester selon le type
        if integration['type'] == 'shopify':
            shopify = ShopifyIntegration(
                integration['config'].get('shop_url'),
                integration['config'].get('access_token')
            )
            success = await shopify.test_connection()
        
        elif integration['type'] == 'woocommerce':
            woo = WooCommerceIntegration(
                integration['config'].get('store_url'),
                integration['config'].get('consumer_key'),
                integration['config'].get('consumer_secret')
            )
            success = await woo.test_connection()
        
        # Mettre à jour le statut
        supabase.table('integrations').update({
            'status': 'connected' if success else 'error',
            'last_test': datetime.utcnow().isoformat()
        }).eq('id', integration_id).execute()
        
        return {
            'success': success,
            'message': 'Connection successful' if success else 'Connection failed'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test integration: {str(e)}"
        )


@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Synchronise les produits depuis l'intégration
    """
    try:
        # Récupérer l'intégration
        response = supabase.table('integrations')\
            .select('*')\
            .eq('id', integration_id)\
            .eq('user_id', current_user['id'])\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration = response.data
        synced_count = 0
        
        # Synchroniser selon le type
        if integration['type'] == 'shopify':
            shopify = ShopifyIntegration(
                integration['config'].get('shop_url'),
                integration['config'].get('access_token')
            )
            products = await shopify.get_products()
            
            # Importer les produits
            for product in products:
                product_data = {
                    'user_id': current_user['id'],
                    'name': product.get('title'),
                    'description': product.get('body_html'),
                    'price': float(product['variants'][0].get('price', 0)) if product.get('variants') else 0,
                    'image': product['images'][0].get('src') if product.get('images') else None,
                    'external_id': product.get('id'),
                    'external_source': 'shopify',
                    'in_stock': True,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                # Insérer ou mettre à jour
                supabase.table('products').upsert(product_data, on_conflict='external_id').execute()
                synced_count += 1
        
        elif integration['type'] == 'woocommerce':
            woo = WooCommerceIntegration(
                integration['config'].get('store_url'),
                integration['config'].get('consumer_key'),
                integration['config'].get('consumer_secret')
            )
            products = await woo.get_products()
            
            # Importer les produits
            for product in products:
                product_data = {
                    'user_id': current_user['id'],
                    'name': product.get('name'),
                    'description': product.get('description'),
                    'price': float(product.get('price', 0)),
                    'image': product['images'][0].get('src') if product.get('images') else None,
                    'external_id': str(product.get('id')),
                    'external_source': 'woocommerce',
                    'in_stock': product.get('stock_status') == 'instock',
                    'created_at': datetime.utcnow().isoformat()
                }
                
                supabase.table('products').upsert(product_data, on_conflict='external_id').execute()
                synced_count += 1
        
        # Mettre à jour l'intégration
        supabase.table('integrations').update({
            'products_count': synced_count,
            'last_sync': datetime.utcnow().isoformat(),
            'status': 'connected'
        }).eq('id', integration_id).execute()
        
        return {
            'success': True,
            'synced_count': synced_count,
            'message': f'{synced_count} products synchronized'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync integration: {str(e)}"
        )


@router.patch("/{integration_id}/auto-sync")
async def toggle_auto_sync(
    integration_id: str,
    enabled: bool,
    current_user: Dict = Depends(get_current_user)
):
    """
    Active/désactive la synchronisation automatique
    """
    try:
        response = supabase.table('integrations')\
            .update({'auto_sync': enabled})\
            .eq('id', integration_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {
            'success': True,
            'message': f'Auto-sync {"enabled" if enabled else "disabled"}'
        }
    
    except Exception as e:
        logger.error(f"Error toggling auto-sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle auto-sync: {str(e)}"
        )


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Supprime une intégration
    """
    try:
        response = supabase.table('integrations')\
            .delete()\
            .eq('id', integration_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {
            'success': True,
            'message': 'Integration deleted successfully'
        }
    
    except Exception as e:
        logger.error(f"Error deleting integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete integration: {str(e)}"
        )


@router.post("/webhook/{integration_type}")
async def handle_webhook(
    integration_type: str,
    request: Request
):
    """
    Gère les webhooks entrants des intégrations
    """
    try:
        body = await request.body()
        headers = request.headers

        # Vérifier la signature du webhook (Shopify / WooCommerce)
        if integration_type == "shopify":
            shopify_secret = __import__("os").getenv("SHOPIFY_WEBHOOK_SECRET", "")
            if shopify_secret:
                sig_header = headers.get("X-Shopify-Hmac-Sha256", "")
                import base64
                expected = base64.b64encode(
                    hmac.new(shopify_secret.encode(), body, hashlib.sha256).digest()
                ).decode()
                if not hmac.compare_digest(expected, sig_header):
                    raise HTTPException(status_code=401, detail="Invalid Shopify webhook signature")

        elif integration_type == "woocommerce":
            woo_secret = __import__("os").getenv("WOOCOMMERCE_WEBHOOK_SECRET", "")
            if woo_secret:
                sig_header = headers.get("X-WC-Webhook-Signature", "")
                import base64
                expected = base64.b64encode(
                    hmac.new(woo_secret.encode(), body, hashlib.sha256).digest()
                ).decode()
                if not hmac.compare_digest(expected, sig_header):
                    raise HTTPException(status_code=401, detail="Invalid WooCommerce webhook signature")

        # Parser et traiter les événements
        import json as _json
        try:
            payload = _json.loads(body)
        except Exception:
            payload = {}

        event_type = (
            headers.get("X-Shopify-Topic")
            or headers.get("X-WC-Webhook-Topic")
            or payload.get("event")
            or "unknown"
        )
        logger.info(f"Webhook received from {integration_type}: {event_type}")

        # Enregistrer le webhook en DB
        try:
            supabase.table("webhook_logs").insert({
                "integration_type": integration_type,
                "event_type": event_type,
                "payload": payload,
                "status": "received",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception:
            pass

        # Traiter les événements selon le type
        if integration_type == "shopify" and event_type == "orders/create":
            order_id = payload.get("id")
            if order_id:
                try:
                    supabase.table("integrations").update({
                        "last_event_at": datetime.utcnow().isoformat(),
                        "last_event_type": event_type
                    }).eq("integration_type", "shopify").execute()
                except Exception:
                    pass

        elif integration_type == "shopify" and event_type in ("products/create", "products/update"):
            pass  # Sync produit géré par la tâche Celery

        return {
            'success': True,
            'message': 'Webhook received',
            'event_type': event_type
        }
    
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle webhook: {str(e)}"
        )
