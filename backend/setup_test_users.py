import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def update_user_password(email: str, new_password: str):
    print(f"Updating password for {email}...")
    
    # Check if user exists
    user_res = supabase.table("users").select("id").eq("email", email).execute()
    
    if not user_res.data:
        print(f"User {email} not found!")
        return
    
    user_id = user_res.data[0]["id"]
    hashed = hash_password(new_password)
    
    # Update password
    update_res = supabase.table("users").update({"password_hash": hashed}).eq("id", user_id).execute()
    
    if update_res.data:
        print(f"✅ Password updated for {email}")
    else:
        print(f"❌ Failed to update password for {email}")

if __name__ == "__main__":
    test_password = "Test1234!"
    
    users_to_update = [
        "admin@getyourshare.com",
        "merchant1@fashionstore.com",
        "influencer1@fashion.com",
        "commercial1@shareyoursales.ma"
    ]
    
    print(f"Setting password to '{test_password}' for test users...")
    
    for email in users_to_update:
        update_user_password(email, test_password)
        
    print("\nDone! You can now run the full system test.")
