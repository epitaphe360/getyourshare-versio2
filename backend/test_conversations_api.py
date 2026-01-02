#!/usr/bin/env python3
"""
Test l'endpoint des conversations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from supabase_config import supabase
import jwt
from datetime import datetime, timedelta

# Config JWT (doit correspondre au backend)
JWT_SECRET = os.getenv('JWT_SECRET', 'your_secret_key_change_this_in_production')
JWT_ALGORITHM = 'HS256'

print("=" * 60)
print("TEST API CONVERSATIONS")
print("=" * 60)

# 1. Récupérer un utilisateur admin
print("\n1. Récupération d'un utilisateur admin:")
users = supabase.table('users').select('id, email, role').eq('role', 'admin').limit(1).execute()

if not users.data:
    print("   ❌ Aucun admin trouvé")
    sys.exit(1)

admin = users.data[0]
print(f"   ✅ Trouvé: {admin['email']}")
admin_id = admin['id']

# 2. Créer un JWT valide pour ce user
print("\n2. Création d'un token JWT valide:")
now = datetime.utcnow()
payload = {
    "sub": admin_id,
    "email": admin['email'],
    "role": admin['role'],
    "type": "access",
    "iat": now,
    "exp": now + timedelta(hours=24)
}

token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
print(f"   ✅ Token: {token[:50]}...")

# 3. Simuler un appel API en exécutant le code du endpoint
print("\n3. Simulation de l'endpoint /api/messages/conversations:")

# Simuler la extraction du user du cookie
current_user = {
    "id": admin_id,
    "email": admin['email'],
    "role": admin['role']
}

# Exécuter la logique de l'endpoint
try:
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    print(f"   User ID: {user_id}")
    print(f"   User Role: {user_role}")
    
    # Pour admin, récupérer toutes les conversations
    if user_role == "admin":
        result = supabase.from_("conversations").select("""
            *,
            merchant:merchant_id(id, username, email, company_name),
            influencer:influencer_id(id, username, email)
        """).order("last_message_at", desc=True).execute()
        
        conversations = result.data if result.data else []
        print(f"\n   ✅ Conversations trouvées: {len(conversations)}")
        
        if conversations:
            for i, conv in enumerate(conversations[:3], 1):
                print(f"\n   Conversation {i}:")
                print(f"      ID: {conv.get('id')}")
                print(f"      Merchant: {conv.get('merchant', {}).get('company_name', 'N/A')}")
                print(f"      Influencer: {conv.get('influencer', {}).get('username', 'N/A')}")
                print(f"      Last message at: {conv.get('last_message_at')}")
                print(f"      Status: {conv.get('status')}")
        else:
            print("   ❌ Aucune conversation retournée")
    else:
        print(f"   ⚠️ User n'est pas admin (role: {user_role})")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
