from supabase_client import supabase

def check_exec_sql():
    try:
        response = supabase.rpc('exec_sql', {'query': 'SELECT 1'}).execute()
        print("exec_sql exists and works:", response)
    except Exception as e:
        print(f"exec_sql failed: {e}")

if __name__ == "__main__":
    check_exec_sql()
