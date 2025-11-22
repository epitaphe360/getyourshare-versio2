import os
from supabase import create_client, Client
from datetime import datetime

SUPABASE_URL = "https://iamezkmapbhlhhvvsits.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

def debug_insert():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    user_id = "11111111-1111-1111-1111-111111111111"
    
    print(f"Attempting to insert gamification profile for {user_id}...")
    
    new_profile = {
        'user_id': user_id,
        'total_points': 0,
        'level': 1,
        'experience': 0,
        'achievements': [],
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }
    
    try:
        response = supabase.table("user_gamification").insert(new_profile).execute()
        print("Insert SUCCESS!")
        print(response.data)
    except Exception as e:
        print(f"Insert FAILED: {e}")

if __name__ == "__main__":
    debug_insert()
