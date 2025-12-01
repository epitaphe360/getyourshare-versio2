#!/usr/bin/env python
"""Test direct de l'endpoint admin/users pour les merchants"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("🔍 Test de l'endpoint GET /api/admin/users?role=merchant")
print("=" * 60)

# Simuler la logique de l'endpoint
role = "merchant"
status = None
subscription = None

query = supabase.table("users").select(
    "id, email, username, role, status, created_at, subscription_plan, first_name, last_name, phone, bio"
)

# Filtrer par rôle merchant
query = query.eq("role", role)

if status:
    query = query.eq("status", status)

if subscription:
    query = query.eq("subscription_plan", subscription)

# Exécuter la requête
response = query.order("created_at", desc=True).execute()

print(f"\n📊 Résultat de la requête:")
print(f"   - Nombre d'utilisateurs: {len(response.data)}")

if response.data:
    print(f"\n📋 Premiers 5 merchants:")
    for i, user in enumerate(response.data[:5]):
        print(f"\n   Merchant #{i+1}:")
        print(f"      - ID: {user.get('id')}")
        print(f"      - Email: {user.get('email')}")
        print(f"      - Username: {user.get('username')}")
        print(f"      - Role: {user.get('role')}")
        print(f"      - Status: {user.get('status')}")
        print(f"      - Plan: {user.get('subscription_plan')}")

# Format de réponse comme l'API
api_response = {
    "success": True,
    "users": [
        {
            "id": str(u.get("id")),
            "email": u.get("email", ""),
            "username": u.get("username", ""),
            "role": u.get("role", ""),
            "status": u.get("status", "active"),
            "created_at": str(u.get("created_at", "")),
            "subscription_plan": u.get("subscription_plan", ""),
            "first_name": u.get("first_name", ""),
            "last_name": u.get("last_name", ""),
            "phone": u.get("phone", ""),
            "bio": u.get("bio", "")
        }
        for u in response.data
    ],
    "total": len(response.data)
}

print(f"\n✅ Format de réponse API:")
print(f"   - success: {api_response['success']}")
print(f"   - total: {api_response['total']}")
print(f"   - users: [{len(api_response['users'])} items]")

if api_response['users']:
    print(f"\n   Premier user dans la réponse:")
    first = api_response['users'][0]
    for key, value in first.items():
        print(f"      {key}: {value}")
