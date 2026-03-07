"""Script pour nettoyer la base de données via l'API Supabase"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("❌ Erreur: Variables d'environnement manquantes")
    sys.exit(1)

supabase: Client = create_client(url, key)

print("🧹 NETTOYAGE DE LA BASE DE DONNÉES...")
print("="*60)

# Liste des utilisateurs de test
test_emails = [
    'admin@getyourshare.com',
    'influenceur@test.com',
    'influenceur2@test.com',
    'marchand@test.com',
    'commercial@test.com'
]

# Récupérer les IDs
print("\n📋 Recherche des utilisateurs de test...")
user_ids = []
for email in test_emails:
    try:
        res = supabase.table('users').select('id').eq('email', email).execute()
        if res.data:
            user_ids.append(res.data[0]['id'])
            print(f"   ✓ {email}")
    except:
        pass

if not user_ids:
    print("\n✅ Aucun utilisateur de test trouvé - Base déjà propre!")
    sys.exit(0)

print(f"\n🎯 {len(user_ids)} utilisateurs à nettoyer")

# Tables à nettoyer dans l'ordre (enfants -> parents)
tables = [
    "transactions", "leads", "campaign_influencers", "campaigns",
    "products", "services", "tracking_links", "conversions",
    "payouts", "subscriptions", "notifications", "kyc_verifications",
    "payment_accounts", "payout_preferences", "trust_scores",
    "webhooks", "webhook_logs", "api_keys", "security_events",
    "commercial_objectives", "referral_codes", "live_streams",
    "user_badges", "disputes", "social_media_accounts",
    "affiliation_requests", "publications"
]

print("\n🗑️  Suppression des données liées...")
deleted_count = 0

for table in tables:
    try:
        for uid in user_ids:
            # Essayer différentes colonnes FK
            for col in ['user_id', 'merchant_id', 'influencer_id', 'admin_id', 
                       'commercial_id', 'owner_id', 'sender_id', 'receiver_id',
                       'resolved_by', 'created_by', 'sales_rep_id']:
                try:
                    result = supabase.table(table).delete().eq(col, uid).execute()
                    if result.data and len(result.data) > 0:
                        deleted_count += len(result.data)
                except:
                    pass
    except:
        pass

print(f"   ✓ {deleted_count} enregistrements supprimés")

# Supprimer les utilisateurs
print("\n👥 Suppression des utilisateurs...")
success = 0
for uid in user_ids:
    try:
        supabase.table('users').delete().eq('id', uid).execute()
        success += 1
        print(f"   ✓ Utilisateur supprimé")
    except Exception as e:
        print(f"   ✗ Échec: {str(e)[:80]}")

print("\n" + "="*60)
if success == len(user_ids):
    print("✅ NETTOYAGE TERMINÉ AVEC SUCCÈS!")
    print(f"   {success}/{len(user_ids)} utilisateurs supprimés")
else:
    print(f"⚠️  NETTOYAGE PARTIEL: {success}/{len(user_ids)} utilisateurs supprimés")
    print("\n💡 Exécutez le script SQL CLEAN_ALL_DATA.sql dans Supabase SQL Editor")
    print("   pour un nettoyage complet.")

print("="*60)
