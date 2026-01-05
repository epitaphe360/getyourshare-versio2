import os
import sys
from supabase import create_client, Client

# Add backend directory to path to import config
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
    sys.exit(1)

supabase: Client = create_client(url, key)

try:
    # Try to select one row to see keys
    response = supabase.table("subscriptions").select("*").limit(1).execute()
    if response.data:
        print("Columns found in subscriptions table:")
        print(response.data[0].keys())
    else:
        print("Table is empty, cannot infer columns from data.")
        # Try to insert a dummy row to trigger an error that might list columns? 
        # Or just assume it's empty.
        
except Exception as e:
    print(f"Error querying subscriptions table: {e}")
