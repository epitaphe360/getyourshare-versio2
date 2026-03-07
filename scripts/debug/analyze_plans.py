import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)
os.chdir(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv("backend/.env")

from utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

print("\n📊 Analyse des plans d'abonnement dans la base...\n")

# Récupérer tous les plans utilisés
result = supabase.from_("users").select("subscription_plan").execute()

plans = {}
for user in result.data:
    plan = user.get('subscription_plan')
    if plan:
        plans[plan] = plans.get(plan, 0) + 1
    else:
        plans['NULL'] = plans.get('NULL', 0) + 1

print("Plans actuellement utilisés:")
for plan, count in sorted(plans.items()):
    print(f"  - {plan}: {count} utilisateur(s)")

print(f"\n✅ Total: {len(plans)} plans différents")

# Générer le script SQL corrigé
all_plans = [p for p in plans.keys() if p != 'NULL']
all_plans.extend(['professional', 'premium', 'enterprise'])
all_plans = sorted(set(all_plans))

print("\n📋 Script SQL à exécuter dans Supabase:\n")
print("-" * 60)
print("-- Supprimer l'ancienne contrainte")
print("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_subscription_plan_check;")
print()
print("-- Ajouter la nouvelle contrainte avec TOUS les plans")
plans_list = "', '".join(all_plans)
print(f"ALTER TABLE users ADD CONSTRAINT users_subscription_plan_check")
print(f"CHECK (subscription_plan IS NULL OR subscription_plan IN ('{plans_list}'));")
print("-" * 60)
print("\n✅ Ce script acceptera NULL et tous les plans existants + nouveaux\n")
