
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def apply_sql(filename):
    print(f"Applying {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split by statement (simple split by ;)
    commands = [cmd.strip() for cmd in sql.split(';') if cmd.strip()]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        try:
            # Try 'query' param first
            supabase.rpc('exec_sql', {'query': cmd}).execute()
            print("Success via RPC (query)")
        except Exception as e:
            print(f"RPC (query) failed: {e}")
            try:
                # Try 'sql_query' param
                supabase.rpc('exec_sql', {'sql_query': cmd}).execute()
                print("Success via RPC (sql_query)")
            except Exception as e2:
                print(f"RPC (sql_query) failed: {e2}")

if __name__ == "__main__":
    apply_sql('ADD_STATUS_COLUMNS.sql')
