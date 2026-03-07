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
    response = supabase.table("subscription_plans").select("*").execute()
    plans = response.data
    print(f"Found {len(plans)} plans:")
    for plan in plans:
        print(f"- ID: {plan.get('id')}, Name: {plan.get('name')}, Price: {plan.get('price')}, MAD: {plan.get('price_mad')}")
except Exception as e:
    print(f"Error fetching plans: {e}")
