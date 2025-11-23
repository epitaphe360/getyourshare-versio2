import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in environment variables.")
    exit(1)

supabase: Client = create_client(url, key)

def check_merchants():
    print("--- Checking Users (Role: Merchant) ---")
    users_result = supabase.from_("users").select("*").eq("role", "merchant").execute()
    users = users_result.data if users_result.data else []
    print(f"Found {len(users)} merchants in users table.")
    
    for i, u in enumerate(users[:5]):
        print(f"User {i}: ID={u.get('id')}, Company={u.get('company_name')}, Username={u.get('username')}")

    print("\n--- Checking Merchants Table ---")
    try:
        merchants_result = supabase.from_("merchants").select("*").execute()
        merchants = merchants_result.data if merchants_result.data else []
        print(f"Found {len(merchants)} entries in merchants table.")
        
        if merchants:
            print("First merchant columns:", merchants[0].keys())
            print("First merchant data:", merchants[0])
            
    except Exception as e:
        print(f"Error accessing merchants table: {e}")

if __name__ == "__main__":
    check_merchants()
