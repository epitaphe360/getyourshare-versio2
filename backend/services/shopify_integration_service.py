"""
Shopify Integration Service for ShareYourSales
Complete Shopify API integration for product sync, order tracking, and affiliate management

Dependencies:
    pip install requests

Environment Variables:
    SHOPIFY_SHOP_NAME: Your Shopify shop name (e.g., 'my-shop' for my-shop.myshopify.com)
    SHOPIFY_ACCESS_TOKEN: Shopify Admin API access token
    SHOPIFY_API_VERSION: API version (default: 2024-01)

API Documentation:
    https://shopify.dev/docs/api/admin-rest

Features:
    - OAuth authentication
    - Product synchronization
    - Order management
    - Inventory tracking
    - Customer data
    - Discount codes
    - Webhooks
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hmac
import hashlib
import base64


logger = logging.getLogger(__name__)


class ShopifyIntegrationService:
    """
    Shopify API integration service

    Supports:
    - Product CRUD operations
    - Order management
    - Customer management
    - Discount code generation
    - Inventory tracking
    - Webhook management

    Example:
        service = ShopifyIntegrationService(
            shop_name="my-shop",
            access_token="shpat_..."
        )

        # Get products
        products = service.get_products(limit=50)

        # Create discount code
        discount = service.create_discount_code(
            code="AFFILIATE10",
            percentage=10,
            usage_limit=100
        )

        # Get orders
        orders = service.get_orders(status="any", limit=50)
    """

    def __init__(
        self,
        shop_name: Optional[str] = None,
        access_token: Optional[str] = None,
        api_version: str = "2024-01"
    ):
        """
        Initialize Shopify integration

        Args:
            shop_name: Shopify shop name (without .myshopify.com)
            access_token: Shopify Admin API access token
            api_version: Shopify API version
        """
        self.shop_name = shop_name or os.getenv("SHOPIFY_SHOP_NAME")
        self.access_token = access_token or os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_version = api_version or os.getenv("SHOPIFY_API_VERSION", "2024-01")

        if not self.shop_name or not self.access_token:
            logger.warning("ShopifyIntegrationService: SHOPIFY_SHOP_NAME ou SHOPIFY_ACCESS_TOKEN manquant — service désactivé")
            self.available = False
            self.base_url = None
            return

        self.available = True
        self.base_url = f"https://{self.shop_name}.myshopify.com/admin/api/{self.api_version}"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Shopify API"""
        if not getattr(self, 'available', False):
            raise ValueError("Shopify service is not available: missing SHOPIFY_SHOP_NAME or SHOPIFY_ACCESS_TOKEN")
        url = f"{self.base_url}/{endpoint}"

        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, params=params, json=json_data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, params=params, json=json_data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            # Return empty dict for 204 No Content
            if response.status_code == 204:
                return {"success": True}

            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            logger.error(f"Shopify API error: {error_data}")
            return {
                "success": False,
                "error": error_data.get("errors", str(e))
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== Products =====

    def get_products(
        self,
        limit: int = 50,
        since_id: Optional[str] = None,
        status: str = "active"  # active, archived, draft
    ) -> Dict[str, Any]:
        """
        Get products from Shopify

        Args:
            limit: Number of products (max 250)
            since_id: Restrict results to after specified ID
            status: Product status

        Returns:
            Products data
        """
        params = {
            "limit": min(limit, 250),
            "status": status
        }

        if since_id:
            params["since_id"] = since_id

        result = self._make_request("GET", "products.json", params=params)

        if "products" in result:
            result["success"] = True

        return result

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get single product"""
        result = self._make_request("GET", f"products/{product_id}.json")

        if "product" in result:
            result["success"] = True

        return result

    def create_product(
        self,
        title: str,
        body_html: str,
        vendor: str,
        product_type: str,
        price: float,
        compare_at_price: Optional[float] = None,
        sku: Optional[str] = None,
        inventory_quantity: int = 0,
        images: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new product

        Args:
            title: Product title
            body_html: Product description (HTML)
            vendor: Product vendor/brand
            product_type: Product type
            price: Product price
            compare_at_price: Original price (for sale pricing)
            sku: Stock Keeping Unit
            inventory_quantity: Initial inventory
            images: List of image URLs
            tags: Product tags

        Returns:
            Created product data
        """
        product_data = {
            "product": {
                "title": title,
                "body_html": body_html,
                "vendor": vendor,
                "product_type": product_type,
                "variants": [{
                    "price": str(price),
                    "sku": sku,
                    "inventory_quantity": inventory_quantity,
                    "inventory_management": "shopify"
                }]
            }
        }

        if compare_at_price:
            product_data["product"]["variants"][0]["compare_at_price"] = str(compare_at_price)

        if images:
            product_data["product"]["images"] = [{"src": url} for url in images]

        if tags:
            product_data["product"]["tags"] = ",".join(tags)

        result = self._make_request("POST", "products.json", json_data=product_data)

        if "product" in result:
            result["success"] = True

        return result

    def update_product(
        self,
        product_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update product"""
        product_data = {"product": updates}

        result = self._make_request("PUT", f"products/{product_id}.json", json_data=product_data)

        if "product" in result:
            result["success"] = True

        return result

    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """Delete product"""
        return self._make_request("DELETE", f"products/{product_id}.json")

    # ===== Orders =====

    def get_orders(
        self,
        limit: int = 50,
        status: str = "any",  # open, closed, cancelled, any
        since_id: Optional[str] = None,
        created_at_min: Optional[datetime] = None,
        created_at_max: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get orders from Shopify

        Args:
            limit: Number of orders (max 250)
            status: Order status
            since_id: Restrict results after ID
            created_at_min: Min creation date
            created_at_max: Max creation date

        Returns:
            Orders data
        """
        params = {
            "limit": min(limit, 250),
            "status": status
        }

        if since_id:
            params["since_id"] = since_id

        if created_at_min:
            params["created_at_min"] = created_at_min.isoformat()

        if created_at_max:
            params["created_at_max"] = created_at_max.isoformat()

        result = self._make_request("GET", "orders.json", params=params)

        if "orders" in result:
            result["success"] = True

        return result

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get single order"""
        result = self._make_request("GET", f"orders/{order_id}.json")

        if "order" in result:
            result["success"] = True

        return result

    def create_order(
        self,
        line_items: List[Dict[str, Any]],
        customer: Optional[Dict[str, Any]] = None,
        shipping_address: Optional[Dict[str, Any]] = None,
        discount_codes: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create an order

        Args:
            line_items: List of items [{"variant_id": "...", "quantity": 1}]
            customer: Customer data
            shipping_address: Shipping address
            discount_codes: Discount codes to apply

        Returns:
            Created order data
        """
        order_data = {
            "order": {
                "line_items": line_items
            }
        }

        if customer:
            order_data["order"]["customer"] = customer

        if shipping_address:
            order_data["order"]["shipping_address"] = shipping_address

        if discount_codes:
            order_data["order"]["discount_codes"] = discount_codes

        result = self._make_request("POST", "orders.json", json_data=order_data)

        if "order" in result:
            result["success"] = True

        return result

    # ===== Customers =====

    def get_customers(
        self,
        limit: int = 50,
        since_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get customers"""
        params = {"limit": min(limit, 250)}

        if since_id:
            params["since_id"] = since_id

        result = self._make_request("GET", "customers.json", params=params)

        if "customers" in result:
            result["success"] = True

        return result

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get single customer"""
        result = self._make_request("GET", f"customers/{customer_id}.json")

        if "customer" in result:
            result["success"] = True

        return result

    def search_customers(self, query: str) -> Dict[str, Any]:
        """
        Search customers

        Args:
            query: Search query (e.g., "email:john@example.com")

        Returns:
            Matching customers
        """
        params = {"query": query}

        result = self._make_request("GET", "customers/search.json", params=params)

        if "customers" in result:
            result["success"] = True

        return result

    # ===== Discount Codes =====

    def create_discount_code(
        self,
        code: str,
        value_type: str = "percentage",  # percentage or fixed_amount
        value: float = 10.0,
        usage_limit: Optional[int] = None,
        minimum_order_amount: Optional[float] = None,
        starts_at: Optional[datetime] = None,
        ends_at: Optional[datetime] = None,
        applies_to_product_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create price rule and discount code

        Args:
            code: Discount code
            value_type: Type of discount
            value: Discount value
            usage_limit: Maximum uses
            minimum_order_amount: Minimum purchase amount
            starts_at: Start date
            ends_at: End date
            applies_to_product_ids: Specific products

        Returns:
            Created discount code data
        """
        # Create price rule first
        price_rule_data = {
            "price_rule": {
                "title": f"Affiliate Code: {code}",
                "target_type": "line_item",
                "target_selection": "entitled" if applies_to_product_ids else "all",
                "allocation_method": "across",
                "value_type": value_type,
                "value": f"-{value}",
                "customer_selection": "all",
                "starts_at": (starts_at or datetime.now()).isoformat()
            }
        }

        if usage_limit:
            price_rule_data["price_rule"]["usage_limit"] = usage_limit

        if minimum_order_amount:
            price_rule_data["price_rule"]["prerequisite_subtotal_range"] = {
                "greater_than_or_equal_to": str(minimum_order_amount)
            }

        if ends_at:
            price_rule_data["price_rule"]["ends_at"] = ends_at.isoformat()

        if applies_to_product_ids:
            price_rule_data["price_rule"]["entitled_product_ids"] = applies_to_product_ids

        # Create price rule
        price_rule_result = self._make_request("POST", "price_rules.json", json_data=price_rule_data)

        if "price_rule" not in price_rule_result:
            return price_rule_result

        price_rule_id = price_rule_result["price_rule"]["id"]

        # Create discount code
        discount_code_data = {
            "discount_code": {
                "code": code
            }
        }

        discount_result = self._make_request(
            "POST",
            f"price_rules/{price_rule_id}/discount_codes.json",
            json_data=discount_code_data
        )

        if "discount_code" in discount_result:
            discount_result["success"] = True
            discount_result["price_rule_id"] = price_rule_id

        return discount_result

    def get_discount_codes(self, price_rule_id: str) -> Dict[str, Any]:
        """Get discount codes for a price rule"""
        result = self._make_request("GET", f"price_rules/{price_rule_id}/discount_codes.json")

        if "discount_codes" in result:
            result["success"] = True

        return result

    # ===== Inventory =====

    def get_inventory_levels(
        self,
        inventory_item_ids: Optional[List[str]] = None,
        location_ids: Optional[List[str]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get inventory levels"""
        params = {"limit": min(limit, 250)}

        if inventory_item_ids:
            params["inventory_item_ids"] = ",".join(inventory_item_ids)

        if location_ids:
            params["location_ids"] = ",".join(location_ids)

        result = self._make_request("GET", "inventory_levels.json", params=params)

        if "inventory_levels" in result:
            result["success"] = True

        return result

    def update_inventory(
        self,
        inventory_item_id: str,
        location_id: str,
        available: int
    ) -> Dict[str, Any]:
        """Update inventory quantity"""
        inventory_data = {
            "inventory_item_id": inventory_item_id,
            "location_id": location_id,
            "available": available
        }

        result = self._make_request("POST", "inventory_levels/set.json", json_data=inventory_data)

        if "inventory_level" in result:
            result["success"] = True

        return result

    # ===== Webhooks =====

    def create_webhook(
        self,
        topic: str,
        address: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Create webhook

        Args:
            topic: Webhook topic (e.g., "orders/create", "products/update")
            address: Callback URL
            format: Data format (json or xml)

        Returns:
            Created webhook data
        """
        webhook_data = {
            "webhook": {
                "topic": topic,
                "address": address,
                "format": format
            }
        }

        result = self._make_request("POST", "webhooks.json", json_data=webhook_data)

        if "webhook" in result:
            result["success"] = True

        return result

    def get_webhooks(self) -> Dict[str, Any]:
        """Get all webhooks"""
        result = self._make_request("GET", "webhooks.json")

        if "webhooks" in result:
            result["success"] = True

        return result

    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Delete webhook"""
        return self._make_request("DELETE", f"webhooks/{webhook_id}.json")

    def verify_webhook(
        self,
        data: bytes,
        hmac_header: str,
        secret: str
    ) -> bool:
        """
        Verify webhook HMAC signature

        Args:
            data: Raw request body
            hmac_header: X-Shopify-Hmac-SHA256 header value
            secret: Shopify app secret

        Returns:
            True if valid
        """
        digest = hmac.new(
            secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).digest()

        computed_hmac = base64.b64encode(digest).decode()

        return hmac.compare_digest(computed_hmac, hmac_header)


# ===== Usage Example =====
if __name__ == "__main__":
    service = ShopifyIntegrationService(
        shop_name="my-shop",
        access_token="shpat_..."
    )

    # Get products
    products = service.get_products(limit=10, status="active")
    print("Products:", products)

    # Create discount code
    discount = service.create_discount_code(
        code="AFFILIATE10",
        value_type="percentage",
        value=10.0,
        usage_limit=100
    )
    print("Discount created:", discount)

    # Get orders
    orders = service.get_orders(limit=10, status="any")
    print("Orders:", orders)
