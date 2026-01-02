
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

def apply_sql(filename):
    print(f"Applying {filename}...")
    with open(filename, 'r') as f:
        sql = f.read()
    
    # Split by statement if needed, but supabase-py doesn't support raw SQL easily.
    # We'll use a workaround or just assume the user runs it.
    # Actually, I can use the `rpc` call if I had a `exec_sql` function, but I don't.
    # I will print instructions for the user or try to use a python script to alter table if possible.
    # But wait, I can use the `postgres` connection if I had the connection string.
    # Since I don't have direct SQL access via client, I will rely on the user running the SQL or use a python migration if possible.
    # However, for this environment, I'll try to use the `rpc` if available or just print the SQL.
    pass

# Since I cannot execute raw SQL via the supabase client without a specific RPC, 
# I will try to use the `run_in_terminal` to execute it via a python script that uses `psycopg2` if available, 
# or just ask the user. 
# But wait, I can use the `run_in_terminal` to run a python script that uses `supabase-py` to insert a dummy row that triggers the column creation? No.

# I will assume the user (me) can run the SQL via a tool if I had one.
# Actually, I'll use the `run_in_terminal` to run a python script that connects to the DB if I have the connection string.
# I don't have the connection string in `.env` (only URL and Key).
# So I cannot run raw SQL easily.

# BUT! I can use the `rpc` method if there is a function `exec_sql` or similar.
# Let's check if there is one.
try:
    response = supabase.rpc('exec_sql', {'sql': 'SELECT 1'}).execute()
    print("exec_sql RPC exists!")
except Exception as e:
    print(f"exec_sql RPC does not exist: {e}")

