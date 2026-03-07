
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in environment variables.")
    exit(1)

supabase: Client = create_client(url, key)

def check_table(table_name):
    print(f"Checking table: {table_name}")
    try:
        response = supabase.table(table_name).select("*").limit(1).execute()
        print(f"  - Exists. Rows: {len(response.data)}")
        if len(response.data) > 0:
            print(f"  - Columns: {list(response.data[0].keys())}")
        else:
            print("  - Empty, cannot infer columns easily via select.")
    except Exception as e:
        print(f"  - Error: {e}")

tables = [
    "subscriptions", 
    "user_subscriptions", 
    "subscription_plans", 
    "commissions", 
    "invoices", 
    "product_reviews", 
    "conversations", 
    "messages",
    "products"
]

for t in tables:
    check_table(t)
