
from supabase import create_client
import json

SUPABASE_URL = "https://iamezkmapbhlhhvvsits.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Fetching conversions...")
try:
    response = supabase.table('conversions').select('*').execute()
    conversions = response.data
    print(f"Found {len(conversions)} conversions.")
    
    if len(conversions) > 0:
        print("Sample conversion keys:", conversions[0].keys())
        
        print("\nChecking first 5 conversions for campaign_id and influencer_id:")
        for i, conv in enumerate(conversions[:5]):
            print(f"ID: {conv.get('id')}")
            print(f"  Campaign ID: {conv.get('campaign_id')}")
            print(f"  Influencer ID: {conv.get('influencer_id')}")
            print(f"  Sale Amount: {conv.get('sale_amount')}")
            print("-" * 20)
            
            # Check if these IDs exist in their respective tables
            if conv.get('product_id'):
                prod = supabase.table('products').select('name').eq('id', conv['product_id']).execute()
                print(f"  -> Product Lookup: {prod.data}")
            else:
                print("  -> Product ID is None/Empty")

            if conv.get('influencer_id'):
                inf = supabase.table('users').select('email').eq('id', conv['influencer_id']).execute()
                print(f"  -> Influencer Lookup: {inf.data}")
            else:
                print("  -> Influencer ID is None/Empty")
            print("=" * 30)

except Exception as e:
    print(f"Error: {e}")
