#!/usr/bin/env python3
"""
Script de peuplement de la base de données avec des données de test
Génère des données réalistes pour tous les systèmes de l'application
"""

import os
import sys
import random
from datetime import datetime, timedelta
from faker import Faker
import bcrypt

# Ajouter le répertoire parent au path pour importer les modules du backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY', 'your-service-key')

# Initialiser Faker pour les données françaises
fake = Faker('fr_FR')

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password: str) -> str:
    """Hasher un mot de passe"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_test_users():
    """Créer des utilisateurs de test"""
    print("🧑 Création des utilisateurs de test...")

    users = []

    # 1 Admin
    users.append({
        'email': 'admin@getyourshare.com',
        'password_hash': hash_password('Admin123!'),
        'role': 'admin',
        'full_name': 'Admin Platform',
        'is_active': True,
        'created_at': datetime.utcnow().isoformat()
    })

    # 10 Merchants
    for i in range(10):
        users.append({
            'email': f'merchant{i+1}@example.com',
            'password_hash': hash_password('Merchant123!'),
            'role': 'merchant',
            'full_name': fake.company(),
            'phone': fake.phone_number(),
            'is_active': True,
            'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 180))).isoformat()
        })

    # 20 Influencers
    for i in range(20):
        users.append({
            'email': f'influencer{i+1}@example.com',
            'password_hash': hash_password('Influencer123!'),
            'role': 'influencer',
            'full_name': fake.name(),
            'username': f'influencer_{i+1}',
            'phone': fake.phone_number(),
            'is_active': True,
            'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 180))).isoformat()
        })

    # 5 Commercials
    for i in range(5):
        users.append({
            'email': f'commercial{i+1}@example.com',
            'password_hash': hash_password('Commercial123!'),
            'role': 'commercial',
            'full_name': fake.name(),
            'phone': fake.phone_number(),
            'is_active': True,
            'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 180))).isoformat()
        })

    try:
        result = supabase.table('users').insert(users).execute()
        print(f"✅ {len(users)} utilisateurs créés")
        return result.data
    except Exception as e:
        print(f"❌ Erreur création utilisateurs: {e}")
        return []

def create_merchants(user_ids):
    """Créer des profils merchants"""
    print("🏢 Création des profils merchants...")

    merchants = []
    merchant_users = [u for u in user_ids if 'merchant' in u.get('email', '')]

    for user in merchant_users:
        merchants.append({
            'user_id': user['id'],
            'company_name': fake.company(),
            'website': fake.url(),
            'contact_name': user['full_name'],
            'contact_email': user['email'],
            'balance': random.uniform(100, 10000),
            'campaigns_count': random.randint(0, 10),
            'created_at': user['created_at']
        })

    try:
        result = supabase.table('merchants').insert(merchants).execute()
        print(f"✅ {len(merchants)} merchants créés")
        return result.data
    except Exception as e:
        print(f"❌ Erreur création merchants: {e}")
        return []

def create_products(merchant_ids):
    """Créer des produits"""
    print("📦 Création des produits...")

    products = []
    categories = ['Électronique', 'Mode', 'Maison', 'Beauté', 'Sport', 'Livres', 'Jouets', 'Alimentation']

    for merchant in merchant_ids:
        # Chaque merchant a entre 3 et 15 produits
        for _ in range(random.randint(3, 15)):
            products.append({
                'merchant_id': merchant['id'],
                'name': fake.catch_phrase(),
                'description': fake.text(max_nb_chars=200),
                'category': random.choice(categories),
                'price': round(random.uniform(10, 500), 2),
                'commission_rate': round(random.uniform(5, 20), 2),
                'stock_quantity': random.randint(0, 100),
                'sku': f'SKU-{random.randint(10000, 99999)}',
                'is_active': random.choice([True, True, True, False]),
                'views_count': random.randint(0, 1000),
                'clicks_count': random.randint(0, 500),
                'sales_count': random.randint(0, 50),
                'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 180))).isoformat()
            })

    try:
        result = supabase.table('products').insert(products).execute()
        print(f"✅ {len(products)} produits créés")
        return result.data
    except Exception as e:
        print(f"❌ Erreur création produits: {e}")
        return []

def create_services(merchant_ids):
    """Créer des services"""
    print("💼 Création des services...")

    services = []
    categories = ['Consulting', 'Marketing', 'Design', 'Développement', 'Formation', 'Support']

    for merchant in merchant_ids[:5]:  # Seulement les 5 premiers merchants ont des services
        for _ in range(random.randint(2, 5)):
            services.append({
                'merchant_id': merchant['id'],
                'nom': fake.bs(),
                'description': fake.text(max_nb_chars=200),
                'categorie': random.choice(categories),
                'depot_initial': round(random.uniform(100, 5000), 2),
                'prix_par_lead': round(random.uniform(10, 100), 2),
                'commission_rate': round(random.uniform(10, 30), 2),
                'status': random.choice(['actif', 'actif', 'pause', 'termine']),
                'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 180))).isoformat()
            })

    try:
        result = supabase.table('services').insert(services).execute()
        print(f"✅ {len(services)} services créés")
        return result.data
    except Exception as e:
        print(f"❌ Erreur création services: {e}")
        return []

def create_subscriptions(user_ids):
    """Créer des abonnements"""
    print("💳 Création des abonnements...")

    subscriptions = []

    # Plans influenceurs
    influencer_plans = ['free', 'basic', 'pro', 'elite', 'premium']
    influencer_users = [u for u in user_ids if 'influencer' in u.get('email', '')]

    for user in influencer_users:
        plan = random.choice(influencer_plans)
        start_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
        subscriptions.append({
            'user_id': user['id'],
            'plan_code': plan,
            'plan_name': plan.capitalize(),
            'status': 'active' if random.random() > 0.1 else 'cancelled',
            'current_period_start': start_date.isoformat(),
            'current_period_end': (start_date + timedelta(days=30)).isoformat(),
            'created_at': start_date.isoformat()
        })

    # Plans merchants
    merchant_plans = ['freemium', 'standard', 'premium', 'enterprise']
    merchant_users = [u for u in user_ids if 'merchant' in u.get('email', '')]

    for user in merchant_users:
        plan = random.choice(merchant_plans)
        start_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
        subscriptions.append({
            'user_id': user['id'],
            'plan_code': plan,
            'plan_name': plan.capitalize(),
            'status': 'active' if random.random() > 0.1 else 'cancelled',
            'current_period_start': start_date.isoformat(),
            'current_period_end': (start_date + timedelta(days=30)).isoformat(),
            'created_at': start_date.isoformat()
        })

    # Plans commercials
    commercial_plans = ['starter', 'pro', 'enterprise']
    commercial_users = [u for u in user_ids if 'commercial' in u.get('email', '')]

    for user in commercial_users:
        plan = random.choice(commercial_plans)
        start_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
        subscriptions.append({
            'user_id': user['id'],
            'plan_code': plan,
            'plan_name': plan.capitalize(),
            'status': 'active',
            'current_period_start': start_date.isoformat(),
            'current_period_end': (start_date + timedelta(days=30)).isoformat(),
            'created_at': start_date.isoformat()
        })

    try:
        result = supabase.table('subscriptions').insert(subscriptions).execute()
        print(f"✅ {len(subscriptions)} abonnements créés")
        return result.data
    except Exception as e:
        print(f"❌ Erreur création abonnements: {e}")
        return []

def create_transactions(user_ids):
    """Créer des transactions"""
    print("💰 Création des transactions...")

    transactions = []

    for user in user_ids:
        # Chaque utilisateur a entre 0 et 50 transactions
        for _ in range(random.randint(0, 50)):
            amount = round(random.uniform(10, 500), 2)
            transactions.append({
                'user_id': user['id'],
                'amount': amount,
                'type': random.choice(['commission', 'payout', 'refund', 'subscription']),
                'status': random.choice(['completed', 'completed', 'completed', 'pending', 'failed']),
                'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 180))).isoformat()
            })

    try:
        result = supabase.table('transactions').insert(transactions).execute()
        print(f"✅ {len(transactions)} transactions créées")
        return result.data
    except Exception as e:
        print(f"❌ Erreur création transactions: {e}")
        return []

def create_registration_requests():
    """Créer des demandes d'inscription"""
    print("📝 Création des demandes d'inscription...")

    registrations = []
    statuses = ['pending', 'approved', 'rejected']

    for i in range(15):
        registrations.append({
            'company_name': fake.company(),
            'email': fake.email(),
            'contact_person': fake.name(),
            'phone': fake.phone_number(),
            'country': random.choice(['FR', 'MA', 'US', 'BE', 'CA']),
            'website': fake.url(),
            'business_type': random.choice(['E-commerce', 'SaaS', 'Services', 'Marketplace', 'Agence']),
            'estimated_budget': round(random.uniform(500, 50000), 2),
            'status': random.choice(statuses),
            'created_at': (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat()
        })

    try:
        result = supabase.table('advertiser_registrations').insert(registrations).execute()
        print(f"✅ {len(registrations)} demandes d'inscription créées")
        return result.data
    except Exception as e:
        print(f"❌ Erreur création demandes: {e}")
        return []

def main():
    """Fonction principale"""
    print("🚀 Démarrage du peuplement de la base de données...\n")

    # Vérifier la connexion Supabase
    if SUPABASE_URL == 'https://your-project.supabase.co':
        print("❌ Erreur: Veuillez configurer SUPABASE_URL et SUPABASE_SERVICE_KEY")
        print("   Exporter les variables d'environnement :")
        print("   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_SERVICE_KEY='your-service-key'")
        return

    try:
        # 1. Créer les utilisateurs
        users = create_test_users()
        if not users:
            print("❌ Impossible de continuer sans utilisateurs")
            return

        # 2. Créer les merchants
        merchants = create_merchants(users)

        # 3. Créer les produits
        if merchants:
            products = create_products(merchants)

        # 4. Créer les services
        if merchants:
            services = create_services(merchants)

        # 5. Créer les abonnements
        subscriptions = create_subscriptions(users)

        # 6. Créer les transactions
        transactions = create_transactions(users)

        # 7. Créer les demandes d'inscription
        registrations = create_registration_requests()

        print("\n✅ Peuplement terminé avec succès!")
        print("\n📊 Résumé:")
        print(f"   - {len(users)} utilisateurs")
        print(f"   - {len(merchants)} merchants")
        print(f"   - {len(products) if 'products' in locals() else 0} produits")
        print(f"   - {len(services) if 'services' in locals() else 0} services")
        print(f"   - {len(subscriptions)} abonnements")
        print(f"   - {len(transactions)} transactions")
        print(f"   - {len(registrations)} demandes d'inscription")

        print("\n🔐 Comptes de test créés:")
        print("   Admin:      admin@getyourshare.com / Admin123!")
        print("   Merchant:   merchant1@example.com / Merchant123!")
        print("   Influencer: influencer1@example.com / Influencer123!")
        print("   Commercial: commercial1@example.com / Commercial123!")

    except Exception as e:
        print(f"\n❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
