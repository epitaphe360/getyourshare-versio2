import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 60)
print("VÉRIFICATION DES FACTURES")
print("=" * 60)

# Vérifier les factures existantes
result = supabase.from_("invoices").select("*").execute()
invoices = result.data if result.data else []

print(f"\n✅ Nombre de factures: {len(invoices)}")

if len(invoices) > 0:
    print("\n📄 FACTURES EXISTANTES:")
    for inv in invoices[:5]:  # Afficher les 5 premières
        print(f"\n  - ID: {inv.get('id')}")
        print(f"    Numéro: {inv.get('invoice_number')}")
        print(f"    Merchant ID: {inv.get('merchant_id')}")
        print(f"    Montant: {inv.get('amount')} {inv.get('currency', 'EUR')}")
        print(f"    Statut: {inv.get('status')}")
        print(f"    Date: {inv.get('created_at')}")
else:
    print("\n⚠️  AUCUNE FACTURE - Création de données de test...")
    
    # Récupérer un merchant pour les factures test
    merchants = supabase.from_("users").select("id, email, company_name").eq("role", "merchant").limit(5).execute()
    
    if merchants.data and len(merchants.data) > 0:
        print(f"\n✅ {len(merchants.data)} merchants trouvés")
        
        test_invoices = []
        base_date = datetime.now()
        
        for i, merchant in enumerate(merchants.data[:3], 1):
            invoice = {
                "merchant_id": merchant['id'],
                "invoice_number": f"INV-2024-{str(i).zfill(4)}",
                "amount": 1000.00 + (i * 500),
                "tax_amount": (1000.00 + (i * 500)) * 0.2,
                "total_amount": (1000.00 + (i * 500)) * 1.2,
                "currency": "EUR",
                "description": f"Services de marketing digital - Mois {i}",
                "status": ["pending", "paid", "pending"][i % 3],
                "created_at": (base_date - timedelta(days=i*10)).isoformat(),
                "due_date": (base_date + timedelta(days=30-i*10)).isoformat(),
                "paid_at": (base_date - timedelta(days=i*5)).isoformat() if i == 2 else None
            }
            test_invoices.append(invoice)
            print(f"\n  Facture {i}:")
            print(f"    Merchant: {merchant.get('company_name') or merchant.get('email')}")
            print(f"    Montant: {invoice['total_amount']:.2f} EUR")
            print(f"    Statut: {invoice['status']}")
        
        # Insérer les factures
        result = supabase.from_("invoices").insert(test_invoices).execute()
        
        if result.data:
            print(f"\n✅ {len(result.data)} factures de test créées avec succès!")
        else:
            print("\n❌ Erreur lors de la création des factures")
    else:
        print("\n❌ Aucun merchant trouvé pour créer les factures de test")
        print("   Veuillez d'abord créer des utilisateurs avec le rôle 'merchant'")

print("\n" + "=" * 60)
