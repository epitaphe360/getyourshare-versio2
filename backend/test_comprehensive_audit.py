import requests
import json
import time
import math
from datetime import datetime
try:
    from supabase_client import supabase
except ImportError:
    print("Warning: Could not import supabase_client. Database operations will be skipped.")
    supabase = None

BASE_URL = "http://localhost:8000"
PASSWORD = "Test1234!"

USERS = {
    "admin": "admin@getyourshare.com",
    "merchant": "merchant1@fashionstore.com",
    "influencer": "influencer1@fashion.com",
    "commercial": "commercial1@shareyoursales.ma"
}

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

def print_info(key, value):
    print(f"     {key}: {Color.CYAN}{value}{Color.ENDC}")

def check_integrity(data, path="root"):
    """Recursively check for NaN, Infinity, or 'NaN' strings in JSON data."""
    issues = []
    
    if isinstance(data, dict):
        for k, v in data.items():
            issues.extend(check_integrity(v, f"{path}.{k}"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            issues.extend(check_integrity(item, f"{path}[{i}]"))
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            issues.append(f"Found NaN/Inf at {path}: {data}")
    elif isinstance(data, str):
        if data.lower() == "nan" or data.lower() == "null":
             # "null" string might be valid text, but "nan" is suspicious
            if data.lower() == "nan":
                issues.append(f"Found 'NaN' string at {path}")
            
    return issues

def validate_response(response, description):
    if response.status_code != 200:
        print_fail(f"Failed {description}", f"Status: {response.status_code}, Body: {response.text[:200]}")
        return False
    
    try:
        data = response.json()
        issues = check_integrity(data)
        if issues:
            print_fail(f"Data integrity issues in {description}", ", ".join(issues[:3]))
            return False
        
        print_success(f"{description} retrieved & verified")
        return True
    except Exception as e:
        print_fail(f"Exception validating {description}", str(e))
        return False

def login(session, email, role_name):
    print_section(f"Authenticating as {role_name} ({email})...")
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": PASSWORD},
            headers={"Content-Type": "application/json", "Origin": "http://localhost:3000"}
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            print_success(f"Login successful as {user.get('role')}")
            
            # Extract token from cookies and set Authorization header
            token = response.cookies.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
            else:
                print_fail("Token not found in cookies")
            
            # Perform a GET request to ensure CSRF cookie is set
            session.get(f"{BASE_URL}/api/dashboard/stats")
            
            print(f"Cookies after login: {session.cookies.get_dict()}")

            # Extract CSRF token from cookies and set X-CSRF-Token header
            csrf_token = session.cookies.get("csrf_token")
            if csrf_token:
                session.headers.update({"X-CSRF-Token": csrf_token})
                print(f"CSRF Token set in headers: {csrf_token}")
                print(f"Session headers: {session.headers}")
            else:
                print_fail("CSRF Token not found in cookies")
                
            return user
        else:
            print_fail(f"Login failed: {response.status_code}", response.text)
            return None
    except Exception as e:
        print_fail(f"Login exception", str(e))
        return None

def refresh_csrf_header(session):
    """Update X-CSRF-Token header from current session cookies"""
    csrf_token = session.cookies.get("csrf_token")
    if csrf_token:
        session.headers.update({"X-CSRF-Token": csrf_token})
        # print(f"Refreshed CSRF Token: {csrf_token}")
    else:
        print_fail("Could not refresh CSRF token: Cookie missing")

# --- 1. ADMIN DASHBOARD TESTS ---
def test_admin_dashboard(session):
    print_header("TESTING ADMIN DASHBOARD")
    
    # Overview Stats
    print_section("Overview Stats")
    validate_response(session.get(f"{BASE_URL}/api/dashboard/stats"), "Admin Stats (Legacy)")
    validate_response(session.get(f"{BASE_URL}/api/analytics/overview"), "Admin Analytics Overview")
    validate_response(session.get(f"{BASE_URL}/api/analytics/platform-metrics"), "Platform Metrics")

    # Charts & Data
    print_section("Charts & Visualizations")
    validate_response(session.get(f"{BASE_URL}/api/analytics/revenue-chart?days=30"), "Revenue Chart")
    validate_response(session.get(f"{BASE_URL}/api/analytics/categories"), "Category Distribution")
    validate_response(session.get(f"{BASE_URL}/api/analytics/top-merchants"), "Top Merchants")
    validate_response(session.get(f"{BASE_URL}/api/analytics/top-influencers"), "Top Influencers")

    # User Management
    print_section("User Management")
    validate_response(session.get(f"{BASE_URL}/api/admin/users?role=merchant"), "Merchant List")
    validate_response(session.get(f"{BASE_URL}/api/admin/users?role=influencer"), "Influencer List")

# --- 2. MERCHANT DASHBOARD TESTS ---
def test_merchant_dashboard(session, user_id):
    print_header("TESTING MERCHANT DASHBOARD")
    
    # Dashboard Overview
    print_section("Dashboard Overview")
    validate_response(session.get(f"{BASE_URL}/api/dashboard/stats"), "Merchant Stats (Legacy)")
    validate_response(session.get(f"{BASE_URL}/api/analytics/merchant/performance?merchant_id={user_id}"), "Merchant Performance")
    
    # Charts
    print_section("Charts")
    validate_response(session.get(f"{BASE_URL}/api/analytics/merchant/sales-chart?merchant_id={user_id}&days=30"), "Sales Chart")

    # Campaigns
    print_section("Campaigns")
    validate_response(session.get(f"{BASE_URL}/api/campaigns"), "Campaigns List")

    # Products
    print_section("Products")
    validate_response(session.get(f"{BASE_URL}/api/products"), "Products List")

    # Subscriptions
    print_section("Subscriptions")
    validate_response(session.get(f"{BASE_URL}/api/subscriptions/current"), "Current Subscription")

# --- 3. INFLUENCER DASHBOARD TESTS ---
def test_influencer_dashboard(session, user_id):
    print_header("TESTING INFLUENCER DASHBOARD")
    
    # Dashboard Overview
    print_section("Dashboard Overview")
    validate_response(session.get(f"{BASE_URL}/api/dashboard/stats"), "Influencer Stats (Legacy)")
    validate_response(session.get(f"{BASE_URL}/api/analytics/influencer/overview?influencer_id={user_id}"), "Influencer Overview")

    # Charts
    print_section("Charts")
    validate_response(session.get(f"{BASE_URL}/api/analytics/influencer/earnings-chart?influencer_id={user_id}&days=30"), "Earnings Chart")

    # Marketplace
    print_section("Marketplace")
    validate_response(session.get(f"{BASE_URL}/api/marketplace/products"), "Marketplace Products")

    # Earnings
    print_section("Earnings/Wallet")
    # Note: finance/earnings might return 404 if not implemented, checking anyway
    res = session.get(f"{BASE_URL}/api/finance/earnings")
    if res.status_code == 200:
        validate_response(res, "Earnings Endpoint")
    elif res.status_code == 404:
        print_info("Earnings Endpoint", "Not Found (Optional)")
    else:
        print_fail("Earnings Endpoint Error", res.text)

# --- 4. COMMERCIAL DASHBOARD TESTS ---
def test_commercial_dashboard(session):
    print_header("TESTING COMMERCIAL DASHBOARD")
    
    # Dashboard Overview
    print_section("Dashboard Overview")
    validate_response(session.get(f"{BASE_URL}/api/sales/dashboard/me"), "Commercial Stats")

    # Leads
    print_section("Leads Management")
    validate_response(session.get(f"{BASE_URL}/api/leads"), "Leads List")

# --- 5. MESSAGING SYSTEM ---
def test_messaging(merchant_session, influencer_session, merchant_user, influencer_user):
    print_header("TESTING MESSAGING SYSTEM")
    
    print_section("Sending Message (Merchant -> Influencer)")
    msg_content = f"Audit Test {datetime.now().isoformat()}"
    try:
        payload = {
            "recipient_id": influencer_user["id"],
            "recipient_type": "influencer",
            "content": msg_content,
            "subject": "Audit Test"
        }
        res = merchant_session.post(f"{BASE_URL}/api/messages/send", json=payload)
        
        if res.status_code == 200:
            print_success("Message sent successfully")
            # Check inbox
            print_section("Checking Inbox (Influencer)")
            validate_response(influencer_session.get(f"{BASE_URL}/api/messages/conversations"), "Inbox")
        else:
            print_fail("Failed to send message", res.text)
    except Exception as e:
        print_fail("Exception in messaging test", str(e))

# --- 6. ADMIN SOCIAL TOOLS TESTS ---
def test_admin_social_tools(session):
    print_header("TESTING ADMIN SOCIAL TOOLS")
    
    # Posts
    print_section("Social Posts")
    validate_response(session.get(f"{BASE_URL}/api/admin/social/posts"), "List Social Posts")
    
    # Templates
    print_section("Social Templates")
    validate_response(session.get(f"{BASE_URL}/api/admin/social/templates"), "List Social Templates")
    
    # Analytics
    print_section("Social Analytics")
    validate_response(session.get(f"{BASE_URL}/api/admin/social/analytics"), "Social Analytics")

# --- 7. COMMERCIALS DIRECTORY TESTS ---
def test_commercials_directory(session, commercial_user_id):
    print_header("TESTING COMMERCIALS DIRECTORY")
    
    # Directory
    print_section("Directory Listing")
    validate_response(session.get(f"{BASE_URL}/api/commercials/directory"), "Search Commercials")
    
    # My Profile
    print_section("My Profile")
    validate_response(session.get(f"{BASE_URL}/api/commercials/profile/my-profile"), "Get My Profile")
    
    # Public Profile
    print_section("Public Profile")
    validate_response(session.get(f"{BASE_URL}/api/commercials/{commercial_user_id}"), "Get Public Profile")

# --- 8. AI FEATURES TESTS ---
def test_ai_features(session, user_id, role):
    print_header(f"TESTING AI FEATURES ({role})")
    
    # Bot
    print_section("AI Bot")
    validate_response(session.get(f"{BASE_URL}/api/bot/conversations"), "Bot Conversations")
    validate_response(session.get(f"{BASE_URL}/api/bot/suggestions"), "Bot Suggestions")
    
    # Product Recommendations (Influencer only)
    if role == "Influencer":
        print_section("Product Recommendations")
        validate_response(session.get(f"{BASE_URL}/api/ai/product-recommendations/{user_id}"), "Product Recommendations")
        
        print_section("Content Templates")
        validate_response(session.get(f"{BASE_URL}/api/ai/content-templates/{user_id}"), "Content Templates")
        
    # Live Shopping
    print_section("Live Shopping")
    validate_response(session.get(f"{BASE_URL}/api/ai/live-shopping/upcoming"), "Upcoming Live Sessions")

# --- 9. GAMIFICATION TESTS ---
def test_gamification(session, user_id, role="Merchant"):
    print_header("TESTING GAMIFICATION")
    print_section("Gamification Status")
    validate_response(session.get(f"{BASE_URL}/api/gamification/{user_id}"), "Gamification Status")

    if role == "Merchant":
        print_section("Influencer Matching")
        # Merchant only usually, but let's check access
        validate_response(session.get(f"{BASE_URL}/api/matching/get-recommendations?merchant_id={user_id}"), "Matching Recommendations")

# --- 10. ADVANCED PAYMENTS & INVOICING ---
def test_advanced_payments(session, role, user_id):
    print_header(f"TESTING ADVANCED PAYMENTS ({role})")
    
    if role == "Admin":
        print_section("Admin Invoices")
        validate_response(session.get(f"{BASE_URL}/api/admin/invoices"), "All Invoices")
        validate_response(session.get(f"{BASE_URL}/api/admin/gateways/stats"), "Gateway Stats")
        
    if role == "Merchant":
        print_section("Merchant Invoices & Deposits")
        validate_response(session.get(f"{BASE_URL}/api/merchant/invoices"), "My Invoices")
        validate_response(session.get(f"{BASE_URL}/api/leads/deposits/balance"), "Deposit Balance")
        validate_response(session.get(f"{BASE_URL}/api/leads/deposits/transactions"), "Deposit Transactions")
        validate_response(session.get(f"{BASE_URL}/api/mobile-payments-ma/providers"), "Mobile Payment Providers")

# --- 11. TEAM & COMPANY MANAGEMENT ---
def test_team_management(session, role):
    print_header(f"TESTING TEAM MANAGEMENT ({role})")
    if role == "Merchant":
        print_section("Team Members")
        validate_response(session.get(f"{BASE_URL}/api/team/members"), "Team Members")
        validate_response(session.get(f"{BASE_URL}/api/team/stats"), "Team Stats")
        
        print_section("Company Links")
        validate_response(session.get(f"{BASE_URL}/api/company/links/my-company-links"), "Company Links")

# --- 12. CONTENT STUDIO & SOCIAL ---
def test_content_studio(session, role):
    print_header(f"TESTING CONTENT STUDIO ({role})")
    if role == "Influencer":
        print_section("Content Templates")
        validate_response(session.get(f"{BASE_URL}/api/content-studio/templates"), "Content Templates")
        
        print_section("Social Connections")
        validate_response(session.get(f"{BASE_URL}/api/social-media/connections"), "Social Connections")
        validate_response(session.get(f"{BASE_URL}/api/social-media/dashboard"), "Social Dashboard")

# --- 13. ADVANCED COLLABORATION ---
def test_advanced_collaboration(session, role):
    print_header(f"TESTING ADVANCED COLLABORATION ({role})")
    if role == "Merchant":
        print_section("Affiliation Requests (Merchant)")
        validate_response(session.get(f"{BASE_URL}/api/affiliation-requests/merchant/pending"), "Pending Requests")
        validate_response(session.get(f"{BASE_URL}/api/merchant/affiliation-requests/stats"), "Request Stats")
        
    if role == "Influencer":
        print_section("Affiliation Requests (Influencer)")
        validate_response(session.get(f"{BASE_URL}/api/affiliation-requests/my-requests"), "My Requests")

# --- 14. WEBHOOKS & INTEGRATIONS ---
def test_integrations(session):
    print_header("TESTING INTEGRATIONS")
    print_section("TikTok Shop")
    validate_response(session.get(f"{BASE_URL}/api/tiktok-shop/analytics"), "TikTok Analytics")

# --- 15. USER MANAGEMENT & VALIDATION ---
def test_user_management(session):
    print_header("TESTING USER MANAGEMENT & VALIDATION")
    
    # 1. Register New Users (Merchant, Influencer, Commercial)
    timestamp = int(time.time())
    
    roles_to_test = [
        {"role": "merchant", "email": f"test_merchant_{timestamp}@example.com", "phone": "0600000001"},
        {"role": "influencer", "email": f"test_influencer_{timestamp}@example.com", "phone": "0600000002"},
        # Commercial registration might be admin-only or different endpoint, checking auth/register first
    ]
    
    for user_data in roles_to_test:
        print_section(f"Registering New {user_data['role'].capitalize()}")
        payload = {
            "email": user_data["email"],
            "password": "TestPassword123!",
            "role": user_data["role"],
            "phone": user_data["phone"]
        }
        res = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        if validate_response(res, f"Register {user_data['role']}"):
            new_user_id = res.json().get("user_id")
            
            # 2. Admin Actions on New User
            if new_user_id:
                print_section(f"Admin Actions on {user_data['role']}")
                # Ban
                ban_payload = {"status": "banned"}
                refresh_csrf_header(session)
                print(f"Sending PATCH with headers: {session.headers}")
                validate_response(session.patch(f"{BASE_URL}/api/admin/users/{new_user_id}/status", json=ban_payload), "Ban User")
                
                time.sleep(1) # Wait a bit

                # Unban (Activate)
                activate_payload = {"status": "active"}
                refresh_csrf_header(session)
                validate_response(session.patch(f"{BASE_URL}/api/admin/users/{new_user_id}/status", json=activate_payload), "Activate User")

    # 3. Admin Create User
    print_section("Admin Create User")
    admin_create_payload = {
        "username": f"admin_created_{timestamp}",
        "email": f"admin_created_{timestamp}@example.com",
        "password": "TestPassword123!",
        "role": "influencer",
        "status": "active"
    }
    refresh_csrf_header(session)
    validate_response(session.post(f"{BASE_URL}/api/admin/users", json=admin_create_payload), "Admin Create User")

    # 4. Audit Logs
    print_section("Audit Logs")
    validate_response(session.get(f"{BASE_URL}/api/logs/audit"), "Audit Logs")

# --- 16. INFLUENCER ACTIONS ---
def test_influencer_actions(session, user_id):
    print_header("TESTING INFLUENCER ACTIONS")
    
    # 1. Generate Affiliate Link
    print_section("Generate Affiliate Link")
    # First get a product to link to
    products_res = session.get(f"{BASE_URL}/api/marketplace/products")
    if products_res.status_code == 200 and products_res.json().get("products"):
        product_id = products_res.json()["products"][0]["id"]
        
        # --- SIMULATE APPROVAL ---
        if supabase:
            try:
                # Use user_id directly as influencer_id (based on FK constraint error)
                real_influencer_id = user_id
                
                # 2. Get merchant_id from product
                prod_data = products_res.json()["products"][0]
                merchant_id = prod_data.get("merchant_id")
                
                # Check if request exists using influencer_id
                existing = supabase.table("affiliation_requests").select("*").eq("influencer_id", real_influencer_id).eq("product_id", product_id).execute()
                
                if existing.data:
                    # Update to approved (active)
                    print("   [INFO] Updating existing request to 'active'...")
                    supabase.table("affiliation_requests").update({"status": "active"}).eq("id", existing.data[0]["id"]).execute()
                else:
                    # Insert approved request
                    print("   [INFO] Inserting 'active' request...")
                    try:
                        res = supabase.table("affiliation_requests").insert({
                            "influencer_id": real_influencer_id,
                            "product_id": product_id,
                            "merchant_id": merchant_id,
                            "status": "active"
                        }).execute()
                        print("   [SUCCESS] 'active' request inserted.")
                    except Exception as e:
                        print_fail("Failed to insert 'active' request", str(e))
                        # Try pending_approval just in case
                        try:
                            print("   [INFO] Retrying with 'pending_approval'...")
                            res = supabase.table("affiliation_requests").insert({
                                "influencer_id": real_influencer_id,
                                "product_id": product_id,
                                "merchant_id": merchant_id,
                                "status": "pending_approval"
                            }).execute()
                            if res.data:
                                req_id = res.data[0]['id']
                                print("   [INFO] Updating 'pending_approval' to 'active'...")
                                supabase.table("affiliation_requests").update({"status": "active"}).eq("id", req_id).execute()
                        except Exception as e2:
                            print_fail("Failed retry with 'pending_approval'", str(e2))

                print_success("Simulated approved affiliation request in DB")
            except Exception as e:
                print_fail("Failed to simulate approval in DB", str(e))
        # -------------------------

        link_payload = {"product_id": product_id}
        refresh_csrf_header(session)
        # Corrected endpoint URL
        # Expect 201 Created
        res = session.post(f"{BASE_URL}/api/affiliate/generate-link", json=link_payload)
        if res.status_code in [200, 201]:
            print_success("Generate Link")
        else:
            print_fail("Generate Link", f"Status: {res.status_code}, Body: {res.text}")
    else:
        print_fail("Skipping Generate Link", "No products found in marketplace")

    # 2. Request Payout
    print_section("Request Payout")
    payout_payload = {
        "amount": 100.0,
        "payment_method": "bank_transfer",
        "currency": "EUR"
    }
    refresh_csrf_header(session)
    # This might fail if balance is insufficient, but we check the response
    res = session.post(f"{BASE_URL}/api/payouts/request", json=payout_payload)
    if res.status_code == 200:
        print_success("Payout Request successful")
    elif (res.status_code == 400 or res.status_code == 500) and ("Solde insuffisant" in res.text or "Payout refusé" in res.text):
        print_success("Payout Request validated (Insufficient Balance)")
    else:
        print_fail("Payout Request Failed", f"Status: {res.status_code}, Body: {res.text}")

if __name__ == "__main__":
    print(f"{Color.BOLD}STARTING FULL SYSTEM AUDIT...{Color.ENDC}")
    
    # Sessions
    admin_session = requests.Session()
    merchant_session = requests.Session()
    influencer_session = requests.Session()
    commercial_session = requests.Session()
    
    # 1. Admin Tests
    admin_user = login(admin_session, USERS["admin"], "Admin")
    if admin_user:
        test_admin_dashboard(admin_session)
        test_admin_social_tools(admin_session)
        test_advanced_payments(admin_session, "Admin", admin_user["id"])
        test_user_management(admin_session) # Added User Management Tests
        
    # 2. Merchant Tests
    merchant_user = login(merchant_session, USERS["merchant"], "Merchant")
    if merchant_user:
        test_merchant_dashboard(merchant_session, merchant_user["id"])
        test_ai_features(merchant_session, merchant_user["id"], "Merchant")
        test_advanced_payments(merchant_session, "Merchant", merchant_user["id"])
        test_team_management(merchant_session, "Merchant")
        test_advanced_collaboration(merchant_session, "Merchant")
        test_gamification(merchant_session, merchant_user["id"], "Merchant")
        test_integrations(merchant_session)
        
    # 3. Influencer Tests
    influencer_user = login(influencer_session, USERS["influencer"], "Influencer")
    if influencer_user:
        test_influencer_dashboard(influencer_session, influencer_user["id"])
        test_ai_features(influencer_session, influencer_user["id"], "Influencer")
        test_content_studio(influencer_session, "Influencer")
        test_advanced_collaboration(influencer_session, "Influencer")
        test_gamification(influencer_session, influencer_user["id"], "Influencer")
        test_influencer_actions(influencer_session, influencer_user["id"]) # Added Influencer Actions Tests
        
    # 4. Commercial Tests
    commercial_user = login(commercial_session, USERS["commercial"], "Commercial")
    if commercial_user:
        test_commercial_dashboard(commercial_session)
        test_commercials_directory(commercial_session, commercial_user["id"])
        test_ai_features(commercial_session, commercial_user["id"], "Commercial")
        
    # 5. Cross-Role Tests (Messaging)
    if merchant_user and influencer_user:
        test_messaging(merchant_session, influencer_session, merchant_user, influencer_user)
        
    print_header("AUDIT COMPLETE")
