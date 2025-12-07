#!/usr/bin/env python3
"""
Appliquer la correction du trigger via SQL direct
Note: Supabase ne permet pas d'exécuter du DDL via l'API REST
Ce script affiche le SQL à exécuter manuellement
"""
import os

print("=" * 70)
print("🔧 CORRECTION DU TRIGGER PAYOUTS")
print("=" * 70)

print("\n📋 SQL à exécuter dans Supabase SQL Editor:")
print("\n" + "-" * 70)

with open("FIX_PAYOUT_TRIGGER.sql", "r", encoding="utf-8") as f:
    sql = f.read()
    print(sql)

print("-" * 70)

print("\n💡 Instructions:")
print("1. Copiez le SQL ci-dessus")
print("2. Ouvrez Supabase Dashboard > SQL Editor")
print("3. Collez et exécutez le SQL")
print("4. Relancez le script d'automation")

print("\n" + "=" * 70)

# Alternative: Désactiver temporairement le trigger pour les tests
print("\n🔓 ALTERNATIVE: Désactiver temporairement le trigger pour les tests")
print("\nSQL pour désactiver:")
print("ALTER TABLE payouts DISABLE TRIGGER validate_payout_amount;")
print("\nSQL pour réactiver:")
print("ALTER TABLE payouts ENABLE TRIGGER validate_payout_amount;")

print("\n" + "=" * 70)
