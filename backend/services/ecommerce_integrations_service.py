"""
Service d'intégrations E-commerce
Shopify, WooCommerce, PrestaShop, Magento

Synchronisation bidirectionnelle des produits, commandes, inventaire
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import json
import hmac
import hashlib
import base64
from decimal import Decimal

import logging
logger = logging.getLogger(__name__)


class EcommerceIntegrationsService:
    """
    Service pour gérer les intégrations avec les plateformes e-commerce
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    # ============================================
    # SHOPIFY INTEGRATION
    # ============================================

    def connect_shopify(
        self,
        user_id: str,
        shop_url: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Connecter un store Shopify

        Args:
            user_id: ID du merchant
            shop_url: URL du shop (ex: mystore.myshopify.com)
            access_token: Token d'accès Shopify API

        Returns:
            Dict avec les infos de connexion
        """
        try:
            # Nettoyer l'URL
            if not shop_url.endswith('.myshopify.com'):
                shop_url = f"{shop_url}.myshopify.com"

            # Tester la connexion
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            test_url = f"https://{shop_url}/admin/api/2024-01/shop.json"
            response = requests.get(test_url, headers=headers, timeout=10)

            if response.status_code != 200:
                raise Exception(f"Connexion Shopify échouée: {response.text}")

            shop_data = response.json().get('shop', {})

            # Sauvegarder la connexion
            integration_data = {
                'user_id': user_id,
                'platform': 'shopify',
                'shop_url': shop_url,
                'access_token': access_token,
                'shop_name': shop_data.get('name'),
                'shop_email': shop_data.get('email'),
                'currency': shop_data.get('currency'),
                'status': 'connected',
                'connected_at': datetime.now().isoformat(),
                'metadata': {
                    'shop_id': shop_data.get('id'),
                    'domain': shop_data.get('domain'),
                    'country': shop_data.get('country_name')
                }
            }

            # Insérer ou mettre à jour
            existing = self.supabase.table('ecommerce_integrations').select('id').eq('user_id', user_id).eq('platform', 'shopify').execute()

            if existing.data:
                result = self.supabase.table('ecommerce_integrations').update(integration_data).eq('user_id', user_id).eq('platform', 'shopify').execute()
            else:
                result = self.supabase.table('ecommerce_integrations').insert(integration_data).execute()

            return {
                'success': True,
                'platform': 'shopify',
                'shop_name': shop_data.get('name'),
                'connected': True,
                'integration': result.data[0] if result.data else integration_data
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Shopify connection error: {e}")
            raise Exception(f"Erreur de connexion Shopify: {str(e)}")
        except Exception as e:
            logger.error(f"Shopify integration error: {e}")
            raise

    def sync_shopify_products(self, user_id: str) -> Dict[str, Any]:
        """
        Synchroniser les produits Shopify → GetYourShare
        """
        try:
            # Récupérer les credentials
            integration = self.supabase.table('ecommerce_integrations').select('*').eq('user_id', user_id).eq('platform', 'shopify').single().execute()

            if not integration.data:
                raise Exception("Shopify non connecté")

            shop_url = integration.data['shop_url']
            access_token = integration.data['access_token']

            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }

            # Récupérer les produits Shopify
            products_url = f"https://{shop_url}/admin/api/2024-01/products.json"
            response = requests.get(products_url, headers=headers, timeout=30)

            if response.status_code != 200:
                raise Exception(f"Erreur Shopify API: {response.text}")

            shopify_products = response.json().get('products', [])

            # Synchroniser dans notre DB
            synced_count = 0
            errors = []

            for sp in shopify_products:
                try:
                    # Mapper les champs Shopify → nos champs
                    product_data = {
                        'merchant_id': user_id,
                        'name': sp.get('title'),
                        'description': sp.get('body_html', ''),
                        'price': float(sp.get('variants', [{}])[0].get('price', 0)),
                        'currency': 'USD',  # Shopify par défaut
                        'sku': sp.get('variants', [{}])[0].get('sku'),
                        'image_url': sp.get('images', [{}])[0].get('src') if sp.get('images') else None,
                        'stock_quantity': sp.get('variants', [{}])[0].get('inventory_quantity', 0),
                        'is_active': sp.get('status') == 'active',
                        'metadata': {
                            'shopify_id': sp.get('id'),
                            'shopify_handle': sp.get('handle'),
                            'product_type': sp.get('product_type'),
                            'vendor': sp.get('vendor')
                        }
                    }

                    # Vérifier si le produit existe déjà (via shopify_id)
                    existing = self.supabase.table('products').select('id').eq('merchant_id', user_id).filter('metadata->>shopify_id', 'eq', str(sp.get('id'))).execute()

                    if existing.data:
                        # Update
                        self.supabase.table('products').update(product_data).eq('id', existing.data[0]['id']).execute()
                    else:
                        # Insert
                        self.supabase.table('products').insert(product_data).execute()

                    synced_count += 1

                except Exception as e:
                    errors.append(f"Produit {sp.get('title')}: {str(e)}")
                    logger.error(f"Error syncing product {sp.get('id')}: {e}")

            return {
                'success': True,
                'platform': 'shopify',
                'total_products': len(shopify_products),
                'synced': synced_count,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Shopify sync error: {e}")
            raise

    # ============================================
    # WOOCOMMERCE INTEGRATION
    # ============================================

    def connect_woocommerce(
        self,
        user_id: str,
        site_url: str,
        consumer_key: str,
        consumer_secret: str
    ) -> Dict[str, Any]:
        """
        Connecter un store WooCommerce

        Args:
            user_id: ID du merchant
            site_url: URL du site WordPress/WooCommerce
            consumer_key: Clé API WooCommerce
            consumer_secret: Secret API WooCommerce
        """
        try:
            # Nettoyer l'URL
            site_url = site_url.rstrip('/')

            # Tester la connexion
            from requests.auth import HTTPBasicAuth

            test_url = f"{site_url}/wp-json/wc/v3/system_status"
            auth = HTTPBasicAuth(consumer_key, consumer_secret)

            response = requests.get(test_url, auth=auth, timeout=10)

            if response.status_code != 200:
                raise Exception(f"Connexion WooCommerce échouée: {response.text}")

            system_data = response.json()

            # Sauvegarder la connexion
            integration_data = {
                'user_id': user_id,
                'platform': 'woocommerce',
                'site_url': site_url,
                'consumer_key': consumer_key,
                'consumer_secret': consumer_secret,
                'status': 'connected',
                'connected_at': datetime.now().isoformat(),
                'metadata': {
                    'environment': system_data.get('environment', {}),
                    'wc_version': system_data.get('environment', {}).get('version')
                }
            }

            # Insérer ou mettre à jour
            existing = self.supabase.table('ecommerce_integrations').select('id').eq('user_id', user_id).eq('platform', 'woocommerce').execute()

            if existing.data:
                result = self.supabase.table('ecommerce_integrations').update(integration_data).eq('user_id', user_id).eq('platform', 'woocommerce').execute()
            else:
                result = self.supabase.table('ecommerce_integrations').insert(integration_data).execute()

            return {
                'success': True,
                'platform': 'woocommerce',
                'site_url': site_url,
                'connected': True,
                'integration': result.data[0] if result.data else integration_data
            }

        except Exception as e:
            logger.error(f"WooCommerce connection error: {e}")
            raise

    def sync_woocommerce_products(self, user_id: str) -> Dict[str, Any]:
        """
        Synchroniser les produits WooCommerce → GetYourShare
        """
        try:
            from requests.auth import HTTPBasicAuth

            # Récupérer les credentials
            integration = self.supabase.table('ecommerce_integrations').select('*').eq('user_id', user_id).eq('platform', 'woocommerce').single().execute()

            if not integration.data:
                raise Exception("WooCommerce non connecté")

            site_url = integration.data['site_url']
            consumer_key = integration.data['consumer_key']
            consumer_secret = integration.data['consumer_secret']

            auth = HTTPBasicAuth(consumer_key, consumer_secret)

            # Récupérer les produits
            products_url = f"{site_url}/wp-json/wc/v3/products"
            response = requests.get(products_url, auth=auth, params={'per_page': 100}, timeout=30)

            if response.status_code != 200:
                raise Exception(f"Erreur WooCommerce API: {response.text}")

            wc_products = response.json()

            # Synchroniser
            synced_count = 0
            errors = []

            for wp in wc_products:
                try:
                    product_data = {
                        'merchant_id': user_id,
                        'name': wp.get('name'),
                        'description': wp.get('description', ''),
                        'price': float(wp.get('price', 0)),
                        'currency': 'USD',
                        'sku': wp.get('sku'),
                        'image_url': wp.get('images', [{}])[0].get('src') if wp.get('images') else None,
                        'stock_quantity': wp.get('stock_quantity', 0),
                        'is_active': wp.get('status') == 'publish',
                        'metadata': {
                            'woocommerce_id': wp.get('id'),
                            'permalink': wp.get('permalink'),
                            'categories': [c.get('name') for c in wp.get('categories', [])]
                        }
                    }

                    # Vérifier si existe
                    existing = self.supabase.table('products').select('id').eq('merchant_id', user_id).filter('metadata->>woocommerce_id', 'eq', str(wp.get('id'))).execute()

                    if existing.data:
                        self.supabase.table('products').update(product_data).eq('id', existing.data[0]['id']).execute()
                    else:
                        self.supabase.table('products').insert(product_data).execute()

                    synced_count += 1

                except Exception as e:
                    errors.append(f"Produit {wp.get('name')}: {str(e)}")
                    logger.error(f"Error syncing WC product {wp.get('id')}: {e}")

            return {
                'success': True,
                'platform': 'woocommerce',
                'total_products': len(wc_products),
                'synced': synced_count,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"WooCommerce sync error: {e}")
            raise

    # ============================================
    # PRESTASHOP INTEGRATION
    # ============================================

    def connect_prestashop(
        self,
        user_id: str,
        shop_url: str,
        api_key: str
    ) -> Dict[str, Any]:
        """
        Connecter un store PrestaShop
        """
        try:
            # Nettoyer l'URL
            shop_url = shop_url.rstrip('/')

            # Tester la connexion
            test_url = f"{shop_url}/api"
            response = requests.get(test_url, auth=(api_key, ''), timeout=10)

            if response.status_code != 200:
                raise Exception(f"Connexion PrestaShop échouée: {response.text}")

            # Sauvegarder
            integration_data = {
                'user_id': user_id,
                'platform': 'prestashop',
                'shop_url': shop_url,
                'api_key': api_key,
                'status': 'connected',
                'connected_at': datetime.now().isoformat()
            }

            existing = self.supabase.table('ecommerce_integrations').select('id').eq('user_id', user_id).eq('platform', 'prestashop').execute()

            if existing.data:
                result = self.supabase.table('ecommerce_integrations').update(integration_data).eq('user_id', user_id).eq('platform', 'prestashop').execute()
            else:
                result = self.supabase.table('ecommerce_integrations').insert(integration_data).execute()

            return {
                'success': True,
                'platform': 'prestashop',
                'connected': True,
                'integration': result.data[0] if result.data else integration_data
            }

        except Exception as e:
            logger.error(f"PrestaShop connection error: {e}")
            raise

    # ============================================
    # GENERIC METHODS
    # ============================================

    def disconnect_platform(self, user_id: str, platform: str) -> Dict[str, Any]:
        """
        Déconnecter une plateforme e-commerce
        """
        try:
            result = self.supabase.table('ecommerce_integrations').update({'status': 'disconnected'}).eq('user_id', user_id).eq('platform', platform).execute()

            return {
                'success': True,
                'platform': platform,
                'disconnected': True
            }

        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            raise

    def get_connected_platforms(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Liste des plateformes connectées
        """
        try:
            result = self.supabase.table('ecommerce_integrations').select('platform, shop_url, site_url, status, connected_at').eq('user_id', user_id).eq('status', 'connected').execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Get platforms error: {e}")
            return []

    def sync_orders(self, user_id: str, platform: str) -> Dict[str, Any]:
        """
        Synchroniser les commandes depuis la plateforme
        """
        # TODO: Implémenter sync des commandes
        return {
            'success': True,
            'platform': platform,
            'message': 'Sync des commandes à implémenter'
        }
