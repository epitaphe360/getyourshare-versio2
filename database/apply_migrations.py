#!/usr/bin/env python3
"""
Script d'application automatique des migrations SQL vers Supabase

Usage:
    python apply_migrations.py                    # Applique toutes les migrations
    python apply_migrations.py --migration 001    # Applique une migration spécifique
    python apply_migrations.py --dry-run          # Simule sans exécuter
"""

import os
import sys
from pathlib import Path

# Tenter d'importer les dépendances optionnelles
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Charger les variables d'environnement depuis backend/.env
if DOTENV_AVAILABLE:
    backend_env = Path(__file__).parent.parent / "backend" / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

# Initialiser le client Supabase si disponible
supabase = None
if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Chemin des migrations
MIGRATIONS_DIR = Path(__file__).parent / "migrations_organized"

# Ordre d'exécution des migrations
MIGRATION_ORDER = [
    "001_base_schema.sql",
    "002_add_smtp_settings.sql",
    "003_add_email_verification.sql",
    "004_add_company_settings.sql",
    "005_add_all_settings_tables.sql",
    "006_create_subscription_and_support_tables.sql",
    "007_add_tracking_tables.sql",
    "008_cleanup_old_affiliation_system.sql",
    "009_add_affiliation_requests.sql",
    "010_modify_trackable_links_unified.sql",
    "011_add_payment_columns.sql",
    "012_add_payment_gateways.sql",
    "013_enable_2fa_for_all.sql",
    "015_add_services_to_affiliation.sql",
    "016_add_service_id_to_publications.sql",
    "021_add_transaction_functions.sql",
    "022_update_transaction_functions.sql",
]


def execute_sql(sql_content: str, migration_name: str, dry_run: bool = False) -> bool:
    """
    Exécute du SQL via l'API Supabase PostgREST

    Args:
        sql_content: Contenu SQL à exécuter
        migration_name: Nom de la migration (pour logging)
        dry_run: Si True, simule sans exécuter

    Returns:
        True si succès, False sinon
    """
    if dry_run:
        print(f"   [DRY-RUN] Simulation de l'exécution de {migration_name}")
        print(f"   SQL length: {len(sql_content)} caractères")
        return True

    try:
        # Supabase ne permet pas d'exécuter du SQL arbitraire via l'API client Python
        # On doit utiliser l'API REST directement
        import requests

        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }

        # Note: Cette approche nécessite que l'utilisateur exécute les migrations
        # manuellement via le SQL Editor de Supabase ou via psql
        print(f"   ⚠️  L'API Supabase Python ne supporte pas l'exécution directe de SQL")
        print(f"   📋 Veuillez copier le contenu de {migration_name} dans le SQL Editor de Supabase")
        return False

    except Exception as e:
        print(f"   ❌ Erreur lors de l'exécution: {e}")
        return False


def apply_migration(migration_file: str, dry_run: bool = False) -> bool:
    """
    Applique une migration spécifique

    Args:
        migration_file: Nom du fichier de migration
        dry_run: Si True, simule sans exécuter

    Returns:
        True si succès, False sinon
    """
    migration_path = MIGRATIONS_DIR / migration_file

    if not migration_path.exists():
        print(f"❌ Migration non trouvée: {migration_file}")
        return False

    print(f"\n{'📋' if dry_run else '🚀'} Application de {migration_file}...")

    # Lire le contenu du fichier SQL
    try:
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
    except Exception as e:
        print(f"❌ Erreur de lecture du fichier: {e}")
        return False

    # Ignorer les fichiers vides
    if not sql_content.strip():
        print(f"   ⏭️  Fichier vide, ignoré")
        return True

    # Afficher les instructions pour exécution manuelle
    print(f"   📄 Taille: {len(sql_content)} caractères")
    print(f"   📍 Chemin: {migration_path}")

    if dry_run:
        print(f"   ✅ [DRY-RUN] Migration simulée avec succès")
        return True

    # Instructions pour l'utilisateur
    print(f"\n   📋 INSTRUCTIONS:")
    print(f"   1. Ouvrez Supabase: {SUPABASE_URL.replace('//', '//app.')}")
    print(f"   2. Allez dans SQL Editor")
    print(f"   3. Créez une nouvelle query")
    print(f"   4. Copiez le contenu de: {migration_path}")
    print(f"   5. Exécutez la query")
    print(f"   6. Vérifiez qu'il n'y a pas d'erreurs\n")

    response = input(f"   Avez-vous exécuté cette migration avec succès? (o/n): ")
    return response.lower() in ['o', 'y', 'oui', 'yes']


def apply_all_migrations(dry_run: bool = False):
    """
    Applique toutes les migrations dans l'ordre

    Args:
        dry_run: Si True, simule sans exécuter
    """
    if not SUPABASE_URL:
        print("❌ ERREUR: Variable SUPABASE_URL non définie!")
        print("   Utilisez --generate-combined pour créer un fichier SQL unique à la place.")
        sys.exit(1)

    print("="*70)
    print("🗄️  MIGRATION SUPABASE - ShareYourSales")
    print("="*70)
    print(f"\n📍 Base de données: {SUPABASE_URL}")
    print(f"📁 Dossier migrations: {MIGRATIONS_DIR}")
    print(f"📋 Nombre de migrations: {len(MIGRATION_ORDER)}")

    if dry_run:
        print("\n⚠️  MODE DRY-RUN: Aucune modification ne sera effectuée\n")

    success_count = 0
    failed_migrations = []

    for i, migration_file in enumerate(MIGRATION_ORDER, 1):
        print(f"\n[{i}/{len(MIGRATION_ORDER)}] ", end="")

        success = apply_migration(migration_file, dry_run)

        if success:
            success_count += 1
            print(f"   ✅ Succès")
        else:
            failed_migrations.append(migration_file)
            print(f"   ❌ Échec")

            if not dry_run:
                response = input("\n   Continuer malgré l'erreur? (o/n): ")
                if response.lower() not in ['o', 'y', 'oui', 'yes']:
                    break

    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DE LA MIGRATION")
    print("="*70)
    print(f"✅ Succès: {success_count}/{len(MIGRATION_ORDER)}")

    if failed_migrations:
        print(f"❌ Échecs: {len(failed_migrations)}")
        print("\nMigrations échouées:")
        for migration in failed_migrations:
            print(f"  - {migration}")
    else:
        print("\n🎉 Toutes les migrations ont été appliquées avec succès!")

    print("\n" + "="*70)


def generate_single_migration_file():
    """
    Génère un fichier SQL unique avec toutes les migrations combinées
    """
    print("\n🔨 Génération d'un fichier de migration unique...")

    output_file = MIGRATIONS_DIR.parent / "ALL_MIGRATIONS_COMBINED.sql"

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("-- ============================================\n")
        out.write("-- MIGRATIONS COMPLÈTES - ShareYourSales\n")
        out.write("-- Généré automatiquement\n")
        out.write("-- ============================================\n\n")

        for migration_file in MIGRATION_ORDER:
            migration_path = MIGRATIONS_DIR / migration_file

            if not migration_path.exists():
                out.write(f"\n-- ❌ MIGRATION MANQUANTE: {migration_file}\n\n")
                continue

            out.write(f"\n-- ============================================\n")
            out.write(f"-- MIGRATION: {migration_file}\n")
            out.write(f"-- ============================================\n\n")

            with open(migration_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    out.write(content)
                    out.write("\n\n")
                else:
                    out.write("-- (fichier vide)\n\n")

    print(f"✅ Fichier généré: {output_file}")
    print(f"📄 Taille: {output_file.stat().st_size} octets")
    print(f"\n📋 Vous pouvez maintenant:")
    print(f"   1. Ouvrir {output_file}")
    print(f"   2. Copier tout le contenu")
    print(f"   3. Coller dans le SQL Editor de Supabase")
    print(f"   4. Exécuter en une seule fois\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Applique les migrations SQL vers Supabase")
    parser.add_argument("--migration", help="Applique une migration spécifique (ex: 001)")
    parser.add_argument("--dry-run", action="store_true", help="Simule sans exécuter")
    parser.add_argument("--generate-combined", action="store_true", help="Génère un fichier SQL unique avec toutes les migrations")

    args = parser.parse_args()

    if args.generate_combined:
        generate_single_migration_file()
    elif args.migration:
        # Trouver la migration correspondante
        migration_file = None
        for m in MIGRATION_ORDER:
            if m.startswith(args.migration):
                migration_file = m
                break

        if migration_file:
            apply_migration(migration_file, args.dry_run)
        else:
            print(f"❌ Migration non trouvée: {args.migration}")
            print(f"\nMigrations disponibles:")
            for m in MIGRATION_ORDER:
                print(f"  - {m}")
    else:
        apply_all_migrations(args.dry_run)
