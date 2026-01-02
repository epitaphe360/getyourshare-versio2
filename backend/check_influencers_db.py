import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

load_dotenv()

def check_users():
    print("Checking users table...")
    try:
        response = supabase.table("users").select("*").eq("role", "influencer").execute()
        users = response.data
        print(f"Found {len(users)} influencers in users table.")
        for u in users:
            print(f"- {u.get('email')} (ID: {u.get('id')})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
