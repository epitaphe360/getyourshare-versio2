import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Try loading .env.railway if variables are missing
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(".env.railway")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    # Fallback to hardcoded creds from supabase_creds.py
    try:
        import supabase_creds
        url = supabase_creds.SUPABASE_URL
        key = supabase_creds.SUPABASE_KEY
    except ImportError:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found and supabase_creds.py missing.")
        exit(1)

supabase: Client = create_client(url, key)

try:
    # Get a single row to inspect keys
    response = supabase.table("subscription_plans").select("*").limit(1).execute()
    if response.data:
        print("Columns in subscription_plans:")
        print(response.data[0].keys())
    else:
        print("No data in subscription_plans")
except Exception as e:
    print(f"Error: {e}")
