import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.supabase_client import supabase

async def check_data():
    print("--- CHECKING DATABASE CONTENT ---")
    
    tables = ['users', 'products', 'services', 'sales', 'commissions', 'tracking_links', 'conversions', 'payouts']
    
    for table in tables:
        try:
            response = supabase.table(table).select('id', count='exact', head=True).execute()
            count = response.count
            print(f"Table '{table}': {count} rows")
        except Exception as e:
            print(f"Error checking table '{table}': {e}")

    print("\n--- CHECKING SPECIFIC DATA FOR CHARTS ---")
    
    # Check sales for revenue chart
    sales = supabase.table('sales').select('amount, created_at').execute()
    print(f"Sales with amount: {len(sales.data)}")
    if sales.data:
        print(f"Sample sale: {sales.data[0]}")
        
    # Check commissions for influencers
    commissions = supabase.table('commissions').select('amount, influencer_id').execute()
    print(f"Commissions: {len(commissions.data)}")
    
    # Check tracking links
    links = supabase.table('tracking_links').select('clicks, influencer_id').execute()
    print(f"Tracking links: {len(links.data)}")

if __name__ == "__main__":
    asyncio.run(check_data())
