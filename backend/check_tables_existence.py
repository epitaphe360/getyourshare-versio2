
from supabase_client import supabase
import sys

def check_tables():
    tables = ['affiliate_links', 'trackable_links', 'affiliation_requests']
    for table in tables:
        try:
            # Try to select 1 row to see if table exists
            supabase.table(table).select("id").limit(1).execute()
            print(f"Table '{table}' exists.")
        except Exception as e:
            print(f"Table '{table}' does NOT exist or error: {e}")

if __name__ == "__main__":
    check_tables()
