import os
from supabase import create_client, Client

SUPABASE_URL = "https://iamezkmapbhlhhvvsits.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

def inspect_users():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Try to get table info via rpc if possible, or just infer.
    # We can try to insert a user with a random ID and see if it works.
    # If it works, it's likely a table.
    
    import uuid
    random_id = str(uuid.uuid4())
    
    print(f"Attempting to insert random user {random_id}...")
    try:
        user_data = {
            "id": random_id,
            "email": f"test_{random_id}@example.com",
            "role": "user"
        }
        response = supabase.table("users").insert(user_data).execute()
        print("Insert into users SUCCESS. It is likely a table.")
        
        # Clean up
        supabase.table("users").delete().eq("id", random_id).execute()
        
    except Exception as e:
        print(f"Insert into users FAILED: {e}")

if __name__ == "__main__":
    inspect_users()
