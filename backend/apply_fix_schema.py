import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env vars
load_dotenv(os.path.join(os.getcwd(), '.env'))
load_dotenv(os.path.join(os.getcwd(), '..', '.env'))

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
            
        # Split by semicolon to execute statements individually if needed, 
        # but Supabase RPC might handle blocks.
        # However, Supabase-py doesn't have a direct 'query' method for raw SQL unless we use an RPC function that executes SQL.
        # But we can use the `postgres` interface if available or just try to use a known RPC function if one exists.
        # Wait, usually we can't execute raw SQL via the JS/Python client unless we have a specific RPC function for it.
        
        # Let's check if there is an `exec_sql` or similar RPC function.
        # If not, we might be stuck unless we have direct postgres access.
        
        # But wait, the user asked me to run SQL queries before. How did I do it?
        # I used `backend/apply_sql.py` in my previous attempt, but it failed because it didn't exist.
        
        # If I can't run raw SQL, I can't apply the schema fix easily.
        # I'll assume there is an `exec_sql` function or I'll try to create one if I can (but I can't create one without running SQL!).
        
        # Let's try to use the `rpc` method to call `exec_sql` if it exists.
        # If not, I might have to tell the user I can't run SQL directly.
        
        # However, looking at the context, there was a `backend/test_full_system.py` that ran successfully.
        
        # Let's try to use `rpc('exec_sql', {'query': sql_content})`.
        
        response = supabase.rpc('exec_sql', {'query': sql_content}).execute()
        print("Success:", response)
        
    except Exception as e:
        print(f"Error applying SQL: {e}")
        # Fallback: Try to split statements?
        # Or maybe the RPC function is named differently.

if __name__ == "__main__":
    if len(sys.argv) > 1:
        apply_sql_file(sys.argv[1])
    else:
        # Default to FIX_MISSING_SCHEMA.sql in the parent directory
        apply_sql_file(os.path.join(os.path.dirname(os.getcwd()), 'FIX_MISSING_SCHEMA.sql'))
