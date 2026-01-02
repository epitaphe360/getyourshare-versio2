
import os
import bcrypt
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("AuditAccounts")

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    logger.error("Supabase credentials not found in environment variables.")
    exit(1)

supabase: Client = create_client(url, key)

# Target accounts for the audit
ACCOUNTS = {
    "admin": {
        "email": "admin@getyourshare.com",
        "role": "admin",
        "password": "Test1234!"
    },
    "merchant": {
        "email": "merchant1@fashionstore.com",
        "role": "merchant",
        "password": "Test1234!",
        "profile_table": "merchants",
        "profile_data": {
            "company_name": "Fashion Store",
            "subscription_plan": "pro",
            "category": "Mode et lifestyle",
            "description": "Test Merchant for Audit"
        }
    },
    "influencer": {
        "email": "influencer1@fashion.com",
        "role": "influencer",
        "password": "Test1234!",
        "profile_table": "influencers",
        "profile_data": {
            "username": "influencer1",
            "full_name": "Test Influencer",
            "subscription_plan": "pro",
            "category": "Lifestyle",
            "audience_size": 50000,
            "influencer_type": "micro"
        }
    },
    "commercial": {
        "email": "commercial1@shareyoursales.ma",
        "role": "commercial",
        "password": "Test1234!",
        "profile_table": "sales_representatives",
        "profile_data": {
            "first_name": "Commercial",
            "last_name": "One",
            "phone": "+212600000000",
            "commission_rate": 5.0,
            "is_active": True
        }
    }
}

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def ensure_user(account_key, account_data):
    email = account_data["email"]
    role = account_data["role"]
    password = account_data["password"]
    
    logger.info(f"Processing {account_key} ({email})...")
    
    # 1. Check/Create User
    user_id = None
    existing = supabase.table("users").select("id").eq("email", email).execute()
    
    password_hash = hash_password(password)
    
    if existing.data:
        user_id = existing.data[0]["id"]
        logger.info(f"   User exists (ID: {user_id}). Updating password...")
        supabase.table("users").update({
            "password_hash": password_hash,
            "role": role # Ensure role is correct
        }).eq("id", user_id).execute()
    else:
        logger.info(f"   Creating user...")
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "is_verified": True,
            "two_fa_enabled": False
        }
        result = supabase.table("users").insert(user_data).execute()
        if result.data:
            user_id = result.data[0]["id"]
            logger.info(f"   User created (ID: {user_id})")
        else:
            logger.error(f"   Failed to create user {email}")
            return

    # 2. Check/Create Profile
    if "profile_table" in account_data:
        table = account_data["profile_table"]
        profile_data = account_data["profile_data"]
        
        logger.info(f"   Checking profile in {table}...")
        
        # Check if profile exists
        existing_profile = supabase.table(table).select("id").eq("user_id", user_id).execute()
        
        if not existing_profile.data:
            logger.info(f"   Creating profile...")
            profile_data["user_id"] = user_id
            # Add email to profile if it's sales_representatives (as seen in commercial_endpoints.py)
            if table == "sales_representatives":
                profile_data["email"] = email
                
            try:
                supabase.table(table).insert(profile_data).execute()
                logger.info(f"   Profile created.")
            except Exception as e:
                logger.error(f"   Failed to create profile: {e}")
        else:
            logger.info(f"   Profile exists.")

def main():
    logger.info("=== ENSURING AUDIT ACCOUNTS ===")
    for key, data in ACCOUNTS.items():
        try:
            ensure_user(key, data)
        except Exception as e:
            logger.error(f"Error processing {key}: {e}")
    logger.info("=== DONE ===")

if __name__ == "__main__":
    main()
