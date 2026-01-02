
from supabase_config import get_supabase_client
import asyncio

async def check_merchant_name():
    supabase = get_supabase_client()
    
    merchant_id = '22222222-2222-2222-2222-222222222225'
    try:
        user = supabase.table('users').select('company_name').eq('id', merchant_id).single().execute()
        print(f"Merchant {merchant_id}: {user.data}")
    except Exception as e:
        print(f"Merchant {merchant_id} not found or error: {e}")

    # Check IDs for the companies mentioned by user
    companies = ["Tech Gadgets Pro", "Fashion Store Paris", "Food Delights", "Beauty Paris", "Sport Shop Elite"]
    for company in companies:
        user = supabase.table('users').select('id').eq('company_name', company).execute()
        print(f"{company}: {user.data}")

if __name__ == "__main__":
    asyncio.run(check_merchant_name())
