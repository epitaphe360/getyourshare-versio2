#!/usr/bin/env python
"""Vérifier les mots de passe hachés dans la BD"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("Récupération des utilisateurs...")
users = client.table("users").select("id, email, password").execute()

print("\nUtilisateurs trouvés:")
for user in users.data:
    print(f"\nEmail: {user['email']}")
    print(f"ID: {user['id']}")
    print(f"Password hash: {user['password'][:50]}...")
