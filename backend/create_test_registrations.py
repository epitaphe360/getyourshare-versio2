import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 70)
print("CRÉATION DE DEMANDES D'INSCRIPTION DE TEST")
print("=" * 70)

test_merchants = [
    {
        "email": "pending.boutique@test.com",
        "password_hash": "$2b$12$abcdefghijklmnopqrstuv",  # Hash factice
        "role": "merchant",
        "status": "pending",
        "company_name": "Boutique Fashion Paris",
        "username": "boutique_fashion",
        "phone": "+33612345678",
        "country": "FR",
        "is_active": False
    },
    {
        "email": "pending.tech@test.com",
        "password_hash": "$2b$12$abcdefghijklmnopqrstuv",
        "role": "merchant",
        "status": "pending",
        "company_name": "Tech Solutions Inc",
        "username": "tech_solutions",
        "phone": "+33687654321",
        "country": "US",
        "is_active": False
    },
    {
        "email": "pending.sports@test.com",
        "password_hash": "$2b$12$abcdefghijklmnopqrstuv",
        "role": "merchant",
        "status": "pending",
        "company_name": "Sports Gear Pro",
        "username": "sports_gear",
        "phone": "+33698765432",
        "country": "FR",
        "is_active": False
    }
]

print(f"\n📝 Création de {len(test_merchants)} demandes de test...")

result = supabase.from_("users").insert(test_merchants).execute()

if result.data:
    print(f"\n✅ {len(result.data)} demandes créées avec succès!")
    for merchant in result.data:
        print(f"\n   - {merchant.get('company_name')}")
        print(f"     Email: {merchant.get('email')}")
        print(f"     Statut: {merchant.get('status')}")
        print(f"     Pays: {merchant.get('country')}")
else:
    print("\n❌ Erreur lors de la création des demandes")

# Vérification
print("\n" + "=" * 70)
print("VÉRIFICATION")
print("=" * 70)

pending_result = supabase.from_("users").select("*").eq("role", "merchant").eq("status", "pending").execute()
pending = pending_result.data if pending_result.data else []
print(f"\n✅ Total demandes en attente: {len(pending)}")

print("\n" + "=" * 70)
