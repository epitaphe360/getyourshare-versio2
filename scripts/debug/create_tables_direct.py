#!/usr/bin/env python3
"""
Script pour créer les tables manquantes directement avec psycopg2
"""
import os
import psycopg2
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('backend/.env')

# Construire l'URL de connexion PostgreSQL depuis l'URL Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

# URL de connexion PostgreSQL (remplacer par votre vraie URL de DB)
# Format: postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
db_url = os.getenv('DATABASE_URL', '')

if not db_url:
    print("❌ DATABASE_URL non trouvée dans .env")
    print("💡 Veuillez exécuter ce SQL manuellement dans Supabase SQL Editor:")
    print("\n" + "="*60)
    with open('CREATE_SIMPLE_TABLES.sql', 'r', encoding='utf-8') as f:
        print(f.read())
    print("="*60)
    exit(0)

try:
    # Connexion à la base de données
    print("🔄 Connexion à PostgreSQL...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Lire le script SQL
    with open('CREATE_SIMPLE_TABLES.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Exécuter le script
    print("🔄 Exécution du script SQL...")
    cursor.execute(sql_script)
    conn.commit()
    
    print("✅ Script exécuté avec succès!")
    print("📋 Tables créées:")
    print("   - wishlists (listes de souhaits)")
    print("   - shipments (expéditions)")
    print("   - warehouses (entrepôts)")
    print("   - coupons (codes promo)")
    print("   - invoices (factures)")
    print("   - events (événements)")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\n💡 Veuillez copier ce SQL et l'exécuter manuellement dans Supabase:")
    print("\n" + "="*60)
    with open('CREATE_SIMPLE_TABLES.sql', 'r', encoding='utf-8') as f:
        print(f.read())
    print("="*60)
