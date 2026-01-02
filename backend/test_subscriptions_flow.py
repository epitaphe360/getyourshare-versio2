import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import os
import sys

# Add backend directory to path to import supabase_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase_client import supabase
except ImportError:
    print("Warning: Could not import supabase_client. Database operations will be skipped.")
    supabase = None

BASE_URL = "http://localhost:8000"
PASSWORD = "Test1234!"
MERCHANT_EMAIL = "merchant_sub_test@test.com"

class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD} {text} {Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}")

def print_section(text):
    print(f"\n{Color.BLUE}{Color.BOLD}>> {text}{Color.ENDC}")

def print_success(text):
    print(f"{Color.GREEN}   [OK] {text}{Color.ENDC}")

def print_fail(text, details=""):
    print(f"{Color.FAIL}   [FAIL] {text}{Color.ENDC}")
    if details:
        print(f"{Color.FAIL}     Details: {details}{Color.ENDC}")

def create_test_user():
    print_section("Creating Test User")
    # Check if user exists
    res = supabase.table("users").select("id").eq("email", MERCHANT_EMAIL).execute()
    if res.data:
        user_id = res.data[0]["id"]
        print_success(f"User already exists: {user_id}")
        return user_id
    
    # Create user
    from db_helpers import hash_password
    user_data = {
        "email": MERCHANT_EMAIL,
        "password_hash": hash_password(PASSWORD),
        "role": "merchant",
        "username": "merchant_sub_test",
        "status": "active",
        "is_active": True
    }
    res = supabase.table("users").insert(user_data).execute()
    if res.data:
        user_id = res.data[0]["id"]
        print_success(f"Created user: {user_id}")
        
        # Create merchant profile
        merchant_data = {
            "user_id": user_id,
            "company_name": "Subscription Test Co",
            "industry": "Retail"
        }
        supabase.table("merchants").insert(merchant_data).execute()
        return user_id
    else:
        print_fail("Failed to create user")
        return None

def login(session):
    print_section("Logging in")
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": MERCHANT_EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_success("Login successful")
            token = response.cookies.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
            
            # Get CSRF token
            session.get(f"{BASE_URL}/api/dashboard/stats")
            csrf_token = session.cookies.get("csrf_token")
            if csrf_token:
                session.headers.update({"X-CSRF-Token": csrf_token})
            
            return True
        else:
            print_fail(f"Login failed: {response.status_code}", response.text)
            return False
    except Exception as e:
        print_fail("Login exception", str(e))
        return False

def clean_subscriptions(user_id):
    print_section("Cleaning up existing subscriptions")
    supabase.table("subscriptions").delete().eq("user_id", user_id).execute()
    print_success("Subscriptions cleaned")

def test_subscription_flow():
    print_header("TESTING SUBSCRIPTION FLOW")
    
    session = requests.Session()
    user_id = create_test_user()
    if not user_id:
        return
    
    if not login(session):
        return
    
    clean_subscriptions(user_id)
    
    # --- Step 1: Check Default State ---
    print_section("Step 1: Check Default State (Freemium)")
    res = session.get(f"{BASE_URL}/api/subscriptions/current")
    if res.status_code == 200:
        data = res.json()
        print(f"Current Plan: {data.get('plan_name')}")
        if data.get("plan_name") in ["Freemium", "Free"]:
            print_success("Default plan is correct")
        else:
            print_fail(f"Expected Freemium/Free, got {data.get('plan_name')}")
    else:
        print_fail("Failed to get current subscription", res.text)

    # --- Step 2: Get Available Plans ---
    print_section("Step 2: Get Available Plans")
    res = session.get(f"{BASE_URL}/api/subscriptions/plans")
    plans = []
    if res.status_code == 200:
        plans = res.json()
        print_success(f"Retrieved {len(plans)} plans")
        for p in plans:
            print(f" - {p['name']} ({p['id']})")
    else:
        print_fail("Failed to get plans", res.text)
        return

    if not plans:
        print_fail("No plans available to test")
        return

    # Pick a plan (e.g., the first paid plan)
    target_plan = plans[0]
    print(f"Selected plan for testing: {target_plan['name']}")

    # --- Step 3: Simulate Subscription ---
    print_section(f"Step 3: Simulate Subscription to {target_plan['name']}")
    
    # Insert subscription directly into DB
    sub_id = str(uuid.uuid4())
    now = datetime.utcnow()
    end_date = now + timedelta(days=30)
    
    sub_data = {
        "id": sub_id,
        "user_id": user_id,
        "plan_id": target_plan["id"],
        "status": "active",
        "stripe_subscription_id": f"sub_test_{uuid.uuid4()}",
        # "stripe_customer_id": f"cus_test_{uuid.uuid4()}", # Not in schema
        "current_period_start": now.isoformat(),
        "current_period_end": end_date.isoformat(),
        # "current_team_members": 0, # Not in schema
        # "current_domains": 0 # Not in schema
    }
    
    res_db = supabase.table("subscriptions").insert(sub_data).execute()
    if res_db.data:
        print_success("Inserted subscription record into DB")
    else:
        print_fail("Failed to insert subscription record")
        return

    # Verify via API
    res = session.get(f"{BASE_URL}/api/subscriptions/current")
    if res.status_code == 200:
        data = res.json()
        print(f"Current Plan: {data.get('plan_name')}")
        # Note: API might return 'plan_name' from joined table or from the subscription object
        # The endpoint implementation joins with subscription_plans or returns data from v_active_subscriptions
        if data.get("plan_name") == target_plan["name"] or data.get("plan_id") == target_plan["id"]:
             print_success(f"API reflects active subscription: {target_plan['name']}")
        else:
             # Fallback check if names don't match exactly due to casing
             if target_plan['name'] in data.get('plan_name', ''):
                 print_success(f"API reflects active subscription (fuzzy match): {data.get('plan_name')}")
             else:
                 print_fail(f"Expected {target_plan['name']}, got {data.get('plan_name')}")
                 print(json.dumps(data, indent=2))
    else:
        print_fail("Failed to get current subscription", res.text)

    # --- Step 4: Check Usage ---
    print_section("Step 4: Check Usage Limits")
    res = session.get(f"{BASE_URL}/api/subscriptions/usage")
    if res.status_code == 200:
        data = res.json()
        print_success("Usage data retrieved")
        print(f" - Team Members: {data.get('team_members_used')} / {data.get('team_members_limit')}")
        print(f" - Domains: {data.get('domains_used')} / {data.get('domains_limit')}")
        
        # Verify limits match plan
        if data.get('team_members_limit') == target_plan.get('max_team_members'):
            print_success("Team member limit matches plan")
        else:
            print_fail(f"Team limit mismatch: Expected {target_plan.get('max_team_members')}, got {data.get('team_members_limit')}")
    else:
        print_fail("Failed to get usage", res.text)

    # --- Step 5: Simulate Upgrade ---
    if len(plans) > 1:
        upgrade_plan = plans[1]
        print_section(f"Step 5: Simulate Upgrade to {upgrade_plan['name']}")
        
        # Update DB
        res_db = supabase.table("subscriptions").update({"plan_id": upgrade_plan["id"]}).eq("id", sub_id).execute()
        if res_db.data:
            print_success("Updated subscription record in DB")
            
            # Verify via API
            res = session.get(f"{BASE_URL}/api/subscriptions/current")
            if res.status_code == 200:
                data = res.json()
                print(f"Current Plan: {data.get('plan_name')}")
                if data.get("plan_name") == upgrade_plan["name"] or data.get("plan_id") == upgrade_plan["id"]:
                    print_success(f"API reflects upgrade: {upgrade_plan['name']}")
                else:
                    if upgrade_plan['name'] in data.get('plan_name', ''):
                        print_success(f"API reflects upgrade (fuzzy match): {data.get('plan_name')}")
                    else:
                        print_fail(f"Expected {upgrade_plan['name']}, got {data.get('plan_name')}")
            else:
                print_fail("Failed to get current subscription", res.text)
        else:
            print_fail("Failed to update subscription in DB")
    else:
        print("Skipping upgrade test (only 1 plan available)")

    # --- Step 6: Simulate Cancellation ---
    print_section("Step 6: Simulate Cancellation")
    
    # Update DB to canceled
    try:
        res_db = supabase.table("subscriptions").update({
            "status": "canceled",
            # "canceled_at": datetime.utcnow().isoformat(), # Not in schema
            # "ended_at": datetime.utcnow().isoformat() # Not in schema
        }).eq("id", sub_id).execute()
        
        if res_db.data:
            print_success("Updated subscription to canceled in DB")
            
            # Verify via API
            res = session.get(f"{BASE_URL}/api/subscriptions/current")
            if res.status_code == 200:
                data = res.json()
                print(f"Current Plan: {data.get('plan_name')}")
                print(f"Status: {data.get('status')}")
                
                if data.get("plan_name") in ["Freemium", "Free"]:
                    print_success("API correctly fell back to Default Plan after cancellation")
                elif data.get("status") == "canceled":
                    print_success("API returns canceled subscription")
                else:
                    print_fail(f"Expected Default Plan or Canceled status, got {data.get('plan_name')} ({data.get('status')})")
            else:
                print_fail("Failed to get current subscription", res.text)
        else:
            print_fail("Failed to cancel subscription in DB")
    except Exception as e:
        print_fail("Exception canceling subscription", str(e))
        # Try 'cancelled' with double l
        try:
            print("Retrying with 'cancelled'...")
            res_db = supabase.table("subscriptions").update({
                "status": "cancelled"
            }).eq("id", sub_id).execute()
            print_success("Updated subscription to cancelled (double l)")
        except Exception as e2:
            print_fail("Exception canceling subscription (retry)", str(e2))

    # Cleanup
    clean_subscriptions(user_id)

if __name__ == "__main__":
    test_subscription_flow()
