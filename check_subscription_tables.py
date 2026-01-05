
from backend.supabase_client import supabase
import json

def check_tables():
    print("Checking tables...")
    
    # Check subscription_plans
    try:
        print("Checking subscription_plans...")
        plans = supabase.table("subscription_plans").select("*").limit(1).execute()
        print(f"subscription_plans exists. Data: {plans.data}")
    except Exception as e:
        print(f"Error checking subscription_plans: {e}")

    # Check subscriptions
    try:
        print("Checking subscriptions...")
        subs = supabase.table("subscriptions").select("*").limit(1).execute()
        print(f"subscriptions exists. Data: {subs.data}")
    except Exception as e:
        print(f"Error checking subscriptions: {e}")

if __name__ == "__main__":
    check_tables()
