import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in environment variables.")
    exit(1)

supabase: Client = create_client(url, key)

def check_services():
    print("--- Checking Services Table ---")
    try:
        services_result = supabase.from_("services").select("*").execute()
        services = services_result.data if services_result.data else []
        print(f"Found {len(services)} services.")
        
        if services:
            print("First service columns:", services[0].keys())
            print("First service data:", json.dumps(services[0], indent=2, default=str))
            
            # Check specific fields
            print("\nChecking specific fields for all services:")
            for s in services:
                print(f"ID: {s.get('id')}")
                print(f"  Name: {s.get('name')}")
                print(f"  Price/Lead: {s.get('price_per_lead')}")
                print(f"  Capacity: {s.get('capacity_per_month')}")
                print(f"  Total Leads: {s.get('total_leads')}")
                
    except Exception as e:
        print(f"Error accessing services table: {e}")

if __name__ == "__main__":
    check_services()
