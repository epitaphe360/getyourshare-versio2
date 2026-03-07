#!/usr/bin/env python3
"""
Script d'installation automatique du Dashboard Commercial
Exécute les 2 scripts SQL nécessaires dans Supabase
"""

import os
from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://gwgvnusegnnhiciprvyc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3Z3ZudXNlZ25uaGljaXBydnljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MjE3NjgsImV4cCI6MjA0NjM5Nzc2OH0.gftLI_u0AxQUVIUi3hWjfJQ-m6Y56b5H5lDwbMEDGbU")

def read_sql_file(filename):
    """Lit le contenu d'un fichier SQL"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé: {filepath}")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def execute_sql(supabase: Client, sql_content: str, description: str):
    """Exécute un script SQL via Supabase"""
    print(f"\n{'='*60}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    try:
        # Supabase Python client ne supporte pas l'exécution SQL directe
        # Il faut utiliser l'API REST ou le SQL Editor
        print("⚠️  NOTE: Le client Python Supabase ne peut pas exécuter du SQL brut.")
        print("   Vous devez utiliser l'une de ces méthodes:")
        print()
        print("   MÉTHODE 1: SQL Editor (RECOMMANDÉ)")
        print("   1. Ouvrir: https://app.supabase.com/project/gwgvnusegnnhiciprvyc/sql/new")
        print(f"   2. Copier le contenu de: {description}")
        print("   3. Cliquer sur 'RUN'")
        print()
        print("   MÉTHODE 2: Via psql (si vous avez PostgreSQL installé)")
        print("   psql 'postgresql://postgres:[PASSWORD]@db.gwgvnusegnnhiciprvyc.supabase.co:5432/postgres' < fichier.sql")
        print()
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║   🚀 INSTALLATION DASHBOARD COMMERCIAL - Tracknow.io        ║
║   Installation des tables et données de test                ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialiser Supabase
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connexion à Supabase établie")
    except Exception as e:
        print(f"❌ Erreur de connexion à Supabase: {e}")
        return
    
    # Étape 1: Ajouter la colonne subscription_tier
    print("\n" + "="*60)
    print("ÉTAPE 1/2: Ajouter la colonne subscription_tier")
    print("="*60)
    
    sql1 = read_sql_file("ADD_SUBSCRIPTION_TIER_COLUMN.sql")
    if sql1:
        print("\n📄 Contenu du fichier ADD_SUBSCRIPTION_TIER_COLUMN.sql:")
        print("-" * 60)
        print(sql1[:500] + "..." if len(sql1) > 500 else sql1)
        print("-" * 60)
        execute_sql(supabase, sql1, "ADD_SUBSCRIPTION_TIER_COLUMN.sql")
    
    # Étape 2: Insérer les données
    print("\n" + "="*60)
    print("ÉTAPE 2/2: Insérer les données de test")
    print("="*60)
    
    sql2 = read_sql_file("INSERT_COMMERCIAL_DATA.sql")
    if sql2:
        print("\n📄 Contenu du fichier INSERT_COMMERCIAL_DATA.sql:")
        print("-" * 60)
        print(f"Taille: {len(sql2)} caractères")
        print("Première ligne:", sql2.split('\n')[0])
        print("-" * 60)
        execute_sql(supabase, sql2, "INSERT_COMMERCIAL_DATA.sql")
    
    # Instructions finales
    print("\n" + "="*60)
    print("📋 PROCHAINES ÉTAPES")
    print("="*60)
    print()
    print("1️⃣  Exécuter les 2 scripts SQL dans Supabase SQL Editor:")
    print("    https://app.supabase.com/project/gwgvnusegnnhiciprvyc/sql/new")
    print()
    print("2️⃣  Démarrer le backend:")
    print("    cd backend")
    print("    python server.py")
    print()
    print("3️⃣  Démarrer le frontend:")
    print("    cd frontend")
    print("    npm start")
    print()
    print("4️⃣  Tester avec les comptes:")
    print("    • commercial.starter@tracknow.io / Test123!")
    print("    • commercial.pro@tracknow.io / Test123!")
    print("    • commercial.enterprise@tracknow.io / Test123!")
    print()
    print("📖 Voir COMMERCIAL_DASHBOARD_QUICK_START.md pour plus de détails")
    print()

if __name__ == "__main__":
    main()
