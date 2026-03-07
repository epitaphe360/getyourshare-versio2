import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env vars
load_dotenv(os.path.join(os.getcwd(), '.env.production'))
load_dotenv(os.path.join(os.getcwd(), '.env'))

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
    sys.exit(1)

supabase: Client = create_client(url, key)

def get_columns(table_name):
    try:
        # Try to select one row to see keys
        response = supabase.table(table_name).select("*").limit(1).execute()
        if response.data:
            return list(response.data[0].keys())
        else:
            return "Table empty or no data"
    except Exception as e:
        return f"Error: {e}"

print("affiliate_links columns:", get_columns("affiliate_links"))
print("tracking_links columns:", get_columns("tracking_links"))
print("affiliation_requests columns:", get_columns("affiliation_requests"))
