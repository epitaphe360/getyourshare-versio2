import os
import sys
import time
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Erreur: Variables d'environnement manquantes")
    sys.exit(1)

supabase: Client = create_client(url, key)

# Ordre de suppression critique (Enfants -> Parents)
tables_ordered = [
    "transactions",
    "leads",
    "clicks", 
    "campaign_influencers",
    "campaigns",
    "products",
    "services",
    "subscriptions",
    "payment_accounts",
    "payout_preferences",
    "kyc_verifications",
    "notifications",
    "audit_logs",
    "social_media_accounts",
    "api_keys",
    "email_campaigns",
    "shipments",
    "conversations",
    "events",
    "messages",
    "commercial_objectives",
    "affiliate_stats",
    "influencer_stats",
    "merchant_stats",
    "platform_stats",
    "disputes",
    "data_exports",
    "referral_codes",
    "webhooks",
    "webhook_logs",
    "report_runs",
    "custom_reports",
    "content_templates",
    "media_library",
    "seo_metadata",
    "user_2fa",
    "user_sessions",
    "sales_assignments",
    "affiliation_requests",
    "analytics_reports",
    "support_tickets",
    "payment_integrations",
    "product_collections",
    "wishlists",
    "warehouses",
    "coupons",
    "security_events",
    "live_streams",
    "user_badges"
]

test_emails = [
    'admin@getyourshare.com',
    'influenceur@test.com',
    'influenceur2@test.com',
    'marchand@test.com',
    'commercial@test.com'
]

print("🧹 Démarrage du nettoyage intelligent...")

def delete_data_for_users():
    # 1. Récupérer les IDs des utilisateurs de test
    user_ids = []
    for email in test_emails:
        res = supabase.table('users').select('id').eq('email', email).execute()
        if res.data:
            user_ids.append(res.data[0]['id'])
    
    if not user_ids:
        print("Aucun utilisateur de test trouvé. Le nettoyage est peut-être déjà fait.")
        return

    print(f"Cibles identifiées: {len(user_ids)} utilisateurs.")

    # 2. Supprimer les données dépendantes pour ces utilisateurs
    for table in tables_ordered:
        print(f"   Nettoyage table '{table}'...")
        for uid in user_ids:
            try:
                # On essaie de supprimer par user_id, merchant_id, influencer_id, etc.
                possible_fk_cols = [
                    'user_id', 'merchant_id', 'influencer_id', 'admin_id', 
                    'commercial_id', 'owner_id', 'sender_id', 'receiver_id',
                    'sales_rep_id', 'resolved_by', 'created_by', 'updated_by'
                ]
                
                for col in possible_fk_cols:
                    try:
                        # On ne peut pas vérifier si la colonne existe facilement sans faire une requête qui échoue
                        # On tente la suppression, si ça échoue c'est pas grave (souvent car colonne inexistante)
                        supabase.table(table).delete().eq(col, uid).execute()
                    except Exception:
                        pass 
                        
            except Exception as e:
                # Ignorer les erreurs de tables inexistantes ou colonnes manquantes
                pass

    # 3. Supprimer les utilisateurs eux-mêmes
    print("   Suppression des comptes utilisateurs...")
    for uid in user_ids:
        try:
            supabase.table('users').delete().eq('id', uid).execute()
            print(f"      ✅ Utilisateur {uid} supprimé.")
        except Exception as e:
            print(f"      ❌ Echec suppression utilisateur {uid}: {e}")

delete_data_for_users()
print("🏁 Nettoyage terminé.")
