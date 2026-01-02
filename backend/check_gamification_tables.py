import os
from supabase import create_client, Client

# Load env vars manually since we are not using dotenv here
SUPABASE_URL = "https://iamezkmapbhlhhvvsits.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

def check_tables():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    user_id = "11111111-1111-1111-1111-111111111111"
    
    print(f"Checking if user {user_id} exists in 'users' table...")
    try:
        response = supabase.table("users").select("id").eq("id", user_id).execute()
        if response.data:
            print("User FOUND in 'users' table.")
        else:
            print("User NOT FOUND in 'users' table.")
            
            # Check if any users exist
            all_users = supabase.table("users").select("id").limit(5).execute()
            print(f"First 5 users in DB: {[u['id'] for u in all_users.data]}")
            
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == "__main__":
    check_tables()
