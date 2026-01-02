from supabase_client import supabase

def check_data():
    tables = ['users', 'products', 'services', 'campaigns', 'sales', 'commissions', 'tracking_links', 'conversions', 'payouts', 'leads']
    
    print("--- Database Counts ---")
    for table in tables:
        try:
            response = supabase.table(table).select('id', count='exact').execute()
            count = response.count
            print(f"{table}: {count}")
        except Exception as e:
            print(f"{table}: Error - {e}")

if __name__ == "__main__":
    check_data()
