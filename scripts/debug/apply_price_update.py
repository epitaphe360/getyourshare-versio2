import sys
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(".env.railway")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    try:
        import supabase_creds
        url = supabase_creds.SUPABASE_URL
        key = supabase_creds.SUPABASE_KEY
    except ImportError:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found.")
        exit(1)

supabase: Client = create_client(url, key)

def run_update():
    print("Updating Marketplace plan price...")
    try:
        with open('UPDATE_MARKETPLACE_PRICE.sql', 'r') as f:
            sql_content = f.read()
            
        # Try RPC
        try:
            supabase.rpc('exec_sql', {'query': sql_content}).execute()
            print("Update executed via RPC.")
        except Exception:
            # Fallback: execute statement directly if possible or via separate calls if we had a way
            # Since we don't have direct SQL access without RPC or a driver, and RPC failed before...
            # We can try to use the table interface to update.
            print("RPC failed. Trying table update...")
            
            data = {
                "price": 29.00,
                "price_mad": 290.00,
                "price_usd": 32.00
            }
            
            response = supabase.table("subscription_plans").update(data).eq("code", "marketplace").execute()
            print(f"Update response: {response}")

    except Exception as e:
        print(f"Error: {e}")

run_update()
