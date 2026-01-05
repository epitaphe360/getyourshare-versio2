import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

load_dotenv()

from supabase_client import supabase

def check_table(table_name):
    print(f"Checking table: {table_name}...", end=" ")
    try:
        supabase.table(table_name).select("*").limit(1).execute()
        print("EXISTS")
        return True
    except Exception as e:
        print(f"MISSING or ERROR: {e}")
        return False

tables_to_check = [
    "users",
    "merchants",
    "influencers",
    "products",
    "services",
    "product_categories",
    "product_reviews",
    "affiliate_requests",
    "campaigns",
    "sales",
    "conversions",
    "click_tracking",
    "commissions",
    "payouts"
]

print("--- Database Table Check ---")
for table in tables_to_check:
    check_table(table)
