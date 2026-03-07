
import os
from supabase import create_client, Client

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

supabase: Client = create_client(url, key)

try:
    # Try to select one row to see keys
    response = supabase.table("subscription_plans").select("*").limit(1).execute()
    if response.data:
        print("Columns:", response.data[0].keys())
    else:
        print("Table is empty, cannot infer columns from data.")
except Exception as e:
    print(f"Error inspecting table: {e}")
