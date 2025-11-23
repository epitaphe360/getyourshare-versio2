
from supabase_config import get_supabase_client
import asyncio

async def check_specific_commissions():
    supabase = get_supabase_client()
    
    influencers = {
        "Nadia Travel": "33333333-3333-3333-3333-333333333337",
        "Youssef Fashion": "33333333-3333-3333-3333-333333333336",
        "Leila Food": "77777777-7777-7777-7777-777777777771",
        "Karim Tech (email)": "e4dd947f-217a-4605-a5c1-093f9bee34ca",
        "Sofia Travel (email)": "5bcd78a1-5b35-481d-b44f-7dda6a1ed3a3"
    }
    
    print("--- Commissions for specific influencers ---")
    for name, uid in influencers.items():
        commissions = supabase.table('commissions').select('amount').eq('influencer_id', uid).execute()
        total = sum([float(c['amount']) for c in commissions.data])
        print(f"{name} ({uid}): {total} € (Count: {len(commissions.data)})")

    print("\n--- Sales for specific merchants ---")
    merchants = {
        "Sport Shop Elite": "22222222-2222-2222-2222-222222222225",
        "Tech Gadgets Pro": "22222222-2222-2222-2222-222222222223",
        "Fashion Store Paris": "22222222-2222-2222-2222-222222222222",
        "Food Delights": "22222222-2222-2222-2222-222222222226",
        "Beauty Paris": "22222222-2222-2222-2222-222222222224"
    }
    
    for name, uid in merchants.items():
        sales = supabase.table('sales').select('amount').eq('merchant_id', uid).execute()
        total = sum([float(s['amount']) for s in sales.data])
        print(f"{name} ({uid}): {total} € (Count: {len(sales.data)})")

if __name__ == "__main__":
    asyncio.run(check_specific_commissions())
