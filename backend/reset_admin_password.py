#!/usr/bin/env python
"""Créer ou réinitialiser un compte admin avec un mot de passe connu"""

import bcrypt
from supabase import create_client
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

# Mot de passe à utiliser
PASSWORD = "Admin123!"
password_hash = bcrypt.hashpw(PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print("="*70)
print("🔐 RÉINITIALISATION COMPTE ADMIN")
print("="*70)
print(f"Email: admin@getyourshare.com")
print(f"Mot de passe: {PASSWORD}")
print(f"Hash: {password_hash}")
print()

try:
    # Chercher si le compte existe
    user_response = client.table("users").select("id").eq("email", "admin@getyourshare.com").execute()
    
    if user_response.data:
        # Mettre à jour le compte existant
        admin_id = user_response.data[0]['id']
        print(f"📧 Compte trouvé (ID: {admin_id})")
        print(f"🔄 Mise à jour du mot de passe...")
        
        update_result = client.table("users").update({
            "password_hash": password_hash
        }).eq("id", admin_id).execute()
        
        print(f"✅ Mot de passe mis à jour!")
    else:
        # Créer un nouveau compte
        print(f"👤 Compte non trouvé, création...")
        
        admin_data = {
            "email": "admin@getyourshare.com",
            "password_hash": password_hash,
            "role": "admin",
            "full_name": "Admin User",
            "is_active": True,
            "is_verified": True,
            "status": "active"
        }
        
        insert_result = client.table("users").insert(admin_data).execute()
        print(f"✅ Compte créé!")

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("="*70)
print("✅ Vous pouvez maintenant vous connecter avec:")
print(f"   Email: admin@getyourshare.com")
print(f"   Password: {PASSWORD}")
print("="*70)
