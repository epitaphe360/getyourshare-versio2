#!/usr/bin/env python3
"""
Analyse l'intégration des endpoints backend dans le frontend
Compare les endpoints disponibles vs utilisés dans les dashboards
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def extract_api_calls_from_file(file_path):
    """Extrait les appels API d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Patterns pour trouver les endpoints
        patterns = [
            r'[\'"`]/api/([a-zA-Z0-9_/-]+)[\'"`]',  # '/api/...'
            r'axios\.(get|post|put|delete|patch)\([\'"`]/api/([a-zA-Z0-9_/-]+)',
            r'fetch\([\'"`]/api/([a-zA-Z0-9_/-]+)',
            r'url:\s*[\'"`]/api/([a-zA-Z0-9_/-]+)',
            r'endpoint:\s*[\'"`]/api/([a-zA-Z0-9_/-]+)',
        ]

        endpoints = set()
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    endpoint = match[-1] if match[-1] else match[0]
                else:
                    endpoint = match

                # Nettoyer l'endpoint
                endpoint = endpoint.strip().strip('/')
                if endpoint and not endpoint.startswith('${') and '...' not in endpoint:
                    endpoints.add(endpoint)

        return endpoints
    except Exception as e:
        return set()


def analyze_frontend():
    """Analyse le frontend pour trouver tous les endpoints utilisés"""
    frontend_dir = Path("frontend/src")

    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return {}

    print("🔍 Scanning frontend files...")

    all_endpoints = defaultdict(list)
    dashboard_files = []

    for root, dirs, files in os.walk(frontend_dir):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                file_path = Path(root) / file
                endpoints = extract_api_calls_from_file(file_path)

                if endpoints:
                    relative_path = file_path.relative_to(frontend_dir)
                    for endpoint in endpoints:
                        all_endpoints[endpoint].append(str(relative_path))

                # Identifier les fichiers dashboard
                if 'dashboard' in file.lower() or 'Dashboard' in file:
                    dashboard_files.append(str(file_path.relative_to(frontend_dir)))

    return all_endpoints, dashboard_files


def get_backend_endpoints():
    """Liste les endpoints du backend basés sur les routes"""
    backend_routes = {
        # Core Business
        'analytics': ['overview', 'conversions', 'revenue', 'top-products', 'top-influencers', 'conversion-rate', 'geography', 'time-series'],
        'products': ['', '{id}', '{id}/analytics', '{id}/generate-link', 'categories', 'search', 'bulk-upload', 'import-csv', 'export', '{id}/duplicate', '{id}/variations'],
        'campaigns': ['', '{id}', '{id}/activate', '{id}/pause', '{id}/analytics', '{id}/influencers', '{id}/invite-influencers'],
        'commissions': ['', 'pending', 'calculate', 'pay/{id}'],
        'reports': ['sales', 'conversions', 'commissions', 'export/pdf', 'export/excel'],

        # AI & Advanced
        'ai': ['recommendations/for-you', 'recommendations/collaborative', 'recommendations/content-based', 'recommendations/hybrid', 'recommendations/trending', 'recommendations/similar/{id}', 'chatbot', 'chatbot/history', 'insights'],
        'advanced-analytics': ['cohorts', 'rfm-analysis', 'segments', 'ab-tests', 'ab-tests/{id}/results', 'ab-tests/{id}/assign', 'ab-tests/{id}/stop'],

        # Support & Collaboration
        'support': ['tickets', 'tickets/{id}', 'tickets/{id}/reply', 'tickets/{id}/status', 'tickets/{id}/priority', 'tickets/{id}/assign', 'tickets/{id}/close', 'stats', 'categories'],
        'live-chat': ['ws/{user_id}', 'rooms', 'rooms/{id}/history', 'rooms/{id}/participants', 'rooms/{id}/mark-read'],
        'team': ['roles', 'permissions', 'members', 'invite', 'invitations', 'invitations/{id}/cancel', 'invitations/accept', 'members/{id}/role', 'members/{id}', 'activity'],

        # E-commerce & Payments
        'ecommerce': ['shopify/connect', 'woocommerce/connect', 'prestashop/connect', 'shopify/sync-products', 'woocommerce/sync-products', 'connected', '{platform}/disconnect'],
        'payments': ['stripe/create-checkout', 'stripe/verify-payment', 'paypal/create-order', 'paypal/execute-payment', 'crypto/create-payment', 'crypto/status/{id}', 'transactions', 'transactions/{id}'],
        'webhooks': ['stripe', 'shopify', 'woocommerce', 'paypal', 'logs'],

        # Engagement
        'gamification': ['badges', 'badges/earned', 'achievements', 'points', 'leaderboard'],
        'kyc': ['upload-documents', 'status', 'verify', 'admin/pending', 'admin/approve/{id}', 'admin/reject/{id}'],
        'social-media': ['{platform}/connect', 'connections', 'posts/create', 'posts', 'posts/{id}/analytics', '{platform}/disconnect'],

        # Mobile
        'whatsapp': ['send', 'webhook', 'messages'],
        'mobile-payments-ma': ['orange-money', 'inwi-money', 'maroc-telecom', 'transactions', 'webhook'],

        # Admin
        'admin': ['stats/overview', 'stats/revenue-trend', 'users', 'users/{id}', 'users/{id}/action', 'moderation/queue', 'moderation/moderate', 'system/health', 'system/logs', 'system/errors', 'audit-logs'],

        # Content & Utilities
        'content-studio': ['generate-caption', 'generate-hashtags', 'schedule-post', 'scheduled-posts', 'scheduled-posts/{id}', 'upload-media', 'media-library', 'create-template'],
    }

    return backend_routes


def main():
    print("=" * 80)
    print("🔍 ANALYSE D'INTÉGRATION FRONTEND ↔ BACKEND")
    print("=" * 80)
    print()

    # Analyser le frontend
    frontend_endpoints, dashboard_files = analyze_frontend()

    print(f"📊 Fichiers Frontend analysés")
    print(f"   Dashboards trouvés: {len(dashboard_files)}")
    print(f"   Endpoints API uniques utilisés: {len(frontend_endpoints)}")
    print()

    # Liste des dashboards
    print("📋 DASHBOARDS IDENTIFIÉS")
    print("-" * 80)
    for dashboard in sorted(dashboard_files):
        print(f"   ✅ {dashboard}")
    print()

    # Endpoints backend disponibles
    backend_routes = get_backend_endpoints()
    total_backend_endpoints = sum(len(endpoints) for endpoints in backend_routes.values())

    print(f"📊 ENDPOINTS BACKEND DISPONIBLES: {total_backend_endpoints}")
    print("-" * 80)
    for category, endpoints in sorted(backend_routes.items()):
        print(f"   {category:30} {len(endpoints):3} endpoints")
    print()

    # Endpoints frontend utilisés
    print(f"📊 ENDPOINTS UTILISÉS DANS LE FRONTEND: {len(frontend_endpoints)}")
    print("-" * 80)

    # Grouper par catégorie
    categorized_frontend = defaultdict(list)
    for endpoint in sorted(frontend_endpoints):
        category = endpoint.split('/')[0] if '/' in endpoint else endpoint
        categorized_frontend[category].append(endpoint)

    for category in sorted(categorized_frontend.keys()):
        endpoints = categorized_frontend[category]
        print(f"   {category:30} {len(endpoints):3} endpoints")
    print()

    # Comparaison détaillée
    print("=" * 80)
    print("📊 COMPARAISON DÉTAILLÉE PAR CATÉGORIE")
    print("=" * 80)
    print()

    all_categories = set(backend_routes.keys()) | set(categorized_frontend.keys())

    for category in sorted(all_categories):
        backend_count = len(backend_routes.get(category, []))
        frontend_count = len(categorized_frontend.get(category, []))

        if backend_count > 0:
            coverage = (frontend_count / backend_count * 100) if backend_count > 0 else 0
            status = "✅" if coverage >= 50 else "⚠️" if coverage >= 25 else "❌"

            print(f"{status} {category:30} Backend: {backend_count:3} | Frontend: {frontend_count:3} | {coverage:5.1f}%")
    print()

    # Endpoints manquants (backend disponible mais pas utilisé)
    print("=" * 80)
    print("⚠️  ENDPOINTS BACKEND NON UTILISÉS DANS LE FRONTEND")
    print("=" * 80)
    print()

    missing_count = 0
    for category, backend_endpoints in sorted(backend_routes.items()):
        frontend_used = categorized_frontend.get(category, [])

        # Simplifier la comparaison
        frontend_simple = set(e.split('/')[-1] for e in frontend_used)

        missing = []
        for endpoint in backend_endpoints:
            # Simplifier le nom du endpoint backend
            simple_endpoint = endpoint.split('/')[-1].replace('{id}', '').replace('{user_id}', '').replace('{platform}', '')

            # Vérifier si utilisé
            found = False
            for fe in frontend_simple:
                if simple_endpoint in fe or fe in simple_endpoint:
                    found = True
                    break

            if not found and simple_endpoint:
                missing.append(endpoint)

        if missing:
            print(f"📂 {category}")
            for endpoint in missing:
                print(f"   ❌ /api/{category}/{endpoint}")
                missing_count += 1
            print()

    if missing_count == 0:
        print("✅ Tous les endpoints backend principaux sont utilisés dans le frontend!")
    else:
        print(f"Total: {missing_count} endpoints backend non utilisés")

    print()

    # Résumé final
    print("=" * 80)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 80)
    print(f"Dashboards identifiés:          {len(dashboard_files)}")
    print(f"Endpoints backend disponibles:  {total_backend_endpoints}")
    print(f"Endpoints utilisés frontend:    {len(frontend_endpoints)}")
    print(f"Taux d'utilisation:             {len(frontend_endpoints) / total_backend_endpoints * 100:.1f}%")
    print()

    # Recommandations
    print("=" * 80)
    print("💡 RECOMMANDATIONS")
    print("=" * 80)
    print()

    if len(frontend_endpoints) < total_backend_endpoints * 0.5:
        print("⚠️  Le frontend n'utilise que {}% des endpoints backend".format(
            int(len(frontend_endpoints) / total_backend_endpoints * 100)
        ))
        print("   Recommandation: Intégrer davantage d'endpoints dans les dashboards")
        print()

    print("Endpoints prioritaires à intégrer:")
    priority_endpoints = [
        "ai/recommendations/for-you",
        "gamification/leaderboard",
        "support/tickets",
        "live-chat/rooms",
        "advanced-analytics/rfm-analysis",
        "admin/stats/overview",
    ]

    for endpoint in priority_endpoints:
        category, path = endpoint.split('/', 1)
        if category in categorized_frontend:
            status = "✅ Déjà intégré"
        else:
            status = "❌ À intégrer"
        print(f"   {status} - /api/{endpoint}")

    print()
    print("=" * 80)
    print("✅ Analyse terminée!")
    print("=" * 80)


if __name__ == "__main__":
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    main()
