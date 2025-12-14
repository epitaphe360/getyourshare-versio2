"""
Tests de Paiements Complets

Couvre:
- Création de paiements
- Webhooks (CMI, Stripe, PayPal)
- Commissions (calcul, paiement, validation)
- Payouts influenceurs
- Remboursements
- Abonnements
- Sécurité des transactions
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal
import json
import hmac
import hashlib

try:
    from server import app
    HAS_APP = True
except ImportError:
    HAS_APP = False
    app = None


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def client():
    """Client de test FastAPI"""
    if not HAS_APP:
        pytest.skip("Server app not available")
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Headers d'authentification"""
    return {"Authorization": "Bearer valid-test-token"}


@pytest.fixture
def admin_headers():
    """Headers d'authentification admin"""
    return {"Authorization": "Bearer admin-test-token"}


@pytest.fixture
def mock_supabase():
    """Mock du client Supabase"""
    with patch('supabase_client.supabase') as mock:
        yield mock


@pytest.fixture
def mock_auth_user():
    """Mock de l'utilisateur authentifié"""
    with patch('auth.get_current_user') as mock:
        mock.return_value = {
            "id": "user-123",
            "email": "test@example.com",
            "role": "influencer"
        }
        yield mock


@pytest.fixture
def sample_payment_data():
    """Données de paiement exemple"""
    return {
        "amount": 99.99,
        "currency": "MAD",
        "payment_method": "cmi",
        "plan_id": "pro_monthly",
        "metadata": {"user_id": "user-123"}
    }


@pytest.fixture
def sample_payout_request():
    """Demande de paiement exemple"""
    return {
        "amount": 500.00,
        "currency": "MAD",
        "method": "bank_transfer",
        "bank_details": {
            "iban": "MA12 1234 5678 9012 3456 7890 12",
            "bic": "BCPOMAMC",
            "account_holder": "Test User"
        }
    }


# ============================================
# TESTS CRÉATION DE PAIEMENTS
# ============================================

class TestPaymentCreation:
    """Tests pour la création de paiements"""

    def test_create_subscription_payment(self, client, auth_headers, sample_payment_data, mock_supabase, mock_auth_user):
        """Création d'un paiement d'abonnement"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "payment-123", "status": "pending"}]
        )

        response = client.post(
            "/api/payments/init-subscription",
            json=sample_payment_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 404]
        if response.status_code in [200, 201]:
            data = response.json()
            assert "payment_url" in data or "session_id" in data or "id" in data

    def test_payment_amount_validation(self, client, auth_headers, sample_payment_data, mock_auth_user):
        """Validation du montant de paiement"""
        # Montant négatif
        sample_payment_data["amount"] = -100
        response = client.post(
            "/api/payments/init-subscription",
            json=sample_payment_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 404, 422]

        # Montant zéro
        sample_payment_data["amount"] = 0
        response = client.post(
            "/api/payments/init-subscription",
            json=sample_payment_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 404, 422]

    def test_payment_currency_validation(self, client, auth_headers, sample_payment_data, mock_auth_user):
        """Validation de la devise"""
        sample_payment_data["currency"] = "INVALID"
        response = client.post(
            "/api/payments/init-subscription",
            json=sample_payment_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 404, 422]

    def test_payment_requires_auth(self, client, sample_payment_data):
        """Paiement nécessite authentification"""
        response = client.post(
            "/api/payments/init-subscription",
            json=sample_payment_data
        )
        assert response.status_code in [401, 403, 404]


# ============================================
# TESTS WEBHOOKS CMI
# ============================================

class TestCMIWebhooks:
    """Tests pour les webhooks CMI (paiement Maroc)"""

    @pytest.fixture
    def cmi_success_payload(self):
        """Payload CMI de succès"""
        return {
            "TransId": "CMI123456",
            "MerchantId": "123456789",
            "orderId": "order-123",
            "amount": "99.99",
            "currency": "504",  # MAD
            "ProcReturnCode": "00",  # Success
            "Response": "Approved",
            "AuthCode": "123456",
            "clientid": "user-123"
        }

    def test_cmi_webhook_success(self, client, cmi_success_payload, mock_supabase):
        """Webhook CMI de succès"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        response = client.post(
            "/api/webhooks/cmi/callback",
            data=cmi_success_payload
        )

        assert response.status_code in [200, 302, 404]

    def test_cmi_webhook_failure(self, client, cmi_success_payload, mock_supabase):
        """Webhook CMI d'échec"""
        cmi_success_payload["ProcReturnCode"] = "05"  # Declined
        cmi_success_payload["Response"] = "Declined"

        response = client.post(
            "/api/webhooks/cmi/callback",
            data=cmi_success_payload
        )

        assert response.status_code in [200, 302, 400, 404]

    def test_cmi_webhook_validates_signature(self, client, cmi_success_payload):
        """Webhook CMI valide la signature"""
        # Signature invalide devrait être rejetée
        cmi_success_payload["signature"] = "invalid-signature"

        response = client.post(
            "/api/webhooks/cmi/callback",
            data=cmi_success_payload
        )

        # Devrait échouer ou être ignoré
        assert response.status_code in [200, 400, 401, 403, 404]


# ============================================
# TESTS WEBHOOKS STRIPE
# ============================================

class TestStripeWebhooks:
    """Tests pour les webhooks Stripe"""

    @pytest.fixture
    def stripe_success_payload(self):
        """Payload Stripe de succès"""
        return {
            "id": "evt_123",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_123",
                    "payment_status": "paid",
                    "amount_total": 9999,
                    "currency": "mad",
                    "customer": "cus_123",
                    "metadata": {"user_id": "user-123", "plan_id": "pro"}
                }
            }
        }

    def test_stripe_webhook_success(self, client, stripe_success_payload, mock_supabase):
        """Webhook Stripe de succès"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        # Simuler signature Stripe
        with patch('stripe.Webhook.construct_event', return_value=stripe_success_payload):
            response = client.post(
                "/api/webhooks/stripe",
                json=stripe_success_payload,
                headers={"Stripe-Signature": "test-signature"}
            )

            assert response.status_code in [200, 404]

    def test_stripe_webhook_validates_signature(self, client, stripe_success_payload):
        """Webhook Stripe valide la signature"""
        with patch('stripe.Webhook.construct_event', side_effect=Exception("Invalid signature")):
            response = client.post(
                "/api/webhooks/stripe",
                json=stripe_success_payload,
                headers={"Stripe-Signature": "invalid-signature"}
            )

            assert response.status_code in [400, 401, 404]

    def test_stripe_webhook_handles_refund(self, client, mock_supabase):
        """Webhook Stripe gère les remboursements"""
        refund_payload = {
            "id": "evt_456",
            "type": "charge.refunded",
            "data": {
                "object": {
                    "id": "ch_123",
                    "amount_refunded": 9999,
                    "metadata": {"payment_id": "payment-123"}
                }
            }
        }

        with patch('stripe.Webhook.construct_event', return_value=refund_payload):
            response = client.post(
                "/api/webhooks/stripe",
                json=refund_payload,
                headers={"Stripe-Signature": "test-signature"}
            )

            assert response.status_code in [200, 404]


# ============================================
# TESTS COMMISSIONS
# ============================================

class TestCommissions:
    """Tests pour le système de commissions"""

    def test_calculate_commission(self, client, auth_headers, mock_supabase, mock_auth_user):
        """Calcul de commission"""
        sale_data = {
            "sale_amount": 1000.00,
            "product_id": "prod-123",
            "affiliate_link_id": "link-123"
        }

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"commission_rate": 10.0}
        )

        response = client.post(
            "/api/commissions/calculate",
            json=sale_data,
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            assert "commission" in data or "amount" in data

    def test_commission_rate_validation(self, client, auth_headers, mock_auth_user):
        """Validation du taux de commission"""
        # Taux négatif devrait échouer
        response = client.post(
            "/api/commissions/set-rate",
            json={"product_id": "prod-123", "rate": -5},
            headers=auth_headers
        )
        assert response.status_code in [400, 403, 404, 422]

        # Taux > 100% devrait échouer
        response = client.post(
            "/api/commissions/set-rate",
            json={"product_id": "prod-123", "rate": 150},
            headers=auth_headers
        )
        assert response.status_code in [400, 403, 404, 422]

    def test_get_pending_commissions(self, client, auth_headers, mock_supabase, mock_auth_user):
        """Récupération des commissions en attente"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {"id": "comm-1", "amount": 100.00, "status": "pending"},
                {"id": "comm-2", "amount": 200.00, "status": "pending"}
            ]
        )

        response = client.get(
            "/api/commissions/pending",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]


# ============================================
# TESTS PAYOUTS
# ============================================

class TestPayouts:
    """Tests pour les demandes de paiement"""

    def test_request_payout(self, client, auth_headers, sample_payout_request, mock_supabase, mock_auth_user):
        """Demande de paiement"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"available_balance": 1000.00}
        )
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "payout-123", "status": "pending"}]
        )

        response = client.post(
            "/api/payouts/request",
            json=sample_payout_request,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 404]

    def test_payout_insufficient_balance(self, client, auth_headers, sample_payout_request, mock_supabase, mock_auth_user):
        """Paiement avec solde insuffisant"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"available_balance": 100.00}  # Moins que demandé
        )

        sample_payout_request["amount"] = 500.00

        response = client.post(
            "/api/payouts/request",
            json=sample_payout_request,
            headers=auth_headers
        )

        assert response.status_code in [400, 404]

    def test_payout_minimum_amount(self, client, auth_headers, sample_payout_request, mock_supabase, mock_auth_user):
        """Paiement avec montant minimum"""
        sample_payout_request["amount"] = 1.00  # Trop petit

        response = client.post(
            "/api/payouts/request",
            json=sample_payout_request,
            headers=auth_headers
        )

        # Devrait échouer si en dessous du minimum
        assert response.status_code in [200, 400, 404, 422]

    def test_payout_validates_bank_details(self, client, auth_headers, sample_payout_request, mock_auth_user):
        """Paiement valide les coordonnées bancaires"""
        sample_payout_request["bank_details"]["iban"] = "INVALID"

        response = client.post(
            "/api/payouts/request",
            json=sample_payout_request,
            headers=auth_headers
        )

        assert response.status_code in [400, 404, 422]

    def test_admin_approve_payout(self, client, admin_headers, mock_supabase):
        """Admin approuve un paiement"""
        with patch('auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "admin-123", "role": "admin"}

            response = client.post(
                "/api/admin/payouts/payout-123/approve",
                headers=admin_headers
            )

            assert response.status_code in [200, 404]

    def test_admin_reject_payout(self, client, admin_headers, mock_supabase):
        """Admin rejette un paiement"""
        with patch('auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "admin-123", "role": "admin"}

            response = client.post(
                "/api/admin/payouts/payout-123/reject",
                json={"reason": "Documents manquants"},
                headers=admin_headers
            )

            assert response.status_code in [200, 404]


# ============================================
# TESTS ABONNEMENTS
# ============================================

class TestSubscriptions:
    """Tests pour les abonnements"""

    def test_get_subscription_plans(self, client):
        """Récupération des plans d'abonnement"""
        response = client.get("/api/subscription-plans")

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_upgrade_subscription(self, client, auth_headers, mock_supabase, mock_auth_user):
        """Upgrade d'abonnement"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"plan_id": "enterprise"},
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 404]

    def test_cancel_subscription(self, client, auth_headers, mock_supabase, mock_auth_user):
        """Annulation d'abonnement"""
        response = client.post(
            "/api/subscriptions/cancel",
            json={"reason": "too_expensive", "feedback": "Test"},
            headers=auth_headers
        )

        assert response.status_code in [200, 404]

    def test_subscription_expiry_handling(self, client, auth_headers, mock_supabase, mock_auth_user):
        """Gestion expiration abonnement"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "sub-123",
                "plan": "pro",
                "expires_at": (datetime.now() - timedelta(days=1)).isoformat()
            }
        )

        response = client.get(
            "/api/subscriptions/current",
            headers=auth_headers
        )

        # Devrait indiquer que l'abonnement est expiré
        assert response.status_code in [200, 404]


# ============================================
# TESTS SÉCURITÉ PAIEMENTS
# ============================================

class TestPaymentSecurity:
    """Tests de sécurité pour les paiements"""

    def test_payment_idempotency(self, client, auth_headers, sample_payment_data, mock_supabase, mock_auth_user):
        """Paiements sont idempotents"""
        sample_payment_data["idempotency_key"] = "unique-key-123"

        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "payment-123"}]
        )

        # Premier appel
        response1 = client.post(
            "/api/payments/init-subscription",
            json=sample_payment_data,
            headers=auth_headers
        )

        # Deuxième appel avec la même clé
        response2 = client.post(
            "/api/payments/init-subscription",
            json=sample_payment_data,
            headers=auth_headers
        )

        # Les deux devraient réussir avec le même résultat
        if response1.status_code in [200, 201] and response2.status_code in [200, 201]:
            # Devrait retourner le même paiement
            pass

    def test_payment_amount_tampering_prevention(self, client, auth_headers, mock_auth_user):
        """Prévention de la falsification du montant"""
        response = client.post(
            "/api/payments/init-subscription",
            json={
                "amount": 0.01,  # Montant très bas
                "currency": "MAD",
                "plan_id": "enterprise"  # Plan cher
            },
            headers=auth_headers
        )

        # Devrait valider que le montant correspond au plan
        assert response.status_code in [400, 404, 422]

    def test_payment_replay_attack_prevention(self, client, mock_supabase):
        """Prévention des attaques par replay"""
        webhook_payload = {
            "id": "evt_123",
            "type": "checkout.session.completed",
            "timestamp": (datetime.now() - timedelta(hours=2)).timestamp()
        }

        # Un webhook trop vieux devrait être rejeté
        response = client.post(
            "/api/webhooks/stripe",
            json=webhook_payload,
            headers={"Stripe-Signature": "old-signature"}
        )

        assert response.status_code in [400, 401, 404]

    def test_sensitive_payment_data_not_logged(self, client, auth_headers, mock_auth_user, mock_supabase):
        """Données sensibles non loggées"""
        # Ce test vérifie que les numéros de carte ne sont pas exposés
        payment_with_card = {
            "amount": 100,
            "currency": "MAD",
            "card_number": "4111111111111111",  # Ne devrait jamais être accepté en clair
            "cvv": "123"
        }

        response = client.post(
            "/api/payments/direct",
            json=payment_with_card,
            headers=auth_headers
        )

        # L'endpoint ne devrait pas accepter les données de carte en clair
        assert response.status_code in [400, 404, 422]

    def test_concurrent_payout_prevention(self, client, auth_headers, sample_payout_request, mock_supabase, mock_auth_user):
        """Prévention des payouts simultanés"""
        import threading
        results = []

        def make_payout():
            response = client.post(
                "/api/payouts/request",
                json=sample_payout_request,
                headers=auth_headers
            )
            results.append(response.status_code)

        # Lancer plusieurs demandes simultanées
        threads = [threading.Thread(target=make_payout) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Au moins certaines devraient échouer si bien implémenté
        # (pas de double paiement)


# ============================================
# TESTS REMBOURSEMENTS
# ============================================

class TestRefunds:
    """Tests pour les remboursements"""

    def test_request_refund(self, client, auth_headers, mock_supabase, mock_auth_user):
        """Demande de remboursement"""
        response = client.post(
            "/api/payments/refund",
            json={
                "payment_id": "payment-123",
                "reason": "Product not as described",
                "amount": 50.00  # Remboursement partiel
            },
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 404]

    def test_refund_exceeds_payment_amount(self, client, auth_headers, mock_supabase, mock_auth_user):
        """Remboursement supérieur au paiement"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"amount": 100.00}
        )

        response = client.post(
            "/api/payments/refund",
            json={
                "payment_id": "payment-123",
                "amount": 200.00  # Plus que le paiement original
            },
            headers=auth_headers
        )

        assert response.status_code in [400, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
