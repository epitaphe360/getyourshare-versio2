#!/usr/bin/env python3
"""
Script pour vérifier les tables existantes dans Supabase
et identifier quelles migrations sont nécessaires

Usage:
    python check_existing_tables.py
"""

import os
import sys
from pathlib import Path

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv
    backend_env = Path(__file__).parent.parent / "backend" / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
except ImportError:
    pass

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("❌ Module 'supabase' non installé")
    print("   Installez-le avec: pip install supabase")
    sys.exit(1)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Variables d'environnement manquantes!")
    print("   SUPABASE_URL et SUPABASE_SERVICE_KEY doivent être définis")
    sys.exit(1)

# Initialiser le client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Tables attendues par catégorie
EXPECTED_TABLES = {
    "Core": ["users", "merchants", "influencers"],
    "Products": ["products", "services", "product_categories"],
    "Campaigns": ["campaigns", "campaign_products", "campaign_settings"],
    "Tracking": ["tracking_links", "conversions", "click_tracking", "affiliate_links"],
    "Sales": ["sales", "commissions", "payouts"],
    "Subscriptions": ["subscription_plans", "subscriptions", "user_subscriptions"],
    "Payments": ["invoices", "payments", "payment_methods", "payment_gateways"],
    "Settings": ["platform_settings", "settings", "company_settings"],
    "Support": ["support_tickets", "ticket_messages"],
    "Other": ["notifications", "user_sessions", "webhook_logs"]
}

def check_table_exists(table_name: str) -> bool:
    """Vérifie si une table existe dans Supabase"""
    try:
        # Essayer de faire un count sur la table
        result = supabase.table(table_name).select("*", count="exact").limit(0).execute()
        return True
    except Exception as e:
        # Si erreur "table does not exist", retourner False
        if "does not exist" in str(e).lower() or "relation" in str(e).lower():
            return False
        # Autre erreur, considérer que la table existe mais a des problèmes de permissions
        return True

def main():
    print("="*70)
    print("🔍 DIAGNOSTIC DES TABLES SUPABASE")
    print("="*70)
    print(f"\n📍 Base de données: {SUPABASE_URL}")
    print("\n" + "="*70)

    all_tables = []
    for category, tables in EXPECTED_TABLES.items():
        all_tables.extend(tables)

    existing_tables = []
    missing_tables = []

    print("\n🔍 Vérification des tables...\n")

    for category, tables in EXPECTED_TABLES.items():
        print(f"📂 {category}:")
        for table in tables:
            exists = check_table_exists(table)
            status = "✅" if exists else "❌"
            print(f"   {status} {table}")

            if exists:
                existing_tables.append(table)
            else:
                missing_tables.append(table)

    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    print(f"✅ Tables existantes: {len(existing_tables)}/{len(all_tables)}")
    print(f"❌ Tables manquantes: {len(missing_tables)}/{len(all_tables)}")

    if missing_tables:
        print(f"\n⚠️  TABLES MANQUANTES:")
        for table in missing_tables:
            print(f"   - {table}")

        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   1. Générer un fichier de migration incrémentale:")
        print(f"      python generate_incremental_migration.py")
        print(f"   2. Ou exécuter les migrations manquantes manuellement")
    else:
        print("\n🎉 Toutes les tables principales existent!")

    print("\n" + "="*70)

    # Retourner le nombre de tables manquantes comme code de sortie
    sys.exit(len(missing_tables))

if __name__ == "__main__":
    main()
