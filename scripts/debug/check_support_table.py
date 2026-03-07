
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def check_tables():
    try:
        # Try to select from support_tickets
        print("Checking support_tickets table...")
        supabase.table("support_tickets").select("id").limit(1).execute()
        print("✅ support_tickets table exists")
    except Exception as e:
        print(f"❌ support_tickets table check failed: {e}")

if __name__ == "__main__":
    check_tables()
