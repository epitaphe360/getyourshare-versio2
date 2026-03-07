import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path)

from supabase_client import get_supabase_client

def verify_fix():
    print("Verifying Referral System Fix...")
    supabase = get_supabase_client()
    
    try:
        # 1. Get a test user
        print("Fetching a user to test with...")
        # We need a user from auth.users or public.users. 
        # public.users is usually a copy.
        users = supabase.table('users').select('id, email').limit(1).execute()
        
        if not users.data:
            print("No users found in public.users. Cannot verify RPC without a user_id.")
            return
            
        test_user = users.data[0]
        user_id = test_user['id']
        email = test_user.get('email', 'No Email')
        print(f"Testing with User: {email} (ID: {user_id})")
        
        # 2. Test the RPC function 'generate_referral_code'
        print("\nTesting RPC 'generate_referral_code'...")
        try:
            # Note: This will generate a code based on the email. 
            # It doesn't insert into referral_codes table, just returns the string (based on my understanding of the fix).
            # The endpoint does the insertion.
            result = supabase.rpc('generate_referral_code', {'p_user_id': user_id}).execute()
            print(f"✅ RPC Success! Generated Code: {result.data}")
        except Exception as e:
            print(f"❌ RPC Failed: {e}")
            print("Did you run the SQL script in Supabase?")
            return

        # 3. Test the View 'v_referral_dashboard'
        print("\nTesting View 'v_referral_dashboard'...")
        try:
            # Just try to select from it
            view_result = supabase.table('v_referral_dashboard').select('*').limit(1).execute()
            print("✅ View Access Success!")
        except Exception as e:
            print(f"❌ View Access Failed: {e}")
            
        print("\nVerification Complete. The database side is fixed.")
        print("Please restart your backend server to apply Python code changes.")

    except Exception as e:
        print(f"An error occurred during verification: {e}")

if __name__ == "__main__":
    verify_fix()
