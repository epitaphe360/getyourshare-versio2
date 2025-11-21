from dotenv import load_dotenv
from supabase import create_client
import os
import json

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

print("="*60)
print("📋 UTILISATEURS DISPONIBLES")
print("="*60)

response = supabase.table("users").select("id,email,role").limit(5).execute()
print(f"\nTotal d'utilisateurs trouvés: {len(response.data)}\n")

for i, user in enumerate(response.data, 1):
    print(f"{i}. Email: {user['email']}")
    print(f"   Rôle: {user.get('role', 'N/A')}")
    print()

print("="*60)
print("Note: Utilisez ces emails pour tester l'authentification")
print("="*60)
