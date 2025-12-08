#!/usr/bin/env python3
"""
Database Migration Script
Applies SQL migrations to Supabase database
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from db_helpers import supabase
    print("✅ Connected to Supabase")
except ImportError as e:
    print(f"❌ Error importing db_helpers: {e}")
    print("\nMake sure you're in the backend directory and db_helpers.py exists")
    sys.exit(1)


def read_migration_file(filename):
    """Read a migration SQL file"""
    migration_path = Path(__file__).parent / filename

    if not migration_path.exists():
        print(f"❌ Migration file not found: {filename}")
        return None

    with open(migration_path, 'r', encoding='utf-8') as f:
        return f.read()


def apply_migration(filename):
    """Apply a migration to the database"""
    print(f"\n📄 Reading migration: {filename}")

    sql_content = read_migration_file(filename)
    if not sql_content:
        return False

    print(f"📊 Migration size: {len(sql_content)} characters")
    print(f"🚀 Applying migration...")

    try:
        # Execute SQL via Supabase
        # Note: Supabase Python client doesn't have direct SQL execution
        # We need to use the REST API or PostgREST

        print("\n⚠️  Direct SQL execution via Python client is limited.")
        print("\nPlease apply this migration using one of these methods:")
        print("\n1. Supabase Dashboard (RECOMMENDED):")
        print("   - Go to your Supabase project")
        print("   - Navigate to SQL Editor")
        print("   - Copy and paste the content of:")
        print(f"     {filename}")
        print("   - Click 'Run'")

        print("\n2. psql Command Line:")
        print(f"   psql 'postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres' -f migrations/{filename}")

        print("\n3. Supabase CLI:")
        print("   supabase db push")

        return True

    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False


def main():
    """Main migration script"""
    print("=" * 60)
    print("🗄️  GetYourShare Database Migration Tool")
    print("=" * 60)

    # List of migrations in order
    migrations = [
        "005_ensure_all_tables.sql",  # Recommended - idempotent
        # "004_fix_support_tickets_columns.sql",  # Only if needed
        # "003_add_missing_features_tables.sql",  # Legacy
    ]

    print("\n📋 Available Migrations:")
    for i, migration in enumerate(migrations, 1):
        print(f"   {i}. {migration}")

    print("\n" + "=" * 60)
    print("\n⚠️  IMPORTANT: Read the instructions below")
    print("=" * 60)

    # Show the recommended migration
    recommended = migrations[0]
    apply_migration(recommended)

    print("\n" + "=" * 60)
    print("✅ Migration instructions displayed above")
    print("=" * 60)

    # Display the SQL content for easy copying
    print("\n\n📝 SQL Content for Copy/Paste:")
    print("=" * 60)

    sql_content = read_migration_file(recommended)
    if sql_content:
        print("\n--- START OF SQL ---\n")
        print(sql_content)
        print("\n--- END OF SQL ---\n")

    print("=" * 60)
    print("\n✅ Copy the SQL above and paste it into Supabase SQL Editor")
    print("=" * 60)


if __name__ == "__main__":
    main()
