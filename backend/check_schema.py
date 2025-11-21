#!/usr/bin/env python
"""Vérifier le schéma de la table users"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("Récupération des utilisateurs...")
users = client.table("users").select("*").limit(5).execute()

print("\nUtilisateurs trouvés:")
print("\nColonnes disponibles:")
if users.data:
    for key in users.data[0].keys():
        print(f"  - {key}")

print("\nPremier utilisateur:")
if users.data:
    import json
    print(json.dumps(users.data[0], indent=2, default=str))
