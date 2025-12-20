import sys
import os
import time

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)
os.chdir(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv("backend/.env")

SQL_FILE = 'ADD_MISSING_TABLES_AND_COLUMNS.sql'

def run_with_psycopg2():
    try:
        import psycopg2
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found in .env")
            return False
            
        print("🔌 Connecting to database via psycopg2...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"📖 Reading {SQL_FILE}...")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        print("🚀 Executing SQL script...")
        cur.execute(sql_content)
        
        print("✅ Script executed successfully via psycopg2!")
        conn.close()
        return True
    except ImportError:
        print("⚠️  psycopg2 not installed.")
        return False
    except Exception as e:
        print(f"❌ Error with psycopg2: {e}")
        return False

def run_with_supabase_rpc():
    try:
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        print("🔌 Connecting via Supabase Client (RPC)...")
        
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # Try to execute via exec_sql RPC
        print("🚀 Sending SQL to exec_sql function...")
        supabase.rpc('exec_sql', {'query': sql_content}).execute()
        
        print("✅ Script executed successfully via RPC!")
        return True
    except Exception as e:
        print(f"❌ Error with Supabase RPC: {e}")
        if "function public.exec_sql" in str(e) or "does not exist" in str(e):
            print("ℹ️  The 'exec_sql' function is missing in your database.")
        return False

if __name__ == "__main__":
    print(f"🔧 Attempting to execute {SQL_FILE}...\n")
    
    # Try psycopg2 first (most reliable)
    if run_with_psycopg2():
        sys.exit(0)
        
    print("\n🔄 Trying fallback method...\n")
    
    # Try Supabase RPC
    if run_with_supabase_rpc():
        sys.exit(0)
        
    print("\n❌ All execution methods failed.")
    print("📋 Please execute the script manually in Supabase SQL Editor:")
    print(f"   1. Copy content of {SQL_FILE}")
    print("   2. Go to Supabase Dashboard > SQL Editor")
    print("   3. Paste and Run")
    print("\n💡 To fix this locally, run: pip install psycopg2-binary")
