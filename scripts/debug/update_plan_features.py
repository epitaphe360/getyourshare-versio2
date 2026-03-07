
import os
from supabase import create_client
import json

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"
supabase = create_client(url, key)

# Update Marketplace Plan (Influencers)
marketplace_features = {
    "support": "priority",
    "analytics_level": "advanced",
    "marketplace_access": True,
    "commission_rate": 3.0,
    "instant_payout": True,
    "priority_support": True,
    "max_campaigns": None, # Unlimited
    "max_tracking_links": None # Unlimited
}

print("Updating Marketplace plan features...")
try:
    data = supabase.table("subscription_plans").update({"features": marketplace_features}).eq("code", "marketplace").execute()
    print("Success:", data.data)
except Exception as e:
    print("Error updating Marketplace:", e)

# Update Pro Plan (Legacy/Standard)
pro_features = {
    "instant_payout": True,
    "priority_support": False,
    "advanced_analytics": True,
    "commission_rate": 10.0,
    "analytics_level": "advanced"
}

print("Updating Pro plan features...")
try:
    data = supabase.table("subscription_plans").update({"features": pro_features}).eq("code", "pro").execute()
    print("Success:", data.data)
except Exception as e:
    print("Error updating Pro:", e)
