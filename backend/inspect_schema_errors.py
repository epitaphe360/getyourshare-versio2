
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

def inspect_table(table_name):
    print(f"--- Inspecting {table_name} ---")
    try:
        # Try to select one row to see columns in the error or result
        response = supabase.table(table_name).select("*").limit(1).execute()
        if response.data:
            print(f"Columns: {list(response.data[0].keys())}")
        else:
            print("Table is empty, cannot infer columns easily via select. Trying to insert dummy to provoke error or check metadata if possible.")
            # In supabase-py, we don't have direct schema inspection easily without SQL.
            # But we can try to call a stored procedure if we had one, or just rely on the previous error messages.
            # Actually, let's try to run a raw SQL query if possible, but the client doesn't support raw SQL directly unless enabled.
            # We will assume the previous error messages are correct.
            pass
    except Exception as e:
        print(f"Error inspecting {table_name}: {e}")

inspect_table("commissions")
inspect_table("social_media_stats")
inspect_table("leads")
