"""
Tests pour les repositories (BaseRepository et implémentations concrètes)
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from repositories.base_repository import BaseRepository
from repositories.user_repository import UserRepository
from repositories.campaign_repository import CampaignRepository
from repositories.product_repository import ProductRepository
from repositories.sale_repository import SaleRepository
from repositories.tracking_repository import TrackingRepository


@pytest.fixture
def mock_supabase():
    """Mock Supabase client pour tests"""
    mock = Mock()
    mock.table = Mock()
    return mock


@pytest.fixture
def base_repo(mock_supabase):
    """Instance de BaseRepository pour tests"""
    return BaseRepository(mock_supabase, table_name="test_table")


@pytest.fixture
def user_repo(mock_supabase):
    """Instance de UserRepository pour tests"""
    return UserRepository(mock_supabase)


@pytest.fixture
def campaign_repo(mock_supabase):
    """Instance de CampaignRepository pour tests"""
    return CampaignRepository(mock_supabase)


@pytest.fixture
def product_repo(mock_supabase):
    """Instance de ProductRepository pour tests"""
    return ProductRepository(mock_supabase)


@pytest.fixture
def sale_repo(mock_supabase):
    """Instance de SaleRepository pour tests"""
    return SaleRepository(mock_supabase)


@pytest.fixture
def tracking_repo(mock_supabase):
    """Instance de TrackingRepository pour tests"""
    return TrackingRepository(mock_supabase)


# ============================================
# BaseRepository Tests
# ============================================

class TestBaseRepository:
    """Tests pour BaseRepository"""

    def test_init_with_table_name(self, mock_supabase):
        """Test initialisation avec table_name"""
        repo = BaseRepository(mock_supabase, table_name="users")
        assert repo.table_name == "users"
        assert repo.supabase == mock_supabase

    def test_init_with_class_attribute(self, mock_supabase):
        """Test initialisation avec table_name comme attribut de classe"""
        class TestRepo(BaseRepository):
            table_name = "products"

        repo = TestRepo(mock_supabase)
        assert repo.table_name == "products"

    def test_init_without_table_name_raises_error(self, mock_supabase):
        """Test que l'absence de table_name lève une erreur"""
        with pytest.raises(ValueError, match="must define table_name"):
            BaseRepository(mock_supabase)

    def test_execute_query_success(self, base_repo, mock_supabase):
        """Test _execute_query avec succès"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "name": "test"}]
        mock_result.count = 1

        mock_query = Mock()
        mock_query.execute = Mock(return_value=mock_result)

        result = base_repo._execute_query(mock_query, operation="test_op")

        assert result["success"] is True
        assert result["data"] == [{"id": "1", "name": "test"}]
        assert result["count"] == 1

    def test_execute_query_failure(self, base_repo):
        """Test _execute_query avec échec"""
        mock_query = Mock()
        mock_query.execute = Mock(side_effect=Exception("Database error"))

        result = base_repo._execute_query(mock_query, operation="test_op")

        assert result["success"] is False
        assert "Database error" in result["error"]
        assert result["data"] is None

    @pytest.mark.asyncio
    async def test_find_by_id_success(self, base_repo, mock_supabase):
        """Test find_by_id avec succès"""
        mock_result = Mock()
        mock_result.data = {"id": "123", "name": "Test"}

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.maybe_single = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(select=Mock(return_value=mock_query)))

        result = await base_repo.find_by_id("123")

        assert result == {"id": "123", "name": "Test"}

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self):
        """Test find_by_id quand l'enregistrement n'existe pas"""
        # Créer un mock complètement isolé pour ce test
        fresh_mock = Mock()

        mock_result = Mock()
        mock_result.data = None  # Pas de données trouvées

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.maybe_single = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_table = Mock()
        mock_table.select = Mock(return_value=mock_query)

        fresh_mock.table = Mock(return_value=mock_table)

        # Créer repo avec le mock isolé
        repo = BaseRepository(fresh_mock, table_name="test_table")
        result = await repo.find_by_id("999")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_adds_timestamp(self, base_repo, mock_supabase):
        """Test que create() ajoute created_at automatiquement"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "name": "New", "created_at": "2024-01-01T00:00:00"}]

        mock_query = Mock()
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(insert=Mock(return_value=mock_query)))

        data = {"name": "New"}
        result = await base_repo.create(data)

        assert result is not None
        assert result["id"] == "1"
        # Vérifier que created_at a été ajouté aux données
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_update_adds_timestamp(self, base_repo, mock_supabase):
        """Test que update() ajoute updated_at automatiquement"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "name": "Updated", "updated_at": "2024-01-01T00:00:00"}]

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(update=Mock(return_value=mock_query)))

        data = {"name": "Updated"}
        result = await base_repo.update("1", data)

        assert result is not None
        assert result["id"] == "1"
        # Vérifier que updated_at a été ajouté aux données
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_delete_success(self, base_repo, mock_supabase):
        """Test delete() avec succès"""
        mock_result = Mock()
        mock_result.data = [{"id": "1"}]

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(delete=Mock(return_value=mock_query)))

        result = await base_repo.delete("1")

        assert result is True

    @pytest.mark.asyncio
    async def test_count_with_filters(self, base_repo, mock_supabase):
        """Test count() avec filtres"""
        mock_result = Mock()
        mock_result.count = 42

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(select=Mock(return_value=mock_query)))

        result = await base_repo.count({"status": "active"})

        assert result == 42

    @pytest.mark.asyncio
    async def test_bulk_create(self, base_repo, mock_supabase):
        """Test bulk_create() avec plusieurs enregistrements"""
        mock_result = Mock()
        mock_result.data = [
            {"id": "1", "name": "First"},
            {"id": "2", "name": "Second"}
        ]

        mock_query = Mock()
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(insert=Mock(return_value=mock_query)))

        records = [{"name": "First"}, {"name": "Second"}]
        result = await base_repo.bulk_create(records)

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"


# ============================================
# UserRepository Tests
# ============================================

class TestUserRepository:
    """Tests pour UserRepository"""

    def test_table_name_is_users(self, user_repo):
        """Test que la table est bien 'users'"""
        assert user_repo.table_name == "users"

    @pytest.mark.asyncio
    async def test_find_by_email(self, user_repo, mock_supabase):
        """Test find_by_email()"""
        mock_result = Mock()
        mock_result.data = {"id": "1", "email": "test@example.com"}

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.maybe_single = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(select=Mock(return_value=mock_query)))

        result = await user_repo.find_by_email("test@example.com")

        assert result is not None
        assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_verify_user(self, user_repo, mock_supabase):
        """Test verify_user() marque l'utilisateur comme vérifié"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "verified": True, "verification_token": None}]

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(update=Mock(return_value=mock_query)))

        result = await user_repo.verify_user("1")

        assert result is not None
        assert result["verified"] is True

    @pytest.mark.asyncio
    async def test_update_last_login(self, user_repo, mock_supabase):
        """Test update_last_login() met à jour le timestamp"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "last_login": datetime.utcnow().isoformat()}]

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(update=Mock(return_value=mock_query)))

        result = await user_repo.update_last_login("1")

        assert result is not None
        assert "last_login" in result


# ============================================
# CampaignRepository Tests
# ============================================

class TestCampaignRepository:
    """Tests pour CampaignRepository"""

    def test_table_name_is_campaigns(self, campaign_repo):
        """Test que la table est bien 'campaigns'"""
        assert campaign_repo.table_name == "campaigns"

    @pytest.mark.asyncio
    async def test_update_status(self, campaign_repo, mock_supabase):
        """Test update_status()"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "status": "paused"}]

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(update=Mock(return_value=mock_query)))

        result = await campaign_repo.update_status("1", "paused")

        assert result is not None
        assert result["status"] == "paused"

    @pytest.mark.asyncio
    async def test_get_campaign_stats(self, mock_supabase):
        """Test get_campaign_stats() retourne les stats"""
        # Créer un nouveau repo avec un mock frais
        repo = CampaignRepository(mock_supabase)

        # Mock find_by_id pour retourner les données de campagne
        async def mock_find_by_id(campaign_id):
            return {
                "id": campaign_id,
                "name": "Test Campaign",
                "status": "active",
                "budget": 1000,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }

        repo.find_by_id = mock_find_by_id

        result = await repo.get_campaign_stats("1")

        assert result["id"] == "1"
        assert result["name"] == "Test Campaign"
        assert result["budget"] == 1000


# ============================================
# ProductRepository Tests
# ============================================

class TestProductRepository:
    """Tests pour ProductRepository"""

    def test_table_name_is_products(self, product_repo):
        """Test que la table est bien 'products'"""
        assert product_repo.table_name == "products"

    @pytest.mark.asyncio
    async def test_update_stock(self, product_repo, mock_supabase):
        """Test update_stock()"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "stock_quantity": 50}]

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(update=Mock(return_value=mock_query)))

        result = await product_repo.update_stock("1", 50)

        assert result is not None
        assert result["stock_quantity"] == 50

    @pytest.mark.asyncio
    async def test_update_price(self, product_repo, mock_supabase):
        """Test update_price()"""
        mock_result = Mock()
        mock_result.data = [{"id": "1", "price": 99.99}]

        mock_query = Mock()
        mock_query.eq = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(update=Mock(return_value=mock_query)))

        result = await product_repo.update_price("1", 99.99)

        assert result is not None
        assert result["price"] == 99.99

    @pytest.mark.asyncio
    async def test_search_by_name(self, product_repo, mock_supabase):
        """Test search_by_name()"""
        mock_result = Mock()
        mock_result.data = [
            {"id": "1", "name": "Product One"},
            {"id": "2", "name": "Product Two"}
        ]

        mock_query = Mock()
        mock_query.ilike = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.execute = Mock(return_value=mock_result)

        mock_supabase.table = Mock(return_value=Mock(select=Mock(return_value=mock_query)))

        result = await product_repo.search_by_name("Product")

        assert len(result) == 2


# ============================================
# SaleRepository Tests
# ============================================

class TestSaleRepository:
    """Tests pour SaleRepository"""

    def test_table_name_is_sales(self, sale_repo):
        """Test que la table est bien 'sales'"""
        assert sale_repo.table_name == "sales"

    @pytest.mark.asyncio
    async def test_get_total_revenue(self, sale_repo, mock_supabase):
        """Test get_total_revenue() calcule correctement"""
        # Mock find_by pour retourner des ventes
        sale_repo.find_by = AsyncMock(return_value=[
            {"id": "1", "amount": 100},
            {"id": "2", "amount": 200},
            {"id": "3", "amount": 300}
        ])

        result = await sale_repo.get_total_revenue("merchant_1")

        assert result == 600


# ============================================
# TrackingRepository Tests
# ============================================

class TestTrackingRepository:
    """Tests pour TrackingRepository"""

    def test_table_name_is_tracking_events(self, tracking_repo):
        """Test que la table est bien 'tracking_events'"""
        assert tracking_repo.table_name == "tracking_events"

    @pytest.mark.asyncio
    async def test_get_conversion_rate(self, tracking_repo):
        """Test get_conversion_rate() calcule correctement"""
        # Mock count_by_event_type
        tracking_repo.count_by_event_type = AsyncMock(side_effect=[100, 5])  # 100 clicks, 5 conversions

        result = await tracking_repo.get_conversion_rate("link_1")

        assert result["link_id"] == "link_1"
        assert result["clicks"] == 100
        assert result["conversions"] == 5
        assert result["conversion_rate"] == 5.0

    @pytest.mark.asyncio
    async def test_get_conversion_rate_no_clicks(self, tracking_repo):
        """Test get_conversion_rate() avec 0 clicks"""
        tracking_repo.count_by_event_type = AsyncMock(side_effect=[0, 0])

        result = await tracking_repo.get_conversion_rate("link_1")

        assert result["conversion_rate"] == 0
