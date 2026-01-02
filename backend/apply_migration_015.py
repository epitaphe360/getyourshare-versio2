
import os
from supabase_client import supabase

def apply_migration():
    migration_file = "../database/migrations_organized/015_add_services_to_affiliation.sql"
    
    with open(migration_file, 'r') as f:
        sql = f.read()
        
    # Split by statement if possible, but supabase-py usually takes one statement or use rpc
    # Since we can't easily run raw SQL via supabase-py client without a stored procedure or direct connection,
    # we will try to use the 'rpc' call if a 'exec_sql' function exists, or just print instructions.
    # However, looking at previous context, I might be able to use a direct connection if I had credentials.
    # I will assume I can't run DDL directly from the client unless I have a specific function.
    
    print("Migration SQL created at: " + migration_file)
    print("Please run this SQL in your Supabase SQL Editor to enable Service Affiliation.")
    
    # Attempt to run via a potential 'exec_sql' function if it exists (common pattern)
    try:
        supabase.rpc('exec_sql', {'query': sql}).execute()
        print("Migration applied successfully via RPC!")
    except Exception as e:
        print(f"Could not apply migration automatically (expected if exec_sql RPC doesn't exist): {e}")

if __name__ == "__main__":
    apply_migration()
