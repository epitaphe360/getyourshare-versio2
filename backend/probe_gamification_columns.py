import os
from supabase import create_client, Client

SUPABASE_URL = "https://iamezkmapbhlhhvvsits.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

def probe_schema():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    print("Probing information_schema.columns...")
    try:
        # Note: PostgREST might not expose information_schema directly via the table interface
        # unless it's been explicitly exposed. But it's worth a try.
        # Often it's not exposed.
        
        # Alternative: Try to select specific columns one by one.
        potential_columns = [
            "id", "user_id", "user_type", "total_points", "current_level", 
            "level_points", "badges_earned", "missions_completed", 
            "streak_days", "current_streak", "last_activity_date", 
            "leaderboard_position", "leaderboard_region", 
            "created_at", "updated_at", "level", "experience", "achievements", "last_updated"
        ]
        
        existing_columns = []
        
        for col in potential_columns:
            try:
                supabase.table("user_gamification").select(col).limit(1).execute()
                existing_columns.append(col)
                print(f"Column '{col}' EXISTS.")
            except Exception as e:
                # print(f"Column '{col}' does not exist (or other error).")
                pass
                
        print("\nExisting columns:", existing_columns)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_schema()
