import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(".env.railway")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found.")
    exit(1)

supabase: Client = create_client(url, key)

def check_affiliates():
    print("Checking for affiliate data...")

    try:
        # 1. Check for users with role 'influencer'
        print("\n--- Affiliates (Users with role='influencer') ---")
        response = supabase.table("users").select("*").eq("role", "influencer").execute()
        affiliates = response.data
        print(f"Total Affiliates found: {len(affiliates)}")
        
        if affiliates:
            for aff in affiliates:
                print(f"- ID: {aff.get('id')}")
                print(f"  Email: {aff.get('email')}")
                print(f"  Name: {aff.get('first_name')} {aff.get('last_name')}")
                print(f"  Status: {aff.get('status')}")
                print(f"  Clicks: {aff.get('clicks')}")
                print(f"  Conversions: {aff.get('conversions')}")
                print(f"  Total Earned: {aff.get('total_earned')}")
                print("---")
        else:
            print("No affiliates found.")

        # 2. Check for tracking links (activity)
        print("\n--- Tracking Links ---")
        response = supabase.table("tracking_links").select("*").execute()
        links = response.data
        print(f"Total Tracking Links found: {len(links)}")
        if links:
             print(f"Sample link: {links[0]}")

        # 3. Check for conversions/sales linked to affiliates
        # Note: Table name might be 'conversions' or 'sales' depending on schema, checking 'conversions' first based on previous context
        print("\n--- Conversions ---")
        try:
            response = supabase.table("conversions").select("*").execute()
            conversions = response.data
            print(f"Total Conversions found: {len(conversions)}")
        except Exception as e:
            print(f"Could not query 'conversions' table: {e}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_affiliates()
