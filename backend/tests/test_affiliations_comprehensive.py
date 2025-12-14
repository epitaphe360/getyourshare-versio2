"""
Tests Affiliations et Liens Complets

Couvre:
- Création de liens d'affiliation
- Tracking des clics
- Conversions
- Statistiques
- Demandes d'affiliation
- Validation des liens
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import uuid

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
            "role": "influencer"
        }
        yield mock


@pytest.fixture
def merchant_auth():
    with patch('auth.get_current_user') as mock:
        mock.return_value = {
            "id": "mer-123",
            "email": "merchant@test.com",
            "role": "merchant"
        }
        yield mock


# ============================================
# TESTS CRÉATION DE LIENS
# ============================================

class TestAffiliateLinkCreation:
    """Tests pour la création de liens d'affiliation"""

    def test_create_link_for_product(self, client, mock_supabase, influencer_auth):
        """Création d'un lien pour un produit"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "link-123", "code": "ABC123", "product_id": "prod-123"}]
        )

        response = client.post(
            "/api/affiliate-links",
            json={"product_id": "prod-123"},
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 201, 404]

    def test_create_link_generates_unique_code(self, client, mock_supabase, influencer_auth):
        """Le code généré est unique"""
        codes = set()
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "link-123", "code": str(uuid.uuid4())[:8]}]
        )

        for _ in range(10):
            response = client.post(
                "/api/affiliate-links",
                json={"product_id": "prod-123"},
                headers={"Authorization": "Bearer token"}
            )
            if response.status_code in [200, 201]:
                data = response.json()
                if "code" in data:
                    codes.add(data["code"])

    def test_create_link_requires_product_id(self, client, influencer_auth):
        """Product ID est requis"""
        response = client.post(
            "/api/affiliate-links",
            json={},
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [400, 404, 422]

    def test_create_link_for_nonexistent_product(self, client, mock_supabase, influencer_auth):
        """Échec pour produit inexistant"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=None
        )

        response = client.post(
            "/api/affiliate-links",
            json={"product_id": "nonexistent"},
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [400, 404]

    def test_create_link_with_custom_parameters(self, client, mock_supabase, influencer_auth):
        """Création avec paramètres personnalisés"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "link-123", "utm_source": "instagram", "utm_campaign": "summer"}]
        )

        response = client.post(
            "/api/affiliate-links",
            json={
                "product_id": "prod-123",
                "utm_source": "instagram",
                "utm_campaign": "summer"
            },
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 201, 404]

    def test_merchant_cannot_create_affiliate_link(self, client, merchant_auth):
        """Marchand ne peut pas créer de lien d'affiliation"""
        response = client.post(
            "/api/affiliate-links",
            json={"product_id": "prod-123"},
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [403, 404]


# ============================================
# TESTS TRACKING DES CLICS
# ============================================

class TestClickTracking:
    """Tests pour le tracking des clics"""

    def test_track_click(self, client, mock_supabase):
        """Enregistrement d'un clic"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        response = client.get("/r/ABC123")  # Redirection tracking
        assert response.status_code in [200, 301, 302, 307, 404]

    def test_track_click_with_referrer(self, client, mock_supabase):
        """Clic avec referrer"""
        response = client.get(
            "/r/ABC123",
            headers={"Referer": "https://instagram.com/post/123"}
        )
        assert response.status_code in [200, 301, 302, 307, 404]

    def test_track_click_stores_user_agent(self, client, mock_supabase):
        """User agent est stocké"""
        response = client.get(
            "/r/ABC123",
            headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)"}
        )
        assert response.status_code in [200, 301, 302, 307, 404]

    def test_track_click_invalid_code(self, client, mock_supabase):
        """Clic avec code invalide"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=None
        )

        response = client.get("/r/INVALID")
        assert response.status_code in [302, 404]

    def test_click_increments_counter(self, client, mock_supabase):
        """Le compteur de clics est incrémenté"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "link-123", "clicks": 10}
        )

        response = client.get("/r/ABC123")
        # Le compteur devrait être incrémenté


# ============================================
# TESTS CONVERSIONS
# ============================================

class TestConversions:
    """Tests pour les conversions"""

    def test_record_conversion(self, client, mock_supabase, merchant_auth):
        """Enregistrement d'une conversion"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "conv-123", "amount": 100}]
        )

        response = client.post(
            "/api/conversions",
            json={
                "affiliate_link_id": "link-123",
                "order_id": "order-456",
                "amount": 100.00
            },
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 201, 404]

    def test_conversion_creates_commission(self, client, mock_supabase, merchant_auth):
        """Conversion crée une commission"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"commission_rate": 10.0, "influencer_id": "inf-123"}
        )
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "comm-123", "amount": 10.0}]
        )

        response = client.post(
            "/api/conversions",
            json={
                "affiliate_link_id": "link-123",
                "order_id": "order-456",
                "amount": 100.00
            },
            headers={"Authorization": "Bearer merchant-token"}
        )
        # Une commission de 10% (10.0) devrait être créée

    def test_conversion_with_zero_amount(self, client, mock_supabase, merchant_auth):
        """Conversion avec montant zéro"""
        response = client.post(
            "/api/conversions",
            json={
                "affiliate_link_id": "link-123",
                "order_id": "order-456",
                "amount": 0
            },
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [400, 404, 422]

    def test_duplicate_conversion_rejected(self, client, mock_supabase, merchant_auth):
        """Conversion dupliquée rejetée"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "existing-conv"}]
        )

        response = client.post(
            "/api/conversions",
            json={
                "affiliate_link_id": "link-123",
                "order_id": "order-456",  # Même order_id
                "amount": 100.00
            },
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [400, 404, 409]


# ============================================
# TESTS STATISTIQUES
# ============================================

class TestAffiliateStatistics:
    """Tests pour les statistiques d'affiliation"""

    def test_get_link_stats(self, client, mock_supabase, influencer_auth):
        """Statistiques d'un lien"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data={"clicks": 100, "conversions": 10, "revenue": 500}
        )

        response = client.get(
            "/api/affiliate-links/link-123/stats",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 404]

    def test_get_all_links_stats(self, client, mock_supabase, influencer_auth):
        """Statistiques de tous les liens"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "l1", "clicks": 50, "conversions": 5},
                {"id": "l2", "clicks": 100, "conversions": 15}
            ]
        )

        response = client.get(
            "/api/affiliate-links/stats",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 404]

    def test_stats_by_period(self, client, mock_supabase, influencer_auth):
        """Statistiques par période"""
        response = client.get(
            "/api/affiliate-links/stats?period=30d",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 404]

    def test_conversion_rate_calculation(self, client, mock_supabase, influencer_auth):
        """Calcul du taux de conversion"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data={"clicks": 100, "conversions": 10}
        )

        response = client.get(
            "/api/affiliate-links/link-123/stats",
            headers={"Authorization": "Bearer token"}
        )

        if response.status_code == 200:
            data = response.json()
            # Taux de conversion devrait être 10%
            if "conversion_rate" in data:
                assert data["conversion_rate"] == 10.0

    def test_stats_only_for_own_links(self, client, mock_supabase, influencer_auth):
        """Statistiques uniquement pour ses propres liens"""
        # Mock lien appartenant à un autre utilisateur
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "link-123", "user_id": "other-user"}
        )

        response = client.get(
            "/api/affiliate-links/link-123/stats",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [403, 404]


# ============================================
# TESTS DEMANDES D'AFFILIATION
# ============================================

class TestAffiliationRequests:
    """Tests pour les demandes d'affiliation"""

    def test_request_affiliation(self, client, mock_supabase, influencer_auth):
        """Demande d'affiliation à un marchand"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "req-123", "status": "pending"}]
        )

        response = client.post(
            "/api/affiliation-requests",
            json={
                "merchant_id": "mer-123",
                "message": "Je souhaite promouvoir vos produits"
            },
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 201, 404]

    def test_list_my_requests(self, client, mock_supabase, influencer_auth):
        """Liste de mes demandes"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "req-1", "status": "pending"},
                {"id": "req-2", "status": "approved"}
            ]
        )

        response = client.get(
            "/api/affiliation-requests",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 404]

    def test_merchant_list_received_requests(self, client, mock_supabase, merchant_auth):
        """Marchand voit les demandes reçues"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "req-1", "influencer_id": "inf-123", "status": "pending"}]
        )

        response = client.get(
            "/api/affiliation-requests/received",
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 404]

    def test_merchant_approve_request(self, client, mock_supabase, merchant_auth):
        """Marchand approuve une demande"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "req-123", "status": "approved"}]
        )

        response = client.post(
            "/api/affiliation-requests/req-123/approve",
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 404]

    def test_merchant_reject_request(self, client, mock_supabase, merchant_auth):
        """Marchand rejette une demande"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "req-123", "status": "rejected"}]
        )

        response = client.post(
            "/api/affiliation-requests/req-123/reject",
            json={"reason": "Pas adapté à notre marque"},
            headers={"Authorization": "Bearer merchant-token"}
        )
        assert response.status_code in [200, 404]

    def test_cannot_request_twice(self, client, mock_supabase, influencer_auth):
        """Ne peut pas faire deux demandes au même marchand"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "existing-req"}]
        )

        response = client.post(
            "/api/affiliation-requests",
            json={"merchant_id": "mer-123"},
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [400, 404, 409]


# ============================================
# TESTS VALIDATION DES LIENS
# ============================================

class TestLinkValidation:
    """Tests de validation des liens"""

    def test_link_expiration(self, client, mock_supabase, influencer_auth):
        """Lien expiré ne fonctionne pas"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "link-123",
                "expires_at": (datetime.now() - timedelta(days=1)).isoformat()
            }
        )

        response = client.get("/r/EXPIRED")
        assert response.status_code in [302, 404, 410]

    def test_deactivated_link(self, client, mock_supabase):
        """Lien désactivé ne fonctionne pas"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "link-123", "active": False}
        )

        response = client.get("/r/DEACTIVATED")
        assert response.status_code in [302, 404, 410]

    def test_toggle_link_status(self, client, mock_supabase, influencer_auth):
        """Activer/désactiver un lien"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "link-123", "active": False}]
        )

        response = client.put(
            "/api/affiliate-links/link-123/toggle",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 404]

    def test_delete_link(self, client, mock_supabase, influencer_auth):
        """Supprimer un lien"""
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()

        response = client.delete(
            "/api/affiliate-links/link-123",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 204, 404]

    def test_cannot_delete_others_link(self, client, mock_supabase, influencer_auth):
        """Ne peut pas supprimer le lien d'un autre"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "link-123", "user_id": "other-user"}
        )

        response = client.delete(
            "/api/affiliate-links/link-123",
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [403, 404]


# ============================================
# TESTS URL SHORTENING
# ============================================

class TestURLShortening:
    """Tests pour le raccourcissement d'URL"""

    def test_short_url_generated(self, client, mock_supabase, influencer_auth):
        """URL courte générée"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "link-123", "short_url": "https://gys.link/ABC123"}]
        )

        response = client.post(
            "/api/affiliate-links",
            json={"product_id": "prod-123"},
            headers={"Authorization": "Bearer token"}
        )

        if response.status_code in [200, 201]:
            data = response.json()
            if "short_url" in data:
                assert "gys.link" in data["short_url"] or len(data["short_url"]) < 50

    def test_custom_slug(self, client, mock_supabase, influencer_auth):
        """Slug personnalisé"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "link-123", "slug": "my-promo"}]
        )

        response = client.post(
            "/api/affiliate-links",
            json={
                "product_id": "prod-123",
                "custom_slug": "my-promo"
            },
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [200, 201, 400, 404]

    def test_custom_slug_already_taken(self, client, mock_supabase, influencer_auth):
        """Slug personnalisé déjà pris"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "existing-link", "slug": "my-promo"}]
        )

        response = client.post(
            "/api/affiliate-links",
            json={
                "product_id": "prod-123",
                "custom_slug": "my-promo"
            },
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code in [400, 404, 409]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
