import sys
import os
from dotenv import load_dotenv
from supabase_client import supabase

def apply_sql():
    print("Applying dashboard columns...")
    
    sql_commands = [
        # Products table
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0;",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS total_views INTEGER DEFAULT 0;",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS total_clicks INTEGER DEFAULT 0;",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS total_sales INTEGER DEFAULT 0;",
        
        # Influencers table
        "ALTER TABLE influencers ADD COLUMN IF NOT EXISTS total_followers INTEGER DEFAULT 0;",
        "ALTER TABLE influencers ADD COLUMN IF NOT EXISTS engagement_rate DECIMAL(5,2) DEFAULT 0;",
        "ALTER TABLE influencers ADD COLUMN IF NOT EXISTS total_earnings DECIMAL(10,2) DEFAULT 0;",
        "ALTER TABLE influencers ADD COLUMN IF NOT EXISTS total_clicks INTEGER DEFAULT 0;",
        "ALTER TABLE influencers ADD COLUMN IF NOT EXISTS total_sales INTEGER DEFAULT 0;",
        "ALTER TABLE influencers ADD COLUMN IF NOT EXISTS influencer_type VARCHAR(50);",
        
        # Merchants table
        "ALTER TABLE merchants ADD COLUMN IF NOT EXISTS products_count INTEGER DEFAULT 0;",
        "ALTER TABLE merchants ADD COLUMN IF NOT EXISTS total_sales DECIMAL(10,2) DEFAULT 0;"
    ]
    
    for cmd in sql_commands:
        try:
            print(f"Executing: {cmd}")
            # Try RPC exec_sql
            response = supabase.rpc('exec_sql', {'query': cmd}).execute()
            print("Success.")
        except Exception as e:
            print(f"RPC failed for command: {cmd}")
            print(f"Error: {e}")
            
if __name__ == "__main__":
    apply_sql()
