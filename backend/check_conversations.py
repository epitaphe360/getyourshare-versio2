#!/usr/bin/env python3
from config.supabase_config import supabase

print("=== VÉRIFICATION DES CONVERSATIONS ===\n")

# Vérifier les conversations
try:
    conversations = supabase.table('conversations').select('*').execute()
    print(f"Total conversations: {len(conversations.data) if conversations.data else 0}")
    
    if conversations.data:
        for i, conv in enumerate(conversations.data[:5], 1):
            print(f"  {i}. ID: {conv.get('id')}")
            print(f"     Merchant: {conv.get('merchant_id')}")
            print(f"     Influencer: {conv.get('influencer_id')}")
            print(f"     Created: {conv.get('created_at')}")
    else:
        print("  ❌ Aucune conversation trouvée")
except Exception as e:
    print(f"❌ Erreur conversations: {e}")

print("\n=== VÉRIFICATION DES MESSAGES ===\n")

# Vérifier les messages
try:
    messages = supabase.table('messages').select('*').execute()
    print(f"Total messages: {len(messages.data) if messages.data else 0}")
    
    if messages.data:
        for i, msg in enumerate(messages.data[:3], 1):
            print(f"  {i}. Conversation: {msg.get('conversation_id')}")
            print(f"     Sender: {msg.get('sender_id')}")
            print(f"     Content: {msg.get('content')[:50]}...")
    else:
        print("  ❌ Aucun message trouvé")
except Exception as e:
    print(f"❌ Erreur messages: {e}")

print("\n=== VÉRIFICATION DES UTILISATEURS ===\n")

# Vérifier les users
try:
    users = supabase.table('users').select('id, email, role').execute()
    print(f"Total utilisateurs: {len(users.data) if users.data else 0}")
    
    if users.data:
        roles_count = {}
        for user in users.data:
            role = user.get('role', 'unknown')
            roles_count[role] = roles_count.get(role, 0) + 1
        
        print(f"  Répartition par rôle:")
        for role, count in roles_count.items():
            print(f"    - {role}: {count}")
        
        print(f"\n  Exemples d'utilisateurs:")
        for user in users.data[:3]:
            print(f"    - {user.get('email')}: {user.get('role')}")
    else:
        print("  ❌ Aucun utilisateur trouvé")
except Exception as e:
    print(f"❌ Erreur utilisateurs: {e}")

print("\n=== TABLES DISPONIBLES ===\n")
try:
    # Liste des tables (via une requête simple)
    tables_to_check = ['conversations', 'messages', 'users', 'merchants', 'influencers']
    for table in tables_to_check:
        try:
            result = supabase.table(table).select('count', count='exact').execute()
            count = result.count if hasattr(result, 'count') else len(result.data)
            print(f"  ✅ {table}: {count} enregistrements")
        except:
            print(f"  ⚠️ {table}: table non trouvée ou vide")
except Exception as e:
    print(f"❌ Erreur: {e}")
