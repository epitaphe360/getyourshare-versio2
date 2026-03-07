"""
Script pour ajouter des colonnes budget aux merchants
et insérer des données de test réalistes
"""
import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv
import random

# Charger le .env depuis le dossier courant ou backend
if Path(".env").exists():
    load_dotenv()
elif Path("backend/.env").exists():
    load_dotenv("backend/.env")
else:
    print("❌ Fichier .env introuvable")
    sys.exit(1)

# Vérifier que les variables sont chargées
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print(f"❌ Variables d'environnement manquantes:")
    print(f"   SUPABASE_URL: {'✅' if supabase_url else '❌'}")
    print(f"   SUPABASE_KEY: {'✅' if supabase_key else '❌'}")
    print(f"\n💡 Lancez ce script depuis le dossier backend:")
    print(f"   cd backend")
    print(f"   python ../add_merchant_budgets.py")
    sys.exit(1)

# Connexion Supabase
supabase = create_client(supabase_url, supabase_key)

def add_budget_columns_and_data():
    """Ajoute les colonnes de budget si elles n'existent pas et met à jour les données"""
    
    print("\n" + "="*60)
    print("🔧 AJOUT DES COLONNES DE BUDGET AUX MERCHANTS")
    print("="*60 + "\n")
    
    # Récupérer tous les merchants
    result = supabase.table("users").select("id, email, company_name").eq("role", "merchant").execute()
    merchants = result.data
    
    if not merchants:
        print("❌ Aucun merchant trouvé dans la base de données")
        return
    
    print(f"✅ {len(merchants)} merchants trouvés\n")
    
    # Données budgétaires réalistes pour chaque merchant
    budgets = [
        {"balance": 5000.00, "total_spent": 15000.00, "campaigns_count": 5},
        {"balance": 12500.50, "total_spent": 8700.25, "campaigns_count": 3},
        {"balance": 3200.00, "total_spent": 22000.00, "campaigns_count": 8},
        {"balance": 8750.75, "total_spent": 11200.50, "campaigns_count": 4},
        {"balance": 15000.00, "total_spent": 5000.00, "campaigns_count": 2},
        {"balance": 2500.00, "total_spent": 18500.00, "campaigns_count": 6},
        {"balance": 9800.00, "total_spent": 13400.00, "campaigns_count": 7},
        {"balance": 20000.00, "total_spent": 3000.00, "campaigns_count": 1},
    ]
    
    # Mettre à jour chaque merchant avec des données budgétaires
    for i, merchant in enumerate(merchants):
        budget_data = budgets[i % len(budgets)]  # Cycle à travers les budgets
        
        try:
            # Mise à jour du merchant
            update_result = supabase.table("users").update({
                "balance": budget_data["balance"],
                "total_spent": budget_data["total_spent"],
                "campaigns_count": budget_data["campaigns_count"]
            }).eq("id", merchant["id"]).execute()
            
            print(f"✅ Merchant: {merchant.get('email', 'N/A')}")
            print(f"   Balance: {budget_data['balance']} €")
            print(f"   Total dépensé: {budget_data['total_spent']} €")
            print(f"   Campagnes: {budget_data['campaigns_count']}")
            print()
            
        except Exception as e:
            print(f"❌ Erreur pour {merchant.get('email', 'N/A')}: {e}")
            print(f"   Note: Les colonnes balance, total_spent, campaigns_count doivent exister dans la table users")
            print(f"   Utilisez le SQL suivant dans Supabase:")
            print(f"""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS balance DECIMAL(10,2) DEFAULT 0;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS total_spent DECIMAL(10,2) DEFAULT 0;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS campaigns_count INTEGER DEFAULT 0;
            """)
            return
    
    print("\n" + "="*60)
    print("✅ BUDGETS AJOUTÉS AVEC SUCCÈS!")
    print("="*60)
    print("\n💡 Rafraîchissez la page 'Annonceurs' pour voir les budgets")

if __name__ == "__main__":
    add_budget_columns_and_data()
