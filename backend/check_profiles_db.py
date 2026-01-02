import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

load_dotenv()

def check_profiles():
    print("Checking influencer_profiles table...")
    try:
        response = supabase.table("influencer_profiles").select("*").execute()
        profiles = response.data
        print(f"Found {len(profiles)} profiles.")
        for p in profiles:
            print(f"- {p.get('display_name')} (User ID: {p.get('user_id')})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_profiles()
