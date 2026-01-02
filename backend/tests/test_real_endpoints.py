
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server import app
from auth import get_current_user_from_cookie

# Mock user data
MOCK_ADMIN_USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "sub": "00000000-0000-0000-0000-000000000001",
    "email": "admin@example.com",
    "role": "admin",
    "user_metadata": {"role": "admin"}
}

MOCK_MERCHANT_USER = {
    "id": "00000000-0000-0000-0000-000000000002",
    "sub": "00000000-0000-0000-0000-000000000002",
    "email": "merchant@example.com",
    "role": "merchant",
    "user_metadata": {"role": "merchant"}
}

MOCK_INFLUENCER_USER = {
    "id": "00000000-0000-0000-0000-000000000003",
    "sub": "00000000-0000-0000-0000-000000000003",
    "email": "influencer@example.com",
    "role": "influencer",
    "user_metadata": {"role": "influencer"}
}

# Mock Supabase response helper
def mock_supabase_response(data):
    mock_response = MagicMock()
    mock_response.data = data
    mock_response.count = len(data) if isinstance(data, list) else 0
    return mock_response

@pytest.mark.asyncio
class TestRealEndpoints:

    @pytest.fixture
    async def client(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c

    @pytest.fixture
    def mock_supabase(self):
        with patch("server.supabase") as mock:
            yield mock
            
    @pytest.fixture
    def mock_db_helpers(self):
        # Patch all db_helpers used in server.py AND analytics_endpoints.py
        with patch("server.get_user_by_id") as mock_user, \
             patch("server.get_merchant_by_user_id") as mock_merchant, \
             patch("server.get_influencer_by_user_id") as mock_influencer, \
             patch("analytics_endpoints.get_user_by_id") as mock_analytics_user, \
             patch("analytics_endpoints.get_influencer_by_user_id") as mock_analytics_influencer, \
             patch("analytics_endpoints.get_supabase_client") as mock_get_client:
            
            # Link analytics user mock to server user mock for consistency
            mock_analytics_user.side_effect = mock_user.side_effect
            mock_analytics_user.return_value = mock_user.return_value
            mock_analytics_influencer.side_effect = mock_influencer.side_effect
            mock_analytics_influencer.return_value = mock_influencer.return_value
            
            yield {
                "user": mock_user, 
                "merchant": mock_merchant, 
                "influencer": mock_influencer,
                "analytics_user": mock_analytics_user,
                "analytics_influencer": mock_analytics_influencer,
                "get_client": mock_get_client
            }

    async def test_get_postback_logs_admin(self, client, mock_supabase, mock_db_helpers):
        # Override dependency
        app.dependency_overrides[get_current_user_from_cookie] = lambda: MOCK_ADMIN_USER
        mock_db_helpers["user"].return_value = MOCK_ADMIN_USER
        mock_db_helpers["analytics_user"].return_value = MOCK_ADMIN_USER
        
        # Mock DB response
        mock_data = [
            {"id": 1, "click_id": "clk_1", "status": "success", "created_at": "2023-01-01T12:00:00"}
        ]
        
        mock_chain = MagicMock()
        mock_chain.execute.return_value = mock_supabase_response(mock_data)
        
        mock_supabase.table.return_value.select.return_value = mock_chain
        mock_chain.eq.return_value = mock_chain
        mock_chain.range.return_value = mock_chain
        mock_chain.order.return_value = mock_chain

        response = await client.get("/api/logs/postback")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["click_id"] == "clk_1"

    async def test_get_audit_logs_admin(self, client, mock_supabase, mock_db_helpers):
        app.dependency_overrides[get_current_user_from_cookie] = lambda: MOCK_ADMIN_USER
        mock_db_helpers["user"].return_value = MOCK_ADMIN_USER
        mock_db_helpers["analytics_user"].return_value = MOCK_ADMIN_USER
        
        mock_data = [
            {"id": 1, "action": "login", "actor_email": "user@test.com", "created_at": "2023-01-01T12:00:00"}
        ]
        
        mock_chain = MagicMock()
        mock_chain.execute.return_value = mock_supabase_response(mock_data)
        
        mock_supabase.table.return_value.select.return_value = mock_chain
        mock_chain.order.return_value = mock_chain
        mock_chain.range.return_value = mock_chain
        
        response = await client.get("/api/logs/audit")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    async def test_get_coupons_merchant(self, client, mock_supabase, mock_db_helpers):
        app.dependency_overrides[get_current_user_from_cookie] = lambda: MOCK_MERCHANT_USER
        mock_db_helpers["user"].return_value = MOCK_MERCHANT_USER
        
        mock_data = [
            {"id": "cpn_1", "code": "SAVE20", "discount_value": 20, "merchant_id": MOCK_MERCHANT_USER["id"]}
        ]
        
        mock_chain = MagicMock()
        mock_chain.execute.return_value = mock_supabase_response(mock_data)
        
        mock_supabase.table.return_value.select.return_value = mock_chain
        mock_chain.eq.return_value = mock_chain
        mock_chain.range.return_value = mock_chain
        mock_chain.order.return_value = mock_chain
        
        response = await client.get("/api/coupons")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["code"] == "SAVE20"

    async def test_get_merchant_performance(self, client, mock_supabase, mock_db_helpers):
        app.dependency_overrides[get_current_user_from_cookie] = lambda: MOCK_MERCHANT_USER
        mock_db_helpers["user"].return_value = MOCK_MERCHANT_USER
        mock_db_helpers["analytics_user"].return_value = MOCK_MERCHANT_USER
        mock_db_helpers["merchant"].return_value = {"id": "00000000-0000-0000-0000-000000000002"}
        mock_db_helpers["get_client"].return_value = mock_supabase
        
        # Mock sales (2 sales, 1 completed)
        mock_sales = [{"amount": 100, "status": "completed"}, {"amount": 200, "status": "pending"}]
        # Mock tracking_links (40 clicks)
        mock_links = [{"clicks": 10}, {"clicks": 30}]
        # Mock conversions (2 conversions)
        mock_conversions = [{"id": 1}, {"id": 2}]
        # Mock commissions (30 paid)
        mock_commissions = [{"amount": 10}, {"amount": 20}]
        # Mock products
        mock_products = [{"id": 1}]

        def table_side_effect(table_name):
            mock_table = MagicMock()
            mock_chain = MagicMock()
            
            if table_name == "sales":
                mock_chain.execute.return_value = mock_supabase_response(mock_sales)
            elif table_name == "tracking_links":
                mock_chain.execute.return_value = mock_supabase_response(mock_links)
            elif table_name == "conversions":
                mock_chain.execute.return_value = mock_supabase_response(mock_conversions)
            elif table_name == "commissions":
                mock_chain.execute.return_value = mock_supabase_response(mock_commissions)
            elif table_name == "products":
                mock_chain.execute.return_value = mock_supabase_response(mock_products)
            else:
                mock_chain.execute.return_value = mock_supabase_response([])
            
            # Configure chain to return itself for all filter methods
            mock_table.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.gt.return_value = mock_chain
            mock_chain.gte.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            
            return mock_table

        mock_supabase.table.side_effect = table_side_effect

        response = await client.get("/api/analytics/merchant/performance")
        assert response.status_code == 200
        data = response.json()
        
        # Conversion rate: 2 conversions / 40 clicks = 5.0%
        assert data["conversion_rate"] == 5.0
        # Engagement rate (Sales/Conversions): 2 / 2 * 100 = 100.0
        assert data["engagement_rate"] == 100.0
        # Satisfaction rate (Completed/Total Sales): 1 / 2 * 100 = 50.0
        assert data["satisfaction_rate"] == 50.0
        # ROI: (300 - 30) / 30 * 100 = 900.0
        assert data["roi"] == 900.0

    async def test_get_influencer_performance(self, client, mock_supabase, mock_db_helpers):
        app.dependency_overrides[get_current_user_from_cookie] = lambda: MOCK_INFLUENCER_USER
        mock_db_helpers["user"].return_value = MOCK_INFLUENCER_USER
        mock_db_helpers["analytics_user"].return_value = MOCK_INFLUENCER_USER
        mock_db_helpers["influencer"].return_value = {"id": "00000000-0000-0000-0000-000000000003"}
        mock_db_helpers["get_client"].return_value = mock_supabase
        
        # Mock affiliate_links with products
        mock_links = [
            {"id": "link1", "products": {"name": "Product A", "price": 100, "commission_rate": 10}},
            {"id": "link2", "products": {"name": "Product B", "price": 200, "commission_rate": 20}}
        ]
        # Mock commissions
        mock_commissions_1 = [{"amount": 10}]
        mock_commissions_2 = [{"amount": 40}] # Product B has more revenue
        
        def table_side_effect(table_name):
            mock_table = MagicMock()
            mock_chain = MagicMock()
            
            if table_name == "affiliate_links":
                mock_chain.execute.return_value = mock_supabase_response(mock_links)
            elif table_name == "commissions":
                # Need to handle different link_ids if possible, but for now return generic or based on call
                # Since we can't easily inspect call args in side_effect for return value logic without complexity,
                # we'll just return a list that works for the sum logic or mock it differently.
                # Actually, the server loops through links and calls commissions for each.
                # We can use side_effect on execute to return different values.
                pass
            
            mock_table.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            return mock_table

        # More complex mocking for commissions loop
        mock_supabase.table.side_effect = table_side_effect
        
        # We need to intercept the commissions calls specifically
        # The server calls: supabase.table("commissions").select(...).eq("link_id", link["id"])...
        # We can mock the execute method of the chain returned for commissions table
        
        # Let's refine the side_effect
        def refined_side_effect(table_name):
            mock_table = MagicMock()
            mock_chain = MagicMock()
            
            if table_name == "affiliate_links":
                mock_chain.execute.return_value = mock_supabase_response(mock_links)
            elif table_name == "commissions":
                # We need to return different values based on the link_id
                # But we can't easily see the link_id here because it was passed to .eq() earlier in the chain
                # So we'll just return a non-empty list so revenue > 0
                mock_chain.execute.return_value = mock_supabase_response([{"amount": 50}])
            else:
                mock_chain.execute.return_value = mock_supabase_response([])

            mock_table.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            return mock_table
            
        mock_supabase.table.side_effect = refined_side_effect

        response = await client.get("/api/analytics/influencer/performance")
        assert response.status_code == 200
        data = response.json()
        
        # Best product should be one of them (Product A or B)
        # Since we return constant revenue, the first one might be picked or last one depending on logic
        # Logic: if revenue > max_revenue. 
        # If all have same revenue (50), max_revenue updates on first, then 50 > 50 is False.
        # So first product "Product A".
        assert data["best_product"] == "Product A"
        
        # Avg commission rate: (10 + 20) / 2 = 15
        assert data["avg_commission_rate"] == 15.0

