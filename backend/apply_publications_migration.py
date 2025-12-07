import os
import sys
from supabase_client import supabase

def apply_migration():
    # Path relative to backend/
    migration_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'migrations_organized', '016_add_service_id_to_publications.sql')
    
    print(f"Reading migration file: {migration_path}")
    
    try:
        with open(migration_path, 'r') as f:
            sql_content = f.read()
            
        print("Attempting to apply migration via RPC 'exec_sql'...")
        
        # Try to execute via RPC
        try:
            response = supabase.rpc('exec_sql', {'query': sql_content}).execute()
            print("✅ Migration applied successfully via RPC!")
            print(response)
        except Exception as e:
            print(f"⚠️  Could not apply migration automatically via RPC: {e}")
            print("\n" + "="*50)
            print("MANUAL ACTION REQUIRED")
            print("="*50)
            print("Please run the following SQL in your Supabase SQL Editor:")
            print("-" * 20)
            print(sql_content)
            print("-" * 20)
            
    except Exception as e:
        print(f"❌ Error reading migration file: {e}")
        return

if __name__ == "__main__":
    apply_migration()
