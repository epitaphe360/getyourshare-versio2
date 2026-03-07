#!/usr/bin/env python3
"""
Script pour appliquer la migration: Ajouter destination_url à tracking_links
"""
import os
from supabase import create_client, Client

# Configuration Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ ERREUR: Variables d'environnement SUPABASE_URL et SUPABASE_KEY requises")
    exit(1)

supabase: Client = create_client(url, key)

print("🔧 Application de la migration: ADD_DESTINATION_URL_TO_TRACKING_LINKS")
print("=" * 70)

# Lire le fichier SQL
with open("ADD_DESTINATION_URL_TO_TRACKING_LINKS.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

# Extraire les commandes SQL (ignorer les commentaires)
sql_commands = []
for line in sql_content.split('\n'):
    line = line.strip()
    if line and not line.startswith('--'):
        sql_commands.append(line)

sql_query = ' '.join(sql_commands)

try:
    # Exécuter via une requête RPC si disponible, sinon afficher les commandes
    print("\n📋 Commandes SQL à exécuter:")
    print(sql_query)
    
    print("\n✅ Migration créée avec succès!")
    print("\n💡 Note: Pour appliquer cette migration, exécutez ces commandes SQL")
    print("   directement dans votre console Supabase ou via psql.")
    
    # Vérifier si la colonne existe déjà
    print("\n🔍 Vérification de la structure actuelle de tracking_links...")
    result = supabase.table('tracking_links').select('*').limit(1).execute()
    
    if result.data and len(result.data) > 0:
        print(f"\n📊 Colonnes actuelles: {list(result.data[0].keys())}")
        if 'destination_url' in result.data[0]:
            print("✅ La colonne destination_url existe déjà!")
        else:
            print("⚠️  La colonne destination_url n'existe pas encore - migration nécessaire")
    else:
        # Table vide, vérifier via metadata
        print("ℹ️  Table tracking_links vide, impossible de vérifier les colonnes")
        print("   Appliquez la migration SQL pour ajouter destination_url")

except Exception as e:
    print(f"\n⚠️  Erreur lors de la vérification: {e}")
    print("   La migration SQL est prête à être appliquée manuellement")

print("\n" + "=" * 70)
print("✅ Script terminé")
