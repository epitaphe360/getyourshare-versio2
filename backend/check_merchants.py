#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour vérifier les merchants dans la base de données
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv()

# Initialiser Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def check_merchants():
    """Vérifier les merchants dans la BD"""
    print("\n🔍 Vérification des merchants...\n")
    
    # Récupérer tous les merchants
    result = supabase.table("users").select("id, email, role, status, username, subscription_plan, created_at").eq("role", "merchant").execute()
    
    merchants = result.data or []
    print(f"📊 Total merchants: {len(merchants)}\n")
    
    if merchants:
        print("Liste des merchants:")
        print("-" * 100)
        for m in merchants:
            print(f"  📧 Email: {m.get('email', 'N/A')}")
            print(f"     Username: {m.get('username', 'N/A')}")
            print(f"     Status: {m.get('status', 'N/A')}")
            print(f"     Subscription: {m.get('subscription_plan', 'N/A')}")
            print(f"     Created: {m.get('created_at', 'N/A')[:10] if m.get('created_at') else 'N/A'}")
            print("-" * 100)
    else:
        print("❌ Aucun merchant trouvé dans la base de données")
        print("\n💡 Le compte merchant test devrait exister.")
        print("   Email: merchant@test.com")
        print("   Mot de passe: merchant123")
        print("\n   Vérifiez si le compte existe en consultant la table 'users'")

if __name__ == "__main__":
    check_merchants()
