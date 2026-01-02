import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 70)
print("VÉRIFICATION DES TABLES REVIEWS")
print("=" * 70)

# Essayer de récupérer les reviews
try:
    result = supabase.table('product_reviews').select('*').limit(1).execute()
    print(f"\n✅ Table 'product_reviews' existe")
    print(f"   Reviews trouvés: {len(result.data) if result.data else 0}")
except Exception as e:
    print(f"\n❌ Erreur avec 'product_reviews': {str(e)}")

# Essayer reviews (sans product_)
try:
    result = supabase.table('reviews').select('*').limit(1).execute()
    print(f"\n✅ Table 'reviews' existe")
    print(f"   Reviews trouvés: {len(result.data) if result.data else 0}")
except Exception as e:
    print(f"\n❌ Erreur avec 'reviews': {str(e)}")

print("\n" + "=" * 70)
