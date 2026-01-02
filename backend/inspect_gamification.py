import os
from supabase import create_client, Client

SUPABASE_URL = "https://iamezkmapbhlhhvvsits.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

def inspect():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    print("Attempting to select 'badges_earned' from user_gamification...")
    try:
        response = supabase.table("user_gamification").select("badges_earned").limit(1).execute()
        print("Success! Column exists.")
        print(response)
    except Exception as e:
        print(f"Error selecting badges_earned: {e}")

    print("\nAttempting to select 'current_streak' from user_gamification...")
    try:
        response = supabase.table("user_gamification").select("current_streak").limit(1).execute()
        print("Success! Column exists.")
    except Exception as e:
        print(f"Error selecting current_streak: {e}")

if __name__ == "__main__":
    inspect()
