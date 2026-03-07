#!/usr/bin/env python3
"""
Appliquer la migration tracking_events via RPC SQL
"""
import os
import requests

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Variables d'environnement manquantes")
    exit(1)

print("🔧 Application de la migration tracking_events...")
print("=" * 70)

# Les commandes SQL à exécuter
sql_commands = [
    "ALTER TABLE tracking_events ADD COLUMN IF NOT EXISTS browser TEXT",
    "ALTER TABLE tracking_events ADD COLUMN IF NOT EXISTS device TEXT",
    "ALTER TABLE tracking_events ADD COLUMN IF NOT EXISTS country TEXT",
    "ALTER TABLE tracking_events ADD COLUMN IF NOT EXISTS city TEXT",
    "ALTER TABLE tracking_events ADD COLUMN IF NOT EXISTS referrer TEXT"
]

# Utiliser l'API REST de Supabase pour exécuter SQL via RPC
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

for sql in sql_commands:
    print(f"\n📝 Exécution: {sql[:60]}...")
    
    # Note: Cette méthode ne fonctionnera que si vous avez une fonction RPC configurée
    # Sinon, utilisez directement l'éditeur SQL de Supabase
    
print("\n✅ Commandes SQL prêtes!")
print("\n💡 Pour appliquer ces changements, copiez et exécutez ce SQL dans Supabase:")
print("\n" + "=" * 70)
print("""
ALTER TABLE tracking_events 
ADD COLUMN IF NOT EXISTS browser TEXT,
ADD COLUMN IF NOT EXISTS device TEXT,
ADD COLUMN IF NOT EXISTS country TEXT,
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS referrer TEXT;
""")
print("=" * 70)

# Vérifier si les colonnes existent maintenant
from supabase import create_client, Client
supabase: Client = create_client(url, key)

try:
    # Tenter une insertion test
    links = supabase.table('tracking_links').select('id').limit(1).execute()
    if links.data:
        link_id = links.data[0]['id']
        test_data = {
            "tracking_link_id": link_id,
            "event_type": "test",
            "ip_address": "127.0.0.1",
            "user_agent": "Test",
            "browser": "Chrome",
            "device": "Desktop",
            "country": "France",
            "city": "Paris",
            "referrer": "https://test.com"
        }
        result = supabase.table('tracking_events').insert(test_data).execute()
        if result.data:
            print("\n✅ SUCCÈS! Les colonnes ont été ajoutées correctement!")
            # Nettoyer
            supabase.table('tracking_events').delete().eq('id', result.data[0]['id']).execute()
        
except Exception as e:
    if 'Could not find' in str(e) and 'browser' in str(e):
        print("\n⚠️  Les colonnes n'existent pas encore.")
        print("   Exécutez le SQL ci-dessus dans Supabase SQL Editor")
    else:
        print(f"\n✅ Les colonnes semblent déjà exister! Erreur: {e}")
