"""
Vérifier les utilisateurs actifs dans les dernières 24h
"""
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("=" * 80)
print("VÉRIFICATION UTILISATEURS ACTIFS")
print("=" * 80)

# Récupérer tous les utilisateurs
users_result = supabase.table('users').select('id, email, last_login, created_at').execute()
users = users_result.data

print(f"\n✅ Total utilisateurs: {len(users)}")

# Vérifier combien ont un last_login
with_last_login = [u for u in users if u.get('last_login')]
print(f"✅ Utilisateurs avec last_login: {len(with_last_login)}")

# Vérifier combien sont actifs dans les dernières 24h
yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
print(f"\n📅 Date de référence (24h): {yesterday}")

active_24h = [u for u in users if u.get('last_login') and u.get('last_login') > yesterday]
print(f"✅ Utilisateurs actifs 24h: {len(active_24h)}")

# Afficher quelques exemples
print("\n📋 EXEMPLES D'UTILISATEURS:")
for i, user in enumerate(users[:10], 1):
    email = user.get('email', 'N/A')
    last_login = user.get('last_login', 'Jamais connecté')
    is_active = '✅' if user.get('last_login') and user.get('last_login') > yesterday else '❌'
    print(f"{i}. {is_active} {email}: {last_login}")

# Problème identifié ?
print("\n" + "=" * 80)
if len(with_last_login) == 0:
    print("❌ PROBLÈME: Aucun utilisateur n'a de last_login !")
    print("   La colonne last_login n'est probablement pas mise à jour lors du login.")
elif len(active_24h) == 0:
    print("⚠️  ATTENTION: Aucun utilisateur actif dans les 24h")
    print("   Les utilisateurs ne se sont pas connectés récemment,")
    print("   OU la colonne last_login n'est pas mise à jour correctement.")
else:
    print(f"✅ SUCCÈS: {len(active_24h)} utilisateurs actifs dans les 24h")
print("=" * 80)

# Vérifier la requête utilisée dans le backend
print("\n📊 TEST REQUÊTE BACKEND:")
try:
    active_count = supabase.table("users").select("id", count="exact", head=True).gt("last_login", yesterday).execute()
    backend_count = active_count.count or 0
    print(f"Résultat de la requête backend: {backend_count}")
    
    if backend_count != len(active_24h):
        print(f"⚠️  INCOHÉRENCE: count={backend_count} vs len={len(active_24h)}")
    else:
        print("✅ Cohérence OK")
except Exception as e:
    print(f"❌ Erreur: {e}")
