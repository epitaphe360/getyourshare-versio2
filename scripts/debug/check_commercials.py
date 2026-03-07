import sys
import os

# Naviguer vers le répertoire backend
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)
os.chdir(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv("backend/.env")

from utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

# Vérifier les colonnes de la table users
print("\n📋 Récupération d'un utilisateur pour voir la structure...")
sample = supabase.from_("users").select("*").limit(1).execute()
if sample.data:
    print(f"✅ Colonnes disponibles: {', '.join(sample.data[0].keys())}")
    print(f"\n📊 Exemple d'utilisateur:")
    for key, value in list(sample.data[0].items())[:10]:
        print(f"  - {key}: {value}")
else:
    print("  ⚠️  Aucun utilisateur dans la base")

# Vérifier les commerciaux
result = supabase.from_("users").select("id,email,role").eq("role", "commercial").execute()

print(f"\n✅ Nombre de commerciaux: {len(result.data)}\n")

if result.data:
    for u in result.data:
        print(f"  - {u.get('email')} (ID: {u.get('id')[:8]}...)")
else:
    print("  ⚠️  Aucun commercial trouvé dans la base de données")

# Vérifier les influenceurs
result_inf = supabase.from_("users").select("id,email,role").eq("role", "influencer").execute()

print(f"\n✅ Nombre d'influenceurs: {len(result_inf.data)}\n")

if result_inf.data:
    for u in result_inf.data:
        print(f"  - {u.get('email')} (ID: {u.get('id')[:8]}...)")
else:
    print("  ⚠️  Aucun influenceur trouvé dans la base de données")

# Vérifier tous les rôles disponibles
result_roles = supabase.from_("users").select("role").execute()
roles = set([u.get('role') for u in result_roles.data if u.get('role')])
print(f"\n✅ Rôles disponibles dans la base: {', '.join(sorted(roles))}")
