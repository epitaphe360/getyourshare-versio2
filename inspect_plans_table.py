
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load from backend/.env
load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

try:
    response = supabase.from_("subscription_plans").select("*").limit(1).execute()
    if response.data:
        print("Columns found:", response.data[0].keys())
        print("Sample data:", response.data[0])
    else:
        print("Table is empty")
except Exception as e:
    print(f"Error: {e}")
