import os
import sys
from supabase_client import supabase

def apply_optimization():
    print("🚀 Applying Database Optimization...")
    
    sql_file_path = os.path.join(os.path.dirname(__file__), "..", "OPTIMIZE_MERCHANTS_QUERY.sql")
    
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql = f.read()
            
        print(f"📖 Read SQL file: {sql_file_path}")
        
        # Try to execute via RPC if available (common in some setups)
        try:
            response = supabase.rpc('exec_sql', {'query': sql}).execute()
            print("✅ SQL executed successfully via RPC!")
        except Exception as e:
            print(f"⚠️ Could not execute SQL via RPC: {e}")
            print("ℹ️ This is normal if the 'exec_sql' function is not defined in your database.")
            print("👉 Please copy the content of 'OPTIMIZE_MERCHANTS_QUERY.sql' and run it in the Supabase SQL Editor.")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file {sql_file_path}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    apply_optimization()
