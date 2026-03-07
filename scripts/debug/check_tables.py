
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    print("Supabase credentials not found")
    exit(1)

supabase: Client = create_client(url, key)

tables = ["tracking_links", "conversions", "invitations", "subscriptions", "subscription_plans", "products", "sales", "campaigns"]

for table in tables:
    try:
        response = supabase.table(table).select("id").limit(1).execute()
        print(f"✅ Table '{table}' exists.")
    except Exception as e:
        print(f"❌ Table '{table}' error: {e}")
