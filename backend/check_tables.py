
from supabase_client import supabase
try:
    # Try to select one row to see columns, or just check error
    print("Checking commissions table...")
    res = supabase.table('commissions').select('*').limit(1).execute()
    if res.data:
        print("Commissions columns:", res.data[0].keys())
    else:
        print("Commissions table empty, but query worked.")
except Exception as e:
    print(f"Error checking commissions: {e}")

try:
    print("Checking conversions table...")
    res = supabase.table('conversions').select('*').limit(1).execute()
    if res.data:
        print("Conversions columns:", res.data[0].keys())
    else:
        print("Conversions table empty, but query worked.")
except Exception as e:
    print(f"Error checking conversions: {e}")
