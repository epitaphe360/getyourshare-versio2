import os
from supabase import create_client, Client

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

supabase: Client = create_client(url, key)

try:
    response = supabase.table("subscription_plans").select("*").execute()
    plans = response.data
    print(f"Found {len(plans)} plans:")
    for plan in plans:
        print(f"ID: {plan.get('id')}, Code: {plan.get('code')}, Name: {plan.get('name')}, Type: {plan.get('type')}, Active: {plan.get('is_active')}, Price: {plan.get('price_mad')} MAD")
        print(f"   Description: {plan.get('description')}")
        print("-" * 20)
except Exception as e:
    print(f"Error fetching plans: {e}")
