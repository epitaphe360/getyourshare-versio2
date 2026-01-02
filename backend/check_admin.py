#!/usr/bin/env python3
"""Check admin users in the database."""

from supabase_config import get_supabase_client

def main():
    sb = get_supabase_client()
    
    # Get all admin users
    result = sb.table('users').select('id,email,role,full_name').eq('role', 'admin').execute()
    
    print("=" * 50)
    print("ADMIN USERS IN DATABASE")
    print("=" * 50)
    
    if result.data:
        for user in result.data:
            print(f"  Email: {user.get('email')}")
            print(f"  Name: {user.get('full_name')}")
            print(f"  Role: {user.get('role')}")
            print(f"  ID: {user.get('id')}")
            print("-" * 30)
    else:
        print("No admin users found!")
    
    print(f"\nTotal admins: {len(result.data)}")

if __name__ == "__main__":
    main()
