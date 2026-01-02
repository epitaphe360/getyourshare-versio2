import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def list_users():
    print("Listing users...")
    res = supabase.table("users").select("email, role").execute()
    for user in res.data:
        print(f"- {user['email']} ({user['role']})")

if __name__ == "__main__":
    list_users()
