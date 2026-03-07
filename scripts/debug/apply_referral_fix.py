import os

def print_instructions():
    print("\n" + "="*60)
    print("REFERRAL SYSTEM FIX INSTRUCTIONS")
    print("="*60)
    print("\nThe automatic fix could not be applied because the 'exec_sql' function")
    print("is missing from your Supabase database.")
    print("\nPlease follow these steps manually:")
    print("\n1. Go to your Supabase Dashboard: https://app.supabase.com")
    print("2. Open the SQL Editor")
    print("3. Create a NEW QUERY")
    print("4. Copy and paste the content of the file 'FIX_REFERRAL_SYSTEM.sql'")
    print("   (located in the root of your project)")
    print("5. Click RUN")
    print("\nOnce executed, the referral code generation will work correctly.")
    print("="*60 + "\n")

if __name__ == "__main__":
    print_instructions()
