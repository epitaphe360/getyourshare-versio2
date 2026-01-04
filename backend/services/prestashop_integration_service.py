"""
PrestaShop Integration Service for ShareYourSales
Complete PrestaShop Web Service API integration

Dependencies:
    pip install requests

Environment Variables:
    PRESTASHOP_URL: PrestaShop store URL (e.g., https://mystore.com)
    PRESTASHOP_API_KEY: PrestaShop Web Service API key

API Documentation:
    https://devdocs.prestashop.com/8/webservice/

Features:
    - Product synchronization
    - Order management
    - Customer management
    - Cart rules (discount codes)
    - Category management
    - Stock management
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import xml.etree.ElementTree as ET


logger = logging.getLogger(__name__)


class PrestaShopIntegrationService:
    """
    PrestaShop Web Service API integration

    Supports:
    - Product CRUD operations
    - Order management
    - Customer management
    - Cart rules (affiliate discounts)
    - Category management
    - Stock management

    Example:
        service = PrestaShopIntegrationService(
            url="https://mystore.com",
            api_key="YOUR_API_KEY"
        )

        # Get products
        products = service.get_products(limit=20)

        # Create cart rule (discount)
        rule = service.create_cart_rule(
            name="Affiliate 10%",
            code="AFFILIATE10",
            reduction_percent=10
        )

        # Get orders
        orders = service.get_orders(limit=20)
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize PrestaShop integration

        Args:
            url: PrestaShop store URL
            api_key: PrestaShop Web Service API key
        """
        self.url = (url or os.getenv("PRESTASHOP_URL", "")).rstrip('/')
        self.api_key = api_key or os.getenv("PRESTASHOP_API_KEY")

        if not self.url or not self.api_key:
            raise ValueError("url and api_key required")

        self.base_url = f"{self.url}/api"

    def _make_request(
        self,
        method: str,
        resource: str,
        resource_id: Optional[str] = None,
        params: Optional[Dict] = None,
        data: Optional[str] = None
    ) -> Any:
        """
        Make HTTP request to PrestaShop API

        Args:
            method: HTTP method
            resource: API resource (products, orders, etc.)
            resource_id: Resource ID
            params: Query parameters
            data: XML data for POST/PUT

        Returns:
            Parsed response
        """
        if resource_id:
            url = f"{self.base_url}/{resource}/{resource_id}"
        else:
            url = f"{self.base_url}/{resource}"

        # Add API key to params
        if params is None:
            params = {}
        params["ws_key"] = self.api_key

        # Default to XML output
        if "output_format" not in params:
            params["output_format"] = "JSON"

        headers = {}
        if data:
            headers["Content-Type"] = "application/xml"

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, data=data, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, params=params, data=data, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            # Try JSON first
            if params.get("output_format") == "JSON":
                try:
                    return response.json()
                except:
                    pass

            # Fall back to XML
            return ET.fromstring(response.content)

        except requests.exceptions.HTTPError as e:
            logger.error(f"PrestaShop API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code if e.response else None
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "error": str(e)}

    def _parse_json_response(self, response: Any, resource: str) -> List[Dict]:
        """Parse JSON response to list of items"""
        if isinstance(response, dict) and resource in response:
            items = response[resource]
            if isinstance(items, list):
                return items
            elif isinstance(items, dict):
                return [items]
        return []

    # ===== Products =====

    def get_products(
        self,
        limit: int = 20,
        offset: int = 0,
        filter_active: Optional[bool] = None,
        filter_id_category: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get products from PrestaShop

        Args:
            limit: Number of products
            offset: Offset for pagination
            filter_active: Filter by active status
            filter_id_category: Filter by category ID

        Returns:
            List of products
        """
        params = {
            "limit": f"{offset},{limit}",
            "display": "full"
        }

        if filter_active is not None:
            params["filter[active]"] = "1" if filter_active else "0"

        if filter_id_category:
            params["filter[id_category_default]"] = str(filter_id_category)

        result = self._make_request("GET", "products", params=params)

        return self._parse_json_response(result, "products")

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get single product"""
        result = self._make_request("GET", "products", resource_id=str(product_id))

        if isinstance(result, dict) and "product" in result:
            return result["product"]

        return {"success": False, "error": "Product not found"}

    def create_product(
        self,
        name: str,
        price: float,
        id_category_default: int = 2,  # Default category
        description: Optional[str] = None,
        description_short: Optional[str] = None,
        quantity: int = 0,
        reference: Optional[str] = None,
        active: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new product

        Args:
            name: Product name
            price: Product price
            id_category_default: Default category ID
            description: Long description
            description_short: Short description
            quantity: Stock quantity
            reference: Product reference/SKU
            active: Product is active

        Returns:
            Created product data
        """
        # Build XML for product creation
        product_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
    <product>
        <id_category_default>{id_category_default}</id_category_default>
        <active>{1 if active else 0}</active>
        <price>{price}</price>
        <name>
            <language id="1">{name}</language>
        </name>
        <link_rewrite>
            <language id="1">{name.lower().replace(' ', '-')}</language>
        </link_rewrite>
"""

        if description:
            product_xml += f"""
        <description>
            <language id="1"><![CDATA[{description}]]></language>
        </description>
"""

        if description_short:
            product_xml += f"""
        <description_short>
            <language id="1"><![CDATA[{description_short}]]></language>
        </description_short>
"""

        if reference:
            product_xml += f"        <reference>{reference}</reference>\n"

        product_xml += """    </product>
</prestashop>"""

        result = self._make_request("POST", "products", data=product_xml)

        if isinstance(result, dict) and "product" in result:
            product_id = result["product"].get("id")

            # Update stock if quantity specified
            if quantity > 0 and product_id:
                self.update_stock(product_id, quantity)

            result["success"] = True
            return result

        return {"success": False, "error": "Failed to create product"}

    def update_product(
        self,
        product_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update product

        Args:
            product_id: Product ID
            updates: Fields to update

        Returns:
            Updated product
        """
        # Get current product
        current = self.get_product(product_id)

        if "error" in current:
            return current

        # Build update XML (simplified - in production use full XML merge)
        update_xml = '<?xml version="1.0" encoding="UTF-8"?><prestashop><product>'

        for key, value in updates.items():
            update_xml += f"<{key}>{value}</{key}>"

        update_xml += '</product></prestashop>'

        result = self._make_request("PUT", "products", resource_id=str(product_id), data=update_xml)

        if isinstance(result, dict) and "product" in result:
            result["success"] = True

        return result

    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete product"""
        result = self._make_request("DELETE", "products", resource_id=str(product_id))

        return {"success": True, "id": product_id}

    # ===== Orders =====

    def get_orders(
        self,
        limit: int = 20,
        offset: int = 0,
        filter_current_state: Optional[int] = None,
        filter_id_customer: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get orders

        Args:
            limit: Number of orders
            offset: Offset
            filter_current_state: Filter by order state ID
            filter_id_customer: Filter by customer ID

        Returns:
            List of orders
        """
        params = {
            "limit": f"{offset},{limit}",
            "display": "full"
        }

        if filter_current_state:
            params["filter[current_state]"] = str(filter_current_state)

        if filter_id_customer:
            params["filter[id_customer]"] = str(filter_id_customer)

        result = self._make_request("GET", "orders", params=params)

        return self._parse_json_response(result, "orders")

    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get single order"""
        result = self._make_request("GET", "orders", resource_id=str(order_id))

        if isinstance(result, dict) and "order" in result:
            return result["order"]

        return {"success": False, "error": "Order not found"}

    def update_order_state(
        self,
        order_id: int,
        state_id: int
    ) -> Dict[str, Any]:
        """
        Update order state

        Args:
            order_id: Order ID
            state_id: New state ID (2=Payment accepted, 3=Processing, 5=Delivered, etc.)

        Returns:
            Updated order
        """
        update_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop>
    <order>
        <id>{order_id}</id>
        <current_state>{state_id}</current_state>
    </order>
</prestashop>"""

        result = self._make_request("PUT", "orders", resource_id=str(order_id), data=update_xml)

        if isinstance(result, dict) and "order" in result:
            result["success"] = True

        return result

    # ===== Customers =====

    def get_customers(
        self,
        limit: int = 20,
        offset: int = 0,
        filter_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get customers"""
        params = {
            "limit": f"{offset},{limit}",
            "display": "full"
        }

        if filter_email:
            params["filter[email]"] = filter_email

        result = self._make_request("GET", "customers", params=params)

        return self._parse_json_response(result, "customers")

    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get single customer"""
        result = self._make_request("GET", "customers", resource_id=str(customer_id))

        if isinstance(result, dict) and "customer" in result:
            return result["customer"]

        return {"success": False, "error": "Customer not found"}

    # ===== Cart Rules (Discount Codes) =====

    def create_cart_rule(
        self,
        name: str,
        code: str,
        reduction_percent: Optional[float] = None,
        reduction_amount: Optional[float] = None,
        minimum_amount: Optional[float] = None,
        quantity: int = 1,
        quantity_per_user: int = 1,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        active: bool = True
    ) -> Dict[str, Any]:
        """
        Create cart rule (discount code)

        Args:
            name: Cart rule name
            code: Discount code
            reduction_percent: Percentage reduction (0-100)
            reduction_amount: Fixed amount reduction
            minimum_amount: Minimum cart amount
            quantity: Total quantity available
            quantity_per_user: Quantity per user
            date_from: Valid from date
            date_to: Valid to date
            active: Rule is active

        Returns:
            Created cart rule
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_from_str = date_from.strftime("%Y-%m-%d %H:%M:%S") if date_from else now
        date_to_str = date_to.strftime("%Y-%m-%d %H:%M:%S") if date_to else "2099-12-31 23:59:59"

        cart_rule_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop>
    <cart_rule>
        <name>
            <language id="1">{name}</language>
        </name>
        <code>{code}</code>
        <quantity>{quantity}</quantity>
        <quantity_per_user>{quantity_per_user}</quantity_per_user>
        <priority>1</priority>
        <partial_use>1</partial_use>
        <date_from>{date_from_str}</date_from>
        <date_to>{date_to_str}</date_to>
        <active>{1 if active else 0}</active>
"""

        if reduction_percent:
            cart_rule_xml += f"        <reduction_percent>{reduction_percent}</reduction_percent>\n"
            cart_rule_xml += "        <reduction_tax>1</reduction_tax>\n"

        if reduction_amount:
            cart_rule_xml += f"        <reduction_amount>{reduction_amount}</reduction_amount>\n"
            cart_rule_xml += "        <reduction_tax>1</reduction_tax>\n"

        if minimum_amount:
            cart_rule_xml += f"        <minimum_amount>{minimum_amount}</minimum_amount>\n"
            cart_rule_xml += "        <minimum_amount_tax>1</minimum_amount_tax>\n"
            cart_rule_xml += "        <minimum_amount_currency>1</minimum_amount_currency>\n"

        cart_rule_xml += """    </cart_rule>
</prestashop>"""

        result = self._make_request("POST", "cart_rules", data=cart_rule_xml)

        if isinstance(result, dict) and "cart_rule" in result:
            result["success"] = True

        return result

    def get_cart_rules(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get cart rules"""
        params = {
            "limit": f"{offset},{limit}",
            "display": "full"
        }

        result = self._make_request("GET", "cart_rules", params=params)

        return self._parse_json_response(result, "cart_rules")

    def delete_cart_rule(self, cart_rule_id: int) -> Dict[str, Any]:
        """Delete cart rule"""
        result = self._make_request("DELETE", "cart_rules", resource_id=str(cart_rule_id))

        return {"success": True, "id": cart_rule_id}

    # ===== Categories =====

    def get_categories(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get product categories"""
        params = {
            "limit": f"{offset},{limit}",
            "display": "full"
        }

        result = self._make_request("GET", "categories", params=params)

        return self._parse_json_response(result, "categories")

    def get_category(self, category_id: int) -> Dict[str, Any]:
        """Get single category"""
        result = self._make_request("GET", "categories", resource_id=str(category_id))

        if isinstance(result, dict) and "category" in result:
            return result["category"]

        return {"success": False, "error": "Category not found"}

    # ===== Stock Management =====

    def update_stock(
        self,
        product_id: int,
        quantity: int,
        id_stock_available: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update product stock quantity

        Args:
            product_id: Product ID
            quantity: New quantity
            id_stock_available: Stock available ID (optional, will auto-detect)

        Returns:
            Updated stock data
        """
        # Get stock_available ID if not provided
        if not id_stock_available:
            params = {
                "filter[id_product]": str(product_id),
                "display": "full"
            }
            stock_result = self._make_request("GET", "stock_availables", params=params)
            stock_items = self._parse_json_response(stock_result, "stock_availables")

            if stock_items:
                id_stock_available = stock_items[0].get("id")

        if not id_stock_available:
            return {"success": False, "error": "Could not find stock_available ID"}

        # Update stock
        stock_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop>
    <stock_available>
        <id>{id_stock_available}</id>
        <id_product>{product_id}</id_product>
        <quantity>{quantity}</quantity>
    </stock_available>
</prestashop>"""

        result = self._make_request("PUT", "stock_availables", resource_id=str(id_stock_available), data=stock_xml)

        if isinstance(result, dict) and "stock_available" in result:
            result["success"] = True

        return result


# ===== Usage Example =====
if __name__ == "__main__":
    service = PrestaShopIntegrationService(
        url="https://mystore.com",
        api_key="YOUR_API_KEY"
    )

    # Get products
    products = service.get_products(limit=10)
    print("Products:", len(products))

    # Create cart rule (affiliate discount)
    cart_rule = service.create_cart_rule(
        name="Affiliate 10%",
        code="AFFILIATE10",
        reduction_percent=10.0,
        quantity=100
    )
    print("Cart rule created:", cart_rule.get("success"))

    # Get orders
    orders = service.get_orders(limit=10)
    print("Orders:", len(orders))
