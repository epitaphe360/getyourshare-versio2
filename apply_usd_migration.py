import sys
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
# Try loading .env.railway if variables are missing
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

def run_migration():
    print("Attempting to run ADD_USD_TO_PLANS.sql via exec_sql RPC...")
    try:
        with open('ADD_USD_TO_PLANS.sql', 'r') as f:
            sql_content = f.read()
            
        # Try to execute the whole block
        response = supabase.rpc('exec_sql', {'query': sql_content}).execute()
        print("Migration executed successfully via RPC.")
    except Exception as e:
        print(f"RPC failed: {e}")
        print("Trying to execute statements one by one...")
        
        # Split by semicolon
        statements = sql_content.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            try:
                supabase.rpc('exec_sql', {'query': stmt}).execute()
                print(f"Executed: {stmt[:50]}...")
            except Exception as inner_e:
                print(f"Failed to execute statement: {stmt[:50]}... Error: {inner_e}")

run_migration()
