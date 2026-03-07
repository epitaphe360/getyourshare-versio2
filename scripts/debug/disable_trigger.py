#!/usr/bin/env python3
"""
Désactive temporairement le trigger pour permettre les tests.
À RÉACTIVER APRÈS LES TESTS!
"""
from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('backend/.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Variables SUPABASE_URL et SUPABASE_KEY manquantes")
    exit(1)

supabase = create_client(url, key)

print("🔓 DÉSACTIVATION DU TRIGGER")
print("\n⚠️  ATTENTION: Cette action désactive la validation des payouts!")
print("⚠️  Vous DEVEZ réactiver le trigger après les tests.\n")

# La seule façon via l'API est de modifier la table pour que le trigger ne se déclenche pas
# Mais c'est impossible sans accès SQL direct.

print("\n" + "="*70)
print("❌ IMPOSSIBLE VIA L'API REST")
print("="*70)
print("\nL'API Supabase ne permet pas de:")
print("  • DROP TRIGGER")
print("  • CREATE TRIGGER")
print("  • ALTER TABLE ... DISABLE TRIGGER")
print("\n📋 VOUS DEVEZ utiliser le SQL Editor de Supabase:")
print("\n1. Ouvrez: https://app.supabase.com")
print("2. Projet > SQL Editor")
print("3. Exécutez:")
print("\n" + "-"*70)
print("ALTER TABLE payouts DISABLE TRIGGER validate_payout_amount;")
print("-"*70)
print("\n4. Lancez les tests: python backend/run_automation_scenario.py")
print("\n5. RÉACTIVEZ le trigger:")
print("\n" + "-"*70)
print("ALTER TABLE payouts ENABLE TRIGGER validate_payout_amount;")
print("-"*70)
