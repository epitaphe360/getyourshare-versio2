import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.supabase_client import supabase

async def update_dates():
    print("--- UPDATING DATES TO BE RECENT ---")
    
    # Target range: Last 30 days (Nov 4 - Dec 4)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    tables = ['sales', 'commissions', 'conversions', 'users', 'products', 'services']
    
    for table in tables:
        print(f"Updating {table}...")
        try:
            # Fetch all rows
            response = supabase.table(table).select('id, created_at').execute()
            rows = response.data
            
            if not rows:
                print(f"No rows in {table}")
                continue
                
            print(f"Found {len(rows)} rows in {table}")
            
            for row in rows:
                # Generate a random date within the last 30 days
                random_days = random.randint(0, 30)
                new_date = (end_date - timedelta(days=random_days)).isoformat()
                
                # Update the row
                supabase.table(table).update({'created_at': new_date}).eq('id', row['id']).execute()
                
            print(f"Updated {table} successfully")
            
        except Exception as e:
            print(f"Error updating {table}: {e}")

if __name__ == "__main__":
    asyncio.run(update_dates())
