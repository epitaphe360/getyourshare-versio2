
import os
import json
from supabase import create_client, Client

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

supabase: Client = create_client(url, key)

print("Applying Influencer Plans Updates...")

# 1. Deactivate Marketplace (99 MAD)
try:
    supabase.table("subscription_plans").update({
        "is_active": False
    }).eq("code", "marketplace").execute()
    print("Deactivated Marketplace plan")
except Exception as e:
    print(f"Error deactivating Marketplace: {e}")

# 2. Upsert Starter (290 MAD)
try:
    # Check if exists
    res = supabase.table("subscription_plans").select("id").eq("code", "starter").execute()
    if res.data:
        # Update
        supabase.table("subscription_plans").update({
            "name": "Starter",
            "type": "marketplace",
            "price_mad": 290.00,
            "price": 29.00,
            "price_usd": 32.00,
            # "role": "influencer", # Column does not exist
            "is_active": True,
            "features": {
                "commission_rate": 5,
                "analytics_level": "basic",
                "instant_payout": False,
                "priority_support": False
            }
        }).eq("code", "starter").execute()
        print("Updated Starter plan")
    else:
        # Insert
        supabase.table("subscription_plans").insert({
            "code": "starter",
            "name": "Starter",
            "type": "marketplace",
            "price_mad": 290.00,
            "price": 29.00,
            "price_usd": 32.00,
            # "role": "influencer", # Column does not exist
            "is_active": True,
            "features": {
                "commission_rate": 5,
                "analytics_level": "basic",
                "instant_payout": False,
                "priority_support": False
            }
        }).execute()
        print("Created Starter plan")
except Exception as e:
    print(f"Error Starter: {e}")

# 3. Update Pro (490 MAD)
try:
    # Check if exists
    res = supabase.table("subscription_plans").select("id").eq("code", "pro").execute()
    if res.data:
        supabase.table("subscription_plans").update({
            "name": "Pro",
            "type": "marketplace",
            "price_mad": 490.00,
            "price": 49.00,
            "price_usd": 54.00,
            # "role": "influencer",
            "is_active": True,
            "features": {
                "commission_rate": 3,
                "analytics_level": "advanced",
                "instant_payout": True,
                "priority_support": True
            }
        }).eq("code", "pro").execute()
        print("Updated Pro plan")
    else:
        supabase.table("subscription_plans").insert({
            "code": "pro",
            "name": "Pro",
            "type": "marketplace",
            "price_mad": 490.00,
            "price": 49.00,
            "price_usd": 54.00,
            # "role": "influencer",
            "is_active": True,
            "features": {
                "commission_rate": 3,
                "analytics_level": "advanced",
                "instant_payout": True,
                "priority_support": True
            }
        }).execute()
        print("Created Pro plan")
except Exception as e:
    print(f"Error Pro: {e}")

# 4. Update Elite -> Enterprise (990 MAD)
try:
    # Try to find 'elite' first
    res = supabase.table("subscription_plans").select("id").eq("code", "elite").execute()
    if res.data:
        supabase.table("subscription_plans").update({
            "name": "Enterprise",
            "type": "marketplace",
            "price_mad": 990.00,
            "price": 99.00,
            "price_usd": 109.00,
            # "role": "influencer",
            "is_active": True,
            "features": {
                "commission_rate": 0,
                "analytics_level": "full",
                "instant_payout": True,
                "priority_support": True,
                "dedicated_manager": True
            }
        }).eq("code", "elite").execute()
        print("Updated Elite to Enterprise")
    else:
        # If elite doesn't exist, check for 'enterprise_influencer' or create it
        res2 = supabase.table("subscription_plans").select("id").eq("code", "enterprise_influencer").execute()
        if res2.data:
             supabase.table("subscription_plans").update({
                "name": "Enterprise",
                "type": "marketplace",
                "price_mad": 990.00,
                "price": 99.00,
                "price_usd": 109.00,
                # "role": "influencer",
                "is_active": True,
                "features": {
                    "commission_rate": 0,
                    "analytics_level": "full",
                    "instant_payout": True,
                    "priority_support": True,
                    "dedicated_manager": True
                }
            }).eq("code", "enterprise_influencer").execute()
             print("Updated Enterprise Influencer plan")
        else:
            # Create
            supabase.table("subscription_plans").insert({
                "code": "enterprise_influencer",
                "name": "Enterprise",
                "type": "marketplace",
                "price_mad": 990.00,
                "price": 99.00,
                "price_usd": 109.00,
                # "role": "influencer",
                "is_active": True,
                "features": {
                    "commission_rate": 0,
                    "analytics_level": "full",
                    "instant_payout": True,
                    "priority_support": True,
                    "dedicated_manager": True
                }
            }).execute()
            print("Created Enterprise Influencer plan")

except Exception as e:
    print(f"Error Enterprise: {e}")

print("Done.")
