import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")

def main():
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )
    
    print("=" * 60)
    print("VÉRIFICATION DE LA TABLE LEADS")
    print("=" * 60)
    
    try:
        result = supabase.table('leads').select('*').limit(1).execute()
        if result.data:
            print(f"✅ Colonnes de 'leads': {list(result.data[0].keys())}")
        else:
            print("⚠️  Aucun enregistrement dans 'leads'")
            # Try to get columns via a different way if possible, but usually select * on empty table works if table exists
            # Let's try to insert a dummy and rollback? No, just check if it exists.
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
