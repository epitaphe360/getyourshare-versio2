"""
Script pour appliquer les tables de gestion d'abonnements dans Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def apply_sql_migration():
    """Applique le script SQL de migration"""
    
    # Créer le client Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Lire le fichier SQL
    with open('CREATE_SUBSCRIPTION_MANAGEMENT_TABLES.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    print("🚀 Application du script SQL...")
    print("=" * 60)
    
    try:
        # Exécuter le script SQL
        # Note: Supabase Python ne supporte pas l'exécution directe de SQL
        # On va créer les tables une par une via l'API REST
        
        print("\n⚠️  IMPORTANT: Ce script nécessite d'exécuter le SQL manuellement")
        print("\n📋 Instructions:")
        print("1. Ouvre Supabase Dashboard: https://supabase.com/dashboard")
        print("2. Va dans ton projet: iamezkmapbhlhhvvsits")
        print("3. Clique sur 'SQL Editor' dans le menu de gauche")
        print("4. Copie-colle le contenu de: CREATE_SUBSCRIPTION_MANAGEMENT_TABLES.sql")
        print("5. Clique sur 'Run' (ou appuie sur Ctrl+Enter)")
        
        print("\n" + "=" * 60)
        print("✅ Le fichier SQL est prêt dans: CREATE_SUBSCRIPTION_MANAGEMENT_TABLES.sql")
        print("\n📊 Tables qui seront créées:")
        print("   - coupons (codes promotionnels)")
        print("   - coupon_redemptions (historique d'utilisation)")
        print("   - user_credits (crédits utilisateurs)")
        print("   - subscription_events (audit trail)")
        print("   - refunds (remboursements)")
        print("\n💡 Astuce: Tu peux aussi utiliser l'alternative ci-dessous")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║  MIGRATION BASE DE DONNÉES - SYSTÈME D'ABONNEMENTS        ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    apply_sql_migration()
    
    print("\n" + "=" * 60)
    print("🔗 Liens utiles:")
    print(f"   Dashboard: https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits")
    print(f"   SQL Editor: https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/sql/new")
    print(f"   Tables: https://supabase.com/dashboard/project/iamezkmapbhlhhvvsits/editor")
    print("=" * 60)
