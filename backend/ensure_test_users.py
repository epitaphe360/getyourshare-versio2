print("Script starting...")
import os
import sys
import bcrypt
from supabase_client import get_supabase_client

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def ensure_test_users():
    supabase = get_supabase_client()
    print("Connected to Supabase")

    users_to_create = [
        {"email": "admin@getyourshare.com", "password": "Admin123!", "role": "admin", "full_name": "Admin User"},
        {"email": "influencer1@fashion.com", "password": "Test123!", "role": "influencer", "full_name": "Sarah El Fassi"},
        {"email": "influencer2@tech.com", "password": "Test123!", "role": "influencer", "full_name": "Pierre Tech"},
        {"email": "influencer3@lifestyle.com", "password": "Test123!", "role": "influencer", "full_name": "Laura Lifestyle"},
        {"email": "merchant1@fashionstore.com", "password": "Test123!", "role": "merchant", "full_name": "Fashion Store"},
        {"email": "merchant2@techgadgets.com", "password": "Test123!", "role": "merchant", "full_name": "Tech Gadgets"},
        {"email": "merchant3@beautyparis.com", "password": "Test123!", "role": "merchant", "full_name": "Beauty Paris"},
        {"email": "commercial1@getyourshare.com", "password": "Test123!", "role": "commercial", "full_name": "Lucas Commercial"}
    ]

    for user_data in users_to_create:
        email = user_data["email"]
        password = user_data["password"]
        role = user_data["role"]
        full_name = user_data["full_name"]

        print(f"Checking user {email}...")
        
        # Check if user exists
        res = supabase.table("users").select("*").eq("email", email).execute()
        
        if res.data:
            user = res.data[0]
            print(f"User {email} exists. Updating password...")
            # Update password
            hashed = hash_password(password)
            supabase.table("users").update({
                "password_hash": hashed,
                "role": role, # Ensure role is correct
                "is_active": True
            }).eq("id", user["id"]).execute()
            print(f"User {email} updated.")
            
            # Ensure profile exists
            ensure_profile(supabase, user["id"], role, full_name, email)
            
        else:
            print(f"User {email} does not exist. Creating...")
            hashed = hash_password(password)
            new_user = {
                "email": email,
                "password_hash": hashed,
                "role": role,
                "is_active": True,
                "two_fa_enabled": False,
                "email_verified": True
            }
            res = supabase.table("users").insert(new_user).execute()
            if res.data:
                user_id = res.data[0]["id"]
                print(f"User {email} created with ID {user_id}")
                ensure_profile(supabase, user_id, role, full_name, email)
            else:
                print(f"Failed to create user {email}")

def ensure_profile(supabase, user_id, role, full_name, email):
    try:
        if role == "merchant":
            # Check if merchant profile exists
            res = supabase.table("merchants").select("id").eq("user_id", user_id).execute()
            if not res.data:
                print(f"Creating merchant profile for {full_name}")
                supabase.table("merchants").insert({
                    "user_id": user_id,
                    "company_name": full_name,
                    "email": email,
                    "industry": "Retail",
                    "country": "MA"
                }).execute()
                
        elif role == "influencer":
            # Check if influencer profile exists
            # Note: Table name might be 'influencers' or 'influencer_profiles' depending on schema
            # Based on db_helpers.py, it seems to be 'influencers'
            res = supabase.table("influencers").select("id").eq("user_id", user_id).execute()
            if not res.data:
                print(f"Creating influencer profile for {full_name}")
                supabase.table("influencers").insert({
                    "user_id": user_id,
                    "username": email.split("@")[0],
                    "full_name": full_name,
                    "email": email
                }).execute()
                
        elif role == "commercial":
             # Check if sales_rep profile exists
            res = supabase.table("sales_representatives").select("id").eq("user_id", user_id).execute()
            if not res.data:
                print(f"Creating sales_rep profile for {full_name}")
                supabase.table("sales_representatives").insert({
                    "user_id": user_id,
                    "first_name": full_name.split(" ")[0],
                    "last_name": " ".join(full_name.split(" ")[1:]),
                    "email": email,
                    "is_active": True
                }).execute()

    except Exception as e:
        print(f"Error creating profile for {email}: {e}")

if __name__ == "__main__":
    ensure_test_users()
