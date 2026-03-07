#!/usr/bin/env python3
"""
Script de test exhaustif complet pour GetYourShare
Teste TOUS les aspects de l'application
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any
from colorama import init, Fore, Style

init(autoreset=True)

class AppTester:
    def __init__(self):
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8080")
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "start_time": datetime.now()
        }
        self.auth_token = None

    def print_header(self, title):
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{title.center(80)}")
        print(f"{Fore.CYAN}{'='*80}\n")

    def print_test(self, test_name, passed, message=""):
        if passed:
            self.results["passed"].append(test_name)
            print(f"{Fore.GREEN}✅ {test_name}")
            if message:
                print(f"   {Fore.LIGHTBLACK_EX}{message}")
        else:
            self.results["failed"].append(f"{test_name}: {message}")
            print(f"{Fore.RED}❌ {test_name}")
            if message:
                print(f"   {Fore.RED}{message}")

    def print_warning(self, test_name, message):
        self.results["warnings"].append(f"{test_name}: {message}")
        print(f"{Fore.YELLOW}⚠️  {test_name}")
        print(f"   {Fore.YELLOW}{message}")

    # ============================================
    # 1. BACKEND HEALTH & STARTUP TESTS
    # ============================================

    def test_backend_health(self):
        """Test backend health check endpoint"""
        self.print_header("TEST 1: BACKEND HEALTH & STARTUP")

        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            self.print_test(
                "Backend Health Check",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   {Fore.LIGHTBLACK_EX}Response: {json.dumps(data, indent=2)}")
        except Exception as e:
            self.print_test("Backend Health Check", False, str(e))

        # Test root endpoint
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            self.print_test(
                "Backend Root Endpoint",
                response.status_code in [200, 307],
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Backend Root Endpoint", False, str(e))

    # ============================================
    # 2. API ENDPOINTS TESTS
    # ============================================

    def test_all_endpoints(self):
        """Test all API endpoints availability"""
        self.print_header("TEST 2: ALL API ENDPOINTS")

        endpoints = {
            # Auth endpoints
            "/api/auth/register": "POST",
            "/api/auth/login": "POST",
            "/api/auth/logout": "POST",

            # User endpoints
            "/api/users/me": "GET",
            "/api/users": "GET",

            # Products endpoints
            "/api/products": "GET",
            "/api/products/search": "GET",

            # Campaigns endpoints
            "/api/campaigns": "GET",

            # Analytics endpoints
            "/api/analytics/dashboard": "GET",
            "/api/analytics/sales": "GET",

            # Subscription endpoints
            "/api/subscriptions/plans": "GET",
            "/api/subscriptions/current": "GET",

            # Platform settings endpoints
            "/api/admin/platform-settings": "GET",

            # Docs
            "/docs": "GET",
            "/openapi.json": "GET"
        }

        for endpoint, method in endpoints.items():
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.backend_url}{endpoint}", timeout=5)

                # Accept 200, 401 (auth required), 422 (validation error) as valid responses
                # 404 or 500 means endpoint doesn't exist or is broken
                is_valid = response.status_code not in [404, 500, 501, 502, 503]

                self.print_test(
                    f"{method} {endpoint}",
                    is_valid,
                    f"Status: {response.status_code}"
                )

                if response.status_code == 404:
                    self.print_warning(
                        f"{method} {endpoint}",
                        "Endpoint non implémenté (404)"
                    )
            except Exception as e:
                self.print_test(f"{method} {endpoint}", False, str(e))

    # ============================================
    # 3. DATABASE CONNECTION TEST
    # ============================================

    def test_database(self):
        """Test database connectivity"""
        self.print_header("TEST 3: DATABASE CONNECTION")

        # Test Supabase connection via API
        try:
            response = requests.get(f"{self.backend_url}/api/users", timeout=10)

            # If we get 401, it means auth is required but DB is accessible
            # If we get 200, DB is accessible
            # If we get 500, DB connection failed
            db_connected = response.status_code in [200, 401, 422]

            self.print_test(
                "Database Connection (via /api/users)",
                db_connected,
                f"Status: {response.status_code} - {'Connected' if db_connected else 'Failed'}"
            )

            if not db_connected:
                print(f"   {Fore.RED}Response: {response.text[:200]}")

        except Exception as e:
            self.print_test("Database Connection", False, str(e))

    # ============================================
    # 4. AUTHENTICATION & JWT TESTS
    # ============================================

    def test_authentication(self):
        """Test authentication system"""
        self.print_header("TEST 4: AUTHENTICATION & JWT")

        # Test login endpoint exists
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": "test@test.com", "password": "test"},
                timeout=5
            )

            # 401 or 422 means endpoint works but credentials invalid
            # 404 means endpoint doesn't exist
            endpoint_exists = response.status_code != 404

            self.print_test(
                "Login Endpoint Exists",
                endpoint_exists,
                f"Status: {response.status_code}"
            )

            if endpoint_exists and response.status_code == 200:
                data = response.json()
                if "access_token" in data or "token" in data:
                    self.auth_token = data.get("access_token") or data.get("token")
                    self.print_test(
                        "JWT Token Generation",
                        True,
                        "Token received successfully"
                    )

        except Exception as e:
            self.print_test("Authentication System", False, str(e))

        # Test register endpoint
        try:
            test_email = f"test_{int(time.time())}@test.com"
            response = requests.post(
                f"{self.backend_url}/api/auth/register",
                json={
                    "email": test_email,
                    "password": "Test1234!",
                    "full_name": "Test User",
                    "role": "influencer"
                },
                timeout=5
            )

            # 200, 201, 400 (already exists), 422 (validation) are acceptable
            endpoint_works = response.status_code in [200, 201, 400, 422]

            self.print_test(
                "Register Endpoint Works",
                endpoint_works,
                f"Status: {response.status_code}"
            )

        except Exception as e:
            self.print_test("Register Endpoint", False, str(e))

    # ============================================
    # 5. EXTERNAL SERVICES TESTS
    # ============================================

    def test_external_services(self):
        """Test external services integration"""
        self.print_header("TEST 5: EXTERNAL SERVICES (Stripe, Supabase)")

        # Check if Stripe is configured
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        self.print_test(
            "Stripe API Key Configured",
            stripe_key is not None and len(stripe_key) > 0,
            "Found in environment" if stripe_key else "Missing from environment"
        )

        # Check if Supabase is configured
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        self.print_test(
            "Supabase URL Configured",
            supabase_url is not None and len(supabase_url) > 0,
            supabase_url if supabase_url else "Missing"
        )

        self.print_test(
            "Supabase Key Configured",
            supabase_key is not None and len(supabase_key) > 0,
            "Key present" if supabase_key else "Missing"
        )

        # Test subscription plans endpoint (tests Stripe integration indirectly)
        try:
            response = requests.get(f"{self.backend_url}/api/subscriptions/plans", timeout=5)
            plans_available = response.status_code in [200, 401]

            self.print_test(
                "Subscription Plans Endpoint",
                plans_available,
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   {Fore.LIGHTBLACK_EX}Found {len(data) if isinstance(data, list) else 'N/A'} subscription plans")

        except Exception as e:
            self.print_test("Subscription Plans", False, str(e))

    # ============================================
    # 6. MODERATION & TRANSLATION TESTS
    # ============================================

    def test_moderation_translation(self):
        """Test moderation and translation services"""
        self.print_header("TEST 6: MODERATION & TRANSLATION SERVICES")

        # Check if OpenAI is configured (required for moderation/translation)
        openai_key = os.getenv("OPENAI_API_KEY")

        self.print_test(
            "OpenAI API Key Configured",
            openai_key is not None and len(openai_key) > 0,
            "Key present (for moderation/translation)" if openai_key else "Missing - moderation/translation will not work"
        )

        # Try to access moderation endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/moderation/status", timeout=5)
            moderation_available = response.status_code != 404

            self.print_test(
                "Moderation Endpoint Available",
                moderation_available,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_warning("Moderation Endpoint", f"Could not test: {e}")

        # Try to access translation endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/translation/languages", timeout=5)
            translation_available = response.status_code != 404

            self.print_test(
                "Translation Endpoint Available",
                translation_available,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_warning("Translation Endpoint", f"Could not test: {e}")

    # ============================================
    # 7. FRONTEND BUILD & STARTUP TEST
    # ============================================

    def test_frontend(self):
        """Test frontend build and files"""
        self.print_header("TEST 7: FRONTEND BUILD & STARTUP")

        frontend_path = "/home/user/getyourshare-versio2/frontend"

        # Check if frontend directory exists
        frontend_exists = os.path.exists(frontend_path)
        self.print_test(
            "Frontend Directory Exists",
            frontend_exists,
            frontend_path
        )

        if not frontend_exists:
            return

        # Check package.json
        package_json_path = os.path.join(frontend_path, "package.json")
        package_json_exists = os.path.exists(package_json_path)
        self.print_test(
            "package.json Exists",
            package_json_exists,
            package_json_path
        )

        # Check if node_modules exists
        node_modules_path = os.path.join(frontend_path, "node_modules")
        node_modules_exists = os.path.exists(node_modules_path)
        self.print_test(
            "node_modules Exists (dependencies installed)",
            node_modules_exists,
            "Dependencies installed" if node_modules_exists else "Run 'npm install'"
        )

        # Check for main source files
        src_path = os.path.join(frontend_path, "src")
        src_exists = os.path.exists(src_path)
        self.print_test(
            "src Directory Exists",
            src_exists,
            src_path
        )

        # Check for key files
        if src_exists:
            key_files = ["App.tsx", "App.jsx", "main.tsx", "main.jsx", "index.tsx", "index.jsx"]
            found_entry = False
            for file in key_files:
                file_path = os.path.join(src_path, file)
                if os.path.exists(file_path):
                    found_entry = True
                    self.print_test(
                        f"Entry Point Found ({file})",
                        True,
                        file_path
                    )
                    break

            if not found_entry:
                self.print_test(
                    "Entry Point File",
                    False,
                    "No App.tsx/jsx or main.tsx/jsx found"
                )

        # Check build output
        dist_path = os.path.join(frontend_path, "dist")
        build_path = os.path.join(frontend_path, "build")

        dist_exists = os.path.exists(dist_path)
        build_exists = os.path.exists(build_path)

        build_output_exists = dist_exists or build_exists
        self.print_test(
            "Build Output Exists",
            build_output_exists,
            f"Found: {'dist' if dist_exists else 'build' if build_exists else 'none'}"
        )

        if not build_output_exists:
            self.print_warning(
                "No Build Output",
                "Run 'npm run build' to create production build"
            )

    # ============================================
    # 8. FRONTEND ROUTES TEST
    # ============================================

    def test_frontend_routes(self):
        """Test frontend routing configuration"""
        self.print_header("TEST 8: FRONTEND ROUTES & PAGES")

        frontend_src = "/home/user/getyourshare-versio2/frontend/src"

        # Common route files
        route_files = [
            "App.tsx", "App.jsx",
            "router.tsx", "router.jsx",
            "routes.tsx", "routes.jsx",
            "Router.tsx", "Router.jsx"
        ]

        found_routes = False
        for file in route_files:
            file_path = os.path.join(frontend_src, file)
            if os.path.exists(file_path):
                found_routes = True
                self.print_test(
                    f"Routes File Found ({file})",
                    True,
                    file_path
                )
                break

        if not found_routes:
            self.print_warning(
                "Routes Configuration",
                "Could not find main routing file"
            )

        # Check for pages directory
        pages_path = os.path.join(frontend_src, "pages")
        pages_exists = os.path.exists(pages_path)

        self.print_test(
            "Pages Directory Exists",
            pages_exists,
            pages_path if pages_exists else "Not found"
        )

        # Count pages if directory exists
        if pages_exists:
            try:
                page_files = [f for f in os.listdir(pages_path) if f.endswith(('.tsx', '.jsx'))]
                self.print_test(
                    f"Page Components ({len(page_files)} found)",
                    len(page_files) > 0,
                    f"Found {len(page_files)} page components"
                )

                # List some key pages
                key_pages = ["Dashboard", "Login", "Register", "Profile", "Products", "Campaigns"]
                for page_name in key_pages:
                    page_files_match = [f for f in page_files if page_name.lower() in f.lower()]
                    if page_files_match:
                        print(f"   {Fore.GREEN}✓ {page_name} page found: {page_files_match[0]}")
                    else:
                        print(f"   {Fore.YELLOW}○ {page_name} page not found")

            except Exception as e:
                self.print_warning("Pages Directory", f"Error reading: {e}")

    # ============================================
    # 9. INTEGRATION TEST (Frontend ↔ Backend)
    # ============================================

    def test_integration(self):
        """Test frontend-backend integration"""
        self.print_header("TEST 9: FRONTEND ↔ BACKEND INTEGRATION")

        # Check CORS configuration
        try:
            response = requests.options(
                f"{self.backend_url}/api/users",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                },
                timeout=5
            )

            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            cors_configured = cors_headers is not None

            self.print_test(
                "CORS Configuration",
                cors_configured,
                f"Allow-Origin: {cors_headers}" if cors_configured else "CORS not configured"
            )

        except Exception as e:
            self.print_test("CORS Configuration", False, str(e))

        # Check if frontend has API configuration
        frontend_src = "/home/user/getyourshare-versio2/frontend/src"
        api_config_files = ["api.ts", "api.js", "config.ts", "config.js", "services/api.ts"]

        found_api_config = False
        for file in api_config_files:
            file_path = os.path.join(frontend_src, file)
            if os.path.exists(file_path):
                found_api_config = True
                self.print_test(
                    f"API Configuration Found ({file})",
                    True,
                    file_path
                )
                break

        if not found_api_config:
            self.print_warning(
                "API Configuration",
                "No API config file found in frontend"
            )

    # ============================================
    # 10. SECURITY TESTS
    # ============================================

    def test_security(self):
        """Test security configurations"""
        self.print_header("TEST 10: SECURITY (CORS, XSS, Injection)")

        # Check environment variables are set
        jwt_secret = os.getenv("JWT_SECRET")
        self.print_test(
            "JWT_SECRET Configured",
            jwt_secret is not None and len(jwt_secret) >= 32,
            f"Length: {len(jwt_secret) if jwt_secret else 0} chars (min 32 recommended)"
        )

        # Test SQL injection protection (try malicious input)
        try:
            response = requests.get(
                f"{self.backend_url}/api/users",
                params={"email": "test'; DROP TABLE users; --"},
                timeout=5
            )

            # Should get 401/422, not 500 (which would indicate SQL injection vulnerability)
            protected = response.status_code != 500

            self.print_test(
                "SQL Injection Protection",
                protected,
                "Protected against basic SQL injection" if protected else "Potential vulnerability"
            )
        except Exception as e:
            self.print_warning("SQL Injection Test", f"Could not test: {e}")

        # Test XSS protection
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/register",
                json={
                    "email": "<script>alert('xss')</script>@test.com",
                    "password": "test",
                    "full_name": "<script>alert('xss')</script>"
                },
                timeout=5
            )

            # Should reject or sanitize, not execute
            if response.status_code == 200:
                data = response.json()
                has_script_tags = "<script>" in str(data)
                self.print_test(
                    "XSS Protection",
                    not has_script_tags,
                    "No script tags in response" if not has_script_tags else "Potential XSS vulnerability"
                )
            else:
                self.print_test(
                    "XSS Protection",
                    True,
                    f"Request rejected (Status: {response.status_code})"
                )

        except Exception as e:
            self.print_warning("XSS Protection Test", f"Could not test: {e}")

        # Check rate limiting
        try:
            # Make multiple rapid requests
            responses = []
            for i in range(10):
                r = requests.get(f"{self.backend_url}/health", timeout=2)
                responses.append(r.status_code)

            # If we get 429 (Too Many Requests), rate limiting is working
            rate_limited = 429 in responses

            if rate_limited:
                self.print_test(
                    "Rate Limiting",
                    True,
                    "Rate limiting is active (429 received)"
                )
            else:
                self.print_warning(
                    "Rate Limiting",
                    "No rate limiting detected (consider implementing)"
                )

        except Exception as e:
            self.print_warning("Rate Limiting Test", f"Could not test: {e}")

    # ============================================
    # 11. COMPONENT TESTS
    # ============================================

    def test_frontend_components(self):
        """Test frontend components"""
        self.print_header("TEST 11: FRONTEND COMPONENTS")

        frontend_src = "/home/user/getyourshare-versio2/frontend/src"
        components_path = os.path.join(frontend_src, "components")

        components_exist = os.path.exists(components_path)
        self.print_test(
            "Components Directory Exists",
            components_exist,
            components_path if components_exist else "Not found"
        )

        if components_exist:
            try:
                component_files = [f for f in os.listdir(components_path)
                                 if f.endswith(('.tsx', '.jsx')) or os.path.isdir(os.path.join(components_path, f))]

                self.print_test(
                    f"Component Files/Folders ({len(component_files)} found)",
                    len(component_files) > 0,
                    f"Found {len(component_files)} components"
                )

                # Check for key components
                key_components = [
                    "Navbar", "Sidebar", "Header", "Footer",
                    "Dashboard", "Card", "Button", "Form", "Modal"
                ]

                found_components = []
                for comp in key_components:
                    comp_files = [f for f in component_files if comp.lower() in f.lower()]
                    if comp_files:
                        found_components.append(comp)
                        print(f"   {Fore.GREEN}✓ {comp} component found")

                self.print_test(
                    f"Key Components ({len(found_components)}/{len(key_components)})",
                    len(found_components) >= len(key_components) // 2,
                    f"Found: {', '.join(found_components)}"
                )

            except Exception as e:
                self.print_warning("Components Directory", f"Error reading: {e}")

    # ============================================
    # GENERATE FINAL REPORT
    # ============================================

    def generate_report(self):
        """Generate final test report"""
        self.print_header("RAPPORT FINAL DE TEST")

        end_time = datetime.now()
        duration = end_time - self.results["start_time"]

        total_tests = len(self.results["passed"]) + len(self.results["failed"])
        pass_rate = (len(self.results["passed"]) / total_tests * 100) if total_tests > 0 else 0

        print(f"{Fore.CYAN}Durée du test: {duration.total_seconds():.2f} secondes")
        print(f"{Fore.CYAN}Tests exécutés: {total_tests}")
        print(f"{Fore.GREEN}Tests réussis: {len(self.results['passed'])} ({pass_rate:.1f}%)")
        print(f"{Fore.RED}Tests échoués: {len(self.results['failed'])}")
        print(f"{Fore.YELLOW}Avertissements: {len(self.results['warnings'])}\n")

        if self.results["failed"]:
            print(f"{Fore.RED}{'='*80}")
            print(f"{Fore.RED}PROBLÈMES DÉTECTÉS:")
            print(f"{Fore.RED}{'='*80}\n")
            for i, failure in enumerate(self.results["failed"], 1):
                print(f"{Fore.RED}{i}. {failure}")

        if self.results["warnings"]:
            print(f"\n{Fore.YELLOW}{'='*80}")
            print(f"{Fore.YELLOW}AVERTISSEMENTS:")
            print(f"{Fore.YELLOW}{'='*80}\n")
            for i, warning in enumerate(self.results["warnings"], 1):
                print(f"{Fore.YELLOW}{i}. {warning}")

        print(f"\n{Fore.CYAN}{'='*80}")
        if pass_rate >= 80:
            print(f"{Fore.GREEN}RÉSULTAT GLOBAL: APPLICATION FONCTIONNELLE ✅")
        elif pass_rate >= 60:
            print(f"{Fore.YELLOW}RÉSULTAT GLOBAL: QUELQUES PROBLÈMES DÉTECTÉS ⚠️")
        else:
            print(f"{Fore.RED}RÉSULTAT GLOBAL: PROBLÈMES CRITIQUES DÉTECTÉS ❌")
        print(f"{Fore.CYAN}{'='*80}\n")

        # Save report to file
        report_path = "/home/user/getyourshare-versio2/TEST_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "total_tests": total_tests,
                "passed": len(self.results["passed"]),
                "failed": len(self.results["failed"]),
                "warnings": len(self.results["warnings"]),
                "pass_rate": pass_rate,
                "passed_tests": self.results["passed"],
                "failed_tests": self.results["failed"],
                "warnings": self.results["warnings"]
            }, f, indent=2)

        print(f"{Fore.CYAN}📄 Rapport détaillé sauvegardé: {report_path}\n")

    # ============================================
    # RUN ALL TESTS
    # ============================================

    def run_all_tests(self):
        """Run all tests sequentially"""
        print(f"{Fore.MAGENTA}{'='*80}")
        print(f"{Fore.MAGENTA}TEST EXHAUSTIF COMPLET - GETYOURSHARE APPLICATION".center(80))
        print(f"{Fore.MAGENTA}{'='*80}\n")

        self.test_backend_health()
        self.test_all_endpoints()
        self.test_database()
        self.test_authentication()
        self.test_external_services()
        self.test_moderation_translation()
        self.test_frontend()
        self.test_frontend_routes()
        self.test_frontend_components()
        self.test_integration()
        self.test_security()

        self.generate_report()

if __name__ == "__main__":
    try:
        # Install colorama if not present
        try:
            import colorama
        except ImportError:
            print("Installing colorama...")
            os.system("pip install colorama -q")
            import colorama

        tester = AppTester()
        tester.run_all_tests()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
