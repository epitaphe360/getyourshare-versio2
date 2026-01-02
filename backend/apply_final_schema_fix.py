import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env vars
# Try loading from backend/.env first, then root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
    sys.exit(1)

supabase: Client = create_client(url, key)

def apply_sql_file(file_path):
    print(f"Applying SQL from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # Execute the SQL using the exec_sql RPC function
        print("Executing SQL via exec_sql RPC...")
        response = supabase.rpc('exec_sql', {'query': sql_content}).execute()
        print("Success:", response)
        
    except Exception as e:
        print(f"Error applying SQL: {e}")
        print("\nIf the error is 'function exec_sql does not exist', you must run the SQL manually in the Supabase Dashboard.")

if __name__ == "__main__":
    # Path to the SQL file relative to this script
    sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'FIX_DB_SCHEMA_FINAL.sql')
    
    if os.path.exists(sql_file_path):
        apply_sql_file(sql_file_path)
    else:
        print(f"Error: SQL file not found at {sql_file_path}")
