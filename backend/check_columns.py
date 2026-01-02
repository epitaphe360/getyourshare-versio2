from supabase_client import supabase
import json

try:
    # Try to select one row to see columns
    res = supabase.table("company_deposits").select("*").limit(1).execute()
    if res.data:
        print("Columns:", list(res.data[0].keys()))
    else:
        # If empty, try to insert a dummy row with minimal columns to see error or success
        # But we don't know minimal columns.
        # We can try to get schema via rpc if available, but we know it's not.
        print("Table is empty, cannot infer columns from data.")
        
        # Try to insert with just ID (if auto-generated) or empty dict? No.
        # Let's try to select a non-existent column and see the error hint?
        try:
            supabase.table("company_deposits").select("non_existent_column").limit(1).execute()
        except Exception as e:
            print(f"Error selecting non-existent: {e}")

except Exception as e:
    print(f"Error: {e}")
