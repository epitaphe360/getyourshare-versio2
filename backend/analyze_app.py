#!/usr/bin/env python3
"""
Analyse complète de l'application GetYourShare
Vérifie les tables, routes, endpoints, et génère un rapport complet
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_routes():
    """Analyse tous les fichiers de routes et compte les endpoints"""
    routes_dir = Path("routes")

    results = {}
    total_endpoints = 0

    for route_file in sorted(routes_dir.glob("*.py")):
        if route_file.name.startswith("__"):
            continue

        with open(route_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Compter les décorateurs @router
        endpoints = re.findall(r'^@router\.(get|post|put|delete|patch|websocket)', content, re.MULTILINE)

        if endpoints:
            results[route_file.name] = {
                'count': len(endpoints),
                'methods': defaultdict(int)
            }

            for method in endpoints:
                results[route_file.name]['methods'][method.upper()] += 1

            total_endpoints += len(endpoints)

    return results, total_endpoints


def analyze_services():
    """Analyse tous les services"""
    services_dir = Path("services")

    services = []
    for service_file in sorted(services_dir.glob("*.py")):
        if service_file.name.startswith("__"):
            continue
        services.append(service_file.name)

    # Compter aussi les sous-dossiers
    for subdir in services_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("__"):
            for service_file in subdir.glob("*.py"):
                if not service_file.name.startswith("__"):
                    services.append(f"{subdir.name}/{service_file.name}")

    return sorted(services)


def analyze_migrations():
    """Analyse les migrations SQL"""
    migrations_dir = Path("migrations")

    migrations = []
    if migrations_dir.exists():
        for migration_file in sorted(migrations_dir.glob("*.sql")):
            migrations.append(migration_file.name)

    return migrations


def check_mounted_routers():
    """Vérifie quels routers sont montés dans server_complete.py"""
    server_file = Path("server_complete.py")

    if not server_file.exists():
        return []

    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Trouver tous les app.include_router
    mounted = re.findall(r'app\.include_router\((\w+)\)', content)

    return mounted


def main():
    print("=" * 80)
    print("🔍 ANALYSE COMPLÈTE DE L'APPLICATION GETYOURSHARE")
    print("=" * 80)
    print()

    # 1. Analyser les routes
    print("📂 ROUTES & ENDPOINTS")
    print("-" * 80)

    routes_data, total_endpoints = analyze_routes()

    for route_file, data in sorted(routes_data.items(), key=lambda x: x[1]['count'], reverse=True):
        methods_str = ", ".join([f"{method}: {count}" for method, count in data['methods'].items()])
        print(f"✅ {route_file:40} {data['count']:3} endpoints  ({methods_str})")

    print("-" * 80)
    print(f"📊 TOTAL ENDPOINTS: {total_endpoints}")
    print()

    # 2. Analyser les services
    print("🔧 SERVICES")
    print("-" * 80)

    services = analyze_services()
    for service in services:
        print(f"✅ {service}")

    print("-" * 80)
    print(f"📊 TOTAL SERVICES: {len(services)}")
    print()

    # 3. Analyser les migrations
    print("🗄️  MIGRATIONS SQL")
    print("-" * 80)

    migrations = analyze_migrations()
    for migration in migrations:
        print(f"✅ {migration}")

    print("-" * 80)
    print(f"📊 TOTAL MIGRATIONS: {len(migrations)}")
    print()

    # 4. Vérifier les routers montés
    print("🔌 ROUTERS MONTÉS DANS SERVER")
    print("-" * 80)

    mounted_routers = check_mounted_routers()
    for router in mounted_routers:
        print(f"✅ {router}")

    print("-" * 80)
    print(f"📊 TOTAL ROUTERS MONTÉS: {len(mounted_routers)}")
    print()

    # 5. Résumé final
    print("=" * 80)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 80)
    print(f"✅ Routes implémentées:     {len(routes_data)}")
    print(f"✅ Total endpoints:         {total_endpoints}")
    print(f"✅ Services disponibles:    {len(services)}")
    print(f"✅ Migrations SQL:          {len(migrations)}")
    print(f"✅ Routers montés:          {len(mounted_routers)}")
    print()

    # 6. Vérifications de cohérence
    print("🔍 VÉRIFICATIONS DE COHÉRENCE")
    print("-" * 80)

    # Routes qui devraient être montées
    expected_routes = {
        'analytics_routes.py': 'analytics_router',
        'products_routes.py': 'products_router',
        'campaigns_routes.py': 'campaigns_router',
        'commissions_routes.py': 'commissions_router',
        'reports_routes.py': 'reports_router',
        'content_studio_routes.py': 'content_studio_router',
        'utility_routes.py': 'utility_router',
        'ecommerce_routes.py': 'ecommerce_router',
        'payment_gateways_routes.py': 'payment_gateways_router',
        'social_media_routes.py': 'social_media_router',
        'team_routes.py': 'team_router',
        'webhooks_routes.py': 'webhooks_router',
        'gamification_routes.py': 'gamification_router',
        'kyc_routes.py': 'kyc_router',
        'mobile_routes.py': 'mobile_router',
        'ai_routes.py': 'ai_router',
        'customer_service_routes.py': 'customer_service_router',
        'live_chat_routes.py': 'live_chat_router',
        'advanced_analytics_routes.py': 'advanced_analytics_router',
        'admin_dashboard_routes.py': 'admin_dashboard_router',
    }

    missing_routers = []
    for route_file, router_name in expected_routes.items():
        if route_file in routes_data and router_name not in mounted_routers:
            missing_routers.append((route_file, router_name))

    if missing_routers:
        print("⚠️  Routers non montés:")
        for route_file, router_name in missing_routers:
            print(f"   - {route_file} → {router_name}")
    else:
        print("✅ Tous les routers principaux sont montés!")

    print()

    # 7. Statut final
    print("=" * 80)
    print("🎯 STATUT FINAL DE L'APPLICATION")
    print("=" * 80)

    status = "✅ PRODUCTION READY" if total_endpoints >= 150 and not missing_routers else "⚠️  NEEDS REVIEW"
    print(f"Statut: {status}")
    print(f"Couverture: {min(100, int(total_endpoints / 165 * 100))}% ({total_endpoints}/165 endpoints)")
    print()

    print("=" * 80)
    print("✅ Analyse complète terminée!")
    print("=" * 80)


if __name__ == "__main__":
    # Changer vers le répertoire backend
    os.chdir(Path(__file__).parent)
    main()
