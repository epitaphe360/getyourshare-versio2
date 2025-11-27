import os
from supabase import create_client
import json

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"
supabase = create_client(url, key)

print("Fetching subscription plans...")
try:
    response = supabase.table("subscription_plans").select("*").execute()
    plans = response.data
    for plan in plans:
        print(f"Plan: {plan.get('name')} (Code: {plan.get('code')})")
        print(f"Features: {json.dumps(plan.get('features'), indent=2)}")
        print("-" * 30)
except Exception as e:
    print("Error:", e)
