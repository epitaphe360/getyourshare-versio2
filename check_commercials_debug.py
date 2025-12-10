import os
from supabase import create_client, Client
import json

url = "https://iamezkmapbhlhhvvsits.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

supabase: Client = create_client(url, key)

def check_commercials_data():
    print("Checking commercials data...")
    
    # Get commercials
    response = supabase.table("users").select("*").eq("role", "commercial").limit(5).execute()
    commercials = response.data
    
    print(f"Found {len(commercials)} commercials.")
    
    for comm in commercials:
        print(f"\nCommercial: {comm.get('email')} (ID: {comm.get('id')})")
        
        # Check profile
        # Note: profile might be a JSONB column in users table or a separate table
        # In the frontend code: commercial.profile?.total_sales
        # In the backend code: it just returns users table rows.
        # Let's see if 'profile' column exists in users table and what's in it.
        
        # Check leads
        leads_count = supabase.table("leads").select("id", count="exact").eq("commercial_id", comm["id"]).execute().count
        print(f"  Leads count: {leads_count}")
        
        # Check sales/commissions (if any table links them)
        # Usually commissions table has user_id or commercial_id
        try:
            commissions_count = supabase.table("commissions").select("id", count="exact").eq("user_id", comm["id"]).execute().count
            print(f"  Commissions count (user_id): {commissions_count}")
        except Exception as e:
            print(f"  Error checking commissions: {e}")

if __name__ == "__main__":
    check_commercials_data()
