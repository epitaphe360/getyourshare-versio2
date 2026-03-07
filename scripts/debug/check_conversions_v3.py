
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase_client import supabase

try:
    print("Fetching conversions...")
    response = supabase.table('conversions').select('*').execute()
    conversions = response.data
    
    print(f"Found {len(conversions)} conversions.")
    
    if len(conversions) > 0:
        print("Keys in first conversion:", conversions[0].keys())

    for i, conv in enumerate(conversions[:10]): # Limit to 10 for brevity
        print(f"Conversion {i+1}:")
        print(f"  ID: {conv.get('id')}")
        print(f"  Campaign ID: {conv.get('campaign_id')}")
        print(f"  Influencer ID: {conv.get('influencer_id')}")
        print(f"  Sale Amount: {conv.get('sale_amount')}")
        print("-" * 20)

except Exception as e:
    print(f"Error: {e}")
