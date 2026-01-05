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

def run_correction():
    print("Applying full price correction...")
    try:
        with open('CORRECT_ALL_PRICES.sql', 'r') as f:
            sql_content = f.read()
            
        # Split by semicolon to execute statements individually
        statements = sql_content.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt or stmt.startswith('--'):
                continue
                
            try:
                # Try RPC first
                supabase.rpc('exec_sql', {'query': stmt}).execute()
                print(f"Executed via RPC: {stmt[:50]}...")
            except Exception:
                # Fallback to table updates based on WHERE clause analysis (simple parser)
                if "UPDATE subscription_plans" in stmt:
                    # Extract code
                    import re
                    code_match = re.search(r"code = '(\w+)'", stmt)
                    if code_match:
                        code = code_match.group(1)
                        # Extract values
                        price_mad = re.search(r"price_mad = ([\d\.]+)", stmt)
                        price = re.search(r"price = ([\d\.]+)", stmt)
                        price_usd = re.search(r"price_usd = ([\d\.]+)", stmt)
                        
                        data = {}
                        if price_mad: data['price_mad'] = float(price_mad.group(1))
                        if price: data['price'] = float(price.group(1))
                        if price_usd: data['price_usd'] = float(price_usd.group(1))
                        
                        if data:
                            supabase.table("subscription_plans").update(data).eq("code", code).execute()
                            print(f"Updated {code} via Table API: {data}")
                    elif "price = 0" in stmt:
                         data = {'price_mad': 0, 'price': 0, 'price_usd': 0}
                         supabase.table("subscription_plans").update(data).eq("price", 0).execute()
                         print("Updated free plans via Table API")

    except Exception as e:
        print(f"Error: {e}")

run_correction()
