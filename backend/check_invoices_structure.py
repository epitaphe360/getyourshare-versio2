import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 60)
print("STRUCTURE DE LA TABLE INVOICES")
print("=" * 60)

# Récupérer une facture pour voir sa structure
result = supabase.from_("invoices").select("*").limit(1).execute()

if result.data and len(result.data) > 0:
    invoice = result.data[0]
    print("\n✅ COLONNES DISPONIBLES:")
    for key in sorted(invoice.keys()):
        value = invoice[key]
        value_type = type(value).__name__
        print(f"   - {key}: {value_type} = {value}")
else:
    print("\n⚠️ Aucune facture trouvée")

print("\n" + "=" * 60)
