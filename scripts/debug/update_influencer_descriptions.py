
import os
from supabase import create_client, Client

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

supabase: Client = create_client(url, key)

print("Updating Influencer Plans Descriptions...")

# 1. Starter
description_starter = "Idéal pour débuter. Accédez aux campagnes standard, générez des liens de tracking illimités et recevez vos paiements chaque mois. Commission standard de 5%."
try:
    supabase.table("subscription_plans").update({
        "description": description_starter
    }).eq("code", "starter").execute()
    print("Updated Starter description")
except Exception as e:
    print(f"Error Starter: {e}")

# 2. Pro
description_pro = "Boostez vos revenus. Accès aux campagnes Premium, paiements instantanés, analytics détaillés pour optimiser vos performances et support prioritaire. Commission réduite à 3%."
try:
    supabase.table("subscription_plans").update({
        "description": description_pro
    }).eq("code", "pro").execute()
    print("Updated Pro description")
except Exception as e:
    print(f"Error Pro: {e}")

# 3. Enterprise
description_enterprise = "Pour les pros. Accès illimité à toutes les campagnes, manager dédié, paiements instantanés, analytics complets et 0% de commission sur vos revenus."
try:
    # Update both 'elite' and 'enterprise_influencer' codes just in case
    supabase.table("subscription_plans").update({
        "description": description_enterprise
    }).in_("code", ["elite", "enterprise_influencer"]).execute()
    print("Updated Enterprise description")
except Exception as e:
    print(f"Error Enterprise: {e}")

print("Done.")
