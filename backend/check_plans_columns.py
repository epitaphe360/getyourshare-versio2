import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(url, key)

def check_columns():
    print("\nChecking 'tracking_links' table:")
    try:
        response = supabase.table('tracking_links').select('*').limit(1).execute()
        print("tracking_links exists")
    except Exception as e:
        print(f"tracking_links error: {e}")

    print("\nChecking 'trackable_links' table:")
    try:
        response = supabase.table('trackable_links').select('*').limit(1).execute()
        print("trackable_links exists")
    except Exception as e:
        print(f"trackable_links error: {e}")

if __name__ == "__main__":
    check_columns()
