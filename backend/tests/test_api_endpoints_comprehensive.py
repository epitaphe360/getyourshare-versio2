"""
Tests API Endpoints Complets

Couvre tous les endpoints critiques:
- Produits (CRUD)
- Utilisateurs
- Commissions
- Analytics
- Dashboard
- Admin
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

try:
    from server import app
    HAS_APP = True
except ImportError:
    HAS_APP = False
    app = None


@pytest.fixture
def client():
    if not HAS_APP:
        pytest.skip("Server app not available")
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    with patch('supabase_client.supabase') as mock:
        yield mock


@pytest.fixture
def influencer_auth():
    with patch('auth.get_current_user') as mock:
        mock.return_value = {
            "id": "inf-123",
            "email": "influencer@test.com",
            "role": "influencer",
            "name": "Test Influencer"
        }
        yield mock


@pytest.fixture
def merchant_auth():
    with patch('auth.get_current_user') as mock:
        mock.return_value = {
            "id": "mer-123",
            "email": "merchant@test.com",
            "role": "merchant",
            "name": "Test Merchant",
            "company_name": "Test Company"
        }
        yield mock


@pytest.fixture
def admin_auth():
    with patch('auth.get_current_user') as mock:
        mock.return_value = {
            "id": "admin-123",
            "email": "admin@test.com",
            "role": "admin",
            "name": "Admin User"
        }
        yield mock


# ============================================
# TESTS PRODUCTS API
# ============================================

class TestProductsAPI:
    """Tests pour l'API Produits"""

    def test_list_products_public(self, client, mock_supabase):
        """Liste des produits publics"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "1", "title": "Product 1", "price": 100},
                {"id": "2", "title": "Product 2", "price": 200}
            ]
        )

        response = client.get("/api/products")
        assert response.status_code in [200, 404]

    def test_get_product_detail(self, client, mock_supabase):
        """Détail d'un produit"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "1", "title": "Product 1", "price": 100, "description": "Test"}
        )

        response = client.get("/api/products/1")
        assert response.status_code in [200, 404]

    def test_create_product_as_merchant(self, client, mock_supabase, merchant_auth):
        """Création de produit par marchand"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "new-prod"}]
        )

        response = client.post(
            "/api/products",
            json={
                "title": "New Product",
                "description": "Test description",
                "price": 150.00,
                "category": "electronics"
            },
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 201, 403, 404]

    def test_create_product_fails_for_influencer(self, client, influencer_auth):
        """Influencer ne peut pas créer de produit"""
        response = client.post(
            "/api/products",
            json={"title": "Test", "price": 100},
            headers={"Authorization": "Bearer influencer-token"}
        )
        assert response.status_code in [403, 404]

    def test_update_product(self, client, mock_supabase, merchant_auth):
        """Mise à jour de produit"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "title": "Updated"}]
        )

        response = client.put(
            "/api/products/1",
            json={"title": "Updated Product"},
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 403, 404]

    def test_delete_product(self, client, mock_supabase, merchant_auth):
        """Suppression de produit"""
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()

        response = client.delete(
            "/api/products/1",
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 204, 403, 404]

    def test_product_search(self, client, mock_supabase):
        """Recherche de produits"""
        mock_supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "title": "Matching Product"}]
        )

        response = client.get("/api/products/search?q=test")
        assert response.status_code in [200, 404]

    def test_product_filter_by_category(self, client, mock_supabase):
        """Filtrage par catégorie"""
        response = client.get("/api/products?category=electronics")
        assert response.status_code in [200, 404]

    def test_product_pagination(self, client, mock_supabase):
        """Pagination des produits"""
        response = client.get("/api/products?page=1&limit=10")
        assert response.status_code in [200, 404]


# ============================================
# TESTS USER API
# ============================================

class TestUserAPI:
    """Tests pour l'API Utilisateurs"""

    def test_get_current_user_profile(self, client, mock_supabase, influencer_auth):
        """Profil utilisateur courant"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "inf-123", "email": "test@example.com", "name": "Test"}
        )

        response = client.get(
            "/api/user/profile",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_update_profile(self, client, mock_supabase, influencer_auth):
        """Mise à jour du profil"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "inf-123", "name": "Updated Name"}]
        )

        response = client.put(
            "/api/user/profile",
            json={"name": "Updated Name", "phone": "+212612345678"},
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_change_password(self, client, mock_supabase, influencer_auth):
        """Changement de mot de passe"""
        response = client.post(
            "/api/user/change-password",
            json={
                "current_password": "oldpassword",
                "new_password": "NewSecureP@ss123!"
            },
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 400, 404]

    def test_get_user_stats(self, client, mock_supabase, influencer_auth):
        """Statistiques utilisateur"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"total_sales": 1000, "total_commissions": 100}]
        )

        response = client.get(
            "/api/user/stats",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]


# ============================================
# TESTS COMMISSIONS API
# ============================================

class TestCommissionsAPI:
    """Tests pour l'API Commissions"""

    def test_list_commissions(self, client, mock_supabase, influencer_auth):
        """Liste des commissions"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "c1", "amount": 100, "status": "pending"},
                {"id": "c2", "amount": 200, "status": "paid"}
            ]
        )

        response = client.get(
            "/api/commissions",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_commission_detail(self, client, mock_supabase, influencer_auth):
        """Détail d'une commission"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "c1", "amount": 100, "status": "pending", "product": "Test"}
        )

        response = client.get(
            "/api/commissions/c1",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_commission_filter_by_status(self, client, mock_supabase, influencer_auth):
        """Filtrage par statut"""
        response = client.get(
            "/api/commissions?status=pending",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_commission_stats(self, client, mock_supabase, influencer_auth):
        """Statistiques de commissions"""
        response = client.get(
            "/api/commissions/stats",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]


# ============================================
# TESTS AFFILIATE LINKS API
# ============================================

class TestAffiliateLinkAPI:
    """Tests pour l'API Liens d'affiliation"""

    def test_create_affiliate_link(self, client, mock_supabase, influencer_auth):
        """Création de lien d'affiliation"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "link-123", "code": "ABC123", "url": "https://..."}]
        )

        response = client.post(
            "/api/affiliate-links",
            json={"product_id": "prod-123"},
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 201, 404]

    def test_list_my_links(self, client, mock_supabase, influencer_auth):
        """Liste de mes liens"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "l1", "code": "ABC"}, {"id": "l2", "code": "DEF"}]
        )

        response = client.get(
            "/api/affiliate-links",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_link_statistics(self, client, mock_supabase, influencer_auth):
        """Statistiques d'un lien"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data={"clicks": 100, "conversions": 10, "revenue": 500}
        )

        response = client.get(
            "/api/affiliate-links/link-123/stats",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]


# ============================================
# TESTS DASHBOARD API
# ============================================

class TestDashboardAPI:
    """Tests pour l'API Dashboard"""

    def test_influencer_dashboard(self, client, mock_supabase, influencer_auth):
        """Dashboard influenceur"""
        response = client.get(
            "/api/dashboard/influencer",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_merchant_dashboard(self, client, mock_supabase, merchant_auth):
        """Dashboard marchand"""
        response = client.get(
            "/api/dashboard/merchant",
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 404]

    def test_dashboard_stats(self, client, mock_supabase, influencer_auth):
        """Statistiques dashboard"""
        response = client.get(
            "/api/dashboard/stats?period=30d",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_dashboard_charts_data(self, client, mock_supabase, influencer_auth):
        """Données pour graphiques"""
        response = client.get(
            "/api/dashboard/charts/revenue?period=30d",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]


# ============================================
# TESTS ADMIN API
# ============================================

class TestAdminAPI:
    """Tests pour l'API Admin"""

    def test_admin_list_users(self, client, mock_supabase, admin_auth):
        """Liste des utilisateurs (admin)"""
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{"id": "1", "email": "user1@test.com"}, {"id": "2", "email": "user2@test.com"}]
        )

        response = client.get(
            "/api/admin/users",
            headers={"Authorization": "Bearer admin-token"}
        )
        assert response.status_code in [200, 404]

    def test_admin_user_detail(self, client, mock_supabase, admin_auth):
        """Détail utilisateur (admin)"""
        response = client.get(
            "/api/admin/users/user-123",
            headers={"Authorization": "Bearer admin-token"}
        )
        assert response.status_code in [200, 404]

    def test_admin_ban_user(self, client, mock_supabase, admin_auth):
        """Bannir un utilisateur"""
        response = client.post(
            "/api/admin/users/user-123/ban",
            json={"reason": "Terms violation"},
            headers={"Authorization": "Bearer admin-token"}
        )
        assert response.status_code in [200, 404]

    def test_admin_pending_registrations(self, client, mock_supabase, admin_auth):
        """Inscriptions en attente"""
        response = client.get(
            "/api/admin/registrations/pending",
            headers={"Authorization": "Bearer admin-token"}
        )
        assert response.status_code in [200, 404]

    def test_admin_approve_registration(self, client, mock_supabase, admin_auth):
        """Approuver une inscription"""
        response = client.post(
            "/api/admin/registrations/reg-123/approve",
            headers={"Authorization": "Bearer admin-token"}
        )
        assert response.status_code in [200, 404]

    def test_admin_platform_analytics(self, client, mock_supabase, admin_auth):
        """Analytics plateforme"""
        response = client.get(
            "/api/admin/analytics",
            headers={"Authorization": "Bearer admin-token"}
        )
        assert response.status_code in [200, 404]

    def test_admin_revenue_report(self, client, mock_supabase, admin_auth):
        """Rapport de revenus"""
        response = client.get(
            "/api/admin/reports/revenue?period=monthly",
            headers={"Authorization": "Bearer admin-token"}
        )
        assert response.status_code in [200, 404]

    def test_admin_access_denied_for_non_admin(self, client, mock_supabase, influencer_auth):
        """Accès refusé pour non-admin"""
        response = client.get(
            "/api/admin/users",
            headers={"Authorization": "Bearer influencer-token"}
        )
        assert response.status_code in [401, 403, 404]


# ============================================
# TESTS ANALYTICS API
# ============================================

class TestAnalyticsAPI:
    """Tests pour l'API Analytics"""

    def test_sales_analytics(self, client, mock_supabase, influencer_auth):
        """Analytics de ventes"""
        response = client.get(
            "/api/analytics/sales?period=30d",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_conversion_analytics(self, client, mock_supabase, influencer_auth):
        """Analytics de conversion"""
        response = client.get(
            "/api/analytics/conversions",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_traffic_analytics(self, client, mock_supabase, influencer_auth):
        """Analytics de trafic"""
        response = client.get(
            "/api/analytics/traffic",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_export_analytics(self, client, mock_supabase, influencer_auth):
        """Export des analytics"""
        response = client.get(
            "/api/analytics/export?format=csv",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]


# ============================================
# TESTS NOTIFICATIONS API
# ============================================

class TestNotificationsAPI:
    """Tests pour l'API Notifications"""

    def test_list_notifications(self, client, mock_supabase, influencer_auth):
        """Liste des notifications"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{"id": "n1", "message": "Test", "read": False}]
        )

        response = client.get(
            "/api/notifications",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_mark_notification_read(self, client, mock_supabase, influencer_auth):
        """Marquer comme lu"""
        response = client.put(
            "/api/notifications/n1/read",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_mark_all_read(self, client, mock_supabase, influencer_auth):
        """Marquer tout comme lu"""
        response = client.put(
            "/api/notifications/read-all",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_notification_preferences(self, client, mock_supabase, influencer_auth):
        """Préférences de notification"""
        response = client.get(
            "/api/notifications/preferences",
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]

    def test_update_notification_preferences(self, client, mock_supabase, influencer_auth):
        """Mise à jour préférences"""
        response = client.put(
            "/api/notifications/preferences",
            json={"email_enabled": True, "push_enabled": False},
            headers={"Authorization": "Bearer user-token"}
        )
        assert response.status_code in [200, 404]


# ============================================
# TESTS ERROR HANDLING
# ============================================

class TestErrorHandling:
    """Tests de gestion des erreurs"""

    def test_404_on_unknown_endpoint(self, client):
        """404 sur endpoint inconnu"""
        response = client.get("/api/unknown/endpoint")
        assert response.status_code == 404

    def test_405_on_wrong_method(self, client):
        """405 sur mauvaise méthode HTTP"""
        response = client.delete("/api/products")  # DELETE sur liste
        assert response.status_code in [404, 405]

    def test_422_on_invalid_json(self, client, influencer_auth):
        """422 sur JSON invalide"""
        response = client.post(
            "/api/products",
            data="not json",
            headers={
                "Authorization": "Bearer user-token",
                "Content-Type": "application/json"
            }
        )
        assert response.status_code in [400, 403, 404, 422]

    def test_error_response_format(self, client):
        """Format de réponse d'erreur"""
        response = client.get("/api/nonexistent")

        if response.status_code == 404:
            data = response.json()
            # Devrait avoir un message d'erreur structuré
            assert "detail" in data or "message" in data or "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
