import os
from supabase import create_client

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"
supabase = create_client(url, key)

def run_sql_file(filename):
    print(f"Running {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        sql = f.read()
        # Split by semicolon to run statements individually if needed, 
        # but Supabase RPC 'exec_sql' (if available) or just raw SQL via a client is needed.
        # The python client doesn't support raw SQL directly on the public schema easily without RPC.
        # However, we can try to use a workaround or just assume the user has a way.
        # Actually, I can't run raw SQL easily with supabase-py unless I have a postgres connection string or an RPC function.
        
        # Let's try to use the 'rpc' method if a 'exec_sql' function exists, 
        # otherwise we might need to use psycopg2 if available or just skip this if I can't.
        
        # But wait, I can use the 'update' method I used before for specific tables.
        # The SQL file contains UPDATE statements. I can parse them and execute them via the client.
        pass

# Since I can't easily run raw SQL file without a dedicated RPC or PG driver, 
# I will implement the updates using the Supabase client directly in Python.

print("Updating prices via Supabase client...")

# 1. Marketplace
try:
    supabase.table("subscription_plans").update({
        "price_mad": 99.00,
        "price": 9.90,
        "price_usd": 10.90
    }).eq("code", "marketplace").execute()
    print("Updated Marketplace")
except Exception as e:
    print(f"Error Marketplace: {e}")

# 2. Small
try:
    supabase.table("subscription_plans").update({
        "price_mad": 199.00,
        "price": 19.90,
        "price_usd": 21.90
    }).eq("code", "small").execute()
    print("Updated Small")
except Exception as e:
    print(f"Error Small: {e}")

# 3. Medium
try:
    supabase.table("subscription_plans").update({
        "price_mad": 499.00,
        "price": 49.90,
        "price_usd": 54.90
    }).eq("code", "medium").execute()
    print("Updated Medium")
except Exception as e:
    print(f"Error Medium: {e}")

# 4. Large
try:
    supabase.table("subscription_plans").update({
        "price_mad": 799.00,
        "price": 79.90,
        "price_usd": 87.90
    }).eq("code", "large").execute()
    print("Updated Large")
except Exception as e:
    print(f"Error Large: {e}")

# 5. Starter
try:
    supabase.table("subscription_plans").update({
        "price_mad": 290.00,
        "price": 29.00,
        "price_usd": 32.00
    }).eq("code", "starter").execute()
    print("Updated Starter")
except Exception as e:
    print(f"Error Starter: {e}")

# 6. Pro
try:
    supabase.table("subscription_plans").update({
        "price_mad": 490.00,
        "price": 49.00,
        "price_usd": 54.00
    }).eq("code", "pro").execute()
    print("Updated Pro")
except Exception as e:
    print(f"Error Pro: {e}")

# 7. Elite
try:
    supabase.table("subscription_plans").update({
        "price_mad": 990.00,
        "price": 99.00,
        "price_usd": 109.00
    }).eq("code", "elite").execute()
    print("Updated Elite")
except Exception as e:
    print(f"Error Elite: {e}")

# 8. Free
try:
    supabase.table("subscription_plans").update({
        "price_mad": 0,
        "price": 0,
        "price_usd": 0
    }).or_("price.eq.0,price_mad.eq.0").execute()
    print("Updated Free plans")
except Exception as e:
    print(f"Error Free: {e}")
