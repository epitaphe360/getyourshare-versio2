import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 60)
print("CORRECTION DES MERCHANT_ID DANS LES FACTURES")
print("=" * 60)

# 1. Trouver un merchant dans la base de données
merchants = supabase.from_("users").select("id, email, company_name").eq("role", "merchant").limit(1).execute()

if not merchants.data or len(merchants.data) == 0:
    print("\n❌ Aucun merchant trouvé. Création d'un merchant de test...")
    
    # Créer un merchant de test
    new_merchant = {
        "email": "merchant.test@shareyoursales.ma",
        "role": "merchant",
        "company_name": "Test Company",
        "phone": "+212600000000",
        "is_active": True
    }
    
    merchant_result = supabase.from_("users").insert(new_merchant).execute()
    if merchant_result.data:
        merchant_id = merchant_result.data[0]['id']
        print(f"✅ Merchant créé avec l'ID: {merchant_id}")
    else:
        print("❌ Erreur lors de la création du merchant")
        exit(1)
else:
    merchant_id = merchants.data[0]['id']
    merchant_name = merchants.data[0].get('company_name') or merchants.data[0].get('email')
    print(f"\n✅ Merchant trouvé: {merchant_name}")
    print(f"   ID: {merchant_id}")

# 2. Mettre à jour toutes les factures avec ce merchant_id
invoices = supabase.from_("invoices").select("id, invoice_number, merchant_id").execute()

if invoices.data:
    null_merchant_invoices = [inv for inv in invoices.data if inv.get('merchant_id') is None]
    
    print(f"\n📊 Total factures: {len(invoices.data)}")
    print(f"   Factures sans merchant_id: {len(null_merchant_invoices)}")
    
    if len(null_merchant_invoices) > 0:
        print(f"\n🔧 Mise à jour de {len(null_merchant_invoices)} factures...")
        
        for inv in null_merchant_invoices:
            result = supabase.from_("invoices").update({
                "merchant_id": merchant_id
            }).eq("id", inv['id']).execute()
            
            if result.data:
                print(f"   ✅ {inv['invoice_number']} → merchant_id ajouté")
            else:
                print(f"   ❌ {inv['invoice_number']} → erreur")
        
        print(f"\n✅ Mise à jour terminée!")
    else:
        print("\n✅ Toutes les factures ont déjà un merchant_id")
else:
    print("\n⚠️ Aucune facture trouvée")

# 3. Vérification finale
invoices_check = supabase.from_("invoices").select("id, invoice_number, merchant_id").execute()
if invoices_check.data:
    with_merchant = [inv for inv in invoices_check.data if inv.get('merchant_id') is not None]
    print(f"\n✅ Vérification finale:")
    print(f"   {len(with_merchant)}/{len(invoices_check.data)} factures ont un merchant_id")

print("\n" + "=" * 60)
