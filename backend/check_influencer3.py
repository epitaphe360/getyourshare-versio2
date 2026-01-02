from db_helpers import get_user_by_email
from services.twofa_service import twofa_service
import asyncio

async def check():
    email = "influencer3@lifestyle.com"
    print(f"Checking {email}...")
    user = get_user_by_email(email)
    if user:
        print("User found:")
        print(f"ID: {user.get('id')}")
        print(f"Role: {user.get('role')}")
        print(f"2FA Enabled (DB column): {user.get('two_fa_enabled')}")
        
        status_2fa = await twofa_service.get_2fa_status(user['id'])
        print(f"2FA Status (Service): {status_2fa}")
    else:
        print("User not found")

if __name__ == "__main__":
    asyncio.run(check())
