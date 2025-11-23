import os
import sys
import uuid
import bcrypt
import random
from dotenv import load_dotenv

# Add the current directory to sys.path to allow imports from local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

load_dotenv()

def seed_influencers():
    print("🌱 Seeding influencers via Supabase Client...")

    # List of dummy influencers to insert
    influencers = [
        {
            "email": "sarah.mode@example.com",
            "first_name": "Sarah",
            "last_name": "Mode",
            "niche": "Fashion",
            "instagram_username": "sarah.style",
            "followers_count": 45000,
            "engagement_rate": 5.2,
            "bio": "Fashion & Lifestyle blogger based in Casablanca.",
            "profile_picture_url": "https://randomuser.me/api/portraits/women/44.jpg"
        },
        {
            "email": "karim.tech@example.com",
            "first_name": "Karim",
            "last_name": "Tech",
            "niche": "Technology",
            "instagram_username": "karim.tech",
            "followers_count": 120000,
            "engagement_rate": 4.8,
            "bio": "Tech reviewer and gadget lover.",
            "profile_picture_url": "https://randomuser.me/api/portraits/men/32.jpg"
        },
        {
            "email": "amina.glam@example.com",
            "first_name": "Amina",
            "last_name": "Glam",
            "niche": "Beauty",
            "instagram_username": "amina.glam",
            "followers_count": 85000,
            "engagement_rate": 6.5,
            "bio": "Makeup artist and beauty consultant.",
            "profile_picture_url": "https://randomuser.me/api/portraits/women/68.jpg"
        },
        {
            "email": "youssef.fit@example.com",
            "first_name": "Youssef",
            "last_name": "Fit",
            "niche": "Fitness",
            "instagram_username": "youssef.fit",
            "followers_count": 60000,
            "engagement_rate": 7.1,
            "bio": "Certified personal trainer. Health is wealth.",
            "profile_picture_url": "https://randomuser.me/api/portraits/men/45.jpg"
        },
        {
            "email": "sofia.travel@example.com",
            "first_name": "Sofia",
            "last_name": "Travel",
            "niche": "Travel",
            "instagram_username": "sofia.wanders",
            "followers_count": 95000,
            "engagement_rate": 5.9,
            "bio": "Exploring the world one city at a time.",
            "profile_picture_url": "https://randomuser.me/api/portraits/women/22.jpg"
        }
    ]

    for inf in influencers:
        user_id = None
        
        # Check if user exists
        try:
            existing = supabase.table("users").select("id").eq("email", inf["email"]).execute()
            if existing.data:
                print(f"User {inf['email']} already exists.")
                user_id = existing.data[0]['id']
        except Exception as e:
            print(f"Error checking user {inf['email']}: {e}")
            continue

        if not user_id:
            user_id = str(uuid.uuid4())
            # Use bcrypt for password hashing
            password_hash = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            # 1. Insert into users table
            user_data = {
                "id": user_id,
                "email": inf["email"],
                "password_hash": password_hash,
                "first_name": inf["first_name"],
                "last_name": inf["last_name"],
                "role": "influencer",
                "is_active": True,
                "username": inf["instagram_username"] # Keeping username as it is common in users table
            }

            try:
                print(f"Creating user {inf['email']}...")
                supabase.table("users").insert(user_data).execute()
            except Exception as e:
                print(f"❌ Failed to create user {inf['email']}: {e}")
                continue
        
        # 2. Insert into influencer_profiles table
        # Check if influencer profile exists
        try:
            existing_profile = supabase.table("influencer_profiles").select("id").eq("user_id", user_id).execute()
            if existing_profile.data:
                print(f"Influencer profile for {inf['email']} already exists.")
                continue
        except Exception as e:
            print(f"Error checking influencer profile: {e}")
            # Continue to try insert
        
        # Match schema from influencers_directory_endpoints.py
        influencer_data = {
            "user_id": user_id,
            "display_name": f"{inf['first_name']} {inf['last_name']}",
            "headline": inf["bio"][:50] if inf["bio"] else "Influencer",
            "bio": inf["bio"],
            "niches": [inf["niche"]], # Array
            "instagram_handle": inf["instagram_username"],
            "instagram_followers": inf["followers_count"],
            "instagram_engagement_rate": inf["engagement_rate"],
            "is_public": True,
            "is_available": True
        }
        
        try:
            supabase.table("influencer_profiles").insert(influencer_data).execute()
            print(f"✅ Created influencer profile for: {inf['first_name']} {inf['last_name']}")
        except Exception as e:
            print(f"⚠️ Could not insert into influencer_profiles: {e}")

    print("Seeding complete.")

if __name__ == "__main__":
    seed_influencers()
