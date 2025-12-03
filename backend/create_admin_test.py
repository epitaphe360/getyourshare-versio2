"""
Créer un compte admin de test et vérifier les commissions plateforme
"""
import os
from supabase import create_client
from dotenv import load_dotenv
import bcrypt

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# 1. Créer ou mettre à jour le compte admin
print("=" * 80)
print("1. CRÉATION/MÀJ COMPTE ADMIN")
print("=" * 80)

# Hash le mot de passe
password = "Admin123!"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Vérifier si l'admin existe déjà
admin_check = supabase.table('users').select('*').eq('email', 'admin@test.com').execute()

if admin_check.data:
    # Mettre à jour
    admin_id = admin_check.data[0]['id']
    supabase.table('users').update({
        'password_hash': hashed,
        'role': 'admin',
        'is_active': True
    }).eq('id', admin_id).execute()
    print(f"✅ Admin mis à jour: admin@test.com")
else:
    # Créer
    result = supabase.table('users').insert({
        'email': 'admin@test.com',
        'password_hash': hashed,
        'role': 'admin',
        'full_name': 'Admin Test',
        'is_active': True
    }).execute()
    admin_id = result.data[0]['id']
    print(f"✅ Admin créé: admin@test.com")

print(f"   ID: {admin_id}")
print(f"   Password: {password}")

# 2. Vérifier les données sales
print("\n" + "=" * 80)
print("2. VÉRIFICATION DONNÉES SALES")
print("=" * 80)

sales = supabase.table('sales').select('*').eq('status', 'completed').execute()
print(f"Ventes complétées: {len(sales.data)}")

if sales.data:
    total_amount = sum(float(s.get('amount', 0)) for s in sales.data)
    total_platform = sum(float(s.get('platform_commission', 0)) for s in sales.data)
    total_influencer = sum(float(s.get('influencer_commission', 0)) for s in sales.data)
    
    print(f"\n💰 TOTAUX:")
    print(f"   Total ventes: {total_amount:.2f} MAD")
    print(f"   Commission plateforme: {total_platform:.2f} MAD")
    print(f"   Commission influenceur: {total_influencer:.2f} MAD")
    
    if total_platform > 0:
        print(f"\n✅ Commission plateforme > 0 : {total_platform:.2f} MAD")
    else:
        print(f"\n❌ Commission plateforme = 0 MAD - PROBLÈME!")

# 3. Afficher les credentials de test
print("\n" + "=" * 80)
print("3. CREDENTIALS DE TEST")
print("=" * 80)
print("Email: admin@test.com")
print(f"Password: {password}")
print("\nVous pouvez maintenant tester dans le dashboard !")
