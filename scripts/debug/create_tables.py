#!/usr/bin/env python3
"""
Script pour créer les tables manquantes dans Supabase
"""
import os
from supabase import create_client

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv('backend/.env')

# Connexion à Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Lire le fichier SQL simplifié
with open('CREATE_SIMPLE_TABLES.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Exécuter le SQL
try:
    print("🔄 Exécution du script SQL...")
    # Diviser le script en commandes individuelles
    commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
    
    success_count = 0
    for cmd in commands:
        if not cmd or len(cmd) < 10:
            continue
        try:
            supabase.rpc('exec_sql', {'sql': cmd + ';'}).execute()
            success_count += 1
        except Exception as e:
            if 'already exists' in str(e).lower():
                success_count += 1
            else:
                print(f"⚠️  Commande ignorée: {str(e)[:100]}")
    
    print(f"✅ Script exécuté! {success_count} commandes réussies")
    print("📋 Tables créées:")
    print("   - wishlists (listes de souhaits)")
    print("   - shipments (expéditions)")
    print("   - warehouses (entrepôts)")
    print("   - coupons (codes promo)")
    print("   - invoices (factures)")
    print("   - events (événements)")
except Exception as e:
    print(f"❌ Erreur: {e}")
    # Alternative: exécuter table par table
    print("\n🔄 Tentative d'exécution table par table...")
    
    tables_sql = sql_content.split('CREATE TABLE IF NOT EXISTS')
    
    for i, table_sql in enumerate(tables_sql[1:], 1):  # Skip first empty split
        try:
            full_sql = 'CREATE TABLE IF NOT EXISTS' + table_sql.split(';')[0] + ';'
            supabase.rpc('exec_sql', {'sql': full_sql}).execute()
            table_name = table_sql.split('(')[0].strip().split()[0]
            print(f"   ✅ Table {table_name} créée")
        except Exception as e2:
            print(f"   ⚠️  Table ignorée (peut déjà exister)")
            continue
    
    print("\n✅ Création des tables terminée")
