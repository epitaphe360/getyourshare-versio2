#!/usr/bin/env python3
"""Test admin login."""

from supabase_config import get_supabase_client
from db_helpers import verify_password

def main():
    sb = get_supabase_client()
    
    # Get admin user
    result = sb.table('users').select('email,password_hash').eq('email', 'admin@getyourshare.com').execute()
    
    if result.data:
        user = result.data[0]
        password_hash = user['password_hash']
        
        print(f"Email: {user['email']}")
        print(f"Hash exists: {bool(password_hash)}")
        print(f"Hash: {password_hash[:30]}...")
        
        # Test password
        test_passwords = ['admin123', 'Admin123', 'admin', 'password', '123456']
        
        for pwd in test_passwords:
            is_valid = verify_password(pwd, password_hash)
            print(f"Password '{pwd}': {'✅ VALID' if is_valid else '❌ Invalid'}")
    else:
        print("Admin not found!")

if __name__ == "__main__":
    main()
