import sys
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(".env.railway")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found.")
    exit(1)

supabase: Client = create_client(url, key)

def apply_sql():
    print("Applying generated_link_id column to affiliate_requests...")
    
    sql_commands = [
        "ALTER TABLE affiliate_requests ADD COLUMN IF NOT EXISTS generated_link_id UUID;"
    ]
    
    for cmd in sql_commands:
        try:
            print(f"Executing: {cmd}")
            # Try RPC exec_sql
            response = supabase.rpc('exec_sql', {'query': cmd}).execute()
            print("Success.")
        except Exception as e:
            print(f"RPC failed for command: {cmd}")
            print(f"Error: {e}")
            print("Please execute the SQL manually in Supabase SQL Editor.")

if __name__ == "__main__":
    apply_sql()
