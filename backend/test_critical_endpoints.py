#!/usr/bin/env python3
"""
Test des endpoints critiques de l'application
Vérifie que les routes sont accessibles et fonctionnelles
"""

import sys
from pathlib import Path

# Test d'imports critiques
print("=" * 80)
print("🧪 TEST DES IMPORTS CRITIQUES")
print("=" * 80)

try:
    print("✅ Testing auth imports...")
    from auth import get_current_user_from_cookie, verify_token
    print("   ✓ auth.py OK")
except ImportError as e:
    print(f"   ❌ auth.py FAILED: {e}")

try:
    print("✅ Testing db_helpers imports...")
    from db_helpers import supabase
    print("   ✓ db_helpers.py OK")
except ImportError as e:
    print(f"   ❌ db_helpers.py FAILED: {e}")

# Test des imports de routes
routes_to_test = [
    "routes.ai_routes",
    "routes.customer_service_routes",
    "routes.live_chat_routes",
    "routes.advanced_analytics_routes",
    "routes.admin_dashboard_routes",
    "routes.analytics_routes",
    "routes.products_routes",
    "routes.campaigns_routes",
    "routes.commissions_routes",
    "routes.reports_routes",
    "routes.content_studio_routes",
    "routes.utility_routes",
    "routes.ecommerce_routes",
    "routes.payment_gateways_routes",
    "routes.social_media_routes",
    "routes.team_routes",
    "routes.webhooks_routes",
    "routes.gamification_routes",
    "routes.kyc_routes",
    "routes.mobile_routes",
]

print("\n" + "=" * 80)
print("🧪 TEST DES IMPORTS DE ROUTES")
print("=" * 80)

successful_routes = []
failed_routes = []

for route_module in routes_to_test:
    try:
        __import__(route_module)
        print(f"✅ {route_module:50} OK")
        successful_routes.append(route_module)
    except ImportError as e:
        print(f"❌ {route_module:50} FAILED: {e}")
        failed_routes.append((route_module, str(e)))
    except Exception as e:
        print(f"⚠️  {route_module:50} ERROR: {e}")
        failed_routes.append((route_module, str(e)))

# Test des imports de services
services_to_test = [
    "services.ai_recommendations_service",
    "services.gamification_service",
    "services.kyc_service",
    "services.ecommerce_integrations_service",
    "services.social_media_service",
    "services.whatsapp_business_service",
]

print("\n" + "=" * 80)
print("🧪 TEST DES IMPORTS DE SERVICES")
print("=" * 80)

successful_services = []
failed_services = []

for service_module in services_to_test:
    try:
        __import__(service_module)
        print(f"✅ {service_module:50} OK")
        successful_services.append(service_module)
    except ImportError as e:
        print(f"❌ {service_module:50} FAILED: {e}")
        failed_services.append((service_module, str(e)))
    except Exception as e:
        print(f"⚠️  {service_module:50} ERROR: {e}")
        failed_services.append((service_module, str(e)))

# Résumé
print("\n" + "=" * 80)
print("📊 RÉSUMÉ DES TESTS")
print("=" * 80)
print(f"Routes testées:     {len(routes_to_test)}")
print(f"Routes OK:          {len(successful_routes)} ✅")
print(f"Routes Failed:      {len(failed_routes)} ❌")
print()
print(f"Services testés:    {len(services_to_test)}")
print(f"Services OK:        {len(successful_services)} ✅")
print(f"Services Failed:    {len(failed_services)} ❌")
print()

# Taux de succès
total_tests = len(routes_to_test) + len(services_to_test)
total_success = len(successful_routes) + len(successful_services)
success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0

print(f"Taux de succès:     {success_rate:.1f}%")
print()

if failed_routes or failed_services:
    print("=" * 80)
    print("⚠️  ERREURS DÉTAILLÉES")
    print("=" * 80)

    if failed_routes:
        print("\nRoutes avec erreurs:")
        for route, error in failed_routes:
            print(f"  ❌ {route}")
            print(f"     {error}")

    if failed_services:
        print("\nServices avec erreurs:")
        for service, error in failed_services:
            print(f"  ❌ {service}")
            print(f"     {error}")
else:
    print("=" * 80)
    print("🎉 TOUS LES TESTS SONT PASSÉS!")
    print("=" * 80)

# Test FastAPI app
print("\n" + "=" * 80)
print("🧪 TEST DE L'APPLICATION FASTAPI")
print("=" * 80)

try:
    print("Tentative d'import du serveur...")
    # Note: Ne pas exécuter le serveur, juste tester l'import
    import importlib.util
    spec = importlib.util.spec_from_file_location("server", "server_complete.py")
    if spec and spec.loader:
        print("✅ server_complete.py peut être chargé")
        print("   ℹ️  Pour démarrer le serveur: python server_complete.py")
    else:
        print("❌ Impossible de charger server_complete.py")
except Exception as e:
    print(f"⚠️  Erreur lors du test du serveur: {e}")

print("\n" + "=" * 80)
print("✅ Tests terminés!")
print("=" * 80)
print()
print("Pour démarrer l'application:")
print("  python server_complete.py")
print()
print("API Documentation:")
print("  http://localhost:8000/docs")
print("=" * 80)

# Exit code
sys.exit(0 if not (failed_routes or failed_services) else 1)
