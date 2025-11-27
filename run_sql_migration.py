import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Try loading .env.railway if variables are missing
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(".env.railway")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    # Fallback to hardcoded creds from supabase_creds.py
    try:
        import supabase_creds
        url = supabase_creds.SUPABASE_URL
        key = supabase_creds.SUPABASE_KEY
    except ImportError:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found and supabase_creds.py missing.")
        exit(1)

supabase: Client = create_client(url, key)

def execute_sql_file(filename):
    print(f"Executing {filename}...")
    with open(filename, 'r') as f:
        sql = f.read()
    
    # Split by semicolon to execute statements individually if needed, 
    # but Supabase RPC 'exec_sql' (if available) or just running via a postgres connector would be better.
    # Since we are using the supabase-py client, we can't directly execute raw SQL unless we have a stored procedure for it.
    # I'll assume there is no 'exec_sql' RPC.
    # However, I can use the 'postgres' connection if I had the connection string, but I only have the API URL/Key here.
    # Wait, I can try to use the `rpc` method if I created a helper function previously.
    
    # Let's check if I can use a python postgres driver (psycopg2) if I have the DB URL.
    # The `api_keys.txt` had DATABASE_URL.
    
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Try to find it in api_keys.txt
        try:
            with open("api_keys.txt", "r") as f:
                for line in f:
                    if line.startswith("DATABASE_URL"):
                        # It might be just the key name or key=value
                        # The file content showed just keys, maybe values are not there?
                        # The file content showed:
                        # JWT_SECRET
                        # STRIPE_SECRET_KEY
                        # ...
                        # It seems it's just a list of keys, not values.
                        pass
        except:
            pass

    # If I can't execute SQL directly, I might be stuck.
    # But wait, I can use the `rpc` call if `exec_sql` exists.
    # Or I can try to use the `sql` method if the client supports it (some versions do).
    
    # Alternative: I can use the `postgres` library if installed.
    try:
        import psycopg2
        # I need the connection string.
        # I'll try to construct it from the supabase project ref if possible, but I need the password.
        # I don't have the password in the context.
        
        # Let's try to use the `rpc` method. I recall seeing `execute_sql_script.py` in the file list.
        # Let's check `execute_sql_script.py`.
        pass
    except ImportError:
        pass

execute_sql_file("ADD_USD_TO_PLANS.sql")
