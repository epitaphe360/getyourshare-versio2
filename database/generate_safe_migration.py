#!/usr/bin/env python3
"""
Génère une version SAFE (idempotente) des migrations SQL
- Ajoute IF NOT EXISTS à toutes les CREATE TABLE
- Ajoute CREATE OR REPLACE pour les fonctions
- Utilise ALTER TABLE ... ADD COLUMN IF NOT EXISTS

Usage:
    python generate_safe_migration.py
"""

import re
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations_organized"
OUTPUT_FILE = Path(__file__).parent / "SAFE_MIGRATIONS_IDEMPOTENT.sql"

# Ordre des migrations
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

def make_idempotent(sql_content: str, migration_name: str) -> str:
    """
    Transforme du SQL pour le rendre idempotent
    """
    lines = sql_content.split('\n')
    result = []

    for line in lines:
        line_upper = line.strip().upper()

        # CREATE TABLE -> CREATE TABLE IF NOT EXISTS
        if line_upper.startswith('CREATE TABLE ') and 'IF NOT EXISTS' not in line_upper:
            line = re.sub(
                r'CREATE TABLE\s+',
                'CREATE TABLE IF NOT EXISTS ',
                line,
                flags=re.IGNORECASE
            )

        # CREATE INDEX -> CREATE INDEX IF NOT EXISTS
        elif line_upper.startswith('CREATE INDEX ') and 'IF NOT EXISTS' not in line_upper:
            line = re.sub(
                r'CREATE INDEX\s+',
                'CREATE INDEX IF NOT EXISTS ',
                line,
                flags=re.IGNORECASE
            )

        # CREATE UNIQUE INDEX -> CREATE UNIQUE INDEX IF NOT EXISTS
        elif line_upper.startswith('CREATE UNIQUE INDEX ') and 'IF NOT EXISTS' not in line_upper:
            line = re.sub(
                r'CREATE UNIQUE INDEX\s+',
                'CREATE UNIQUE INDEX IF NOT EXISTS ',
                line,
                flags=re.IGNORECASE
            )

        # CREATE FUNCTION -> CREATE OR REPLACE FUNCTION
        elif line_upper.startswith('CREATE FUNCTION ') and 'OR REPLACE' not in line_upper:
            line = re.sub(
                r'CREATE FUNCTION\s+',
                'CREATE OR REPLACE FUNCTION ',
                line,
                flags=re.IGNORECASE
            )

        # CREATE TRIGGER -> DROP IF EXISTS + CREATE TRIGGER
        elif line_upper.startswith('CREATE TRIGGER '):
            # Extraire le nom du trigger
            match = re.search(r'CREATE TRIGGER\s+(\w+)', line, re.IGNORECASE)
            if match:
                trigger_name = match.group(1)
                table_match = re.search(r'ON\s+(\w+)', line, re.IGNORECASE)
                if table_match:
                    table_name = table_match.group(1)
                    result.append(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};")

        # ALTER TABLE ADD COLUMN -> ALTER TABLE ADD COLUMN IF NOT EXISTS
        # Note: PostgreSQL supporte IF NOT EXISTS depuis la version 9.6
        elif 'ALTER TABLE' in line_upper and 'ADD COLUMN' in line_upper:
            if 'IF NOT EXISTS' not in line_upper:
                line = re.sub(
                    r'ADD COLUMN\s+',
                    'ADD COLUMN IF NOT EXISTS ',
                    line,
                    flags=re.IGNORECASE
                )

        # DROP TABLE -> DROP TABLE IF EXISTS
        elif line_upper.startswith('DROP TABLE ') and 'IF EXISTS' not in line_upper:
            line = re.sub(
                r'DROP TABLE\s+',
                'DROP TABLE IF EXISTS ',
                line,
                flags=re.IGNORECASE
            )

        result.append(line)

    return '\n'.join(result)

def main():
    print("="*70)
    print("🔨 GÉNÉRATION DE MIGRATIONS IDEMPOTENTES (SAFE)")
    print("="*70)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write("-- ============================================\n")
        out.write("-- MIGRATIONS IDEMPOTENTES (SAFE) - ShareYourSales\n")
        out.write("-- Généré automatiquement\n")
        out.write("-- Peut être exécuté plusieurs fois sans erreur\n")
        out.write("-- ============================================\n\n")

        success_count = 0

        for i, migration_file in enumerate(MIGRATION_ORDER, 1):
            migration_path = MIGRATIONS_DIR / migration_file

            print(f"\n[{i}/{len(MIGRATION_ORDER)}] {migration_file}...", end=" ")

            if not migration_path.exists():
                print("❌ MANQUANT")
                out.write(f"\n-- ❌ MIGRATION MANQUANTE: {migration_file}\n\n")
                continue

            with open(migration_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                print("⏭️  VIDE")
                out.write(f"\n-- ⏭️  MIGRATION VIDE: {migration_file}\n\n")
                continue

            # Transformer en version idempotente
            safe_content = make_idempotent(content, migration_file)

            out.write(f"\n-- ============================================\n")
            out.write(f"-- MIGRATION: {migration_file}\n")
            out.write(f"-- Rendu idempotent (IF NOT EXISTS, OR REPLACE)\n")
            out.write(f"-- ============================================\n\n")
            out.write(safe_content)
            out.write("\n\n")

            success_count += 1
            print("✅")

    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    print(f"✅ Migrations traitées: {success_count}/{len(MIGRATION_ORDER)}")
    print(f"📄 Fichier généré: {OUTPUT_FILE}")
    print(f"📐 Taille: {OUTPUT_FILE.stat().st_size:,} octets")

    print("\n📋 INSTRUCTIONS:")
    print("   1. Ouvrir Supabase SQL Editor")
    print(f"   2. Copier le contenu de: {OUTPUT_FILE}")
    print("   3. Coller et exécuter")
    print("   4. Ce fichier peut être exécuté PLUSIEURS FOIS sans erreur")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()
