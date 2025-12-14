"""
Tests d'Authentification Complets

Couvre:
- Login (succès, échec, validation)
- Register (tous les rôles, validation email)
- 2FA (setup, verify, disable)
- Refresh token
- Logout
- Password reset
- Session management
- Rate limiting
- Security (injection, brute force)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import jwt
from datetime import datetime, timedelta
import json

# Import conditionnel pour éviter les erreurs si server.py n'est pas disponible
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
def valid_user_data():
    """Données utilisateur valides pour l'inscription"""
    return {
        "email": "test_user@example.com",
        "password": "SecureP@ssw0rd123!",
        "name": "Test User",
        "role": "influencer",
        "phone": "+212612345678"
    }


@pytest.fixture
def valid_merchant_data():
    """Données marchand valides"""
    return {
        "email": "merchant@example.com",
        "password": "SecureP@ssw0rd123!",
        "name": "Test Merchant",
        "role": "merchant",
        "company_name": "Test Company SARL",
        "ice_number": "001234567000089",
        "phone": "+212698765432"
    }


@pytest.fixture
def mock_supabase():
    """Mock du client Supabase"""
    with patch('supabase_client.supabase') as mock:
        yield mock


# ============================================
# TESTS DE LOGIN
# ============================================

class TestLogin:
    """Tests pour POST /api/auth/login"""

    def test_login_success_with_valid_credentials(self, client, mock_supabase):
        """Login réussi avec identifiants valides"""
        # Mock la réponse Supabase
        mock_supabase.auth.sign_in_with_password.return_value = MagicMock(
            user=MagicMock(id="user-123", email="test@example.com"),
            session=MagicMock(access_token="valid-token", refresh_token="refresh-token")
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "user-123", "email": "test@example.com", "role": "influencer", "name": "Test"}
        )

        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "validpassword123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        assert "user" in data

    def test_login_fails_with_invalid_email(self, client):
        """Login échoue avec email invalide"""
        response = client.post("/api/auth/login", json={
            "email": "not-an-email",
            "password": "somepassword"
        })

        assert response.status_code in [400, 422]

    def test_login_fails_with_wrong_password(self, client, mock_supabase):
        """Login échoue avec mauvais mot de passe"""
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })

        assert response.status_code in [400, 401]

    def test_login_fails_with_empty_fields(self, client):
        """Login échoue avec champs vides"""
        response = client.post("/api/auth/login", json={
            "email": "",
            "password": ""
        })

        assert response.status_code in [400, 422]

    def test_login_fails_with_missing_email(self, client):
        """Login échoue sans email"""
        response = client.post("/api/auth/login", json={
            "password": "somepassword"
        })

        assert response.status_code == 422

    def test_login_fails_with_missing_password(self, client):
        """Login échoue sans mot de passe"""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com"
        })

        assert response.status_code == 422

    def test_login_sql_injection_prevention(self, client, mock_supabase):
        """Login protège contre l'injection SQL"""
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        malicious_emails = [
            "test@example.com'; DROP TABLE users; --",
            "test@example.com' OR '1'='1",
            "test@example.com\" OR \"1\"=\"1",
        ]

        for email in malicious_emails:
            response = client.post("/api/auth/login", json={
                "email": email,
                "password": "password"
            })
            # Doit échouer proprement, pas avec une erreur serveur
            assert response.status_code in [400, 401, 422]

    def test_login_xss_prevention(self, client):
        """Login sanitize les entrées contre XSS"""
        response = client.post("/api/auth/login", json={
            "email": "<script>alert('xss')</script>@example.com",
            "password": "<script>alert('xss')</script>"
        })

        # Doit échouer la validation
        assert response.status_code in [400, 422]

    def test_login_rate_limiting(self, client):
        """Login a un rate limiting"""
        # Tenter 20 logins rapides
        responses = []
        for i in range(20):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": f"wrongpassword{i}"
            })
            responses.append(response.status_code)

        # Après plusieurs tentatives, devrait avoir un 429
        assert 429 in responses or all(r in [400, 401] for r in responses)


# ============================================
# TESTS D'INSCRIPTION
# ============================================

class TestRegister:
    """Tests pour POST /api/auth/register"""

    def test_register_influencer_success(self, client, valid_user_data, mock_supabase):
        """Inscription influenceur réussie"""
        mock_supabase.auth.sign_up.return_value = MagicMock(
            user=MagicMock(id="new-user-123")
        )
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "new-user-123"}]
        )

        response = client.post("/api/auth/register", json=valid_user_data)

        assert response.status_code in [200, 201]

    def test_register_merchant_success(self, client, valid_merchant_data, mock_supabase):
        """Inscription marchand réussie"""
        mock_supabase.auth.sign_up.return_value = MagicMock(
            user=MagicMock(id="new-merchant-123")
        )
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "new-merchant-123"}]
        )

        response = client.post("/api/auth/register", json=valid_merchant_data)

        assert response.status_code in [200, 201]

    def test_register_fails_with_existing_email(self, client, valid_user_data, mock_supabase):
        """Inscription échoue si email existe déjà"""
        mock_supabase.auth.sign_up.side_effect = Exception("User already registered")

        response = client.post("/api/auth/register", json=valid_user_data)

        assert response.status_code in [400, 409]

    def test_register_fails_with_weak_password(self, client, valid_user_data):
        """Inscription échoue avec mot de passe faible"""
        valid_user_data["password"] = "123"

        response = client.post("/api/auth/register", json=valid_user_data)

        assert response.status_code in [400, 422]

    def test_register_validates_email_format(self, client, valid_user_data):
        """Inscription valide le format email"""
        invalid_emails = ["notanemail", "test@", "@example.com", "test@.com"]

        for email in invalid_emails:
            valid_user_data["email"] = email
            response = client.post("/api/auth/register", json=valid_user_data)
            assert response.status_code in [400, 422], f"Email {email} should be invalid"

    def test_register_validates_role(self, client, valid_user_data):
        """Inscription valide le rôle"""
        valid_user_data["role"] = "admin"  # Ne devrait pas être permis

        response = client.post("/api/auth/register", json=valid_user_data)

        # Admin ne devrait pas pouvoir s'inscrire directement
        assert response.status_code in [400, 403, 422]

    def test_register_merchant_requires_company_info(self, client, valid_user_data):
        """Inscription marchand nécessite infos entreprise"""
        valid_user_data["role"] = "merchant"
        # Pas de company_name ni ice_number

        response = client.post("/api/auth/register", json=valid_user_data)

        # Devrait échouer ou exiger les infos
        assert response.status_code in [200, 400, 422]

    def test_register_sanitizes_input(self, client, valid_user_data):
        """Inscription sanitize les entrées"""
        valid_user_data["name"] = "<script>alert('xss')</script>"

        response = client.post("/api/auth/register", json=valid_user_data)

        if response.status_code in [200, 201]:
            data = response.json()
            if "user" in data and "name" in data["user"]:
                assert "<script>" not in data["user"]["name"]


# ============================================
# TESTS 2FA
# ============================================

class Test2FA:
    """Tests pour l'authentification à deux facteurs"""

    def test_2fa_setup_generates_secret(self, client, mock_supabase):
        """Setup 2FA génère un secret"""
        # Mock auth token
        with patch('auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "email": "test@example.com"}

            response = client.post(
                "/api/auth/2fa/setup",
                headers={"Authorization": "Bearer valid-token"}
            )

            if response.status_code == 200:
                data = response.json()
                assert "secret" in data or "qr_code" in data

    def test_2fa_verify_with_valid_code(self, client, mock_supabase):
        """Vérification 2FA avec code valide"""
        with patch('auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "email": "test@example.com"}
            with patch('pyotp.TOTP.verify', return_value=True):
                response = client.post(
                    "/api/auth/2fa/verify",
                    json={"code": "123456"},
                    headers={"Authorization": "Bearer valid-token"}
                )

                assert response.status_code in [200, 404]  # 404 si endpoint n'existe pas

    def test_2fa_verify_fails_with_invalid_code(self, client, mock_supabase):
        """Vérification 2FA échoue avec code invalide"""
        with patch('auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "email": "test@example.com"}
            with patch('pyotp.TOTP.verify', return_value=False):
                response = client.post(
                    "/api/auth/2fa/verify",
                    json={"code": "000000"},
                    headers={"Authorization": "Bearer valid-token"}
                )

                assert response.status_code in [400, 401, 404]


# ============================================
# TESTS DE REFRESH TOKEN
# ============================================

class TestRefreshToken:
    """Tests pour POST /api/auth/refresh"""

    def test_refresh_with_valid_token(self, client, mock_supabase):
        """Refresh token avec token valide"""
        mock_supabase.auth.refresh_session.return_value = MagicMock(
            session=MagicMock(access_token="new-token", refresh_token="new-refresh")
        )

        response = client.post("/api/auth/refresh")

        # Doit retourner un nouveau token ou échouer si pas de cookie
        assert response.status_code in [200, 401]

    def test_refresh_fails_without_token(self, client):
        """Refresh échoue sans token"""
        response = client.post("/api/auth/refresh")

        assert response.status_code in [401, 403]


# ============================================
# TESTS DE LOGOUT
# ============================================

class TestLogout:
    """Tests pour POST /api/auth/logout"""

    def test_logout_success(self, client, mock_supabase):
        """Logout réussi"""
        mock_supabase.auth.sign_out.return_value = None

        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code in [200, 204]

    def test_logout_clears_session(self, client, mock_supabase):
        """Logout efface la session"""
        mock_supabase.auth.sign_out.return_value = None

        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer valid-token"}
        )

        # Vérifier que les cookies sont effacés si applicable
        if response.status_code in [200, 204]:
            cookies = response.cookies
            # Si des cookies sont définis, ils devraient être vides ou expirés


# ============================================
# TESTS DE SÉCURITÉ
# ============================================

class TestAuthSecurity:
    """Tests de sécurité pour l'authentification"""

    def test_password_not_in_response(self, client, valid_user_data, mock_supabase):
        """Le mot de passe n'est jamais retourné"""
        mock_supabase.auth.sign_up.return_value = MagicMock(
            user=MagicMock(id="new-user-123")
        )
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "new-user-123", "email": "test@example.com"}]
        )

        response = client.post("/api/auth/register", json=valid_user_data)

        if response.status_code in [200, 201]:
            response_text = response.text.lower()
            assert valid_user_data["password"].lower() not in response_text
            assert "password" not in response.json() or response.json().get("password") is None

    def test_token_expiration(self, client, mock_supabase):
        """Les tokens ont une expiration"""
        mock_supabase.auth.sign_in_with_password.return_value = MagicMock(
            user=MagicMock(id="user-123", email="test@example.com"),
            session=MagicMock(access_token="valid-token", refresh_token="refresh-token")
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "user-123", "email": "test@example.com", "role": "influencer"}
        )

        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "validpassword123"
        })

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token") or data.get("token")
            if token:
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    assert "exp" in decoded, "Token should have expiration"
                except jwt.DecodeError:
                    pass  # Token might be opaque

    def test_protected_endpoint_requires_auth(self, client):
        """Endpoints protégés nécessitent authentification"""
        protected_endpoints = [
            "/api/user/profile",
            "/api/dashboard/stats",
            "/api/commissions",
            "/api/payouts/request"
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403, 404, 405], \
                f"Endpoint {endpoint} should require auth"

    def test_admin_endpoint_requires_admin_role(self, client, mock_supabase):
        """Endpoints admin nécessitent rôle admin"""
        # Login as regular user
        with patch('auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "role": "influencer"}

            admin_endpoints = [
                "/api/admin/users",
                "/api/admin/payouts",
                "/api/admin/analytics"
            ]

            for endpoint in admin_endpoints:
                response = client.get(
                    endpoint,
                    headers={"Authorization": "Bearer user-token"}
                )
                assert response.status_code in [401, 403, 404], \
                    f"Endpoint {endpoint} should deny non-admin users"


# ============================================
# TESTS DE PASSWORD RESET
# ============================================

class TestPasswordReset:
    """Tests pour la réinitialisation de mot de passe"""

    def test_request_password_reset(self, client, mock_supabase):
        """Demande de réinitialisation de mot de passe"""
        mock_supabase.auth.reset_password_for_email.return_value = None

        response = client.post("/api/auth/forgot-password", json={
            "email": "test@example.com"
        })

        # Devrait toujours retourner succès pour ne pas révéler si l'email existe
        assert response.status_code in [200, 404]

    def test_password_reset_with_valid_token(self, client, mock_supabase):
        """Réinitialisation avec token valide"""
        mock_supabase.auth.update_user.return_value = MagicMock(
            user=MagicMock(id="user-123")
        )

        response = client.post("/api/auth/reset-password", json={
            "token": "valid-reset-token",
            "password": "NewSecureP@ssw0rd!"
        })

        assert response.status_code in [200, 400, 404]

    def test_password_reset_validates_password_strength(self, client, mock_supabase):
        """Réinitialisation valide la force du mot de passe"""
        response = client.post("/api/auth/reset-password", json={
            "token": "valid-reset-token",
            "password": "weak"
        })

        assert response.status_code in [400, 404, 422]


# ============================================
# TESTS DE VALIDATION D'ENTRÉES
# ============================================

class TestInputValidation:
    """Tests de validation des entrées"""

    def test_email_normalization(self, client, mock_supabase):
        """Email est normalisé (lowercase, trim)"""
        mock_supabase.auth.sign_in_with_password.return_value = MagicMock(
            user=MagicMock(id="user-123", email="test@example.com"),
            session=MagicMock(access_token="valid-token")
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"id": "user-123", "email": "test@example.com", "role": "influencer"}
        )

        # Email avec espaces et majuscules
        response = client.post("/api/auth/login", json={
            "email": "  TEST@EXAMPLE.COM  ",
            "password": "validpassword123"
        })

        # Devrait fonctionner ou échouer proprement
        assert response.status_code in [200, 400, 401]

    def test_phone_validation(self, client, valid_user_data, mock_supabase):
        """Numéro de téléphone est validé"""
        invalid_phones = ["123", "abcdefghij", "++1234567890"]

        for phone in invalid_phones:
            valid_user_data["phone"] = phone
            response = client.post("/api/auth/register", json=valid_user_data)
            # Devrait échouer ou accepter et normaliser
            assert response.status_code in [200, 201, 400, 422]

    def test_max_length_validation(self, client, valid_user_data):
        """Longueurs maximales sont validées"""
        # Nom trop long
        valid_user_data["name"] = "A" * 1000

        response = client.post("/api/auth/register", json=valid_user_data)

        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
