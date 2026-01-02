
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import bcrypt

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

QUICK_LOGIN_USERS = [
    {'email': 'admin@getyourshare.com', 'password': 'Admin123!', 'role': 'admin'},
    {'email': 'influencer1@fashion.com', 'password': 'Test123!', 'role': 'influencer'},
    {'email': 'influencer2@tech.com', 'password': 'Test123!', 'role': 'influencer'},
    {'email': 'influencer3@lifestyle.com', 'password': 'Test123!', 'role': 'influencer'},
    {'email': 'merchant1@fashionstore.com', 'password': 'Test123!', 'role': 'merchant'},
    {'email': 'merchant2@techgadgets.com', 'password': 'Test123!', 'role': 'merchant'},
    {'email': 'merchant3@beautyparis.com', 'password': 'Test123!', 'role': 'merchant'},
    {'email': 'commercial1@getyourshare.com', 'password': 'Test123!', 'role': 'commercial'},
]

def check_and_fix_users():
    print("Checking Quick Login Users...")
    
    for user_info in QUICK_LOGIN_USERS:
        email = user_info['email']
        password = user_info['password']
        role = user_info['role']
        
        print(f"\nChecking {email} ({role})...")
        
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not response.data:
            print(f"❌ User {email} does not exist. Creating...")
            # Create user
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = {
                'email': email,
                'password_hash': password_hash,
                'role': role,
                'is_active': True,
                'full_name': email.split('@')[0],
                'company_name': f"{role.capitalize()} Company"
            }
            try:
                supabase.table('users').insert(new_user).execute()
                print(f"✅ User {email} created successfully.")
            except Exception as e:
                print(f"❌ Failed to create user {email}: {e}")
        else:
            user = response.data[0]
            stored_hash = user.get('password_hash')
            
            if not stored_hash:
                print(f"❌ User {email} exists but has no password hash. Updating...")
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                supabase.table('users').update({'password_hash': password_hash}).eq('id', user['id']).execute()
                print(f"✅ Password updated for {email}.")
                continue

            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    print(f"✅ User {email} exists and password is correct.")
                else:
                    print(f"❌ User {email} exists but password is INCORRECT. Updating...")
                    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    supabase.table('users').update({'password_hash': password_hash}).eq('id', user['id']).execute()
                    print(f"✅ Password updated for {email}.")
            except Exception as e:
                print(f"❌ Error checking password for {email}: {e}")

if __name__ == "__main__":
    check_and_fix_users()
