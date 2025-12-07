import os
import sys
from supabase_client import supabase

def apply_migration():
    print("Applying migration: 016_add_service_id_to_publications.sql")
    
    try:
        with open('database/migrations_organized/016_add_service_id_to_publications.sql', 'r') as f:
            sql = f.read()
            
        # Split by statement if needed, but supabase-py execute might handle it or we use a helper
        # Usually we use a helper or run via psql.
        # But here I'll try to use the rpc 'exec_sql' if available or just print instructions.
        # Since I don't have direct SQL execution capability via supabase-py client usually (unless rpc is set up),
        # I will assume the user has a way to run it or I use the 'execute_sql_script.py' pattern if it exists.
        
        print("SQL Content:")
        print(sql)
        print("\nPlease run this SQL in your Supabase SQL Editor.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    apply_migration()
