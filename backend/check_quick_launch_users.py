import os
import sys
from dotenv import load_dotenv

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

load_dotenv()

try:
    from db_helpers import get_user_by_email
except ImportError:
    print("Error: Could not import db_helpers. Make sure you are running this from the backend directory.")
    sys.exit(1)

users_to_check = [
    "admin@getyourshare.com",
    "hassan.oudrhiri@getyourshare.com",
    "sarah.benali@getyourshare.com",
    "karim.benjelloun@getyourshare.com",
    "boutique.maroc@getyourshare.com",
    "luxury.crafts@getyourshare.com",
    "electromaroc@getyourshare.com",
    "sofia.chakir@getyourshare.com"
]

print("Checking users from COMPTES_TEST_CONNEXION_RAPIDE.md...")
print("-" * 50)

all_exist = True
for email in users_to_check:
    user = get_user_by_email(email)
    if user:
        print(f"✅ {email}: Found (Role: {user.get('role')})")
    else:
        print(f"❌ {email}: NOT FOUND")
        all_exist = False

print("-" * 50)
if all_exist:
    print("All quick launch users exist in the database.")
else:
    print("Some quick launch users are missing.")
