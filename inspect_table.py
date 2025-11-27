import os
import sys
from dotenv import load_dotenv
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

load_dotenv()

from supabase_client import supabase

def inspect_table(table_name):
    print(f"--- Inspecting {table_name} ---")
    try:
        response = supabase.table(table_name).select("*").limit(1).execute()
        if response.data:
            print(f"Columns: {list(response.data[0].keys())}")
            print(f"Sample: {json.dumps(response.data[0], indent=2)}")
        else:
            print("Table is empty.")
    except Exception as e:
        print(f"Error: {e}")

inspect_table("products")
inspect_table("sales_representatives")
inspect_table("trackable_links")
