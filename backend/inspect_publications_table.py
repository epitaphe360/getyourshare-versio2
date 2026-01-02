from supabase_client import supabase
import json

def inspect_table():
    try:
        # Try to fetch one row to see keys
        response = supabase.table('social_media_publications').select('*').limit(1).execute()
        if response.data:
            print("Columns in social_media_publications:", list(response.data[0].keys()))
        else:
            print("Table social_media_publications is empty, cannot infer columns from data.")
            
            # If empty, we can try to insert a dummy row and see what fails, or just assume we need to check schema differently.
            # But usually we can't check schema directly via client without data or rpc.
            # Let's try to see if we can get an error message that lists columns by selecting a non-existent column?
            # No, that's hacky.
            
    except Exception as e:
        print(f"Error inspecting table: {e}")

if __name__ == "__main__":
    inspect_table()
