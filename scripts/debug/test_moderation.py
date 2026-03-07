
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env vars
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Client avec service_role (admin - pour backend)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def test_moderation_queries():
    print("Testing products query...")
    try:
        products_result = supabase.table("products")\
            .select("*, users(full_name, email)")\
            .eq("status", "pending")\
            .limit(1)\
            .execute()
        print("Products query successful")
    except Exception as e:
        print(f"Products query failed: {e}")

    print("\nTesting reviews query...")
    try:
        reviews_result = supabase.table("reviews")\
            .select("*, users(full_name, email)")\
            .eq("status", "pending")\
            .limit(1)\
            .execute()
        print("Reviews query successful")
    except Exception as e:
        print(f"Reviews query failed: {e}")

if __name__ == "__main__":
    test_moderation_queries()
