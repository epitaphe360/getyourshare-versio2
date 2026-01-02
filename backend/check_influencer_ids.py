
from supabase_config import get_supabase_client
import asyncio

async def check_influencer_ids():
    supabase = get_supabase_client()
    
    influencers = ["Nadia Travel", "Karim Tech", "Leila Food", "Youssef Fashion", "Sofia Travel"]
    
    # Search by full_name or email or something
    # The user provided names like "Nadia Travel (@nadia_travel)"
    
    print("--- Influencers ---")
    all_influencers = supabase.table('users').select('id, full_name, email').eq('role', 'influencer').execute()
    for inf in all_influencers.data:
        print(inf)

if __name__ == "__main__":
    asyncio.run(check_influencer_ids())
