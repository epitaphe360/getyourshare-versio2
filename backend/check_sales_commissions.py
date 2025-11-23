
from supabase_config import get_supabase_client
import asyncio

async def check_data():
    supabase = get_supabase_client()
    
    print("--- SALES ---")
    sales = supabase.table('sales').select('*').execute()
    print(f"Total sales: {len(sales.data)}")
    for sale in sales.data[:5]:
        print(sale)
        
    print("\n--- COMMISSIONS ---")
    commissions = supabase.table('commissions').select('*').execute()
    print(f"Total commissions: {len(commissions.data)}")
    for comm in commissions.data[:5]:
        print(comm)

    print("\n--- USERS (Merchants) ---")
    merchants = supabase.table('users').select('id, company_name').eq('role', 'merchant').execute()
    print(f"Total merchants: {len(merchants.data)}")
    for m in merchants.data[:5]:
        print(m)

if __name__ == "__main__":
    asyncio.run(check_data())
