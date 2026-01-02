"""
Lister tous les utilisateurs dans la base de données
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 80)
print("LISTE DE TOUS LES UTILISATEURS")
print("=" * 80)

try:
    response = supabase.table("users").select("email, full_name, role").order("email").execute()
    
    if response.data:
        print(f"\nTotal: {len(response.data)} utilisateurs\n")
        
        # Grouper par rôle
        by_role = {}
        for user in response.data:
            role = user.get('role', 'unknown')
            if role not in by_role:
                by_role[role] = []
            by_role[role].append(user)
        
        for role, users in sorted(by_role.items()):
            print(f"\n{role.upper()} ({len(users)}):")
            print("-" * 80)
            for user in users:
                print(f"  {user['email']:40} | {user.get('full_name', 'N/A')}")
    else:
        print("Aucun utilisateur trouvé")
        
except Exception as e:
    print(f"Erreur: {str(e)}")

print("\n" + "=" * 80)
