"""
WooCommerce Integration Service for ShareYourSales
Complete WooCommerce REST API integration for WordPress-based stores

Dependencies:
    pip install requests

Environment Variables:
    WOOCOMMERCE_URL: WooCommerce store URL (e.g., https://mystore.com)
    WOOCOMMERCE_CONSUMER_KEY: WooCommerce API consumer key
    WOOCOMMERCE_CONSUMER_SECRET: WooCommerce API consumer secret

API Documentation:
    https://woocommerce.github.io/woocommerce-rest-api-docs/

Features:
    - Product synchronization
    - Order management
    - Customer management
    - Coupon codes (affiliate discounts)
    - Inventory tracking
    - Category management
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from requests.auth import HTTPBasicAuth
import base64


logger = logging.getLogger(__name__)


class WooCommerceIntegrationService:
    """
    WooCommerce REST API integration service

    Supports:
    - Product CRUD operations
    - Order management
    - Customer management
    - Coupon/discount code generation
    - Category management
    - Inventory tracking

    Example:
        service = WooCommerceIntegrationService(
            url="https://mystore.com",
            consumer_key="ck_...",
            consumer_secret="cs_..."
        )

        # Get products
        products = service.get_products(per_page=20)

        # Create coupon
        coupon = service.create_coupon(
            code="AFFILIATE10",
            discount_type="percent",
            amount="10"
        )

        # Get orders
        orders = service.get_orders(status="completed")
    """

    def __init__(
        self,
        url: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        api_version: str = "wc/v3"
    ):
        """
        Initialize WooCommerce integration

        Args:
            url: WooCommerce store URL
            consumer_key: WooCommerce API consumer key
            consumer_secret: WooCommerce API consumer secret
            api_version: API version (default: wc/v3)
        """
        self.url = (url or os.getenv("WOOCOMMERCE_URL", "")).rstrip('/')
        self.consumer_key = consumer_key or os.getenv("WOOCOMMERCE_CONSUMER_KEY")
        self.consumer_secret = consumer_secret or os.getenv("WOOCOMMERCE_CONSUMER_SECRET")
        self.api_version = api_version

        if not self.url or not self.consumer_key or not self.consumer_secret:
            raise ValueError("url, consumer_key, and consumer_secret required")

        self.base_url = f"{self.url}/wp-json/{self.api_version}"
        self.auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to WooCommerce API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, auth=self.auth, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, auth=self.auth, params=params, json=json_data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, auth=self.auth, params=params, json=json_data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, auth=self.auth, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            logger.error(f"WooCommerce API error: {error_data}")
            return {
                "success": False,
                "error": error_data.get("message", str(e)),
                "code": error_data.get("code")
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}

    # ===== Products =====

    def get_products(
        self,
        per_page: int = 20,
        page: int = 1,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: str = "publish",  # publish, draft, pending
        stock_status: Optional[str] = None  # instock, outofstock, onbackorder
    ) -> List[Dict[str, Any]]:
        """
        Get products from WooCommerce

        Args:
            per_page: Number of products per page (max 100)
            page: Page number
            search: Search term
            category: Category ID
            status: Product status
            stock_status: Stock status

        Returns:
            List of products
        """
        params = {
            "per_page": min(per_page, 100),
            "page": page,
            "status": status
        }

        if search:
            params["search"] = search

        if category:
            params["category"] = category

        if stock_status:
            params["stock_status"] = stock_status

        result = self._make_request("GET", "products", params=params)

        if isinstance(result, list):
            return result
        elif "error" in result:
            return []
        else:
            return []

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get single product"""
        return self._make_request("GET", f"products/{product_id}")

    def create_product(
        self,
        name: str,
        type: str = "simple",  # simple, grouped, external, variable
        regular_price: str = "0",
        sale_price: Optional[str] = None,
        description: Optional[str] = None,
        short_description: Optional[str] = None,
        sku: Optional[str] = None,
        stock_quantity: Optional[int] = None,
        manage_stock: bool = False,
        categories: Optional[List[Dict[str, int]]] = None,
        images: Optional[List[Dict[str, str]]] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new product

        Args:
            name: Product name
            type: Product type
            regular_price: Regular price
            sale_price: Sale price
            description: Product description
            short_description: Short description
            sku: Stock Keeping Unit
            stock_quantity: Stock quantity
            manage_stock: Enable stock management
            categories: Categories [{"id": 1}]
            images: Images [{"src": "https://..."}]
            tags: Tags [{"name": "tag1"}]

        Returns:
            Created product data
        """
        product_data = {
            "name": name,
            "type": type,
            "regular_price": regular_price,
            "status": "publish"
        }

        if sale_price:
            product_data["sale_price"] = sale_price

        if description:
            product_data["description"] = description

        if short_description:
            product_data["short_description"] = short_description

        if sku:
            product_data["sku"] = sku

        if manage_stock:
            product_data["manage_stock"] = True
            if stock_quantity is not None:
                product_data["stock_quantity"] = stock_quantity

        if categories:
            product_data["categories"] = categories

        if images:
            product_data["images"] = images

        if tags:
            product_data["tags"] = tags

        result = self._make_request("POST", "products", json_data=product_data)

        if "id" in result:
            result["success"] = True

        return result

    def update_product(
        self,
        product_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update product"""
        result = self._make_request("PUT", f"products/{product_id}", json_data=updates)

        if "id" in result:
            result["success"] = True

        return result

    def delete_product(self, product_id: int, force: bool = False) -> Dict[str, Any]:
        """
        Delete product

        Args:
            product_id: Product ID
            force: Permanently delete (True) or move to trash (False)

        Returns:
            Delete result
        """
        params = {"force": "true" if force else "false"}
        result = self._make_request("DELETE", f"products/{product_id}", params=params)

        if "id" in result:
            result["success"] = True

        return result

    # ===== Orders =====

    def get_orders(
        self,
        per_page: int = 20,
        page: int = 1,
        status: Optional[str] = None,  # pending, processing, on-hold, completed, cancelled, refunded, failed
        customer: Optional[int] = None,
        after: Optional[datetime] = None,
        before: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get orders from WooCommerce

        Args:
            per_page: Number of orders per page
            page: Page number
            status: Order status
            customer: Customer ID
            after: Orders created after this date
            before: Orders created before this date

        Returns:
            List of orders
        """
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        if status:
            params["status"] = status

        if customer:
            params["customer"] = customer

        if after:
            params["after"] = after.isoformat()

        if before:
            params["before"] = before.isoformat()

        result = self._make_request("GET", "orders", params=params)

        if isinstance(result, list):
            return result
        else:
            return []

    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get single order"""
        return self._make_request("GET", f"orders/{order_id}")

    def create_order(
        self,
        line_items: List[Dict[str, Any]],
        customer_id: Optional[int] = None,
        billing: Optional[Dict[str, str]] = None,
        shipping: Optional[Dict[str, str]] = None,
        coupon_lines: Optional[List[Dict[str, str]]] = None,
        payment_method: str = "cod",
        status: str = "pending"
    ) -> Dict[str, Any]:
        """
        Create an order

        Args:
            line_items: Items [{"product_id": 1, "quantity": 1}]
            customer_id: Customer ID
            billing: Billing address
            shipping: Shipping address
            coupon_lines: Coupons [{"code": "COUPON"}]
            payment_method: Payment method
            status: Order status

        Returns:
            Created order data
        """
        order_data = {
            "line_items": line_items,
            "payment_method": payment_method,
            "status": status
        }

        if customer_id:
            order_data["customer_id"] = customer_id

        if billing:
            order_data["billing"] = billing

        if shipping:
            order_data["shipping"] = shipping

        if coupon_lines:
            order_data["coupon_lines"] = coupon_lines

        result = self._make_request("POST", "orders", json_data=order_data)

        if "id" in result:
            result["success"] = True

        return result

    def update_order(
        self,
        order_id: int,
        status: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update order"""
        update_data = updates or {}

        if status:
            update_data["status"] = status

        result = self._make_request("PUT", f"orders/{order_id}", json_data=update_data)

        if "id" in result:
            result["success"] = True

        return result

    # ===== Customers =====

    def get_customers(
        self,
        per_page: int = 20,
        page: int = 1,
        search: Optional[str] = None,
        role: str = "all"
    ) -> List[Dict[str, Any]]:
        """Get customers"""
        params = {
            "per_page": min(per_page, 100),
            "page": page,
            "role": role
        }

        if search:
            params["search"] = search

        result = self._make_request("GET", "customers", params=params)

        if isinstance(result, list):
            return result
        else:
            return []

    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get single customer"""
        return self._make_request("GET", f"customers/{customer_id}")

    def create_customer(
        self,
        email: str,
        first_name: str,
        last_name: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        billing: Optional[Dict[str, str]] = None,
        shipping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create customer"""
        customer_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }

        if username:
            customer_data["username"] = username

        if password:
            customer_data["password"] = password

        if billing:
            customer_data["billing"] = billing

        if shipping:
            customer_data["shipping"] = shipping

        result = self._make_request("POST", "customers", json_data=customer_data)

        if "id" in result:
            result["success"] = True

        return result

    # ===== Coupons (Affiliate Codes) =====

    def create_coupon(
        self,
        code: str,
        discount_type: str = "percent",  # percent, fixed_cart, fixed_product
        amount: str = "10",
        usage_limit: Optional[int] = None,
        usage_limit_per_user: Optional[int] = None,
        minimum_amount: Optional[str] = None,
        maximum_amount: Optional[str] = None,
        product_ids: Optional[List[int]] = None,
        excluded_product_ids: Optional[List[int]] = None,
        date_expires: Optional[datetime] = None,
        individual_use: bool = False,
        free_shipping: bool = False
    ) -> Dict[str, Any]:
        """
        Create coupon/discount code

        Args:
            code: Coupon code
            discount_type: Type of discount
            amount: Discount amount
            usage_limit: Total usage limit
            usage_limit_per_user: Usage limit per user
            minimum_amount: Minimum order amount
            maximum_amount: Maximum order amount
            product_ids: Product IDs this coupon applies to
            excluded_product_ids: Excluded product IDs
            date_expires: Expiration date
            individual_use: Cannot be used with other coupons
            free_shipping: Grant free shipping

        Returns:
            Created coupon data
        """
        coupon_data = {
            "code": code,
            "discount_type": discount_type,
            "amount": amount,
            "individual_use": individual_use,
            "free_shipping": free_shipping
        }

        if usage_limit:
            coupon_data["usage_limit"] = usage_limit

        if usage_limit_per_user:
            coupon_data["usage_limit_per_user"] = usage_limit_per_user

        if minimum_amount:
            coupon_data["minimum_amount"] = minimum_amount

        if maximum_amount:
            coupon_data["maximum_amount"] = maximum_amount

        if product_ids:
            coupon_data["product_ids"] = product_ids

        if excluded_product_ids:
            coupon_data["excluded_product_ids"] = excluded_product_ids

        if date_expires:
            coupon_data["date_expires"] = date_expires.isoformat()

        result = self._make_request("POST", "coupons", json_data=coupon_data)

        if "id" in result:
            result["success"] = True

        return result

    def get_coupons(
        self,
        per_page: int = 20,
        page: int = 1,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get coupons"""
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        if search:
            params["search"] = search

        result = self._make_request("GET", "coupons", params=params)

        if isinstance(result, list):
            return result
        else:
            return []

    def get_coupon(self, coupon_id: int) -> Dict[str, Any]:
        """Get single coupon"""
        return self._make_request("GET", f"coupons/{coupon_id}")

    def delete_coupon(self, coupon_id: int, force: bool = True) -> Dict[str, Any]:
        """Delete coupon"""
        params = {"force": "true" if force else "false"}
        result = self._make_request("DELETE", f"coupons/{coupon_id}", params=params)

        if "id" in result:
            result["success"] = True

        return result

    # ===== Categories =====

    def get_product_categories(
        self,
        per_page: int = 20,
        page: int = 1,
        parent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get product categories"""
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        if parent is not None:
            params["parent"] = parent

        result = self._make_request("GET", "products/categories", params=params)

        if isinstance(result, list):
            return result
        else:
            return []

    def create_category(
        self,
        name: str,
        parent: Optional[int] = None,
        description: Optional[str] = None,
        image: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create product category"""
        category_data = {"name": name}

        if parent:
            category_data["parent"] = parent

        if description:
            category_data["description"] = description

        if image:
            category_data["image"] = image

        result = self._make_request("POST", "products/categories", json_data=category_data)

        if "id" in result:
            result["success"] = True

        return result

    # ===== Reports =====

    def get_sales_report(
        self,
        period: str = "week",  # week, month, last_month, year
        date_min: Optional[str] = None,
        date_max: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sales report"""
        params = {"period": period}

        if date_min:
            params["date_min"] = date_min

        if date_max:
            params["date_max"] = date_max

        return self._make_request("GET", "reports/sales", params=params)

    def get_top_sellers_report(
        self,
        period: str = "week",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top selling products"""
        params = {
            "period": period,
            "per_page": limit
        }

        result = self._make_request("GET", "reports/top_sellers", params=params)

        if isinstance(result, list):
            return result
        else:
            return []


# ===== Usage Example =====
if __name__ == "__main__":
    service = WooCommerceIntegrationService(
        url="https://mystore.com",
        consumer_key="ck_...",
        consumer_secret="cs_..."
    )

    # Get products
    products = service.get_products(per_page=10)
    print("Products:", len(products))

    # Create affiliate coupon
    coupon = service.create_coupon(
        code="AFFILIATE10",
        discount_type="percent",
        amount="10",
        usage_limit=100
    )
    print("Coupon created:", coupon.get("success"))

    # Get orders
    orders = service.get_orders(status="completed", per_page=10)
    print("Orders:", len(orders))
