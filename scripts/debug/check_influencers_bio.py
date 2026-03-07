#!/usr/bin/env python3
"""Check if influencers table has bio column"""

from backend.supabase_client import supabase
import sys

try:
    # Try to query the influencers table and check columns
    result = supabase.table("influencers").select("*").limit(1).execute()
    
    if result.data:
        print("✅ Influencers table columns:")
        for key in result.data[0].keys():
            print(f"   - {key}")
        
        if 'bio' in result.data[0]:
            print(f"\n✅ Bio column exists: {result.data[0]['bio']}")
        else:
            print("\n❌ Bio column does NOT exist in influencers table")
    else:
        print("⚠️  No influencer records found")
        
        # Try to check the schema directly
        print("\nAttempting to query with bio column:")
        result2 = supabase.table("influencers").select("id, user_id, bio").limit(1).execute()
        print(f"Result: {result2}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
