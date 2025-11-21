#!/usr/bin/env python3
"""
Vérifier et créer des données de test pour les conversations
"""
import sys
sys.path.insert(0, '/'.join(__file__.split('/')[:-1]))

from supabase_config import supabase

print("=" * 60)
print("DIAGNOSTIC: CONVERSATIONS & MESSAGES")
print("=" * 60)

# 1. Vérifier les tables
tables = ['conversations', 'messages', 'users', 'merchants', 'influencers']
print("\n1. ÉTAT DES TABLES:")
for table in tables:
    try:
        result = supabase.table(table).select('*', count='exact').execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        print(f"   ✅ {table}: {count} enregistrements")
    except Exception as e:
        print(f"   ❌ {table}: {str(e)[:80]}")

# 2. Vérifier les utilisateurs
print("\n2. UTILISATEURS PAR RÔLE:")
try:
    users = supabase.table('users').select('id, email, role').execute()
    if users.data:
        roles_count = {}
        users_list = {'admin': None, 'merchant': None, 'influencer': None}
        
        for user in users.data:
            role = user.get('role', 'unknown')
            roles_count[role] = roles_count.get(role, 0) + 1
            
            # Sauvegarder un exemple de chaque rôle
            if role in users_list and users_list[role] is None:
                users_list[role] = user
        
        for role, count in sorted(roles_count.items()):
            print(f"   {role}: {count}")
        
        print("\n3. EXEMPLE D'UTILISATEURS (par rôle):")
        for role in ['admin', 'merchant', 'influencer']:
            if users_list[role]:
                user = users_list[role]
                print(f"   {role}: {user['email']} (ID: {user['id'][:8]}...)")
    else:
        print("   ❌ Aucun utilisateur")
        users_list = {'admin': None, 'merchant': None, 'influencer': None}
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    users_list = {'admin': None, 'merchant': None, 'influencer': None}

# 3. Vérifier les conversations
print("\n4. CONVERSATIONS:")
try:
    conversations = supabase.table('conversations').select('*').execute()
    if conversations.data:
        print(f"   Trouvées: {len(conversations.data)}")
        for i, conv in enumerate(conversations.data[:3], 1):
            print(f"   {i}. Merchant: {conv.get('merchant_id')[:8]}...")
            print(f"      Influencer: {conv.get('influencer_id')[:8]}...")
            print(f"      Status: {conv.get('status')}")
    else:
        print("   ❌ AUCUNE CONVERSATION - C'est le problème!")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 4. Vérifier les messages
print("\n5. MESSAGES:")
try:
    messages = supabase.table('messages').select('*').execute()
    if messages.data:
        print(f"   Trouvés: {len(messages.data)}")
    else:
        print("   ❌ Aucun message")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 60)
print("RÉSUMÉ DU PROBLÈME:")
print("=" * 60)

# Diagnostic
if users_list['merchant'] and users_list['influencer']:
    print("""
✅ Les utilisateurs existent (merchant et influencer)
❌ Mais il n'y a pas de CONVERSATIONS

SOLUTION:
Pour avoir des conversations, un merchant et un influencer
doivent créer une conversation via l'application.

Option 1: Créer manuellement via Supabase SQL:
  INSERT INTO conversations (merchant_id, influencer_id, status)
  VALUES ('merchant_id', 'influencer_id', 'active')

Option 2: Simuler une création via l'API:
  POST /api/messages/start
  {
    "recipient_id": "influencer_id",
    "campaign_id": "uuid"
  }
    """)
else:
    print("""
⚠️ Il manque des utilisateurs:
    - Merchant: """ + ("✅" if users_list['merchant'] else "❌") + """
    - Influencer: """ + ("✅" if users_list['influencer'] else "❌") + """
    
Créez d'abord des utilisateurs avec les rôles appropriate.
    """)

print("=" * 60)
