
from backend.supabase_client import supabase

def inspect_columns():
    tables = ["users", "services", "campaigns", "badges", "categories"]
    
    for table in tables:
        try:
            print(f"--- {table} ---")
            # Fetch one row to see keys
            res = supabase.table(table).select("*").limit(1).execute()
            if res.data:
                print(res.data[0].keys())
            else:
                print("No data found, cannot infer columns easily via select *")
        except Exception as e:
            print(f"Error inspecting {table}: {e}")

if __name__ == "__main__":
    inspect_columns()
