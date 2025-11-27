import os
import sys
from dotenv import load_dotenv
import bcrypt

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

load_dotenv()

try:
    from db_helpers import get_user_by_email, create_user, update_user, hash_password
    from supabase_client import supabase
except ImportError:
    print("Error: Could not import db_helpers. Make sure you are running this from the backend directory.")
    sys.exit(1)

users_to_create = [
    {
        "email": "admin@getyourshare.com",
        "password": "Test123!",
        "role": "admin",
        "full_name": "Admin User",
        "subscription_plan": "Enterprise"
    },
    {
        "email": "hassan.oudrhiri@getyourshare.com",
        "password": "Test123!",
        "role": "influencer",
        "full_name": "Hassan Oudrhiri",
        "subscription_plan": "Starter",
        "niche": ["Food", "Cuisine"],
        "followers_count": 67000
    },
    {
        "email": "sarah.benali@getyourshare.com",
        "password": "Test123!",
        "role": "influencer",
        "full_name": "Sarah Benali",
        "subscription_plan": "Pro",
        "niche": ["Lifestyle"],
        "followers_count": 125000
    },
    {
        "email": "karim.benjelloun@getyourshare.com",
        "password": "Test123!",
        "role": "influencer",
        "full_name": "Karim Benjelloun",
        "subscription_plan": "Enterprise",
        "niche": ["Tech", "Gaming"],
        "followers_count": 285000,
        "is_verified": True
    },
    {
        "email": "boutique.maroc@getyourshare.com",
        "password": "Test123!",
        "role": "merchant",
        "full_name": "Boutique Maroc",
        "company_name": "Boutique Maroc",
        "subscription_plan": "Starter",
        "business_type": "Artisanat"
    },
    {
        "email": "luxury.crafts@getyourshare.com",
        "password": "Test123!",
        "role": "merchant",
        "full_name": "Luxury Crafts",
        "company_name": "Luxury Crafts",
        "subscription_plan": "Pro",
        "business_type": "Artisanat Premium"
    },
    {
        "email": "electromaroc@getyourshare.com",
        "password": "Test123!",
        "role": "merchant",
        "full_name": "ElectroMaroc",
        "company_name": "ElectroMaroc",
        "subscription_plan": "Enterprise",
        "business_type": "High-Tech",
        "is_verified": True
    },
    {
        "email": "sofia.chakir@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "full_name": "Sofia Chakir",
        "subscription_plan": "Enterprise"
    }
]

print("Creating/Updating quick launch users...")
print("-" * 50)

for user_data in users_to_create:
    email = user_data["email"]
    password = user_data["password"]
    role = user_data["role"]
    
    existing_user = get_user_by_email(email)
    
    if existing_user:
        print(f"🔄 Updating existing user: {email}")
        # Update password and other fields
        new_hash = hash_password(password)
        updates = {
            "password_hash": new_hash,
            "role": role,
            "full_name": user_data.get("full_name"),
            "subscription_plan": user_data.get("subscription_plan"),
            "is_active": True
        }
        if "company_name" in user_data:
            updates["company_name"] = user_data["company_name"]
        if "is_verified" in user_data:
            updates["is_verified"] = user_data["is_verified"]
            
        update_user(existing_user["id"], updates)
        
        # Update specific tables based on role if needed (simplified for now)
        # Ideally we should update influencers/merchants tables too
        
    else:
        print(f"✨ Creating new user: {email}")
        # Create user
        # create_user function handles hashing
        new_user = create_user(
            email=email,
            password=password,
            role=role,
            phone=None,
            is_active=True,
            email_verified=True
        )
        
        if new_user:
            # Update additional fields that create_user might not handle directly
            updates = {
                "full_name": user_data.get("full_name"),
                "subscription_plan": user_data.get("subscription_plan")
            }
            if "company_name" in user_data:
                updates["company_name"] = user_data["company_name"]
            if "is_verified" in user_data:
                updates["is_verified"] = user_data["is_verified"]
                
            update_user(new_user["id"], updates)
            
            # Create profile entries (simplified)
            if role == "influencer":
                supabase.table("influencers").insert({
                    "user_id": new_user["id"],
                    "niche": user_data.get("niche", []),
                    "followers_count": user_data.get("followers_count", 0),
                    "bio": f"Bio for {user_data.get('full_name')}"
                }).execute()
            elif role == "merchant":
                supabase.table("merchants").insert({
                    "user_id": new_user["id"],
                    "company_name": user_data.get("company_name"),
                    "business_type": user_data.get("business_type"),
                    "description": f"Description for {user_data.get('company_name')}"
                }).execute()
            elif role == "commercial":
                supabase.table("sales_representatives").insert({
                    "user_id": new_user["id"],
                    "territory": "Maroc",
                    "commission_rate": 5.0
                }).execute()

print("-" * 50)
print("Done.")
