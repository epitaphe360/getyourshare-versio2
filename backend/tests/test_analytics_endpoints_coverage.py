import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport
from server import app
from analytics_endpoints import router
from auth import get_current_user_from_cookie

@pytest.mark.asyncio
class TestAnalyticsCoverage:
    
    @pytest.fixture
    async def client(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac

    @pytest.fixture
    def mock_supabase(self):
        with patch("analytics_endpoints.get_supabase_client") as mock:
            client_mock = MagicMock()
            mock.return_value = client_mock
            yield client_mock

    @pytest.fixture
    def mock_user_admin(self):
        with patch("analytics_endpoints.get_user_by_id") as mock:
            mock.return_value = {"id": "admin_id", "role": "admin"}
            yield mock

    async def test_get_analytics_overview_success(self, client, mock_supabase, mock_user_admin):
        # Override dependency
        app.dependency_overrides[get_current_user_from_cookie] = lambda: {"id": "admin_id", "role": "admin"}
        
        try:
            # Mock database responses
            # Users counts
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.count = 10
            # Active users
            mock_supabase.table.return_value.select.return_value.gt.return_value.execute.return_value.count = 5
            # Products/Services/Campaigns
            mock_supabase.table.return_value.select.return_value.execute.return_value.count = 20
            
            # Sales data
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
                {"amount": 100, "platform_commission": 10, "commission_amount": 5},
                {"amount": 200, "platform_commission": 20, "commission_amount": 10}
            ]
            
            # Commissions data
            mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{"amount": 15}]

            response = await client.get("/api/analytics/overview")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "users" in data
            assert data["users"]["total_merchants"] == 10
            assert data["users"]["total_influencers"] == 10
            assert data["users"]["total_commercials"] == 10
            assert data["users"]["active_users_24h"] == 5
            
            assert "catalog" in data
            assert data["catalog"]["total_products"] == 20
            assert data["catalog"]["total_services"] == 20
            assert data["catalog"]["total_campaigns"] == 20
            
            assert "financial" in data
            assert data["financial"]["total_revenue"] == 300.0
            assert data["financial"]["platform_commission"] == 30.0
            assert data["financial"]["total_commissions"] == 15.0
        finally:
            app.dependency_overrides = {}

    async def test_get_analytics_overview_forbidden(self, client, mock_supabase):
        # Override dependency with merchant user
        app.dependency_overrides[get_current_user_from_cookie] = lambda: {"id": "user_id", "role": "merchant"}
        
        try:
            with patch("analytics_endpoints.get_user_by_id") as mock_user:
                mock_user.return_value = {"id": "user_id", "role": "merchant"}
                
                response = await client.get("/api/analytics/overview")
                assert response.status_code == 403
        finally:
            app.dependency_overrides = {}
