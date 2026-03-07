import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
if not url or not key:
    # Try root .env
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def test_rpc():
    print("Testing exec_sql RPC...")
    sql = "SELECT 1"
    try:
        # Try with 'sql' parameter
        response = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print(f"Success with 'sql' parameter: {response.data}")
        return True
    except Exception as e:
        print(f"Failed with 'sql' parameter: {e}")
        
    try:
        # Try with 'query' parameter
        response = supabase.rpc('exec_sql', {'query': sql}).execute()
        print(f"Success with 'query' parameter: {response.data}")
        return True
    except Exception as e:
        print(f"Failed with 'query' parameter: {e}")
        
    return False

if __name__ == "__main__":
    test_rpc()
