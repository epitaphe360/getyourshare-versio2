import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 70)
print("VÉRIFICATION DES DEMANDES D'INSCRIPTION - ANNONCEURS")
print("=" * 70)

# Vérifier les merchants avec status pending
result = supabase.from_("users").select("id, email, company_name, username, role, status, created_at").eq("role", "merchant").execute()

merchants = result.data if result.data else []
print(f"\n✅ Total merchants: {len(merchants)}")

if len(merchants) > 0:
    # Compter par statut
    pending = [m for m in merchants if m.get('status') == 'pending']
    approved = [m for m in merchants if m.get('status') == 'approved' or m.get('status') == 'active']
    rejected = [m for m in merchants if m.get('status') == 'rejected']
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   - Pending: {len(pending)}")
    print(f"   - Approved/Active: {len(approved)}")
    print(f"   - Rejected: {len(rejected)}")
    
    if len(pending) > 0:
        print(f"\n📋 DEMANDES EN ATTENTE:")
        for m in pending[:5]:
            print(f"\n   - Email: {m.get('email')}")
            print(f"     Entreprise: {m.get('company_name') or 'N/A'}")
            print(f"     Statut: {m.get('status')}")
    
    # Afficher tous les statuts différents
    all_statuses = set(m.get('status') for m in merchants if m.get('status'))
    print(f"\n📝 Statuts trouvés: {', '.join(all_statuses)}")
    
else:
    print("\n⚠️  AUCUN MERCHANT - Création de données de test...")
    
    test_merchants = [
        {
            "email": "pending1@test.com",
            "role": "merchant",
            "status": "pending",
            "company_name": "Boutique Mode Test",
            "username": "boutique_mode",
            "phone": "+33612345678",
            "is_active": False
        },
        {
            "email": "pending2@test.com",
            "role": "merchant",
            "status": "pending",
            "company_name": "Tech Store Test",
            "username": "tech_store",
            "phone": "+33687654321",
            "is_active": False
        }
    ]
    
    result = supabase.from_("users").insert(test_merchants).execute()
    if result.data:
        print(f"✅ {len(result.data)} demandes de test créées!")
    else:
        print("❌ Erreur lors de la création")

print("\n" + "=" * 70)
